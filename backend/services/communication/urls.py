from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "communication_v1"
router = DefaultRouter()

# Core communication endpoints
router.register("announcements", views.AnnouncementViewSet, basename="announcement")
router.register("messages", views.DirectMessageViewSet, basename="message")
router.register("notifications", views.NotificationViewSet, basename="notification")

# Group messaging
router.register("chat-groups", views.ChatGroupViewSet, basename="chat-group")
router.register("group-messages", views.GroupMessageViewSet, basename="group-message")
router.register("message-reactions", views.MessageReactionViewSet, basename="message-reaction")
router.register("read-receipts", views.ReadReceiptViewSet, basename="read-receipt")
router.register("typing-indicators", views.TypingIndicatorViewSet, basename="typing-indicator")
router.register("message-threads", views.MessageThreadViewSet, basename="message-thread")

# File sharing
router.register("attachments", views.FileAttachmentViewSet, basename="file-attachment")

# Parent-teacher chat
router.register("parent-teacher-chats", views.ParentTeacherChatViewSet, basename="parent-teacher-chat")
router.register("parent-teacher-messages", views.ParentTeacherMessageViewSet, basename="parent-teacher-message")

# Video conferencing
router.register("video-conferences", views.VideoConferenceViewSet, basename="video-conference")
router.register("conference-participants", views.ConferenceParticipantViewSet, basename="conference-participant")

# SMS/Email integration
router.register("sms", views.SMSIntegrationViewSet, basename="sms-integration")
router.register("emails", views.EmailIntegrationViewSet, basename="email-integration")

# Voice messages
router.register("voice-messages", views.VoiceMessageViewSet, basename="voice-message")

# Broadcast messages
router.register("broadcasts", views.BroadcastMessageViewSet, basename="broadcast-message")

# Communication logs
router.register("logs", views.CommunicationLogViewSet, basename="communication-log")


# ── Additional registrations (module expansion) ──
router.register(r"announcement-read", views.AnnouncementReadViewSet, basename="announcement-read")
router.register(r"notification-template", views.NotificationTemplateViewSet, basename="notification-template")
router.register(r"device-token", views.DeviceTokenViewSet, basename="device-token")
router.register(r"group-membership", views.GroupMembershipViewSet, basename="group-membership")
router.register(r"survey", views.SurveyViewSet, basename="survey")
router.register(r"survey-response", views.SurveyResponseViewSet, basename="survey-response")
router.register(r"poll", views.PollViewSet, basename="poll")
router.register(r"poll-vote", views.PollVoteViewSet, basename="poll-vote")
router.register(r"email-template", views.EmailTemplateViewSet, basename="email-template")
router.register(r"s-m-s-gateway-config", views.SMSGatewayConfigViewSet, basename="s-m-s-gateway-config")
router.register(r"s-m-s-log", views.SMSLogViewSet, basename="s-m-s-log")
router.register(r"newsletter", views.NewsletterViewSet, basename="newsletter")
router.register(r"emergency-alert", views.EmergencyAlertViewSet, basename="emergency-alert")
router.register(r"communication-preference", views.CommunicationPreferenceViewSet, basename="communication-preference")
router.register(r"message-template", views.MessageTemplateViewSet, basename="message-template")
router.register(r"message-delivery-status", views.MessageDeliveryStatusViewSet, basename="message-delivery-status")
router.register(r"communication-blacklist", views.CommunicationBlacklistViewSet, basename="communication-blacklist")
router.register(r"communication-analytics", views.CommunicationAnalyticsViewSet, basename="communication-analytics")
router.register(r"notification-schedule", views.NotificationScheduleViewSet, basename="notification-schedule")

urlpatterns = [
    path("", include(router.urls)),
    path("push-tokens/", views.DeviceTokenView.as_view({"post": "create"}), name="push-token-create"),
    path("push-tokens/<path:pk>/", views.DeviceTokenView.as_view({"delete": "destroy"}), name="push-token-delete"),
]
