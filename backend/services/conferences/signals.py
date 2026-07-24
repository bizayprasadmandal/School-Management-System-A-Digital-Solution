"""
Conference Service — Signal handlers
Notify teacher and parent when a conference slot is booked.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender="conferences.ConferenceSlot")
def handle_conference_booked(sender, instance, created, **kwargs):
    """
    Push notification when a conference slot is booked by a parent.
    Notifies the teacher and the booking parent.
    """
    if not instance.is_booked or not instance.booked_by:
        return

    from services.communication.services import send_in_app_notification, send_expo_push_notification

    teacher = instance.teacher
    parent = instance.booked_by
    student = instance.student

    student_name = student.user.full_name if student else "A student"
    date_str = instance.date.strftime("%b %d, %Y")
    time_str = f"{instance.start_time:%I:%M %p} – {instance.end_time:%I:%M %p}"

    push_data = {
        "route": "Conferences",
        "reference_type": "conference_slot",
        "reference_id": str(instance.id),
    }

    # ── Notify the teacher ──────────────────────────────────────────────────
    teacher_title = "New Conference Booked"
    teacher_body = (
        f"{parent.full_name} booked a conference for {student_name} "
        f"on {date_str} at {time_str}."
    )

    send_in_app_notification.delay(
        user_id=str(teacher.id),
        title=teacher_title,
        body=teacher_body,
        reference_type="conference_slot",
        reference_id=str(instance.id),
    )
    send_expo_push_notification.delay(
        user_id=str(teacher.id),
        title=teacher_title,
        body=teacher_body,
        data=push_data,
    )

    # ── Notify the parent who booked ────────────────────────────────────────
    parent_title = "Conference Booked"
    parent_body = (
        f"Your conference with {teacher.full_name} for {student_name} "
        f"has been booked for {date_str} at {time_str}."
    )

    send_in_app_notification.delay(
        user_id=str(parent.id),
        title=parent_title,
        body=parent_body,
        reference_type="conference_slot",
        reference_id=str(instance.id),
    )
    send_expo_push_notification.delay(
        user_id=str(parent.id),
        title=parent_title,
        body=parent_body,
        data=push_data,
    )

    logger.info(
        "Conference booked notification sent for slot %s (teacher=%s, parent=%s)",
        instance.id, teacher.id, parent.id,
    )
