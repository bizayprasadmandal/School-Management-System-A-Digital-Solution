from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Incident, Referral
from .serializers import IncidentSerializer, ReferralSerializer


class IsTeacherOrSchoolAdmin(permissions.BasePermission):
    """Teachers and admins can report behavior incidents."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "school_admin",
            "super_admin",
            "teacher",
        )


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["severity", "status", "incident_type", "student"]
    search_fields = ["description", "incident_type"]
    ordering = ["-occurred_at"]

    def get_queryset(self):
        return Incident.objects.filter(school=self.request.user.school).select_related("student__user", "reported_by")

    def get_permissions(self):
        if self.action in ["create"]:
            # Teachers and admins can report incidents
            return [IsAuthenticated(), IsTeacherOrSchoolAdmin()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, reported_by=self.request.user)


class ReferralViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "incident"]
    search_fields = ["reason", "action_taken"]

    def get_queryset(self):
        return Referral.objects.filter(incident__school=self.request.user.school).select_related(
            "referred_to", "referred_by", "incident"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(referred_by=self.request.user)
