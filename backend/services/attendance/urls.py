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
router.register("biometric", views.BiometricCheckinViewSet, basename="biometric-checkin")
router.register("rfid", views.RFIDCheckinViewSet, basename="rfid-checkin")
router.register("gps", views.GPSAttendanceViewSet, basename="gps-attendance")
router.register("parent-notifications", views.ParentNotificationViewSet, basename="parent-notification")
router.register("dashboard", views.AttendanceDashboardViewSet, basename="attendance-dashboard")
router.register("chronic-absence", views.ChronicAbsenceTrackingViewSet, basename="chronic-absence")
router.register("reports", views.AttendanceReportViewSet, basename="attendance-report")
router.register("bulk-import", views.BulkAttendanceImportViewSet, basename="bulk-import")
router.register("corrections", views.AttendanceCorrectionWorkflowViewSet, basename="attendance-correction")
router.register("history", views.AttendanceHistoryViewViewSet, basename="attendance-history")
router.register("patterns", views.AttendancePatternsViewSet, basename="attendance-patterns")
router.register("realtime", views.RealTimeDashboardViewSet, basename="realtime-dashboard")
router.register("", views.AttendanceViewSet, basename="attendance")

urlpatterns = [path("", include(router.urls))]
