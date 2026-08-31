"""
Academics Service — Admin registration for all models.
"""

from django.contrib import admin

from .models import (
    AcademicEvent,
    AcademicHoliday,
    AcademicNotification,
    AcademicTerm,
    AcademicTranscript,
    Assignment,
    AssignmentSubmission,
    AssignmentVersion,
    CourseCatalogEntry,
    CurriculumStandard,
    EnrollmentIntent,
    EvaluationComment,
    EvaluationCriteria,
    EvaluationScore,
    EvaluationTemplate,
    ExamPaper,
    HomeworkTracker,
    LessonPlan,
    LessonPlanVersion,
    QuestionBank,
    StudentProgressReport,
    StudentSubjectEnrollment,
    Subject,
    SubjectPerformance,
    SubjectStandardMapping,
    SubjectVersion,
    Syllabus,
    SyllabusTopic,
    TeacherAssignment,
    TeacherEffectiveness,
    TeacherEvaluation,
    TeacherProfile,
    TeacherWorkloadConfig,
    TeacherWorkloadSnapshot,
)

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "grade",
        "is_core",
        "is_elective",
        "max_marks",
        "pass_marks",
        "credit_hours",
        "is_active",
    ]
    list_filter = ["grade__school", "is_core", "is_elective", "is_active"]
    search_fields = ["name", "code"]
    list_editable = ["is_active"]


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "employee_id",
        "department",
        "qualification",
        "joining_date",
        "experience_years",
        "is_active",
    ]
    list_filter = ["school", "qualification", "department", "is_active"]
    search_fields = [
        "employee_id",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    def full_name(self, obj):
        return obj.user.full_name


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "teacher",
        "subject",
        "classroom",
        "academic_year",
        "is_primary",
    ]
    list_filter = ["academic_year", "is_primary"]
    search_fields = [
        "teacher__first_name",
        "teacher__last_name",
        "subject__name",
        "subject__code",
    ]


@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "topic",
        "date",
        "duration_minutes",
        "status",
    ]
    list_filter = ["status", "date"]
    search_fields = ["title", "topic"]


# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------


@admin.register(StudentSubjectEnrollment)
class StudentSubjectEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "subject",
        "academic_year",
        "status",
        "enrolled_date",
    ]
    list_filter = ["status", "academic_year"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
        "subject__name",
    ]


# ---------------------------------------------------------------------------
# Standards
# ---------------------------------------------------------------------------


@admin.register(CurriculumStandard)
class CurriculumStandardAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "framework",
        "grade",
        "subject",
        "domain",
        "is_active",
    ]
    list_filter = ["framework", "grade", "subject", "is_active"]
    search_fields = ["code", "name", "description", "domain"]


@admin.register(SubjectStandardMapping)
class SubjectStandardMappingAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "standard",
        "academic_year",
        "coverage_level",
        "mapped_by",
    ]
    list_filter = ["coverage_level", "academic_year"]
    search_fields = [
        "subject__name",
        "subject__code",
        "standard__code",
        "standard__name",
    ]


# ---------------------------------------------------------------------------
# Syllabus
# ---------------------------------------------------------------------------


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "subject",
        "academic_year",
        "term",
        "status",
        "created_by",
    ]
    list_filter = ["status", "term", "academic_year"]
    search_fields = ["title", "subject__name"]


@admin.register(SyllabusTopic)
class SyllabusTopicAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "title",
        "syllabus",
        "status",
        "estimated_hours",
    ]
    list_filter = ["status"]
    search_fields = ["title"]


# ---------------------------------------------------------------------------
# Workload
# ---------------------------------------------------------------------------


@admin.register(TeacherWorkloadConfig)
class TeacherWorkloadConfigAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "max_periods_per_week",
        "max_periods_per_day",
        "max_subjects",
        "max_classes",
        "warning_threshold_pct",
    ]
    list_filter = ["is_active"]


@admin.register(TeacherWorkloadSnapshot)
class TeacherWorkloadSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "teacher",
        "academic_year",
        "week_start_date",
        "total_periods",
        "utilization_pct",
        "is_overloaded",
    ]
    list_filter = ["is_overloaded", "is_underloaded"]
    search_fields = ["teacher__first_name", "teacher__last_name"]


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "max_score",
        "weight",
        "order",
        "is_active",
    ]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "description"]


@admin.register(EvaluationTemplate)
class EvaluationTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "eval_type", "is_active"]
    list_filter = ["eval_type", "is_active"]
    search_fields = ["name", "description"]
    filter_horizontal = ["criteria"]


@admin.register(TeacherEvaluation)
class TeacherEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "teacher",
        "academic_year",
        "status",
        "overall_score",
        "review_date",
    ]
    list_filter = ["status", "academic_year"]
    search_fields = [
        "title",
        "teacher__first_name",
        "teacher__last_name",
    ]


@admin.register(EvaluationScore)
class EvaluationScoreAdmin(admin.ModelAdmin):
    list_display = [
        "evaluation",
        "criterion",
        "score",
        "weighted_score",
        "scored_by",
    ]
    list_filter = ["criterion__category"]
    search_fields = ["criterion__name"]


@admin.register(EvaluationComment)
class EvaluationCommentAdmin(admin.ModelAdmin):
    list_display = [
        "evaluation",
        "comment_type",
        "author",
        "is_private",
        "created_at",
    ]
    list_filter = ["comment_type", "is_private"]
    search_fields = ["content"]


