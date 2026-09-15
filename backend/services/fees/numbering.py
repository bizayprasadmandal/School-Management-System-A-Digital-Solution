"""
Sequential number generation for invoices and receipts.

Format:
  Invoice:  INV-YYYYMM-XXXX  (e.g. INV-202609-0001)
  Receipt:  RCPT-YYYYMM-XXXX (e.g. RCPT-202609-0001)

Uses database-level atomicity to guarantee uniqueness and sequential order.
"""

from django.db import transaction


def generate_invoice_number(school) -> str:
    """
    Generate next sequential invoice number for a school: INV-YYYYMM-XXXX.

    Uses SELECT FOR UPDATE to prevent race conditions between concurrent
    invoice creation requests for the same school.
    """
    from django.utils import timezone

    from .models import FeeInvoice

    period = timezone.now().strftime("%Y%m")
    prefix = f"INV-{period}-"

    with transaction.atomic():
        # Find the highest existing sequence number for this school + period
        last_invoice = (
            FeeInvoice.objects.select_for_update()
            .filter(
                student__school=school,
                invoice_number__startswith=prefix,
            )
            .order_by("-invoice_number")
            .values_list("invoice_number", flat=True)
            .first()
        )

        if last_invoice and last_invoice.startswith(prefix):
            seq_str = last_invoice.split("-")[-1]
            try:
                seq = int(seq_str) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1

        return f"{prefix}{seq:04d}"


def generate_receipt_number(school) -> str:
    """
    Generate next sequential receipt number for a school: RCPT-YYYYMM-XXXX.

    Uses SELECT FOR UPDATE to prevent race conditions between concurrent
    payment creation requests for the same school.
    """
    from django.utils import timezone

    from .models import Payment

    period = timezone.now().strftime("%Y%m")
    prefix = f"RCPT-{period}-"

    with transaction.atomic():
        last_receipt = (
            Payment.objects.select_for_update()
            .filter(
                invoice__student__school=school,
                receipt_number__startswith=prefix,
            )
            .order_by("-receipt_number")
            .values_list("receipt_number", flat=True)
            .first()
        )

        if last_receipt and last_receipt.startswith(prefix):
            seq_str = last_receipt.split("-")[-1]
            try:
                seq = int(seq_str) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1

        return f"{prefix}{seq:04d}"
