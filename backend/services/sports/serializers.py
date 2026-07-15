"""Sports & Extracurriculars serializers."""

from rest_framework import serializers
from .models import Sport, Team, TeamMember, SportEvent, SportAchievement


class SportSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    team_count = serializers.SerializerMethodField()

    class Meta:
        model = Sport
        fields = ["id", "name", "category", "category_display", "description", "min_players", "max_players", "is_active", "team_count", "created_at"]
        read_only_fields = ["id", "created_at"]
    def get_team_count(self, obj): return obj.teams.count()


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
        fields = ["id", "sport", "sport_name", "name", "gender", "gender_display", "coach", "coach_name", "assistant_coach", "is_active", "members", "member_count", "created_at"]
        read_only_fields = ["id", "created_at"]
    def get_member_count(self, obj): return obj.members.filter(status="active").count()


class SportEventSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source="sport.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SportEvent
        fields = ["id", "sport", "sport_name", "team", "team_name", "title", "event_type", "opponent", "location", "event_date", "status", "status_display", "home_score", "opponent_score", "result", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class SportAchievementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True, default=None)
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    event_title = serializers.CharField(source="event.title", read_only=True, default=None)

    class Meta:
        model = SportAchievement
        fields = ["id", "student", "student_name", "team", "team_name", "event", "event_title", "title", "description", "position", "level", "awarded_date", "certificate_url", "created_at"]
        read_only_fields = ["id", "created_at"]
