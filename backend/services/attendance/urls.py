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


# ── Additional registrations (module expansion) ──
router.register(r"attendance-record", views.AttendanceRecordViewSet, basename="attendance-record")
router.register(r"leave-approval-level", views.LeaveApprovalLevelViewSet, basename="leave-approval-level")
router.register(r"q-r-code-checkin", views.QRCodeCheckinViewSet, basename="q-r-code-checkin")
router.register(r"attendance-incentive", views.AttendanceIncentiveViewSet, basename="attendance-incentive")
router.register(
    r"attendance-incentive-award", views.AttendanceIncentiveAwardViewSet, basename="attendance-incentive-award"
)
router.register(r"attendance-prediction", views.AttendancePredictionViewSet, basename="attendance-prediction")
router.register(r"field-trip", views.FieldTripViewSet, basename="field-trip")
router.register(r"field-trip-participant", views.FieldTripParticipantViewSet, basename="field-trip-participant")
router.register(r"attendance-escalation", views.AttendanceEscalationViewSet, basename="attendance-escalation")
router.register(r"attendance-alert-config", views.AttendanceAlertConfigViewSet, basename="attendance-alert-config")
router.register(r"tardy-policy", views.TardyPolicyViewSet, basename="tardy-policy")
router.register(r"tardy-record", views.TardyRecordViewSet, basename="tardy-record")
router.register(r"early-dismissal", views.EarlyDismissalViewSet, basename="early-dismissal")
router.register(r"attendance-make-up", views.AttendanceMakeUpViewSet, basename="attendance-make-up")
router.register(r"attendance-audit-entry", views.AttendanceAuditEntryViewSet, basename="attendance-audit-entry")
router.register(r"attendance-configuration", views.AttendanceConfigurationViewSet, basename="attendance-configuration")
router.register(
    r"student-attendance-summary", views.StudentAttendanceSummaryViewSet, basename="student-attendance-summary"
)
router.register(r"attendance-lockout", views.AttendanceLockoutViewSet, basename="attendance-lockout")
router.register(r"attendance-comment", views.AttendanceCommentViewSet, basename="attendance-comment")
# Empty-prefix viewset MUST be registered last so its `^{pk}/$` detail route
# doesn't swallow the named registrations above (GET -> 404).
router.register("", views.AttendanceViewSet, basename="attendance")

urlpatterns = [path("", include(router.urls))]
