"""URL Configuration for communication."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnnouncementReadViewSet,
    AnnouncementViewSet,
    BroadcastMessageViewSet,
    ChatGroupViewSet,
    CommunicationAnalyticsViewSet,
    CommunicationBlacklistViewSet,
    CommunicationLogViewSet,
    CommunicationPreferenceViewSet,
    ConferenceParticipantViewSet,
    DeviceTokenViewSet,
    DirectMessageViewSet,
    EmailIntegrationViewSet,
    EmailTemplateViewSet,
    EmergencyAlertViewSet,
    FileAttachmentViewSet,
    GroupMembershipViewSet,
    GroupMessageViewSet,
    MessageDeliveryStatusViewSet,
    MessageReactionViewSet,
    MessageTemplateViewSet,
    MessageThreadViewSet,
    NewsletterViewSet,
    NotificationScheduleViewSet,
    NotificationTemplateViewSet,
    NotificationViewSet,
    ParentTeacherChatViewSet,
    ParentTeacherMessageViewSet,
    PollViewSet,
    PollVoteViewSet,
    ReadReceiptViewSet,
    SMSGatewayConfigViewSet,
    SMSIntegrationViewSet,
    SMSLogViewSet,
    SurveyResponseViewSet,
    SurveyViewSet,
    TypingIndicatorViewSet,
    VideoConferenceViewSet,
    VoiceMessageViewSet,
)

app_name = "communication_v1"

router = DefaultRouter()
router.register(r"announcement", AnnouncementViewSet, basename="announcement")
router.register(r"announcement-read", AnnouncementReadViewSet, basename="announcement-read")
router.register(r"direct-message", DirectMessageViewSet, basename="direct-message")
router.register(r"notification-template", NotificationTemplateViewSet, basename="notification-template")
router.register(r"notification", NotificationViewSet, basename="notification")
router.register(r"device-token", DeviceTokenViewSet, basename="device-token")
router.register(r"chat-group", ChatGroupViewSet, basename="chat-group")
router.register(r"group-membership", GroupMembershipViewSet, basename="group-membership")
router.register(r"group-message", GroupMessageViewSet, basename="group-message")
router.register(r"parent-teacher-chat", ParentTeacherChatViewSet, basename="parent-teacher-chat")
router.register(r"parent-teacher-message", ParentTeacherMessageViewSet, basename="parent-teacher-message")
router.register(r"video-conference", VideoConferenceViewSet, basename="video-conference")
router.register(r"conference-participant", ConferenceParticipantViewSet, basename="conference-participant")
router.register(r"s-m-s-integration", SMSIntegrationViewSet, basename="s-m-s-integration")
router.register(r"email-integration", EmailIntegrationViewSet, basename="email-integration")
router.register(r"file-attachment", FileAttachmentViewSet, basename="file-attachment")
router.register(r"message-thread", MessageThreadViewSet, basename="message-thread")
router.register(r"read-receipt", ReadReceiptViewSet, basename="read-receipt")
router.register(r"typing-indicator", TypingIndicatorViewSet, basename="typing-indicator")
router.register(r"message-reaction", MessageReactionViewSet, basename="message-reaction")
router.register(r"voice-message", VoiceMessageViewSet, basename="voice-message")
router.register(r"broadcast-message", BroadcastMessageViewSet, basename="broadcast-message")
router.register(r"communication-log", CommunicationLogViewSet, basename="communication-log")
router.register(r"survey", SurveyViewSet, basename="survey")
router.register(r"survey-response", SurveyResponseViewSet, basename="survey-response")
router.register(r"poll", PollViewSet, basename="poll")
router.register(r"poll-vote", PollVoteViewSet, basename="poll-vote")
router.register(r"email-template", EmailTemplateViewSet, basename="email-template")
router.register(r"s-m-s-gateway-config", SMSGatewayConfigViewSet, basename="s-m-s-gateway-config")
router.register(r"s-m-s-log", SMSLogViewSet, basename="s-m-s-log")
router.register(r"newsletter", NewsletterViewSet, basename="newsletter")
router.register(r"emergency-alert", EmergencyAlertViewSet, basename="emergency-alert")
router.register(r"communication-preference", CommunicationPreferenceViewSet, basename="communication-preference")
router.register(r"message-template", MessageTemplateViewSet, basename="message-template")
router.register(r"message-delivery-status", MessageDeliveryStatusViewSet, basename="message-delivery-status")
router.register(r"communication-blacklist", CommunicationBlacklistViewSet, basename="communication-blacklist")
router.register(r"communication-analytics", CommunicationAnalyticsViewSet, basename="communication-analytics")
router.register(r"notification-schedule", NotificationScheduleViewSet, basename="notification-schedule")

urlpatterns = [
    path("", include(router.urls)),
]
