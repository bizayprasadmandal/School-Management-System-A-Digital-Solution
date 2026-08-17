"""
Attendance Service — Signal handlers
Trigger guardian notifications when attendance is recorded as Absent.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="attendance.AttendanceRecord")
def handle_attendance_saved(sender, instance, created, **kwargs):
    """Queue guardian notification for absent students."""
    if instance.status == "A" and not instance.notified_guardian:
        from .tasks import notify_absent_guardians

        notify_absent_guardians.delay(str(instance.id))

    # Keep the reporting dashboard cache fresh — attendance KPIs are cached for
    # 5 minutes and the frontend never calls the manual refresh endpoint.
    try:
        from django.core.cache import cache

        school_id = instance.student.school_id
        if school_id:
            cache.delete(f"dashboard_stats_{school_id}")
    except Exception:  # pragma: no cover — invalidation must never break writes
        logger.warning("dashboard stats cache invalidation failed", exc_info=True)
