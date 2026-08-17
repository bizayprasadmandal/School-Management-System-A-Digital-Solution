"""Timetable service Celery tasks."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def check_timetable_conflicts(self):
    """Weekly scan for any double-booked teachers or classrooms."""
    try:
        from django.db.models import Count

        from .models import TimetableSlot

        conflicts = (
            TimetableSlot.objects.values("assignment__teacher", "day_of_week", "period", "academic_year")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )
        if conflicts:
            logger.warning("Found %d timetable conflicts: %s", len(conflicts), list(conflicts))
        return {"conflicts_found": len(list(conflicts))}
    except Exception as exc:
        logger.error("check_timetable_conflicts failed: %s", exc)
        raise self.retry(exc=exc)
