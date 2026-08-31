from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EquipmentInventoryViewSet,
    GameLineupViewSet,
    InjuryTrackingViewSet,
    LeagueStandingViewSet,
    PlayerStatisticsViewSet,
    PracticeScheduleViewSet,
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

urlpatterns = [path("", include(router.urls))]
