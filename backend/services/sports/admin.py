from django.contrib import admin

from .models import (
    ComplianceTracking,
    EquipmentInventory,
    FacilityBooking,
    GameLineup,
    InjuryTracking,
    LeagueStanding,
    LiveGameScore,
    LiveStreaming,
    MultiSportScheduling,
    PlayerDevelopmentPlan,
    PlayerStatistics,
    PracticeSchedule,
    RefereeAssignment,
    RefereeManagement,
    RefundManagement,
    SeasonPassMembership,
    Sport,
    SportAchievement,
    SportEvent,
    SportsAnalytics,
    SportsAttendance,
    SportsFundraising,
    SportsMedicalClearance,
    SportsPhotoGallery,
    SportsRegistration,
    SportsSponsorship,
    SportsTravelManagement,
    SportsUniformOrder,
    SportsVolunteerManagement,
    Team,
    TeamCommunication,
    TeamMember,
    TeamRoster,
    TryoutAssessment,
    TryoutScore,
    VideoAnalysis,
    WearableIntegration,
    WeatherIntegration,
)


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    fields = ["student", "role", "status"]


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_active"]
    list_filter = ["category", "is_active", "school"]
    search_fields = ["name"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "sport", "gender", "coach", "is_active"]
    list_filter = ["gender", "is_active"]
    search_fields = ["name"]
    inlines = [TeamMemberInline]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["student", "team", "role", "status"]
    list_filter = ["role", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(SportEvent)
class SportEventAdmin(admin.ModelAdmin):
    list_display = ["title", "sport", "event_date", "status"]
    list_filter = ["status"]
    search_fields = ["title", "opponent"]


@admin.register(SportAchievement)
class SportAchievementAdmin(admin.ModelAdmin):
    list_display = ["title", "student", "position", "level", "awarded_date"]
    list_filter = ["level"]
    search_fields = ["title"]


@admin.register(SportsRegistration)
class SportsRegistrationAdmin(admin.ModelAdmin):
    list_display = ["student", "sport", "status", "payment_status", "registered_at"]
    list_filter = ["status", "payment_status", "registration_type"]
    search_fields = ["student__user__full_name", "sport__name"]


@admin.register(PracticeSchedule)
class PracticeScheduleAdmin(admin.ModelAdmin):
    list_display = ["team", "practice_type", "day_of_week", "start_time", "end_time", "is_active"]
    list_filter = ["practice_type", "day_of_week", "is_active"]
    search_fields = ["team__name"]


@admin.register(SportsAttendance)
class SportsAttendanceAdmin(admin.ModelAdmin):
    list_display = ["student", "team", "session_type", "status", "date"]
    list_filter = ["session_type", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(PlayerStatistics)
class PlayerStatisticsAdmin(admin.ModelAdmin):
    list_display = ["student", "team", "games_played", "goals", "assists", "points"]
    search_fields = ["student__user__full_name"]


@admin.register(TeamRoster)
class TeamRosterAdmin(admin.ModelAdmin):
    list_display = ["team", "roster_type", "season", "total_players", "is_published"]
    list_filter = ["roster_type", "is_published"]
    search_fields = ["team__name", "season"]


@admin.register(InjuryTracking)
class InjuryTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "injury_type", "severity", "status", "injury_date"]
    list_filter = ["injury_type", "severity", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(EquipmentInventory)
class EquipmentInventoryAdmin(admin.ModelAdmin):
    list_display = ["name", "equipment_type", "quantity", "condition", "is_available"]
    list_filter = ["equipment_type", "condition", "is_available"]
    search_fields = ["name"]


@admin.register(GameLineup)
class GameLineupAdmin(admin.ModelAdmin):
    list_display = ["student", "event", "lineup_type", "position", "jersey_number"]
    list_filter = ["lineup_type"]
    search_fields = ["student__user__full_name"]


@admin.register(LeagueStanding)
class LeagueStandingAdmin(admin.ModelAdmin):
    list_display = ["team", "league_name", "season", "rank", "wins", "losses", "games_played"]
    list_filter = ["league_name", "season"]
    search_fields = ["team__name"]


@admin.register(SportsMedicalClearance)
class SportsMedicalClearanceAdmin(admin.ModelAdmin):
    list_display = ["student", "clearance_type", "status", "exam_date", "expiry_date"]
    list_filter = ["clearance_type", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(TeamCommunication)
class TeamCommunicationAdmin(admin.ModelAdmin):
    list_display = ["team", "message_type", "target_audience", "is_pinned", "created_at"]
    list_filter = ["message_type", "target_audience", "is_pinned"]
    search_fields = ["subject", "content"]


@admin.register(SportsPhotoGallery)
class SportsPhotoGalleryAdmin(admin.ModelAdmin):
    list_display = ["team", "title", "photo_type", "taken_date", "is_featured"]
    list_filter = ["photo_type", "is_featured"]
    search_fields = ["title"]


@admin.register(SportsFundraising)
class SportsFundraisingAdmin(admin.ModelAdmin):
    list_display = ["team", "title", "campaign_type", "goal_amount", "raised_amount", "status"]
    list_filter = ["campaign_type", "status"]
    search_fields = ["title"]


@admin.register(SportsSponsorship)
class SportsSponsorshipAdmin(admin.ModelAdmin):
    list_display = ["sponsor_name", "team", "sponsorship_level", "amount", "status"]
    list_filter = ["sponsorship_level", "status"]
    search_fields = ["sponsor_name"]


@admin.register(SportsTravelManagement)
class SportsTravelManagementAdmin(admin.ModelAdmin):
    list_display = ["team", "event", "travel_type", "departure_date", "status"]
    list_filter = ["travel_type", "status"]
    search_fields = ["team__name"]


@admin.register(SportsUniformOrder)
class SportsUniformOrderAdmin(admin.ModelAdmin):
    list_display = ["student", "team", "uniform_type", "size", "status"]
    list_filter = ["status"]
    search_fields = ["student__user__full_name"]


@admin.register(SportsVolunteerManagement)
class SportsVolunteerManagementAdmin(admin.ModelAdmin):
    list_display = ["parent_name", "team", "volunteer_type", "status", "total_hours"]
    list_filter = ["volunteer_type", "status"]
    search_fields = ["parent_name"]


@admin.register(SportsAnalytics)
class SportsAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["team", "analytics_type", "title", "start_date", "end_date"]
    list_filter = ["analytics_type"]
    search_fields = ["title"]


@admin.register(RefereeManagement)
class RefereeManagementAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "referee_type", "certification_level", "status"]
    list_filter = ["referee_type", "certification_level", "status"]
    search_fields = ["first_name", "last_name", "email"]


@admin.register(RefereeAssignment)
class RefereeAssignmentAdmin(admin.ModelAdmin):
    list_display = ["referee", "event", "role", "status", "fee_amount"]
    list_filter = ["status"]
    search_fields = ["referee__first_name", "referee__last_name"]


@admin.register(FacilityBooking)
class FacilityBookingAdmin(admin.ModelAdmin):
    list_display = ["facility_name", "facility_type", "date", "start_time", "end_time", "status"]
    list_filter = ["facility_type", "status"]
    search_fields = ["facility_name"]


@admin.register(LiveGameScore)
class LiveGameScoreAdmin(admin.ModelAdmin):
    list_display = ["event", "home_score", "away_score", "status", "current_period"]
    list_filter = ["status"]
    search_fields = ["event__title"]


@admin.register(VideoAnalysis)
class VideoAnalysisAdmin(admin.ModelAdmin):
    list_display = ["title", "team", "video_type", "status", "created_at"]
    list_filter = ["video_type", "status"]
    search_fields = ["title"]


@admin.register(WearableIntegration)
class WearableIntegrationAdmin(admin.ModelAdmin):
    list_display = ["student", "device_type", "sync_status", "last_sync"]
    list_filter = ["device_type", "sync_status"]
    search_fields = ["student__user__full_name"]


@admin.register(PlayerDevelopmentPlan)
class PlayerDevelopmentPlanAdmin(admin.ModelAdmin):
    list_display = ["student", "title", "phase", "progress_percentage", "status"]
    list_filter = ["phase", "status"]
    search_fields = ["student__user__full_name", "title"]


@admin.register(TryoutAssessment)
class TryoutAssessmentAdmin(admin.ModelAdmin):
    list_display = ["title", "team", "tryout_date", "status", "current_participants"]
    list_filter = ["status"]
    search_fields = ["title"]


@admin.register(TryoutScore)
class TryoutScoreAdmin(admin.ModelAdmin):
    list_display = ["student", "tryout", "total_score", "selection_status"]
    list_filter = ["selection_status"]
    search_fields = ["student__user__full_name"]


@admin.register(SeasonPassMembership)
class SeasonPassMembershipAdmin(admin.ModelAdmin):
    list_display = ["student", "membership_type", "season", "final_amount", "status"]
    list_filter = ["membership_type", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(MultiSportScheduling)
class MultiSportSchedulingAdmin(admin.ModelAdmin):
    list_display = ["event_1", "event_2", "conflict_type", "status"]
    list_filter = ["conflict_type", "status"]
    search_fields = ["event_1__title", "event_2__title"]


@admin.register(RefundManagement)
class RefundManagementAdmin(admin.ModelAdmin):
    list_display = ["student", "refund_amount", "refund_reason", "status", "created_at"]
    list_filter = ["refund_reason", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(ComplianceTracking)
class ComplianceTrackingAdmin(admin.ModelAdmin):
    list_display = ["staff_member", "compliance_type", "status", "expiry_date"]
    list_filter = ["compliance_type", "status"]
    search_fields = ["staff_member__full_name"]


@admin.register(WeatherIntegration)
class WeatherIntegrationAdmin(admin.ModelAdmin):
    list_display = ["event", "weather_condition", "action_taken", "created_at"]
    list_filter = ["weather_condition", "action_taken"]
    search_fields = ["event__title"]


@admin.register(LiveStreaming)
class LiveStreamingAdmin(admin.ModelAdmin):
    list_display = ["title", "team", "status", "scheduled_start", "peak_viewers"]
    list_filter = ["status", "quality"]
    search_fields = ["title"]
