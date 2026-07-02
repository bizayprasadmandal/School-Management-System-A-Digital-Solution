"""Students async tasks."""
from celery import shared_task
import logging
logger = logging.getLogger(__name__)

@shared_task
def send_enrollment_confirmation(student_id: str):
    from .models import Student
    from services.communication.services import send_in_app_notification
    try:
        student = Student.objects.select_related("user").get(id=student_id)
        send_in_app_notification.delay(
            user_id=str(student.user.id),
            title="Enrollment Confirmed",
            body=f"Welcome to {student.school.name}! Your admission number is {student.admission_number}.",
        )
    except Exception as e:
        logger.error("Enrollment confirmation failed: %s", e)
