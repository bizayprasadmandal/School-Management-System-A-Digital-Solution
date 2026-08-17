"""
Gradebook Service — Signal handlers
Notify students/parents when report cards are published or submissions graded.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="gradebook.ReportCard")
def handle_report_card_published(sender, instance, created, **kwargs):
    """Push notification when a report card moves to 'published'."""
    try:
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
            for sg in instance.student.studentguardian_set.filter(guardian__user__isnull=False, portal_access=True):
                send_in_app_notification.delay(
                    user_id=str(sg.guardian.user.id),
                    title="Report Card Available",
                    body=f"{instance.student.user.full_name}'s {instance.exam.name} result: "
                    f"{instance.percentage:.1f}% ({instance.grade_letter}). "
                    f"Rank #{instance.rank_in_class} in class.",
                    reference_type="report_card",
                    reference_id=str(instance.id),
                )
    except Exception:  # pragma: no cover — a notification must never break the request
        logger.exception("handle_report_card_published failed for report card %s", instance.id)


@receiver(post_save, sender="gradebook.AssessmentSubmission")
def handle_assessment_graded(sender, instance, created, **kwargs):
    """
    Push notification when an assessment submission receives a grade
    (marks_obtained is set).

    The whole body is guarded: a notification failure must never turn a grade
    save into a 500 (previously an AttributeError on `assessment.subject_name`
    — which does not exist on the model — crashed every graded submission).
    """
    try:
        # Only notify when marks_obtained is now set
        if instance.marks_obtained is None:
            return

        from services.communication.services import send_expo_push_notification, send_in_app_notification

        assessment = instance.assessment
        student = instance.student
        subject_name = assessment.assignment.subject.name
        assessment_type_label = assessment.get_assessment_type_display()

        # Compute percentage manually (AssessmentSubmission model has no percentage property)
        max_marks = assessment.max_marks
        percentage = (float(instance.marks_obtained) / float(max_marks) * 100) if max_marks and max_marks > 0 else None

        title = f"{assessment_type_label} Graded"
        if percentage is not None:
            body = (
                f"Your {assessment.title} ({subject_name}) has been graded: "
                f"{instance.marks_obtained}/{assessment.max_marks} ({percentage:.1f}%)"
            )
        else:
            body = f"Your {assessment.title} ({subject_name}) has been graded."
        push_data = {
            "route": "Assignments",
            "reference_type": "assessment_submission",
            "reference_id": str(instance.id),
        }

        # Notify student
        send_in_app_notification.delay(
            user_id=str(student.user.id),
            title=title,
            body=body,
            reference_type="assessment_submission",
            reference_id=str(instance.id),
        )
        send_expo_push_notification.delay(
            user_id=str(student.user.id),
            title=title,
            body=body,
            data=push_data,
        )

        # Notify parents
        for sg in student.studentguardian_set.filter(guardian__user__isnull=False, portal_access=True):
            parent_body = (
                f"{student.user.full_name}'s {assessment.title} "
                f"({subject_name}) has been graded: "
                f"{instance.marks_obtained}/{assessment.max_marks}"
            )
            send_in_app_notification.delay(
                user_id=str(sg.guardian.user.id),
                title=title,
                body=parent_body,
                reference_type="assessment_submission",
                reference_id=str(instance.id),
            )
            send_expo_push_notification.delay(
                user_id=str(sg.guardian.user.id),
                title=title,
                body=parent_body,
                data={
                    "route": "Assignments",
                    "reference_type": "assessment_submission",
                    "reference_id": str(instance.id),
                },
            )

        logger.info(
            "Graded notification sent for submission %s (%s)",
            instance.id,
            assessment.title,
        )
    except Exception:  # pragma: no cover — a notification must never break the request
        logger.exception("handle_assessment_graded failed for submission %s", instance.id)
