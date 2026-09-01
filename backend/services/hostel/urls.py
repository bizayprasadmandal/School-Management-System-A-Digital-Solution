"""URL Configuration for hostel."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CheckoutProcessViewSet,
    CommonAreaBookingViewSet,
    ComplaintManagementViewSet,
    EmergencyContactViewSet,
    HostelAllocationViewSet,
    HostelAssetTransferViewSet,
    HostelAssetViewSet,
    HostelAttendanceAlertViewSet,
    HostelAttendanceViewSet,
    HostelEmergencyDrillViewSet,
    HostelEmergencyProtocolViewSet,
    HostelEventParticipantViewSet,
    HostelEventViewSet,
    HostelFeedbackViewSet,
    HostelFeePaymentViewSet,
    HostelFeeViewSet,
    HostelInspectionScheduleViewSet,
    HostelNotificationViewSet,
    HostelReportViewSet,
    HostelRoomViewSet,
    HostelViewSet,
    HostelVisitorViewSet,
    InventoryManagementViewSet,
    LaundryServiceViewSet,
    LeaveManagementViewSet,
    MessAttendanceViewSet,
    MessDietaryRequestViewSet,
    MessFeedbackViewSet,
    MessManagementViewSet,
    MessMenuPlanViewSet,
    RoomInspectionViewSet,
    RoomKeyViewSet,
    RoomMaintenanceViewSet,
    RoommateAssignmentViewSet,
    RoommateMatchRequestViewSet,
    RoommatePreferenceViewSet,
    RoomTransferViewSet,
    VisitorPassViewSet,
    WellnessCheckViewSet,
)

app_name = "hostel_v1"

router = DefaultRouter()
router.register(r"hostel", HostelViewSet, basename="hostel")
router.register(r"hostel-room", HostelRoomViewSet, basename="hostel-room")
router.register(r"hostel-allocation", HostelAllocationViewSet, basename="hostel-allocation")
router.register(r"hostel-fee", HostelFeeViewSet, basename="hostel-fee")
router.register(r"hostel-visitor", HostelVisitorViewSet, basename="hostel-visitor")
router.register(r"room-maintenance", RoomMaintenanceViewSet, basename="room-maintenance")
router.register(r"hostel-attendance", HostelAttendanceViewSet, basename="hostel-attendance")
router.register(r"leave-management", LeaveManagementViewSet, basename="leave-management")
router.register(r"mess-management", MessManagementViewSet, basename="mess-management")
router.register(r"mess-attendance", MessAttendanceViewSet, basename="mess-attendance")
router.register(r"complaint-management", ComplaintManagementViewSet, basename="complaint-management")
router.register(r"room-inspection", RoomInspectionViewSet, basename="room-inspection")
router.register(r"inventory-management", InventoryManagementViewSet, basename="inventory-management")
router.register(r"hostel-report", HostelReportViewSet, basename="hostel-report")
router.register(r"emergency-contact", EmergencyContactViewSet, basename="emergency-contact")
router.register(r"room-transfer", RoomTransferViewSet, basename="room-transfer")
router.register(r"checkout-process", CheckoutProcessViewSet, basename="checkout-process")
router.register(r"hostel-notification", HostelNotificationViewSet, basename="hostel-notification")
router.register(r"hostel-feedback", HostelFeedbackViewSet, basename="hostel-feedback")
router.register(r"roommate-preference", RoommatePreferenceViewSet, basename="roommate-preference")
router.register(r"roommate-assignment", RoommateAssignmentViewSet, basename="roommate-assignment")
router.register(r"room-key", RoomKeyViewSet, basename="room-key")
router.register(r"laundry-service", LaundryServiceViewSet, basename="laundry-service")
router.register(r"common-area-booking", CommonAreaBookingViewSet, basename="common-area-booking")
router.register(r"wellness-check", WellnessCheckViewSet, basename="wellness-check")
router.register(r"visitor-pass", VisitorPassViewSet, basename="visitor-pass")
router.register(r"roommate-match-request", RoommateMatchRequestViewSet, basename="roommate-match-request")
router.register(r"mess-menu-plan", MessMenuPlanViewSet, basename="mess-menu-plan")
router.register(r"mess-dietary-request", MessDietaryRequestViewSet, basename="mess-dietary-request")
router.register(r"hostel-asset", HostelAssetViewSet, basename="hostel-asset")
router.register(r"hostel-asset-transfer", HostelAssetTransferViewSet, basename="hostel-asset-transfer")
router.register(r"hostel-event", HostelEventViewSet, basename="hostel-event")
router.register(r"hostel-event-participant", HostelEventParticipantViewSet, basename="hostel-event-participant")
router.register(r"hostel-emergency-protocol", HostelEmergencyProtocolViewSet, basename="hostel-emergency-protocol")
router.register(r"hostel-emergency-drill", HostelEmergencyDrillViewSet, basename="hostel-emergency-drill")
router.register(r"hostel-fee-payment", HostelFeePaymentViewSet, basename="hostel-fee-payment")
router.register(r"hostel-inspection-schedule", HostelInspectionScheduleViewSet, basename="hostel-inspection-schedule")
router.register(r"mess-feedback", MessFeedbackViewSet, basename="mess-feedback")
router.register(r"hostel-attendance-alert", HostelAttendanceAlertViewSet, basename="hostel-attendance-alert")

urlpatterns = [
    path("", include(router.urls)),
]
