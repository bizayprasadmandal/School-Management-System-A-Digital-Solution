"""Fees Service — Celery tasks (imported from gradebook tasks for bulk invoice generation)"""
from services.gradebook.tasks import generate_bulk_invoices  # re-export

from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def mark_overdue_invoices():
    """Mark unpaid invoices as overdue when past due date."""
    from .models import FeeInvoice
    today = timezone.now().date()
    updated = FeeInvoice.objects.filter(
        status="unpaid", due_date__lt=today
    ).update(status="overdue")
    logger.info("Marked %d invoices as overdue", updated)
    return {"marked_overdue": updated}

@shared_task
def send_fee_reminders():
    """Send reminders for invoices due in 3 days."""
    from .models import FeeInvoice
    from services.communication.services import send_in_app_notification
    from datetime import timedelta
    reminder_date = timezone.now().date() + timedelta(days=3)
    invoices = FeeInvoice.objects.filter(
        status__in=["unpaid", "partial"],
        due_date=reminder_date,
    ).select_related("student__user")
    count = 0
    for invoice in invoices:
        send_in_app_notification.delay(
            user_id=str(invoice.student.user.id),
            title="Fee Payment Reminder",
            body=f"Your fee payment of ${invoice.outstanding_amount:,.2f} "
                 f"(Invoice #{invoice.invoice_number}) is due in 3 days.",
            reference_type="fee_invoice",
            reference_id=str(invoice.id),
        )
        count += 1
    logger.info("Sent %d fee reminders for due date %s", count, reminder_date)
    return {"reminders_sent": count}
