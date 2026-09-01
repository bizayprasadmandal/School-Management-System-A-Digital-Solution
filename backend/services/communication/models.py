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


# =============================================================================
# NEW MODELS: Group Messaging
# =============================================================================


class ChatGroup(models.Model):
    """Chat groups for classes, subjects, clubs, etc."""

    class GroupType(models.TextChoices):
        CLASS = "class", "Class Group"
        SUBJECT = "subject", "Subject Group"
        CLUB = "club", "Club Group"
        DEPARTMENT = "department", "Department Group"
        STAFF = "staff", "Staff Group"
        PARENTS = "parents", "Parents Group"
        CUSTOM = "custom", "Custom Group"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="chat_groups")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    group_type = models.CharField(max_length=15, choices=GroupType.choices, default=GroupType.CUSTOM)
    classroom = models.ForeignKey(
        Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name="chat_groups"
    )
    subject = models.ForeignKey(
        "academics.Subject", on_delete=models.SET_NULL, null=True, blank=True, related_name="chat_groups"
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_chat_groups")
    avatar = models.ImageField(upload_to="chat_groups/avatars/", null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    is_muted = models.BooleanField(default=False)
    max_members = models.PositiveIntegerField(default=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_groups"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_group_type_display()})"

    @property
    def member_count(self):
        return self.memberships.count()


class GroupMembership(models.Model):
    """Track group members and their roles."""

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MODERATOR = "moderator", "Moderator"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_group_memberships")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    nickname = models.CharField(max_length=100, blank=True, help_text="Display name in this group")
    is_muted = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    last_read_at = models.DateTimeField(null=True, blank=True)
    unread_count = models.PositiveIntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "group_memberships"
        unique_together = [("group", "user")]
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.user} in {self.group} ({self.get_role_display()})"


class GroupMessage(models.Model):
    """Messages within a chat group."""

    class MessageType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        FILE = "file", "File"
        VOICE = "voice", "Voice Message"
        VIDEO = "video", "Video"
        SYSTEM = "system", "System Message"
        POLL = "poll", "Poll"
        LOCATION = "location", "Location"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_group_messages")
    message_type = models.CharField(max_length=10, choices=MessageType.choices, default=MessageType.TEXT)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to="chat_groups/messages/", null=True, blank=True)
    reply_to = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")
    is_pinned = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    reactions = models.JSONField(default=dict, blank=True, help_text="{emoji: [user_ids]}")
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "group_messages"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["group", "sent_at"]),
            models.Index(fields=["sender", "sent_at"]),
        ]

    def __str__(self):
        return f"{self.sender} in {self.group}: {self.content[:50]}"

    @property
    def reply_count(self):
        return self.replies.count()


# =============================================================================
# NEW MODELS: Parent-Teacher Chat
# =============================================================================


