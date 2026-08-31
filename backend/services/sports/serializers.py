"""Sports & Extracurriculars serializers."""

from rest_framework import serializers

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


class SportSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    team_count = serializers.SerializerMethodField()

    class Meta:
        model = Sport
        fields = [
            "id",
            "name",
            "category",
            "category_display",
            "description",
            "min_players",
            "max_players",
            "is_active",
            "team_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_team_count(self, obj):
        return getattr(obj, "team_count", obj.teams.count())


class TeamMemberSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = TeamMember
        fields = ["id", "team", "student", "student_name", "role", "role_display", "status", "joined_date", "notes"]
        read_only_fields = ["id", "joined_date"]


class TeamSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source="sport.name", read_only=True)
    coach_name = serializers.CharField(source="coach.full_name", read_only=True, default=None)
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    members = TeamMemberSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "id",
            "sport",
            "sport_name",
            "name",
            "gender",
            "gender_display",
            "coach",
            "coach_name",
            "assistant_coach",
            "is_active",
            "members",
            "member_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_member_count(self, obj):
        return getattr(obj, "member_count", obj.members.filter(status="active").count())


class SportEventSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source="sport.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SportEvent
        fields = [
            "id",
            "sport",
            "sport_name",
            "team",
            "team_name",
            "title",
            "event_type",
            "opponent",
            "location",
            "event_date",
            "status",
            "status_display",
            "home_score",
            "opponent_score",
            "result",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SportAchievementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True, default=None)
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    event_title = serializers.CharField(source="event.title", read_only=True, default=None)

    class Meta:
        model = SportAchievement
        fields = [
            "id",
            "student",
            "student_name",
            "team",
            "team_name",
            "event",
            "event_title",
            "title",
            "description",
            "position",
            "level",
            "awarded_date",
            "certificate_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SportsRegistrationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    sport_name = serializers.CharField(source="sport.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    registration_type_display = serializers.CharField(source="get_registration_type_display", read_only=True)

    class Meta:
        model = SportsRegistration
        fields = [
            "id",
            "student",
            "student_name",
            "sport",
            "sport_name",
            "team",
            "team_name",
            "registration_type",
            "registration_type_display",
            "status",
            "status_display",
            "season",
            "academic_year",
            "fee_amount",
            "payment_status",
            "payment_date",
            "transaction_id",
            "medical_clearance",
            "emergency_contact",
            "emergency_phone",
            "consent_form_signed",
            "physical_exam_date",
            "physical_exam_expiry",
            "parent_name",
            "parent_email",
            "parent_phone",
            "parent_consent",
            "notes",
            "reviewed_by",
            "reviewed_at",
            "registered_at",
            "updated_at",
        ]
        read_only_fields = ["id", "registered_at", "updated_at"]


class PracticeScheduleSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    day_of_week_display = serializers.CharField(source="get_day_of_week_display", read_only=True)
    practice_type_display = serializers.CharField(source="get_practice_type_display", read_only=True)
    coach_name = serializers.CharField(source="coach.full_name", read_only=True, default=None)

    class Meta:
        model = PracticeSchedule
        fields = [
            "id",
            "team",
            "team_name",
            "practice_type",
            "practice_type_display",
            "day_of_week",
            "day_of_week_display",
            "start_time",
            "end_time",
            "location",
            "field_court",
            "is_recurring",
            "start_date",
            "end_date",
            "required",
            "min_attendance",
            "coach",
            "coach_name",
            "notes",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SportsAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    session_type_display = serializers.CharField(source="get_session_type_display", read_only=True)

    class Meta:
        model = SportsAttendance
        fields = [
            "id",
            "student",
            "student_name",
            "team",
            "team_name",
            "session_type",
            "session_type_display",
            "practice",
            "event",
            "status",
            "status_display",
            "minutes_late",
            "date",
            "reason",
            "notes",
            "recorded_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PlayerStatisticsSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True, default=None)

    class Meta:
        model = PlayerStatistics
        fields = [
            "id",
            "student",
            "student_name",
            "team",
            "team_name",
            "event",
            "event_title",
            "games_played",
            "games_started",
            "minutes_played",
            "stats",
            "goals",
            "assists",
            "points",
            "rebounds",
            "steals",
            "blocks",
            "turnovers",
            "fouls",
            "rating",
            "notes",
            "season",
            "academic_year",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamRosterSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    roster_type_display = serializers.CharField(source="get_roster_type_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = TeamRoster
        fields = [
            "id",
            "team",
            "team_name",
            "roster_type",
            "roster_type_display",
            "season",
            "academic_year",
            "roster_data",
            "total_players",
            "is_published",
            "published_at",
            "max_roster_size",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "published_at", "created_at", "updated_at"]


class InjuryTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    injury_type_display = serializers.CharField(source="get_injury_type_display", read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    cleared_by_name = serializers.CharField(source="cleared_by.full_name", read_only=True, default=None)

    class Meta:
        model = InjuryTracking
        fields = [
            "id",
            "student",
            "student_name",
            "team",
            "team_name",
            "injury_type",
            "injury_type_display",
            "severity",
            "severity_display",
            "body_part",
            "description",
            "injury_date",
            "reported_date",
            "expected_return",
            "actual_return",
            "status",
            "status_display",
            "treatment_notes",
            "doctor_name",
            "doctor_contact",
            "activity_restriction",
            "return_to_play_protocol",
            "cleared_by",
            "cleared_by_name",
            "cleared_date",
            "medical_report_url",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EquipmentInventorySerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    equipment_type_display = serializers.CharField(source="get_equipment_type_display", read_only=True)
    condition_display = serializers.CharField(source="get_condition_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.user.full_name", read_only=True, default=None)

    class Meta:
        model = EquipmentInventory
        fields = [
            "id",
            "team",
            "team_name",
            "name",
            "equipment_type",
            "equipment_type_display",
            "description",
            "quantity",
            "condition",
            "condition_display",
            "purchase_date",
            "purchase_price",
            "vendor",
            "last_maintenance",
            "next_maintenance",
            "maintenance_notes",
            "storage_location",
            "is_available",
            "assigned_to",
            "assigned_to_name",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GameLineupSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)
    lineup_type_display = serializers.CharField(source="get_lineup_type_display", read_only=True)

    class Meta:
        model = GameLineup
        fields = [
            "id",
            "event",
            "event_title",
            "student",
            "student_name",
            "lineup_type",
            "lineup_type_display",
            "position",
            "jersey_number",
            "subbed_in_at",
            "subbed_out_at",
            "substitution_reason",
            "minutes_played",
            "stats_snapshot",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LeagueStandingSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    sport_name = serializers.CharField(source="sport.name", read_only=True)
    win_percentage = serializers.ReadOnlyField()
    point_differential = serializers.ReadOnlyField()

    class Meta:
        model = LeagueStanding
        fields = [
            "id",
            "sport",
            "sport_name",
            "league_name",
            "season",
            "division",
            "team",
            "team_name",
            "games_played",
            "wins",
            "losses",
            "ties",
            "points_for",
            "points_against",
            "rank",
            "streak",
            "last_5",
            "win_percentage",
            "point_differential",
            "notes",
            "updated_at",
            "created_at",
        ]
        read_only_fields = ["id", "updated_at", "created_at"]


class SportsMedicalClearanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    clearance_type_display = serializers.CharField(source="get_clearance_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = SportsMedicalClearance
        fields = [
            "id",
            "student",
            "student_name",
            "clearance_type",
            "clearance_type_display",
            "status",
            "status_display",
            "physician_name",
            "physician_contact",
            "exam_date",
            "expiry_date",
            "document_url",
            "restrictions",
            "cleared_for",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "is_valid",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamCommunicationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    message_type_display = serializers.CharField(source="get_message_type_display", read_only=True)
    target_audience_display = serializers.CharField(source="get_target_audience_display", read_only=True)
    sent_by_name = serializers.CharField(source="sent_by.full_name", read_only=True, default=None)

    class Meta:
        model = TeamCommunication
        fields = [
            "id",
            "team",
            "team_name",
            "message_type",
            "message_type_display",
            "target_audience",
            "target_audience_display",
            "subject",
            "content",
            "sent_by",
            "sent_by_name",
            "attachment_url",
            "is_pinned",
            "is_read",
            "read_by",
            "send_immediately",
            "scheduled_at",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "created_at"]


class SportsPhotoGallerySerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    photo_type_display = serializers.CharField(source="get_photo_type_display", read_only=True)
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True, default=None)

    class Meta:
        model = SportsPhotoGallery
        fields = [
            "id",
            "team",
            "team_name",
            "photo_type",
            "photo_type_display",
            "title",
            "description",
            "photo_url",
            "thumbnail_url",
            "photographer",
            "event",
            "taken_date",
            "tags",
            "likes_count",
            "comments_count",
            "is_featured",
            "is_public",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "likes_count", "comments_count", "created_at"]


class SportsFundraisingSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    campaign_type_display = serializers.CharField(source="get_campaign_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = SportsFundraising
        fields = [
            "id",
            "team",
            "team_name",
            "campaign_type",
            "campaign_type_display",
            "status",
            "status_display",
            "title",
            "description",
            "goal_amount",
            "raised_amount",
            "progress_percentage",
            "start_date",
            "end_date",
            "donor_count",
            "average_donation",
            "is_online",
            "online_donation_url",
            "created_by",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SportsSponsorshipSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    sponsorship_level_display = serializers.CharField(source="get_sponsorship_level_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    total_value = serializers.ReadOnlyField()

    class Meta:
        model = SportsSponsorship
        fields = [
            "id",
            "team",
            "team_name",
            "sponsor_name",
            "contact_name",
            "contact_email",
            "contact_phone",
            "website",
            "sponsorship_level",
            "sponsorship_level_display",
            "amount",
            "in_kind_value",
            "total_value",
            "start_date",
            "end_date",
            "is_recurring",
            "logo_on_jersey",
            "banner_at_field",
            "mention_in_programs",
            "social_media_recognition",
            "other_benefits",
            "status",
            "status_display",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SportsTravelManagementSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)
    travel_type_display = serializers.CharField(source="get_travel_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SportsTravelManagement
        fields = [
            "id",
            "team",
            "team_name",
            "event",
            "event_title",
            "travel_type",
            "travel_type_display",
            "status",
            "status_display",
            "departure_date",
            "return_date",
            "vehicle_info",
            "driver_name",
            "driver_contact",
            "hotel_name",
            "hotel_address",
            "hotel_confirmation",
            "meal_plan",
            "estimated_cost",
            "actual_cost",
            "travelers",
            "itinerary_url",
            "emergency_contact",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SportsUniformOrderSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SportsUniformOrder
        fields = [
            "id",
            "team",
            "team_name",
            "student",
            "student_name",
            "uniform_type",
            "size",
            "jersey_number",
            "status",
            "status_display",
            "quantity",
            "cost",
            "payment_status",
            "ordered_date",
            "expected_delivery",
            "delivered_date",
            "vendor",
            "order_number",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SportsVolunteerManagementSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True, default=None)
    volunteer_type_display = serializers.CharField(source="get_volunteer_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SportsVolunteerManagement
        fields = [
            "id",
            "team",
            "team_name",
            "parent_name",
            "parent_email",
            "parent_phone",
            "student",
            "student_name",
            "volunteer_type",
            "volunteer_type_display",
            "status",
            "status_display",
            "availability",
            "background_check_complete",
            "background_check_date",
            "total_hours",
            "skills",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_hours", "created_at", "updated_at"]


class SportsAnalyticsSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    analytics_type_display = serializers.CharField(source="get_analytics_type_display", read_only=True)
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = SportsAnalytics
        fields = [
            "id",
            "team",
            "team_name",
            "analytics_type",
            "analytics_type_display",
            "title",
            "start_date",
            "end_date",
            "analytics_data",
            "insights",
            "recommendations",
            "chart_type",
            "chart_data",
            "key_metrics",
            "is_shared",
            "generated_by",
            "generated_by_name",
            "generated_at",
            "updated_at",
        ]
        read_only_fields = ["id", "generated_at", "updated_at"]


class RefereeManagementSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    referee_type_display = serializers.CharField(source="get_referee_type_display", read_only=True)
    certification_level_display = serializers.CharField(source="get_certification_level_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = RefereeManagement
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "referee_type",
            "referee_type_display",
            "certification_level",
            "certification_level_display",
            "certification_number",
            "certification_expiry",
            "availability",
            "games_officiated",
            "average_rating",
            "status",
            "status_display",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "games_officiated", "average_rating", "created_at", "updated_at"]


class RefereeAssignmentSerializer(serializers.ModelSerializer):
    referee_name = serializers.CharField(source="referee.full_name", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = RefereeAssignment
        fields = [
            "id",
            "referee",
            "referee_name",
            "event",
            "event_title",
            "role",
            "status",
            "status_display",
            "fee_amount",
            "payment_status",
            "rating",
            "comments",
            "notes",
            "assigned_at",
        ]
        read_only_fields = ["id", "assigned_at"]


class FacilityBookingSerializer(serializers.ModelSerializer):
    booked_by_name = serializers.CharField(source="booked_by.full_name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    event_title = serializers.CharField(source="event.title", read_only=True, default=None)
    facility_type_display = serializers.CharField(source="get_facility_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    duration_hours = serializers.ReadOnlyField()

    class Meta:
        model = FacilityBooking
        fields = [
            "id",
            "facility_name",
            "facility_type",
            "facility_type_display",
            "location",
            "booked_by",
            "booked_by_name",
            "team",
            "team_name",
            "event",
            "event_title",
            "date",
            "start_time",
            "end_time",
            "is_recurring",
            "recurrence_pattern",
            "status",
            "status_display",
            "rental_cost",
            "payment_status",
            "equipment_needed",
            "duration_hours",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LiveGameScoreSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    score_diff = serializers.ReadOnlyField()
    updated_by_name = serializers.CharField(source="updated_by.full_name", read_only=True, default=None)

    class Meta:
        model = LiveGameScore
        fields = [
            "id",
            "event",
            "event_title",
            "home_score",
            "away_score",
            "current_period",
            "period_time",
            "status",
            "status_display",
            "possession",
            "shots_on_target",
            "score_diff",
            "last_updated",
            "updated_by",
            "updated_by_name",
            "commentary",
            "is_public",
            "auto_update",
            "created_at",
        ]
        read_only_fields = ["id", "last_updated", "created_at"]


class VideoAnalysisSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True, default=None)
    video_type_display = serializers.CharField(source="get_video_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    duration_formatted = serializers.ReadOnlyField()
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True, default=None)

    class Meta:
        model = VideoAnalysis
        fields = [
            "id",
            "team",
            "team_name",
            "event",
            "event_title",
            "title",
            "description",
            "video_type",
            "video_type_display",
            "video_url",
            "thumbnail_url",
            "duration_seconds",
            "duration_formatted",
            "file_size_mb",
            "status",
            "status_display",
            "analysis_notes",
            "key_moments",
            "tags",
            "is_public",
            "shared_with",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WearableIntegrationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    device_type_display = serializers.CharField(source="get_device_type_display", read_only=True)
    sync_status_display = serializers.CharField(source="get_sync_status_display", read_only=True)

    class Meta:
        model = WearableIntegration
        fields = [
            "id",
            "student",
            "student_name",
            "team",
            "team_name",
            "device_type",
            "device_type_display",
            "device_id",
            "sync_status",
            "sync_status_display",
            "last_sync",
            "heart_rate_data",
            "gps_data",
            "activity_data",
            "sleep_data",
            "auto_sync",
            "share_with_coach",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_sync", "created_at", "updated_at"]


class PlayerDevelopmentPlanSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    phase_display = serializers.CharField(source="get_phase_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = PlayerDevelopmentPlan
        fields = [
            "id",
            "student",
            "student_name",
            "team",
            "team_name",
            "title",
            "description",
            "phase",
            "phase_display",
            "short_term_goals",
            "long_term_goals",
            "baseline_metrics",
            "current_metrics",
            "target_metrics",
            "progress_percentage",
            "status",
            "status_display",
            "start_date",
            "target_date",
            "review_date",
            "created_by",
            "created_by_name",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TryoutAssessmentSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source="sport.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = TryoutAssessment
        fields = [
            "id",
            "sport",
            "sport_name",
            "team",
            "team_name",
            "title",
            "description",
            "tryout_date",
            "location",
            "status",
            "status_display",
            "max_score",
            "passing_score",
            "max_participants",
            "current_participants",
            "created_by",
            "created_by_name",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TryoutScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    tryout_title = serializers.CharField(source="tryout.title", read_only=True)
    selection_status_display = serializers.CharField(source="get_selection_status_display", read_only=True)
    evaluated_by_name = serializers.CharField(source="evaluated_by.full_name", read_only=True, default=None)

    class Meta:
        model = TryoutScore
        fields = [
            "id",
            "tryout",
            "tryout_title",
            "student",
            "student_name",
            "total_score",
            "category_scores",
            "selection_status",
            "selection_status_display",
            "evaluator_notes",
            "strengths",
            "areas_for_improvement",
            "evaluated_by",
            "evaluated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SeasonPassMembershipSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    membership_type_display = serializers.CharField(source="get_membership_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = SeasonPassMembership
        fields = [
            "id",
            "student",
            "student_name",
            "membership_type",
            "membership_type_display",
            "season",
            "academic_year",
            "amount",
            "discount_amount",
            "final_amount",
            "start_date",
            "end_date",
            "auto_renew",
            "renewal_date",
            "payment_status",
            "transaction_id",
            "benefits",
            "status",
            "status_display",
            "is_valid",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MultiSportSchedulingSerializer(serializers.ModelSerializer):
    event_1_title = serializers.CharField(source="event_1.title", read_only=True)
    event_2_title = serializers.CharField(source="event_2.title", read_only=True)
    conflict_type_display = serializers.CharField(source="get_conflict_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    resolved_by_name = serializers.CharField(source="resolved_by.full_name", read_only=True, default=None)

    class Meta:
        model = MultiSportScheduling
        fields = [
            "id",
            "event_1",
            "event_1_title",
            "event_2",
            "event_2_title",
            "conflict_type",
            "conflict_type_display",
            "description",
            "status",
            "status_display",
            "resolution_notes",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "resolved_at", "created_at"]


class RefundManagementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    requested_by_name = serializers.CharField(source="requested_by.full_name", read_only=True)
    refund_reason_display = serializers.CharField(source="get_refund_reason_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)
    refund_percentage = serializers.ReadOnlyField()

    class Meta:
        model = RefundManagement
        fields = [
            "id",
            "requested_by",
            "requested_by_name",
            "student",
            "student_name",
            "registration",
            "original_amount",
            "refund_amount",
            "refund_percentage",
            "refund_reason",
            "refund_reason_display",
            "reason_details",
            "status",
            "status_display",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "approval_notes",
            "processed_at",
            "transaction_id",
            "within_policy",
            "policy_exception",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewed_at", "processed_at", "created_at", "updated_at"]


class ComplianceTrackingSerializer(serializers.ModelSerializer):
    staff_member_name = serializers.CharField(source="staff_member.full_name", read_only=True)
    compliance_type_display = serializers.CharField(source="get_compliance_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    verified_by_name = serializers.CharField(source="verified_by.full_name", read_only=True, default=None)
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = ComplianceTracking
        fields = [
            "id",
            "staff_member",
            "staff_member_name",
            "compliance_type",
            "compliance_type_display",
            "status",
            "status_display",
            "certification_number",
            "issuing_organization",
            "issue_date",
            "expiry_date",
            "document_url",
            "reminder_sent",
            "last_reminder",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "is_valid",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "verified_at", "created_at", "updated_at"]


class WeatherIntegrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    weather_condition_display = serializers.CharField(source="get_weather_condition_display", read_only=True)
    action_taken_display = serializers.CharField(source="get_action_taken_display", read_only=True)
    decided_by_name = serializers.CharField(source="decided_by.full_name", read_only=True, default=None)

    class Meta:
        model = WeatherIntegration
        fields = [
            "id",
            "event",
            "event_title",
            "weather_condition",
            "weather_condition_display",
            "temperature",
            "humidity",
            "wind_speed",
            "precipitation_mm",
            "action_taken",
            "action_taken_display",
            "action_reason",
            "notified_coaches",
            "notified_players",
            "notified_parents",
            "decided_by",
            "decided_by_name",
            "decided_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "decided_at", "created_at"]


class LiveStreamingSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    quality_display = serializers.CharField(source="get_quality_display", read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = LiveStreaming
        fields = [
            "id",
            "event",
            "event_title",
            "team",
            "team_name",
            "title",
            "description",
            "stream_url",
            "embed_code",
            "status",
            "status_display",
            "quality",
            "quality_display",
            "scheduled_start",
            "actual_start",
            "actual_end",
            "duration_minutes",
            "peak_viewers",
            "total_views",
            "recording_url",
            "is_recorded",
            "is_public",
            "requires_login",
            "password",
            "allow_chat",
            "show_scoreboard",
            "created_by",
            "created_by_name",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "actual_start", "actual_end", "created_at", "updated_at"]