# ---------------------------------------------------------------------------
# Transcripts
# ---------------------------------------------------------------------------


@admin.register(AcademicTranscript)
class AcademicTranscriptAdmin(admin.ModelAdmin):
    list_display = [
        "transcript_number",
        "student",
        "academic_year",
        "status",
        "percentage",
        "gpa",
        "grade_letter",
    ]
    list_filter = ["status", "academic_year"]
    search_fields = [
        "transcript_number",
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
    ]


# ---------------------------------------------------------------------------
# Academic Calendar
# ---------------------------------------------------------------------------


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "academic_year",
        "term_type",
        "start_date",
        "end_date",
        "is_current",
    ]
    list_filter = ["term_type", "is_current", "academic_year"]
    search_fields = ["name"]


@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "event_type",
        "start_date",
        "end_date",
        "is_all_day",
        "is_published",
    ]
    list_filter = ["event_type", "is_all_day", "is_published"]
    search_fields = ["title", "description"]
    filter_horizontal = ["affected_grades", "affected_subjects"]


@admin.register(AcademicHoliday)
class AcademicHolidayAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "end_date", "holiday_type"]
    list_filter = ["holiday_type"]
    search_fields = ["name"]


# ---------------------------------------------------------------------------
# Assignments & Homework
# ---------------------------------------------------------------------------


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "assignment_type",
        "status",
        "due_date",
        "max_score",
        "created_by",
    ]
    list_filter = ["assignment_type", "status", "due_date"]
    search_fields = ["title", "description"]


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "assignment",
        "student",
        "status",
        "score",
        "is_late",
        "submitted_at",
    ]
    list_filter = ["status", "is_late"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "assignment__title",
    ]


@admin.register(HomeworkTracker)
class HomeworkTrackerAdmin(admin.ModelAdmin):
    list_display = [
        "classroom",
        "date",
        "subject",
        "teacher",
        "is_completed",
    ]
    list_filter = ["date", "is_completed"]
    search_fields = ["description"]


# ---------------------------------------------------------------------------
# Exam Management
# ---------------------------------------------------------------------------


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = [
        "question_type",
        "difficulty",
        "subject",
        "marks",
        "is_active",
        "usage_count",
    ]
    list_filter = ["question_type", "difficulty", "is_active"]
    search_fields = ["question_text"]


@admin.register(ExamPaper)
class ExamPaperAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "subject",
        "total_marks",
        "duration_minutes",
        "status",
        "created_by",
    ]
    list_filter = ["status"]
    search_fields = ["title"]


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


@admin.register(AcademicNotification)
class AcademicNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "notification_type",
        "priority",
        "recipient",
        "is_read",
        "created_at",
    ]
    list_filter = ["notification_type", "priority", "is_read"]
    search_fields = ["title", "message", "recipient__email"]


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


@admin.register(SubjectPerformance)
class SubjectPerformanceAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "academic_year",
        "total_students",
        "average_score",
        "pass_rate",
    ]
    list_filter = ["academic_year"]
    search_fields = ["subject__name", "subject__code"]


@admin.register(StudentProgressReport)
class StudentProgressReportAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "subject",
        "academic_year",
        "current_score",
        "trend",
        "score_change",
    ]
    list_filter = ["trend", "academic_year"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "subject__name",
    ]


@admin.register(TeacherEffectiveness)
class TeacherEffectivenessAdmin(admin.ModelAdmin):
    list_display = [
        "teacher",
        "subject",
        "academic_year",
        "effectiveness_score",
        "average_student_score",
        "pass_rate",
    ]
    list_filter = ["academic_year"]
    search_fields = [
        "teacher__first_name",
        "teacher__last_name",
        "subject__name",
    ]


# ---------------------------------------------------------------------------
# Versioning
# ---------------------------------------------------------------------------


@admin.register(SubjectVersion)
class SubjectVersionAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "version_number",
        "academic_year",
        "changed_by",
        "created_at",
    ]
    list_filter = ["academic_year"]
    search_fields = ["subject__name", "change_summary"]


@admin.register(LessonPlanVersion)
class LessonPlanVersionAdmin(admin.ModelAdmin):
    list_display = [
        "lesson_plan",
        "version_number",
        "changed_by",
        "created_at",
    ]
    search_fields = ["title", "change_summary"]


@admin.register(AssignmentVersion)
class AssignmentVersionAdmin(admin.ModelAdmin):
    list_display = [
        "assignment",
        "version_number",
        "changed_by",
        "created_at",
    ]
    search_fields = ["title", "change_summary"]


# ---------------------------------------------------------------------------
# Course Catalog
# ---------------------------------------------------------------------------


@admin.register(CourseCatalogEntry)
class CourseCatalogEntryAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "difficulty_level",
        "estimated_hours_per_week",
        "is_published",
        "view_count",
    ]
    list_filter = ["difficulty_level", "is_published"]
    search_fields = [
        "subject__name",
        "catalog_description",
    ]
    filter_horizontal = ["prerequisites", "co_requisites"]


@admin.register(EnrollmentIntent)
class EnrollmentIntentAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "catalog_entry",
        "academic_year",
        "status",
        "created_at",
    ]
    list_filter = ["status", "academic_year"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "catalog_entry__subject__name",
    ]
