"""
Academics signals — trigger notifications for key academic events.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Original: Teacher Assignment created
# ---------------------------------------------------------------------------


@receiver(post_save, sender="academics.TeacherAssignment")
def handle_assignment_created(sender, instance, created, **kwargs):
    """Notify teacher when assigned to a new subject-classroom."""
    if created:
        from services.communication.services import send_in_app_notification

        send_in_app_notification.delay(
            user_id=str(instance.teacher.id),
            title="New Teaching Assignment",
            body=f"You have been assigned to teach {instance.subject.name} for {instance.classroom}.",
            reference_type="teacher_assignment",
            reference_id=str(instance.id),
        )


# ---------------------------------------------------------------------------
# Lesson Plan approval/rejection
# ---------------------------------------------------------------------------


@receiver(post_save, sender="academics.LessonPlan")
def handle_lesson_plan_status_change(sender, instance, **kwargs):
    """Notify teacher when lesson plan is approved or rejected."""
    if instance.status == "approved":
        from services.communication.services import send_in_app_notification

        send_in_app_notification.delay(
            user_id=str(instance.assignment.teacher.id),
            title="Lesson Plan Approved",
            body=f"Your lesson plan '{instance.title}' has been approved.",
            reference_type="lesson_plan",
            reference_id=str(instance.id),
        )
    elif instance.status == "completed":
        from services.communication.services import send_in_app_notification

        send_in_app_notification.delay(
            user_id=str(instance.assignment.teacher.id),
            title="Lesson Plan Completed",
            body=f"Your lesson plan '{instance.title}' has been marked as completed.",
            reference_type="lesson_plan",
            reference_id=str(instance.id),
        )


# ---------------------------------------------------------------------------
# Syllabus approval/rejection
# ---------------------------------------------------------------------------


@receiver(post_save, sender="academics.Syllabus")
def handle_syllabus_status_change(sender, instance, **kwargs):
    """Notify teacher when syllabus is approved or rejected."""
    if instance.status == "approved" and instance.approved_by:
        from services.communication.services import send_in_app_notification

        send_in_app_notification.delay(
            user_id=str(instance.created_by.id),
            title="Syllabus Approved",
            body=f"Your syllabus '{instance.title}' has been approved by {instance.approved_by.full_name}.",
            reference_type="syllabus",
            reference_id=str(instance.id),
        )
    elif instance.status == "rejected":
        from services.communication.services import send_in_app_notification

        send_in_app_notification.delay(
            user_id=str(instance.created_by.id),
            title="Syllabus Rejected",
            body=f"Your syllabus '{instance.title}' has been rejected. Reason: {instance.rejection_reason[:100]}",
            reference_type="syllabus",
            reference_id=str(instance.id),
        )


# ---------------------------------------------------------------------------
# Teacher Evaluation status changes
# ---------------------------------------------------------------------------


@receiver(post_save, sender="academics.TeacherEvaluation")
def handle_evaluation_status_change(sender, instance, **kwargs):
    """Notify teacher on evaluation status changes."""
    from services.communication.services import send_in_app_notification

    status_messages = {
        "self_review": "An evaluation has been created and is awaiting your self-review.",
        "peer_review": "Your self-review has been submitted. Awaiting peer review.",
        "admin_review": "Peer review complete. Awaiting admin review.",
        "completed": f"Evaluation completed with score: {instance.score_display}",
    }

    message = status_messages.get(instance.status)
    if message:
        send_in_app_notification.delay(
            user_id=str(instance.teacher.id),
            title=f"Evaluation: {instance.get_status_display()}",
            body=f"{instance.title} — {message}",
            reference_type="teacher_evaluation",
            reference_id=str(instance.id),
        )


# ---------------------------------------------------------------------------
# Academic Transcript generated/verified
# ---------------------------------------------------------------------------


@receiver(post_save, sender="academics.AcademicTranscript")
def handle_transcript_status_change(sender, instance, **kwargs):
    """Notify student when transcript is generated or verified."""
    from services.communication.services import send_in_app_notification

    if instance.status == "generated":
        send_in_app_notification.delay(
            user_id=str(instance.student.user.id),
            title="Transcript Ready",
            body=f"Your academic transcript ({instance.transcript_number}) has been generated.",
            reference_type="academic_transcript",
            reference_id=str(instance.id),
        )
    elif instance.status == "verified":
        send_in_app_notification.delay(
            user_id=str(instance.student.user.id),
            title="Transcript Verified",
            body=f"Your academic transcript ({instance.transcript_number}) has been verified and is official.",
            reference_type="academic_transcript",
            reference_id=str(instance.id),
        )


# ---------------------------------------------------------------------------
# Enrollment Intent created
# ---------------------------------------------------------------------------


@receiver(post_save, sender="academics.EnrollmentIntent")
def handle_enrollment_intent_created(sender, instance, created, **kwargs):
    """Notify admin when a new enrollment intent is created."""
    if created:
        # Notify school admins
        from services.auth.models import User
        from services.communication.services import send_in_app_notification

        admins = User.objects.filter(
            school=instance.catalog_entry.subject.school,
            role="school_admin",
            is_active=True,
        )
        for admin in admins:
            send_in_app_notification.delay(
                user_id=str(admin.id),
                title="New Enrollment Interest",
                body=f"Student {instance.student} is interested in {instance.catalog_entry.subject.name}.",
                reference_type="enrollment_intent",
                reference_id=str(instance.id),
            )
