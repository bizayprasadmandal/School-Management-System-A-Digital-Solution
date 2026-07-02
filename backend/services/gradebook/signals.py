"""
Gradebook Service — Signal handlers
Notify students/parents when report cards are published.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender="gradebook.ReportCard")
def handle_report_card_published(sender, instance, created, **kwargs):
    """Push notification when a report card moves to 'published'."""
    if not created and instance.status == "published":
        from services.communication.services import send_in_app_notification

        student_user = instance.student.user
        send_in_app_notification.delay(
            user_id=str(student_user.id),
            title="Report Card Published",
            body=f"Your {instance.exam.name} report card is now available. "
                 f"You scored {instance.percentage:.1f}% — Grade {instance.grade_letter}.",
            reference_type="report_card",
            reference_id=str(instance.id),
        )
        # Notify parents
        for sg in instance.student.studentguardian_set.filter(
            guardian__user__isnull=False, portal_access=True
        ):
            send_in_app_notification.delay(
                user_id=str(sg.guardian.user.id),
                title="Report Card Available",
                body=f"{instance.student.user.full_name}'s {instance.exam.name} result: "
                     f"{instance.percentage:.1f}% ({instance.grade_letter}). "
                     f"Rank #{instance.rank_in_class} in class.",
                reference_type="report_card",
                reference_id=str(instance.id),
            )
