"""
Stripe Payment Integration — PaymentIntents + Webhook
Provides:
- POST /fees/stripe/create-payment-intent/ — create a PaymentIntent for an invoice
- POST /fees/stripe/webhook/ — receive Stripe webhook events (payment_intent.succeeded, etc.)

Environment variables:
  STRIPE_SECRET_KEY      — sk_test_... or sk_live_...
  STRIPE_WEBHOOK_SECRET  — whsec_... (optional; verify webhook signatures)
"""

import logging

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import FeeInvoice, Payment

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Subunits per major currency unit (Stripe charges in the smallest unit).
# USD/NPR use 100; a handful of zero-decimal and 3-decimal currencies differ.
_ZERO_DECIMAL_CURRENCIES = {
    "BIF",
    "CLP",
    "DJF",
    "GNF",
    "ISK",
    "JPY",
    "KMF",
    "KRW",
    "PYG",
    "RWF",
    "UGX",
    "VND",
    "VUV",
    "XAF",
    "XOF",
    "XPF",
}
_THREE_DECIMAL_CURRENCIES = {"BHD", "IQD", "JOD", "KWD", "LYD", "OMR", "TND"}


def _subunit_factor(currency):
    """Subunits per major unit for an ISO currency code (default 100)."""
    if currency in _ZERO_DECIMAL_CURRENCIES:
        return 1
    if currency in _THREE_DECIMAL_CURRENCIES:
        return 1000
    return 100


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    """
    Create a Stripe PaymentIntent for a specific invoice.

    Request body:
      invoice_id (str): UUID of the FeeInvoice to pay

    Returns:
      client_secret (str): Stripe client secret for frontend confirmation
      publishable_key (str): Stripe publishable key for frontend
      amount (int): Amount in cents
    """
    invoice_id = request.data.get("invoice_id")
    if not invoice_id:
        return Response({"detail": "invoice_id is required."}, status=400)

    try:
        invoice = FeeInvoice.objects.select_related("student__user", "student__school").get(
            id=invoice_id,
            student__school=request.user.school,
        )
    except FeeInvoice.DoesNotExist:
        return Response({"detail": "Invoice not found."}, status=404)

    # Only allow payment on unpaid/partial/overdue invoices
    if invoice.status not in ("unpaid", "partial", "overdue"):
        return Response(
            {"detail": f"Invoice status is '{invoice.status}' — cannot pay."},
            status=400,
        )

    outstanding = invoice.outstanding_amount
    if outstanding <= 0:
        return Response({"detail": "Invoice has no outstanding amount."}, status=400)

    # Check that the user owns this invoice (or is parent of the student)
    user = request.user
    if user.role == "student" and invoice.student.user_id != user.id:
        return Response({"detail": "This invoice does not belong to you."}, status=403)
    if user.role == "parent":
        is_guardian = invoice.student.guardians.filter(user=user).exists()
        if not is_guardian:
            return Response({"detail": "You are not a guardian of this student."}, status=403)

    # Amount in cents (Stripe uses smallest currency unit)
    amount_cents = int(outstanding * 100)

    try:
        # Create or reuse an existing PaymentIntent for this invoice+user
        # Check if there's a pending PaymentIntent already
        existing_payment = Payment.objects.filter(
            invoice=invoice,
            status=Payment.Status.PENDING,
            payment_method="online",
        ).first()

        if existing_payment and existing_payment.transaction_id:
            try:
                pi = stripe.PaymentIntent.retrieve(existing_payment.transaction_id)
                if pi.status in ("requires_payment_method", "requires_confirmation"):
                    return Response(
                        {
                            "client_secret": pi.client_secret,
                            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
                            "amount": amount_cents,
                            "invoice_id": str(invoice.id),
                            "payment_intent_id": pi.id,
                        }
                    )
            except stripe.error.StripeError:
                pass  # Stale PaymentIntent — create a new one

        # Create a new PaymentIntent
        pi = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            description=f"Invoice {invoice.invoice_number} — {invoice.student.user.full_name}",
            metadata={
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "student_name": invoice.student.user.full_name,
                "school": invoice.student.school.code,
            },
            # Automatic payment methods (cards, wallets, etc.)
            automatic_payment_methods={"enabled": True},
        )

        # Create a pending Payment record to track this intent
        Payment.objects.create(
            invoice=invoice,
            amount=outstanding,
            payment_method="online",
            status=Payment.Status.PENDING,
            transaction_id=pi.id,
            receipt_number=f"STRIPE-{pi.id[:12].upper()}",
            notes=f"Stripe PaymentIntent {pi.id}",
        )

        return Response(
            {
                "client_secret": pi.client_secret,
                "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
                "amount": amount_cents,
                "invoice_id": str(invoice.id),
                "payment_intent_id": pi.id,
            }
        )

    except stripe.error.StripeError as e:
        logger.error("Stripe PaymentIntent creation failed: %s", e.user_message or str(e))
        return Response(
            {"detail": "Payment service error. Please try again later."},
            status=502,
        )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """
    Stripe webhook handler — processes payment_intent.succeeded
    and payment_intent.payment_failed events.

    This endpoint is called by Stripe servers — it is NOT authenticated.
    Signature verification is performed using the webhook secret.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    # Fail CLOSED: without STRIPE_WEBHOOK_SECRET the payload cannot be
    # authenticated, so the request is rejected outright. The only exception is
    # when STRIPE_WEBHOOK_REQUIRE_SIGNATURE is explicitly False (local dev), in
    # which case unsigned payloads are accepted so the flow can be exercised
    # without a real Stripe account. Production always defaults to True (see
    # core/settings/production.py), so production never accepts an
    # unverifiable webhook.
    if not settings.STRIPE_WEBHOOK_SECRET:
        if settings.STRIPE_WEBHOOK_REQUIRE_SIGNATURE:
            logger.error("Stripe webhook: STRIPE_WEBHOOK_SECRET not configured — rejecting request")
            return HttpResponse(
                "Webhook signature verification disabled: STRIPE_WEBHOOK_SECRET not set.",
                status=400,
            )
        import json

        event = json.loads(payload)
        event = stripe.Event.construct_from(event, stripe.api_key)
    else:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except stripe.error.SignatureVerificationError:
            logger.warning("Stripe webhook: invalid signature")
            return HttpResponse(status=400)
        except ValueError:
            logger.warning("Stripe webhook: invalid payload")
            return HttpResponse(status=400)

    event_type = event.get("type") if isinstance(event, dict) else event.type
    logger.info("Stripe webhook received: %s", event_type)

    if event_type == "payment_intent.succeeded":
        pi = event["data"]["object"] if isinstance(event, dict) else event.data.object
        _handle_payment_success(pi)

    elif event_type == "payment_intent.payment_failed":
        pi = event["data"]["object"] if isinstance(event, dict) else event.data.object
        _handle_payment_failed(pi)

    return HttpResponse(status=200)


def _handle_payment_success(payment_intent):
    """Mark the pending Payment as successful and update the invoice."""
    pi_id = payment_intent.id
    try:
        payment = Payment.objects.get(
            transaction_id=pi_id,
            payment_method="online",
            status=Payment.Status.PENDING,
        )
    except Payment.DoesNotExist:
        logger.warning("Stripe webhook: no pending payment found for %s", pi_id)
        return

    # Compare the amount the gateway actually captured with the payment
    # record. Payment.amount is stored in major units; Stripe reports
    # amount_received in minor units (cents). A mismatch means the intent was
    # tampered with or reused — mark the payment FAILED and never credit it.
    amount_received = (
        payment_intent.get("amount_received") if isinstance(payment_intent, dict) else payment_intent.amount_received
    )
    currency = (
        payment_intent.get("currency") if isinstance(payment_intent, dict) else getattr(payment_intent, "currency", "")
    )
    expected_minor = int(payment.amount * _subunit_factor(currency or "usd"))

    if amount_received is None or int(amount_received) != expected_minor:
        payment.status = Payment.Status.FAILED
        payment.gateway_response = {
            "stripe_id": pi_id,
            "amount_received": amount_received,
            "expected_amount": expected_minor,
            "status": "amount_mismatch",
        }
        payment.save(update_fields=["status", "gateway_response"])
        logger.warning(
            "Stripe webhook: amount mismatch for %s — gateway=%s expected=%s; "
            "payment marked FAILED, invoice NOT credited",
            pi_id,
            amount_received,
            expected_minor,
        )
        return

    from django.db import transaction as db_transaction

    with db_transaction.atomic():
        # Re-read the payment row under FOR UPDATE so concurrent webhook
        # deliveries for the same PaymentIntent cannot both pass the earlier
        # status=PENDING lookup and double-credit the invoice.
        locked = Payment.objects.select_for_update().get(pk=payment.pk)
        if locked.status != Payment.Status.PENDING:
            logger.info(
                "Stripe webhook: payment %s already processed (status=%s) — skipping duplicate credit",
                locked.receipt_number,
                locked.status,
            )
            return

        # Lock the invoice row
        invoice = FeeInvoice.objects.select_for_update().get(id=locked.invoice_id)

        locked.status = Payment.Status.SUCCESSFUL
        locked.paid_at = timezone.now()
        locked.gateway_response = {
            "stripe_id": pi_id,
            "amount_received": amount_received,
            "status": "succeeded",
        }
        locked.save(update_fields=["status", "paid_at", "gateway_response"])

        # Update invoice paid_amount and status
        invoice.paid_amount += locked.amount
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = FeeInvoice.Status.PAID
        elif invoice.paid_amount > 0:
            invoice.status = FeeInvoice.Status.PARTIAL
        invoice.save(update_fields=["paid_amount", "status"])

        logger.info(
            "Payment successful: %s on invoice %s ($%.2f)",
            pi_id,
            invoice.invoice_number,
            locked.amount,
        )


def _handle_payment_failed(payment_intent):
    """Mark the pending Payment as failed."""
    pi_id = payment_intent.id
    try:
        payment = Payment.objects.get(
            transaction_id=pi_id,
            payment_method="online",
            status=Payment.Status.PENDING,
        )
    except Payment.DoesNotExist:
        return

    payment.status = Payment.Status.FAILED
    payment.gateway_response = {
        "stripe_id": pi_id,
        "error": (
            payment_intent.get("last_payment_error", {}).get("message", "Unknown error")
            if isinstance(payment_intent, dict)
            else str(payment_intent.last_payment_error.message if payment_intent.last_payment_error else "Unknown")
        ),
    }
    payment.save(update_fields=["status", "gateway_response"])

    logger.warning("Payment failed: %s — %s", pi_id, payment.gateway_response.get("error"))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refund_payment(request):
    """
    Refund a successful Stripe payment.

    Request body:
      payment_id (str): UUID of the Payment record to refund
      reason (str, optional): Reason for the refund

    Only school admins can initiate refunds.
    Only successful online payments can be refunded.
    """
    # Check admin permission
    if request.user.role not in ("school_admin", "super_admin"):
        return Response({"detail": "Only school administrators can issue refunds."}, status=403)

    payment_id = request.data.get("payment_id")
    reason = request.data.get("reason", "")

    if not payment_id:
        return Response({"detail": "payment_id is required."}, status=400)

    try:
        payment = Payment.objects.get(
            id=payment_id,
            invoice__student__school=request.user.school,
        )
    except Payment.DoesNotExist:
        return Response({"detail": "Payment not found."}, status=404)

    # Validate the payment can be refunded
    if payment.status != Payment.Status.SUCCESSFUL:
        return Response(
            {"detail": f"Payment status is '{payment.status}' — can only refund successful payments."},
            status=400,
        )

    if payment.payment_method != "online" or not payment.transaction_id:
        return Response(
            {
                "detail": (
                    "Only online/Stripe payments can be refunded via this endpoint. "
                    "For cash/bank payments, record a reversal manually."
                )
            },
            status=400,
        )

    try:
        # Process the refund via Stripe
        refund = stripe.Refund.create(
            payment_intent=payment.transaction_id,
            reason="requested_by_customer",
            metadata={
                "payment_id": str(payment.id),
                "invoice_number": payment.invoice.invoice_number,
                "refunded_by": request.user.full_name,
                "reason": reason,
            },
        )

        from django.db import transaction as db_transaction

        with db_transaction.atomic():
            # Lock the invoice row
            invoice = FeeInvoice.objects.select_for_update().get(id=payment.invoice_id)

            # Update the payment record
            payment.status = Payment.Status.REFUNDED
            payment.notes = (
                f"{payment.notes}\nRefunded by {request.user.full_name}: {reason}"
                if payment.notes
                else f"Refunded by {request.user.full_name}: {reason}"
            )
            payment.gateway_response = {
                **(payment.gateway_response or {}),
                "refund_id": refund.id,
                "refund_amount": refund.amount,
                "refund_status": refund.status,
                "refund_reason": reason,
            }
            payment.save(update_fields=["status", "notes", "gateway_response"])

            # Revert the invoice paid_amount and status
            invoice.paid_amount -= payment.amount
            if invoice.paid_amount <= 0:
                invoice.paid_amount = 0
                invoice.status = FeeInvoice.Status.UNPAID
            elif invoice.paid_amount < invoice.total_amount:
                invoice.status = FeeInvoice.Status.PARTIAL
            else:
                invoice.status = FeeInvoice.Status.PAID
            invoice.save(update_fields=["paid_amount", "status"])

        logger.info(
            "Payment refunded: %s on invoice %s ($%.2f) — refund_id=%s",
            payment.transaction_id,
            invoice.invoice_number,
            payment.amount,
            refund.id,
        )

        return Response(
            {
                "detail": "Payment refunded successfully.",
                "refund_id": refund.id,
                "amount": float(payment.amount),
                "invoice_status": invoice.status,
            }
        )

    except stripe.error.StripeError as e:
        error_msg = e.user_message or str(e)
        logger.error("Stripe refund failed for payment %s: %s", payment_id, error_msg)
        return Response(
            {"detail": f"Refund failed: {error_msg}"},
            status=502,
        )
