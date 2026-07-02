"""
Communication Service — Django Channels WebSocket consumers
Real-time messaging, notification delivery, and live attendance updates
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    1-to-1 direct messaging over WebSocket.
    Room naming: chat_{min_id}_{max_id} (canonical, user-order-independent)
    """

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.user = user
        recipient_id = self.scope["url_route"]["kwargs"]["recipient_id"]
        ids = sorted([str(user.id), str(recipient_id)])
        self.room_name = f"chat_{ids[0]}_{ids[1]}"
        self.room_group_name = f"ws_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info("WS connect: user=%s room=%s", user.id, self.room_name)

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON payload")
            return

        msg_type = data.get("type", "message")

        if msg_type == "message":
            await self.handle_message(data)
        elif msg_type == "typing":
            await self.handle_typing(data)
        elif msg_type == "read_receipt":
            await self.handle_read_receipt(data)
        else:
            await self.send_error(f"Unknown message type: {msg_type}")

    async def handle_message(self, data):
        content = data.get("content", "").strip()
        if not content:
            return

        recipient_id = self.scope["url_route"]["kwargs"]["recipient_id"]
        message = await self.save_message(recipient_id, content)
        if not message:
            await self.send_error("Failed to save message")
            return

        payload = {
            "type": "chat_message",
            "message": {
                "id": str(message.id),
                "content": message.content,
                "sender_id": str(self.user.id),
                "sender_name": self.user.full_name,
                "sender_avatar": self.user.avatar.url if self.user.avatar else None,
                "status": "sent",
                "sent_at": message.sent_at.isoformat(),
            },
        }
        await self.channel_layer.group_send(self.room_group_name, payload)

    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_indicator",
                "user_id": str(self.user.id),
                "user_name": self.user.full_name,
                "is_typing": data.get("is_typing", False),
            },
        )

    async def handle_read_receipt(self, data):
        message_ids = data.get("message_ids", [])
        if message_ids:
            await self.mark_messages_read(message_ids)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "read_receipt",
                    "reader_id": str(self.user.id),
                    "message_ids": message_ids,
                    "read_at": timezone.now().isoformat(),
                },
            )

    # ── Channel layer event handlers ─────────────────────────────────────────

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def typing_indicator(self, event):
        if event.get("user_id") != str(self.user.id):
            await self.send(text_data=json.dumps(event))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps(event))

    # ── DB helpers (sync → async bridge) ─────────────────────────────────────

    @database_sync_to_async
    def save_message(self, recipient_id, content):
        from .models import DirectMessage
        from services.auth.models import User
        try:
            recipient = User.objects.get(id=recipient_id, school=self.user.school)
            return DirectMessage.objects.create(
                sender=self.user,
                recipient=recipient,
                content=content,
            )
        except User.DoesNotExist:
            logger.warning("Message recipient %s not found", recipient_id)
            return None

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        from .models import DirectMessage
        DirectMessage.objects.filter(
            id__in=message_ids,
            recipient=self.user,
            status__in=["sent", "delivered"],
        ).update(status="read", read_at=timezone.now())

    async def send_error(self, detail):
        await self.send(text_data=json.dumps({"type": "error", "detail": detail}))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Per-user notification channel.
    Group: notifications_{user_id}
    """

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.user = user
        self.group_name = f"notifications_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send unread count on connect
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({"type": "unread_count", "count": count}))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "mark_read":
            notif_id = data.get("notification_id")
            if notif_id:
                await self.mark_notification_read(notif_id)

    async def push_notification(self, event):
        """Called by the server to push a notification to this user."""
        await self.send(text_data=json.dumps({
            "type": "notification",
            "notification": event["notification"],
        }))

    async def unread_count_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "unread_count",
            "count": event["count"],
        }))

    @database_sync_to_async
    def get_unread_count(self):
        from .models import Notification
        return Notification.objects.filter(
            user=self.user, channel="in_app", read_at__isnull=True
        ).count()

    @database_sync_to_async
    def mark_notification_read(self, notif_id):
        from .models import Notification
        Notification.objects.filter(
            id=notif_id, user=self.user
        ).update(status="read", read_at=timezone.now())


class AttendanceLiveConsumer(AsyncWebsocketConsumer):
    """
    Admin / teacher live attendance dashboard.
    Broadcasts real-time attendance updates for a classroom.
    Group: attendance_classroom_{classroom_id}_{date}
    """

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return
        if user.role not in ["school_admin", "super_admin", "teacher"]:
            await self.close(code=4003)
            return

        self.user = user
        kwargs = self.scope["url_route"]["kwargs"]
        self.classroom_id = kwargs["classroom_id"]
        self.date = kwargs.get("date", timezone.now().date().isoformat())
        self.group_name = f"attendance_classroom_{self.classroom_id}_{self.date}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send current snapshot
        snapshot = await self.get_snapshot()
        await self.send(text_data=json.dumps({"type": "snapshot", "data": snapshot}))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def attendance_update(self, event):
        """Receives broadcast from attendance view after a record is saved."""
        await self.send(text_data=json.dumps({
            "type": "attendance_update",
            "record": event["record"],
        }))

    @database_sync_to_async
    def get_snapshot(self):
        from services.attendance.models import AttendanceRecord
        from services.students.models import Student
        records = AttendanceRecord.objects.filter(
            classroom_id=self.classroom_id, date=self.date
        ).select_related("student__user")
        total = Student.objects.filter(
            enrollments__classroom_id=self.classroom_id, enrollments__is_active=True
        ).count()
        return {
            "date": self.date,
            "total_students": total,
            "records": [
                {
                    "student_id": str(r.student.id),
                    "student_name": r.student.user.full_name,
                    "status": r.status,
                    "recorded_at": r.recorded_at.isoformat(),
                }
                for r in records
            ],
        }
