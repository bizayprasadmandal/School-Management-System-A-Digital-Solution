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

urlpatterns = [path("", include(router.urls))]
