from django.contrib import admin

from .models import (
    Announcement,
    BroadcastMessage,
    ChatGroup,
    CommunicationLog,
    ConferenceParticipant,
    DirectMessage,
    EmailIntegration,
    FileAttachment,
    GroupMembership,
    GroupMessage,
    MessageReaction,
    MessageThread,
    Notification,
    NotificationTemplate,
    ParentTeacherChat,
    ParentTeacherMessage,
    ReadReceipt,
    SMSIntegration,
    TypingIndicator,
    VideoConference,
    VoiceMessage,
)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["title", "priority", "audience", "is_draft", "view_count", "created_at"]
    list_filter = ["priority", "audience", "is_draft", "school"]
    search_fields = ["title", "content"]
    readonly_fields = ["view_count", "created_at"]


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "recipient", "status", "sent_at"]
    list_filter = ["status"]
    search_fields = ["sender__email", "recipient__email"]
    readonly_fields = ["id", "sent_at", "delivered_at", "read_at"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "channel", "status", "created_at"]
    list_filter = ["channel", "status"]
    search_fields = ["user__email", "title"]


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "event_type", "school", "is_active"]
    list_filter = ["is_active", "school"]


# =============================================================================
# Group Messaging
# =============================================================================


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "group_type", "school", "member_count", "is_archived", "created_at"]
    list_filter = ["group_type", "is_archived", "school"]
    search_fields = ["name", "description"]
    inlines = [GroupMembershipInline]


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "group", "role", "is_muted", "unread_count", "joined_at"]
    list_filter = ["role", "is_muted"]
    search_fields = ["user__email", "group__name"]


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "group", "message_type", "content", "is_pinned", "sent_at"]
    list_filter = ["message_type", "is_pinned"]
    search_fields = ["sender__email", "content"]
    date_hierarchy = "sent_at"


# =============================================================================
# Parent-Teacher Chat
# =============================================================================


class ParentTeacherMessageInline(admin.TabularInline):
    model = ParentTeacherMessage
    extra = 0


@admin.register(ParentTeacherChat)
class ParentTeacherChatAdmin(admin.ModelAdmin):
    list_display = ["parent", "teacher", "student", "status", "last_message_at"]
    list_filter = ["status"]
    search_fields = ["parent__email", "teacher__email"]
    inlines = [ParentTeacherMessageInline]


@admin.register(ParentTeacherMessage)
class ParentTeacherMessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "chat", "message_type", "is_read_by_parent", "is_read_by_teacher", "sent_at"]
    list_filter = ["message_type", "is_read_by_parent", "is_read_by_teacher"]
    search_fields = ["sender__email", "content"]
    date_hierarchy = "sent_at"


# =============================================================================
# Video Conferencing
# =============================================================================


class ConferenceParticipantInline(admin.TabularInline):
    model = ConferenceParticipant
    extra = 0


@admin.register(VideoConference)
class VideoConferenceAdmin(admin.ModelAdmin):
    list_display = ["title", "conference_type", "host", "status", "scheduled_at", "duration_minutes"]
    list_filter = ["conference_type", "status"]
    search_fields = ["title", "description"]
    date_hierarchy = "scheduled_at"
    inlines = [ConferenceParticipantInline]


@admin.register(ConferenceParticipant)
class ConferenceParticipantAdmin(admin.ModelAdmin):
    list_display = ["user", "conference", "status", "joined_at", "left_at", "duration_minutes"]
    list_filter = ["status"]
    search_fields = ["user__email"]


# =============================================================================
# SMS/Email Integration
# =============================================================================


@admin.register(SMSIntegration)
class SMSIntegrationAdmin(admin.ModelAdmin):
    list_display = ["to_number", "message", "provider", "status", "sent_at", "cost"]
    list_filter = ["provider", "status"]
    search_fields = ["to_number", "message"]
    date_hierarchy = "created_at"


@admin.register(EmailIntegration)
class EmailIntegrationAdmin(admin.ModelAdmin):
    list_display = ["to_email", "subject", "provider", "status", "sent_at"]
    list_filter = ["provider", "status"]
    search_fields = ["to_email", "subject"]
    date_hierarchy = "created_at"


# =============================================================================
# File Sharing
# =============================================================================


@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ["file_name", "file_type", "uploaded_by", "file_size", "download_count", "created_at"]
    list_filter = ["file_type", "is_public"]
    search_fields = ["file_name", "description"]
    date_hierarchy = "created_at"


# =============================================================================
# Message Threading
# =============================================================================


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ["parent_message", "reply_count", "last_reply_at", "is_closed"]
    list_filter = ["is_closed"]
    date_hierarchy = "last_reply_at"


# =============================================================================
# Read Receipts
# =============================================================================


@admin.register(ReadReceipt)
class ReadReceiptAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "read_at"]
    search_fields = ["user__email"]
    date_hierarchy = "read_at"


# =============================================================================
# Typing Indicators
# =============================================================================


@admin.register(TypingIndicator)
class TypingIndicatorAdmin(admin.ModelAdmin):
    list_display = ["user", "chat_type", "chat_id", "started_at", "expires_at"]
    list_filter = ["chat_type"]
    search_fields = ["user__email"]


# =============================================================================
# Message Reactions
# =============================================================================


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "emoji", "created_at"]
    search_fields = ["user__email"]
    date_hierarchy = "created_at"


# =============================================================================
# Voice Messages
# =============================================================================


@admin.register(VoiceMessage)
class VoiceMessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "duration_seconds", "file_size", "is_transcribed", "sent_at"]
    list_filter = ["is_transcribed"]
    search_fields = ["sender__email", "transcription"]
    date_hierarchy = "sent_at"


# =============================================================================
# Broadcast Messages
# =============================================================================


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ["title", "channel", "status", "total_recipients", "total_delivered", "total_read", "created_at"]
    list_filter = ["channel", "status"]
    search_fields = ["title", "content"]
    date_hierarchy = "created_at"
    readonly_fields = ["total_recipients", "total_sent", "total_delivered", "total_failed", "total_read"]


# =============================================================================
# Communication Logs
# =============================================================================


@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = ["communication_type", "sender", "recipient", "status", "sent_at", "cost"]
    list_filter = ["communication_type", "status"]
    search_fields = ["sender__email", "recipient__email", "subject"]
    date_hierarchy = "sent_at"
    readonly_fields = ["cost"]
