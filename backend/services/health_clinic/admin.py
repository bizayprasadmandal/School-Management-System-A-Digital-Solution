from django.contrib import admin

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


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ["student", "blood_type", "height_cm", "weight_kg"]
    list_filter = ["blood_type"]
    search_fields = ["student__user__full_name", "allergies"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(NurseVisit)
class NurseVisitAdmin(admin.ModelAdmin):
    list_display = ["student", "visit_type", "visit_date", "status"]
    list_filter = ["visit_type", "status"]
    search_fields = ["student__user__full_name", "symptoms", "diagnosis"]


@admin.register(Immunization)
class ImmunizationAdmin(admin.ModelAdmin):
    list_display = ["student", "vaccine_name", "dose_number", "date_administered", "next_due_date"]
    list_filter = ["vaccine_name"]
    search_fields = ["student__user__full_name", "vaccine_name"]


@admin.register(MedicationLog)
class MedicationLogAdmin(admin.ModelAdmin):
    list_display = ["student", "medication_name", "dosage", "time_administered"]
    list_filter = ["medication_name"]
    search_fields = ["student__user__full_name", "medication_name"]


# =============================================================================
# Health Forms & Waivers
# =============================================================================


class HealthFormSubmissionInline(admin.TabularInline):
    model = HealthFormSubmission
    extra = 0
    readonly_fields = ["submitted_at"]


@admin.register(HealthForm)
class HealthFormAdmin(admin.ModelAdmin):
    list_display = ["title", "form_type", "status", "is_required", "due_date"]
    list_filter = ["form_type", "status", "is_required"]
    search_fields = ["title", "description"]
    inlines = [HealthFormSubmissionInline]


@admin.register(HealthFormSubmission)
class HealthFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ["student", "form", "status", "submitted_at"]
    list_filter = ["status"]
    search_fields = ["student__user__full_name"]
    readonly_fields = ["submitted_at"]


# =============================================================================
# Allergy Management
# =============================================================================


@admin.register(AllergyManagement)
class AllergyManagementAdmin(admin.ModelAdmin):
    list_display = ["student", "allergen_name", "allergy_type", "severity", "is_active"]
    list_filter = ["allergy_type", "severity", "is_active"]
    search_fields = ["student__user__full_name", "allergen_name"]


# =============================================================================
# Chronic Conditions
# =============================================================================


@admin.register(ChronicConditionTracking)
class ChronicConditionTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "condition_name", "condition_type", "severity", "is_active"]
    list_filter = ["condition_type", "severity", "is_active"]
    search_fields = ["student__user__full_name", "condition_name"]


# =============================================================================
# Emergency Plans & Contacts
# =============================================================================


@admin.register(EmergencyPlan)
class EmergencyPlanAdmin(admin.ModelAdmin):
    list_display = ["title", "plan_type", "status", "effective_date", "review_date"]
    list_filter = ["plan_type", "status"]
    search_fields = ["title", "description"]


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ["student", "contact_name", "relationship", "phone_primary", "is_primary"]
    list_filter = ["relationship", "is_primary", "can_pickup"]
    search_fields = ["student__user__full_name", "contact_name"]


# =============================================================================
# Health Screenings
# =============================================================================


class ScreeningResultInline(admin.TabularInline):
    model = ScreeningResult
    extra = 0


@admin.register(HealthScreening)
class HealthScreeningAdmin(admin.ModelAdmin):
    list_display = ["student", "screening_type", "screening_date", "status", "is_normal"]
    list_filter = ["screening_type", "status", "is_normal"]
    search_fields = ["student__user__full_name"]
    date_hierarchy = "screening_date"
    inlines = [ScreeningResultInline]


@admin.register(ScreeningResult)
class ScreeningResultAdmin(admin.ModelAdmin):
    list_display = ["screening", "metric_name", "metric_value", "is_abnormal"]
    list_filter = ["is_abnormal"]
    search_fields = ["metric_name", "metric_value"]


# =============================================================================
# Medication Inventory & Prescriptions
# =============================================================================


