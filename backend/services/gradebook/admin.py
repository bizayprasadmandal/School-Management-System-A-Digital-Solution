"""
Gradebook Service — Admin registration for all models.
"""

from django.contrib import admin

from .models import (
    Assessment,
    AssessmentSubmission,
    CategoryAssignment,
    CourseGradeCalculation,
    Exam,
    ExamSchedule,
    ExamType,
    ExtraCredit,
    ExtraCreditSubmission,
    GPACalculation,
    Grade,
    GradeChangeLog,
    GradeChangeProposal,
    GradeComment,
    GradeHistory,
    GradeNotification,
    GradingCategory,
    GradingScale,
    GradingScaleEntry,
    LatePenaltyRule,
    ReportCard,
    ReportCardComment,
    RubricAssessment,
    RubricCriterion,
    RubricLevel,
    RubricScore,
    RubricTemplate,
    Standard,
    StandardMasteryScale,
    StudentStandardGrade,
    Transcript,
    TranscriptEntry,
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


# Rubric-Based Grading


class RubricLevelInline(admin.TabularInline):
    model = RubricLevel
    extra = 1


class RubricCriterionInline(admin.TabularInline):
    model = RubricCriterion
    extra = 1
    show_change_link = True


@admin.register(RubricTemplate)
class RubricTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "subject", "is_active"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]
    inlines = [RubricCriterionInline]


@admin.register(RubricCriterion)
class RubricCriterionAdmin(admin.ModelAdmin):
    list_display = ["name", "template", "max_score", "order"]
    list_filter = ["template"]
    search_fields = ["name"]
    inlines = [RubricLevelInline]


@admin.register(RubricLevel)
class RubricLevelAdmin(admin.ModelAdmin):
    list_display = ["name", "criterion", "score", "order"]
    list_filter = ["criterion"]
    search_fields = ["name"]


@admin.register(RubricAssessment)
class RubricAssessmentAdmin(admin.ModelAdmin):
    list_display = ["student", "assessment", "rubric_template", "total_score", "graded_at"]
    list_filter = ["rubric_template"]
    search_fields = ["student__admission_number", "student__user__first_name"]


@admin.register(RubricScore)
class RubricScoreAdmin(admin.ModelAdmin):
    list_display = ["rubric_assessment", "criterion", "selected_level", "score"]
    list_filter = ["criterion"]


# Standards-Based Grading


@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "standard_type", "subject", "is_active"]
    list_filter = ["standard_type", "subject", "is_active"]
    search_fields = ["code", "name"]


@admin.register(StandardMasteryScale)
class StandardMasteryScaleAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_default"]
    list_filter = ["school", "is_default"]
    search_fields = ["name"]


@admin.register(StudentStandardGrade)
class StudentStandardGradeAdmin(admin.ModelAdmin):
    list_display = ["student", "standard", "mastery_level", "score", "graded_at"]
    list_filter = ["mastery_level", "academic_year"]
    search_fields = ["student__admission_number", "student__user__first_name", "standard__code"]


# Grading Categories


@admin.register(GradingCategory)
class GradingCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "weight", "subject", "academic_year", "is_active"]
    list_filter = ["subject", "is_active"]
    search_fields = ["name"]


@admin.register(CategoryAssignment)
class CategoryAssignmentAdmin(admin.ModelAdmin):
    list_display = ["assessment", "category", "created_at"]
    list_filter = ["category"]
    search_fields = ["assessment__title"]


# GPA Calculation


class CourseGradeCalculationInline(admin.TabularInline):
    model = CourseGradeCalculation
    extra = 0


@admin.register(GPACalculation)
class GPACalculationAdmin(admin.ModelAdmin):
    list_display = ["student", "academic_year", "gpa_type", "gpa_value", "class_rank", "calculated_at"]
    list_filter = ["gpa_type", "academic_year"]
    search_fields = ["student__admission_number", "student__user__first_name"]
    inlines = [CourseGradeCalculationInline]


@admin.register(CourseGradeCalculation)
class CourseGradeCalculationAdmin(admin.ModelAdmin):
    list_display = ["gpa_calculation", "subject", "grade_letter", "grade_points", "credits", "is_honors"]
    list_filter = ["is_honors", "is_pass_fail"]
    search_fields = ["subject__name"]


# Transcript


class TranscriptEntryInline(admin.TabularInline):
    model = TranscriptEntry
    extra = 0


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ["transcript_number", "student", "academic_year", "cumulative_gpa", "status", "issued_at"]
    list_filter = ["status", "academic_year"]
    search_fields = ["transcript_number", "student__admission_number", "student__user__first_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [TranscriptEntryInline]


@admin.register(TranscriptEntry)
class TranscriptEntryAdmin(admin.ModelAdmin):
    list_display = ["transcript", "subject", "grade_letter", "grade_points", "credits", "is_honors"]
    list_filter = ["academic_year", "is_honors"]
    search_fields = ["subject__name"]


# Grade Notifications


@admin.register(GradeNotification)
class GradeNotificationAdmin(admin.ModelAdmin):
    list_display = ["student", "notification_type", "channel", "status", "sent_at"]
    list_filter = ["notification_type", "channel", "status"]
    search_fields = ["student__admission_number", "student__user__first_name", "title"]
    date_hierarchy = "created_at"


# Grade History


@admin.register(GradeHistory)
class GradeHistoryAdmin(admin.ModelAdmin):
    list_display = ["student", "subject", "academic_year", "semester", "grade_letter", "percentage"]
    list_filter = ["academic_year", "semester"]
    search_fields = ["student__admission_number", "student__user__first_name", "subject__name"]


# Late Penalty Rules


@admin.register(LatePenaltyRule)
class LatePenaltyRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "penalty_type", "penalty_value", "max_penalty", "grace_period_hours", "is_active"]
    list_filter = ["penalty_type", "is_active"]
    search_fields = ["name"]


# Extra Credit


@admin.register(ExtraCredit)
class ExtraCreditAdmin(admin.ModelAdmin):
    list_display = ["title", "credit_type", "max_bonus_marks", "due_date"]
    list_filter = ["credit_type"]
    search_fields = ["title"]


@admin.register(ExtraCreditSubmission)
class ExtraCreditSubmissionAdmin(admin.ModelAdmin):
    list_display = ["extra_credit", "student", "bonus_marks_obtained", "submitted_at"]
    search_fields = ["student__admission_number", "student__user__first_name", "extra_credit__title"]


# Grade Comments


@admin.register(GradeComment)
class GradeCommentAdmin(admin.ModelAdmin):
    list_display = ["category", "comment_text", "grade_range_min", "grade_range_max", "is_active", "usage_count"]
    list_filter = ["category", "is_active"]
    search_fields = ["comment_text"]


@admin.register(ReportCardComment)
class ReportCardCommentAdmin(admin.ModelAdmin):
    list_display = ["report_card", "comment", "added_by", "added_at"]
    search_fields = ["report_card__student__admission_number", "comment__comment_text"]
