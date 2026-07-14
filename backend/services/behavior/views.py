from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Incident, Referral
from .serializers import IncidentSerializer, ReferralSerializer
from core.permissions import IsSchoolMember, IsSchoolAdmin
from core.pagination import StandardResultsSetPagination


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["severity", "status", "incident_type", "student"]
    search_fields = ["description", "incident_type"]
    ordering = ["-occurred_at"]

    def get_queryset(self):
        return Incident.objects.filter(school=self.request.user.school).select_related(
            "student__user", "reported_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
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
        return Referral.objects.filter(
            incident__school=self.request.user.school
        ).select_related("referred_to", "referred_by", "incident")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]
