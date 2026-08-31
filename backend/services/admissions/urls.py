from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .public_views import PublicApplicationStatusView, PublicApplicationSubmitView, PublicIntakeListView
from .views import (
    AdmissionsEmailNotificationViewSet,
    AdmissionsPipelineViewSet,
    AdmissionsReportViewSet,
    AdmissionsSMSNotificationViewSet,
    ApplicationDocumentViewSet,
    ApplicationFeeViewSet,
    ApplicationReviewViewSet,
    ApplicationTemplateViewSet,
    ApplicationViewSet,
    BulkApplicationImportViewSet,
    EnrollmentConfirmationViewSet,
    EnrollmentIntakeViewSet,
    InterviewScheduleViewSet,
    MeritListEntryViewSet,
    MeritListViewSet,
    ReEnrollmentViewSet,
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
