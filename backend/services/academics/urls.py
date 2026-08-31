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
