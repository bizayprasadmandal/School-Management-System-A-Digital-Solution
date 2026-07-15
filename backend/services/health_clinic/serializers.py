"""Health/Clinic serializers."""

from rest_framework import serializers
from .models import HealthRecord, NurseVisit, Immunization, MedicationLog


class HealthRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    class Meta:
        model = HealthRecord
        fields = ["id", "student", "student_name", "blood_type", "height_cm", "weight_kg", "allergies", "chronic_conditions", "medications", "emergency_contact_name", "emergency_contact_phone", "doctor_name", "doctor_phone", "insurance_provider", "insurance_number", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class NurseVisitSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    visit_type_display = serializers.CharField(source="get_visit_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    treated_by_name = serializers.CharField(source="treated_by.full_name", read_only=True, default=None)

    class Meta:
        model = NurseVisit
        fields = ["id", "student", "student_name", "visit_type", "visit_type_display", "visit_date", "symptoms", "diagnosis", "treatment", "medication_given", "temperature_c", "blood_pressure", "status", "status_display", "treated_by", "treated_by_name", "notes", "follow_up_date", "created_at"]
        read_only_fields = ["id", "visit_date", "created_at"]


class ImmunizationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    class Meta:
        model = Immunization
        fields = ["id", "student", "student_name", "vaccine_name", "dose_number", "date_administered", "administered_by", "facility", "batch_number", "next_due_date", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class MedicationLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    administered_by_name = serializers.CharField(source="administered_by.full_name", read_only=True, default=None)
    class Meta:
        model = MedicationLog
        fields = ["id", "student", "student_name", "medication_name", "dosage", "route", "time_administered", "administered_by", "administered_by_name", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]
