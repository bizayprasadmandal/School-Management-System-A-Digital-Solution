"""Sports & Extracurriculars serializers."""

from rest_framework import serializers

from .models import (
    EquipmentInventory,
    GameLineup,
    InjuryTracking,
    LeagueStanding,
    PlayerStatistics,
    PracticeSchedule,
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
