"""
Fees Service — Invoice ledger helpers.

The credit/debit of ``FeeInvoice.paid_amount`` and the resulting status
recalculation used to be copy-pasted in five places (manual payment create,
Stripe webhook success, Stripe refund, Khalti/eSewa verify success, and the
Nepali refund flow). These helpers own that logic so every path stays
consistent.

Callers are responsible for holding the Payment row lock when the amount
moves in reaction to a gateway event; these helpers lock the invoice row
inside the caller's transaction so concurrent payments against the same
invoice serialize.

Audit trail: every successful credit/debit also writes a ``TransactionLog``
row (and, for refunds, a ``RefundRecord`` + revenue-reversal ``AccountingEntry``;
for payments, a revenue ``AccountingEntry``). Audit writes are idempotent —
keyed on unique transaction ids (``PAY-<id>`` / ``RFD-<id>``) — so webhook
retries and duplicate verifies never double-log. Passing ``payment=None``
(the seeders' style) skips audit writes entirely.
"""

import logging

from django.db import transaction
from django.utils import timezone

from .models import AccountingEntry, FeeInvoice, RefundRecord, TransactionLog

logger = logging.getLogger(__name__)

# Chart-of-accounts codes used for the auto-posted revenue entries.
REVENUE_ACCOUNT_CODE = "4000"
REVENUE_ACCOUNT_NAME = "Fee Revenue"


def post_revenue(
    *,
    school,
    amount,
    reference_type: str,
    reference_id: str,
    description: str,
    student=None,
    payment_method: str = "",
    transaction_type: str = TransactionLog.TransactionType.PAYMENT,
    user=None,
) -> None:
    """Post one revenue payment to the books — for non-fee money streams.

    Used by transport, hostel, and cafeteria flows so their collections hit
    the same ``TransactionLog`` + ``AccountingEntry`` audit trail as fee
    payments. Idempotent via get_or_create on the (reference_type,
    reference_id) pair — calling twice with the same reference never
    double-posts.
    """
    AccountingEntry.objects.get_or_create(
        school=school,
        reference_type=reference_type,
        reference_id=reference_id,
        entry_type=AccountingEntry.EntryType.CREDIT,
        defaults={
            "account_code": REVENUE_ACCOUNT_CODE,
            "account_name": REVENUE_ACCOUNT_NAME,
            "description": description[:200],
            "amount": amount,
            "entry_date": timezone.now().date(),
            "created_by": user,
        },
    )
    TransactionLog.objects.get_or_create(
        transaction_id=f"{reference_type.upper()}-{reference_id}",
        defaults={
            "school": school,
            "transaction_type": transaction_type,
            "student": student,
            "amount": amount,
            "payment_method": payment_method[:50],
            "reference_number": reference_id,
            "status": "success",
            "description": description,
        },
    )


def _recalculate_status(invoice: FeeInvoice) -> None:
    """Recompute invoice status from paid_amount, flooring at zero."""
    if invoice.paid_amount <= 0:
        invoice.paid_amount = 0
        invoice.status = FeeInvoice.Status.UNPAID
    elif invoice.paid_amount >= invoice.total_amount:
        invoice.status = FeeInvoice.Status.PAID
    else:
        invoice.status = FeeInvoice.Status.PARTIAL
    invoice.save(update_fields=["paid_amount", "status"])


def _log_transaction(
    *,
    school_id,
    student_id,
    transaction_type: str,
    transaction_id: str,
    amount,
    description: str,
    payment_method: str = "",
    reference_number: str = "",
    metadata: dict | None = None,
) -> None:
    """Idempotently write a TransactionLog row (unique on transaction_id)."""
    TransactionLog.objects.get_or_create(
        transaction_id=transaction_id,
        defaults={
            "school_id": school_id,
            "student_id": student_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "payment_method": payment_method,
            "reference_number": reference_number,
            "status": "success",
            "description": description,
            "metadata": metadata or {},
        },
    )


def _post_revenue_entry(
    *,
    school_id,
    entry_type: str,
    amount,
    reference_type: str,
    reference_id: str,
    description: str,
    user=None,
) -> None:
    """Idempotently post a revenue AccountingEntry for a payment/refund."""
    AccountingEntry.objects.get_or_create(
        school_id=school_id,
        reference_type=reference_type,
        reference_id=reference_id,
        entry_type=entry_type,
        defaults={
            "account_code": REVENUE_ACCOUNT_CODE,
            "account_name": REVENUE_ACCOUNT_NAME,
            "description": description[:200],
            "amount": amount,
            "entry_date": timezone.now().date(),
            "created_by": user,
        },
    )


