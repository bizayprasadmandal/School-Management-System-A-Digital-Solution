from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .academic_year_views import AcademicYearViewSet

app_name = "students_v1"

router = DefaultRouter()
router.register(r"",               views.StudentViewSet,     basename="student")
router.register(r"classrooms",     views.ClassroomViewSet,   basename="classroom")
router.register(r"grades",         views.GradeViewSet,       basename="grade")
router.register(r"academic-years", AcademicYearViewSet,      basename="academic-year")

urlpatterns = [path("", include(router.urls))]
