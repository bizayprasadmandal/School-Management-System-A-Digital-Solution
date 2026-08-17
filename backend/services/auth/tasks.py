"""Auth service Celery tasks."""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_expired_tokens(self):
    """Delete expired password reset tokens daily."""
    try:
        from .models import PasswordResetToken

        deleted, _ = PasswordResetToken.objects.filter(expires_at__lt=timezone.now()).delete()
        logger.info("Cleaned up %d expired password reset tokens", deleted)
        return {"deleted": deleted}
    except Exception as exc:
        logger.error("cleanup_expired_tokens failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_expired_verification_tokens(self):
    """Delete expired email verification tokens daily."""
    try:
        from .models import EmailVerificationToken

        deleted, _ = EmailVerificationToken.objects.filter(expires_at__lt=timezone.now()).delete()
        logger.info("Cleaned up %d expired email verification tokens", deleted)
        return {"deleted": deleted}
    except Exception as exc:
        logger.error("cleanup_expired_verification_tokens failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_low_backup_codes(self):
    """
    Notify users via in-app notification when their 2FA backup codes
    drop below 2 remaining unused codes. Runs daily via Celery Beat.
    """
    from django.db.models import Count, Q
    from services.communication.services import send_in_app_notification

    from .models import User

    users_with_low_codes = (
        User.objects.filter(two_factor_enabled=True)
        .annotate(unused_codes=Count("backup_codes", filter=Q(backup_codes__used=False)))
        .filter(unused_codes__lt=2)
        .only("id", "first_name", "email")
    )

    try:
        notified = 0
        for user in users_with_low_codes.iterator(chunk_size=100):
            remaining = user.unused_codes
            if remaining == 0:
                title = "No backup codes remaining"
                body = (
                    f"You have used all your 2FA backup codes, {user.first_name}. "
                    "Generate new codes immediately from your security settings "
                    "to avoid being locked out of your account."
                )
            else:
                title = f"Only {remaining} backup code{'s' if remaining > 1 else ''} remaining"
                body = (
                    f"You have {remaining} unused 2FA backup code{'s' if remaining > 1 else ''}. "
                    "Consider generating new codes from your security settings."
                )

            send_in_app_notification.delay(
                user_id=str(user.id),
                title=title,
                body=body,
                reference_type="2fa_backup",
                reference_id="",
            )
            notified += 1

        logger.info("Notified %d users about low backup codes", notified)
        return {"notified": notified}
    except Exception as exc:
        logger.error("notify_low_backup_codes failed: %s", exc)
        raise self.retry(exc=exc)