class ParentTeacherChat(models.Model):
    """Dedicated parent-teacher communication channel."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"
        BLOCKED = "blocked", "Blocked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="parent_teacher_chats")
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="parent_chats")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_chats")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="parent_teacher_chats")
    subject = models.CharField(max_length=200, blank=True, help_text="Chat subject/topic")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    is_archived_by_parent = models.BooleanField(default=False)
    is_archived_by_teacher = models.BooleanField(default=False)
    last_message_at = models.DateTimeField(null=True, blank=True)
    parent_unread_count = models.PositiveIntegerField(default=0)
    teacher_unread_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "parent_teacher_chats"
        unique_together = [("parent", "teacher", "student")]
        ordering = ["-last_message_at"]

    def __str__(self):
        return f"{self.parent} ↔ {self.teacher} ({self.student})"


class ParentTeacherMessage(models.Model):
    """Messages in parent-teacher chat."""

    class MessageType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        FILE = "file", "File"
        SYSTEM = "system", "System Message"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(ParentTeacherChat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_parent_teacher_messages")
    message_type = models.CharField(max_length=10, choices=MessageType.choices, default=MessageType.TEXT)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to="parent_teacher_chat/", null=True, blank=True)
    reply_to = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")
    is_read_by_parent = models.BooleanField(default=False)
    is_read_by_teacher = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "parent_teacher_messages"
        ordering = ["sent_at"]
        indexes = [
            models.Index(fields=["chat", "sent_at"]),
            models.Index(fields=["sender", "sent_at"]),
        ]

    def __str__(self):
        return f"{self.sender} in {self.chat}: {self.content[:50]}"


# =============================================================================
# NEW MODELS: Video Conferencing
# =============================================================================


class VideoConference(models.Model):
    """Virtual meetings/video calls."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ACTIVE = "active", "Active"
        ENDED = "ended", "Ended"
        CANCELLED = "cancelled", "Cancelled"

    class ConferenceType(models.TextChoices):
        MEETING = "meeting", "Meeting"
        PARENT_TEACHER = "parent_teacher", "Parent-Teacher Conference"
        STAFF = "staff", "Staff Meeting"
        CLASS = "class", "Virtual Class"
        TUTORING = "tutoring", "Tutoring Session"
        INTERVIEW = "interview", "Interview"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="video_conferences")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    conference_type = models.CharField(max_length=15, choices=ConferenceType.choices, default=ConferenceType.MEETING)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hosted_conferences")
    meeting_url = models.URLField(blank=True, help_text="Video meeting URL (Zoom, Meet, etc.)")
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    max_participants = models.PositiveIntegerField(default=100)
    is_recorded = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "video_conferences"
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ConferenceParticipant(models.Model):
    """Track conference participants."""

    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        ATTENDED = "attended", "Attended"
        NO_SHOW = "no_show", "No Show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conference = models.ForeignKey(VideoConference, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conference_participations")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.INVITED)
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    invited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_participants"
        unique_together = [("conference", "user")]

    def __str__(self):
        return f"{self.user} - {self.conference} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: SMS/Email Integration
# =============================================================================


class SMSIntegration(models.Model):
    """Send SMS messages via Twilio or other providers."""

    class Provider(models.TextChoices):
        TWILIO = "twilio", "Twilio"
        NEXMO = "nexmo", "Nexmo/Vonage"
        AWS_SNS = "aws_sns", "AWS SNS"
        MESSAGEBIRD = "messagebird", "MessageBird"
        CUSTOM = "custom", "Custom Provider"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        BOUNCED = "bounced", "Bounced"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sms_integrations")
    provider = models.CharField(max_length=15, choices=Provider.choices, default=Provider.TWILIO)
    from_number = models.CharField(max_length=20, blank=True)
    to_number = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    provider_message_id = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_sms")
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sms_integrations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "status"]),
            models.Index(fields=["to_number", "created_at"]),
        ]

    def __str__(self):
        return f"SMS to {self.to_number}: {self.message[:30]}..."


class EmailIntegration(models.Model):
    """Send emails via SendGrid/SES or other providers."""

    class Provider(models.TextChoices):
        SENDGRID = "sendgrid", "SendGrid"
        AWS_SES = "aws_ses", "AWS SES"
        MAILGUN = "mailgun", "Mailgun"
        SMTP = "smtp", "SMTP Server"
        CUSTOM = "custom", "Custom Provider"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        OPENED = "opened", "Opened"
        CLICKED = "clicked", "Clicked"
        BOUNCED = "bounced", "Bounced"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="email_integrations")
    provider = models.CharField(max_length=15, choices=Provider.choices, default=Provider.SENDGRID)
    from_email = models.EmailField()
    to_email = models.EmailField()
    cc_emails = models.JSONField(default=list, blank=True)
    bcc_emails = models.JSONField(default=list, blank=True)
    subject = models.CharField(max_length=255)
    body_html = models.TextField(blank=True)
    body_text = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    provider_message_id = models.CharField(max_length=100, blank=True)
    attachment = models.FileField(upload_to="emails/attachments/", null=True, blank=True)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_emails")
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "email_integrations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "status"]),
            models.Index(fields=["to_email", "created_at"]),
        ]

    def __str__(self):
        return f"Email to {self.to_email}: {self.subject}"


# =============================================================================
# NEW MODELS: File Sharing
# =============================================================================


