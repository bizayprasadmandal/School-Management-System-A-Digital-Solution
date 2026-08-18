from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .public_views import PublicApplicationStatusView, PublicApplicationSubmitView, PublicIntakeListView
from .views import ApplicationDocumentViewSet, ApplicationReviewViewSet, ApplicationViewSet, EnrollmentIntakeViewSet

app_name = "admissions_v1"
router = DefaultRouter()
router.register(r"intakes", EnrollmentIntakeViewSet, basename="enrollment-intake")
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"documents", ApplicationDocumentViewSet, basename="application-document")
router.register(r"reviews", ApplicationReviewViewSet, basename="application-review")
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
