"""Transportation Management URL Configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BusTrackingViewSet,
    DailyTransportAttendanceViewSet,
    DriverLicenseViewSet,
    DriverPerformanceViewSet,
    DriverViewSet,
    FuelLogViewSet,
    GeofenceAlertViewSet,
    GeofenceZoneViewSet,
    ParentTransportAccessViewSet,
    RouteOptimizationViewSet,
    RouteStopViewSet,
    RouteViewSet,
    StopETAViewSet,
    StudentRouteViewSet,
    StudentTransportProfileViewSet,
    TransportAlertViewSet,
    TransportationDailyReportViewSet,
    TransportAuditLogViewSet,
    TransportBudgetViewSet,
    TransportComplianceRecordViewSet,
    TransportDriverScheduleViewSet,
    TransportEmergencyContactViewSet,
    TransportFeeStructureViewSet,
    TransportFeeViewSet,
    TransportIncidentReportViewSet,
    TransportIncidentViewSet,
    TransportMonthlyReportViewSet,
    TransportNotificationViewSet,
    TransportReportViewSet,
    TransportScheduleViewSet,
    TripScheduleViewSet,
    VehicleAssignmentLogViewSet,
    VehicleConditionReportViewSet,
    VehicleDocumentViewSet,
    VehicleGPSLogViewSet,
    VehicleInspectionViewSet,
    VehicleInsuranceViewSet,
    VehicleMaintenanceViewSet,
    VehiclePoolViewSet,
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


# ── Additional registrations (module expansion) ──
router.register(r"vehicle-g-p-s-log", VehicleGPSLogViewSet, basename="vehicle-g-p-s-log")
router.register(r"geofence-zone", GeofenceZoneViewSet, basename="geofence-zone")
router.register(r"geofence-alert", GeofenceAlertViewSet, basename="geofence-alert")
router.register(r"bus-tracking", BusTrackingViewSet, basename="bus-tracking")
router.register(r"stop-e-t-a", StopETAViewSet, basename="stop-e-t-a")
router.register(r"driver-license", DriverLicenseViewSet, basename="driver-license")
router.register(r"driver-performance", DriverPerformanceViewSet, basename="driver-performance")
router.register(r"vehicle-condition-report", VehicleConditionReportViewSet, basename="vehicle-condition-report")
router.register(r"route-optimization", RouteOptimizationViewSet, basename="route-optimization")
router.register(
    r"transportation-daily-report", TransportationDailyReportViewSet, basename="transportation-daily-report"
)
router.register(r"parent-transport-access", ParentTransportAccessViewSet, basename="parent-transport-access")
router.register(
    r"transport-compliance-record", TransportComplianceRecordViewSet, basename="transport-compliance-record"
)
router.register(r"student-transport-profile", StudentTransportProfileViewSet, basename="student-transport-profile")
router.register(r"transport-alert", TransportAlertViewSet, basename="transport-alert")
router.register(r"vehicle-pool", VehiclePoolViewSet, basename="vehicle-pool")
router.register(r"transport-schedule", TransportScheduleViewSet, basename="transport-schedule")
router.register(r"transport-fee-structure", TransportFeeStructureViewSet, basename="transport-fee-structure")
router.register(r"transport-incident", TransportIncidentViewSet, basename="transport-incident-v2")
router.register(r"transport-budget", TransportBudgetViewSet, basename="transport-budget")
router.register(r"transport-audit-log", TransportAuditLogViewSet, basename="transport-audit-log")
router.register(r"transport-monthly-report", TransportMonthlyReportViewSet, basename="transport-monthly-report")
router.register(
    r"transport-emergency-contact", TransportEmergencyContactViewSet, basename="transport-emergency-contact"
)
router.register(r"vehicle-assignment-log", VehicleAssignmentLogViewSet, basename="vehicle-assignment-log")
router.register(r"transport-driver-schedule", TransportDriverScheduleViewSet, basename="transport-driver-schedule")

urlpatterns = [
    path("", include(router.urls)),
]
