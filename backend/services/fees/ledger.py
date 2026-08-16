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
"""

import logging

from django.db import transaction

from .models import FeeInvoice

logger = logging.getLogger(__name__)


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


def credit_invoice(invoice: FeeInvoice, amount) -> FeeInvoice:
    """Lock the invoice row and add ``amount`` to paid_amount.

    Returns the re-fetched, locked invoice so callers can read the updated
    status/balance inside the same transaction.
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
        return locked


def debit_invoice(invoice: FeeInvoice, amount) -> FeeInvoice:
    """Lock the invoice row and subtract ``amount`` (never below zero).

    Returns the re-fetched, locked invoice so callers can read the updated
    status/balance inside the same transaction.
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
        return locked
