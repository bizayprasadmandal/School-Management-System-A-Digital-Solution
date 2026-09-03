from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .public_views import PublicApplicationStatusView, PublicApplicationSubmitView, PublicIntakeListView
from .views import (
    AdmissionAgreementViewSet,
    AdmissionCommunicationLogViewSet,
    AdmissionDecisionViewSet,
    AdmissionDocumentChecklistViewSet,
    AdmissionDocumentVerificationViewSet,
    AdmissionFunnelSnapshotViewSet,
    AdmissionMarketingSourceViewSet,
    AdmissionPolicyViewSet,
    AdmissionPredictionModelViewSet,
    AdmissionReminderViewSet,
    AdmissionsEmailNotificationViewSet,
    AdmissionsPipelineViewSet,
    AdmissionsReportViewSet,
    AdmissionsSMSNotificationViewSet,
    AdmissionTrendAnalysisViewSet,
    AgreementSignatureViewSet,
    ApplicationDocumentViewSet,
    ApplicationFeeViewSet,
    ApplicationReviewViewSet,
    ApplicationTemplateViewSet,
    ApplicationTimelineEventViewSet,
    ApplicationViewSet,
    BulkApplicationImportViewSet,
    CampusVisitViewSet,
    EnrollmentConfirmationViewSet,
    EnrollmentIntakeViewSet,
    EntranceAssessmentViewSet,
    GradeLevelCapacityViewSet,
    InterviewScheduleViewSet,
    MeritListEntryViewSet,
    MeritListViewSet,
    OpenHouseEventViewSet,
    OpenHouseRegistrationViewSet,
    ReEnrollmentViewSet,
    ScholarshipApplicationViewSet,
    ScholarshipViewSet,
    SiblingGroupViewSet,
    SiblingRecordViewSet,
    TransferStudentViewSet,
    WaitlistManagementViewSet,
)

app_name = "admissions_v1"
router = DefaultRouter()
router.register(r"intakes", EnrollmentIntakeViewSet, basename="enrollment-intake")
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"documents", ApplicationDocumentViewSet, basename="application-document")
router.register(r"reviews", ApplicationReviewViewSet, basename="application-review")
router.register(r"fees", ApplicationFeeViewSet, basename="application-fee")
router.register(r"interviews", InterviewScheduleViewSet, basename="interview-schedule")
router.register(r"merit-lists", MeritListViewSet, basename="merit-list")
router.register(r"merit-entries", MeritListEntryViewSet, basename="merit-entry")
router.register(r"waitlist", WaitlistManagementViewSet, basename="waitlist-management")
router.register(r"enrollment-confirmations", EnrollmentConfirmationViewSet, basename="enrollment-confirmation")
router.register(r"reports", AdmissionsReportViewSet, basename="admissions-report")
router.register(r"email-notifications", AdmissionsEmailNotificationViewSet, basename="email-notification")
router.register(r"sms-notifications", AdmissionsSMSNotificationViewSet, basename="sms-notification")
router.register(r"re-enrollments", ReEnrollmentViewSet, basename="re-enrollment")
router.register(r"pipeline", AdmissionsPipelineViewSet, basename="admissions-pipeline")
router.register(r"templates", ApplicationTemplateViewSet, basename="application-template")
router.register(r"bulk-imports", BulkApplicationImportViewSet, basename="bulk-import")

# ── Additional registrations (module expansion) ──
router.register(r"application-timeline-event", ApplicationTimelineEventViewSet, basename="application-timeline-event")
router.register(r"entrance-assessment", EntranceAssessmentViewSet, basename="entrance-assessment")
router.register(r"campus-visit", CampusVisitViewSet, basename="campus-visit")
router.register(r"open-house-event", OpenHouseEventViewSet, basename="open-house-event")
router.register(r"open-house-registration", OpenHouseRegistrationViewSet, basename="open-house-registration")
router.register(r"scholarship", ScholarshipViewSet, basename="scholarship")
router.register(r"scholarship-application", ScholarshipApplicationViewSet, basename="scholarship-application")
router.register(r"admission-policy", AdmissionPolicyViewSet, basename="admission-policy")
router.register(r"admission-agreement", AdmissionAgreementViewSet, basename="admission-agreement")
router.register(r"agreement-signature", AgreementSignatureViewSet, basename="agreement-signature")
router.register(
    r"admission-communication-log", AdmissionCommunicationLogViewSet, basename="admission-communication-log"
)
router.register(r"admission-reminder", AdmissionReminderViewSet, basename="admission-reminder")
router.register(r"grade-level-capacity", GradeLevelCapacityViewSet, basename="grade-level-capacity")
router.register(r"admission-decision", AdmissionDecisionViewSet, basename="admission-decision")
router.register(r"transfer-student", TransferStudentViewSet, basename="transfer-student")
router.register(r"sibling-group", SiblingGroupViewSet, basename="sibling-group")
router.register(r"sibling-record", SiblingRecordViewSet, basename="sibling-record")
router.register(r"admission-funnel-snapshot", AdmissionFunnelSnapshotViewSet, basename="admission-funnel-snapshot")
router.register(
    r"admission-document-checklist", AdmissionDocumentChecklistViewSet, basename="admission-document-checklist"
)
router.register(
    r"admission-document-verification", AdmissionDocumentVerificationViewSet, basename="admission-document-verification"
)
router.register(r"admission-prediction-model", AdmissionPredictionModelViewSet, basename="admission-prediction-model")
router.register(r"admission-marketing-source", AdmissionMarketingSourceViewSet, basename="admission-marketing-source")
router.register(r"admission-trend-analysis", AdmissionTrendAnalysisViewSet, basename="admission-trend-analysis")

urlpatterns = [
    path("", include(router.urls)),
    # Public (unauthenticated) endpoints
    path("public/intakes/", PublicIntakeListView.as_view(), name="public-intakes"),
    path("public/apply/", PublicApplicationSubmitView.as_view(), name="public-apply"),
    path(
        "public/status/<str:application_number>/",
        PublicApplicationStatusView.as_view(),
        name="public-status",
    ),
]