class FileAttachment(models.Model):
    """Shared files in messages and chats."""

    class FileType(models.TextChoices):
        DOCUMENT = "document", "Document"
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        AUDIO = "audio", "Audio"
        ARCHIVE = "archive", "Archive"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="file_attachments")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_files")
    file = models.FileField(upload_to="attachments/%Y/%m/", null=True, blank=True)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FileType.choices, default=FileType.OTHER)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    # Reference to where this file is used
    reference_type = models.CharField(max_length=50, blank=True, help_text="Model name e.g. GroupMessage")
    reference_id = models.CharField(max_length=255, blank=True, help_text="Object ID")
    is_public = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "file_attachments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference_type", "reference_id"]),
            models.Index(fields=["uploaded_by", "created_at"]),
        ]

    def __str__(self):
        return f"{self.file_name} ({self.get_file_type_display()})"

    @property
    def file_size_display(self):
        """Human-readable file size."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"


# =============================================================================
# NEW MODELS: Message Threading
# =============================================================================


class MessageThread(models.Model):
    """Threaded conversations within messages."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_message = models.ForeignKey(GroupMessage, on_delete=models.CASCADE, related_name="threads")
    reply_count = models.PositiveIntegerField(default=0)
    last_reply_at = models.DateTimeField(null=True, blank=True)
    last_reply_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="thread_replies")
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "message_threads"
        ordering = ["-last_reply_at"]

    def __str__(self):
        return f"Thread on: {self.parent_message.content[:50]}"


# =============================================================================
# NEW MODELS: Read Receipts
# =============================================================================


