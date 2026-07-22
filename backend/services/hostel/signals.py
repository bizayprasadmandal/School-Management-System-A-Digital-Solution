"""Hostel signals — audit logging for sensitive actions and in-app notifications."""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from services.auth.models import AuditLog

logger = logging.getLogger(__name__)

def _log(sender, instance, action, **kwargs):
    try:
        user = None
        request = kwargs.get("request")
        if request:
            user = request.user
        AuditLog.objects.create(
            school=getattr(instance, "school", None),
            user=user,
            action=action,
            resource_type=sender._meta.model_name,
            resource_id=str(getattr(instance, "id", "")),
            changes={},
        )
    except Exception as e:
        logger.error("Audit log error: %s", e)

@receiver(post_save, sender="hostel.Hostel")
def log_hostel_save(sender, instance, created, **kwargs):
    _log(sender, instance, "created" if created else "updated")

@receiver(post_delete, sender="hostel.Hostel")
def log_hostel_delete(sender, instance, **kwargs):
    _log(sender, instance, "deleted")

@receiver(post_save, sender="hostel.HostelRoom")
def log_room_save(sender, instance, created, **kwargs):
    _log(sender, instance, "created" if created else "updated")

@receiver(post_delete, sender="hostel.HostelRoom")
def log_room_delete(sender, instance, **kwargs):
    _log(sender, instance, "deleted")

@receiver(post_save, sender="hostel.HostelAllocation")
def log_allocation_save(sender, instance, created, **kwargs):
    _log(sender, instance, "created" if created else "updated")

@receiver(post_delete, sender="hostel.HostelAllocation")
def log_allocation_delete(sender, instance, **kwargs):
    _log(sender, instance, "deleted")
