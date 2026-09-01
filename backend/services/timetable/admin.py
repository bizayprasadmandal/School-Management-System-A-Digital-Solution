from django.contrib import admin

from .models import (
    AcademicCalendar,
    CoCurricularSchedule,
    ConflictDetection,
    ExamSchedule,
    ExamScheduleEntry,
    Period,
    RoomBooking,
    SchoolClosure,
    SchoolEvent,
    SubstituteTeacher,
    TeacherPreference,
    TeacherTimetable,
    TimetableApproval,
    TimetableChange,
    TimetableReport,
    TimetableSlot,
    TimetableTemplate,
    TimetableTemplateSlot,
)


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ["name", "period_number", "start_time", "end_time", "is_break", "school"]
    list_filter = ["school", "is_break"]
    ordering = ["school", "period_number"]


@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ["classroom", "get_day", "period", "get_subject", "get_teacher", "academic_year"]
    list_filter = ["academic_year", "day_of_week", "classroom__grade__school"]

    def get_day(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week)

    get_day.short_description = "Day"

    def get_subject(self, obj):
        return obj.assignment.subject.name

    get_subject.short_description = "Subject"

    def get_teacher(self, obj):
        return obj.assignment.teacher.full_name

    get_teacher.short_description = "Teacher"


@admin.register(SchoolEvent)
class SchoolEventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_type", "start_date", "end_date", "is_school_wide"]
    list_filter = ["event_type", "is_school_wide", "school"]
    search_fields = ["title"]


@admin.register(TeacherTimetable)
class TeacherTimetableAdmin(admin.ModelAdmin):
    list_display = ["teacher", "subject", "classroom", "period", "day_of_week"]
    list_filter = ["day_of_week", "subject"]
    search_fields = ["teacher__username"]


@admin.register(SubstituteTeacher)
class SubstituteTeacherAdmin(admin.ModelAdmin):
    list_display = ["substitute_teacher", "original_teacher", "date", "status"]
    list_filter = ["status", "date"]
    search_fields = ["original_teacher__username", "substitute_teacher__username"]


@admin.register(ConflictDetection)
class ConflictDetectionAdmin(admin.ModelAdmin):
    list_display = ["conflict_type", "status", "created_at"]
    list_filter = ["conflict_type", "status"]


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ["title", "exam_type", "start_date", "end_date", "status"]
    list_filter = ["exam_type", "status"]
    search_fields = ["title"]


@admin.register(ExamScheduleEntry)
class ExamScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ["classroom", "subject", "exam_date", "start_time", "end_time"]
    list_filter = ["exam_date"]


@admin.register(AcademicCalendar)
class AcademicCalendarAdmin(admin.ModelAdmin):
    list_display = ["title", "calendar_type", "start_date", "end_date"]
    list_filter = ["calendar_type"]
    search_fields = ["title"]


@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ["room_name", "booking_type", "date", "start_time", "end_time", "status"]
    list_filter = ["booking_type", "status"]
    search_fields = ["room_name"]


@admin.register(TimetableTemplate)
class TimetableTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "periods_per_day", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(TimetableTemplateSlot)
class TimetableTemplateSlotAdmin(admin.ModelAdmin):
    list_display = ["template", "subject", "period", "day_of_week"]
    list_filter = ["day_of_week"]


@admin.register(TeacherPreference)
class TeacherPreferenceAdmin(admin.ModelAdmin):
    list_display = ["teacher", "preference_type", "day_of_week"]
    list_filter = ["preference_type", "day_of_week"]
    search_fields = ["teacher__username"]


@admin.register(TimetableApproval)
class TimetableApprovalAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "submitted_at", "approved_at"]
    list_filter = ["status"]
    search_fields = ["title"]


@admin.register(TimetableChange)
class TimetableChangeAdmin(admin.ModelAdmin):
    list_display = ["change_type", "effective_date", "notified"]
    list_filter = ["change_type", "notified"]


@admin.register(CoCurricularSchedule)
class CoCurricularScheduleAdmin(admin.ModelAdmin):
    list_display = ["activity_name", "activity_type", "day_of_week", "start_time", "end_time"]
    list_filter = ["activity_type", "day_of_week"]
    search_fields = ["activity_name"]


@admin.register(TimetableReport)
class TimetableReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "date_from", "date_to"]
    list_filter = ["report_type"]
    search_fields = ["title"]


@admin.register(SchoolClosure)
class SchoolClosureAdmin(admin.ModelAdmin):
    list_display = ["title", "closure_type", "date", "notified"]
    list_filter = ["closure_type"]
    search_fields = ["title"]
