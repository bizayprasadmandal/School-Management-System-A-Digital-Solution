"""
Communication Service — Notification delivery service
Handles multi-channel notification dispatch: push, email, SMS, in-app
"""

import logging
from typing import Literal

from celery import shared_task
from django.template import Context, Template
from django.utils import timezone

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
    def send(
        cls,
        user,
        template,
        context: dict,
        channels: list[Channel] = None,
        reference_type: str = "",
        reference_id: str = "",
    ):
        """
        Render template and dispatch to all specified channels.
        Falls back to user preference flags if channels not specified.
        reference_type/reference_id are attached to delivery records so
        callers can dedupe or link notifications to domain objects.
        """
        if channels is None:
            channels = []
            if user.notify_push:
                channels.append("push")
            if user.notify_email:
                channels.append("email")
            if user.notify_sms:
                channels.append("sms")
            channels.append("in_app")

        for channel in channels:
            if channel == "in_app":
                send_in_app_notification.delay(
                    user_id=str(user.id),
                    title=cls._render(template.push_title if template else "", context),
                    body=cls._render(template.push_body if template else "", context),
                    reference_type=reference_type,
                    reference_id=reference_id,
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
def send_in_app_notification(
    self, user_id: str, title: str, body: str, reference_type: str = "", reference_id: str = ""
):
    """Store in-app notification and broadcast via WebSocket."""
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        from services.auth.models import User

        from .models import Notification

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
        from django.conf import settings
        from django.core.mail import send_mail
        from services.auth.models import User

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
    """Send SMS via configured provider (Twilio, Vonage, or console fallback)."""
    try:
        from django.conf import settings
        from services.auth.models import User

        user = User.objects.get(id=user_id)
        if not user.phone or not user.notify_sms:
            return

        provider = settings.SMS_PROVIDER
        message_sid = None

        if provider == "vonage" and settings.VONAGE_API_KEY:
            # ── Vonage (Nexmo) ────────────────────────────────────────────────
            import vonage

            client = vonage.Client(
                key=settings.VONAGE_API_KEY,
                secret=settings.VONAGE_API_SECRET,
            )
            sms = vonage.Sms(client)
            response = sms.send_message(
                {
                    "from": settings.VONAGE_FROM_NUMBER or "EduSphere",
                    "to": user.phone,
                    "text": body,
                }
            )
            if response["messages"][0]["status"] == "0":
                message_sid = response["messages"][0]["message-id"]
                logger.info("SMS sent via Vonage to %s (ID: %s)", user.phone, message_sid)
            else:
                raise Exception(f"Vonage error: {response['messages'][0]['error-text']}")

        elif provider == "console":
            # ── Console/Logging (development) ─────────────────────────────────
            logger.info(
                "[SMS CONSOLE] To: %s | Body: %s",
                user.phone,
                body[:100],
            )
            message_sid = "console_log"

        else:
            # ── Twilio (default) ──────────────────────────────────────────────
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            kwargs = {"body": body, "to": user.phone}
            if settings.TWILIO_MESSAGING_SERVICE_SID:
                kwargs["messaging_service_sid"] = settings.TWILIO_MESSAGING_SERVICE_SID
            else:
                kwargs["from_"] = settings.TWILIO_PHONE_NUMBER

            message = client.messages.create(**kwargs)
            message_sid = message.sid
            logger.info("SMS sent via Twilio to %s (SID: %s)", user.phone, message_sid)

        # Record notification in DB
        from .models import Notification

        Notification.objects.create(
            user=user,
            title="SMS",
            body=body,
            channel="sms",
            status="sent",
            sent_at=timezone.now(),
        )

    except Exception as exc:
        logger.error("SMS failed for user %s: %s", user_id, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_expo_push_notification(self, user_id: str, title: str, body: str, data: dict = None):
    """Send Expo push notification (Expo Push API).

    This is the primary push delivery channel for the Expo React Native app.
    Falls back to Firebase FCM if the token is not an Expo token.
    """
    try:
        import requests
        from django.conf import settings
        from services.auth.models import User

        from .models import DeviceToken, Notification

        user = User.objects.get(id=user_id)
        if not user.notify_push:
            return

        tokens = DeviceToken.objects.filter(user=user, is_active=True).values_list("token", "platform")

        if not tokens:
            return

        headers = {"Content-Type": "application/json"}
        if settings.EXPO_ACCESS_TOKEN:
            headers["Authorization"] = f"Bearer {settings.EXPO_ACCESS_TOKEN}"

        push_data = {
            "title": title,
            "body": body,
            "data": data or {},
            "sound": "default",
            "badge": 1,
            "channelId": "default",
            "priority": "high",
        }

        success_count = 0
        failure_count = 0
        for token, platform in tokens:
            if token.startswith("ExponentPushToken") or token.startswith("ExpoPushToken"):
                # Send via Expo Push API
                push_data["to"] = token
                resp = requests.post(
                    "https://exp.host/--/api/v2/push/send",
                    json=push_data,
                    headers=headers,
                    timeout=10,
                )
                resp_data = resp.json()
                if resp.ok and resp_data.get("data", {}).get("status") == "ok":
                    success_count += 1
                else:
                    errors = resp_data.get("data", {}).get("errors", [])
                    error_codes = [e.get("code") for e in errors]
                    if "DeviceNotRegistered" in error_codes:
                        DeviceToken.objects.filter(token=token).update(is_active=False)
                    failure_count += 1
                    logger.warning(
                        "Expo push failed for token %s: %s",
                        token[:20],
                        resp_data,
                    )
            else:
                # Fallback to Firebase FCM for non-Expo tokens
                try:
                    from core.firebase import get_firebase_app
                    from firebase_admin import messaging

                    app = get_firebase_app()
                    if app is None:
                        continue

                    message = messaging.Message(
                        notification=messaging.Notification(title=title, body=body),
                        data=data or {},
                        token=token,
                    )
                    messaging.send(message)
                    success_count += 1
                except Exception as fcm_err:
                    failure_count += 1
                    if "NOT_FOUND" in str(fcm_err) or "Unregistered" in str(fcm_err):
                        DeviceToken.objects.filter(token=token).update(is_active=False)
                    logger.warning("FCM fallback failed for token: %s", fcm_err)

        # Record in-app notification for delivery tracking
        Notification.objects.create(
            user=user,
            title=title,
            body=body,
            channel="push",
            status="sent",
            sent_at=timezone.now(),
            reference_type=data.get("reference_type", "") if data else "",
            reference_id=data.get("reference_id", "") if data else "",
        )

        logger.info(
            "Expo push sent to user %s: %d success, %d failure",
            user_id,
            success_count,
            failure_count,
        )

    except Exception as exc:
        logger.error("Expo push notification failed for user %s: %s", user_id, exc)
        raise self.retry(exc=exc)


# Alias for backward compatibility — existing callers can still use send_push_notification
send_push_notification = send_expo_push_notification


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def broadcast_announcement(self, announcement_id: str):
    """
    Send an announcement to all targeted users via their preferred channels.
    Runs as a background task after announcement is published.
    """
    from services.auth.models import User

    from .models import Announcement, NotificationTemplate

    try:
        announcement = Announcement.objects.select_related("school").get(id=announcement_id)
    except Announcement.DoesNotExist:
        logger.error("Announcement %s not found", announcement_id)
        return

    try:
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
        if announcement.send_push:
            channels.append("push")
        if announcement.send_email:
            channels.append("email")
        if announcement.send_sms:
            channels.append("sms")
        channels.append("in_app")

        template = NotificationTemplate.objects.filter(school=school, event_type="announcement", is_active=True).first()

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
            announcement_id,
            dispatched,
            channels,
        )
    except Exception as exc:
        logger.error("Announcement broadcast failed for %s: %s", announcement_id, exc)
        raise self.retry(exc=exc)
    return {"announcement_id": announcement_id, "dispatched": dispatched}
