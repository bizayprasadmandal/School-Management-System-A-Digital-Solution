"""
Gradebook Service — Admin registration for all models.
"""

from django.contrib import admin

from .models import (
    Assessment,
    AssessmentSubmission,
    Exam,
    ExamSchedule,
    ExamType,
    Grade,
    GradeChangeLog,
    GradeChangeProposal,
    GradingScale,
    GradingScaleEntry,
    ReportCard,
)


class GradingScaleEntryInline(admin.TabularInline):
    model = GradingScaleEntry
    extra = 1


@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_default"]
    list_filter = ["school", "is_default"]
    search_fields = ["name"]
    inlines = [GradingScaleEntryInline]


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "weightage", "is_terminal"]
    list_filter = ["school", "is_terminal"]
    search_fields = ["name"]


class ExamScheduleInline(admin.TabularInline):
    model = ExamSchedule
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "school",
        "exam_type",
        "academic_year",
        "start_date",
        "end_date",
        "status",
    ]
    list_filter = ["status", "school", "academic_year"]
    search_fields = ["name"]
    inlines = [ExamScheduleInline]


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "exam",
        "subject",
        "classroom",
        "date",
        "start_time",
        "end_time",
        "max_marks",
    ]
    list_filter = ["date", "exam"]
    search_fields = ["subject__name", "classroom__name"]


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "exam_schedule",
        "marks_obtained",
        "is_absent",
        "graded_at",
    ]
    list_filter = ["is_absent", "exam_schedule__exam"]
    search_fields = [
        "student__admission_number",
        "student__user__first_name",
    ]


@admin.register(GradeChangeLog)
class GradeChangeLogAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "exam_schedule",
        "action",
        "marks_obtained_old",
        "marks_obtained_new",
        "changed_by",
        "changed_at",
    ]
    list_filter = ["action"]
    search_fields = ["remarks_old", "remarks_new"]
    date_hierarchy = "changed_at"


@admin.register(GradeChangeProposal)
class GradeChangeProposalAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "exam_schedule",
        "action",
        "status",
        "proposed_by",
        "proposed_at",
    ]
    list_filter = ["status", "action"]
    search_fields = ["reason"]
    date_hierarchy = "proposed_at"


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "exam",
        "percentage",
        "grade_letter",
        "rank_in_class",
        "status",
    ]
    list_filter = ["status", "exam"]
    search_fields = [
        "student__admission_number",
        "student__user__first_name",
    ]
    readonly_fields = ["id", "generated_at", "published_at"]


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "assessment_type",
        "due_date",
        "max_marks",
    ]
    list_filter = ["assessment_type"]
    search_fields = ["title"]


@admin.register(AssessmentSubmission)
class AssessmentSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "assessment",
        "student",
        "submitted_at",
    ]
    search_fields = [
        "student__user__first_name",
        "student__admission_number",
        "assessment__title",
    ]
