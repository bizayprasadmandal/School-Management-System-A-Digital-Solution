"""Serializers for health_clinic."""

from rest_framework import serializers

from .models import (
    AllergyManagement,
    ChronicConditionTracking,
    DentalRecord,
    EmergencyContact,
    EmergencyPlan,
    EquipmentMaintenance,
    FamilyMedicalHistory,
    GrowthChart,
    HealthAlert,
    HealthAssessment,
    HealthAudit,
    HealthCampaign,
    HealthCompliance,
    HealthEducation,
    HealthEducationMaterial,
    HealthForm,
    HealthFormSubmission,
    HealthInsuranceRecord,
    HealthRecord,
    HealthReport,
    HealthRiskAssessment,
    HealthScreening,
    HealthStaffTraining,
    HealthSurvey,
    Immunization,
    IncidentReport,
    LabResult,
    MedicalEquipment,
    MedicalHistory,
    MedicalReferral,
    MedicationInventory,
    MedicationLog,
    MedicationPrescription,
    MentalHealthRecord,
    NurseSchedule,
    NurseVisit,
    ParentNotification,
    ScreeningResult,
    TelehealthSession,
    VaccinationSchedule,
    VisionRecord,
    VitalSigns,
)


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "blood_type",
            "height_cm",
            "weight_kg",
            "allergies",
            "chronic_conditions",
            "medications",
            "emergency_contact_name",
            "emergency_contact_phone",
            "doctor_name",
            "doctor_phone",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NurseVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseVisit
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "visit_type",
            "visit_date",
            "symptoms",
            "diagnosis",
            "treatment",
            "medication_given",
            "temperature_c",
            "blood_pressure",
            "status",
            "treated_by",
        ]
        read_only_fields = ["id", "created_at"]


class ImmunizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Immunization
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "vaccine_name",
            "dose_number",
            "date_administered",
            "administered_by",
            "facility",
            "batch_number",
            "next_due_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MedicationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationLog
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "medication_name",
            "dosage",
            "route",
            "time_administered",
            "administered_by",
            "on_delete",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HealthFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthForm
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "description",
            "form_type",
            "status",
            "form_fields",
            "instructions",
            "is_required",
            "due_date",
            "created_by",
            "on_delete",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthFormSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthFormSubmission
        fields = [
            "id",
            "id",
            "form",
            "on_delete",
            "student",
            "on_delete",
            "submitted_by",
            "on_delete",
            "status",
            "form_data",
            "attachments",
            "reviewed_by",
            "on_delete",
            "reviewed_at",
            "review_notes",
            "signature_data",
        ]
        read_only_fields = ["id", "updated_at"]


class AllergyManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllergyManagement
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "allergen_name",
            "allergy_type",
            "severity",
            "symptoms",
            "reaction_description",
            "treatment_protocol",
            "emergency_medication",
            "medication_location",
            "diagnosis_date",
            "diagnosed_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ChronicConditionTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChronicConditionTracking
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "condition_type",
            "condition_name",
            "severity",
            "diagnosed_date",
            "diagnosed_by",
            "management_plan",
            "medication_schedule",
            "dietary_restrictions",
            "activity_restrictions",
            "emergency_protocol",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmergencyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyPlan
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "plan_type",
            "status",
            "description",
            "procedures",
            "responsible_staff",
            "contact_numbers",
            "required_equipment",
            "equipment_location",
            "last_training_date",
            "training_notes",
            "effective_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "contact_name",
            "relationship",
            "phone_primary",
            "phone_secondary",
            "email",
            "address",
            "is_primary",
            "can_pickup",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthScreeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthScreening
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "screening_type",
            "screening_date",
            "status",
            "result_summary",
            "is_normal",
            "referral_needed",
            "referral_notes",
            "referred_to",
            "screened_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ScreeningResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningResult
        fields = [
            "id",
            "id",
            "screening",
            "on_delete",
            "metric_name",
            "metric_value",
            "normal_range",
            "is_abnormal",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MedicationInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationInventory
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "medication_name",
            "generic_name",
            "category",
            "quantity_on_hand",
            "unit_of_measure",
            "reorder_threshold",
            "storage_location",
            "requires_refrigeration",
            "expiration_date",
            "lot_number",
            "supplier",
            "last_reorder_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MedicationPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationPrescription
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "medication_name",
            "dosage",
            "frequency",
            "route",
            "start_date",
            "end_date",
            "times_per_day",
            "administration_times",
            "prescribed_by",
            "prescriber_phone",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ParentNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentNotification
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "notification_type",
            "delivery_method",
            "status",
            "subject",
            "message",
            "nurse_visit",
            "on_delete",
            "medication_log",
            "on_delete",
            "sent_at",
        ]
        read_only_fields = ["id", "created_at"]


class HealthComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCompliance
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "compliance_type",
            "status",
            "due_date",
            "completed_date",
            "expiration_date",
            "requirement",
            "notes",
            "document_url",
            "verified_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NurseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseSchedule
        fields = [
            "id",
            "school",
            "id",
            "nurse",
            "on_delete",
            "on_delete",
            "day_of_week",
            "shift_type",
            "start_time",
            "end_time",
            "is_available",
            "location",
            "notes",
            "is_recurring",
            "effective_from",
            "effective_until",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class IncidentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "incident_type",
            "severity",
            "incident_date",
            "location",
            "description",
            "action_taken",
            "action_details",
            "reported_by",
            "on_delete",
            "witnessed_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MedicalReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalReferral
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "referral_reason",
            "status",
            "provider_name",
            "provider_phone",
            "provider_address",
            "reason_for_referral",
            "urgency",
            "referral_date",
            "appointment_date",
            "completed_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "report_type",
            "status",
            "period_start",
            "period_end",
            "summary",
            "findings",
            "recommendations",
            "total_students",
            "total_visits",
            "total_incidents",
            "generated_by",
        ]
        read_only_fields = ["id", "created_at"]


class HealthAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthAlert
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "alert_type",
            "urgency_level",
            "alert_message",
            "emergency_instructions",
            "medication_name",
            "medication_location",
            "emergency_contact_name",
            "emergency_contact_phone",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthEducation
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "description",
            "resource_type",
            "topic_category",
            "content_url",
            "file_url",
            "content_text",
            "target_grades",
            "is_required",
            "created_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TelehealthSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelehealthSession
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "session_type",
            "status",
            "scheduled_date",
            "scheduled_time",
            "duration_minutes",
            "meeting_link",
            "meeting_id",
            "meeting_password",
            "healthcare_provider",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DentalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentalRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "visit_date",
            "dentist_name",
            "status",
            "examination_findings",
            "cavities_count",
            "gum_health",
            "treatment_provided",
            "prescriptions",
            "next_checkup_date",
            "xray_url",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VisionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisionRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "screening_date",
            "result",
            "left_eye_vision",
            "right_eye_vision",
            "color_blindness",
            "glasses_prescribed",
            "prescription_details",
            "specialist_referral",
            "referral_details",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GrowthChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowthChart
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "recorded_date",
            "height_cm",
            "weight_kg",
            "bmi",
            "head_circumference_cm",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "notes",
            "recorded_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class VitalSignsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSigns
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "recorded_date",
            "recorded_time",
            "temperature",
            "heart_rate",
            "respiratory_rate",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "oxygen_saturation",
            "blood_glucose",
            "pain_scale",
        ]
        read_only_fields = ["id", "created_at"]


class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "test_name",
            "test_date",
            "result_date",
            "status",
            "result_value",
            "normal_range",
            "is_abnormal",
            "lab_name",
            "ordered_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "history_type",
            "condition_name",
            "diagnosis_date",
            "treating_physician",
            "treatment",
            "outcome",
            "is_chronic",
            "is_resolved",
            "resolved_date",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FamilyMedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMedicalHistory
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "relationship",
            "condition_name",
            "age_at_diagnosis",
            "is_hereditary",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HealthInsuranceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthInsuranceRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "insurance_type",
            "provider_name",
            "policy_number",
            "group_number",
            "subscriber_name",
            "subscriber_relationship",
            "effective_date",
            "expiry_date",
            "coverage_amount",
            "copay_amount",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VaccinationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationSchedule
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "vaccine_name",
            "dose_number",
            "due_date",
            "completed_date",
            "status",
            "administered_by",
            "batch_number",
            "site_of_administration",
            "reactions",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthAssessment
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "assessment_type",
            "assessment_date",
            "assessed_by",
            "on_delete",
            "general_health",
            "immunizations_current",
            "allergies_checked",
            "medications_checked",
            "vision_screened",
            "hearing_screened",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthRiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRiskAssessment
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "assessment_date",
            "risk_level",
            "risk_factors",
            "chronic_conditions",
            "family_history_risks",
            "lifestyle_factors",
            "environmental_factors",
            "mitigation_plan",
            "assessed_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MentalHealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentalHealthRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "session_type",
            "session_date",
            "provider",
            "on_delete",
            "presenting_issue",
            "assessment_findings",
            "diagnosis",
            "treatment_plan",
            "interventions",
            "progress_notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthEducationMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthEducationMaterial
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "material_type",
            "topic",
            "description",
            "content",
            "file_url",
            "target_audience",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCampaign
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "campaign_type",
            "start_date",
            "end_date",
            "target_audience",
            "status",
            "budget",
            "participants_count",
            "materials",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthSurvey
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "description",
            "questions",
            "target_audience",
            "start_date",
            "end_date",
            "status",
            "is_anonymous",
            "response_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MedicalEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalEquipment
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "equipment_type",
            "model_name",
            "serial_number",
            "purchase_date",
            "purchase_cost",
            "status",
            "location",
            "last_calibration_date",
            "next_calibration_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EquipmentMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentMaintenance
        fields = [
            "id",
            "id",
            "equipment",
            "on_delete",
            "maintenance_type",
            "maintenance_date",
            "next_due_date",
            "cost",
            "performed_by",
            "description",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HealthStaffTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthStaffTraining
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "staff_member",
            "on_delete",
            "training_name",
            "training_type",
            "provider",
            "start_date",
            "end_date",
            "hours",
            "certificate_url",
            "expiry_date",
            "is_completed",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class HealthAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthAudit
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "audit_type",
            "title",
            "audit_date",
            "auditor",
            "status",
            "findings",
            "recommendations",
            "corrective_actions",
            "compliance_score",
            "notes",
            "report_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
