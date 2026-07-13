"""
Communication Service — Notification delivery service
Handles multi-channel notification dispatch: push, email, SMS, in-app
"""

import logging
from typing import Literal
from django.utils import timezone
from django.template import Template, Context
from celery import shared_task

logger = logging.getLogger(__name__)

Channel = Literal["push", "email", "sms", "in_app"]


class NotificationService:
    """
    Central notification dispatcher. Supports:
      - In-app (stored in DB + broadcast via WebSocket)
      - Email (SendGrid)
      - SMS (Twilio)
      - Push (Firebase FCM)
    """

    @classmethod
    def send(cls, user, template, context: dict, channels: list[Channel] = None):
        """
        Render template and dispatch to all specified channels.
        Falls back to user preference flags if channels not specified.
        """
        if channels is None:
            channels = []
            if user.notify_push:   channels.append("push")
            if user.notify_email:  channels.append("email")
            if user.notify_sms:    channels.append("sms")
            channels.append("in_app")

        for channel in channels:
            if channel == "in_app":
                send_in_app_notification.delay(
                    user_id=str(user.id),
                    title=cls._render(template.push_title if template else "", context),
                    body=cls._render(template.push_body if template else "", context),
                )
            elif channel == "email" and template and template.email_subject:
                send_email_notification.delay(
                    user_id=str(user.id),
                    subject=cls._render(template.email_subject, context),
                    body=cls._render(template.email_body, context),
                )
            elif channel == "sms" and template and template.sms_body:
                send_sms_notification.delay(
                    user_id=str(user.id),
                    body=cls._render(template.sms_body, context),
                )
            elif channel == "push" and template and template.push_title:
                send_push_notification.delay(
                    user_id=str(user.id),
                    title=cls._render(template.push_title, context),
                    body=cls._render(template.push_body, context),
                )

    @staticmethod
    def _render(template_str: str, context: dict) -> str:
        """Simple Django template rendering for notification content."""
        try:
            return Template(template_str).render(Context(context))
        except Exception:
            return template_str


# ─── Celery tasks ─────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_in_app_notification(self, user_id: str, title: str, body: str,
                              reference_type: str = "", reference_id: str = ""):
    """Store in-app notification and broadcast via WebSocket."""
    try:
        from .models import Notification
        from services.auth.models import User
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        user = User.objects.get(id=user_id)
        notif = Notification.objects.create(
            user=user,
            title=title,
            body=body,
            channel="in_app",
            status="sent",
            sent_at=timezone.now(),
            reference_type=reference_type,
            reference_id=reference_id,
        )

        # Broadcast via WebSocket to the user's notification channel
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user_id}",
                {
                    "type": "push_notification",
                    "notification": {
                        "id": str(notif.id),
                        "title": title,
                        "body": body,
                        "created_at": notif.created_at.isoformat(),
                        "read_at": None,
                    },
                },
            )

        logger.info("In-app notification sent to user %s: %s", user_id, title)

    except Exception as exc:
        logger.error("Failed to send in-app notification to %s: %s", user_id, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_notification(self, user_id: str, subject: str, body: str):
    """Send email via SendGrid."""
    try:
        from services.auth.models import User
        from django.core.mail import send_mail
        from django.conf import settings

        user = User.objects.get(id=user_id)
        if not user.email or not user.notify_email:
            return

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        from .models import Notification
        Notification.objects.create(
            user=user,
            title=subject,
            body=body,
            channel="email",
            status="sent",
            sent_at=timezone.now(),
        )

        logger.info("Email sent to %s: %s", user.email, subject)

    except Exception as exc:
        logger.error("Email failed for user %s: %s", user_id, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_notification(self, user_id: str, body: str):
    """Send SMS via Twilio."""
    try:
        from services.auth.models import User
        from django.conf import settings

        user = User.objects.get(id=user_id)
        if not user.phone or not user.notify_sms:
            return

        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Prefer messaging service SID (handles regulatory compliance);
        # fall back to direct phone number for simpler setups.
        kwargs = {"body": body, "to": user.phone}
        if settings.TWILIO_MESSAGING_SERVICE_SID:
            kwargs["messaging_service_sid"] = settings.TWILIO_MESSAGING_SERVICE_SID
        else:
            kwargs["from_"] = settings.TWILIO_PHONE_NUMBER

        message = client.messages.create(**kwargs)

        from .models import Notification
        Notification.objects.create(
            user=user,
            title="SMS",
            body=body,
            channel="sms",
            status="sent",
            sent_at=timezone.now(),
        )

        logger.info("SMS sent to %s (SID: %s)", user.phone, message.sid)

    except Exception as exc:
        logger.error("SMS failed for user %s: %s", user_id, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_push_notification(self, user_id: str, title: str, body: str,
                            data: dict = None):
    """Send Firebase FCM push notification."""
    try:
        from services.auth.models import User
        from core.firebase import get_firebase_app

        app = get_firebase_app()
        if app is None:
            logger.warning(
                "Push notification skipped for user %s — Firebase not configured",
                user_id,
            )
            return

        from firebase_admin import messaging

        user = User.objects.get(id=user_id)
        if not user.notify_push:
            return

        # Look up FCM token from device registry
        from .models import DeviceToken
        tokens = DeviceToken.objects.filter(
            user=user, is_active=True
        ).values_list("token", flat=True)

        if not tokens:
            return

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            tokens=list(tokens),
        )
        response = messaging.send_each_for_multicast(message)

        # Deactivate invalid tokens
        if response.failure_count > 0:
            for idx, result in enumerate(response.responses):
                if not result.success:
                    DeviceToken.objects.filter(token=list(tokens)[idx]).update(is_active=False)

        logger.info(
            "Push sent to user %s: %d success, %d failure",
            user_id, response.success_count, response.failure_count,
        )

    except Exception as exc:
        logger.error("Push notification failed for user %s: %s", user_id, exc)
        raise self.retry(exc=exc)


@shared_task
def broadcast_announcement(announcement_id: str):
    """
    Send an announcement to all targeted users via their preferred channels.
    Runs as a background task after announcement is published.
    """
    from .models import Announcement, NotificationTemplate
    from services.auth.models import User
    from services.students.models import Student

    try:
        announcement = Announcement.objects.select_related("school").get(id=announcement_id)
    except Announcement.DoesNotExist:
        logger.error("Announcement %s not found", announcement_id)
        return

    # Resolve target users based on audience
    school = announcement.school
    qs = User.objects.filter(school=school, is_active=True)

    audience_role_map = {
        "teachers": ["teacher"],
        "students": ["student"],
        "parents": ["parent"],
        "staff": ["teacher", "accountant", "librarian", "counselor"],
        "all": None,
    }
    roles = audience_role_map.get(announcement.audience)
    if roles:
        qs = qs.filter(role__in=roles)

    channels = []
    if announcement.send_push:   channels.append("push")
    if announcement.send_email:  channels.append("email")
    if announcement.send_sms:    channels.append("sms")
    channels.append("in_app")

    template = NotificationTemplate.objects.filter(
        school=school, event_type="announcement", is_active=True
    ).first()

    context = {
        "school_name": school.name,
        "title": announcement.title,
        "content": announcement.content[:200],
    }

    dispatched = 0
    for user in qs.iterator(chunk_size=100):
        NotificationService.send(user=user, template=template, context=context, channels=channels)
        dispatched += 1

    logger.info(
        "Announcement %s broadcast to %d users via %s",
        announcement_id, dispatched, channels,
    )
    return {"announcement_id": announcement_id, "dispatched": dispatched}
