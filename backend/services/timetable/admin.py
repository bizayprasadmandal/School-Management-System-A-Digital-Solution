from django.contrib import admin
from .models import Period, TimetableSlot, SchoolEvent

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

    def get_subject(self, obj): return obj.assignment.subject.name
    get_subject.short_description = "Subject"

    def get_teacher(self, obj): return obj.assignment.teacher.full_name
    get_teacher.short_description = "Teacher"

@admin.register(SchoolEvent)
class SchoolEventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_type", "start_date", "end_date", "is_school_wide"]
    list_filter = ["event_type", "is_school_wide", "school"]
    search_fields = ["title"]
