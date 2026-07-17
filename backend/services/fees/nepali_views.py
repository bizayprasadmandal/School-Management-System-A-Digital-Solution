"""
Nepali Payment Gateway Integration — Khalti + eSewa

Provides:
- POST /fees/nepali/initiate/ — initiate a payment with the selected gateway
- POST /fees/nepali/verify/ — verify a completed payment (called after gateway redirect)

Environment variables:
  KHALTI_SECRET_KEY       — Live/Test secret key from Khalti merchant dashboard
  KHALTI_MERCHANT_ID      — Merchant ID (used for return_url reference)
  ESEWA_MERCHANT_CODE     — Product code from eSewa merchant registration
  ESEWA_SECRET_KEY        — Secret key from eSewa merchant registration

API docs:
  Khalti: https://docs.khalti.com/khalti-epayment/
  eSewa:  https://developer.esewa.com.np/pages/Epay
"""

import hashlib
import hmac
import json
import logging
import uuid
from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import FeeInvoice, Payment

logger = logging.getLogger(__name__)

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _amount_to_paisa(amount: Decimal) -> int:
    """Convert NPR amount to paisa (Khalti uses paisa, 1 NPR = 100 paisa)."""
    return int((amount * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_DOWN))


def _validate_invoice_access(invoice: FeeInvoice, user) -> Response | None:
    """Check that the invoice belongs to the user's school and is payable."""
    if invoice.student.school_id != user.school_id:
        return Response({"detail": "Invoice not found."}, status=404)
    if invoice.status not in ("unpaid", "partial", "overdue"):
        return Response(
            {"detail": f"Invoice status is '{invoice.status}' — cannot pay."},
            status=400,
        )
    if invoice.outstanding_amount <= 0:
        return Response({"detail": "Invoice has no outstanding amount."}, status=400)
    # Role check
    if user.role == "student" and invoice.student.user_id != user.id:
        return Response({"detail": "This invoice does not belong to you."}, status=403)
    if user.role == "parent":
        is_guardian = invoice.student.guardians.filter(user=user).exists()
        if not is_guardian:
            return Response({"detail": "You are not a guardian of this student."}, status=403)
    return None


def _create_pending_payment(invoice: FeeInvoice, amount: Decimal, method: str,
                            transaction_id: str = "") -> Payment:
    """Create a pending Payment record for a gateway transaction."""
    return Payment.objects.create(
        invoice=invoice,
        amount=amount,
        payment_method=method,
        status=Payment.Status.PENDING,
        transaction_id=transaction_id or f"{method.upper()}-{uuid.uuid4().hex[:12].upper()}",
        receipt_number=f"{method.upper()}-{uuid.uuid4().hex[:8].upper()}",
        notes=f"{method.upper()} payment initiated",
    )

# ─── Khalti API ──────────────────────────────────────────────────────────────


KHALTI_INITIATE_URL = "https://dev.khalti.com/api/v2/epayment/initiate/"
KHALTI_LOOKUP_URL = "https://dev.khalti.com/api/v2/epayment/lookup/"
KHALTI_PAYMENT_URL = "https://dev.khalti.com/epayment/"

# Production URLs (commented out for safety)
# KHALTI_INITIATE_URL = "https://khalti.com/api/v2/epayment/initiate/"
# KHALTI_LOOKUP_URL = "https://khalti.com/api/v2/epayment/lookup/"
# KHALTI_PAYMENT_URL = "https://khalti.com/epayment/"


