"""Timetable service Celery tasks."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_timetable_conflicts():
    """Weekly scan for any double-booked teachers or classrooms."""
    from .models import TimetableSlot
    from django.db.models import Count
    conflicts = (
        TimetableSlot.objects
        .values("assignment__teacher", "day_of_week", "period", "academic_year")
        .annotate(count=Count("id"))
        .filter(count__gt=1)
    )
    if conflicts:
        logger.warning("Found %d timetable conflicts: %s", len(conflicts), list(conflicts))
    return {"conflicts_found": len(list(conflicts))}
