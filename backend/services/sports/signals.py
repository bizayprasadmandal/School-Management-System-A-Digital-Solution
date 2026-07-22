"""Sports signals — audit logging for sensitive actions."""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from services.auth.models import AuditLog

logger = logging.getLogger(__name__)

def _log(sender, instance, action, **kwargs):
    try:
        AuditLog.objects.create(
            school=getattr(instance, "school", None),
            action=action,
            resource_type=sender._meta.model_name,
            resource_id=str(getattr(instance, "id", "")),
            changes={},
        )
    except Exception as e:
        logger.error("Audit log error: %s", e)

for model_name in ["Sport", "Team", "TeamMember", "SportEvent", "SportAchievement"]:
    @receiver(post_save, sender=f"sports.{model_name}")
    def log_save(sender, instance, created, **kwargs):
        _log(sender, instance, "created" if created else "updated")

    @receiver(post_delete, sender=f"sports.{model_name}")
    def log_delete(sender, instance, **kwargs):
        _log(sender, instance, "deleted")
