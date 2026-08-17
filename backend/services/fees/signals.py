"""
Fees Service — Signal handlers
Notify guardians and students when payments are received, and keep the
reporting dashboard cache fresh after money movements.
"""

import logging

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _invalidate_dashboard_cache(school_id):
    """Drop the school's dashboard-stats / at-risk caches after a write.

    The reporting endpoints cache for 5 minutes and the frontend never calls
    the manual refresh endpoint, so without invalidation KPIs go stale right
    after payments/attendance are recorded.
    """
    if not school_id:
        return
    cache.delete(f"dashboard_stats_{school_id}")
    # at_risk keys include the query params (threshold/days), so use a pattern
    # delete where the backend supports it (Redis); other backends expire by TTL.
    deleter = getattr(cache, "delete_pattern", None)
    if deleter is not None:
        try:
            deleter(f"at_risk_students_{school_id}_*")
        except Exception:  # pragma: no cover — invalidation must never break writes
            logger.warning("dashboard at-risk cache pattern delete failed", exc_info=True)


@receiver(post_save, sender="fees.Payment")
def handle_payment_recorded(sender, instance, created, **kwargs):
    """Send payment receipt notification on successful payment."""
    if created and instance.status == "successful":
        from services.communication.services import send_email_notification, send_in_app_notification

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

    _invalidate_dashboard_cache(instance.invoice.student.school_id)


@receiver(post_save, sender="fees.FeeInvoice")
def handle_invoice_changed(sender, instance, **kwargs):
    """Keep the dashboard fee KPI cache fresh after any invoice change.

    NOTE: overdue notification is intentionally NOT handled here. The
    `mark_overdue_invoices` Celery task owns that flow and already sends the
    student + parent notifications; a post_save signal on status=overdue fired
    on EVERY save (not just the transition), so students received two identical
    "Fee Payment Overdue" in-app notifications per invoice.
    """
    try:
        school_id = instance.student.school_id
    except Exception:  # pragma: no cover — student relation always exists
        school_id = None
    _invalidate_dashboard_cache(school_id)
