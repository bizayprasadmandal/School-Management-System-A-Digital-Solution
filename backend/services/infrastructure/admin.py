"""Infrastructure admin configuration."""

from django.contrib import admin

from .models import (
    Asset,
    AssetAssignment,
    AssetLifecycle,
    Building,
    InfrastructureComplianceRecord,
    InfrastructureEmergencyPlan,
    InfrastructureReport,
    PreventiveMaintenance,
    Room,
    RoomAllocation,
    SafetyInspection,
    SpaceReservation,
    UtilityTracker,
    VendorContract,
    WarrantyClaim,
    WorkOrder,
    WorkOrderComment,
)


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "floors", "status", "is_active"]
    list_filter = ["status", "is_active"]
    search_fields = ["name", "code"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["room_number", "building", "room_type", "capacity", "status"]
    list_filter = ["room_type", "status", "has_projector", "has_smartboard"]
    search_fields = ["room_number", "name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = ["room", "allocation_type", "effective_from", "effective_to"]
    list_filter = ["allocation_type"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "priority", "status", "building", "assigned_to", "created_at"]
    list_filter = ["category", "priority", "status"]
    search_fields = ["title", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(WorkOrderComment)
class WorkOrderCommentAdmin(admin.ModelAdmin):
    list_display = ["work_order", "author", "created_at"]
    readonly_fields = ["id", "created_at"]


@admin.register(PreventiveMaintenance)
class PreventiveMaintenanceAdmin(admin.ModelAdmin):
    list_display = ["title", "frequency", "status", "next_due", "assigned_to"]
    list_filter = ["frequency", "status"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["asset_tag", "name", "asset_type", "condition", "status", "building"]
    list_filter = ["asset_type", "condition", "status"]
    search_fields = ["asset_tag", "name", "serial_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ["asset", "assigned_to", "room", "status", "assigned_date"]
    list_filter = ["status"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(AssetLifecycle)
class AssetLifecycleAdmin(admin.ModelAdmin):
    list_display = ["asset", "event", "event_date", "cost"]
    list_filter = ["event"]
    readonly_fields = ["id", "created_at"]


@admin.register(WarrantyClaim)
class WarrantyClaimAdmin(admin.ModelAdmin):
    list_display = ["asset", "claim_number", "status", "claim_date"]
    list_filter = ["status"]
    search_fields = ["claim_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(SpaceReservation)
class SpaceReservationAdmin(admin.ModelAdmin):
    list_display = ["title", "room", "date", "start_time", "end_time", "status"]
    list_filter = ["status", "purpose"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(UtilityTracker)
class UtilityTrackerAdmin(admin.ModelAdmin):
    list_display = ["building", "utility_type", "reading_date", "consumption", "cost"]
    list_filter = ["utility_type"]
    readonly_fields = ["id", "created_at"]


@admin.register(SafetyInspection)
class SafetyInspectionAdmin(admin.ModelAdmin):
    list_display = ["title", "inspection_type", "status", "overall_severity", "scheduled_date"]
    list_filter = ["inspection_type", "status", "overall_severity"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(InfrastructureComplianceRecord)
class InfrastructureComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ["title", "compliance_type", "status", "last_audit_date", "next_audit_date"]
    list_filter = ["compliance_type", "status"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(VendorContract)
class VendorContractAdmin(admin.ModelAdmin):
    list_display = ["vendor_name", "contract_type", "title", "start_date", "end_date", "status"]
    list_filter = ["contract_type", "status"]
    search_fields = ["vendor_name", "title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(InfrastructureEmergencyPlan)
class InfrastructureEmergencyPlanAdmin(admin.ModelAdmin):
    list_display = ["title", "plan_type", "last_drill_date", "next_drill_date", "is_active"]
    list_filter = ["plan_type", "is_active"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(InfrastructureReport)
class InfrastructureReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "date_from", "date_to", "created_at"]
    list_filter = ["report_type"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]
