from django.contrib import admin
from .models import HealthRecord, NurseVisit, Immunization, MedicationLog

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ["student", "blood_type", "height_cm", "weight_kg"]; list_filter = ["blood_type"]; search_fields = ["student__user__full_name", "allergies"]; readonly_fields = ["id", "created_at", "updated_at"]

@admin.register(NurseVisit)
class NurseVisitAdmin(admin.ModelAdmin):
    list_display = ["student", "visit_type", "visit_date", "status"]; list_filter = ["visit_type", "status"]; search_fields = ["student__user__full_name", "symptoms", "diagnosis"]

@admin.register(Immunization)
class ImmunizationAdmin(admin.ModelAdmin):
    list_display = ["student", "vaccine_name", "dose_number", "date_administered", "next_due_date"]; list_filter = ["vaccine_name"]; search_fields = ["student__user__full_name", "vaccine_name"]

@admin.register(MedicationLog)
class MedicationLogAdmin(admin.ModelAdmin):
    list_display = ["student", "medication_name", "dosage", "time_administered"]; list_filter = ["medication_name"]; search_fields = ["student__user__full_name", "medication_name"]
