from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "academics_v1"
router = DefaultRouter()
router.register("subjects", views.SubjectViewSet, basename="subject")
router.register("assignments", views.TeacherAssignmentViewSet, basename="assignment")
router.register("teacher-profiles", views.TeacherProfileViewSet, basename="teacher-profile")
router.register("lesson-plans", views.LessonPlanViewSet, basename="lesson-plan")
router.register(
    "student-subject-enrollments",
    views.StudentSubjectEnrollmentViewSet,
    basename="student-subject-enrollment",
)
router.register(
    "curriculum-standards",
    views.CurriculumStandardViewSet,
    basename="curriculum-standard",
)
router.register(
    "subject-standard-mappings",
    views.SubjectStandardMappingViewSet,
    basename="subject-standard-mapping",
)
router.register(
    "syllabi",
    views.SyllabusViewSet,
    basename="syllabus",
)
router.register(
    "workload-config",
    views.TeacherWorkloadConfigViewSet,
    basename="workload-config",
)
router.register(
    "workload",
    views.TeacherWorkloadViewSet,
    basename="workload",
)
router.register(
    "evaluation-criteria",
    views.EvaluationCriteriaViewSet,
    basename="evaluation-criteria",
)
router.register(
    "evaluation-templates",
    views.EvaluationTemplateViewSet,
    basename="evaluation-template",
)
router.register(
    "evaluations",
    views.TeacherEvaluationViewSet,
    basename="evaluation",
)
router.register(
    "transcripts",
    views.AcademicTranscriptViewSet,
    basename="transcript",
)
# P1: Academic Calendar
router.register(
    "terms",
    views.AcademicTermViewSet,
    basename="term",
)
router.register(
    "events",
    views.AcademicEventViewSet,
    basename="event",
)
router.register(
    "holidays",
    views.AcademicHolidayViewSet,
    basename="holiday",
)
# P2: Assignment & Homework
router.register(
    "homework-assignments",
    views.AssignmentViewSet,
    basename="homework-assignment",
)
router.register(
    "submissions",
    views.AssignmentSubmissionViewSet,
    basename="submission",
)
router.register(
    "homework-tracker",
    views.HomeworkTrackerViewSet,
    basename="homework-tracker",
)
# P3: Exam Management
router.register(
    "question-bank",
    views.QuestionBankViewSet,
    basename="question-bank",
)
router.register(
    "exam-papers",
    views.ExamPaperViewSet,
    basename="exam-paper",
)
# P4: Notifications
router.register(
    "notifications",
    views.AcademicNotificationViewSet,
    basename="notification",
)
# P5: Analytics
router.register(
    "subject-performance",
    views.SubjectPerformanceViewSet,
    basename="subject-performance",
)
router.register(
    "student-progress",
    views.StudentProgressViewSet,
    basename="student-progress",
)
router.register(
    "teacher-effectiveness",
    views.TeacherEffectivenessViewSet,
    basename="teacher-effectiveness",
)

# Nested router for syllabus topics
syllabus_router = DefaultRouter()
syllabus_router.register("topics", views.SyllabusTopicViewSet, basename="syllabus-topic")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "syllabi/<uuid:syllabus_pk>/",
        include(syllabus_router.urls),
    ),
]
