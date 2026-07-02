"""Auth service Celery tasks."""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def cleanup_expired_tokens():
    """Delete expired password reset tokens daily."""
    from .models import PasswordResetToken
    deleted, _ = PasswordResetToken.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()
    logger.info("Cleaned up %d expired password reset tokens", deleted)
    return {"deleted": deleted}
