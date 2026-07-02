"""Auth Service — Signal handlers for audit logging and security events."""
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    from .models import AuditLog
    AuditLog.objects.create(
        school=user.school, user=user, action="login",
        resource_type="user", resource_id=str(user.id),
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    logger.warning("Login failed for %s from %s",
        credentials.get("email", "unknown"),
        request.META.get("REMOTE_ADDR", ""))

@receiver(post_save, sender="auth_service.User")
def on_user_created(sender, instance, created, **kwargs):
    if created:
        logger.info("New user created: %s [%s] school=%s",
            instance.email, instance.role,
            instance.school.code if instance.school else "none")
