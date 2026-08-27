from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import AttendanceChangeLog, AttendanceLeave, AttendanceRecord, PeriodAttendance

MAX_BULK_RECORDS = 50
ATTENDANCE_EDIT_WINDOW_DAYS = getattr(settings, "ATTENDANCE_EDIT_WINDOW_DAYS", 7)


def log_attendance_change(attendance_type, record, change_type, user, old_values=None, new_values=None, reason=""):
    """Create an audit log entry for attendance changes."""
    AttendanceChangeLog.objects.create(
        attendance_type=attendance_type,
        attendance_id=record.id,
        change_type=change_type,
        old_values=old_values,
        new_values=new_values,
        changed_by=user,
        reason=reason,
    )


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    updated_by_name = serializers.CharField(source="updated_by.full_name", read_only=True, default=None)
    can_edit = serializers.SerializerMethodField()

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
            "updated_by",
            "updated_by_name",
            "updated_at",
            "remarks",
            "notified_guardian",
            "can_edit",
        ]
        read_only_fields = ["recorded_by", "recorded_at", "updated_by", "updated_at", "notified_guardian"]

    def get_can_edit(self, obj):
        """Check if this record can still be edited within the time window."""
        if not obj.recorded_at:
            return False
        now = timezone.now()
        elapsed = now - obj.recorded_at
        return elapsed.days <= ATTENDANCE_EDIT_WINDOW_DAYS


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
    updated_by_name = serializers.CharField(source="updated_by.full_name", read_only=True, default=None)
    can_edit = serializers.SerializerMethodField()

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
            "updated_by",
            "updated_by_name",
            "updated_at",
            "can_edit",
        ]
        read_only_fields = ["recorded_by", "recorded_at", "updated_by", "updated_at"]

    def get_can_edit(self, obj):
        """Check if this record can still be edited within the time window."""
        if not obj.recorded_at:
            return False
        now = timezone.now()
        elapsed = now - obj.recorded_at
        return elapsed.days <= ATTENDANCE_EDIT_WINDOW_DAYS

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


class AttendanceChangeLogSerializer(serializers.ModelSerializer):
    """Read-only serializer for attendance change logs."""

    changed_by_name = serializers.CharField(source="changed_by.full_name", read_only=True, default=None)

    class Meta:
        model = AttendanceChangeLog
        fields = [
            "id",
            "attendance_type",
            "attendance_id",
            "change_type",
            "old_values",
            "new_values",
            "changed_by",
            "changed_by_name",
            "changed_at",
            "reason",
        ]
        read_only_fields = fields


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
