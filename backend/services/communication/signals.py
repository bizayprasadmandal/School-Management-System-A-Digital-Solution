"""Communication — signal handlers."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="auth_service.School")
def ensure_standard_templates_on_school_created(sender, instance, created, **kwargs):
    """Every school gets the standard notification templates on creation."""
    if not created:
        return
    from .templates import ensure_school_notification_templates

    count = ensure_school_notification_templates(instance)
    logger.info(
        "Seeded %d standard notification templates for new school %s",
        count,
        instance.code,
    )