class ReadReceipt(models.Model):
    """Track when messages are read by recipients."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(GroupMessage, on_delete=models.CASCADE, related_name="read_receipts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="message_read_receipts")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "read_receipts"
        unique_together = [("message", "user")]
        ordering = ["-read_at"]

    def __str__(self):
        return f"{self.user} read {self.message} at {self.read_at}"


# =============================================================================
# NEW MODELS: Typing Indicators
# =============================================================================


class TypingIndicator(models.Model):
    """Show when someone is typing in a chat."""

    class ChatType(models.TextChoices):
        GROUP = "group", "Group Chat"
        PARENT_TEACHER = "parent_teacher", "Parent-Teacher Chat"
        DIRECT = "direct", "Direct Message"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="typing_indicators")
    chat_type = models.CharField(max_length=15, choices=ChatType.choices)
    chat_id = models.CharField(max_length=255, help_text="ID of the chat (group or parent-teacher)")
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "typing_indicators"
        indexes = [
            models.Index(fields=["chat_type", "chat_id"]),
            models.Index(fields=["user", "chat_type"]),
        ]

    def __str__(self):
        return f"{self.user} typing in {self.get_chat_type_display()}"

    @property
    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.expires_at


# =============================================================================
# NEW MODELS: Message Reactions
# =============================================================================


class MessageReaction(models.Model):
    """React to messages with emojis."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(GroupMessage, on_delete=models.CASCADE, related_name="message_reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="message_reactions")
    emoji = models.CharField(max_length=10, help_text="Emoji character(s)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "message_reactions"
        unique_together = [("message", "user", "emoji")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} reacted {self.emoji} to {self.message}"


# =============================================================================
# NEW MODELS: Voice Messages
# =============================================================================


class VoiceMessage(models.Model):
    """Audio messages in chats."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_voice_messages")
    group = models.ForeignKey(
        ChatGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="voice_messages"
    )
    parent_teacher_chat = models.ForeignKey(
        ParentTeacherChat, on_delete=models.SET_NULL, null=True, blank=True, related_name="voice_messages"
    )
    audio_file = models.FileField(upload_to="voice_messages/%Y/%m/", null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(help_text="Audio duration in seconds")
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    transcription = models.TextField(blank=True, help_text="Auto-generated transcription")
    is_transcribed = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "voice_messages"
        ordering = ["-sent_at"]

    def __str__(self):
        return f"Voice from {self.sender} ({self.duration_seconds}s)"

    @property
    def duration_display(self):
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"


# =============================================================================
# NEW MODELS: Broadcast Messages
# =============================================================================


class BroadcastMessage(models.Model):
    """Mass messaging to groups."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        PARTIAL = "partial", "Partially Sent"
        FAILED = "failed", "Failed"

    class Channel(models.TextChoices):
        SMS = "sms", "SMS"
        EMAIL = "email", "Email"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App"
        ALL = "all", "All Channels"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="broadcast_messages")
    title = models.CharField(max_length=255)
    content = models.TextField()
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.IN_APP)
    # Target audience
    target_audience = models.JSONField(
        default=list, help_text="List of audience types: teachers, students, parents, etc."
    )
    target_classrooms = models.ManyToManyField(Classroom, blank=True)
    target_grades = models.ManyToManyField(Grade, blank=True)
    target_users = models.ManyToManyField(User, blank=True, related_name="received_broadcasts")
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    # Stats
    total_recipients = models.PositiveIntegerField(default=0)
    total_sent = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_failed = models.PositiveIntegerField(default=0)
    total_read = models.PositiveIntegerField(default=0)
    # Settings
    priority = models.CharField(
        max_length=10, choices=Announcement.Priority.choices, default=Announcement.Priority.NORMAL
    )
    require_read_receipt = models.BooleanField(default=False)
    allow_reply = models.BooleanField(default=True)
    # Metadata
    attachment = models.FileField(upload_to="broadcasts/attachments/", null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_broadcasts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "broadcast_messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def delivery_rate(self):
        if self.total_recipients == 0:
            return 0
        return round((self.total_delivered / self.total_recipients) * 100, 2)

    @property
    def read_rate(self):
        if self.total_delivered == 0:
            return 0
        return round((self.total_read / self.total_delivered) * 100, 2)


# =============================================================================
# NEW MODELS: Communication Logs
# =============================================================================


class CommunicationLog(models.Model):
    """Track all communications for audit and analytics."""

    class CommunicationType(models.TextChoices):
        SMS = "sms", "SMS"
        EMAIL = "email", "Email"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App Message"
        ANNOUNCEMENT = "announcement", "Announcement"
        BROADCAST = "broadcast", "Broadcast"
        DIRECT_MESSAGE = "direct_message", "Direct Message"
        GROUP_MESSAGE = "group_message", "Group Message"
        PARENT_TEACHER = "parent_teacher", "Parent-Teacher Chat"
        VIDEO_CONFERENCE = "video_conference", "Video Conference"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="communication_logs")
    communication_type = models.CharField(max_length=20, choices=CommunicationType.choices)
    # Sender/Recipient
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_communications")
    recipient = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_communications"
    )
    recipient_group = models.ForeignKey(
        ChatGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_communications"
    )
    # Content
    subject = models.CharField(max_length=255, blank=True)
    content_preview = models.TextField(blank=True, help_text="First 500 chars of content")
    # Reference
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.CharField(max_length=255, blank=True)
    # Status
    status = models.CharField(max_length=20, default="sent")
    # Timing
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    # Cost tracking
    cost = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    # Error tracking
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "communication_logs"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["school", "communication_type"]),
            models.Index(fields=["sender", "sent_at"]),
            models.Index(fields=["recipient", "sent_at"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]

    def __str__(self):
        return f"{self.get_communication_type_display()} - {self.sender} → {self.recipient or self.recipient_group}"


# =============================================================================
# NEW MODELS: Surveys & Polls
# =============================================================================


class Survey(models.Model):
    """Surveys distributed to students, parents, or staff."""

    class SurveyType(models.TextChoices):
        FEEDBACK = "feedback", "Feedback Survey"
        SATISFACTION = "satisfaction", "Satisfaction Survey"
        NEEDS_ASSESSMENT = "needs", "Needs Assessment"
        ACADEMIC = "academic", "Academic Survey"
        DEMOGRAPHIC = "demographic", "Demographic Survey"
        CUSTOM = "custom", "Custom Survey"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"
        ANALYZED = "analyzed", "Analyzed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="surveys")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    survey_type = models.CharField(max_length=15, choices=SurveyType.choices, default=SurveyType.FEEDBACK)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    questions = models.JSONField(default=list, blank=True)
    target_audience = models.CharField(max_length=50, blank=True, help_text="Students, Parents, Staff, All")
    target_grades = models.CharField(max_length=100, blank=True)
    is_anonymous = models.BooleanField(default=True)
    allow_multiple_responses = models.BooleanField(default=False)
    # Schedule
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # Results
    total_invited = models.PositiveIntegerField(default=0)
    total_responses = models.PositiveIntegerField(default=0)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "communication_surveys"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_survey_type_display()})"

    @property
    def response_rate(self):
        if self.total_invited == 0:
            return 0
        return round((self.total_responses / self.total_invited) * 100, 2)


