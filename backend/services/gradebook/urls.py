from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "gradebook_v1"
router = DefaultRouter()

# Core gradebook endpoints
router.register("exams", views.ExamViewSet, basename="exam")
router.register("grades", views.GradeViewSet, basename="grade")
router.register("proposals", views.GradeChangeProposalViewSet, basename="grade-change-proposal")
router.register("assessments", views.AssessmentViewSet, basename="assessment")
router.register("submissions", views.AssessmentSubmissionViewSet, basename="submission")
router.register("report-cards", views.ReportCardViewSet, basename="report-card")

# Rubric-based grading
router.register("rubric-templates", views.RubricTemplateViewSet, basename="rubric-template")
router.register("rubric-criteria", views.RubricCriterionViewSet, basename="rubric-criterion")
router.register("rubric-levels", views.RubricLevelViewSet, basename="rubric-level")
router.register("rubric-assessments", views.RubricAssessmentViewSet, basename="rubric-assessment")

# Standards-based grading
router.register("standards", views.StandardViewSet, basename="standard")
router.register("mastery-scales", views.StandardMasteryScaleViewSet, basename="mastery-scale")
router.register("standard-grades", views.StudentStandardGradeViewSet, basename="standard-grade")

# Grading categories
router.register("grading-categories", views.GradingCategoryViewSet, basename="grading-category")
router.register("category-assignments", views.CategoryAssignmentViewSet, basename="category-assignment")

# GPA calculation
router.register("gpa-calculations", views.GPACalculationViewSet, basename="gpa-calculation")
router.register("course-grades", views.CourseGradeCalculationViewSet, basename="course-grade")

# Transcripts
router.register("transcripts", views.TranscriptViewSet, basename="transcript")
router.register("transcript-entries", views.TranscriptEntryViewSet, basename="transcript-entry")

# Grade notifications
router.register("notifications", views.GradeNotificationViewSet, basename="grade-notification")

# Grade history
router.register("grade-history", views.GradeHistoryViewSet, basename="grade-history")

# Late penalty rules
router.register("late-penalties", views.LatePenaltyRuleViewSet, basename="late-penalty")

# Extra credit
router.register("extra-credit", views.ExtraCreditViewSet, basename="extra-credit")
router.register("extra-credit-submissions", views.ExtraCreditSubmissionViewSet, basename="extra-credit-submission")

# Grade comments
router.register("comments", views.GradeCommentViewSet, basename="grade-comment")
router.register("report-card-comments", views.ReportCardCommentViewSet, basename="report-card-comment")

# Expanded: exam scheduling & grading config
router.register("exam-schedules", views.ExamScheduleViewSet, basename="exam-schedule")
router.register("exam-types", views.ExamTypeViewSet, basename="exam-type")
router.register("grading-scales", views.GradingScaleViewSet, basename="grading-scale")
router.register("grading-scale-entries", views.GradingScaleEntryViewSet, basename="grading-scale-entry")
router.register("grade-change-logs", views.GradeChangeLogViewSet, basename="grade-change-log")
router.register("rubric-scores", views.RubricScoreViewSet, basename="rubric-score")

urlpatterns = [path("", include(router.urls))]
