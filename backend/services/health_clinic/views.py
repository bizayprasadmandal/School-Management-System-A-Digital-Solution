"""Health/Clinic — School-scoped viewsets."""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import (
    AllergyManagement,
    ChronicConditionTracking,
    EmergencyContact,
    EmergencyPlan,
    HealthAlert,
    HealthCompliance,
    HealthEducation,
    HealthForm,
    HealthFormSubmission,
    HealthRecord,
    HealthReport,
    HealthScreening,
    Immunization,
    IncidentReport,
    MedicalReferral,
    MedicationInventory,
    MedicationLog,
    MedicationPrescription,
    NurseSchedule,
    NurseVisit,
    ParentNotification,
    ScreeningResult,
    TelehealthSession,
)
from .serializers import (
    AllergyManagementSerializer,
    ChronicConditionTrackingSerializer,
    EmergencyContactSerializer,
    EmergencyPlanSerializer,
    HealthAlertSerializer,
    HealthComplianceSerializer,
    HealthEducationSerializer,
    HealthFormSerializer,
    HealthFormSubmissionSerializer,
    HealthRecordSerializer,
    HealthReportSerializer,
    HealthScreeningSerializer,
    ImmunizationSerializer,
    IncidentReportSerializer,
    MedicalReferralSerializer,
    MedicationInventorySerializer,
    MedicationLogSerializer,
    MedicationPrescriptionSerializer,
    NurseScheduleSerializer,
    NurseVisitSerializer,
    ParentNotificationSerializer,
    ScreeningResultSerializer,
    TelehealthSessionSerializer,
)


class HealthRecordViewSet(viewsets.ModelViewSet):
    serializer_class = HealthRecordSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "allergies",
        "chronic_conditions",
    ]
    filterset_fields = ["blood_type"]

    def get_queryset(self):
        return HealthRecord.objects.filter(school=self.request.user.school).select_related("student__user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class NurseVisitViewSet(viewsets.ModelViewSet):
    serializer_class = NurseVisitSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "symptoms",
        "diagnosis",
        "treatment",
    ]
    filterset_fields = ["visit_type", "status", "student"]

    def get_queryset(self):
        return NurseVisit.objects.filter(school=self.request.user.school).select_related("student__user", "treated_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, treated_by=self.request.user)


class ImmunizationViewSet(viewsets.ModelViewSet):
    serializer_class = ImmunizationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "vaccine_name"]
    filterset_fields = ["student", "vaccine_name"]

    def get_queryset(self):
        return Immunization.objects.filter(student__school=self.request.user.school).select_related("student__user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class MedicationLogViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "medication_name"]
    filterset_fields = ["student", "medication_name"]

    def get_queryset(self):
        return MedicationLog.objects.filter(student__school=self.request.user.school).select_related(
            "student__user", "administered_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(administered_by=self.request.user)


# =============================================================================
# Health Forms & Waivers ViewSets
# =============================================================================


class HealthFormViewSet(viewsets.ModelViewSet):
    serializer_class = HealthFormSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["form_type", "status", "is_required"]

    def get_queryset(self):
        return HealthForm.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class HealthFormSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = HealthFormSubmissionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    filterset_fields = ["form", "student", "status"]

    def get_queryset(self):
        return HealthFormSubmission.objects.filter(form__school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


# =============================================================================
# Allergy Management ViewSets
# =============================================================================


class AllergyManagementViewSet(viewsets.ModelViewSet):
    serializer_class = AllergyManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "allergen_name"]
    filterset_fields = ["student", "allergy_type", "severity", "is_active"]

    def get_queryset(self):
        return AllergyManagement.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Chronic Condition Tracking ViewSets
# =============================================================================


class ChronicConditionTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = ChronicConditionTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "condition_name"]
    filterset_fields = ["student", "condition_type", "severity", "is_active"]

    def get_queryset(self):
        return ChronicConditionTracking.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Emergency Plans & Contacts ViewSets
# =============================================================================


class EmergencyPlanViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["plan_type", "status"]

    def get_queryset(self):
        return EmergencyPlan.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class EmergencyContactViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyContactSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "contact_name"]
    filterset_fields = ["student", "relationship", "is_primary", "can_pickup"]

    def get_queryset(self):
        return EmergencyContact.objects.filter(student__school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Health Screenings ViewSets
# =============================================================================


class HealthScreeningViewSet(viewsets.ModelViewSet):
    serializer_class = HealthScreeningSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    filterset_fields = ["student", "screening_type", "status", "is_normal"]

    def get_queryset(self):
        return HealthScreening.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, screened_by=self.request.user)


class ScreeningResultViewSet(viewsets.ModelViewSet):
    serializer_class = ScreeningResultSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["screening", "is_abnormal"]

    def get_queryset(self):
        return ScreeningResult.objects.filter(screening__school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Medication Inventory & Prescriptions ViewSets
# =============================================================================


class MedicationInventoryViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationInventorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["medication_name", "generic_name"]
    filterset_fields = ["category", "is_active", "requires_refrigeration"]

    def get_queryset(self):
        return MedicationInventory.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MedicationPrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationPrescriptionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "medication_name"]
    filterset_fields = ["student", "status", "frequency"]

    def get_queryset(self):
        return MedicationPrescription.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Parent Notifications ViewSets
# =============================================================================


class ParentNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = ParentNotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "subject"]
    filterset_fields = ["student", "notification_type", "delivery_method", "status"]

    def get_queryset(self):
        return ParentNotification.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Health Compliance ViewSets
# =============================================================================


class HealthComplianceViewSet(viewsets.ModelViewSet):
    serializer_class = HealthComplianceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "requirement"]
    filterset_fields = ["student", "compliance_type", "status"]

    def get_queryset(self):
        return HealthCompliance.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Nurse Scheduling ViewSets
# =============================================================================


class NurseScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = NurseScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["nurse", "day_of_week", "shift_type", "is_available"]

    def get_queryset(self):
        return NurseSchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Incident Reports ViewSets
# =============================================================================


class IncidentReportViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "description"]
    filterset_fields = ["student", "incident_type", "severity", "action_taken"]

    def get_queryset(self):
        return IncidentReport.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, reported_by=self.request.user)


# =============================================================================
# Medical Referrals ViewSets
# =============================================================================


class MedicalReferralViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalReferralSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "provider_name"]
    filterset_fields = ["student", "referral_reason", "status"]

    def get_queryset(self):
        return MedicalReferral.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, referred_by=self.request.user)


# =============================================================================
# Health Reports ViewSets
# =============================================================================


class HealthReportViewSet(viewsets.ModelViewSet):
    serializer_class = HealthReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "summary"]
    filterset_fields = ["report_type", "status"]

    def get_queryset(self):
        return HealthReport.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, generated_by=self.request.user)


# =============================================================================
# Critical Health Alerts ViewSets
# =============================================================================


class HealthAlertViewSet(viewsets.ModelViewSet):
    serializer_class = HealthAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "alert_message"]
    filterset_fields = ["student", "alert_type", "urgency_level", "is_active"]

    def get_queryset(self):
        return HealthAlert.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Health Education ViewSets
# =============================================================================


class HealthEducationViewSet(viewsets.ModelViewSet):
    serializer_class = HealthEducationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["resource_type", "topic_category", "is_required"]

    def get_queryset(self):
        return HealthEducation.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


# =============================================================================
# Telehealth Sessions ViewSets
# =============================================================================


class TelehealthSessionViewSet(viewsets.ModelViewSet):
    serializer_class = TelehealthSessionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    filterset_fields = ["student", "session_type", "status", "scheduled_date"]

    def get_queryset(self):
        return TelehealthSession.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
