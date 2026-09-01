"""URL Configuration for attendance."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceAlertConfigViewSet,
    AttendanceAuditEntryViewSet,
    AttendanceChangeLogViewSet,
    AttendanceCommentViewSet,
    AttendanceConfigurationViewSet,
    AttendanceCorrectionWorkflowViewSet,
    AttendanceDashboardViewSet,
    AttendanceDataArchiveViewSet,
    AttendanceEscalationViewSet,
    AttendanceHistoryViewViewSet,
    AttendanceIncentiveAwardViewSet,
    AttendanceIncentiveViewSet,
    AttendanceLeaveViewSet,
    AttendanceLockoutViewSet,
    AttendanceMakeUpViewSet,
    AttendancePatternsViewSet,
    AttendancePolicyViewSet,
    AttendancePredictionViewSet,
    AttendanceRecordViewSet,
    AttendanceReportViewSet,
    BiometricCheckinViewSet,
    BulkAttendanceImportViewSet,
    ChronicAbsenceTrackingViewSet,
    EarlyDismissalViewSet,
    FieldTripParticipantViewSet,
    FieldTripViewSet,
    GPSAttendanceViewSet,
    HolidayViewSet,
    LeaveApprovalLevelViewSet,
    LeaveBalanceViewSet,
    ParentNotificationViewSet,
    PeriodAttendanceViewSet,
    QRCodeCheckinViewSet,
    QRCodeSessionViewSet,
    RealTimeDashboardViewSet,
    RFIDCheckinViewSet,
    StudentAttendanceSummaryViewSet,
    SubstituteTeacherViewSet,
    TardyPolicyViewSet,
    TardyRecordViewSet,
)

app_name = "attendance_v1"

router = DefaultRouter()
router.register(r"attendance-record", AttendanceRecordViewSet, basename="attendance-record")
router.register(r"period-attendance", PeriodAttendanceViewSet, basename="period-attendance")
router.register(r"attendance-leave", AttendanceLeaveViewSet, basename="attendance-leave")
router.register(r"attendance-change-log", AttendanceChangeLogViewSet, basename="attendance-change-log")
router.register(r"attendance-policy", AttendancePolicyViewSet, basename="attendance-policy")
router.register(r"holiday", HolidayViewSet, basename="holiday")
router.register(r"leave-balance", LeaveBalanceViewSet, basename="leave-balance")
router.register(r"leave-approval-level", LeaveApprovalLevelViewSet, basename="leave-approval-level")
router.register(r"q-r-code-session", QRCodeSessionViewSet, basename="q-r-code-session")
router.register(r"q-r-code-checkin", QRCodeCheckinViewSet, basename="q-r-code-checkin")
router.register(r"substitute-teacher", SubstituteTeacherViewSet, basename="substitute-teacher")
router.register(r"attendance-data-archive", AttendanceDataArchiveViewSet, basename="attendance-data-archive")
router.register(r"biometric-checkin", BiometricCheckinViewSet, basename="biometric-checkin")
router.register(r"r-f-i-d-checkin", RFIDCheckinViewSet, basename="r-f-i-d-checkin")
router.register(r"g-p-s-attendance", GPSAttendanceViewSet, basename="g-p-s-attendance")
router.register(r"parent-notification", ParentNotificationViewSet, basename="parent-notification")
router.register(r"attendance-dashboard", AttendanceDashboardViewSet, basename="attendance-dashboard")
router.register(r"chronic-absence-tracking", ChronicAbsenceTrackingViewSet, basename="chronic-absence-tracking")
router.register(r"attendance-report", AttendanceReportViewSet, basename="attendance-report")
router.register(r"bulk-attendance-import", BulkAttendanceImportViewSet, basename="bulk-attendance-import")
router.register(
    r"attendance-correction-workflow", AttendanceCorrectionWorkflowViewSet, basename="attendance-correction-workflow"
)
router.register(r"attendance-history-view", AttendanceHistoryViewViewSet, basename="attendance-history-view")
router.register(r"attendance-patterns", AttendancePatternsViewSet, basename="attendance-patterns")
router.register(r"real-time-dashboard", RealTimeDashboardViewSet, basename="real-time-dashboard")
router.register(r"attendance-incentive", AttendanceIncentiveViewSet, basename="attendance-incentive")
router.register(r"attendance-incentive-award", AttendanceIncentiveAwardViewSet, basename="attendance-incentive-award")
router.register(r"attendance-prediction", AttendancePredictionViewSet, basename="attendance-prediction")
router.register(r"field-trip", FieldTripViewSet, basename="field-trip")
router.register(r"field-trip-participant", FieldTripParticipantViewSet, basename="field-trip-participant")
router.register(r"attendance-escalation", AttendanceEscalationViewSet, basename="attendance-escalation")
router.register(r"attendance-alert-config", AttendanceAlertConfigViewSet, basename="attendance-alert-config")
router.register(r"tardy-policy", TardyPolicyViewSet, basename="tardy-policy")
router.register(r"tardy-record", TardyRecordViewSet, basename="tardy-record")
router.register(r"early-dismissal", EarlyDismissalViewSet, basename="early-dismissal")
router.register(r"attendance-make-up", AttendanceMakeUpViewSet, basename="attendance-make-up")
router.register(r"attendance-audit-entry", AttendanceAuditEntryViewSet, basename="attendance-audit-entry")
router.register(r"attendance-configuration", AttendanceConfigurationViewSet, basename="attendance-configuration")
router.register(r"student-attendance-summary", StudentAttendanceSummaryViewSet, basename="student-attendance-summary")
router.register(r"attendance-lockout", AttendanceLockoutViewSet, basename="attendance-lockout")
router.register(r"attendance-comment", AttendanceCommentViewSet, basename="attendance-comment")

urlpatterns = [
    path("", include(router.urls)),
]
