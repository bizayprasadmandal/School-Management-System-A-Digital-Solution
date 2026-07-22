"""
Counseling Service — Signal handlers for automated notifications.

Triggers:
- When a referral is created, notify the assigned counselor
- When an appointment status changes, notify the student/counselor
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StudentReferral, CounselingAppointment
from services.communication.models import Notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=StudentReferral)
def notify_referral_created(sender, instance, created, **kwargs):
    """Notify the assigned counselor when a new referral is created."""
    if not created or not instance.assigned_to:
        return

    try:
        Notification.objects.create(
            user=instance.assigned_to,
            title="New Student Referral",
            body=(
                f"A new {instance.get_priority_display()} priority "
                f"{instance.get_category_display()} referral has been created for "
                f"{instance.student.user.full_name}."
            ),
            channel="in_app",
            status="sent",
            reference_type="referral",
            reference_id=str(instance.id),
        )
        logger.info(
            "Referral %s notification sent to counselor %s",
            instance.id, instance.assigned_to.email,
        )
    except Exception as e:
        logger.error("Failed to send referral notification: %s", e)


@receiver(post_save, sender=CounselingAppointment)
def notify_appointment_status_change(sender, instance, created, **kwargs):
    """Notify the student when an appointment status changes."""
    if created:
        return  # Student will be notified by the counselor directly

    # Only notify on status changes
    try:
        Notification.objects.create(
            user=instance.student.user,
            title=f"Appointment {instance.get_status_display()}",
            body=(
                f"Your {instance.get_appointment_type_display()} appointment "
                f"on {instance.scheduled_date} is now "
                f"{instance.get_status_display().lower()}."
            ),
            channel="in_app",
            status="sent",
            reference_type="appointment",
            reference_id=str(instance.id),
        )
    except Exception as e:
        logger.error("Failed to send appointment status notification: %s", e)
