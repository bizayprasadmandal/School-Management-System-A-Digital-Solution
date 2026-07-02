"""
Students Service — Signal handlers
Auto-create guardian portal account when student is enrolled.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender="students.Enrollment")
def handle_enrollment_created(sender, instance, created, **kwargs):
    """When a student is enrolled, ensure their user account is active."""
    if created:
        student = instance.student
        if not student.user.is_active:
            student.user.is_active = True
            student.user.save(update_fields=["is_active"])
        logger.info("Student %s enrolled in %s", student.admission_number, instance.classroom)


@receiver(post_save, sender="students.StudentGuardian")
def handle_guardian_linked(sender, instance, created, **kwargs):
    """Send welcome notification to guardian when portal access is granted."""
    if created and instance.portal_access and instance.guardian.user:
        from services.communication.services import send_in_app_notification
        send_in_app_notification.delay(
            user_id=str(instance.guardian.user.id),
            title="Portal Access Granted",
            body=f"You now have access to {instance.student.user.full_name}'s academic profile.",
        )
