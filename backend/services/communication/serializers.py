"""Serializers for communication."""

from rest_framework import serializers

from .models import (
    Announcement,
    AnnouncementRead,
    BroadcastMessage,
    ChatGroup,
    CommunicationAnalytics,
    CommunicationBlacklist,
    CommunicationLog,
    CommunicationPreference,
    ConferenceParticipant,
    DeviceToken,
    DirectMessage,
    EmailIntegration,
    EmailTemplate,
    EmergencyAlert,
    FileAttachment,
    GroupMembership,
    GroupMessage,
    MessageDeliveryStatus,
    MessageReaction,
    MessageTemplate,
    MessageThread,
    Newsletter,
    Notification,
    NotificationSchedule,
    NotificationTemplate,
    ParentTeacherChat,
    ParentTeacherMessage,
    Poll,
    PollVote,
    ReadReceipt,
    SMSGatewayConfig,
    SMSIntegration,
    SMSLog,
    Survey,
    SurveyResponse,
    TypingIndicator,
    VideoConference,
    VoiceMessage,
)


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            "id",
            "school",
            "id",
            "title",
            "content",
            "priority",
            "audience",
            "target_grades",
            "target_classrooms",
            "attachment",
            "send_email",
            "send_sms",
            "send_push",
            "is_draft",
            "created_by",
            "published_at",
            "expires_at",
            "created_at",
        ]
        read_only_fields = ["id", "school", "created_by", "created_at"]


class AnnouncementReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementRead
        fields = ["id", "announcement", "user", "read_at"]
        read_only_fields = ["id"]


class DirectMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectMessage
        fields = [
            "id",
            "id",
            "sender",
            "recipient",
            "content",
            "attachment",
            "status",
            "parent_message",
            "is_deleted_sender",
            "is_deleted_recipient",
            "sent_at",
            "delivered_at",
            "read_at",
        ]
        read_only_fields = ["id", "sender", "status", "sent_at"]

    def validate_recipient(self, value):
        # 1-to-1 messaging is tenant-scoped: sender and recipient must share a school.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Cannot message a user from another school.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        if attrs.get("recipient") and attrs["recipient"].id == user.id:
            raise serializers.ValidationError({"detail": "You cannot send a message to yourself."})
        return attrs


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "school",
            "name",
            "event_type",
            "email_subject",
            "email_body",
            "sms_body",
            "push_title",
            "push_body",
            "is_active",
        ]
        read_only_fields = ["id"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "id",
            "user",
            "title",
            "body",
            "channel",
            "status",
            "reference_type",
            "reference_id",
            "sent_at",
            "read_at",
            "failure_reason",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = [
            "id",
            "user",
            "token",
            "platform",
            "device_id",
            "device_name",
            "app_version",
            "is_active",
            "registered_at",
            "last_used_at",
        ]
        read_only_fields = ["id"]


class ChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "group_type",
            "classroom",
            "subject",
            "created_by",
            "avatar",
            "is_archived",
            "is_muted",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GroupMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMembership
        fields = [
            "id",
            "id",
            "group",
            "user",
            "role",
            "nickname",
            "is_muted",
            "is_pinned",
            "last_read_at",
            "unread_count",
            "joined_at",
            "last_active_at",
        ]
        read_only_fields = ["id"]


class GroupMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = [
            "id",
            "id",
            "group",
            "sender",
            "message_type",
            "content",
            "attachment",
            "reply_to",
            "is_pinned",
            "is_edited",
            "is_deleted",
            "reactions",
            "sent_at",
        ]
        read_only_fields = ["id", "updated_at"]


class ParentTeacherChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentTeacherChat
        fields = [
            "id",
            "school",
            "id",
            "parent",
            "teacher",
            "student",
            "subject",
            "status",
            "is_archived_by_parent",
            "is_archived_by_teacher",
            "last_message_at",
            "parent_unread_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ParentTeacherMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentTeacherMessage
        fields = [
            "id",
            "id",
            "chat",
            "sender",
            "message_type",
            "content",
            "attachment",
            "reply_to",
            "is_read_by_parent",
            "is_read_by_teacher",
            "sent_at",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class VideoConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoConference
        fields = [
            "id",
            "school",
            "id",
            "title",
            "description",
            "conference_type",
            "host",
            "meeting_url",
            "meeting_id",
            "meeting_password",
            "scheduled_at",
            "duration_minutes",
            "status",
            "max_participants",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceParticipant
        fields = ["id", "id", "conference", "user", "status", "joined_at", "left_at", "duration_minutes", "invited_at"]
        read_only_fields = ["id"]


class SMSIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSIntegration
        fields = [
            "id",
            "school",
            "id",
            "provider",
            "from_number",
            "to_number",
            "message",
            "status",
            "provider_message_id",
            "cost",
            "sent_by",
            "error_message",
            "sent_at",
            "delivered_at",
        ]
        read_only_fields = ["id", "created_at"]


class EmailIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailIntegration
        fields = [
            "id",
            "school",
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
            "provider_message_id",
            "attachment",
            "sent_by",
        ]
        read_only_fields = ["id", "created_at"]


class FileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = [
            "id",
            "school",
            "id",
            "uploaded_by",
            "file",
            "file_name",
            "file_type",
            "file_size",
            "mime_type",
            "description",
            "reference_type",
            "reference_id",
            "is_public",
            "download_count",
        ]
        read_only_fields = ["id", "created_at"]


class MessageThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageThread
        fields = [
            "id",
            "id",
            "parent_message",
            "reply_count",
            "last_reply_at",
            "last_reply_by",
            "is_closed",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReadReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadReceipt
        fields = ["id", "id", "message", "user", "read_at"]
        read_only_fields = ["id"]


class TypingIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypingIndicator
        fields = ["id", "id", "user", "chat_type", "chat_id", "started_at", "expires_at"]
        read_only_fields = ["id"]


class MessageReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReaction
        fields = ["id", "id", "message", "user", "emoji", "created_at"]
        read_only_fields = ["id", "created_at"]


class VoiceMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceMessage
        fields = [
            "id",
            "id",
            "sender",
            "group",
            "parent_teacher_chat",
            "audio_file",
            "duration_seconds",
            "file_size",
            "transcription",
            "is_transcribed",
            "sent_at",
        ]
        read_only_fields = ["id"]


class BroadcastMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastMessage
        fields = [
            "id",
            "school",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CommunicationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationLog
        fields = [
            "id",
            "school",
            "id",
            "communication_type",
            "sender",
            "recipient",
            "recipient_group",
            "subject",
            "content_preview",
            "reference_type",
            "reference_id",
            "status",
        ]
        read_only_fields = ["id"]


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = [
            "id",
            "school",
            "id",
            "title",
            "description",
            "survey_type",
            "status",
            "questions",
            "target_audience",
            "target_grades",
            "is_anonymous",
            "allow_multiple_responses",
            "start_date",
            "end_date",
            "total_invited",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = [
            "id",
            "id",
            "survey",
            "respondent_type",
            "student",
            "parent",
            "staff",
            "answers",
            "overall_rating",
            "comments",
            "submitted_at",
        ]
        read_only_fields = ["id"]


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = [
            "id",
            "school",
            "id",
            "created_by",
            "title",
            "description",
            "options",
            "status",
            "target_group",
            "target_audience",
            "is_anonymous",
            "allow_multiple_choices",
            "max_choices",
        ]
        read_only_fields = ["id", "created_at"]


class PollVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollVote
        fields = ["id", "id", "poll", "voter_type", "student", "parent", "staff", "selected_options", "voted_at"]
        read_only_fields = ["id"]


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            "id",
            "school",
            "id",
            "name",
            "category",
            "subject",
            "body_html",
            "body_text",
            "is_active",
            "times_used",
            "last_used_at",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SMSGatewayConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSGatewayConfig
        fields = [
            "id",
            "school",
            "id",
            "provider",
            "api_key",
            "api_secret",
            "sender_id",
            "webhook_url",
            "is_active",
            "total_sms_sent",
            "total_sms_cost",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SMSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSLog
        fields = [
            "id",
            "school",
            "id",
            "recipient_phone",
            "recipient_name",
            "message",
            "status",
            "provider_message_id",
            "cost",
            "error_message",
            "reference_type",
            "reference_id",
            "sent_by",
            "sent_at",
        ]
        read_only_fields = ["id"]


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = [
            "id",
            "school",
            "id",
            "title",
            "subject",
            "content_html",
            "content_text",
            "status",
            "target_audience",
            "target_grades",
            "scheduled_date",
            "sent_date",
            "total_recipients",
            "total_opened",
            "total_clicked",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmergencyAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyAlert
        fields = [
            "id",
            "school",
            "id",
            "title",
            "message",
            "alert_level",
            "status",
            "send_email",
            "send_sms",
            "send_push",
            "send_pa",
            "target_audience",
            "total_sent",
            "total_delivered",
            "total_read",
        ]
        read_only_fields = ["id", "created_at"]


class CommunicationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationPreference
        fields = [
            "id",
            "school",
            "id",
            "user",
            "email_enabled",
            "sms_enabled",
            "push_enabled",
            "in_app_enabled",
            "announcements",
            "fee_notices",
            "attendance_alerts",
            "emergency_alerts",
            "event_reminders",
            "quiet_hours_start",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MessageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTemplate
        fields = [
            "id",
            "school",
            "id",
            "name",
            "template_type",
            "category",
            "subject",
            "body",
            "variables",
            "is_active",
            "times_used",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MessageDeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageDeliveryStatus
        fields = [
            "id",
            "school",
            "id",
            "notification",
            "broadcast",
            "recipient",
            "channel",
            "status",
            "sent_at",
            "delivered_at",
            "read_at",
            "error_message",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CommunicationBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationBlacklist
        fields = [
            "id",
            "school",
            "id",
            "user",
            "channel",
            "category",
            "reason",
            "blacklisted_at",
            "expires_at",
            "is_active",
        ]
        read_only_fields = ["id"]


class CommunicationAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationAnalytics
        fields = [
            "id",
            "school",
            "id",
            "period_start",
            "period_end",
            "emails_sent",
            "emails_delivered",
            "emails_opened",
            "emails_clicked",
            "emails_bounced",
            "emails_unsubscribed",
            "sms_sent",
            "sms_delivered",
            "sms_failed",
            "push_sent",
        ]
        read_only_fields = ["id"]


class NotificationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSchedule
        fields = [
            "id",
            "school",
            "id",
            "notification",
            "announcement",
            "scheduled_at",
            "status",
            "is_recurring",
            "recurrence_pattern",
            "recurrence_end",
            "last_executed",
            "next_execution",
            "execution_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
