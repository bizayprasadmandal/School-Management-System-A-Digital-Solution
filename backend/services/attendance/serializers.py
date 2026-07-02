from rest_framework import serializers
from django.db import transaction
from .models import AttendanceRecord, AttendanceLeave


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id", "student", "student_name", "classroom", "date",
            "status", "recorded_by", "recorded_at", "remarks", "notified_guardian",
        ]
        read_only_fields = ["recorded_by", "recorded_at", "notified_guardian"]


class BulkAttendanceSerializer(serializers.Serializer):
    classroom_id = serializers.IntegerField()
    date = serializers.DateField()
    records = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
    )

    def validate_classroom_id(self, value):
        from services.students.models import Classroom
        user = self.context["request"].user
        try:
            return Classroom.objects.get(id=value, school=user.school)
        except Classroom.DoesNotExist:
            raise serializers.ValidationError("Classroom not found.")

    @transaction.atomic
    def save(self):
        classroom = self.validated_data["classroom_id"]
        date = self.validated_data["date"]
        user = self.context["request"].user
        from services.students.models import AcademicYear
        academic_year = AcademicYear.objects.filter(school=user.school, is_current=True).first()

        records = []
        for entry in self.validated_data["records"]:
            record, _ = AttendanceRecord.objects.update_or_create(
                student_id=entry["student_id"],
                date=date,
                defaults={
                    "classroom": classroom,
                    "academic_year": academic_year,
                    "status": entry["status"],
                    "remarks": entry.get("remarks", ""),
                    "recorded_by": user,
                },
            )
            records.append(record)
        return records


class AttendanceLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLeave
        fields = [
            "id", "student", "leave_type", "from_date", "to_date",
            "reason", "supporting_document", "status",
            "reviewed_by", "review_remarks", "requested_at", "reviewed_at",
            "total_days",
        ]
        read_only_fields = ["status", "reviewed_by", "review_remarks", "requested_at", "reviewed_at"]
