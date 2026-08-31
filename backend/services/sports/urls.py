from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ComplianceTrackingViewSet,
    EquipmentInventoryViewSet,
    FacilityBookingViewSet,
    GameLineupViewSet,
    InjuryTrackingViewSet,
    LeagueStandingViewSet,
    LiveGameScoreViewSet,
    LiveStreamingViewSet,
    MultiSportSchedulingViewSet,
    PlayerDevelopmentPlanViewSet,
    PlayerStatisticsViewSet,
    PracticeScheduleViewSet,
    RefereeAssignmentViewSet,
    RefereeManagementViewSet,
    RefundManagementViewSet,
    SeasonPassMembershipViewSet,
    SportAchievementViewSet,
    SportEventViewSet,
    SportsAnalyticsViewSet,
    SportsAttendanceViewSet,
    SportsFundraisingViewSet,
    SportsMedicalClearanceViewSet,
    SportsPhotoGalleryViewSet,
    SportsRegistrationViewSet,
    SportsSponsorshipViewSet,
    SportsTravelManagementViewSet,
    SportsUniformOrderViewSet,
    SportsVolunteerManagementViewSet,
    SportViewSet,
    TeamCommunicationViewSet,
    TeamMemberViewSet,
    TeamRosterViewSet,
    TeamViewSet,
    TryoutAssessmentViewSet,
    TryoutScoreViewSet,
    VideoAnalysisViewSet,
    WearableIntegrationViewSet,
    WeatherIntegrationViewSet,
)

app_name = "sports_v1"
router = DefaultRouter()
# Core
router.register(r"sports", SportViewSet, basename="sport")
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"team-members", TeamMemberViewSet, basename="team-member")
router.register(r"events", SportEventViewSet, basename="sport-event")
router.register(r"achievements", SportAchievementViewSet, basename="sport-achievement")
# Registration & Attendance
router.register(r"registrations", SportsRegistrationViewSet, basename="sports-registration")
router.register(r"attendance", SportsAttendanceViewSet, basename="sports-attendance")
# Practice & Training
router.register(r"practices", PracticeScheduleViewSet, basename="practice-schedule")
router.register(r"statistics", PlayerStatisticsViewSet, basename="player-statistics")
router.register(r"rosters", TeamRosterViewSet, basename="team-roster")
router.register(r"lineups", GameLineupViewSet, basename="game-lineup")
# Health & Medical
router.register(r"injuries", InjuryTrackingViewSet, basename="injury-tracking")
router.register(r"medical-clearances", SportsMedicalClearanceViewSet, basename="sports-medical-clearance")
# Equipment
router.register(r"equipment", EquipmentInventoryViewSet, basename="equipment-inventory")
router.register(r"uniform-orders", SportsUniformOrderViewSet, basename="sports-uniform-order")
# League
router.register(r"league-standings", LeagueStandingViewSet, basename="league-standing")
# Communication & Media
router.register(r"communications", TeamCommunicationViewSet, basename="team-communication")
router.register(r"photos", SportsPhotoGalleryViewSet, basename="sports-photo-gallery")
# Fundraising & Sponsorship
router.register(r"fundraising", SportsFundraisingViewSet, basename="sports-fundraising")
router.register(r"sponsorships", SportsSponsorshipViewSet, basename="sports-sponsorship")
# Travel & Volunteer
router.register(r"travel", SportsTravelManagementViewSet, basename="sports-travel")
router.register(r"volunteers", SportsVolunteerManagementViewSet, basename="sports-volunteer")
# Analytics
router.register(r"analytics", SportsAnalyticsViewSet, basename="sports-analytics")
# Referees
router.register(r"referees", RefereeManagementViewSet, basename="referee-management")
router.register(r"referee-assignments", RefereeAssignmentViewSet, basename="referee-assignment")
# Facility
router.register(r"facility-bookings", FacilityBookingViewSet, basename="facility-booking")
# Live Scoring
router.register(r"live-scores", LiveGameScoreViewSet, basename="live-game-score")
# Video
router.register(r"videos", VideoAnalysisViewSet, basename="video-analysis")
# Wearables
router.register(r"wearables", WearableIntegrationViewSet, basename="wearable-integration")
# Development
router.register(r"development-plans", PlayerDevelopmentPlanViewSet, basename="player-development-plan")
# Tryouts
router.register(r"tryouts", TryoutAssessmentViewSet, basename="tryout-assessment")
router.register(r"tryout-scores", TryoutScoreViewSet, basename="tryout-score")
# Memberships
router.register(r"season-passes", SeasonPassMembershipViewSet, basename="season-pass-membership")
# Scheduling
router.register(r"schedule-conflicts", MultiSportSchedulingViewSet, basename="multi-sport-scheduling")
# Refunds
router.register(r"refunds", RefundManagementViewSet, basename="refund-management")
# Compliance
router.register(r"compliance", ComplianceTrackingViewSet, basename="compliance-tracking")
# Weather
router.register(r"weather-alerts", WeatherIntegrationViewSet, basename="weather-integration")
# Live Streaming
router.register(r"live-streams", LiveStreamingViewSet, basename="live-streaming")

urlpatterns = [path("", include(router.urls))]
