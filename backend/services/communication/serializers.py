"""
Communication Service — DRF Serializers
"""

from rest_framework import serializers

from .models import (
    Announcement,
    BroadcastMessage,
    ChatGroup,
    CommunicationLog,
    ConferenceParticipant,
    DeviceToken,
    DirectMessage,
    EmailIntegration,
    FileAttachment,
    GroupMembership,
    GroupMessage,
    MessageReaction,
    MessageThread,
    Notification,
    ParentTeacherChat,
    ParentTeacherMessage,
    ReadReceipt,
    SMSIntegration,
    TypingIndicator,
    VideoConference,
    VoiceMessage,
)


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "content",
            "priority",
            "audience",
            "send_email",
            "send_sms",
            "send_push",
            "target_grades",
            "target_classrooms",
            "published_at",
            "expires_at",
            "is_draft",
            "view_count",
            "created_by_name",
            "created_at",
            "is_read",
            "attachment",
        ]
        read_only_fields = ["id", "created_by", "created_at", "published_at", "view_count"]

    MAX_FILE_SIZE_MB = 10

    def validate_attachment(self, value):
        if value and value.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"File size must not exceed {self.MAX_FILE_SIZE_MB} MB.")
        if value:
            allowed_types = [
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/gif",
                "text/plain",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"File type '{value.content_type}' is not allowed. "
                    f"Allowed types: PDF, JPEG, PNG, GIF, TXT, DOC, DOCX."
                )
        return value

    def get_is_read(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.reads.filter(user=request.user).exists()


class DirectMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    sender_avatar = serializers.ImageField(source="sender.avatar", read_only=True)
    sender_role = serializers.CharField(source="sender.role", read_only=True)
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True)
    recipient_avatar = serializers.ImageField(source="recipient.avatar", read_only=True)

    class Meta:
        model = DirectMessage
        fields = [
            "id",
            "sender",
            "sender_name",
            "sender_avatar",
            "sender_role",
            "recipient",
            "recipient_name",
            "recipient_avatar",
            "content",
            "attachment",
            "status",
            "sent_at",
            "read_at",
            "parent_message",
        ]
        read_only_fields = ["id", "sender", "status", "sent_at", "read_at"]

    def validate_recipient(self, value):
        request = self.context["request"]
        if value == request.user:
            raise serializers.ValidationError("You cannot message yourself.")
        if value.school != request.user.school:
            raise serializers.ValidationError("Recipient must be in the same school.")
        return value

    MAX_FILE_SIZE_MB = 10

    def validate_attachment(self, value):
        if value and value.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"File size must not exceed {self.MAX_FILE_SIZE_MB} MB.")
        if value:
            allowed_types = [
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/gif",
                "text/plain",
            ]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"File type '{value.content_type}' is not allowed. " f"Allowed types: PDF, JPEG, PNG, GIF, TXT."
                )
        return value

    def create(self, validated_data):
        return DirectMessage.objects.create(**validated_data)


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Register/update a push notification token for the authenticated user."""

    class Meta:
        model = DeviceToken
        fields = ["id", "token", "platform", "device_id", "device_name", "app_version", "is_active"]
        read_only_fields = ["id", "is_active"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        # Upsert: if token already exists for this user, update it
        token, created = DeviceToken.objects.update_or_create(
            token=validated_data["token"],
            defaults={
                "user": validated_data["user"],
                "platform": validated_data.get("platform", "android"),
                "device_id": validated_data.get("device_id", ""),
                "device_name": validated_data.get("device_name", ""),
                "app_version": validated_data.get("app_version", ""),
                "is_active": True,
            },
        )
        return token


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "body",
            "channel",
            "status",
            "reference_type",
            "reference_id",
            "created_at",
            "sent_at",
            "read_at",
        ]
        read_only_fields = fields


# =============================================================================
# Group Messaging Serializers
# =============================================================================


class GroupMembershipSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = GroupMembership
        fields = [
            "id",
            "group",
            "user",
            "user_name",
            "user_email",
            "role",
            "nickname",
            "is_muted",
            "is_pinned",
            "unread_count",
            "joined_at",
        ]
        read_only_fields = ["id", "joined_at", "unread_count"]


class ChatGroupSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatGroup
        fields = [
            "id",
            "name",
            "description",
            "group_type",
            "classroom",
            "subject",
            "created_by",
            "created_by_name",
            "avatar",
            "is_archived",
            "is_muted",
            "max_members",
            "member_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_member_count(self, obj):
        return obj.member_count


class GroupMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = GroupMessage
        fields = [
            "id",
            "group",
            "sender",
            "sender_name",
            "message_type",
            "content",
            "attachment",
            "reply_to",
            "is_pinned",
            "is_edited",
            "reactions",
            "sent_at",
            "reply_count",
        ]
        read_only_fields = ["id", "sender", "is_pinned", "is_edited", "sent_at"]

    def get_reply_count(self, obj):
        return obj.reply_count


# =============================================================================
# Parent-Teacher Chat Serializers
# =============================================================================


class ParentTeacherMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)

    class Meta:
        model = ParentTeacherMessage
        fields = [
            "id",
            "chat",
            "sender",
            "sender_name",
            "message_type",
            "content",
            "attachment",
            "reply_to",
            "is_read_by_parent",
            "is_read_by_teacher",
            "sent_at",
        ]
        read_only_fields = ["id", "sender", "is_read_by_parent", "is_read_by_teacher", "sent_at"]


class ParentTeacherChatSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.full_name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ParentTeacherChat
        fields = [
            "id",
            "parent",
            "parent_name",
            "teacher",
            "teacher_name",
            "student",
            "student_name",
            "subject",
            "status",
            "last_message_at",
            "parent_unread_count",
            "teacher_unread_count",
            "last_message",
            "created_at",
        ]
        read_only_fields = ["id", "last_message_at", "parent_unread_count", "teacher_unread_count", "created_at"]

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return ParentTeacherMessageSerializer(last_msg, context=self.context).data
        return None


# =============================================================================
# Video Conferencing Serializers
# =============================================================================


class ConferenceParticipantSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ConferenceParticipant
        fields = [
            "id",
            "conference",
            "user",
            "user_name",
            "status",
            "joined_at",
            "left_at",
            "duration_minutes",
            "invited_at",
        ]
        read_only_fields = ["id", "invited_at"]


class VideoConferenceSerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(source="host.full_name", read_only=True)
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = VideoConference
        fields = [
            "id",
            "title",
            "description",
            "conference_type",
            "host",
            "host_name",
            "meeting_url",
            "meeting_id",
            "scheduled_at",
            "duration_minutes",
            "status",
            "max_participants",
            "is_recorded",
            "recording_url",
            "participant_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_participant_count(self, obj):
        return obj.participants.count()


# =============================================================================
# SMS/Email Integration Serializers
# =============================================================================


class SMSIntegrationSerializer(serializers.ModelSerializer):
    sent_by_name = serializers.CharField(source="sent_by.full_name", read_only=True, default=None)

    class Meta:
        model = SMSIntegration
        fields = [
            "id",
            "provider",
            "from_number",
            "to_number",
            "message",
            "status",
            "cost",
            "sent_by",
            "sent_by_name",
            "error_message",
            "sent_at",
            "delivered_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "provider_message_id",
            "cost",
            "error_message",
            "sent_at",
            "delivered_at",
            "created_at",
        ]


class EmailIntegrationSerializer(serializers.ModelSerializer):
    sent_by_name = serializers.CharField(source="sent_by.full_name", read_only=True, default=None)

    class Meta:
        model = EmailIntegration
        fields = [
            "id",
            "provider",
            "from_email",
            "to_email",
            "cc_emails",
            "bcc_emails",
            "subject",
            "body_html",
            "body_text",
            "status",
            "attachment",
            "sent_by",
            "sent_by_name",
            "error_message",
            "sent_at",
            "delivered_at",
            "opened_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "provider_message_id",
            "error_message",
            "sent_at",
            "delivered_at",
            "opened_at",
            "clicked_at",
            "created_at",
        ]


# =============================================================================
# File Sharing Serializers
# =============================================================================


class FileAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True)
    file_size_display = serializers.SerializerMethodField()

    class Meta:
        model = FileAttachment
        fields = [
            "id",
            "uploaded_by",
            "uploaded_by_name",
            "file",
            "file_name",
            "file_type",
            "file_size",
            "file_size_display",
            "mime_type",
            "description",
            "is_public",
            "download_count",
            "created_at",
        ]
        read_only_fields = ["id", "download_count", "created_at"]

    def get_file_size_display(self, obj):
        return obj.file_size_display


# =============================================================================
# Message Threading Serializers
# =============================================================================


class MessageThreadSerializer(serializers.ModelSerializer):
    last_reply_by_name = serializers.CharField(source="last_reply_by.full_name", read_only=True, default=None)

    class Meta:
        model = MessageThread
        fields = [
            "id",
            "parent_message",
            "reply_count",
            "last_reply_at",
            "last_reply_by",
            "last_reply_by_name",
            "is_closed",
            "created_at",
        ]
        read_only_fields = ["id", "reply_count", "last_reply_at", "created_at"]


# =============================================================================
# Read Receipts Serializers
# =============================================================================


class ReadReceiptSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ReadReceipt
        fields = ["id", "message", "user", "user_name", "read_at"]
        read_only_fields = ["id", "read_at"]


# =============================================================================
# Typing Indicators Serializers
# =============================================================================


class TypingIndicatorSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = TypingIndicator
        fields = ["id", "user", "user_name", "chat_type", "chat_id", "started_at", "expires_at"]
        read_only_fields = ["id", "started_at"]


# =============================================================================
# Message Reactions Serializers
# =============================================================================


class MessageReactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = MessageReaction
        fields = ["id", "message", "user", "user_name", "emoji", "created_at"]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Voice Messages Serializers
# =============================================================================


class VoiceMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = VoiceMessage
        fields = [
            "id",
            "sender",
            "sender_name",
            "group",
            "parent_teacher_chat",
            "audio_file",
            "duration_seconds",
            "duration_display",
            "file_size",
            "transcription",
            "is_transcribed",
            "sent_at",
        ]
        read_only_fields = ["id", "sent_at"]

    def get_duration_display(self, obj):
        return obj.duration_display


# =============================================================================
# Broadcast Messages Serializers
# =============================================================================


class BroadcastMessageSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    delivery_rate = serializers.SerializerMethodField()
    read_rate = serializers.SerializerMethodField()

    class Meta:
        model = BroadcastMessage
        fields = [
            "id",
            "title",
            "content",
            "channel",
            "target_audience",
            "target_classrooms",
            "target_grades",
            "target_users",
            "status",
            "scheduled_at",
            "sent_at",
            "total_recipients",
            "total_sent",
            "total_delivered",
            "total_failed",
            "total_read",
            "priority",
            "require_read_receipt",
            "allow_reply",
            "attachment",
            "created_by",
            "created_by_name",
            "delivery_rate",
            "read_rate",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "total_recipients",
            "total_sent",
            "total_delivered",
            "total_failed",
            "total_read",
            "created_at",
            "updated_at",
        ]

    def get_delivery_rate(self, obj):
        return obj.delivery_rate

    def get_read_rate(self, obj):
        return obj.read_rate


# =============================================================================
# Communication Logs Serializers
# =============================================================================


class CommunicationLogSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True, default=None)
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True, default=None)

    class Meta:
        model = CommunicationLog
        fields = [
            "id",
            "communication_type",
            "sender",
            "sender_name",
            "recipient",
            "recipient_name",
            "subject",
            "content_preview",
            "status",
            "sent_at",
            "delivered_at",
            "read_at",
            "cost",
            "error_message",
        ]
        read_only_fields = fields
