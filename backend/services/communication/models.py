"""
Communication Service — Messaging, announcements, notifications
"""

import uuid

from django.db import models
from services.auth.models import School, User
from services.students.models import Classroom, Grade


class Announcement(models.Model):
    """School-wide or targeted announcements."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Audience(models.TextChoices):
        ALL = "all", "All Users"
        TEACHERS = "teachers", "Teachers Only"
        STUDENTS = "students", "Students Only"
        PARENTS = "parents", "Parents Only"
        STAFF = "staff", "Staff Only"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.ALL)
    target_grades = models.ManyToManyField(Grade, blank=True)
    target_classrooms = models.ManyToManyField(Classroom, blank=True)
    attachment = models.FileField(upload_to="announcements/", null=True, blank=True)
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_draft = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "announcements"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.priority.upper()}] {self.title}"


class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "announcement_reads"
        unique_together = [("announcement", "user")]

    def __str__(self):
        return f"{self.user} read {self.announcement}"


class DirectMessage(models.Model):
    """1-to-1 messaging thread."""

    class Status(models.TextChoices):
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        READ = "read", "Read"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    attachment = models.FileField(upload_to="messages/attachments/", null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SENT)
    parent_message = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")
    is_deleted_sender = models.BooleanField(default=False)
    is_deleted_recipient = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "direct_messages"
        ordering = ["sent_at"]
        indexes = [
            models.Index(fields=["sender", "recipient"]),
            models.Index(fields=["recipient", "status"]),
            models.Index(fields=["recipient", "sent_at"]),
            models.Index(fields=["sender", "sent_at"]),
        ]

    def __str__(self):
        return f"{self.sender.full_name} → {self.recipient.full_name} ({self.sent_at:%Y-%m-%d %H:%M})"


class NotificationTemplate(models.Model):
    """Reusable notification templates with variable substitution."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="notification_templates")
    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50)  # e.g. "attendance_absent", "fee_due"
    email_subject = models.CharField(max_length=255, blank=True)
    email_body = models.TextField(blank=True)
    sms_body = models.CharField(max_length=160, blank=True)
    push_title = models.CharField(max_length=100, blank=True)
    push_body = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_templates"
        unique_together = [("school", "event_type")]

    def __str__(self):
        return f"{self.school} — {self.name} ({self.event_type})"


class Notification(models.Model):
    """Individual notification delivery record."""

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        READ = "read", "Read"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    body = models.TextField()
    channel = models.CharField(max_length=10, choices=Channel.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.CharField(max_length=255, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "channel", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.title} [{self.status}]"


class DeviceToken(models.Model):
    """FCM push notification token per device per user."""

    class Platform(models.TextChoices):
        IOS = "ios", "iOS"
        ANDROID = "android", "Android"
        WEB = "web", "Web (PWA)"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="device_tokens")
    token = models.TextField(unique=True)
    platform = models.CharField(max_length=10, choices=Platform.choices)
    device_id = models.CharField(max_length=255, blank=True)
    device_name = models.CharField(max_length=255, blank=True)
    app_version = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "device_tokens"
        indexes = [models.Index(fields=["user", "is_active"])]

    def __str__(self):
        return f"{self.user.email} [{self.platform}] {'✓' if self.is_active else '✗'}"
