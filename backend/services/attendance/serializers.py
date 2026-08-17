from django.db import transaction
from rest_framework import serializers

from .models import AttendanceLeave, AttendanceRecord

MAX_BULK_RECORDS = 50


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "student",
            "student_name",
            "classroom",
            "date",
            "status",
            "recorded_by",
            "recorded_at",
            "remarks",
            "notified_guardian",
        ]
        read_only_fields = ["recorded_by", "recorded_at", "notified_guardian"]


class BulkAttendanceSerializer(serializers.Serializer):
    classroom_id = serializers.IntegerField()
    date = serializers.DateField()
    records = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
        max_length=MAX_BULK_RECORDS,
    )

    def validate_records(self, value):
        if len(value) > MAX_BULK_RECORDS:
            raise serializers.ValidationError(
                f"Cannot record attendance for more than {MAX_BULK_RECORDS} students at once."
            )
        return value

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
        from services.students.models import AcademicYear, Student

        academic_year = AcademicYear.objects.filter(school=user.school, is_current=True).first()

        # Tenant isolation on the write path: every student in the payload must
        # belong to the classroom's school, otherwise a teacher could record
        # attendance against another school's students by ID.
        student_ids = [entry["student_id"] for entry in self.validated_data["records"]]
        valid_ids = set(
            str(i)
            for i in Student.objects.filter(id__in=student_ids, school=classroom.school).values_list("id", flat=True)
        )
        invalid_ids = [str(sid) for sid in student_ids if str(sid) not in valid_ids]
        if invalid_ids:
            raise serializers.ValidationError({"records": f"Student(s) not found in this school: {invalid_ids[:5]}"})

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
            "id",
            "student",
            "leave_type",
            "from_date",
            "to_date",
            "reason",
            "supporting_document",
            "status",
            "reviewed_by",
            "review_remarks",
            "requested_at",
            "reviewed_at",
            "total_days",
        ]
        read_only_fields = ["status", "reviewed_by", "review_remarks", "requested_at", "reviewed_at"]
