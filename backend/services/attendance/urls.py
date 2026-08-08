from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "attendance_v1"
router = DefaultRouter()
# IMPORTANT: register "leaves" BEFORE the empty-prefix viewset. DefaultRouter
# emits the detail route `^{pk}/$` for the empty-prefix viewset, which would
# otherwise swallow `/leaves/` as a pk (GET -> 404, POST -> 405).
router.register("leaves", views.AttendanceLeaveViewSet, basename="leave")
router.register("", views.AttendanceViewSet, basename="attendance")

urlpatterns = [path("", include(router.urls))]
