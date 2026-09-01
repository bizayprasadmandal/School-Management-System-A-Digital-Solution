"""URL Configuration for conferences."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ConferenceAccessibilityRequirementViewSet,
    ConferenceAnalyticsViewSet,
    ConferenceApprovalViewSet,
    ConferenceAvailabilityViewSet,
    ConferenceBlockedSlotViewSet,
    ConferenceBookingRuleViewSet,
    ConferenceBookingViewSet,
    ConferenceCalendarSyncViewSet,
    ConferenceConferenceTypeViewSet,
    ConferenceExportViewSet,
    ConferenceFeedbackTemplateViewSet,
    ConferenceFeedbackViewSet,
    ConferenceFollowUpViewSet,
    ConferenceHistoryDetailViewSet,
    ConferenceHistoryViewSet,
    ConferenceLocationViewSet,
    ConferenceNoShowViewSet,
    ConferenceNotesViewSet,
    ConferenceNoteTemplateViewSet,
    ConferenceReminderScheduleViewSet,
    ConferenceReminderViewSet,
    ConferenceReportViewSet,
    ConferenceResourceViewSet,
    ConferenceRoomBookingViewSet,
    ConferenceScheduleOverrideViewSet,
    ConferenceSettingsViewSet,
    ConferenceSlotViewSet,
    ConferenceSurveyResponseViewSet,
    ConferenceSurveyViewSet,
    ConferenceSystemNotificationViewSet,
    ConferenceTemplateSectionViewSet,
    ConferenceTemplateViewSet,
    ConferenceTimeSlotViewSet,
    ConferenceTypeViewSet,
    ConferenceWaitingListViewSet,
    FollowUpTrackingViewSet,
    RecurringConferenceParticipantViewSet,
    RecurringConferenceViewSet,
    VirtualConferenceViewSet,
    WaitlistManagementViewSet,
)

app_name = "conferences_v1"

router = DefaultRouter()
router.register(r"conference-slot", ConferenceSlotViewSet, basename="conference-slot")
router.register(r"conference-type", ConferenceTypeViewSet, basename="conference-type")
router.register(r"conference-booking", ConferenceBookingViewSet, basename="conference-booking")
router.register(r"conference-reminder", ConferenceReminderViewSet, basename="conference-reminder")
router.register(r"conference-notes", ConferenceNotesViewSet, basename="conference-notes")
router.register(r"follow-up-tracking", FollowUpTrackingViewSet, basename="follow-up-tracking")
router.register(r"conference-availability", ConferenceAvailabilityViewSet, basename="conference-availability")
router.register(r"conference-report", ConferenceReportViewSet, basename="conference-report")
router.register(r"conference-feedback", ConferenceFeedbackViewSet, basename="conference-feedback")
router.register(r"conference-history", ConferenceHistoryViewSet, basename="conference-history")
router.register(r"virtual-conference", VirtualConferenceViewSet, basename="virtual-conference")
router.register(r"conference-template", ConferenceTemplateViewSet, basename="conference-template")
router.register(r"waitlist-management", WaitlistManagementViewSet, basename="waitlist-management")
router.register(r"conference-waiting-list", ConferenceWaitingListViewSet, basename="conference-waiting-list")
router.register(r"recurring-conference", RecurringConferenceViewSet, basename="recurring-conference")
router.register(
    r"recurring-conference-participant",
    RecurringConferenceParticipantViewSet,
    basename="recurring-conference-participant",
)
router.register(r"conference-settings", ConferenceSettingsViewSet, basename="conference-settings")
router.register(r"conference-analytics", ConferenceAnalyticsViewSet, basename="conference-analytics")
router.register(r"conference-booking-rule", ConferenceBookingRuleViewSet, basename="conference-booking-rule")
router.register(
    r"conference-system-notification", ConferenceSystemNotificationViewSet, basename="conference-system-notification"
)
router.register(r"conference-export", ConferenceExportViewSet, basename="conference-export")
router.register(r"conference-location", ConferenceLocationViewSet, basename="conference-location")
router.register(r"conference-blocked-slot", ConferenceBlockedSlotViewSet, basename="conference-blocked-slot")
router.register(
    r"conference-schedule-override", ConferenceScheduleOverrideViewSet, basename="conference-schedule-override"
)
router.register(
    r"conference-reminder-schedule", ConferenceReminderScheduleViewSet, basename="conference-reminder-schedule"
)
router.register(
    r"conference-accessibility-requirement",
    ConferenceAccessibilityRequirementViewSet,
    basename="conference-accessibility-requirement",
)
router.register(r"conference-note-template", ConferenceNoteTemplateViewSet, basename="conference-note-template")
router.register(r"conference-approval", ConferenceApprovalViewSet, basename="conference-approval")
router.register(r"conference-resource", ConferenceResourceViewSet, basename="conference-resource")
router.register(r"conference-survey", ConferenceSurveyViewSet, basename="conference-survey")
router.register(r"conference-survey-response", ConferenceSurveyResponseViewSet, basename="conference-survey-response")
router.register(r"conference-calendar-sync", ConferenceCalendarSyncViewSet, basename="conference-calendar-sync")
router.register(r"conference-history-detail", ConferenceHistoryDetailViewSet, basename="conference-history-detail")
router.register(r"conference-time-slot", ConferenceTimeSlotViewSet, basename="conference-time-slot")
router.register(
    r"conference-feedback-template", ConferenceFeedbackTemplateViewSet, basename="conference-feedback-template"
)
router.register(r"conference-follow-up", ConferenceFollowUpViewSet, basename="conference-follow-up")
router.register(r"conference-room-booking", ConferenceRoomBookingViewSet, basename="conference-room-booking")
router.register(
    r"conference-template-section", ConferenceTemplateSectionViewSet, basename="conference-template-section"
)
router.register(r"conference-no-show", ConferenceNoShowViewSet, basename="conference-no-show")
router.register(r"conference-conference-type", ConferenceConferenceTypeViewSet, basename="conference-conference-type")

urlpatterns = [
    path("", include(router.urls)),
]
