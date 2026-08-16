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
  KHALTI_BASE_URL         — Khalti API base URL (dev: https://dev.khalti.com,
                            prod: https://khalti.com)
  ESEWA_BASE_URL          — eSewa payment form base URL (dev:
                            https://rc-epay.esewa.com.np, prod:
                            https://epay.esewa.com.np)
  ESEWA_STATUS_BASE_URL   — eSewa status/refund API base URL (dev:
                            https://rc.esewa.com.np, prod: https://esewa.com.np)

API docs:
  Khalti: https://docs.khalti.com/khalti-epayment/
  eSewa:  https://developer.esewa.com.np/pages/Epay
"""

import base64
import hashlib
import hmac
import logging
import uuid
from decimal import ROUND_DOWN, Decimal, InvalidOperation

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import FeeInvoice, Payment

logger = logging.getLogger(__name__)

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _amount_to_paisa(amount: Decimal) -> int:
    """Convert NPR amount to paisa (Khalti uses paisa, 1 NPR = 100 paisa)."""
    return int((amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_DOWN))


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


def _create_pending_payment(invoice: FeeInvoice, amount: Decimal, method: str, transaction_id: str = "") -> Payment:
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


# Base URLs come from django.conf.settings so the sandbox endpoints used in
# local development are replaced by the live gateway hosts in production
# (see KHALTI_BASE_URL / ESEWA_BASE_URL / ESEWA_STATUS_BASE_URL in
# core/settings/base.py — production.py defaults them to the live hosts).
KHALTI_BASE_URL = settings.KHALTI_BASE_URL.rstrip("/")
ESEWA_BASE_URL = settings.ESEWA_BASE_URL.rstrip("/")
ESEWA_STATUS_BASE_URL = settings.ESEWA_STATUS_BASE_URL.rstrip("/")

KHALTI_INITIATE_URL = f"{KHALTI_BASE_URL}/api/v2/epayment/initiate/"
KHALTI_LOOKUP_URL = f"{KHALTI_BASE_URL}/api/v2/epayment/lookup/"
KHALTI_PAYMENT_URL = f"{KHALTI_BASE_URL}/epayment/"
KHALTI_REFUND_URL = f"{KHALTI_BASE_URL}/api/v2/payment/refund/"

ESEWA_FORM_URL = f"{ESEWA_BASE_URL}/api/epay/main/v2/form"
ESEWA_STATUS_URL = f"{ESEWA_STATUS_BASE_URL}/api/epay/transaction/status/"
ESEWA_REFUND_URL = f"{ESEWA_STATUS_BASE_URL}/api/esewav2/refund/"


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
        invoice = FeeInvoice.objects.select_related("student__user", "student__school").get(id=invoice_id)
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
            "Reusing existing Khalti pending payment: txn=%s",
            existing.transaction_id,
        )
        # We can't know if the Khalti session is still valid, so just proceed with new one
        # Cancel the old one conceptually by marking it failed
        existing.status = Payment.Status.FAILED
        gw_resp = existing.gateway_response or {}
        gw_resp["superseded"] = True
        existing.gateway_response = gw_resp
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
        invoice.invoice_number,
        amount,
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

    return Response(
        {
            "gateway": "khalti",
            "payment_url": payment_url,
            "pidx": pidx,
            "purchase_order_id": purchase_order_id,
        }
    )


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
        gw_resp = existing.gateway_response or {}
        gw_resp["superseded"] = True
        existing.gateway_response = gw_resp
        existing.save(update_fields=["status", "gateway_response"])

    transaction_uuid = f"{uuid.uuid4().hex[:12].upper()}"
    total_amount = str(int(amount))  # eSewa expects integer string
    # For simplicity, we set tax_amount=0 and amount=total_amount
    # In a real scenario, break down into amount + tax_amount as needed
    amount_str = str(int(amount))
    tax_amount = "0"

    # Generate HMAC-SHA256 signature
    # Message format: total_amount={total},transaction_uuid={uuid},product_code={code}
    message = (
        f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={settings.ESEWA_MERCHANT_CODE}"
    )
    signature = hmac.new(
        settings.ESEWA_SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_b64 = base64.b64encode(signature).decode("utf-8")

    # Create pending payment record
    _create_pending_payment(
        invoice,
        amount,
        "esewa",
        transaction_id=f"ESEWA-{transaction_uuid}",
    )

    return Response(
        {
            "gateway": "esewa",
            "gateway_url": ESEWA_FORM_URL,
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
        }
    )


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
        # Verify the amount the gateway recorded matches our payment record.
        # Khalti reports total_amount in paisa; Payment.amount is in NPR.
        gateway_total = data.get("total_amount")
        expected_total = _amount_to_paisa(payment.amount)
        if gateway_total is None or int(gateway_total) != expected_total:
            payment.status = Payment.Status.FAILED
            payment.gateway_response = {
                **data,
                "khalti_pidx": pidx,
                "status": "amount_mismatch",
                "gateway_total_amount": gateway_total,
                "expected_total_amount": expected_total,
            }
            payment.save(update_fields=["status", "gateway_response"])
            logger.warning(
                "Khalti amount mismatch for pidx=%s — gateway=%s expected=%s; " "payment marked FAILED",
                pidx,
                gateway_total,
                expected_total,
            )
            return Response(
                {
                    "status": "failed",
                    "detail": "Gateway returned amount does not match the invoice amount.",
                    "gateway": "khalti",
                },
                status=400,
            )
        _mark_payment_successful(
            payment,
            {
                "khalti_pidx": pidx,
                "transaction_id": data.get("transaction_id", ""),
                "status": "Completed",
                "total_amount": data.get("total_amount"),
                "fee_amount": data.get("fee_amount"),
                "refunded": data.get("refunded", False),
            },
        )
        logger.info(
            "Khalti payment successful: pidx=%s invoice=%s amount=%.2f",
            pidx,
            payment.invoice.invoice_number,
            payment.amount,
        )
        return Response(
            {
                "status": "successful",
                "receipt_number": payment.receipt_number,
                "invoice_id": str(payment.invoice.id),
                "gateway": "khalti",
            }
        )
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
            pidx,
            status_from_gateway,
        )
        return Response(
            {
                "status": "failed",
                "detail": f"Payment status: {status_from_gateway}",
                "gateway": "khalti",
            }
        )


def _verify_esewa(request):
    """Verify payment with eSewa transaction status API."""
    transaction_uuid = request.data.get("transaction_uuid")

    if not transaction_uuid:
        return Response({"detail": "transaction_uuid is required."}, status=400)

    # Look up the pending payment from OUR records first. The amount sent to
    # the eSewa status API and the amount checked against the gateway
    # response come from the Payment record — the client-supplied
    # total_amount is never trusted.
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

    # eSewa status check API
    status_url = ESEWA_STATUS_URL

    params = {
        "product_code": settings.ESEWA_MERCHANT_CODE,
        "total_amount": str(int(payment.amount)),
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

    if gateway_status == "COMPLETE":
        # Verify the amount the gateway recorded matches our payment record.
        gateway_total = data.get("total_amount")
        expected_total = payment.amount
        try:
            gateway_total_dec = Decimal(str(gateway_total))
        except (TypeError, ValueError, InvalidOperation):
            gateway_total_dec = None
        if gateway_total_dec is None or gateway_total_dec != expected_total:
            payment.status = Payment.Status.FAILED
            payment.gateway_response = {
                "esewa_transaction_uuid": transaction_uuid,
                "gateway_status": "amount_mismatch",
                "gateway_total_amount": gateway_total,
                "expected_total_amount": str(expected_total),
                **data,
            }
            payment.save(update_fields=["status", "gateway_response"])
            logger.warning(
                "eSewa amount mismatch for uuid=%s — gateway=%s expected=%s; " "payment marked FAILED",
                transaction_uuid,
                gateway_total,
                expected_total,
            )
            return Response(
                {
                    "status": "failed",
                    "detail": "Gateway returned amount does not match the invoice amount.",
                    "gateway": "esewa",
                },
                status=400,
            )
        _mark_payment_successful(
            payment,
            {
                "esewa_transaction_uuid": transaction_uuid,
                "esewa_ref_id": data.get("ref_id", ""),
                "status": "COMPLETE",
                "total_amount": data.get("total_amount"),
            },
        )
        logger.info(
            "eSewa payment successful: uuid=%s invoice=%s amount=%.2f",
            transaction_uuid,
            payment.invoice.invoice_number,
            payment.amount,
        )
        return Response(
            {
                "status": "successful",
                "receipt_number": payment.receipt_number,
                "invoice_id": str(payment.invoice.id),
                "gateway": "esewa",
            }
        )
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
            transaction_uuid,
            gateway_status,
        )
        return Response(
            {
                "status": "failed",
                "detail": f"Payment status: {gateway_status}",
                "gateway": "esewa",
            }
        )


# ─── Refund (via gateway) ─────────────────────────────────────────────────────


def _khalti_refund(payment: Payment, reason: str):
    """
    Refund a Khalti payment via POST {KHALTI_BASE_URL}/api/v2/payment/refund/.
    Returns (ok: bool, detail) — the gateway response dict on success, or an
    error message. Khalti refunds are initiated with the original transaction
    token (pidx) and the amount in paisa.
    """
    payload = {
        "token": payment.transaction_id,
        "amount": _amount_to_paisa(payment.amount),
    }
    try:
        resp = requests.post(
            KHALTI_REFUND_URL,
            headers=_khalti_headers(),
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error(
            "Khalti refund API call failed for %s (txn=%s): %s",
            payment.receipt_number,
            payment.transaction_id,
            str(e),
        )
        return False, f"Khalti refund API error: {e}"

    refund = data.get("refund", {})
    state = refund.get("state", "")
    if not refund or state.lower() not in ("completed", "pending"):
        logger.error(
            "Khalti refund not accepted for %s (txn=%s): %s",
            payment.receipt_number,
            payment.transaction_id,
            data,
        )
        return False, f"Khalti refund not accepted by gateway: {data}"
    logger.info(
        "Khalti refund accepted for %s (txn=%s): state=%s",
        payment.receipt_number,
        payment.transaction_id,
        state,
    )
    return True, data


def _esewa_refund(payment: Payment, reason: str):
    """
    Refund an eSewa payment via POST {ESEWA_STATUS_BASE_URL}/api/esewav2/refund/.
    Returns (ok: bool, detail). The request is signed with HMAC-SHA256 over
    transaction_uuid/refund_amount/product_code (same scheme as the initiate
    flow). eSewa accepts refunds only in NPR integer units.
    """
    transaction_uuid = (
        payment.transaction_id[len("ESEWA-") :]
        if payment.transaction_id.startswith("ESEWA-")
        else payment.transaction_id
    )
    refund_amount = str(int(payment.amount))

    message = (
        f"transaction_uuid={transaction_uuid},"
        f"refund_amount={refund_amount},"
        f"product_code={settings.ESEWA_MERCHANT_CODE}"
    )
    signature = hmac.new(
        settings.ESEWA_SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_b64 = base64.b64encode(signature).decode("utf-8")

    payload = {
        "product_code": settings.ESEWA_MERCHANT_CODE,
        "transaction_uuid": transaction_uuid,
        "refund_amount": refund_amount,
        "signature": signature_b64,
    }
    try:
        resp = requests.post(
            ESEWA_REFUND_URL,
            headers=_esewa_headers(),
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error(
            "eSewa refund API call failed for %s (uuid=%s): %s",
            payment.receipt_number,
            transaction_uuid,
            str(e),
        )
        return False, f"eSewa refund API error: {e}"

    refund = data.get("data", {})
    if refund.get("status", "").upper() != "REFUND":
        logger.error(
            "eSewa refund not accepted for %s (uuid=%s): %s",
            payment.receipt_number,
            transaction_uuid,
            data,
        )
        return False, f"eSewa refund not accepted by gateway: {data}"
    logger.info(
        "eSewa refund accepted for %s (uuid=%s): status=REFUND",
        payment.receipt_number,
        transaction_uuid,
    )
    return True, data


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refund_nepali_payment(request):
    """
    Refund a Khalti or eSewa payment via the gateway refund API.

    Request body:
      payment_id (str): UUID of the Payment record to refund
      reason (str, optional): Reason for the refund

    The gateway refund API is called FIRST (Khalti /api/v2/payment/refund/,
    eSewa /api/esewav2/refund/); the local record is only marked REFUNDED
    after the gateway accepts the refund. If the gateway call fails, the
    payment stays SUCCESSFUL and the error is returned so an operator can
    investigate — the local status is never flipped without the gateway.
    """
    if request.user.role not in ("school_admin", "super_admin"):
        return Response({"detail": "Only school administrators can issue refunds."}, status=403)

    payment_id = request.data.get("payment_id")
    reason = request.data.get("reason", "")
    if not payment_id:
        return Response({"detail": "payment_id is required."}, status=400)

    # Serialize concurrent refunds on the payment row itself: the SUCCESSFUL
    # status check, the gateway refund call, and the invoice adjustment all
    # run under this lock, so two racing refunds cannot both pass the status
    # check, hit the gateway refund API twice, or subtract the amount twice.
    with transaction.atomic():
        try:
            payment = Payment.objects.select_for_update().get(
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

        if payment.payment_method == "khalti":
            ok, detail = _khalti_refund(payment, reason)
        elif payment.payment_method == "esewa":
            ok, detail = _esewa_refund(payment, reason)
        else:
            return Response({"detail": "Unsupported payment gateway."}, status=400)

        if not ok:
            logger.error(
                "Nepali refund failed for %s (%s): %s",
                payment.receipt_number,
                payment.payment_method,
                detail,
            )
            return Response(
                {"detail": f"Refund failed: {detail}"},
                status=502,
            )

        payment.status = Payment.Status.REFUNDED
        gw_response = payment.gateway_response or {}
        gw_response["refund_reason"] = reason
        gw_response["refunded_at"] = timezone.now().isoformat()
        gw_response["gateway_refund"] = detail
        payment.gateway_response = gw_response
        payment.save(update_fields=["status", "gateway_response"])

        from .ledger import debit_invoice

        invoice = debit_invoice(payment.invoice, payment.amount)

    logger.info(
        "Nepali payment refunded: %s (%s) on invoice %s",
        payment.receipt_number,
        payment.payment_method,
        invoice.invoice_number,
    )

    return Response(
        {
            "detail": "Payment refunded successfully.",
            "amount": float(payment.amount),
            "invoice_status": invoice.status,
        }
    )


# ─── Internal Helpers ────────────────────────────────────────────────────────


def _mark_payment_successful(payment: Payment, gateway_data: dict) -> bool:
    """Mark a pending Payment as successful and update the invoice.

    Returns True if THIS call performed the PENDING -> SUCCESSFUL transition
    and credited the invoice; False if the payment was already processed by a
    concurrent request (the row is re-read under a row lock, so racing verify
    calls serialize here and only the first one credits the invoice).

    The amount the gateway recorded is verified against ``payment.amount`` by
    the caller before this is reached; this helper only guards the transition.
    """
    with transaction.atomic():
        # Re-read the payment row under FOR UPDATE so two concurrent verify
        # requests with the same transaction_id cannot both pass the earlier
        # status=PENDING lookup and double-credit the invoice.
        locked = Payment.objects.select_for_update().get(pk=payment.pk)
        if locked.status != Payment.Status.PENDING:
            logger.info(
                "Payment %s already processed (status=%s) — skipping duplicate credit",
                locked.receipt_number,
                locked.status,
            )
            return False

        invoice = FeeInvoice.objects.select_for_update().get(id=locked.invoice_id)

        locked.status = Payment.Status.SUCCESSFUL
        locked.paid_at = timezone.now()
        locked.gateway_response = {
            **(locked.gateway_response or {}),
            **gateway_data,
        }
        locked.save(update_fields=["status", "paid_at", "gateway_response"])

        from .ledger import credit_invoice

        credit_invoice(invoice, locked.amount)
        return True
