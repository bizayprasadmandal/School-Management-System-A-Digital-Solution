from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "attendance_v1"
router = DefaultRouter()
# IMPORTANT: register specific paths BEFORE the empty-prefix viewset.
# DefaultRouter emits the detail route `^{pk}/$` for the empty-prefix viewset,
# which would otherwise swallow named paths as a pk (GET -> 404).
router.register("leaves", views.AttendanceLeaveViewSet, basename="leave")
router.register("periods", views.PeriodAttendanceViewSet, basename="period-attendance")
router.register("changelogs", views.AttendanceChangeLogViewSet, basename="attendance-changelog")
router.register("policies", views.AttendancePolicyViewSet, basename="attendance-policy")
router.register("holidays", views.HolidayViewSet, basename="holiday")
router.register("leave-balances", views.LeaveBalanceViewSet, basename="leave-balance")
router.register("qr-sessions", views.QRCodeSessionViewSet, basename="qr-session")
router.register("substitutes", views.SubstituteTeacherViewSet, basename="substitute")
router.register("archives", views.AttendanceDataArchiveViewSet, basename="attendance-archive")
router.register("", views.AttendanceViewSet, basename="attendance")

urlpatterns = [path("", include(router.urls))]
