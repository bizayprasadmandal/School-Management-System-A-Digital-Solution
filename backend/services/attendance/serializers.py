"""Serializers for attendance."""

from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from .models import (
    AttendanceAlertConfig,
    AttendanceAuditEntry,
    AttendanceChangeLog,
    AttendanceComment,
    AttendanceConfiguration,
    AttendanceCorrectionWorkflow,
    AttendanceDashboard,
    AttendanceDataArchive,
    AttendanceEscalation,
    AttendanceHistoryView,
    AttendanceIncentive,
    AttendanceIncentiveAward,
    AttendanceLeave,
    AttendanceLockout,
    AttendanceMakeUp,
    AttendancePatterns,
    AttendancePolicy,
    AttendancePrediction,
    AttendanceRecord,
    AttendanceReport,
    BiometricCheckin,
    BulkAttendanceImport,
    ChronicAbsenceTracking,
    EarlyDismissal,
    FieldTrip,
    FieldTripParticipant,
    GPSAttendance,
    Holiday,
    LeaveApprovalLevel,
    LeaveBalance,
    ParentNotification,
    PeriodAttendance,
    QRCodeCheckin,
    QRCodeSession,
    RealTimeDashboard,
    RFIDCheckin,
    StudentAttendanceSummary,
    SubstituteTeacher,
    TardyPolicy,
    TardyRecord,
)

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
    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "student",
            "classroom",
            "academic_year",
            "date",
            "status",
            "recorded_by",
            "recorded_at",
            "updated_by",
            "updated_at",
            "remarks",
        ]
        read_only_fields = ["id", "updated_at"]


class PeriodAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodAttendance
        fields = [
            "id",
            "student",
            "assignment",
            "date",
            "period_number",
            "status",
            "recorded_by",
            "recorded_at",
            "updated_by",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


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
        ]
        read_only_fields = ["id"]


class AttendanceChangeLogSerializer(serializers.ModelSerializer):
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
            "changed_at",
            "reason",
        ]
        read_only_fields = ["id"]


class AttendancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendancePolicy
        fields = [
            "id",
            "school",
            "name",
            "min_attendance_pct",
            "auto_fail_below",
            "notify_parent_below_pct",
            "notify_admin_below_pct",
            "edit_window_days",
            "reminder_time",
            "escalation_enabled",
            "escalation_after_minutes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ["id", "school", "name", "date", "holiday_type", "description", "academic_year", "created_at"]
        read_only_fields = ["id", "created_at"]


class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "student",
            "academic_year",
            "sick_leave_total",
            "sick_leave_used",
            "casual_leave_total",
            "casual_leave_used",
            "other_leave_total",
            "other_leave_used",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LeaveApprovalLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApprovalLevel
        fields = ["id", "leave", "level", "approver", "status", "remarks", "decided_at", "created_at"]
        read_only_fields = ["id", "created_at"]


class QRCodeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCodeSession
        fields = [
            "id",
            "classroom",
            "teacher",
            "date",
            "period_number",
            "qr_code",
            "secret_key",
            "is_active",
            "expires_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class QRCodeCheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCodeCheckin
        fields = ["id", "session", "student", "checked_in_at", "ip_address", "device_info"]
        read_only_fields = ["id"]


class SubstituteTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubstituteTeacher
        fields = [
            "id",
            "original_teacher",
            "substitute_teacher",
            "date",
            "period_number",
            "classroom",
            "subject",
            "reason",
            "is_auto_assigned",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AttendanceDataArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceDataArchive
        fields = [
            "id",
            "school",
            "academic_year",
            "archive_type",
            "data",
            "record_count",
            "date_from",
            "date_to",
            "archived_at",
            "is_purged",
        ]
        read_only_fields = ["id"]


class BiometricCheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricCheckin
        fields = [
            "id",
            "school",
            "id",
            "student",
            "biometric_type",
            "device_id",
            "status",
            "confidence_score",
            "latitude",
            "longitude",
            "checkin_time",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RFIDCheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFIDCheckin
        fields = [
            "id",
            "school",
            "id",
            "student",
            "card_number",
            "reader_id",
            "status",
            "location",
            "latitude",
            "longitude",
            "checkin_time",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class GPSAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSAttendance
        fields = [
            "id",
            "school",
            "id",
            "student",
            "latitude",
            "longitude",
            "accuracy_meters",
            "geofence_name",
            "geofence_radius",
            "distance_from_school",
            "status",
            "device_id",
            "device_type",
            "checkin_time",
        ]
        read_only_fields = ["id", "created_at"]


class ParentNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentNotification
        fields = [
            "id",
            "school",
            "id",
            "student",
            "notification_type",
            "channel",
            "title",
            "message",
            "parent_email",
            "parent_phone",
            "status",
            "sent_at",
            "delivered_at",
            "read_at",
        ]
        read_only_fields = ["id", "created_at"]


class AttendanceDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceDashboard
        fields = [
            "id",
            "school",
            "id",
            "dashboard_type",
            "title",
            "start_date",
            "end_date",
            "total_students",
            "average_attendance",
            "present_count",
            "absent_count",
            "late_count",
            "excused_count",
            "attendance_trend",
            "daily_breakdown",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ChronicAbsenceTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChronicAbsenceTracking
        fields = [
            "id",
            "school",
            "id",
            "student",
            "academic_year",
            "term",
            "total_days",
            "days_present",
            "days_absent",
            "days_late",
            "attendance_percentage",
            "absence_percentage",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AttendanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceReport
        fields = [
            "id",
            "school",
            "id",
            "report_type",
            "title",
            "description",
            "start_date",
            "end_date",
            "classroom",
            "student",
            "grade",
            "total_students",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BulkAttendanceImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkAttendanceImport
        fields = [
            "id",
            "school",
            "id",
            "file_name",
            "file_url",
            "status",
            "total_records",
            "successful_records",
            "failed_records",
            "error_log",
            "date_column",
            "student_column",
            "status_column",
            "overwrite_existing",
            "imported_by",
        ]
        read_only_fields = ["id", "created_at"]


class AttendanceCorrectionWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceCorrectionWorkflow
        fields = [
            "id",
            "school",
            "id",
            "correction_type",
            "attendance_record",
            "period_attendance",
            "old_status",
            "new_status",
            "old_time",
            "new_time",
            "reason",
            "supporting_document",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AttendanceHistoryViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceHistoryView
        fields = [
            "id",
            "id",
            "student",
            "academic_year",
            "term",
            "total_days",
            "days_present",
            "days_absent",
            "days_late",
            "days_excused",
            "attendance_percentage",
            "timeline_data",
            "monthly_trend",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AttendancePatternsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendancePatterns
        fields = [
            "id",
            "school",
            "id",
            "student",
            "academic_year",
            "pattern_type",
            "pattern_name",
            "description",
            "frequency",
            "percentage",
            "risk_level",
            "pattern_data",
            "affected_dates",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RealTimeDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealTimeDashboard
        fields = [
            "id",
            "school",
            "id",
            "scope",
            "scope_id",
            "total_expected",
            "total_present",
            "total_absent",
            "total_late",
            "total_excused",
            "total_early_departure",
            "attendance_percentage",
            "live_checkins",
            "recent_alerts",
            "last_refreshed",
        ]
        read_only_fields = ["id", "created_at"]


class AttendanceIncentiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceIncentive
        fields = [
            "id",
            "school",
            "id",
            "name",
            "incentive_type",
            "description",
            "required_streak_days",
            "required_percentage",
            "points_value",
            "is_active",
            "start_date",
            "end_date",
            "total_available",
            "total_awarded",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AttendanceIncentiveAwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceIncentiveAward
        fields = [
            "id",
            "id",
            "incentive",
            "student",
            "awarded_date",
            "awarded_by",
            "streak_days",
            "attendance_percentage",
            "notes",
            "points_earned",
            "total_points",
        ]
        read_only_fields = ["id"]


class AttendancePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendancePrediction
        fields = [
            "id",
            "school",
            "id",
            "student",
            "prediction_type",
            "risk_score",
            "prediction_date",
            "predicted_period_start",
            "predicted_period_end",
            "risk_factors",
            "historical_pattern",
            "recommended_action",
            "priority_level",
            "reviewed",
        ]
        read_only_fields = ["id", "created_at"]


class FieldTripSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldTrip
        fields = [
            "id",
            "school",
            "id",
            "title",
            "description",
            "destination",
            "status",
            "departure_date",
            "departure_time",
            "return_date",
            "return_time",
            "organizer",
            "chaperones",
            "eligible_grades",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FieldTripParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldTripParticipant
        fields = [
            "id",
            "id",
            "field_trip",
            "student",
            "consent_status",
            "attendance_status",
            "parent_contacted",
            "payment_status",
            "notes",
            "enrolled_at",
        ]
        read_only_fields = ["id"]


class AttendanceEscalationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceEscalation
        fields = [
            "id",
            "school",
            "id",
            "student",
            "escalation_level",
            "status",
            "trigger_reason",
            "absences_count",
            "tardies_count",
            "actions_taken",
            "assigned_to",
            "meeting_date",
            "meeting_notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AttendanceAlertConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceAlertConfig
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "absence_threshold",
            "tardy_threshold",
            "lookback_days",
            "consecutive_absences",
            "consecutive_count",
            "notify_parent",
            "notify_counselor",
            "notify_admin",
            "notify_teacher",
            "email_template",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TardyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = TardyPolicy
        fields = [
            "id",
            "school",
            "id",
            "name",
            "tardy_count",
            "consequence",
            "notify_parent",
            "detention_minutes",
            "in_school_suspension",
            "warning_only",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TardyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TardyRecord
        fields = [
            "id",
            "id",
            "student",
            "attendance_record",
            "tardy_date",
            "arrival_time",
            "minutes_late",
            "reason",
            "excuse",
            "policy_applied",
            "consequence",
            "status",
            "parent_notified",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EarlyDismissalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EarlyDismissal
        fields = [
            "id",
            "school",
            "id",
            "student",
            "requested_by",
            "reason_type",
            "status",
            "dismissal_date",
            "requested_departure_time",
            "actual_departure_time",
            "reason_detail",
            "pickup_person",
            "pickup_id_verified",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AttendanceMakeUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceMakeUp
        fields = [
            "id",
            "school",
            "id",
            "student",
            "original_absence",
            "status",
            "make_up_date",
            "start_time",
            "end_time",
            "location",
            "supervised_by",
            "reason",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AttendanceAuditEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceAuditEntry
        fields = [
            "id",
            "school",
            "id",
            "student",
            "change_type",
            "old_status",
            "new_status",
            "old_time",
            "new_time",
            "changed_by",
            "reason",
            "change_date",
            "change_timestamp",
        ]
        read_only_fields = ["id"]


class AttendanceConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceConfiguration
        fields = [
            "id",
            "school",
            "id",
            "attendance_mode",
            "check_in_method",
            "grace_period_minutes",
            "tardy_threshold_minutes",
            "absent_threshold_minutes",
            "early_departure_threshold_minutes",
            "auto_notify_absent",
            "auto_notify_tardy",
            "notify_after_minutes",
            "parent_portal_enabled",
            "parent_real_time_view",
            "auto_apply_holidays",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentAttendanceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendanceSummary
        fields = [
            "id",
            "school",
            "id",
            "student",
            "academic_year",
            "semester",
            "total_school_days",
            "days_present",
            "days_absent",
            "days_late",
            "days_excused",
            "days_early_departure",
            "attendance_percentage",
            "tardiness_rate",
        ]
        read_only_fields = ["id", "created_at"]


class AttendanceLockoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLockout
        fields = [
            "id",
            "school",
            "id",
            "lock_date",
            "period",
            "locked_by",
            "lock_reason",
            "is_locked",
            "locked_at",
            "unlocked_by",
            "unlocked_at",
            "unlock_reason",
        ]
        read_only_fields = ["id"]


class AttendanceCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceComment
        fields = [
            "id",
            "school",
            "id",
            "student",
            "author",
            "comment_type",
            "comment",
            "comment_date",
            "related_date",
            "is_visible_to_parent",
            "is_visible_to_student",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ── Serializers restored from original module (expansion regression fix) ──


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
