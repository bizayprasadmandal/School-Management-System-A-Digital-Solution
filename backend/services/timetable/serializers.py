"""Serializers for timetable."""

from rest_framework import serializers

from .models import (
    AcademicCalendar,
    AcademicSession,
    BellSchedule,
    BellScheduleEntry,
    ClassGroup,
    ClassGroupEnrollment,
    ClassSchedule,
    CoCurricularSchedule,
    ConflictDetection,
    DailySchedule,
    ExamAttendance,
    ExamRoomAllocation,
    ExamSchedule,
    ExamScheduleEntry,
    LessonPlan,
    Period,
    RoomBooking,
    RoomUtilization,
    SchoolClosure,
    SchoolEvent,
    SeatingArrangement,
    SubjectTeacherAssignment,
    SubstituteSchedule,
    SubstituteTeacher,
    TeacherPreference,
    TeacherTimetable,
    TeacherWorkload,
    TimetableAnalytics,
    TimetableApproval,
    TimetableChange,
    TimetableChangeRequest,
    TimetableReport,
    TimetableResource,
    TimetableResourceBooking,
    TimetableSlot,
    TimetableTemplate,
    TimetableTemplateSlot,
    TimetableValidationError,
    TimetableValidationRule,
    TimetableVersion,
)


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ["id", "school", "name", "period_number", "start_time", "end_time", "is_break"]
        read_only_fields = ["id", "school"]

    def validate_period_number(self, value):
        request = self.context.get("request")
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            school = request.user.school
            qs = Period.objects.filter(school=school, period_number=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(f"A period with number {value} already exists for this school.")
        return value


class TimetableSlotSerializer(serializers.ModelSerializer):

    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    subject_code = serializers.CharField(source="assignment.subject.code", read_only=True)
    teacher_name = serializers.CharField(source="assignment.teacher.full_name", read_only=True)
    classroom_name = serializers.SerializerMethodField()
    period_name = serializers.CharField(source="period.name", read_only=True)
    period_number = serializers.IntegerField(source="period.period_number", read_only=True)
    start_time = serializers.TimeField(source="period.start_time", read_only=True)
    end_time = serializers.TimeField(source="period.end_time", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = TimetableSlot
        fields = [
            "id",
            "classroom",
            "classroom_name",
            "assignment",
            "subject_name",
            "subject_code",
            "teacher_name",
            "period",
            "period_name",
            "period_number",
            "start_time",
            "end_time",
            "day_of_week",
            "day_name",
            "room",
            "academic_year",
            "effective_from",
            "effective_to",
        ]

    def get_classroom_name(self, obj):
        return str(obj.classroom)

    def get_day_name(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")

    def validate(self, attrs):
        # Conflict detection: teacher double-booking.
        # Use instance values for fields not present in a PATCH payload.
        assignment = attrs.get("assignment") or getattr(self.instance, "assignment", None)
        if assignment is None:
            return attrs
        teacher = assignment.teacher
        day = attrs.get("day_of_week", getattr(self.instance, "day_of_week", None))
        period = attrs.get("period", getattr(self.instance, "period", None))
        academic_year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        existing = TimetableSlot.objects.filter(
            assignment__teacher=teacher,
            day_of_week=day,
            period=period,
            academic_year=academic_year,
        ).exclude(pk=self.instance.pk if self.instance else None)
        if existing.exists():
            raise serializers.ValidationError(
                f"Teacher '{teacher.full_name}' is already assigned to another class "
                f"in {period.name} on {dict(TimetableSlot.DAYS_OF_WEEK)[day]}."
            )
        return attrs


class SchoolEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolEvent
        fields = [
            "id",
            "school",
            "title",
            "description",
            "event_type",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "venue",
            "is_school_wide",
            "target_grades",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "school", "created_by", "created_at"]


class TeacherTimetableSerializer(serializers.ModelSerializer):

    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.__str__", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherTimetable
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "teacher",
            "academic_year",
            "slot",
            "classroom",
            "subject",
            "period",
            "day_of_week",
            "total_hours_per_week",
        ]

    def get_day_name(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")


class SubstituteTeacherSerializer(serializers.ModelSerializer):

    original_teacher_name = serializers.CharField(source="original_teacher.get_full_name", read_only=True)
    substitute_teacher_name = serializers.CharField(source="substitute_teacher.get_full_name", read_only=True)

    class Meta:
        model = SubstituteTeacher
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "school",
            "original_teacher",
            "substitute_teacher",
            "slot",
            "date",
            "period",
            "reason",
            "status",
            "notes",
        ]


class ConflictDetectionSerializer(serializers.ModelSerializer):

    conflict_type_display = serializers.CharField(source="get_conflict_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ConflictDetection
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "school",
            "conflict_type",
            "slot1",
            "slot2",
            "description",
            "status",
            "resolution_notes",
            "resolved_by",
            "resolved_at",
        ]


class ExamScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSchedule
        fields = [
            "id",
            "school",
            "id",
            "title",
            "exam_type",
            "academic_year",
            "start_date",
            "end_date",
            "status",
            "instructions",
            "published_at",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ExamScheduleEntrySerializer(serializers.ModelSerializer):

    classroom_name = serializers.CharField(source="classroom.__str__", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    invigilator_name = serializers.CharField(source="invigilator.get_full_name", read_only=True)

    class Meta:
        model = ExamScheduleEntry
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "exam_schedule",
            "classroom",
            "subject",
            "exam_date",
            "start_time",
            "end_time",
            "room",
            "invigilator",
            "total_marks",
            "passing_marks",
        ]


class AcademicCalendarSerializer(serializers.ModelSerializer):

    calendar_type_display = serializers.CharField(source="get_calendar_type_display", read_only=True)

    class Meta:
        model = AcademicCalendar
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "school",
            "academic_year",
            "title",
            "calendar_type",
            "start_date",
            "end_date",
            "description",
            "is_school_wide",
            "target_grades",
            "notes",
        ]


class RoomBookingSerializer(serializers.ModelSerializer):

    booked_by_name = serializers.CharField(source="booked_by.get_full_name", read_only=True)
    booking_type_display = serializers.CharField(source="get_booking_type_display", read_only=True)

    class Meta:
        model = RoomBooking
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "school",
            "room_name",
            "booking_type",
            "booked_by",
            "date",
            "start_time",
            "end_time",
            "purpose",
            "attendees_count",
            "status",
            "notes",
            "approved_by",
        ]


class TimetableTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableTemplate
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "grade",
            "periods_per_day",
            "working_days",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableTemplateSlotSerializer(serializers.ModelSerializer):

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = TimetableTemplateSlot
        fields = "__all__"

    def get_day_name(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")


class TeacherPreferenceSerializer(serializers.ModelSerializer):

    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    preference_type_display = serializers.CharField(source="get_preference_type_display", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherPreference
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "teacher",
            "preference_type",
            "day_of_week",
            "period",
            "reason",
            "is_recurring",
            "effective_from",
            "effective_to",
        ]

    def get_day_name(self, obj):
        if obj.day_of_week is not None:
            return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")
        return None


class TimetableApprovalSerializer(serializers.ModelSerializer):

    submitted_by_name = serializers.CharField(source="submitted_by.get_full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = TimetableApproval
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "school",
            "title",
            "academic_year",
            "grade",
            "status",
            "submitted_by",
            "submitted_at",
            "approved_by",
            "approved_at",
        ]


class TimetableChangeSerializer(serializers.ModelSerializer):

    change_type_display = serializers.CharField(source="get_change_type_display", read_only=True)
    changed_by_name = serializers.CharField(source="changed_by.get_full_name", read_only=True)

    class Meta:
        model = TimetableChange
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "school",
            "change_type",
            "slot",
            "old_value",
            "new_value",
            "effective_date",
            "reason",
            "changed_by",
            "notified",
        ]


class CoCurricularScheduleSerializer(serializers.ModelSerializer):

    activity_type_display = serializers.CharField(source="get_activity_type_display", read_only=True)
    instructor_name = serializers.CharField(source="instructor.get_full_name", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = CoCurricularSchedule
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "school",
            "activity_name",
            "activity_type",
            "instructor",
            "day_of_week",
            "start_time",
            "end_time",
            "venue",
            "max_participants",
            "target_grades",
            "is_mandatory",
            "is_active",
        ]

    def get_day_name(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")


class TimetableReportSerializer(serializers.ModelSerializer):

    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)

    class Meta:
        model = TimetableReport
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "school",
            "title",
            "report_type",
            "academic_year",
            "date_from",
            "date_to",
            "data",
            "summary",
            "generated_by",
            "file_url",
        ]


