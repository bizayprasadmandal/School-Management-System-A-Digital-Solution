"""
Fees Service — Signal handlers
Notify guardians and students when invoices become overdue or payments are received.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender="fees.Payment")
def handle_payment_recorded(sender, instance, created, **kwargs):
    """Send payment receipt notification on successful payment."""
    if created and instance.status == "successful":
        from services.communication.services import send_in_app_notification, send_email_notification

        student_user = instance.invoice.student.user
        amount = f"${instance.amount:,.2f}"
        msg = (
            f"Payment of {amount} received for invoice "
            f"#{instance.invoice.invoice_number}. Receipt: {instance.receipt_number}."
        )
        send_in_app_notification.delay(
            user_id=str(student_user.id),
            title="Payment Confirmed",
            body=msg,
            reference_type="payment",
            reference_id=str(instance.id),
        )
        send_email_notification.delay(
            user_id=str(student_user.id),
            subject=f"Payment Receipt — {instance.receipt_number}",
            body=msg,
        )
        logger.info("Payment receipt sent for %s", instance.receipt_number)


@receiver(post_save, sender="fees.FeeInvoice")
def handle_invoice_overdue(sender, instance, created, **kwargs):
    """Push overdue notification when invoice status transitions to 'overdue'."""
    if not created and instance.status == "overdue":
        from services.communication.services import send_in_app_notification
        send_in_app_notification.delay(
            user_id=str(instance.student.user.id),
            title="Fee Payment Overdue",
            body=f"Invoice #{instance.invoice_number} of ${instance.outstanding_amount:,.2f} "
                 f"is now overdue. Please pay immediately to avoid penalties.",
            reference_type="fee_invoice",
            reference_id=str(instance.id),
        )
