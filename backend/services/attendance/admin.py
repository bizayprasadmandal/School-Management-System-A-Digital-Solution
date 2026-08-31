"""
Attendance Service — Admin registration for all models.
"""

from django.contrib import admin

from .models import (
    AttendanceChangeLog,
    AttendanceCorrectionWorkflow,
    AttendanceDashboard,
    AttendanceDataArchive,
    AttendanceHistoryView,
    AttendanceLeave,
    AttendancePatterns,
    AttendancePolicy,
    AttendanceRecord,
    AttendanceReport,
    BiometricCheckin,
    BulkAttendanceImport,
    ChronicAbsenceTracking,
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
    SubstituteTeacher,
)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "date",
        "status",
        "classroom",
        "recorded_by",
        "notified_guardian",
    ]
    list_filter = ["status", "date", "classroom__grade__school"]
    search_fields = [
        "student__admission_number",
        "student__user__first_name",
        "student__user__last_name",
    ]
    date_hierarchy = "date"


@admin.register(PeriodAttendance)
class PeriodAttendanceAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "assignment",
        "date",
        "period_number",
        "status",
    ]
    list_filter = ["status", "date"]
    search_fields = [
        "student__user__first_name",
        "student__admission_number",
    ]
    date_hierarchy = "date"


@admin.register(AttendanceLeave)
class AttendanceLeaveAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "leave_type",
        "from_date",
        "to_date",
        "status",
    ]
    list_filter = ["leave_type", "status"]
    search_fields = [
        "student__user__first_name",
        "student__admission_number",
    ]


@admin.register(AttendanceChangeLog)
class AttendanceChangeLogAdmin(admin.ModelAdmin):
    list_display = [
        "attendance_type",
        "attendance_id",
        "change_type",
        "changed_by",
        "changed_at",
    ]
    list_filter = ["attendance_type", "change_type"]
    search_fields = ["reason"]
    date_hierarchy = "changed_at"


@admin.register(AttendancePolicy)
class AttendancePolicyAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "name",
        "min_attendance_pct",
        "edit_window_days",
        "is_active",
    ]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ["school", "name", "date", "holiday_type", "description"]
    list_filter = ["school", "holiday_type"]
    search_fields = ["name"]
    date_hierarchy = "date"


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "academic_year",
        "sick_leave_total",
        "sick_leave_used",
        "casual_leave_total",
        "casual_leave_used",
    ]
    list_filter = ["academic_year"]
    search_fields = ["student__user__first_name", "student__admission_number"]


@admin.register(LeaveApprovalLevel)
class LeaveApprovalLevelAdmin(admin.ModelAdmin):
    list_display = [
        "leave",
        "level",
        "approver",
        "status",
        "decided_at",
    ]
    list_filter = ["status", "level"]
    search_fields = ["remarks"]


@admin.register(QRCodeSession)
class QRCodeSessionAdmin(admin.ModelAdmin):
    list_display = [
        "classroom",
        "teacher",
        "date",
        "expires_at",
        "is_active",
    ]
    list_filter = ["is_active", "date"]
    search_fields = ["classroom__name"]
    date_hierarchy = "date"


@admin.register(QRCodeCheckin)
class QRCodeCheckinAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "session",
        "checked_in_at",
    ]
    search_fields = ["student__user__first_name", "student__admission_number"]


@admin.register(SubstituteTeacher)
class SubstituteTeacherAdmin(admin.ModelAdmin):
    list_display = [
        "original_teacher",
        "substitute_teacher",
        "date",
        "classroom",
        "subject",
        "reason",
    ]
    list_filter = ["date"]
    search_fields = [
        "original_teacher__first_name",
        "substitute_teacher__first_name",
        "reason",
    ]
    date_hierarchy = "date"


@admin.register(AttendanceDataArchive)
class AttendanceDataArchiveAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "academic_year",
        "archive_type",
        "record_count",
        "archived_at",
    ]
    list_filter = ["archive_type"]
    search_fields = ["school__name"]


@admin.register(BiometricCheckin)
class BiometricCheckinAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "biometric_type",
        "status",
        "confidence_score",
        "checkin_time",
    ]
    list_filter = ["biometric_type", "status"]
    search_fields = ["student__admission_number", "student__user__first_name"]
    date_hierarchy = "checkin_time"


@admin.register(RFIDCheckin)
class RFIDCheckinAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "card_number",
        "location",
        "checkin_time",
    ]
    list_filter = ["status"]
    search_fields = ["student__admission_number", "card_number"]
    date_hierarchy = "checkin_time"


@admin.register(GPSAttendance)
class GPSAttendanceAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "latitude",
        "longitude",
        "status",
        "checkin_time",
    ]
    list_filter = ["status"]
    search_fields = ["student__admission_number", "student__user__first_name"]
    date_hierarchy = "checkin_time"


@admin.register(ParentNotification)
class ParentNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "notification_type",
        "channel",
        "sent_at",
        "status",
    ]
    list_filter = ["notification_type", "channel", "status"]
    search_fields = ["student__admission_number", "student__user__first_name"]
    date_hierarchy = "created_at"


@admin.register(AttendanceDashboard)
class AttendanceDashboardAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "dashboard_type",
        "title",
        "total_students",
        "present_count",
        "absent_count",
        "late_count",
    ]
    list_filter = ["dashboard_type"]
    date_hierarchy = "created_at"


@admin.register(ChronicAbsenceTracking)
class ChronicAbsenceTrackingAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "academic_year",
        "days_absent",
        "absence_percentage",
        "severity_level",
        "status",
    ]
    list_filter = ["severity_level", "status"]
    search_fields = ["student__admission_number", "student__user__first_name"]


@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "report_type",
        "title",
        "status",
        "generated_by",
    ]
    list_filter = ["report_type", "status"]
    search_fields = ["school__name", "title"]
    date_hierarchy = "created_at"


@admin.register(BulkAttendanceImport)
class BulkAttendanceImportAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "file_name",
        "status",
        "successful_records",
        "failed_records",
        "imported_by",
    ]
    list_filter = ["status"]
    search_fields = ["school__name", "file_name"]
    date_hierarchy = "created_at"


@admin.register(AttendanceCorrectionWorkflow)
class AttendanceCorrectionWorkflowAdmin(admin.ModelAdmin):
    list_display = [
        "correction_type",
        "requested_by",
        "old_status",
        "new_status",
        "status",
    ]
    list_filter = ["correction_type", "status"]
    search_fields = ["reason"]


@admin.register(AttendanceHistoryView)
class AttendanceHistoryViewAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "academic_year",
        "total_days",
        "days_present",
        "days_absent",
        "attendance_percentage",
    ]
    search_fields = ["student__admission_number", "student__user__first_name"]


@admin.register(AttendancePatterns)
class AttendancePatternsAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "academic_year",
        "pattern_type",
        "pattern_name",
        "risk_level",
    ]
    list_filter = ["pattern_type", "risk_level"]
    search_fields = ["student__admission_number", "student__user__first_name", "pattern_name"]


@admin.register(RealTimeDashboard)
class RealTimeDashboardAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "scope",
        "total_expected",
        "total_present",
        "total_absent",
        "attendance_percentage",
    ]
    list_filter = ["scope"]
    date_hierarchy = "created_at"
