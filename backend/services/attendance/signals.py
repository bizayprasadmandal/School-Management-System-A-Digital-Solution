"""
Attendance Service — Signal handlers
Trigger guardian notifications when attendance is recorded as Absent.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender="attendance.AttendanceRecord")
def handle_attendance_saved(sender, instance, created, **kwargs):
    """Queue guardian notification for absent students."""
    if instance.status == "A" and not instance.notified_guardian:
        from .tasks import notify_absent_guardians
        notify_absent_guardians.delay(str(instance.id))
