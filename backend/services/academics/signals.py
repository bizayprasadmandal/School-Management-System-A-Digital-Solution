"""Academics signals — notify teacher on new assignment."""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender="academics.TeacherAssignment")
def handle_assignment_created(sender, instance, created, **kwargs):
    if created:
        from services.communication.services import send_in_app_notification
        send_in_app_notification.delay(
            user_id=str(instance.teacher.id),
            title="New Teaching Assignment",
            body=f"You have been assigned to teach {instance.subject.name} for {instance.classroom}.",
            reference_type="assignment", reference_id=str(instance.id),
        )
