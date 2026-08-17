"""Academics async tasks."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_lesson_plan_approved(self, plan_id: int):
    from services.communication.services import send_in_app_notification

    from .models import LessonPlan

    try:
        plan = LessonPlan.objects.select_related("assignment__teacher").get(id=plan_id)
    except LessonPlan.DoesNotExist:
        logger.error("Lesson plan approval notify skipped: plan %s not found", plan_id)
        return
    except Exception as exc:
        logger.error("Lesson plan approval notify failed: %s", exc)
        raise self.retry(exc=exc)
    try:
        send_in_app_notification.delay(
            user_id=str(plan.assignment.teacher.id),
            title="Lesson Plan Approved",
            body=f'Your lesson plan "{plan.title}" for {plan.date} has been approved.',
        )
    except Exception as exc:
        logger.error("Lesson plan approval notify failed: %s", exc)
        raise self.retry(exc=exc)
