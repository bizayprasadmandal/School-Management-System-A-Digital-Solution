"""
Conference Service — Signal handlers
Notify teacher and parent when a conference slot is booked.
"""

import logging
from datetime import time as dtime

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _format_time(value):
    """
    Format a TimeField for display. On freshly-created instances the attribute
    may still hold the raw string ("09:00") because Django only converts on
    read-back from the DB, so coerce before strftime.
    """
    if isinstance(value, dtime):
        return value.strftime("%I:%M %p")
    try:
        return dtime.fromisoformat(str(value)).strftime("%I:%M %p")
    except ValueError:
        return str(value)


@receiver(post_save, sender="conferences.ConferenceSlot")
def handle_conference_booked(sender, instance, created, **kwargs):
    """
    Push notification when a conference slot is booked by a parent.
    Notifies the teacher and the booking parent.
    """
    if not instance.is_booked or not instance.booked_by:
        return

    from services.communication.services import send_expo_push_notification, send_in_app_notification

    teacher = instance.teacher
    parent = instance.booked_by
    student = instance.student

    student_name = student.user.full_name if student else "A student"
    date_str = instance.date.strftime("%b %d, %Y")
    time_str = f"{_format_time(instance.start_time)} – {_format_time(instance.end_time)}"

    push_data = {
        "route": "Conferences",
        "reference_type": "conference_slot",
        "reference_id": str(instance.id),
    }

    # ── Notify the teacher ──────────────────────────────────────────────────
    teacher_title = "New Conference Booked"
    teacher_body = f"{parent.full_name} booked a conference for {student_name} " f"on {date_str} at {time_str}."

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
        f"Your conference with {teacher.full_name} for {student_name} " f"has been booked for {date_str} at {time_str}."
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
        instance.id,
        teacher.id,
        parent.id,
    )
