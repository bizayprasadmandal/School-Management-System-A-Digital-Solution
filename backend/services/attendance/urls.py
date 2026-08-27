from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "attendance_v1"
router = DefaultRouter()
# IMPORTANT: register "leaves" and "periods" BEFORE the empty-prefix viewset.
# DefaultRouter emits the detail route `^{pk}/$` for the empty-prefix viewset,
# which would otherwise swallow `/leaves/` or `/periods/` as a pk (GET -> 404).
router.register("leaves", views.AttendanceLeaveViewSet, basename="leave")
router.register("periods", views.PeriodAttendanceViewSet, basename="period-attendance")
router.register("changelogs", views.AttendanceChangeLogViewSet, basename="attendance-changelog")
router.register("", views.AttendanceViewSet, basename="attendance")

urlpatterns = [path("", include(router.urls))]
