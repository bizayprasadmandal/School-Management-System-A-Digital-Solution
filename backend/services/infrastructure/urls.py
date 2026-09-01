"""URL Configuration for infrastructure."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccessControlPointViewSet,
    AssetAssignmentViewSet,
    AssetLifecycleViewSet,
    AssetViewSet,
    BuildingInspectionViewSet,
    BuildingViewSet,
    CCTVCameraViewSet,
    EnergyAlertViewSet,
    EnergyMeterViewSet,
    EnergyReadingViewSet,
    FloorPlanViewSet,
    GreenInitiativeViewSet,
    InfrastructureAlertViewSet,
    InfrastructureComplianceRecordViewSet,
    InfrastructureEmergencyPlanViewSet,
    InfrastructureMaintenanceRequestViewSet,
    InfrastructureReportViewSet,
    LightingScheduleViewSet,
    MaintenanceCostTrackingViewSet,
    ParkingAssignmentViewSet,
    ParkingLotViewSet,
    PestControlInspectionViewSet,
    PestTreatmentViewSet,
    PreventiveMaintenanceViewSet,
    RoomAllocationViewSet,
    RoomEquipmentViewSet,
    RoomViewSet,
    SafetyInspectionViewSet,
    SpaceReservationViewSet,
    UtilityTrackerViewSet,
    VendorContractViewSet,
    VendorPerformanceViewSet,
    WarrantyClaimViewSet,
    WasteCollectionScheduleViewSet,
    WaterUsageRecordViewSet,
    WorkOrderCommentViewSet,
    WorkOrderViewSet,
)

app_name = "infrastructure_v1"

router = DefaultRouter()
router.register(r"building", BuildingViewSet, basename="building")
router.register(r"room", RoomViewSet, basename="room")
router.register(r"room-allocation", RoomAllocationViewSet, basename="room-allocation")
router.register(r"work-order", WorkOrderViewSet, basename="work-order")
router.register(r"work-order-comment", WorkOrderCommentViewSet, basename="work-order-comment")
router.register(r"preventive-maintenance", PreventiveMaintenanceViewSet, basename="preventive-maintenance")
router.register(r"asset", AssetViewSet, basename="asset")
router.register(r"asset-assignment", AssetAssignmentViewSet, basename="asset-assignment")
router.register(r"asset-lifecycle", AssetLifecycleViewSet, basename="asset-lifecycle")
router.register(r"warranty-claim", WarrantyClaimViewSet, basename="warranty-claim")
router.register(r"space-reservation", SpaceReservationViewSet, basename="space-reservation")
router.register(r"utility-tracker", UtilityTrackerViewSet, basename="utility-tracker")
router.register(r"safety-inspection", SafetyInspectionViewSet, basename="safety-inspection")
router.register(
    r"infrastructure-compliance-record",
    InfrastructureComplianceRecordViewSet,
    basename="infrastructure-compliance-record",
)
router.register(r"vendor-contract", VendorContractViewSet, basename="vendor-contract")
router.register(
    r"infrastructure-emergency-plan", InfrastructureEmergencyPlanViewSet, basename="infrastructure-emergency-plan"
)
router.register(r"infrastructure-report", InfrastructureReportViewSet, basename="infrastructure-report")
router.register(r"energy-meter", EnergyMeterViewSet, basename="energy-meter")
router.register(r"energy-reading", EnergyReadingViewSet, basename="energy-reading")
router.register(r"energy-alert", EnergyAlertViewSet, basename="energy-alert")
router.register(r"c-c-t-v-camera", CCTVCameraViewSet, basename="c-c-t-v-camera")
router.register(r"access-control-point", AccessControlPointViewSet, basename="access-control-point")
router.register(r"pest-control-inspection", PestControlInspectionViewSet, basename="pest-control-inspection")
router.register(r"pest-treatment", PestTreatmentViewSet, basename="pest-treatment")
router.register(r"waste-collection-schedule", WasteCollectionScheduleViewSet, basename="waste-collection-schedule")
router.register(r"green-initiative", GreenInitiativeViewSet, basename="green-initiative")
router.register(r"water-usage-record", WaterUsageRecordViewSet, basename="water-usage-record")
router.register(r"vendor-performance", VendorPerformanceViewSet, basename="vendor-performance")
router.register(r"building-inspection", BuildingInspectionViewSet, basename="building-inspection")
router.register(r"infrastructure-alert", InfrastructureAlertViewSet, basename="infrastructure-alert")
router.register(r"floor-plan", FloorPlanViewSet, basename="floor-plan")
router.register(r"room-equipment", RoomEquipmentViewSet, basename="room-equipment")
router.register(r"parking-lot", ParkingLotViewSet, basename="parking-lot")
router.register(r"parking-assignment", ParkingAssignmentViewSet, basename="parking-assignment")
router.register(r"lighting-schedule", LightingScheduleViewSet, basename="lighting-schedule")
router.register(r"maintenance-cost-tracking", MaintenanceCostTrackingViewSet, basename="maintenance-cost-tracking")
router.register(
    r"infrastructure-maintenance-request",
    InfrastructureMaintenanceRequestViewSet,
    basename="infrastructure-maintenance-request",
)

urlpatterns = [
    path("", include(router.urls)),
]
