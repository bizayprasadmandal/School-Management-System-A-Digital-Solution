"""Health/Clinic — School-scoped viewsets."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import HealthRecord, NurseVisit, Immunization, MedicationLog
from .serializers import HealthRecordSerializer, NurseVisitSerializer, ImmunizationSerializer, MedicationLogSerializer
from core.permissions import IsSchoolAdmin, IsSchoolMember
from core.pagination import StandardResultsSetPagination


class HealthRecordViewSet(viewsets.ModelViewSet):
    serializer_class = HealthRecordSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "allergies", "chronic_conditions"]
    filterset_fields = ["blood_type"]
    def get_queryset(self):
        return HealthRecord.objects.filter(school=self.request.user.school).select_related("student__user")
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)


class NurseVisitViewSet(viewsets.ModelViewSet):
    serializer_class = NurseVisitSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "symptoms", "diagnosis", "treatment"]
    filterset_fields = ["visit_type", "status", "student"]
    def get_queryset(self):
        return NurseVisit.objects.filter(school=self.request.user.school).select_related("student__user", "treated_by")
    def get_permissions(self): return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, treated_by=self.request.user)


class ImmunizationViewSet(viewsets.ModelViewSet):
    serializer_class = ImmunizationSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "vaccine_name"]
    filterset_fields = ["student", "vaccine_name"]
    def get_queryset(self):
        return Immunization.objects.filter(student__school=self.request.user.school).select_related("student__user")
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save()


class MedicationLogViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationLogSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "medication_name"]
    filterset_fields = ["student", "medication_name"]
    def get_queryset(self):
        return MedicationLog.objects.filter(student__school=self.request.user.school).select_related("student__user", "administered_by")
    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]
    def perform_create(self, serializer):
        serializer.save(administered_by=self.request.user)
