"""
Counseling Service — Celery tasks for reminders and notifications.
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from services.communication.models import Notification

logger = logging.getLogger(__name__)


@shared_task
def send_appointment_reminders():
    """Send reminders for appointments scheduled for tomorrow.

    Runs daily (configure via Celery Beat schedule in settings).
    """
    from .models import CounselingAppointment

    tomorrow = timezone.now().date() + timedelta(days=1)

    upcoming = CounselingAppointment.objects.filter(
        scheduled_date=tomorrow,
        status__in=["scheduled", "in_progress"],
        school__is_active=True,
    ).select_related("student__user", "counselor", "school")

    sent_count = 0
    for appointment in upcoming:
        try:
            # Notify the student
            Notification.objects.create(
                user=appointment.student.user,
                title="Upcoming Counseling Appointment",
                body=(
                    f"Reminder: You have a {appointment.get_appointment_type_display()} "
                    f"appointment tomorrow ({appointment.scheduled_date}) "
                    f"at {appointment.scheduled_time}."
                ),
                channel="in_app",
                status="sent",
                reference_type="appointment_reminder",
                reference_id=str(appointment.id),
            )
            # Notify the counselor
            Notification.objects.create(
                user=appointment.counselor,
                title="Upcoming Counseling Appointment",
                body=(
                    f"Reminder: You have a {appointment.get_appointment_type_display()} "
                    f"appointment with {appointment.student.user.full_name} "
                    f"tomorrow ({appointment.scheduled_date}) at {appointment.scheduled_time}."
                ),
                channel="in_app",
                status="sent",
                reference_type="appointment_reminder",
                reference_id=str(appointment.id),
            )
            sent_count += 1
        except Exception as e:
            logger.error(
                "Failed to send reminder for appointment %s: %s",
                appointment.id,
                e,
            )

    logger.info("Sent %d appointment reminder notifications", sent_count)
    return {"reminders_sent": sent_count}


@shared_task
def send_pending_referral_reminders():
    """Remind counselors about referrals that have been pending for 3+ days."""
    from .models import StudentReferral

    threshold = timezone.now() - timedelta(days=3)

    stale_referrals = StudentReferral.objects.filter(
        created_at__lte=threshold,
        status__in=["pending", "under_review"],
        school__is_active=True,
    ).select_related("student__user", "assigned_to", "school")

    sent_count = 0
    for referral in stale_referrals:
        if not referral.assigned_to:
            continue
        try:
            Notification.objects.create(
                user=referral.assigned_to,
                title="Pending Referral Needs Attention",
                body=(
                    f"A {referral.get_priority_display()} priority referral for "
                    f"{referral.student.user.full_name} has been pending for over 3 days."
                ),
                channel="in_app",
                status="sent",
                reference_type="referral_reminder",
                reference_id=str(referral.id),
            )
            sent_count += 1
        except Exception as e:
            logger.error("Failed to send referral reminder: %s", e)

    logger.info("Sent %d pending referral reminders", sent_count)
    return {"reminders_sent": sent_count}
