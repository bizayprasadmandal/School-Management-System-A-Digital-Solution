"""Students async tasks."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_enrollment_confirmation(self, student_id: str):
    from services.communication.services import send_in_app_notification

    from .models import Student

    try:
        student = Student.objects.select_related("user").get(id=student_id)
    except Student.DoesNotExist:
        logger.error("Enrollment confirmation skipped: student %s not found", student_id)
        return
    except Exception as exc:
        logger.error("Enrollment confirmation failed: %s", exc)
        raise self.retry(exc=exc)
    try:
        send_in_app_notification.delay(
            user_id=str(student.user.id),
            title="Enrollment Confirmed",
            body=f"Welcome to {student.school.name}! Your admission number is {student.admission_number}.",
        )
    except Exception as exc:
        logger.error("Enrollment confirmation failed: %s", exc)
        raise self.retry(exc=exc)
