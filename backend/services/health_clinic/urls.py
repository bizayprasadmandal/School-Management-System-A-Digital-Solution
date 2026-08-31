from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AllergyManagementViewSet,
    ChronicConditionTrackingViewSet,
    EmergencyContactViewSet,
    EmergencyPlanViewSet,
    HealthAlertViewSet,
    HealthComplianceViewSet,
    HealthEducationViewSet,
    HealthFormSubmissionViewSet,
    HealthFormViewSet,
    HealthRecordViewSet,
    HealthReportViewSet,
    HealthScreeningViewSet,
    ImmunizationViewSet,
    IncidentReportViewSet,
    MedicalReferralViewSet,
    MedicationInventoryViewSet,
    MedicationLogViewSet,
    MedicationPrescriptionViewSet,
    NurseScheduleViewSet,
    NurseVisitViewSet,
    ParentNotificationViewSet,
    ScreeningResultViewSet,
    TelehealthSessionViewSet,
)

app_name = "health_v1"
router = DefaultRouter()
router.register(r"records", HealthRecordViewSet, basename="health-record")
router.register(r"visits", NurseVisitViewSet, basename="nurse-visit")
router.register(r"immunizations", ImmunizationViewSet, basename="immunization")
router.register(r"medication-logs", MedicationLogViewSet, basename="medication-log")
router.register(r"forms", HealthFormViewSet, basename="health-form")
router.register(r"form-submissions", HealthFormSubmissionViewSet, basename="health-form-submission")
router.register(r"allergies", AllergyManagementViewSet, basename="allergy")
router.register(r"chronic-conditions", ChronicConditionTrackingViewSet, basename="chronic-condition")
router.register(r"emergency-plans", EmergencyPlanViewSet, basename="emergency-plan")
router.register(r"emergency-contacts", EmergencyContactViewSet, basename="emergency-contact")
router.register(r"screenings", HealthScreeningViewSet, basename="health-screening")
router.register(r"screening-results", ScreeningResultViewSet, basename="screening-result")
router.register(r"medication-inventory", MedicationInventoryViewSet, basename="medication-inventory")
router.register(r"prescriptions", MedicationPrescriptionViewSet, basename="medication-prescription")
router.register(r"notifications", ParentNotificationViewSet, basename="parent-notification")
router.register(r"compliance", HealthComplianceViewSet, basename="health-compliance")
router.register(r"nurse-schedule", NurseScheduleViewSet, basename="nurse-schedule")
router.register(r"incidents", IncidentReportViewSet, basename="incident-report")
router.register(r"referrals", MedicalReferralViewSet, basename="medical-referral")
router.register(r"reports", HealthReportViewSet, basename="health-report")
router.register(r"alerts", HealthAlertViewSet, basename="health-alert")
router.register(r"education", HealthEducationViewSet, basename="health-education")
router.register(r"telehealth", TelehealthSessionViewSet, basename="telehealth-session")
urlpatterns = [path("", include(router.urls))]
