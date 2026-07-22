"""
Counseling Service — Serializers.
"""

from rest_framework import serializers
from .models import CounselingAppointment, StudentReferral


class CounselingAppointmentSerializer(serializers.ModelSerializer):
    """Full appointment details — used for GET and detail views."""

    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_grade = serializers.CharField(
        source="student.classroom.grade.name", read_only=True, allow_null=True,
    )
    student_class = serializers.CharField(
        source="student.classroom.name", read_only=True, allow_null=True,
    )

    class Meta:
        model = CounselingAppointment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class CounselingAppointmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Appointment creation/update — write-only fields excluded."""

    send_reminder = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = CounselingAppointment
        fields = [
            "counselor", "student", "appointment_type", "status",
            "scheduled_date", "scheduled_time", "duration_minutes",
            "location", "reason", "notes", "follow_up_needed",
            "follow_up_date", "send_reminder",
        ]


class StudentReferralSerializer(serializers.ModelSerializer):
    """Full referral details with computed display names."""

    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_grade = serializers.CharField(
        source="student.classroom.grade.name", read_only=True, allow_null=True,
    )
    student_class = serializers.CharField(
        source="student.classroom.name", read_only=True, allow_null=True,
    )
    referred_by_name = serializers.CharField(source="referred_by.full_name", read_only=True, allow_null=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, allow_null=True)

    class Meta:
        model = StudentReferral
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "action_taken_at"]


class StudentReferralCreateUpdateSerializer(serializers.ModelSerializer):
    """Referral creation/update — sensitive computed fields excluded."""

    notify_counselor = serializers.BooleanField(default=True, write_only=True)

    class Meta:
        model = StudentReferral
        fields = [
            "student", "assigned_to", "category", "priority", "status",
            "reason", "notes", "intervention_plan", "outcome",
            "follow_up_date", "is_confidential", "notify_counselor",
        ]

    def validate_reason(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Reason must be at least 10 characters.")
        return value
