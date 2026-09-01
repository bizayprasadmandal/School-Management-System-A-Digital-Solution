"""Hostel / Accommodation Management — Django Admin registrations."""

from django.contrib import admin

from .models import (
    CheckoutProcess,
    ComplaintManagement,
    EmergencyContact,
    Hostel,
    HostelAllocation,
    HostelAttendance,
    HostelFee,
    HostelFeedback,
    HostelNotification,
    HostelReport,
    HostelRoom,
    HostelVisitor,
    InventoryManagement,
    LeaveManagement,
    MessAttendance,
    MessManagement,
    RoomInspection,
    RoomMaintenance,
    RoomTransfer,
)


class HostelRoomInline(admin.TabularInline):
    model = HostelRoom
    extra = 1
    fields = ["room_number", "floor", "room_type", "capacity", "monthly_fee", "is_active"]


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "gender", "status", "warden", "total_floors"]
    list_filter = ["gender", "status", "school"]
    search_fields = ["name", "code", "address"]
    inlines = [HostelRoomInline]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = ["room_number", "hostel", "floor", "room_type", "capacity", "is_active"]
    list_filter = ["room_type", "is_active", "has_ac", "is_furnished"]
    search_fields = ["room_number", "hostel__name"]
    readonly_fields = ["id", "created_at"]


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ["student", "room", "status", "check_in_date", "check_out_date", "is_paid"]
    list_filter = ["status", "is_paid"]
    search_fields = ["student__user__full_name", "room__room_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(HostelFee)
class HostelFeeAdmin(admin.ModelAdmin):
    list_display = ["name", "hostel", "amount", "billing_cycle", "is_active"]
    list_filter = ["billing_cycle", "is_active"]
    search_fields = ["name", "hostel__name"]
    readonly_fields = ["id", "created_at"]


@admin.register(HostelVisitor)
class HostelVisitorAdmin(admin.ModelAdmin):
    list_display = ["visitor_name", "student_visited", "hostel", "in_time", "out_time"]
    list_filter = ["hostel"]
    search_fields = ["visitor_name", "phone"]
    readonly_fields = ["id", "created_at"]


@admin.register(RoomMaintenance)
class RoomMaintenanceAdmin(admin.ModelAdmin):
    list_display = ["room", "maintenance_type", "status", "priority", "reported_date", "completed_date"]
    list_filter = ["maintenance_type", "status", "priority"]
    search_fields = ["room__room_number", "description"]
    date_hierarchy = "reported_date"


@admin.register(HostelAttendance)
class HostelAttendanceAdmin(admin.ModelAdmin):
    list_display = ["allocation", "date", "status", "check_in_time", "check_out_time", "is_in_campus"]
    list_filter = ["status", "date"]
    search_fields = ["allocation__student__user__first_name"]
    date_hierarchy = "date"


@admin.register(LeaveManagement)
class LeaveManagementAdmin(admin.ModelAdmin):
    list_display = ["allocation", "leave_type", "status", "from_date", "to_date", "total_days"]
    list_filter = ["leave_type", "status"]
    search_fields = ["allocation__student__user__first_name", "reason"]
    date_hierarchy = "from_date"


@admin.register(MessManagement)
class MessManagementAdmin(admin.ModelAdmin):
    list_display = ["hostel", "date", "meal_type", "is_vegetarian", "cost_per_meal", "rating"]
    list_filter = ["meal_type", "is_vegetarian", "date"]
    search_fields = ["description"]
    date_hierarchy = "date"


@admin.register(MessAttendance)
class MessAttendanceAdmin(admin.ModelAdmin):
    list_display = ["mess_menu", "allocation", "status", "recorded_at"]
    list_filter = ["status"]
    search_fields = ["allocation__student__user__first_name"]


@admin.register(ComplaintManagement)
class ComplaintManagementAdmin(admin.ModelAdmin):
    list_display = ["title", "complaint_type", "status", "priority", "hostel", "created_at"]
    list_filter = ["complaint_type", "status", "priority"]
    search_fields = ["title", "description"]
    date_hierarchy = "created_at"


@admin.register(RoomInspection)
class RoomInspectionAdmin(admin.ModelAdmin):
    list_display = ["room", "inspection_type", "status", "scheduled_date", "cleanliness_rating", "has_issues"]
    list_filter = ["inspection_type", "status", "has_issues"]
    search_fields = ["room__room_number"]
    date_hierarchy = "scheduled_date"


@admin.register(InventoryManagement)
class InventoryManagementAdmin(admin.ModelAdmin):
    list_display = ["item_name", "item_category", "quantity", "status", "hostel", "asset_tag"]
    list_filter = ["item_category", "status"]
    search_fields = ["item_name", "asset_tag"]


@admin.register(HostelReport)
class HostelReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "status", "hostel", "period_start", "period_end"]
    list_filter = ["report_type", "status"]
    search_fields = ["title", "summary"]
    date_hierarchy = "created_at"


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_type", "phone_primary", "hostel", "is_available_24x7", "is_active"]
    list_filter = ["contact_type", "is_available_24x7", "is_active"]
    search_fields = ["name", "phone_primary"]


@admin.register(RoomTransfer)
class RoomTransferAdmin(admin.ModelAdmin):
    list_display = ["allocation", "from_room", "to_room", "status", "requested_date", "transfer_date"]
    list_filter = ["status"]
    search_fields = ["allocation__student__user__first_name", "reason"]
    date_hierarchy = "created_at"


@admin.register(CheckoutProcess)
class CheckoutProcessAdmin(admin.ModelAdmin):
    list_display = ["allocation", "status", "checkout_date", "room_inspected", "keys_returned", "pending_dues"]
    list_filter = ["status", "room_inspected", "keys_returned"]
    search_fields = ["allocation__student__user__first_name"]
    date_hierarchy = "checkout_date"


@admin.register(HostelNotification)
class HostelNotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "notification_type", "status", "hostel", "recipient_type", "is_priority", "sent_at"]
    list_filter = ["notification_type", "status", "is_priority"]
    search_fields = ["title", "message"]
    date_hierarchy = "created_at"


@admin.register(HostelFeedback)
class HostelFeedbackAdmin(admin.ModelAdmin):
    list_display = ["allocation", "feedback_type", "rating", "is_anonymous", "hostel", "created_at"]
    list_filter = ["feedback_type", "rating", "is_anonymous"]
    search_fields = ["comment", "suggestion"]
    date_hierarchy = "created_at"