class SurveyResponse(models.Model):
    """Individual survey responses."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses")
    respondent_type = models.CharField(max_length=20, blank=True)
    student = models.ForeignKey("students.Student", on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="survey_responses")
    staff = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="staff_survey_responses"
    )
    answers = models.JSONField(default=dict, blank=True)
    overall_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "communication_survey_responses"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Response to {self.survey.title} ({self.submitted_at})"


class Poll(models.Model):
    """Quick polls for groups or classes."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="polls")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    options = models.JSONField(default=list, help_text="List of poll options")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Target
    target_group = models.ForeignKey(ChatGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="polls")
    target_audience = models.CharField(max_length=50, blank=True)
    # Settings
    is_anonymous = models.BooleanField(default=False)
    allow_multiple_choices = models.BooleanField(default=False)
    max_choices = models.PositiveIntegerField(default=1)
    # Schedule
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    # Results
    total_votes = models.PositiveIntegerField(default=0)
    results_data = models.JSONField(default=dict, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "communication_polls"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.total_votes} votes)"


class PollVote(models.Model):
    """Individual poll votes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    voter_type = models.CharField(max_length=20, blank=True)
    student = models.ForeignKey("students.Student", on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="poll_votes")
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="staff_poll_votes")
    selected_options = models.JSONField(default=list, help_text="List of selected option indices")
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "communication_poll_votes"
        unique_together = [("poll", "student")]

    def __str__(self):
        return f"Vote on {self.poll.title} ({self.voted_at})"


# =============================================================================
# NEW MODELS: Email Templates
# =============================================================================


class EmailTemplate(models.Model):
    """Reusable email templates for communications."""

    class Category(models.TextChoices):
        WELCOME = "welcome", "Welcome Email"
        FEE_REMINDER = "fee_reminder", "Fee Reminder"
        EVENT_INVITE = "event", "Event Invitation"
        REPORT_CARD = "report", "Report Card"
        ABSENCE_ALERT = "absence", "Absence Alert"
        NEWSLETTER = "newsletter", "Newsletter"
        ADMISSION = "admission", "Admission"
        CUSTOM = "custom", "Custom"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="email_templates")
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=15, choices=Category.choices, default=Category.CUSTOM)
    subject = models.CharField(max_length=255)
    body_html = models.TextField(help_text="HTML body with {{variable}} placeholders")
    body_text = models.TextField(blank=True, help_text="Plain text fallback")
    # Usage
    is_active = models.BooleanField(default=True)
    times_used = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "email_templates"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


# =============================================================================
# NEW MODELS: SMS Gateway
# =============================================================================


class SMSGatewayConfig(models.Model):
    """SMS gateway configuration per school."""

    class Provider(models.TextChoices):
        TWILIO = "twilio", "Twilio"
        AFRICASTALKING = "africastalking", "Africa's Talking"
        NEXMO = "nexmo", "Nexmo/Vonage"
        MSG91 = "msg91", "MSG91"
        CUSTOM = "custom", "Custom API"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name="sms_gateway_config")
    provider = models.CharField(max_length=20, choices=Provider.choices)
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    sender_id = models.CharField(max_length=20, blank=True)
    webhook_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    # Usage stats
    total_sms_sent = models.PositiveIntegerField(default=0)
    total_sms_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sms_gateway_configs"

    def __str__(self):
        return f"SMS Gateway — {self.school.name} ({self.get_provider_display()})"


class SMSLog(models.Model):
    """Log of all SMS messages sent."""

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sms_logs")
    recipient_phone = models.CharField(max_length=30)
    recipient_name = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.QUEUED)
    # Tracking
    provider_message_id = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    error_message = models.TextField(blank=True)
    # Related
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.CharField(max_length=255, blank=True)
    # Metadata
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sms_logs"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["school", "status"]),
            models.Index(fields=["recipient_phone"]),
        ]

    def __str__(self):
        return f"SMS to {self.recipient_phone} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Newsletter
# =============================================================================


class Newsletter(models.Model):
    """School newsletters."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="newsletters")
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=255)
    content_html = models.TextField()
    content_text = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    # Target
    target_audience = models.CharField(max_length=50, blank=True, help_text="Parents, Staff, Students, All")
    target_grades = models.CharField(max_length=100, blank=True)
    # Schedule
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    # Stats
    total_recipients = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    total_bounced = models.PositiveIntegerField(default=0)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "newsletters"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def open_rate(self):
        if self.total_recipients == 0:
            return 0
        return round((self.total_opened / self.total_recipients) * 100, 2)


