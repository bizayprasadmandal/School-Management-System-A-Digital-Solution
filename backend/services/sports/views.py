"""Sports & Extracurriculars — Viewsets with school-scoped CRUD."""

import logging

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Sport, SportAchievement, SportEvent, Team, TeamMember
from .serializers import (
    SportAchievementSerializer,
    SportEventSerializer,
    SportSerializer,
    TeamMemberSerializer,
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
        return Sport.objects.filter(school=self.request.user.school)

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
        # TeamMember has no school FK (derived via team), so validate that the
        # referenced team AND student belong to the caller's school — otherwise
        # an admin could link another school's student/team by UUID.
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
