from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthRecordViewSet, NurseVisitViewSet, ImmunizationViewSet, MedicationLogViewSet

app_name = "health_v1"
router = DefaultRouter()
router.register(r"records", HealthRecordViewSet, basename="health-record")
router.register(r"visits", NurseVisitViewSet, basename="nurse-visit")
router.register(r"immunizations", ImmunizationViewSet, basename="immunization")
router.register(r"medication-logs", MedicationLogViewSet, basename="medication-log")
urlpatterns = [path("", include(router.urls))]
