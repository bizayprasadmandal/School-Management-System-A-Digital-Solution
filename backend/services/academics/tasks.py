"""Academics async tasks."""
from celery import shared_task
import logging
logger = logging.getLogger(__name__)

@shared_task
def notify_lesson_plan_approved(plan_id: int):
    from .models import LessonPlan
    from services.communication.services import send_in_app_notification
    try:
        plan = LessonPlan.objects.select_related("assignment__teacher").get(id=plan_id)
        send_in_app_notification.delay(
            user_id=str(plan.assignment.teacher.id),
            title="Lesson Plan Approved",
            body=f"Your lesson plan \"{plan.title}\" for {plan.date} has been approved.",
        )
    except Exception as e:
        logger.error("Lesson plan approval notify failed: %s", e)
