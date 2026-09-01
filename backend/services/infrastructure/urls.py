"""Infrastructure URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"buildings", views.BuildingViewSet)
router.register(r"rooms", views.RoomViewSet)
router.register(r"room-allocations", views.RoomAllocationViewSet)
router.register(r"work-orders", views.WorkOrderViewSet)
router.register(r"work-order-comments", views.WorkOrderCommentViewSet)
router.register(r"preventive-maintenance", views.PreventiveMaintenanceViewSet)
router.register(r"assets", views.AssetViewSet)
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

urlpatterns = [
    path("", include(router.urls)),
]
