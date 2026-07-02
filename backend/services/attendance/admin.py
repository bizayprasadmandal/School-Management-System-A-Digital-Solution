from django.contrib import admin
from .models import AttendanceRecord, AttendanceLeave, PeriodAttendance

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ["student", "date", "status", "classroom", "recorded_by", "notified_guardian"]
    list_filter = ["status", "date", "classroom__grade__school"]
    search_fields = ["student__admission_number", "student__user__first_name"]
    date_hierarchy = "date"

@admin.register(AttendanceLeave)
class AttendanceLeaveAdmin(admin.ModelAdmin):
    list_display = ["student", "leave_type", "from_date", "to_date", "status", "total_days"]
    list_filter = ["leave_type", "status"]
    search_fields = ["student__user__first_name", "student__admission_number"]