@admin.register(MedicationInventory)
class MedicationInventoryAdmin(admin.ModelAdmin):
    list_display = [
        "medication_name",
        "category",
        "quantity_on_hand",
        "reorder_threshold",
        "expiration_date",
        "is_active",
    ]
    list_filter = ["category", "is_active", "requires_refrigeration"]
    search_fields = ["medication_name", "generic_name"]


@admin.register(MedicationPrescription)
class MedicationPrescriptionAdmin(admin.ModelAdmin):
    list_display = ["student", "medication_name", "dosage", "frequency", "status", "start_date"]
    list_filter = ["status", "frequency"]
    search_fields = ["student__user__full_name", "medication_name"]
    date_hierarchy = "start_date"


# =============================================================================
# Parent Notifications
# =============================================================================


@admin.register(ParentNotification)
class ParentNotificationAdmin(admin.ModelAdmin):
    list_display = ["student", "notification_type", "delivery_method", "status", "sent_at"]
    list_filter = ["notification_type", "delivery_method", "status"]
    search_fields = ["student__user__full_name", "subject"]
    readonly_fields = ["sent_at", "read_at"]


# =============================================================================
# Health Compliance
# =============================================================================


@admin.register(HealthCompliance)
class HealthComplianceAdmin(admin.ModelAdmin):
    list_display = ["student", "compliance_type", "status", "due_date", "completed_date"]
    list_filter = ["compliance_type", "status"]
    search_fields = ["student__user__full_name", "requirement"]
    date_hierarchy = "due_date"


# =============================================================================
# Nurse Scheduling
# =============================================================================


@admin.register(NurseSchedule)
class NurseScheduleAdmin(admin.ModelAdmin):
    list_display = ["nurse", "day_of_week", "shift_type", "start_time", "end_time", "is_available"]
    list_filter = ["day_of_week", "shift_type", "is_available"]
    search_fields = ["nurse__first_name", "location"]


# =============================================================================
# Incident Reports
# =============================================================================


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ["student", "incident_type", "severity", "incident_date", "action_taken", "parent_notified"]
    list_filter = ["incident_type", "severity", "action_taken", "parent_notified"]
    search_fields = ["student__user__full_name", "description"]
    date_hierarchy = "incident_date"


# =============================================================================
# Medical Referrals
# =============================================================================


@admin.register(MedicalReferral)
class MedicalReferralAdmin(admin.ModelAdmin):
    list_display = ["student", "referral_reason", "status", "provider_name", "referral_date", "appointment_date"]
    list_filter = ["referral_reason", "status"]
    search_fields = ["student__user__full_name", "provider_name", "reason_for_referral"]
    date_hierarchy = "referral_date"


# =============================================================================
# Health Reports
# =============================================================================


@admin.register(HealthReport)
class HealthReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "status", "period_start", "period_end", "total_students"]
    list_filter = ["report_type", "status"]
    search_fields = ["title", "summary"]
    date_hierarchy = "created_at"


# =============================================================================
# Critical Health Alerts
# =============================================================================


@admin.register(HealthAlert)
class HealthAlertAdmin(admin.ModelAdmin):
    list_display = ["student", "alert_type", "urgency_level", "medication_name", "is_active"]
    list_filter = ["alert_type", "urgency_level", "is_active"]
    search_fields = ["student__user__full_name", "alert_message"]


# =============================================================================
# Health Education
# =============================================================================


@admin.register(HealthEducation)
class HealthEducationAdmin(admin.ModelAdmin):
    list_display = ["title", "resource_type", "topic_category", "is_required"]
    list_filter = ["resource_type", "topic_category", "is_required"]
    search_fields = ["title", "description"]


# =============================================================================
# Telehealth Sessions
# =============================================================================


@admin.register(TelehealthSession)
class TelehealthSessionAdmin(admin.ModelAdmin):
    list_display = ["student", "session_type", "status", "scheduled_date", "scheduled_time", "healthcare_provider"]
    list_filter = ["session_type", "status"]
    search_fields = ["student__user__full_name"]
    date_hierarchy = "scheduled_date"