class SchoolClosureSerializer(serializers.ModelSerializer):

    closure_type_display = serializers.CharField(source="get_closure_type_display", read_only=True)

    class Meta:
        model = SchoolClosure
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "school",
            "title",
            "closure_type",
            "date",
            "description",
            "affects_all",
            "target_grades",
            "notified",
        ]


# ─── New Views ───────────────────────────────────────────────────────────────
class BellScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BellSchedule
        fields = [
            "id",
            "school",
            "id",
            "name",
            "day_type",
            "is_active",
            "effective_from",
            "effective_until",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BellScheduleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BellScheduleEntry
        fields = [
            "id",
            "id",
            "bell_schedule",
            "period",
            "start_time",
            "end_time",
            "is_break",
            "break_name",
            "sort_order",
        ]
        read_only_fields = ["id"]


class ClassGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroup
        fields = [
            "id",
            "school",
            "id",
            "grade_level",
            "section_name",
            "academic_year",
            "max_students",
            "current_students",
            "class_teacher",
            "homeroom",
            "subjects",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ClassGroupEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroupEnrollment
        fields = ["id", "id", "class_group", "student", "enrolled_date", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class SubjectTeacherAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectTeacherAssignment
        fields = [
            "id",
            "school",
            "id",
            "teacher",
            "subject",
            "subject_code",
            "class_group",
            "periods_per_week",
            "academic_year",
            "semester",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LessonPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonPlan
        fields = [
            "id",
            "school",
            "id",
            "teacher",
            "class_group",
            "subject",
            "plan_date",
            "period",
            "timetable_slot",
            "topic",
            "learning_objectives",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ExamRoomAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamRoomAllocation
        fields = [
            "id",
            "school",
            "id",
            "exam_schedule",
            "room",
            "seating_capacity",
            "students_allocated",
            "invigilator",
            "co_invigilator",
            "seating_arrangement",
            "equipment_needed",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SeatingArrangementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatingArrangement
        fields = ["id", "id", "room_allocation", "student", "seat_number", "row", "column", "created_at"]
        read_only_fields = ["id", "created_at"]


class ExamAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttendance
        fields = [
            "id",
            "id",
            "exam_entry",
            "student",
            "status",
            "arrival_time",
            "departure_time",
            "minutes_late",
            "seating",
            "invigilator_notes",
            "recorded_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AcademicSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSession
        fields = [
            "id",
            "school",
            "id",
            "name",
            "academic_year",
            "semester",
            "start_date",
            "end_date",
            "enrollment_start",
            "enrollment_end",
            "exam_start_date",
            "exam_end_date",
            "results_date",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SubstituteScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubstituteSchedule
        fields = [
            "id",
            "school",
            "id",
            "substitute_teacher",
            "original_teacher",
            "date",
            "timetable_slot",
            "class_group",
            "subject",
            "status",
            "lesson_plan",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomUtilizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomUtilization
        fields = [
            "id",
            "id",
            "room",
            "date",
            "total_hours_available",
            "total_hours_used",
            "utilization_percentage",
            "teaching_hours",
            "exam_hours",
            "meeting_hours",
            "event_hours",
            "conflicts_detected",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TimetableValidationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableValidationRule
        fields = [
            "id",
            "school",
            "id",
            "name",
            "rule_type",
            "description",
            "max_value",
            "min_value",
            "parameters",
            "is_hard_constraint",
            "priority",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableValidationErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableValidationError
        fields = [
            "id",
            "id",
            "rule",
            "timetable_slot",
            "severity",
            "message",
            "details",
            "resolved",
            "resolved_by",
            "resolved_at",
            "resolution_notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TimetableResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableResource
        fields = [
            "id",
            "school",
            "id",
            "name",
            "resource_type",
            "room",
            "capacity",
            "is_available",
            "hourly_cost",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableResourceBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableResourceBooking
        fields = [
            "id",
            "id",
            "resource",
            "booked_by",
            "class_group",
            "booking_date",
            "start_time",
            "end_time",
            "purpose",
            "event",
            "status",
            "approved_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableAnalytics
        fields = [
            "id",
            "school",
            "id",
            "academic_year",
            "semester",
            "generation_date",
            "total_classes",
            "total_slots",
            "total_teachers",
            "total_rooms",
            "conflicts_found",
            "conflicts_resolved",
            "validation_score",
            "avg_teacher_load",
            "max_teacher_load",
        ]
        read_only_fields = ["id", "created_at"]


class TimetableChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableChangeRequest
        fields = [
            "id",
            "school",
            "id",
            "requested_by",
            "request_type",
            "status",
            "description",
            "original_slot",
            "requested_slot",
            "approved_by",
            "approval_notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DailyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySchedule
        fields = [
            "id",
            "school",
            "id",
            "date",
            "day_of_week",
            "total_classes_scheduled",
            "total_classes_conducted",
            "total_classes_cancelled",
            "total_substitutes",
            "is_holiday",
            "holiday_name",
            "is_special_schedule",
            "special_schedule_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeacherWorkloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherWorkload
        fields = [
            "id",
            "school",
            "id",
            "teacher",
            "academic_year",
            "semester",
            "total_periods_per_week",
            "total_classes",
            "total_students",
            "subjects_taught",
            "classes_taught",
            "max_periods_per_week",
            "workload_percentage",
            "duty_hours_per_week",
        ]
        read_only_fields = ["id", "created_at"]


class ClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        fields = [
            "id",
            "id",
            "class_group",
            "academic_year",
            "total_weekly_periods",
            "subjects_scheduled",
            "is_finalized",
            "finalized_at",
            "finalized_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableVersion
        fields = [
            "id",
            "school",
            "id",
            "academic_year",
            "semester",
            "version_number",
            "name",
            "description",
            "timetable_data",
            "is_current",
            "is_published",
            "published_at",
            "changes_from_previous",
            "created_by",
        ]
        read_only_fields = ["id", "created_at"]