# =============================================================================
# NEW MODELS: Emergency Alert System
# =============================================================================


class EmergencyAlert(models.Model):
    """School-wide emergency alerts (lockdown, evacuation, etc.)."""

    class AlertLevel(models.TextChoices):
        INFO = "info", "Informational"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"
        TEST = "test", "Test Alert"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        RESOLVED = "resolved", "Resolved"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="emergency_alerts")
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_level = models.CharField(max_length=10, choices=AlertLevel.choices, default=AlertLevel.WARNING)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Channels
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=True)
    send_push = models.BooleanField(default=True)
    send_pa = models.BooleanField(default=False, help_text="Play on school PA system")
    # Target
    target_audience = models.CharField(max_length=50, default="all", help_text="all, parents, staff, students")
    # Tracking
    total_sent = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_read = models.PositiveIntegerField(default=0)
    # Metadata
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_alerts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "emergency_alerts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "alert_level", "status"]),
        ]

    def __str__(self):
        return f"[{self.get_alert_level_display()}] {self.title}"


# =============================================================================
# NEW MODELS: Communication Preferences
# =============================================================================


class CommunicationPreference(models.Model):
    """Per-user communication preferences."""

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="comm_preferences")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="comm_preferences")
    # Channel toggles
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    # Category preferences
    announcements = models.CharField(max_length=10, choices=Channel.choices, default=Channel.EMAIL)
    fee_notices = models.CharField(max_length=10, choices=Channel.choices, default=Channel.EMAIL)
    attendance_alerts = models.CharField(max_length=10, choices=Channel.choices, default=Channel.SMS)
    emergency_alerts = models.CharField(max_length=10, choices=Channel.choices, default=Channel.PUSH)
    event_reminders = models.CharField(max_length=10, choices=Channel.choices, default=Channel.EMAIL)
    # Quiet hours
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "communication_preferences"

    def __str__(self):
        return f"Comm Preferences — {self.user.full_name}"


# =============================================================================
# NEW MODELS: Message Templates
# =============================================================================


class MessageTemplate(models.Model):
    """Reusable message templates for various communications."""

    class TemplateType(models.TextChoices):
        EMAIL = "email", "Email Template"
        SMS = "sms", "SMS Template"
        PUSH = "push", "Push Notification Template"
        IN_APP = "in_app", "In-App Message"

    class Category(models.TextChoices):
        FEE = "fee", "Fee Related"
        ATTENDANCE = "attendance", "Attendance"
        EVENT = "event", "Event"
        ACADEMIC = "academic", "Academic"
        GENERAL = "general", "General"
        WELCOME = "welcome", "Welcome"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="message_templates")
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=10, choices=TemplateType.choices)
    category = models.CharField(max_length=15, choices=Category.choices, default=Category.GENERAL)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(help_text="Message body with {{variable}} placeholders")
    variables = models.JSONField(default=list, blank=True, help_text="Available template variables")
    is_active = models.BooleanField(default=True)
    times_used = models.PositiveIntegerField(default=0)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "message_templates"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


# =============================================================================
# NEW MODELS: Delivery Tracking
# =============================================================================


