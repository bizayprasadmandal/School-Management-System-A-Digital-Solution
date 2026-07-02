from django.contrib import admin
from .models import Exam, ExamSchedule, Grade, ReportCard, GradingScale, GradingScaleEntry, ExamType, Assessment

class GradingScaleEntryInline(admin.TabularInline):
    model = GradingScaleEntry
    extra = 1

@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_default"]
    inlines = [GradingScaleEntryInline]

@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "weightage", "is_terminal"]

class ExamScheduleInline(admin.TabularInline):
    model = ExamSchedule
    extra = 0

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "exam_type", "start_date", "end_date", "status"]
    list_filter = ["status", "school", "academic_year"]
    search_fields = ["name"]
    inlines = [ExamScheduleInline]

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["student", "exam_schedule", "marks_obtained", "is_absent", "graded_at"]
    list_filter = ["is_absent", "exam_schedule__exam"]
    search_fields = ["student__admission_number"]

@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ["student", "exam", "percentage", "grade_letter", "rank_in_class", "status"]
    list_filter = ["status", "exam"]
    search_fields = ["student__admission_number", "student__user__first_name"]
    readonly_fields = ["id", "generated_at", "published_at"]

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ["title", "assessment_type", "due_date", "max_marks"]
    list_filter = ["assessment_type"]
