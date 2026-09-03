"""Conference Scheduler URL Configuration with Zoom integration."""

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
    ZoomConnectionView,
    ZoomMeetingsListView,
)

app_name = "conferences"

router = DefaultRouter()
router.register(r"conference-slots", ConferenceSlotViewSet, basename="conference_slot")
router.register(r"conference-types", ConferenceTypeViewSet, basename="conference_type")
router.register(r"bookings", ConferenceBookingViewSet, basename="conference_booking")
router.register(r"reminders", ConferenceReminderViewSet, basename="conference_reminder")
router.register(r"notes", ConferenceNotesViewSet, basename="conference_notes")
router.register(r"follow-ups", FollowUpTrackingViewSet, basename="follow_up")
router.register(r"availability", ConferenceAvailabilityViewSet, basename="conference_availability")
router.register(r"reports", ConferenceReportViewSet, basename="conference_report")
router.register(r"feedback", ConferenceFeedbackViewSet, basename="conference_feedback")
router.register(r"history", ConferenceHistoryViewSet, basename="conference_history")
router.register(r"virtual", VirtualConferenceViewSet, basename="virtual_conference")
router.register(r"templates", ConferenceTemplateViewSet, basename="conference_template")
router.register(r"waitlist", WaitlistManagementViewSet, basename="waitlist")


# ── Additional registrations (module expansion) ──
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
    # Zoom integration
    path("zoom/connection/", ZoomConnectionView.as_view(), name="zoom_connection"),
    path("zoom/meetings/", ZoomMeetingsListView.as_view(), name="zoom_meetings"),
]
