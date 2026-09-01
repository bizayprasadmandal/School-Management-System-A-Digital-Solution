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
        fields = ["id", "school", "on_delete", "name", "period_number", "start_time", "end_time", "is_break"]
        read_only_fields = ["id"]


class TimetableSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableSlot
        fields = [
            "id",
            "classroom",
            "on_delete",
            "assignment",
            "on_delete",
            "period",
            "on_delete",
            "day_of_week",
            "academic_year",
            "on_delete",
            "room",
            "effective_from",
            "effective_to",
        ]
        read_only_fields = ["id"]


class SchoolEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolEvent
        fields = [
            "id",
            "school",
            "on_delete",
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
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TeacherTimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherTimetable
        fields = [
            "id",
            "id",
            "teacher",
            "on_delete",
            "academic_year",
            "on_delete",
            "slot",
            "on_delete",
            "classroom",
            "on_delete",
            "subject",
            "on_delete",
            "period",
            "on_delete",
            "day_of_week",
            "total_hours_per_week",
        ]
        read_only_fields = ["id", "created_at"]


class SubstituteTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubstituteTeacher
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "original_teacher",
            "on_delete",
            "substitute_teacher",
            "on_delete",
            "slot",
            "on_delete",
            "date",
            "period",
            "on_delete",
            "reason",
            "status",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConflictDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConflictDetection
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "conflict_type",
            "slot1",
            "on_delete",
            "slot2",
            "on_delete",
            "description",
            "status",
            "resolution_notes",
            "resolved_by",
            "on_delete",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ExamScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSchedule
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "exam_type",
            "academic_year",
            "on_delete",
            "start_date",
            "end_date",
            "status",
            "instructions",
            "published_at",
            "created_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ExamScheduleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamScheduleEntry
        fields = [
            "id",
            "id",
            "exam_schedule",
            "on_delete",
            "classroom",
            "on_delete",
            "subject",
            "on_delete",
            "exam_date",
            "start_time",
            "end_time",
            "room",
            "invigilator",
            "on_delete",
            "total_marks",
            "passing_marks",
        ]
        read_only_fields = ["id", "created_at"]


class AcademicCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendar
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "academic_year",
            "on_delete",
            "title",
            "calendar_type",
            "start_date",
            "end_date",
            "description",
            "is_school_wide",
            "target_grades",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomBooking
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "room_name",
            "booking_type",
            "booked_by",
            "on_delete",
            "date",
            "start_time",
            "end_time",
            "purpose",
            "attendees_count",
            "status",
            "notes",
            "approved_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableTemplate
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "grade",
            "on_delete",
            "periods_per_day",
            "working_days",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableTemplateSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableTemplateSlot
        fields = [
            "id",
            "id",
            "template",
            "on_delete",
            "subject",
            "on_delete",
            "period",
            "on_delete",
            "day_of_week",
            "room",
            "notes",
        ]
        read_only_fields = ["id"]


class TeacherPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherPreference
        fields = [
            "id",
            "id",
            "teacher",
            "on_delete",
            "preference_type",
            "day_of_week",
            "period",
            "on_delete",
            "reason",
            "is_recurring",
            "effective_from",
            "effective_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableApproval
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "academic_year",
            "on_delete",
            "grade",
            "on_delete",
            "status",
            "submitted_by",
            "on_delete",
            "submitted_at",
            "approved_by",
            "on_delete",
            "approved_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableChange
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "change_type",
            "slot",
            "on_delete",
            "old_value",
            "new_value",
            "effective_date",
            "reason",
            "changed_by",
            "on_delete",
            "notified",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CoCurricularScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoCurricularSchedule
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "activity_name",
            "activity_type",
            "instructor",
            "on_delete",
            "day_of_week",
            "start_time",
            "end_time",
            "venue",
            "max_participants",
            "target_grades",
            "is_mandatory",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "report_type",
            "academic_year",
            "on_delete",
            "date_from",
            "date_to",
            "data",
            "summary",
            "generated_by",
            "on_delete",
            "file_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SchoolClosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClosure
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "closure_type",
            "date",
            "description",
            "affects_all",
            "target_grades",
            "notified",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BellScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BellSchedule
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
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
            "on_delete",
            "period",
            "on_delete",
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
            "on_delete",
            "grade_level",
            "section_name",
            "academic_year",
            "max_students",
            "current_students",
            "class_teacher",
            "on_delete",
            "homeroom",
            "on_delete",
            "subjects",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ClassGroupEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroupEnrollment
        fields = [
            "id",
            "id",
            "class_group",
            "on_delete",
            "student",
            "on_delete",
            "enrolled_date",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SubjectTeacherAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectTeacherAssignment
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "teacher",
            "on_delete",
            "subject",
            "subject_code",
            "class_group",
            "on_delete",
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
            "on_delete",
            "teacher",
            "on_delete",
            "class_group",
            "on_delete",
            "subject",
            "plan_date",
            "period",
            "on_delete",
            "timetable_slot",
            "on_delete",
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
            "on_delete",
            "exam_schedule",
            "on_delete",
            "room",
            "on_delete",
            "seating_capacity",
            "students_allocated",
            "invigilator",
            "on_delete",
            "co_invigilator",
            "on_delete",
            "seating_arrangement",
            "equipment_needed",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SeatingArrangementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatingArrangement
        fields = [
            "id",
            "id",
            "room_allocation",
            "on_delete",
            "student",
            "on_delete",
            "seat_number",
            "row",
            "column",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ExamAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttendance
        fields = [
            "id",
            "id",
            "exam_entry",
            "on_delete",
            "student",
            "on_delete",
            "status",
            "arrival_time",
            "departure_time",
            "minutes_late",
            "seating",
            "on_delete",
            "invigilator_notes",
            "recorded_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "substitute_teacher",
            "on_delete",
            "original_teacher",
            "on_delete",
            "date",
            "timetable_slot",
            "on_delete",
            "class_group",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "timetable_slot",
            "on_delete",
            "severity",
            "message",
            "details",
            "resolved",
            "resolved_by",
            "on_delete",
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
            "on_delete",
            "name",
            "resource_type",
            "room",
            "on_delete",
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
            "on_delete",
            "booked_by",
            "on_delete",
            "class_group",
            "on_delete",
            "booking_date",
            "start_time",
            "end_time",
            "purpose",
            "event",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "requested_by",
            "on_delete",
            "request_type",
            "status",
            "description",
            "original_slot",
            "on_delete",
            "requested_slot",
            "on_delete",
            "approved_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "teacher",
            "on_delete",
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
            "on_delete",
            "academic_year",
            "total_weekly_periods",
            "subjects_scheduled",
            "is_finalized",
            "finalized_at",
            "finalized_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]
