"""Django Admin registrations for hostel."""

from django.contrib import admin

from .models import (
    CheckoutProcess,
    CommonAreaBooking,
    ComplaintManagement,
    EmergencyContact,
    Hostel,
    HostelAllocation,
    HostelAsset,
    HostelAssetTransfer,
    HostelAttendance,
    HostelAttendanceAlert,
    HostelEmergencyDrill,
    HostelEmergencyProtocol,
    HostelEvent,
    HostelEventParticipant,
    HostelFee,
    HostelFeedback,
    HostelFeePayment,
    HostelInspectionSchedule,
    HostelNotification,
    HostelReport,
    HostelRoom,
    HostelVisitor,
    InventoryManagement,
    LaundryService,
    LeaveManagement,
    MessAttendance,
    MessDietaryRequest,
    MessFeedback,
    MessManagement,
    MessMenuPlan,
    RoomInspection,
    RoomKey,
    RoomMaintenance,
    RoommateAssignment,
    RoommateMatchRequest,
    RoommatePreference,
    RoomTransfer,
    VisitorPass,
    WellnessCheck,
)


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(HostelFee)
class HostelFeeAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(HostelVisitor)
class HostelVisitorAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(RoomMaintenance)
class RoomMaintenanceAdmin(admin.ModelAdmin):
    list_display = ["id", "status"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(HostelAttendance)
class HostelAttendanceAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(LeaveManagement)
class LeaveManagementAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(MessManagement)
class MessManagementAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(MessAttendance)
class MessAttendanceAdmin(admin.ModelAdmin):
    list_display = ["id", "status"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ComplaintManagement)
class ComplaintManagementAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(RoomInspection)
class RoomInspectionAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(InventoryManagement)
class InventoryManagementAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(HostelReport)
class HostelReportAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(RoomTransfer)
class RoomTransferAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(CheckoutProcess)
class CheckoutProcessAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(HostelNotification)
class HostelNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(HostelFeedback)
class HostelFeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(RoommatePreference)
class RoommatePreferenceAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(RoommateAssignment)
class RoommateAssignmentAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(RoomKey)
class RoomKeyAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(LaundryService)
class LaundryServiceAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(CommonAreaBooking)
class CommonAreaBookingAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(WellnessCheck)
class WellnessCheckAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(VisitorPass)
class VisitorPassAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(RoommateMatchRequest)
class RoommateMatchRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(MessMenuPlan)
class MessMenuPlanAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(MessDietaryRequest)
class MessDietaryRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(HostelAsset)
class HostelAssetAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(HostelAssetTransfer)
class HostelAssetTransferAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(HostelEvent)
class HostelEventAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(HostelEventParticipant)
class HostelEventParticipantAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(HostelEmergencyProtocol)
class HostelEmergencyProtocolAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(HostelEmergencyDrill)
class HostelEmergencyDrillAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(HostelFeePayment)
class HostelFeePaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(HostelInspectionSchedule)
class HostelInspectionScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(MessFeedback)
class MessFeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(HostelAttendanceAlert)
class HostelAttendanceAlertAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]
