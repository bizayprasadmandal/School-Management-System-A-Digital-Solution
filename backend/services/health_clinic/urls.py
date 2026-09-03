from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AllergyManagementViewSet,
    ChronicConditionTrackingViewSet,
    DentalRecordViewSet,
    EmergencyContactViewSet,
    EmergencyPlanViewSet,
    EquipmentMaintenanceViewSet,
    FamilyMedicalHistoryViewSet,
    GrowthChartViewSet,
    HealthAlertViewSet,
    HealthAssessmentViewSet,
    HealthAuditViewSet,
    HealthCampaignViewSet,
    HealthComplianceViewSet,
    HealthEducationMaterialViewSet,
    HealthEducationViewSet,
    HealthFormSubmissionViewSet,
    HealthFormViewSet,
    HealthInsuranceRecordViewSet,
    HealthRecordViewSet,
    HealthReportViewSet,
    HealthRiskAssessmentViewSet,
    HealthScreeningViewSet,
    HealthStaffTrainingViewSet,
    HealthSurveyViewSet,
    ImmunizationViewSet,
    IncidentReportViewSet,
    LabResultViewSet,
    MedicalEquipmentViewSet,
    MedicalHistoryViewSet,
    MedicalReferralViewSet,
    MedicationInventoryViewSet,
    MedicationLogViewSet,
    MedicationPrescriptionViewSet,
    MentalHealthRecordViewSet,
    NurseScheduleViewSet,
    NurseVisitViewSet,
    ParentNotificationViewSet,
    ScreeningResultViewSet,
    TelehealthSessionViewSet,
    VaccinationScheduleViewSet,
    VisionRecordViewSet,
    VitalSignsViewSet,
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

# ── Additional registrations (module expansion) ──
router.register(r"dental-record", DentalRecordViewSet, basename="dental-record")
router.register(r"vision-record", VisionRecordViewSet, basename="vision-record")
router.register(r"growth-chart", GrowthChartViewSet, basename="growth-chart")
router.register(r"vital-signs", VitalSignsViewSet, basename="vital-signs")
router.register(r"lab-result", LabResultViewSet, basename="lab-result")
router.register(r"medical-history", MedicalHistoryViewSet, basename="medical-history")
router.register(r"family-medical-history", FamilyMedicalHistoryViewSet, basename="family-medical-history")
router.register(r"health-insurance-record", HealthInsuranceRecordViewSet, basename="health-insurance-record")
router.register(r"vaccination-schedule", VaccinationScheduleViewSet, basename="vaccination-schedule")
router.register(r"health-assessment", HealthAssessmentViewSet, basename="health-assessment")
router.register(r"health-risk-assessment", HealthRiskAssessmentViewSet, basename="health-risk-assessment")
router.register(r"mental-health-record", MentalHealthRecordViewSet, basename="mental-health-record")
router.register(r"health-education-material", HealthEducationMaterialViewSet, basename="health-education-material")
router.register(r"health-campaign", HealthCampaignViewSet, basename="health-campaign")
router.register(r"health-survey", HealthSurveyViewSet, basename="health-survey")
router.register(r"medical-equipment", MedicalEquipmentViewSet, basename="medical-equipment")
router.register(r"equipment-maintenance", EquipmentMaintenanceViewSet, basename="equipment-maintenance")
router.register(r"health-staff-training", HealthStaffTrainingViewSet, basename="health-staff-training")
router.register(r"health-audit", HealthAuditViewSet, basename="health-audit")

urlpatterns = [path("", include(router.urls))]
