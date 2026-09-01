"""Serializers for attendance."""

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


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "student",
            "on_delete",
            "classroom",
            "on_delete",
            "academic_year",
            "on_delete",
            "date",
            "status",
            "recorded_by",
            "on_delete",
            "recorded_at",
            "updated_by",
            "on_delete",
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
            "on_delete",
            "assignment",
            "on_delete",
            "date",
            "period_number",
            "status",
            "recorded_by",
            "on_delete",
            "recorded_at",
            "updated_by",
            "on_delete",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class AttendanceLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLeave
        fields = [
            "id",
            "student",
            "on_delete",
            "leave_type",
            "from_date",
            "to_date",
            "reason",
            "supporting_document",
            "status",
            "reviewed_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
        fields = [
            "id",
            "school",
            "on_delete",
            "name",
            "date",
            "holiday_type",
            "description",
            "academic_year",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "student",
            "on_delete",
            "academic_year",
            "on_delete",
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
        fields = [
            "id",
            "leave",
            "on_delete",
            "level",
            "approver",
            "on_delete",
            "status",
            "remarks",
            "decided_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class QRCodeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCodeSession
        fields = [
            "id",
            "classroom",
            "on_delete",
            "teacher",
            "on_delete",
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
        fields = ["id", "session", "on_delete", "student", "on_delete", "checked_in_at", "ip_address", "device_info"]
        read_only_fields = ["id"]


class SubstituteTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubstituteTeacher
        fields = [
            "id",
            "original_teacher",
            "on_delete",
            "substitute_teacher",
            "on_delete",
            "date",
            "period_number",
            "classroom",
            "on_delete",
            "subject",
            "on_delete",
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
            "on_delete",
            "academic_year",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "academic_year",
            "on_delete",
            "term",
            "on_delete",
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
            "on_delete",
            "report_type",
            "title",
            "description",
            "start_date",
            "end_date",
            "classroom",
            "on_delete",
            "student",
            "on_delete",
            "grade",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "correction_type",
            "attendance_record",
            "on_delete",
            "period_attendance",
            "on_delete",
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
            "on_delete",
            "academic_year",
            "on_delete",
            "term",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "academic_year",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "awarded_date",
            "awarded_by",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "title",
            "description",
            "destination",
            "status",
            "departure_date",
            "departure_time",
            "return_date",
            "return_time",
            "organizer",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "escalation_level",
            "status",
            "trigger_reason",
            "absences_count",
            "tardies_count",
            "actions_taken",
            "assigned_to",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "attendance_record",
            "on_delete",
            "tardy_date",
            "arrival_time",
            "minutes_late",
            "reason",
            "excuse",
            "policy_applied",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "requested_by",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "original_absence",
            "on_delete",
            "status",
            "make_up_date",
            "start_time",
            "end_time",
            "location",
            "supervised_by",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "change_type",
            "old_status",
            "new_status",
            "old_time",
            "new_time",
            "changed_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "lock_date",
            "period",
            "locked_by",
            "on_delete",
            "lock_reason",
            "is_locked",
            "locked_at",
            "unlocked_by",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "author",
            "on_delete",
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
