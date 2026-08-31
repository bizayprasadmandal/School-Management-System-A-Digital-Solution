"""Health/Clinic serializers."""

from rest_framework import serializers

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


class HealthRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = HealthRecord
        fields = [
            "id",
            "student",
            "student_name",
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
            "insurance_provider",
            "insurance_number",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_student(self, value):
        # Health records must stay within the tenant — the student has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


class NurseVisitSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    visit_type_display = serializers.CharField(source="get_visit_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    treated_by_name = serializers.CharField(source="treated_by.full_name", read_only=True, default=None)

    class Meta:
        model = NurseVisit
        fields = [
            "id",
            "student",
            "student_name",
            "visit_type",
            "visit_type_display",
            "visit_date",
            "symptoms",
            "diagnosis",
            "treatment",
            "medication_given",
            "temperature_c",
            "blood_pressure",
            "status",
            "status_display",
            "treated_by",
            "treated_by_name",
            "notes",
            "follow_up_date",
            "created_at",
        ]
        read_only_fields = ["id", "treated_by", "visit_date", "created_at"]

    def validate_student(self, value):
        # Nurse visits must stay within the tenant — the student has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


class ImmunizationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = Immunization
        fields = [
            "id",
            "student",
            "student_name",
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

    def validate_student(self, value):
        # Immunizations must stay within the tenant — the student has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


class MedicationLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    administered_by_name = serializers.CharField(source="administered_by.full_name", read_only=True, default=None)

    class Meta:
        model = MedicationLog
        fields = [
            "id",
            "student",
            "student_name",
            "medication_name",
            "dosage",
            "route",
            "time_administered",
            "administered_by",
            "administered_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "administered_by", "created_at"]

    def validate_student(self, value):
        # Medication logs must stay within the tenant — the student has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


# =============================================================================
# Health Forms & Waivers Serializers
# =============================================================================


class HealthFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthForm
        fields = [
            "id",
            "title",
            "description",
            "form_type",
            "status",
            "form_fields",
            "instructions",
            "is_required",
            "due_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HealthFormSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    form_title = serializers.CharField(source="form.title", read_only=True)
    submitted_by_name = serializers.CharField(source="submitted_by.full_name", read_only=True, default=None)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)

    class Meta:
        model = HealthFormSubmission
        fields = [
            "id",
            "form",
            "form_title",
            "student",
            "student_name",
            "submitted_by",
            "submitted_by_name",
            "status",
            "form_data",
            "attachments",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "review_notes",
            "signature_data",
            "signed_at",
            "submitted_at",
        ]
        read_only_fields = ["id", "submitted_at"]


# =============================================================================
# Allergy Management Serializers
# =============================================================================


class AllergyManagementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = AllergyManagement
        fields = [
            "id",
            "student",
            "student_name",
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
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Chronic Condition Tracking Serializers
# =============================================================================


class ChronicConditionTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = ChronicConditionTracking
        fields = [
            "id",
            "student",
            "student_name",
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
            "emergency_medication",
            "emergency_med_location",
            "specialist_name",
            "specialist_phone",
            "is_active",
            "last_review_date",
            "next_review_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Emergency Plans & Contacts Serializers
# =============================================================================


class EmergencyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyPlan
        fields = [
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
            "review_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "student",
            "student_name",
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
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Health Screenings Serializers
# =============================================================================


class ScreeningResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningResult
        fields = [
            "id",
            "screening",
            "metric_name",
            "metric_value",
            "normal_range",
            "is_abnormal",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HealthScreeningSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    results = ScreeningResultSerializer(many=True, read_only=True)
    screened_by_name = serializers.CharField(source="screened_by.full_name", read_only=True, default=None)

    class Meta:
        model = HealthScreening
        fields = [
            "id",
            "student",
            "student_name",
            "screening_type",
            "screening_date",
            "status",
            "result_summary",
            "is_normal",
            "referral_needed",
            "referral_notes",
            "referred_to",
            "screened_by",
            "screened_by_name",
            "notes",
            "results",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Medication Inventory & Prescriptions Serializers
# =============================================================================


class MedicationInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationInventory
        fields = [
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
            "is_controlled",
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MedicationPrescriptionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = MedicationPrescription
        fields = [
            "id",
            "student",
            "student_name",
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
            "parent_consent",
            "consent_date",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Parent Notifications Serializers
# =============================================================================


class ParentNotificationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = ParentNotification
        fields = [
            "id",
            "student",
            "student_name",
            "notification_type",
            "delivery_method",
            "status",
            "subject",
            "message",
            "sent_at",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "read_at", "created_at"]


# =============================================================================
# Health Compliance Serializers
# =============================================================================


class HealthComplianceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    verified_by_name = serializers.CharField(source="verified_by.full_name", read_only=True, default=None)

    class Meta:
        model = HealthCompliance
        fields = [
            "id",
            "student",
            "student_name",
            "compliance_type",
            "status",
            "due_date",
            "completed_date",
            "expiration_date",
            "requirement",
            "notes",
            "document_url",
            "verified_by",
            "verified_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Nurse Scheduling Serializers
# =============================================================================


class NurseScheduleSerializer(serializers.ModelSerializer):
    nurse_name = serializers.CharField(source="nurse.full_name", read_only=True)

    class Meta:
        model = NurseSchedule
        fields = [
            "id",
            "nurse",
            "nurse_name",
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
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Incident Reports Serializers
# =============================================================================


class IncidentReportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True, default=None)

    class Meta:
        model = IncidentReport
        fields = [
            "id",
            "student",
            "student_name",
            "incident_type",
            "severity",
            "incident_date",
            "location",
            "description",
            "action_taken",
            "action_details",
            "reported_by",
            "reported_by_name",
            "witnessed_by",
            "parent_notified",
            "parent_notified_at",
            "follow_up_needed",
            "follow_up_notes",
            "treatment_given",
            "hospital_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Medical Referrals Serializers
# =============================================================================


class MedicalReferralSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    referred_by_name = serializers.CharField(source="referred_by.full_name", read_only=True, default=None)

    class Meta:
        model = MedicalReferral
        fields = [
            "id",
            "student",
            "student_name",
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
            "follow_up_needed",
            "follow_up_notes",
            "referred_by",
            "referred_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Health Reports Serializers
# =============================================================================


class HealthReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = HealthReport
        fields = [
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
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Critical Health Alerts Serializers
# =============================================================================


class HealthAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = HealthAlert
        fields = [
            "id",
            "student",
            "student_name",
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
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Health Education Serializers
# =============================================================================


class HealthEducationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = HealthEducation
        fields = [
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
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Telehealth Sessions Serializers
# =============================================================================


class TelehealthSessionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    healthcare_provider_name = serializers.CharField(
        source="healthcare_provider.full_name", read_only=True, default=None
    )

    class Meta:
        model = TelehealthSession
        fields = [
            "id",
            "student",
            "student_name",
            "session_type",
            "status",
            "scheduled_date",
            "scheduled_time",
            "duration_minutes",
            "meeting_link",
            "meeting_id",
            "healthcare_provider",
            "healthcare_provider_name",
            "parent_present",
            "nurse_present",
            "notes",
            "diagnosis",
            "treatment_plan",
            "follow_up_needed",
            "follow_up_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
