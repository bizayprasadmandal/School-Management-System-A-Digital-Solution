"""Hostel / Accommodation Management URL Configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CheckoutProcessViewSet,
    ComplaintManagementViewSet,
    EmergencyContactViewSet,
    HostelAllocationViewSet,
    HostelAttendanceViewSet,
    HostelFeedbackViewSet,
    HostelFeeViewSet,
    HostelNotificationViewSet,
    HostelReportViewSet,
    HostelRoomViewSet,
    HostelViewSet,
    HostelVisitorViewSet,
    InventoryManagementViewSet,
    LeaveManagementViewSet,
    MessAttendanceViewSet,
    MessManagementViewSet,
    RoomInspectionViewSet,
    RoomMaintenanceViewSet,
    RoomTransferViewSet,
)

app_name = "hostel_v1"

router = DefaultRouter()
router.register(r"hostels", HostelViewSet, basename="hostel")
router.register(r"rooms", HostelRoomViewSet, basename="room")
router.register(r"allocations", HostelAllocationViewSet, basename="allocation")
router.register(r"fees", HostelFeeViewSet, basename="fee")
router.register(r"visitors", HostelVisitorViewSet, basename="visitor")
router.register(r"maintenance", RoomMaintenanceViewSet, basename="maintenance")
router.register(r"attendance", HostelAttendanceViewSet, basename="hostel-attendance")
router.register(r"leaves", LeaveManagementViewSet, basename="leave")
router.register(r"mess", MessManagementViewSet, basename="mess")
router.register(r"mess-attendance", MessAttendanceViewSet, basename="mess-attendance")
router.register(r"complaints", ComplaintManagementViewSet, basename="complaint")
router.register(r"inspections", RoomInspectionViewSet, basename="inspection")
router.register(r"inventory", InventoryManagementViewSet, basename="inventory")
router.register(r"reports", HostelReportViewSet, basename="hostel-report")
router.register(r"emergency-contacts", EmergencyContactViewSet, basename="emergency-contact")
router.register(r"transfers", RoomTransferViewSet, basename="room-transfer")
router.register(r"checkouts", CheckoutProcessViewSet, basename="checkout")
router.register(r"notifications", HostelNotificationViewSet, basename="notification")
router.register(r"feedback", HostelFeedbackViewSet, basename="feedback")

urlpatterns = [
    path("", include(router.urls)),
]
