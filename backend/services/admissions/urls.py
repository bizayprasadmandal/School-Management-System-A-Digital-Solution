from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnrollmentIntakeViewSet, ApplicationViewSet, ApplicationDocumentViewSet, ApplicationReviewViewSet
app_name = "admissions_v1"
router = DefaultRouter()
router.register(r"intakes", EnrollmentIntakeViewSet, basename="enrollment-intake")
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"documents", ApplicationDocumentViewSet, basename="application-document")
router.register(r"reviews", ApplicationReviewViewSet, basename="application-review")
urlpatterns = [path("", include(router.urls))]
