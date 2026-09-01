"""Transportation Management URL Configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DailyTransportAttendanceViewSet,
    DriverViewSet,
    FuelLogViewSet,
    RouteStopViewSet,
    RouteViewSet,
    StudentRouteViewSet,
    TransportFeeViewSet,
    TransportIncidentReportViewSet,
    TransportNotificationViewSet,
    TransportReportViewSet,
    TripScheduleViewSet,
    VehicleDocumentViewSet,
    VehicleInspectionViewSet,
    VehicleInsuranceViewSet,
    VehicleMaintenanceViewSet,
    VehicleViewSet,
)

app_name = "transport_v1"

router = DefaultRouter()
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"drivers", DriverViewSet, basename="driver")
router.register(r"routes", RouteViewSet, basename="route")
router.register(r"route-stops", RouteStopViewSet, basename="route-stop")
router.register(r"student-routes", StudentRouteViewSet, basename="student-route")
router.register(r"maintenance", VehicleMaintenanceViewSet, basename="maintenance")
router.register(r"fees", TransportFeeViewSet, basename="transport-fee")
router.register(r"insurance", VehicleInsuranceViewSet, basename="vehicle-insurance")
router.register(r"attendance", DailyTransportAttendanceViewSet, basename="transport-attendance")
router.register(r"incidents", TransportIncidentReportViewSet, basename="transport-incident")
router.register(r"inspections", VehicleInspectionViewSet, basename="vehicle-inspection")
router.register(r"trips", TripScheduleViewSet, basename="trip-schedule")
router.register(r"fuel-logs", FuelLogViewSet, basename="fuel-log")
router.register(r"notifications", TransportNotificationViewSet, basename="transport-notification")
router.register(r"reports", TransportReportViewSet, basename="transport-report")
router.register(r"documents", VehicleDocumentViewSet, basename="vehicle-document")

urlpatterns = [
    path("", include(router.urls)),
]
