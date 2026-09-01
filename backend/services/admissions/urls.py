"""URL Configuration for admissions."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

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
router.register(r"enrollment-intake", EnrollmentIntakeViewSet, basename="enrollment-intake")
router.register(r"application", ApplicationViewSet, basename="application")
router.register(r"application-timeline-event", ApplicationTimelineEventViewSet, basename="application-timeline-event")
router.register(r"application-document", ApplicationDocumentViewSet, basename="application-document")
router.register(r"entrance-assessment", EntranceAssessmentViewSet, basename="entrance-assessment")
router.register(r"application-review", ApplicationReviewViewSet, basename="application-review")
router.register(r"application-fee", ApplicationFeeViewSet, basename="application-fee")
router.register(r"interview-schedule", InterviewScheduleViewSet, basename="interview-schedule")
router.register(r"merit-list", MeritListViewSet, basename="merit-list")
router.register(r"merit-list-entry", MeritListEntryViewSet, basename="merit-list-entry")
router.register(r"waitlist-management", WaitlistManagementViewSet, basename="waitlist-management")
router.register(r"enrollment-confirmation", EnrollmentConfirmationViewSet, basename="enrollment-confirmation")
router.register(r"admissions-report", AdmissionsReportViewSet, basename="admissions-report")
router.register(
    r"admissions-email-notification", AdmissionsEmailNotificationViewSet, basename="admissions-email-notification"
)
router.register(
    r"admissions-s-m-s-notification", AdmissionsSMSNotificationViewSet, basename="admissions-s-m-s-notification"
)
router.register(r"re-enrollment", ReEnrollmentViewSet, basename="re-enrollment")
router.register(r"admissions-pipeline", AdmissionsPipelineViewSet, basename="admissions-pipeline")
router.register(r"application-template", ApplicationTemplateViewSet, basename="application-template")
router.register(r"bulk-application-import", BulkApplicationImportViewSet, basename="bulk-application-import")
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
]
