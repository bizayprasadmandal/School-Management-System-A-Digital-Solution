"""Hostel Service — automated maintenance tasks.

Daily beat tasks:
- ``mark_overdue_hostel_payments``: pending/partial hostel fee payments
  past due flip to overdue (idempotent — only those rows transition).
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def mark_overdue_hostel_payments(self, school_id=None):
    """Flip pending/partial hostel fee payments past their due date to overdue."""
    from services.hostel.models import HostelFeePayment

    today = timezone.now().date()
    qs = HostelFeePayment.objects.filter(
        status__in=[HostelFeePayment.Status.PENDING, HostelFeePayment.Status.PARTIAL],
        due_date__lt=today,
    )
    if school_id is not None:
        qs = qs.filter(school_id=school_id)

    updated = qs.update(status=HostelFeePayment.Status.OVERDUE)
    logger.info(
        "mark_overdue_hostel_payments completed",
        extra={"overdue_marked": updated, "cutoff_date": str(today)},
    )
    return {"overdue_marked": updated}
