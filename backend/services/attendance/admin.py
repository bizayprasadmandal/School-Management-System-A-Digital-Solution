"""
Attendance Service — Admin registration for all models.
"""

from django.contrib import admin

from .models import (
    AttendanceChangeLog,
    AttendanceDataArchive,
    AttendanceLeave,
    AttendancePolicy,
    AttendanceRecord,
    Holiday,
    LeaveApprovalLevel,
    LeaveBalance,
    PeriodAttendance,
    QRCodeCheckin,
    QRCodeSession,
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
