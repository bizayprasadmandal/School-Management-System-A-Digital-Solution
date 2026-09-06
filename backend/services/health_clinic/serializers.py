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
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = HealthRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "school"]

    def validate_student(self, value):
        # Health records must stay within the tenant — the student has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


class NurseVisitSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    treated_by_name = serializers.CharField(source="treated_by.get_full_name", read_only=True)

    class Meta:
        model = NurseVisit
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
            "treated_by_name",
        ]
        read_only_fields = ["id", "created_at", "school"]

    def validate_student(self, value):
        # Nurse visits must stay within the tenant — the student has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


class ImmunizationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = Immunization
        fields = [
            "id",
            "id",
            "student",
            "vaccine_name",
            "dose_number",
            "date_administered",
            "administered_by",
            "facility",
            "batch_number",
            "next_due_date",
            "notes",
            "created_at",
            "student_name",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_student(self, value):
        # Immunizations must stay within the tenant — the student has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


class MedicationLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    administered_by_name = serializers.CharField(source="administered_by.get_full_name", read_only=True)

    class Meta:
        model = MedicationLog
        fields = [
            "id",
            "id",
            "student",
            "medication_name",
            "dosage",
            "route",
            "time_administered",
            "administered_by",
            "notes",
            "created_at",
            "student_name",
            "administered_by_name",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_student(self, value):
        # Medication logs must stay within the tenant — the student has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


class HealthFormSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = HealthForm
        fields = [
            "id",
            "school",
            "id",
            "title",
            "description",
            "form_type",
            "status",
            "form_fields",
            "instructions",
            "is_required",
            "due_date",
            "created_by",
            "created_at",
            "updated_at",
            "created_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class HealthFormSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    form_title = serializers.CharField(source="form.title", read_only=True)
    submitted_by_name = serializers.CharField(source="submitted_by.get_full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model = HealthFormSubmission
        fields = [
            "id",
            "id",
            "form",
            "student",
            "submitted_by",
            "status",
            "form_data",
            "attachments",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
            "signature_data",
            "student_name",
            "form_title",
            "submitted_by_name",
            "reviewed_by_name",
        ]
        read_only_fields = ["id", "updated_at"]


class AllergyManagementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = AllergyManagement
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class ChronicConditionTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = ChronicConditionTracking
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class EmergencyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyPlan
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class EmergencyContactSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HealthScreeningSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    screened_by_name = serializers.CharField(source="screened_by.get_full_name", read_only=True)

    class Meta:
        model = HealthScreening
        fields = [
            "id",
            "school",
            "id",
            "student",
            "screening_type",
            "screening_date",
            "status",
            "result_summary",
            "is_normal",
            "referral_needed",
            "referral_notes",
            "referred_to",
            "screened_by",
            "student_name",
            "screened_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class ScreeningResultSerializer(serializers.ModelSerializer):
    screening_label = serializers.CharField(source="screening.__str__", read_only=True)

    class Meta:
        model = ScreeningResult
        fields = [
            "id",
            "id",
            "screening",
            "metric_name",
            "metric_value",
            "normal_range",
            "is_abnormal",
            "notes",
            "created_at",
            "screening_label",
        ]
        read_only_fields = ["id", "created_at"]


class MedicationInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationInventory
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class MedicationPrescriptionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = MedicationPrescription
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class ParentNotificationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = ParentNotification
        fields = [
            "id",
            "school",
            "id",
            "student",
            "notification_type",
            "delivery_method",
            "status",
            "subject",
            "message",
            "nurse_visit",
            "medication_log",
            "sent_at",
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "school",
        )


class HealthComplianceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    verified_by_name = serializers.CharField(source="verified_by.get_full_name", read_only=True)

    class Meta:
        model = HealthCompliance
        fields = [
            "id",
            "school",
            "id",
            "student",
            "compliance_type",
            "status",
            "due_date",
            "completed_date",
            "expiration_date",
            "requirement",
            "notes",
            "document_url",
            "verified_by",
            "student_name",
            "verified_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class NurseScheduleSerializer(serializers.ModelSerializer):
    nurse_name = serializers.CharField(source="nurse.get_full_name", read_only=True)

    class Meta:
        model = NurseSchedule
        fields = [
            "id",
            "school",
            "id",
            "nurse",
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
            "nurse_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class IncidentReportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.get_full_name", read_only=True)

    class Meta:
        model = IncidentReport
        fields = [
            "id",
            "school",
            "id",
            "student",
            "incident_type",
            "severity",
            "incident_date",
            "location",
            "description",
            "action_taken",
            "action_details",
            "reported_by",
            "witnessed_by",
            "student_name",
            "reported_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class MedicalReferralSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = MedicalReferral
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class HealthReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)

    class Meta:
        model = HealthReport
        fields = [
            "id",
            "school",
            "id",
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
            "generated_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "school",
        )


class HealthAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = HealthAlert
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class HealthEducationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = HealthEducation
        fields = [
            "id",
            "school",
            "id",
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
            "created_at",
            "created_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class TelehealthSessionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = TelehealthSession
        fields = [
            "id",
            "school",
            "id",
            "student",
            "session_type",
            "status",
            "scheduled_date",
            "scheduled_time",
            "duration_minutes",
            "meeting_link",
            "meeting_id",
            "meeting_password",
            "healthcare_provider",
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class DentalRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = DentalRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class VisionRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = VisionRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class GrowthChartSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = GrowthChart
        fields = [
            "id",
            "school",
            "id",
            "student",
            "recorded_date",
            "height_cm",
            "weight_kg",
            "bmi",
            "head_circumference_cm",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "notes",
            "recorded_by",
            "student_name",
            "recorded_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "school",
        )


class VitalSignsSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = VitalSigns
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "school",
        )


class LabResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    ordered_by_name = serializers.CharField(source="ordered_by.get_full_name", read_only=True)

    class Meta:
        model = LabResult
        fields = [
            "id",
            "school",
            "id",
            "student",
            "test_name",
            "test_date",
            "result_date",
            "status",
            "result_value",
            "normal_range",
            "is_abnormal",
            "lab_name",
            "ordered_by",
            "student_name",
            "ordered_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class MedicalHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = MedicalHistory
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class FamilyMedicalHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = FamilyMedicalHistory
        fields = [
            "id",
            "school",
            "id",
            "student",
            "relationship",
            "condition_name",
            "age_at_diagnosis",
            "is_hereditary",
            "notes",
            "created_at",
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "school",
        )


class HealthInsuranceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = HealthInsuranceRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class VaccinationScheduleSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)

    class Meta:
        model = VaccinationSchedule
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class HealthAssessmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    assessed_by_name = serializers.CharField(source="assessed_by.get_full_name", read_only=True)

    class Meta:
        model = HealthAssessment
        fields = [
            "id",
            "school",
            "id",
            "student",
            "assessment_type",
            "assessment_date",
            "assessed_by",
            "general_health",
            "immunizations_current",
            "allergies_checked",
            "medications_checked",
            "vision_screened",
            "hearing_screened",
            "student_name",
            "assessed_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class HealthRiskAssessmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    assessed_by_name = serializers.CharField(source="assessed_by.get_full_name", read_only=True)

    class Meta:
        model = HealthRiskAssessment
        fields = [
            "id",
            "school",
            "id",
            "student",
            "assessment_date",
            "risk_level",
            "risk_factors",
            "chronic_conditions",
            "family_history_risks",
            "lifestyle_factors",
            "environmental_factors",
            "mitigation_plan",
            "assessed_by",
            "student_name",
            "assessed_by_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class MentalHealthRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    provider_name = serializers.CharField(source="provider.get_full_name", read_only=True)

    class Meta:
        model = MentalHealthRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
            "session_type",
            "session_date",
            "provider",
            "presenting_issue",
            "assessment_findings",
            "diagnosis",
            "treatment_plan",
            "interventions",
            "progress_notes",
            "student_name",
            "provider_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class HealthEducationMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthEducationMaterial
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class HealthCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCampaign
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class HealthSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthSurvey
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class MedicalEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalEquipment
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )


class EquipmentMaintenanceSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = EquipmentMaintenance
        fields = [
            "id",
            "id",
            "equipment",
            "maintenance_type",
            "maintenance_date",
            "next_due_date",
            "cost",
            "performed_by",
            "description",
            "notes",
            "created_at",
            "equipment_name",
        ]
        read_only_fields = ["id", "created_at"]


class HealthStaffTrainingSerializer(serializers.ModelSerializer):
    staff_member_name = serializers.CharField(source="staff_member.get_full_name", read_only=True)

    class Meta:
        model = HealthStaffTraining
        fields = [
            "id",
            "school",
            "id",
            "staff_member",
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
            "staff_member_name",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "school",
        )


class HealthAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthAudit
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "school",
        )
