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

urlpatterns = [
    path("", include(router.urls)),
    path("push-tokens/", views.DeviceTokenView.as_view({"post": "create"}), name="push-token-create"),
    path("push-tokens/<path:pk>/", views.DeviceTokenView.as_view({"delete": "destroy"}), name="push-token-delete"),
]
