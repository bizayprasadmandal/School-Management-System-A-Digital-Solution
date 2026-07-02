"""Communication signals — track announcement view counts."""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender="communication.DirectMessage")
def handle_message_sent(sender, instance, created, **kwargs):
    """Push WebSocket notification when a direct message is created."""
    if created:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        import json
        channel_layer = get_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{instance.recipient.id}",
                    {
                        "type": "push_notification",
                        "notification": {
                            "id": str(instance.id),
                            "title": f"Message from {instance.sender.full_name}",
                            "body": instance.content[:100],
                            "created_at": instance.sent_at.isoformat(),
                            "read_at": None,
                        },
                    },
                )
            except Exception as e:
                logger.debug("WS push failed: %s", e)
