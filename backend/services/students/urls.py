from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .academic_year_views import AcademicYearViewSet

app_name = "students_v1"

router = DefaultRouter()

# Specific sub-resources MUST be registered BEFORE the empty prefix catch-all.
# When StudentViewSet is at r"", its detail regex ^(?P<pk>[^/.]+)/$ will
# greedily match any non-slash segment (e.g. "classrooms") as a primary-key
# lookup, returning 404 instead of routing to the correct ViewSet.
router.register(r"classrooms",     views.ClassroomViewSet,   basename="classroom")
router.register(r"grades",         views.GradeViewSet,       basename="grade")
router.register(r"academic-years", AcademicYearViewSet,      basename="academic-year")
router.register(r"",               views.StudentViewSet,     basename="student")

urlpatterns = [path("", include(router.urls))]
