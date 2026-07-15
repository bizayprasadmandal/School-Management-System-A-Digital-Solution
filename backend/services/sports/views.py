"""Sports & Extracurriculars — Viewsets with school-scoped CRUD."""

import logging
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Sport, Team, TeamMember, SportEvent, SportAchievement
from .serializers import SportSerializer, TeamSerializer, TeamMemberSerializer, SportEventSerializer, SportAchievementSerializer
from core.permissions import IsSchoolAdmin, IsSchoolMember
from core.pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)


class SportViewSet(viewsets.ModelViewSet):
    serializer_class = SportSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description"]; filterset_fields = ["category", "is_active"]
    def get_queryset(self): return Sport.objects.filter(school=self.request.user.school)
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]; filterset_fields = ["sport", "is_active", "gender"]
    def get_queryset(self):
        return Team.objects.filter(school=self.request.user.school).select_related("sport", "coach").prefetch_related("members__student__user")
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)


class TeamMemberViewSet(viewsets.ModelViewSet):
    serializer_class = TeamMemberSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]; filterset_fields = ["team", "status", "role"]
    def get_queryset(self):
        return TeamMember.objects.filter(team__school=self.request.user.school).select_related("student__user", "team")
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save()


class SportEventViewSet(viewsets.ModelViewSet):
    serializer_class = SportEventSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "opponent", "location"]; filterset_fields = ["sport", "team", "status"]
    def get_queryset(self):
        return SportEvent.objects.filter(school=self.request.user.school).select_related("sport", "team")
    def get_permissions(self): return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)


class SportAchievementViewSet(viewsets.ModelViewSet):
    serializer_class = SportAchievementSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "position", "level"]; filterset_fields = ["student", "team", "level"]
    def get_queryset(self):
        return SportAchievement.objects.filter(school=self.request.user.school).select_related("student__user", "team", "event")
    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)
