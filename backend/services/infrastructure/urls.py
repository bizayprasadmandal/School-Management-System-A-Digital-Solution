"""Infrastructure URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"buildings", views.BuildingViewSet, basename="building")
router.register(r"rooms", views.RoomViewSet, basename="room")
router.register(r"room-allocations", views.RoomAllocationViewSet)
router.register(r"work-orders", views.WorkOrderViewSet, basename="work-order")
router.register(r"work-order-comments", views.WorkOrderCommentViewSet)
router.register(r"preventive-maintenance", views.PreventiveMaintenanceViewSet)
router.register(r"assets", views.AssetViewSet, basename="asset")
router.register(r"asset-assignments", views.AssetAssignmentViewSet)
router.register(r"asset-lifecycle", views.AssetLifecycleViewSet)
router.register(r"warranty-claims", views.WarrantyClaimViewSet)
router.register(r"space-reservations", views.SpaceReservationViewSet)
router.register(r"utility-tracker", views.UtilityTrackerViewSet)
router.register(r"safety-inspections", views.SafetyInspectionViewSet)
router.register(r"compliance-records", views.InfrastructureComplianceRecordViewSet)
router.register(r"vendor-contracts", views.VendorContractViewSet)
router.register(r"emergency-plans", views.InfrastructureEmergencyPlanViewSet)
router.register(r"reports", views.InfrastructureReportViewSet)


# ── Additional registrations (module expansion) ──
router.register(r"energy-meter", views.EnergyMeterViewSet, basename="energy-meter")
router.register(r"energy-reading", views.EnergyReadingViewSet, basename="energy-reading")
router.register(r"energy-alert", views.EnergyAlertViewSet, basename="energy-alert")
router.register(r"c-c-t-v-camera", views.CCTVCameraViewSet, basename="c-c-t-v-camera")
router.register(r"access-control-point", views.AccessControlPointViewSet, basename="access-control-point")
router.register(r"pest-control-inspection", views.PestControlInspectionViewSet, basename="pest-control-inspection")
router.register(r"pest-treatment", views.PestTreatmentViewSet, basename="pest-treatment")
router.register(
    r"waste-collection-schedule", views.WasteCollectionScheduleViewSet, basename="waste-collection-schedule"
)
router.register(r"green-initiative", views.GreenInitiativeViewSet, basename="green-initiative")
router.register(r"water-usage-record", views.WaterUsageRecordViewSet, basename="water-usage-record")
router.register(r"vendor-performance", views.VendorPerformanceViewSet, basename="vendor-performance")
router.register(r"building-inspection", views.BuildingInspectionViewSet, basename="building-inspection")
router.register(r"infrastructure-alert", views.InfrastructureAlertViewSet, basename="infrastructure-alert")
router.register(r"floor-plan", views.FloorPlanViewSet, basename="floor-plan")
router.register(r"room-equipment", views.RoomEquipmentViewSet, basename="room-equipment")
router.register(r"parking-lot", views.ParkingLotViewSet, basename="parking-lot")
router.register(r"parking-assignment", views.ParkingAssignmentViewSet, basename="parking-assignment")
router.register(r"lighting-schedule", views.LightingScheduleViewSet, basename="lighting-schedule")
router.register(
    r"maintenance-cost-tracking", views.MaintenanceCostTrackingViewSet, basename="maintenance-cost-tracking"
)
router.register(
    r"infrastructure-maintenance-request",
    views.InfrastructureMaintenanceRequestViewSet,
    basename="infrastructure-maintenance-request",
)

app_name = "infrastructure_v1"

urlpatterns = [
    path("", include(router.urls)),
]
