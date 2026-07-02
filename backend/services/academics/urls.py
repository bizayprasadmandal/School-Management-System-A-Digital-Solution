from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "academics_v1"
router = DefaultRouter()
router.register("subjects", views.SubjectViewSet, basename="subject")
router.register("assignments", views.TeacherAssignmentViewSet, basename="assignment")
router.register("teacher-profiles", views.TeacherProfileViewSet, basename="teacher-profile")
router.register("lesson-plans", views.LessonPlanViewSet, basename="lesson-plan")

urlpatterns = [path("", include(router.urls))]
