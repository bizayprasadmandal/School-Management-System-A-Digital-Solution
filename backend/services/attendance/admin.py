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
        "period",
        "date",
        "status",
        "recorded_by",
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
        "total_days",
    ]
    list_filter = ["leave_type", "status"]
    search_fields = [
        "student__user__first_name",
        "student__admission_number",
    ]


@admin.register(AttendanceChangeLog)
class AttendanceChangeLogAdmin(admin.ModelAdmin):
    list_display = [
        "attendance_record",
        "old_status",
        "new_status",
        "changed_by",
        "reason",
        "created_at",
    ]
    list_filter = ["old_status", "new_status"]
    search_fields = ["reason"]
    date_hierarchy = "created_at"


@admin.register(AttendancePolicy)
class AttendancePolicyAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "name",
        "min_attendance_pct",
        "consecutive_absent_limit",
        "auto_notify_guardian",
    ]
    list_filter = ["auto_notify_guardian"]
    search_fields = ["name"]


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ["school", "name", "date", "end_date", "description"]
    list_filter = ["school"]
    search_fields = ["name"]
    date_hierarchy = "date"


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "academic_year",
        "leave_type",
        "total_days",
        "used_days",
        "remaining_days",
    ]
    list_filter = ["leave_type", "academic_year"]
    search_fields = ["student__user__first_name", "student__admission_number"]


@admin.register(LeaveApprovalLevel)
class LeaveApprovalLevelAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "level",
        "approver_role",
        "auto_approve_days",
    ]
    list_filter = ["level"]
    search_fields = ["approver_role"]


@admin.register(QRCodeSession)
class QRCodeSessionAdmin(admin.ModelAdmin):
    list_display = [
        "classroom",
        "period",
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
        "method",
    ]
    list_filter = ["method"]
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
        "archived_at",
        "record_count",
    ]
    list_filter = ["academic_year"]
    search_fields = ["school__name"]
