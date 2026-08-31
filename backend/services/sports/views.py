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
    BadgeAward,
    ComplianceTracking,
    EligibilityRule,
    EquipmentInventory,
    FacilityBooking,
    GameLineup,
    InjuryTracking,
    InsuranceTracking,
    LeagueStanding,
    LiveGameScore,
    LiveStreaming,
    MerchandiseOrder,
    MerchandiseStore,
    MultiSportScheduling,
    PlayerDevelopmentPlan,
    PlayerStatistics,
    PlayerTransferSystem,
    PracticeSchedule,
    RefereeAssignment,
    RefereeManagement,
    RefundManagement,
    SeasonArchive,
    SeasonPassMembership,
    Sport,
    SportAchievement,
    SportEvent,
    SportsAnalytics,
    SportsAttendance,
    SportsFundraising,
    SportsGamification,
    SportsLeaderboard,
    SportsMedicalClearance,
    SportsPhotoGallery,
    SportsRegistration,
    SportsSponsorship,
    SportsTravelManagement,
    SportsUniformOrder,
    SportsVolunteerManagement,
    StudentEligibility,
    SuspensionManagement,
    Team,
    TeamCommunication,
    TeamMember,
    TeamRoster,
    TournamentBracket,
    TournamentMatch,
    TryoutAssessment,
    TryoutScore,
    VideoAnalysis,
    WearableIntegration,
    WeatherIntegration,
)
from .serializers import (
    BadgeAwardSerializer,
    ComplianceTrackingSerializer,
    EligibilityRuleSerializer,
    EquipmentInventorySerializer,
    FacilityBookingSerializer,
    GameLineupSerializer,
    InjuryTrackingSerializer,
    InsuranceTrackingSerializer,
    LeagueStandingSerializer,
    LiveGameScoreSerializer,
    LiveStreamingSerializer,
    MerchandiseOrderSerializer,
    MerchandiseStoreSerializer,
    MultiSportSchedulingSerializer,
    PlayerDevelopmentPlanSerializer,
    PlayerStatisticsSerializer,
    PlayerTransferSystemSerializer,
    PracticeScheduleSerializer,
    RefereeAssignmentSerializer,
    RefereeManagementSerializer,
    RefundManagementSerializer,
    SeasonArchiveSerializer,
    SeasonPassMembershipSerializer,
    SportAchievementSerializer,
    SportEventSerializer,
    SportsAnalyticsSerializer,
    SportsAttendanceSerializer,
    SportSerializer,
    SportsFundraisingSerializer,
    SportsGamificationSerializer,
    SportsLeaderboardSerializer,
    SportsMedicalClearanceSerializer,
    SportsPhotoGallerySerializer,
    SportsRegistrationSerializer,
    SportsSponsorshipSerializer,
    SportsTravelManagementSerializer,
    SportsUniformOrderSerializer,
    SportsVolunteerManagementSerializer,
    StudentEligibilitySerializer,
    SuspensionManagementSerializer,
    TeamCommunicationSerializer,
    TeamMemberSerializer,
    TeamRosterSerializer,
    TeamSerializer,
    TournamentBracketSerializer,
    TournamentMatchSerializer,
    TryoutAssessmentSerializer,
    TryoutScoreSerializer,
    VideoAnalysisSerializer,
    WearableIntegrationSerializer,
    WeatherIntegrationSerializer,
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


class RefereeManagementViewSet(viewsets.ModelViewSet):
    serializer_class = RefereeManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["first_name", "last_name", "email"]
    filterset_fields = ["referee_type", "certification_level", "status"]

    def get_queryset(self):
        return RefereeManagement.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RefereeAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = RefereeAssignmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["referee", "event", "status"]

    def get_queryset(self):
        return RefereeAssignment.objects.filter(referee__school=self.request.user.school).select_related(
            "referee", "event"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class FacilityBookingViewSet(viewsets.ModelViewSet):
    serializer_class = FacilityBookingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["facility_name", "location"]
    filterset_fields = ["facility_type", "status", "date"]

    def get_queryset(self):
        return FacilityBooking.objects.filter(school=self.request.user.school).select_related(
            "booked_by", "team", "event"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, booked_by=self.request.user)


class LiveGameScoreViewSet(viewsets.ModelViewSet):
    serializer_class = LiveGameScoreSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        return LiveGameScore.objects.filter(event__school=self.request.user.school).select_related(
            "event", "updated_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)


class VideoAnalysisViewSet(viewsets.ModelViewSet):
    serializer_class = VideoAnalysisSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title"]
    filterset_fields = ["team", "video_type", "status"]

    def get_queryset(self):
        return VideoAnalysis.objects.filter(school=self.request.user.school).select_related(
            "team", "event", "uploaded_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, uploaded_by=self.request.user)


class WearableIntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = WearableIntegrationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "team", "device_type", "sync_status"]

    def get_queryset(self):
        return WearableIntegration.objects.filter(team__school=self.request.user.school).select_related(
            "student__user", "team"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class PlayerDevelopmentPlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerDevelopmentPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title"]
    filterset_fields = ["student", "team", "phase", "status"]

    def get_queryset(self):
        return PlayerDevelopmentPlan.objects.filter(team__school=self.request.user.school).select_related(
            "student__user", "team", "created_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TryoutAssessmentViewSet(viewsets.ModelViewSet):
    serializer_class = TryoutAssessmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title"]
    filterset_fields = ["sport", "team", "status"]

    def get_queryset(self):
        return TryoutAssessment.objects.filter(school=self.request.user.school).select_related(
            "sport", "team", "created_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class TryoutScoreViewSet(viewsets.ModelViewSet):
    serializer_class = TryoutScoreSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tryout", "student", "selection_status"]

    def get_queryset(self):
        return TryoutScore.objects.filter(tryout__school=self.request.user.school).select_related(
            "tryout", "student__user", "evaluated_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(evaluated_by=self.request.user)


class SeasonPassMembershipViewSet(viewsets.ModelViewSet):
    serializer_class = SeasonPassMembershipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "membership_type", "status"]

    def get_queryset(self):
        return SeasonPassMembership.objects.filter(school=self.request.user.school).select_related("student__user")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MultiSportSchedulingViewSet(viewsets.ModelViewSet):
    serializer_class = MultiSportSchedulingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["conflict_type", "status"]

    def get_queryset(self):
        return MultiSportScheduling.objects.filter(school=self.request.user.school).select_related(
            "event_1", "event_2", "resolved_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RefundManagementViewSet(viewsets.ModelViewSet):
    serializer_class = RefundManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "refund_reason", "status"]

    def get_queryset(self):
        return RefundManagement.objects.filter(school=self.request.user.school).select_related(
            "requested_by", "student__user", "registration", "reviewed_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, requested_by=self.request.user)


class ComplianceTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = ComplianceTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["staff_member", "compliance_type", "status"]

    def get_queryset(self):
        return ComplianceTracking.objects.filter(school=self.request.user.school).select_related(
            "staff_member", "verified_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class WeatherIntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = WeatherIntegrationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["weather_condition", "action_taken"]

    def get_queryset(self):
        return WeatherIntegration.objects.filter(school=self.request.user.school).select_related("event", "decided_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class LiveStreamingViewSet(viewsets.ModelViewSet):
    serializer_class = LiveStreamingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["team", "status", "quality"]

    def get_queryset(self):
        return LiveStreaming.objects.filter(school=self.request.user.school).select_related(
            "event", "team", "created_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class SuspensionManagementViewSet(viewsets.ModelViewSet):
    serializer_class = SuspensionManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "staff_member", "team", "suspension_type", "status"]

    def get_queryset(self):
        return SuspensionManagement.objects.filter(school=self.request.user.school).select_related(
            "student__user", "staff_member", "team", "issued_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, issued_by=self.request.user)


class TournamentBracketViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentBracketSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sport", "bracket_type", "status"]

    def get_queryset(self):
        return TournamentBracket.objects.filter(school=self.request.user.school).select_related("sport", "created_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class TournamentMatchViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentMatchSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["bracket", "team_1", "team_2", "status"]

    def get_queryset(self):
        return TournamentMatch.objects.filter(bracket__school=self.request.user.school).select_related(
            "bracket", "team_1", "team_2", "winner"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class MerchandiseStoreViewSet(viewsets.ModelViewSet):
    serializer_class = MerchandiseStoreSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["team", "product_type", "status"]

    def get_queryset(self):
        return MerchandiseStore.objects.filter(school=self.request.user.school).select_related("team")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MerchandiseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = MerchandiseOrderSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product", "student", "status", "payment_status"]

    def get_queryset(self):
        return MerchandiseOrder.objects.filter(school=self.request.user.school).select_related(
            "product", "student__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InsuranceTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = InsuranceTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "insurance_type", "status"]

    def get_queryset(self):
        return InsuranceTracking.objects.filter(school=self.request.user.school).select_related(
            "student__user", "verified_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class EligibilityRuleViewSet(viewsets.ModelViewSet):
    serializer_class = EligibilityRuleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sport", "rule_type", "status"]

    def get_queryset(self):
        return EligibilityRule.objects.filter(school=self.request.user.school).select_related("sport")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class StudentEligibilityViewSet(viewsets.ModelViewSet):
    serializer_class = StudentEligibilitySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "sport", "status"]

    def get_queryset(self):
        return StudentEligibility.objects.filter(school=self.request.user.school).select_related(
            "student__user", "sport", "reviewed_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PlayerTransferSystemViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerTransferSystemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "transfer_type", "status"]

    def get_queryset(self):
        return PlayerTransferSystem.objects.filter(school=self.request.user.school).select_related(
            "student__user", "from_team", "to_team", "approved_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SeasonArchiveViewSet(viewsets.ModelViewSet):
    serializer_class = SeasonArchiveSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["team", "season"]

    def get_queryset(self):
        return SeasonArchive.objects.filter(school=self.request.user.school).select_related("team")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SportsGamificationViewSet(viewsets.ModelViewSet):
    serializer_class = SportsGamificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["badge_type", "is_active"]

    def get_queryset(self):
        return SportsGamification.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BadgeAwardViewSet(viewsets.ModelViewSet):
    serializer_class = BadgeAwardSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["badge", "student", "team"]

    def get_queryset(self):
        return BadgeAward.objects.filter(badge__school=self.request.user.school).select_related(
            "badge", "student__user", "team", "awarded_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(awarded_by=self.request.user)


class SportsLeaderboardViewSet(viewsets.ModelViewSet):
    serializer_class = SportsLeaderboardSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sport", "leaderboard_type", "is_active"]

    def get_queryset(self):
        return SportsLeaderboard.objects.filter(school=self.request.user.school).select_related("sport")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
