"""Sports & Extracurriculars — Viewsets with school-scoped CRUD."""

import logging

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
from .serializers import (
    EquipmentInventorySerializer,
    GameLineupSerializer,
    InjuryTrackingSerializer,
    LeagueStandingSerializer,
    PlayerStatisticsSerializer,
    PracticeScheduleSerializer,
    SportAchievementSerializer,
    SportEventSerializer,
    SportsAnalyticsSerializer,
    SportsAttendanceSerializer,
    SportSerializer,
    SportsFundraisingSerializer,
    SportsMedicalClearanceSerializer,
    SportsPhotoGallerySerializer,
    SportsRegistrationSerializer,
    SportsSponsorshipSerializer,
    SportsTravelManagementSerializer,
    SportsUniformOrderSerializer,
    SportsVolunteerManagementSerializer,
    TeamCommunicationSerializer,
    TeamMemberSerializer,
    TeamRosterSerializer,
    TeamSerializer,
)

logger = logging.getLogger(__name__)


class SportViewSet(viewsets.ModelViewSet):
    serializer_class = SportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description"]
    filterset_fields = ["category", "is_active"]

    def get_queryset(self):
        return Sport.objects.filter(school=self.request.user.school).annotate(team_count=Count("teams"))

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["sport", "is_active", "gender"]

    def get_queryset(self):
        return (
            Team.objects.filter(school=self.request.user.school)
            .select_related("sport", "coach")
            .prefetch_related("members__student__user")
            .annotate(member_count=Count("members", filter=Q(members__status="active")))
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TeamMemberViewSet(viewsets.ModelViewSet):
    serializer_class = TeamMemberSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["team", "status", "role"]

    def get_queryset(self):
        return TeamMember.objects.filter(team__school=self.request.user.school).select_related("student__user", "team")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        team = serializer.validated_data.get("team")
        student = serializer.validated_data.get("student")
        school = self.request.user.school
        if team is not None and team.school_id != school.id:
            raise PermissionDenied("Team not found in your school.")
        if student is not None and student.school_id != school.id:
            raise PermissionDenied("Student not found in your school.")
        serializer.save()


class SportEventViewSet(viewsets.ModelViewSet):
    serializer_class = SportEventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "opponent", "location"]
    filterset_fields = ["sport", "team", "status"]

    def get_queryset(self):
        return SportEvent.objects.filter(school=self.request.user.school).select_related("sport", "team")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SportAchievementViewSet(viewsets.ModelViewSet):
    serializer_class = SportAchievementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "position", "level"]
    filterset_fields = ["student", "team", "level"]

    def get_queryset(self):
        return SportAchievement.objects.filter(school=self.request.user.school).select_related(
            "student__user", "team", "event"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SportsRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = SportsRegistrationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "sport__name"]
    filterset_fields = ["sport", "team", "status", "payment_status"]

    def get_queryset(self):
        return SportsRegistration.objects.filter(school=self.request.user.school).select_related(
            "student__user", "sport", "team", "reviewed_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def approve(self, request, pk=None):
        """Approve a registration."""
        registration = self.get_object()
        registration.status = SportsRegistration.Status.APPROVED
        registration.reviewed_by = request.user
        from django.utils import timezone

        registration.reviewed_at = timezone.now()
        registration.save()
        return Response({"status": "approved"})


class PracticeScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = PracticeScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["location", "field_court"]
    filterset_fields = ["team", "practice_type", "day_of_week", "is_active"]

    def get_queryset(self):
        return PracticeSchedule.objects.filter(school=self.request.user.school).select_related("team", "coach")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SportsAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = SportsAttendanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name"]
    filterset_fields = ["team", "session_type", "status", "date"]

    def get_queryset(self):
        return SportsAttendance.objects.filter(team__school=self.request.user.school).select_related(
            "student__user", "team"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class PlayerStatisticsViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerStatisticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name"]
    filterset_fields = ["team", "event", "season"]

    def get_queryset(self):
        return PlayerStatistics.objects.filter(team__school=self.request.user.school).select_related(
            "student__user", "team", "event"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class TeamRosterViewSet(viewsets.ModelViewSet):
    serializer_class = TeamRosterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["team", "roster_type", "is_published"]

    def get_queryset(self):
        return TeamRoster.objects.filter(team__school=self.request.user.school).select_related("team", "created_by")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class InjuryTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = InjuryTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name"]
    filterset_fields = ["team", "injury_type", "severity", "status"]

    def get_queryset(self):
        return InjuryTracking.objects.filter(school=self.request.user.school).select_related(
            "student__user", "team", "cleared_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class EquipmentInventoryViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentInventorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["team", "equipment_type", "condition", "is_available"]

    def get_queryset(self):
        return EquipmentInventory.objects.filter(school=self.request.user.school).select_related(
            "team", "assigned_to__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class GameLineupViewSet(viewsets.ModelViewSet):
    serializer_class = GameLineupSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["event", "lineup_type"]

    def get_queryset(self):
        return GameLineup.objects.filter(event__school=self.request.user.school).select_related(
            "student__user", "event"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class LeagueStandingViewSet(viewsets.ModelViewSet):
    serializer_class = LeagueStandingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["league_name", "division"]
    filterset_fields = ["sport", "season"]

    def get_queryset(self):
        return LeagueStanding.objects.filter(school=self.request.user.school).select_related("sport", "team")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SportsMedicalClearanceViewSet(viewsets.ModelViewSet):
    serializer_class = SportsMedicalClearanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "clearance_type", "status"]

    def get_queryset(self):
        return SportsMedicalClearance.objects.filter(school=self.request.user.school).select_related(
            "student__user", "reviewed_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TeamCommunicationViewSet(viewsets.ModelViewSet):
    serializer_class = TeamCommunicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["subject", "content"]
    filterset_fields = ["team", "message_type", "target_audience", "is_pinned"]

    def get_queryset(self):
        return TeamCommunication.objects.filter(team__school=self.request.user.school).select_related("team", "sent_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(sent_by=self.request.user)


class SportsPhotoGalleryViewSet(viewsets.ModelViewSet):
    serializer_class = SportsPhotoGallerySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "photographer"]
    filterset_fields = ["team", "photo_type", "is_featured", "is_public"]

    def get_queryset(self):
        return SportsPhotoGallery.objects.filter(team__school=self.request.user.school).select_related(
            "team", "uploaded_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class SportsFundraisingViewSet(viewsets.ModelViewSet):
    serializer_class = SportsFundraisingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["team", "campaign_type", "status"]

    def get_queryset(self):
        return SportsFundraising.objects.filter(team__school=self.request.user.school).select_related(
            "team", "created_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SportsSponsorshipViewSet(viewsets.ModelViewSet):
    serializer_class = SportsSponsorshipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["sponsor_name", "contact_name"]
    filterset_fields = ["team", "sponsorship_level", "status"]

    def get_queryset(self):
        return SportsSponsorship.objects.filter(team__school=self.request.user.school).select_related("team")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save()


class SportsTravelManagementViewSet(viewsets.ModelViewSet):
    serializer_class = SportsTravelManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["team", "travel_type", "status"]

    def get_queryset(self):
        return SportsTravelManagement.objects.filter(team__school=self.request.user.school).select_related(
            "team", "event"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class SportsUniformOrderViewSet(viewsets.ModelViewSet):
    serializer_class = SportsUniformOrderSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "uniform_type"]
    filterset_fields = ["team", "status", "payment_status"]

    def get_queryset(self):
        return SportsUniformOrder.objects.filter(team__school=self.request.user.school).select_related(
            "student__user", "team"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class SportsVolunteerManagementViewSet(viewsets.ModelViewSet):
    serializer_class = SportsVolunteerManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["parent_name"]
    filterset_fields = ["team", "volunteer_type", "status"]

    def get_queryset(self):
        return SportsVolunteerManagement.objects.filter(team__school=self.request.user.school).select_related(
            "team", "student__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class SportsAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = SportsAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title"]
    filterset_fields = ["team", "analytics_type", "is_shared"]

    def get_queryset(self):
        return SportsAnalytics.objects.filter(team__school=self.request.user.school).select_related(
            "team", "generated_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)