def _khalti_headers() -> dict:
    return {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def _esewa_headers() -> dict:
    return {"Content-Type": "application/json"}


# ─── Initiate Payment (supports both Khalti and eSewa) ───────────────────────


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    Initiate a payment with Khalti or eSewa.

    Request body:
      invoice_id (str): UUID of the FeeInvoice to pay
      gateway (str): "khalti" or "esewa"
      return_url (str, optional): Frontend URL to redirect after payment.
                                  Defaults to the frontend callback page.

    Returns:
      For Khalti: { payment_url, pidx, gateway }
      For eSewa:  { form_params, gateway_url, gateway }
    """
    invoice_id = request.data.get("invoice_id")
    gateway = request.data.get("gateway", "").lower()
    return_url = request.data.get(
        "return_url",
        f"{request.scheme}://{request.get_host()}/fees/callback",
    )

    if gateway not in ("khalti", "esewa"):
        return Response({"detail": "Gateway must be 'khalti' or 'esewa'."}, status=400)

    if not invoice_id:
        return Response({"detail": "invoice_id is required."}, status=400)

    try:
        invoice = FeeInvoice.objects.select_related(
            "student__user", "student__school"
        ).get(id=invoice_id)
    except FeeInvoice.DoesNotExist:
        return Response({"detail": "Invoice not found."}, status=404)

    # Validate access
    error = _validate_invoice_access(invoice, request.user)
    if error:
        return error

    outstanding = invoice.outstanding_amount

    if gateway == "khalti":
        return _initiate_khalti(invoice, outstanding, return_url, request)
    else:
        return _initiate_esewa(invoice, outstanding, return_url, request)


def _initiate_khalti(invoice, amount, return_url, request):
    """Call Khalti /epayment/initiate/ API and return the payment URL."""
    # Check for existing pending payment for this invoice
    existing = Payment.objects.filter(
        invoice=invoice,
        payment_method="khalti",
        status=Payment.Status.PENDING,
    ).first()
    if existing:
        # If there's already a pending Khalti payment, return its info
        logger.info(
            "Reusing existing Khalti pending payment: txn=%s", existing.transaction_id,
        )
        # We can't know if the Khalti session is still valid, so just proceed with new one
        # Cancel the old one conceptually by marking it failed
        existing.status = Payment.Status.FAILED
        existing.gateway_response = {**existing.gateway_response or {}, "superseded": True}
        existing.save(update_fields=["status", "gateway_response"])

    purchase_order_id = f"INV-{invoice.invoice_number}-{uuid.uuid4().hex[:6].upper()}"
    website_url = f"{request.scheme}://{request.get_host()}"

    payload = {
        "return_url": return_url,
        "website_url": website_url,
        "amount": _amount_to_paisa(amount),
        "purchase_order_id": purchase_order_id,
        "purchase_order_name": f"Fee Invoice {invoice.invoice_number}",
    }

    logger.info(
        "Khalti initiate: invoice=%s amount=%.2f",
        invoice.invoice_number, amount,
    )

    try:
        resp = requests.post(
            KHALTI_INITIATE_URL,
            headers=_khalti_headers(),
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error("Khalti initiate failed: %s", str(e))
        return Response(
            {"detail": "Payment gateway error. Please try again later."},
            status=502,
        )

    pidx = data.get("pidx")
    payment_url = data.get("payment_url", "")

    if not pidx:
        logger.warning("Khalti initiate response missing pidx: %s", data)
        return Response(
            {"detail": "Payment gateway error. Please try again."},
            status=502,
        )

    # Create pending payment record
    _create_pending_payment(invoice, amount, "khalti", transaction_id=pidx)

    return Response({
        "gateway": "khalti",
        "payment_url": payment_url,
        "pidx": pidx,
        "purchase_order_id": purchase_order_id,
    })


def _initiate_esewa(invoice, amount, return_url, request):
    """
    Prepare eSewa form params with HMAC-SHA256 signature.
    Returns form data that the frontend submits via POST to eSewa.
    """
    # Check for existing pending payment for this invoice
    existing = Payment.objects.filter(
        invoice=invoice,
        payment_method="esewa",
        status=Payment.Status.PENDING,
    ).first()
    if existing:
        existing.status = Payment.Status.FAILED
        existing.gateway_response = {**existing.gateway_response or {}, "superseded": True}
        existing.save(update_fields=["status", "gateway_response"])

    transaction_uuid = f"{uuid.uuid4().hex[:12].upper()}"
    total_amount = str(int(amount))  # eSewa expects integer string
    # For simplicity, we set tax_amount=0 and amount=total_amount
    # In a real scenario, break down into amount + tax_amount as needed
    amount_str = str(int(amount))
    tax_amount = "0"

    # Generate HMAC-SHA256 signature
    # Message format: total_amount={total},transaction_uuid={uuid},product_code={code}
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={settings.ESEWA_MERCHANT_CODE}"
    signature = hmac.new(
        settings.ESEWA_SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_b64 = __import__("base64").b64encode(signature).decode("utf-8")

    # Create pending payment record
    _create_pending_payment(
        invoice, amount, "esewa",
        transaction_id=f"ESEWA-{transaction_uuid}",
    )

    return Response({
        "gateway": "esewa",
        "gateway_url": "https://rc-epay.esewa.com.np/api/epay/main/v2/form",
        # Production: "https://epay.esewa.com.np/api/epay/main/v2/form"
        "form_params": {
            "amount": amount_str,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
            "product_code": settings.ESEWA_MERCHANT_CODE,
            "success_url": return_url,
            "failure_url": return_url,
            "signature": signature_b64,
        },
    })


# ─── Verify Payment (called after gateway redirect) ─────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])  # Verified via signature / token
def verify_payment(request):
    """
    Verify a completed payment with the gateway.

    Request body:
      gateway (str): "khalti" or "esewa"
      pidx (str, for Khalti): Payment identifier from Khalti redirect
      transaction_uuid (str, for eSewa): Transaction UUID from eSewa redirect
      total_amount (str, for eSewa): Total amount from eSewa redirect

    Returns:
      { status, receipt_number, invoice_id, gateway }
    """
    gateway = request.data.get("gateway", "").lower()

    if gateway == "khalti":
        return _verify_khalti(request)
    elif gateway == "esewa":
        return _verify_esewa(request)
    else:
        return Response({"detail": "Gateway must be 'khalti' or 'esewa'."}, status=400)


def _verify_khalti(request):
    """Verify payment with Khalti /epayment/lookup/ API."""
    pidx = request.data.get("pidx")
    if not pidx:
        return Response({"detail": "pidx is required."}, status=400)

    try:
        resp = requests.post(
            KHALTI_LOOKUP_URL,
            headers=_khalti_headers(),
            json={"pidx": pidx},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error("Khalti lookup failed for pidx=%s: %s", pidx, str(e))
        return Response(
            {"detail": "Payment verification failed. Please contact support."},
            status=502,
        )

    status_from_gateway = data.get("status", "")

    # Find the pending payment record
    try:
        payment = Payment.objects.get(
            transaction_id=pidx,
            payment_method="khalti",
            status=Payment.Status.PENDING,
        )
    except Payment.DoesNotExist:
        logger.warning("Khalti verify: no pending payment found for pidx=%s", pidx)
        return Response(
            {"detail": "Payment record not found. It may have already been processed."},
            status=404,
        )

    if status_from_gateway == "Completed":
        _mark_payment_successful(payment, {
            "khalti_pidx": pidx,
            "transaction_id": data.get("transaction_id", ""),
            "status": "Completed",
            "total_amount": data.get("total_amount"),
            "fee_amount": data.get("fee_amount"),
            "refunded": data.get("refunded", False),
        })
        logger.info(
            "Khalti payment successful: pidx=%s invoice=%s amount=%.2f",
            pidx, payment.invoice.invoice_number, payment.amount,
        )
        return Response({
            "status": "successful",
            "receipt_number": payment.receipt_number,
            "invoice_id": str(payment.invoice.id),
            "gateway": "khalti",
        })
    else:
        payment.status = Payment.Status.FAILED
        payment.gateway_response = {
            "khalti_pidx": pidx,
            "status": status_from_gateway,
            **data,
        }
        payment.save(update_fields=["status", "gateway_response"])
        logger.warning(
            "Khalti payment failed: pidx=%s status=%s",
            pidx, status_from_gateway,
        )
        return Response({
            "status": "failed",
            "detail": f"Payment status: {status_from_gateway}",
            "gateway": "khalti",
        })


def _verify_esewa(request):
    """Verify payment with eSewa transaction status API."""
    transaction_uuid = request.data.get("transaction_uuid")
    total_amount = request.data.get("total_amount")

    if not transaction_uuid or not total_amount:
        return Response(
            {"detail": "transaction_uuid and total_amount are required."},
            status=400,
        )

    # eSewa status check API
    status_url = "https://rc.esewa.com.np/api/epay/transaction/status/"
    # Production: "https://esewa.com.np/api/epay/transaction/status/"

    params = {
        "product_code": settings.ESEWA_MERCHANT_CODE,
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
    }

    try:
        resp = requests.get(
            status_url,
            params=params,
            headers=_esewa_headers(),
            timeout=15,
        )
        data = resp.json() if resp.status_code == 200 else {"status": "NOT_FOUND"}
    except requests.RequestException as e:
        logger.error("eSewa status check failed for uuid=%s: %s", transaction_uuid, str(e))
        return Response(
            {"detail": "Payment verification failed. Please contact support."},
            status=502,
        )

    gateway_status = data.get("status", "")

    # Find the pending payment
    tid = f"ESEWA-{transaction_uuid}"
    try:
        payment = Payment.objects.get(
            transaction_id=tid,
            payment_method="esewa",
            status=Payment.Status.PENDING,
        )
    except Payment.DoesNotExist:
        logger.warning("eSewa verify: no pending payment found for uuid=%s", transaction_uuid)
        return Response(
            {"detail": "Payment record not found."},
            status=404,
        )

    if gateway_status == "COMPLETE":
        _mark_payment_successful(payment, {
            "esewa_transaction_uuid": transaction_uuid,
            "esewa_ref_id": data.get("ref_id", ""),
            "status": "COMPLETE",
            "total_amount": data.get("total_amount"),
        })
        logger.info(
            "eSewa payment successful: uuid=%s invoice=%s amount=%.2f",
            transaction_uuid, payment.invoice.invoice_number, payment.amount,
        )
        return Response({
            "status": "successful",
            "receipt_number": payment.receipt_number,
            "invoice_id": str(payment.invoice.id),
            "gateway": "esewa",
        })
    else:
        payment.status = Payment.Status.FAILED
        payment.gateway_response = {
            "esewa_transaction_uuid": transaction_uuid,
            "gateway_status": gateway_status,
            **data,
        }
        payment.save(update_fields=["status", "gateway_response"])
        logger.warning(
            "eSewa payment failed: uuid=%s status=%s",
            transaction_uuid, gateway_status,
        )
        return Response({
            "status": "failed",
            "detail": f"Payment status: {gateway_status}",
            "gateway": "esewa",
        })


# ─── Refund (via gateway, if supported) ──────────────────────────────────────


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refund_nepali_payment(request):
    """
    Refund a Khalti or eSewa payment.

    Request body:
      payment_id (str): UUID of the Payment record to refund

    Note: Khalti and eSewa refund capabilities depend on merchant agreement.
    This endpoint currently marks the payment as refunded locally and adjusts
    the invoice. Gateway-initiated refunds require additional merchant setup.
    """
    if request.user.role not in ("school_admin", "super_admin"):
        return Response({"detail": "Only school administrators can issue refunds."}, status=403)

    payment_id = request.data.get("payment_id")
    if not payment_id:
        return Response({"detail": "payment_id is required."}, status=400)

    try:
        payment = Payment.objects.get(
            id=payment_id,
            invoice__student__school=request.user.school,
            payment_method__in=["khalti", "esewa"],
        )
    except Payment.DoesNotExist:
        return Response({"detail": "Payment not found."}, status=404)

    if payment.status != Payment.Status.SUCCESSFUL:
        return Response(
            {"detail": f"Payment status is '{payment.status}' — can only refund successful payments."},
            status=400,
        )

    with transaction.atomic():
        invoice = FeeInvoice.objects.select_for_update().get(id=payment.invoice_id)

        payment.status = Payment.Status.REFUNDED
        gw_response = payment.gateway_response or {}
        gw_response["refund_reason"] = request.data.get("reason", "")
        gw_response["refunded_at"] = timezone.now().isoformat()
        payment.gateway_response = gw_response
        payment.save(update_fields=["status", "gateway_response"])

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
        "Nepali payment refunded: %s (%s) on invoice %s",
        payment.receipt_number, payment.payment_method, invoice.invoice_number,
    )

    return Response({
        "detail": "Payment refunded successfully.",
        "amount": float(payment.amount),
        "invoice_status": invoice.status,
    })


# ─── Internal Helpers ────────────────────────────────────────────────────────


def _mark_payment_successful(payment: Payment, gateway_data: dict) -> None:
    """Mark a pending Payment as successful and update the invoice."""
    with transaction.atomic():
        invoice = FeeInvoice.objects.select_for_update().get(id=payment.invoice_id)

        payment.status = Payment.Status.SUCCESSFUL
        payment.paid_at = timezone.now()
        payment.gateway_response = {
            **(payment.gateway_response or {}),
            **gateway_data,
        }
        payment.save(update_fields=["status", "paid_at", "gateway_response"])

        invoice.paid_amount += payment.amount
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = FeeInvoice.Status.PAID
        elif invoice.paid_amount > 0:
            invoice.status = FeeInvoice.Status.PARTIAL
        invoice.save(update_fields=["paid_amount", "status"])
