"""
HR Service — Signals for notifications on key HR events.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="hr.LeaveRequest")
def handle_leave_request_status_change(sender, instance, **kwargs):
    """Notify employee when leave request is approved or rejected."""
    from services.communication.services import send_in_app_notification

    if instance.status == "approved":
        leave_type = instance.get_leave_type_display()
        period = f"{instance.from_date} to {instance.to_date}"
        send_in_app_notification.delay(
            user_id=str(instance.employee.user.id),
            title="Leave Request Approved",
            body=f"Your {leave_type} request ({period}) has been approved.",
            reference_type="leave_request",
            reference_id=str(instance.id),
        )
    elif instance.status == "rejected":
        reason = instance.review_notes[:100]
        leave_type = instance.get_leave_type_display()
        send_in_app_notification.delay(
            user_id=str(instance.employee.user.id),
            title="Leave Request Rejected",
            body=f"Your {leave_type} request rejected. Reason: {reason}",
            reference_type="leave_request",
            reference_id=str(instance.id),
        )


@receiver(post_save, sender="hr.PerformanceReview")
def handle_performance_review_status_change(sender, instance, **kwargs):
    """Notify employee on review status changes."""
    from services.communication.services import send_in_app_notification

    status_messages = {
        "self_review": "A performance review has been created. Please complete your self-assessment.",
        "manager_review": "Your self-assessment has been submitted. Awaiting manager review.",
        "hr_review": "Manager review complete. Awaiting HR review.",
        "completed": f"Your performance review is complete. Rating: {instance.rating_display}",
    }

    message = status_messages.get(instance.status)
    if message:
        send_in_app_notification.delay(
            user_id=str(instance.employee.user.id),
            title=f"Performance Review: {instance.get_status_display()}",
            body=f"{instance.cycle.name} — {message}",
            reference_type="performance_review",
            reference_id=str(instance.id),
        )


@receiver(post_save, sender="hr.Certification")
def handle_certification_expiry_warning(sender, instance, **kwargs):
    """Notify employee when certification is expiring soon."""
    from django.utils import timezone
    from services.communication.services import send_in_app_notification

    if instance.expiry_date and instance.status == "active":
        days_until = (instance.expiry_date - timezone.now().date()).days
        if days_until <= 30 and days_until > 0:
            send_in_app_notification.delay(
                user_id=str(instance.employee.user.id),
                title="Certification Expiring Soon",
                body=f"Your {instance.name} certification expires in {days_until} days ({instance.expiry_date}).",
                priority="high",
                reference_type="certification",
                reference_id=str(instance.id),
            )


@receiver(post_save, sender="hr.TrainingEnrollment")
def handle_training_enrollment_status_change(sender, instance, **kwargs):
    """Notify employee on training enrollment status changes."""
    from services.communication.services import send_in_app_notification

    if instance.status == "completed":
        send_in_app_notification.delay(
            user_id=str(instance.employee.user.id),
            title="Training Completed",
            body=f"You have completed '{instance.program.name}'. Score: {instance.score or 'N/A'}",
            reference_type="training_enrollment",
            reference_id=str(instance.id),
        )


@receiver(post_save, sender="hr.Applicant")
def handle_applicant_status_change(sender, instance, **kwargs):
    """Notify admins when new applicant is received."""
    from services.communication.services import send_in_app_notification

    if instance.status == "new":
        from services.auth.models import User

        admins = User.objects.filter(
            school=instance.job_posting.school,
            role="school_admin",
            is_active=True,
        )
        for admin in admins:
            send_in_app_notification.delay(
                user_id=str(admin.id),
                title="New Job Applicant",
                body=f"{instance.full_name} applied for {instance.job_posting.title}.",
                reference_type="applicant",
                reference_id=str(instance.id),
            )