class MessageDeliveryStatus(models.Model):
    """Detailed delivery status for each recipient of a broadcast/announcement."""

    class DeliveryStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        READ = "read", "Read"
        FAILED = "failed", "Failed"
        BOUNCED = "bounced", "Bounced"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="message_delivery_statuses")
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="delivery_statuses", null=True, blank=True
    )
    broadcast = models.ForeignKey(
        BroadcastMessage, on_delete=models.CASCADE, related_name="delivery_statuses", null=True, blank=True
    )
    # Recipient
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="message_delivery_statuses")
    # Channel
    channel = models.CharField(max_length=20, choices=CommunicationLog.CommunicationType.choices)
    # Status
    status = models.CharField(max_length=15, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING)
    # Timing
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    # Error
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "message_delivery_statuses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "status"]),
            models.Index(fields=["notification", "status"]),
        ]

    def __str__(self):
        return f"{self.recipient.full_name} — {self.get_status_display()} ({self.channel})"


class CommunicationBlacklist(models.Model):
    """Users who opted out of certain communications."""

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        ALL = "all", "All Channels"

    class Category(models.TextChoices):
        MARKETING = "marketing", "Marketing"
        NEWSLETTERS = "newsletter", "Newsletters"
        FEE_REMINDERS = "fee", "Fee Reminders"
        EVENTS = "event", "Event Notifications"
        ALL = "all", "All Categories"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="comm_blacklists")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comm_blacklists")
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.ALL)
    category = models.CharField(max_length=15, choices=Category.choices, default=Category.ALL)
    reason = models.TextField(blank=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "communication_blacklists"
        unique_together = [("user", "channel", "category")]

    def __str__(self):
        return f"{self.user.full_name} — Blacklisted: {self.get_channel_display()} / {self.get_category_display()}"


class CommunicationAnalytics(models.Model):
    """Aggregate communication analytics and metrics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="communication_analytics")
    # Period
    period_start = models.DateField()
    period_end = models.DateField()
    # Email stats
    emails_sent = models.PositiveIntegerField(default=0)
    emails_delivered = models.PositiveIntegerField(default=0)
    emails_opened = models.PositiveIntegerField(default=0)
    emails_clicked = models.PositiveIntegerField(default=0)
    emails_bounced = models.PositiveIntegerField(default=0)
    emails_unsubscribed = models.PositiveIntegerField(default=0)
    # SMS stats
    sms_sent = models.PositiveIntegerField(default=0)
    sms_delivered = models.PositiveIntegerField(default=0)
    sms_failed = models.PositiveIntegerField(default=0)
    # Push stats
    push_sent = models.PositiveIntegerField(default=0)
    push_opened = models.PositiveIntegerField(default=0)
    push_failed = models.PositiveIntegerField(default=0)
    # Costs
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    email_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sms_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Engagement
    avg_open_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_click_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Top categories
    top_categories = models.JSONField(default=dict, blank=True)
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "communication_analytics"
        ordering = ["-period_start"]
        unique_together = [("school", "period_start", "period_end")]

    def __str__(self):
        return f"Analytics {self.period_start} to {self.period_end} — {self.school.name}"

    @property
    def delivery_rate(self):
        total = self.emails_sent + self.sms_sent
        if total == 0:
            return 0
        delivered = self.emails_delivered + self.sms_delivered
        return round((delivered / total) * 100, 2)


class NotificationSchedule(models.Model):
    """Scheduled future notifications."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        CANCELLED = "cancelled", "Cancelled"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="notification_schedules")
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="schedules", null=True, blank=True
    )
    announcement = models.ForeignKey(
        Announcement, on_delete=models.CASCADE, related_name="schedules", null=True, blank=True
    )
    # Schedule
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True, help_text="daily, weekly, monthly")
    recurrence_end = models.DateField(null=True, blank=True)
    # Execution
    last_executed = models.DateTimeField(null=True, blank=True)
    next_execution = models.DateTimeField(null=True, blank=True)
    execution_count = models.PositiveIntegerField(default=0)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_schedules"
        ordering = ["scheduled_at"]
        indexes = [
            models.Index(fields=["school", "status", "scheduled_at"]),
        ]

    def __str__(self):
        return f"Scheduled for {self.scheduled_at} ({self.get_status_display()})"
