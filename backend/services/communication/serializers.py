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
            "on_delete",
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
            "published_at",
            "expires_at",
        ]
        read_only_fields = ["id", "created_at"]


class AnnouncementReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementRead
        fields = ["id", "announcement", "on_delete", "user", "on_delete", "read_at"]
        read_only_fields = ["id"]


class DirectMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectMessage
        fields = [
            "id",
            "id",
            "sender",
            "on_delete",
            "recipient",
            "on_delete",
            "content",
            "attachment",
            "status",
            "parent_message",
            "on_delete",
            "is_deleted_sender",
            "is_deleted_recipient",
            "sent_at",
            "delivered_at",
            "read_at",
        ]
        read_only_fields = ["id"]


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "school",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "name",
            "description",
            "group_type",
            "classroom",
            "on_delete",
            "subject",
            "on_delete",
            "created_by",
            "on_delete",
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
            "on_delete",
            "user",
            "on_delete",
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
            "on_delete",
            "sender",
            "on_delete",
            "message_type",
            "content",
            "attachment",
            "reply_to",
            "on_delete",
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
            "on_delete",
            "parent",
            "on_delete",
            "teacher",
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "sender",
            "on_delete",
            "message_type",
            "content",
            "attachment",
            "reply_to",
            "on_delete",
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
            "on_delete",
            "title",
            "description",
            "conference_type",
            "host",
            "on_delete",
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
        fields = [
            "id",
            "id",
            "conference",
            "on_delete",
            "user",
            "on_delete",
            "status",
            "joined_at",
            "left_at",
            "duration_minutes",
            "invited_at",
        ]
        read_only_fields = ["id"]


class SMSIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSIntegration
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "provider",
            "from_number",
            "to_number",
            "message",
            "status",
            "provider_message_id",
            "cost",
            "sent_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "uploaded_by",
            "on_delete",
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
            "on_delete",
            "reply_count",
            "last_reply_at",
            "last_reply_by",
            "on_delete",
            "is_closed",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReadReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadReceipt
        fields = ["id", "id", "message", "on_delete", "user", "on_delete", "read_at"]
        read_only_fields = ["id"]


class TypingIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypingIndicator
        fields = ["id", "id", "user", "on_delete", "chat_type", "chat_id", "started_at", "expires_at"]
        read_only_fields = ["id"]


class MessageReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReaction
        fields = ["id", "id", "message", "on_delete", "user", "on_delete", "emoji", "created_at"]
        read_only_fields = ["id", "created_at"]


class VoiceMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceMessage
        fields = [
            "id",
            "id",
            "sender",
            "on_delete",
            "group",
            "on_delete",
            "parent_teacher_chat",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "communication_type",
            "sender",
            "on_delete",
            "recipient",
            "on_delete",
            "recipient_group",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "respondent_type",
            "student",
            "on_delete",
            "parent",
            "on_delete",
            "staff",
            "on_delete",
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
            "on_delete",
            "created_by",
            "on_delete",
            "title",
            "description",
            "options",
            "status",
            "target_group",
            "on_delete",
            "target_audience",
            "is_anonymous",
            "allow_multiple_choices",
            "max_choices",
        ]
        read_only_fields = ["id", "created_at"]


class PollVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollVote
        fields = [
            "id",
            "id",
            "poll",
            "on_delete",
            "voter_type",
            "student",
            "on_delete",
            "parent",
            "on_delete",
            "staff",
            "on_delete",
            "selected_options",
            "voted_at",
        ]
        read_only_fields = ["id"]


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "category",
            "subject",
            "body_html",
            "body_text",
            "is_active",
            "times_used",
            "last_used_at",
            "created_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "on_delete",
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
            "on_delete",
            "name",
            "template_type",
            "category",
            "subject",
            "body",
            "variables",
            "is_active",
            "times_used",
            "created_by",
            "on_delete",
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
            "on_delete",
            "notification",
            "on_delete",
            "broadcast",
            "on_delete",
            "recipient",
            "on_delete",
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
            "on_delete",
            "user",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "notification",
            "on_delete",
            "announcement",
            "on_delete",
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
