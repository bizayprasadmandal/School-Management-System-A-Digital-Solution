from django.db import transaction
from rest_framework import serializers

from .models import AttendanceLeave, AttendanceRecord, PeriodAttendance

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


class PeriodAttendanceSerializer(serializers.ModelSerializer):
    """Serializer for period-level attendance tracking."""

    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    teacher_name = serializers.CharField(source="assignment.teacher.full_name", read_only=True)

    class Meta:
        model = PeriodAttendance
        fields = [
            "id",
            "student",
            "student_name",
            "assignment",
            "subject_name",
            "teacher_name",
            "date",
            "period_number",
            "status",
            "recorded_by",
            "recorded_at",
        ]
        read_only_fields = ["recorded_by", "recorded_at"]

    def validate_period_number(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Period number must be between 1 and 10.")
        return value

    def validate(self, data):
        # Ensure teacher can only record for their own assignments
        user = self.context["request"].user
        if user.role == "teacher":
            assignment = data.get("assignment")
            if assignment and assignment.teacher != user:
                raise serializers.ValidationError(
                    {"assignment": "You can only record attendance for your own classes."}
                )
        return data


class BulkPeriodAttendanceSerializer(serializers.Serializer):
    """Bulk record period attendance for multiple students."""

    assignment_id = serializers.IntegerField()
    date = serializers.DateField()
    period_number = serializers.IntegerField(min_value=1, max_value=10)
    records = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
        max_length=MAX_BULK_RECORDS,
    )

    def validate_assignment_id(self, value):
        from services.academics.models import TeacherAssignment

        user = self.context["request"].user
        try:
            assignment = TeacherAssignment.objects.select_related("subject", "teacher").get(id=value)
        except TeacherAssignment.DoesNotExist:
            raise serializers.ValidationError("Teacher assignment not found.")

        # Tenant isolation: assignment must belong to user's school
        if assignment.subject.school != user.school:
            raise serializers.ValidationError("Assignment not found in your school.")

        return assignment

    def validate_records(self, value):
        if len(value) > MAX_BULK_RECORDS:
            raise serializers.ValidationError(
                f"Cannot record attendance for more than {MAX_BULK_RECORDS} students at once."
            )
        return value

    @transaction.atomic
    def save(self):
        assignment = self.validated_data["assignment_id"]
        date = self.validated_data["date"]
        period_number = self.validated_data["period_number"]
        user = self.context["request"].user

        from services.students.models import Student

        student_ids = [entry["student_id"] for entry in self.validated_data["records"]]
        valid_ids = set(
            str(i)
            for i in Student.objects.filter(id__in=student_ids, school=assignment.subject.school).values_list(
                "id", flat=True
            )
        )
        invalid_ids = [str(sid) for sid in student_ids if str(sid) not in valid_ids]
        if invalid_ids:
            raise serializers.ValidationError({"records": f"Student(s) not found in this school: {invalid_ids[:5]}"})

        records = []
        for entry in self.validated_data["records"]:
            record, _ = PeriodAttendance.objects.update_or_create(
                student_id=entry["student_id"],
                assignment=assignment,
                date=date,
                period_number=period_number,
                defaults={
                    "status": entry["status"],
                    "recorded_by": user,
                },
            )
            records.append(record)
        return records
