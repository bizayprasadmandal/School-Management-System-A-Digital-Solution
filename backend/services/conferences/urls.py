"""Conference Scheduler URL Configuration with Zoom integration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ConferenceAvailabilityViewSet,
    ConferenceBookingViewSet,
    ConferenceFeedbackViewSet,
    ConferenceHistoryViewSet,
    ConferenceNotesViewSet,
    ConferenceReminderViewSet,
    ConferenceReportViewSet,
    ConferenceSlotViewSet,
    ConferenceTemplateViewSet,
    ConferenceTypeViewSet,
    FollowUpTrackingViewSet,
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

urlpatterns = [
    path("", include(router.urls)),
    # Zoom integration
    path("zoom/connection/", ZoomConnectionView.as_view(), name="zoom_connection"),
    path("zoom/meetings/", ZoomMeetingsListView.as_view(), name="zoom_meetings"),
]