def credit_invoice(
    invoice: FeeInvoice,
    amount,
    *,
    payment=None,
    user=None,
) -> FeeInvoice:
    """Lock the invoice row and add ``amount`` to paid_amount.

    Returns the re-fetched, locked invoice so callers can read the updated
    status/balance inside the same transaction.

    When ``payment`` is provided, also writes the audit trail: a
    ``TransactionLog`` (type=payment) and a credit ``AccountingEntry`` on the
    Fee Revenue account.
    """
    with transaction.atomic():
        locked = FeeInvoice.objects.select_for_update().get(pk=invoice.pk)
        locked.paid_amount += amount
        _recalculate_status(locked)
        logger.info(
            "Invoice %s credited %s (paid=%s, status=%s)",
            locked.invoice_number,
            amount,
            locked.paid_amount,
            locked.status,
        )

        if payment is not None:
            _log_transaction(
                school_id=locked.student.school_id,
                student_id=locked.student_id,
                transaction_type=TransactionLog.TransactionType.PAYMENT,
                transaction_id=f"PAY-{payment.id}",
                amount=amount,
                description=(f"Payment {payment.receipt_number} received for invoice " f"{locked.invoice_number}"),
                payment_method=payment.payment_method,
                reference_number=payment.receipt_number,
                metadata={"invoice_number": locked.invoice_number},
            )
            _post_revenue_entry(
                school_id=locked.student.school_id,
                entry_type=AccountingEntry.EntryType.CREDIT,
                amount=amount,
                reference_type="payment",
                reference_id=str(payment.id),
                description=(f"Fee revenue — payment {payment.receipt_number} for " f"invoice {locked.invoice_number}"),
                user=user,
            )

        return locked


def debit_invoice(
    invoice: FeeInvoice,
    amount,
    *,
    payment=None,
    reason: str = "",
    user=None,
) -> FeeInvoice:
    """Lock the invoice row and subtract ``amount`` (never below zero).

    Returns the re-fetched, locked invoice so callers can read the updated
    status/balance inside the same transaction.

    When ``payment`` is provided, also writes the audit trail: a
    ``TransactionLog`` (type=refund), a ``RefundRecord`` (status=processed,
    approved_by=user), and a debit ``AccountingEntry`` reversing the revenue.
    """
    with transaction.atomic():
        locked = FeeInvoice.objects.select_for_update().get(pk=invoice.pk)
        locked.paid_amount -= amount
        _recalculate_status(locked)
        logger.info(
            "Invoice %s debited %s (paid=%s, status=%s)",
            locked.invoice_number,
            amount,
            locked.paid_amount,
            locked.status,
        )

        if payment is not None:
            school_id = locked.student.school_id
            _log_transaction(
                school_id=school_id,
                student_id=locked.student_id,
                transaction_type=TransactionLog.TransactionType.REFUND,
                transaction_id=f"RFD-{payment.id}",
                amount=amount,
                description=(
                    f"Refund of payment {payment.receipt_number} on invoice "
                    f"{locked.invoice_number}" + (f": {reason}" if reason else "")
                ),
                payment_method=payment.payment_method,
                reference_number=payment.receipt_number,
                metadata={
                    "invoice_number": locked.invoice_number,
                    "refunded_by": user.full_name if user else "",
                    "reason": reason,
                },
            )
            RefundRecord.objects.get_or_create(
                payment=payment,
                defaults={
                    "school_id": school_id,
                    "student_id": locked.student_id,
                    "invoice": locked,
                    "amount": amount,
                    "reason": reason or f"Refund of payment {payment.receipt_number}",
                    "status": RefundRecord.Status.PROCESSED,
                    "processed_date": timezone.now().date(),
                    "refund_method": payment.payment_method,
                    "approved_by": user,
                    "notes": f"Auto-created by refund of {payment.receipt_number}",
                },
            )
            _post_revenue_entry(
                school_id=school_id,
                entry_type=AccountingEntry.EntryType.DEBIT,
                amount=amount,
                reference_type="refund",
                reference_id=str(payment.id),
                description=(
                    f"Revenue reversal — refund of payment "
                    f"{payment.receipt_number} on invoice {locked.invoice_number}"
                ),
                user=user,
            )

        return locked
