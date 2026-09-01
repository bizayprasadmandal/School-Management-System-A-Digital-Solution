"""Serializers for infrastructure."""

from rest_framework import serializers

from .models import (
    AccessControlPoint,
    Asset,
    AssetAssignment,
    AssetLifecycle,
    Building,
    BuildingInspection,
    CCTVCamera,
    EnergyAlert,
    EnergyMeter,
    EnergyReading,
    FloorPlan,
    GreenInitiative,
    InfrastructureAlert,
    InfrastructureComplianceRecord,
    InfrastructureEmergencyPlan,
    InfrastructureMaintenanceRequest,
    InfrastructureReport,
    LightingSchedule,
    MaintenanceCostTracking,
    ParkingAssignment,
    ParkingLot,
    PestControlInspection,
    PestTreatment,
    PreventiveMaintenance,
    Room,
    RoomAllocation,
    RoomEquipment,
    SafetyInspection,
    SpaceReservation,
    UtilityTracker,
    VendorContract,
    VendorPerformance,
    WarrantyClaim,
    WasteCollectionSchedule,
    WaterUsageRecord,
    WorkOrder,
    WorkOrderComment,
)


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "code",
            "description",
            "floors",
            "year_built",
            "total_area_sqft",
            "address",
            "latitude",
            "longitude",
            "status",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "name",
            "room_number",
            "floor",
            "room_type",
            "capacity",
            "area_sqft",
            "has_projector",
            "has_smartboard",
            "has_ac",
            "has_wifi",
            "has_computers",
            "computer_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomAllocation
        fields = [
            "id",
            "id",
            "room",
            "on_delete",
            "allocation_type",
            "classroom",
            "on_delete",
            "teacher",
            "on_delete",
            "department",
            "event_name",
            "effective_from",
            "effective_to",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "description",
            "category",
            "priority",
            "status",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "reported_by",
            "on_delete",
            "assigned_to",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WorkOrderCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderComment
        fields = ["id", "id", "work_order", "on_delete", "author", "on_delete", "comment", "attachments", "created_at"]
        read_only_fields = ["id", "created_at"]


class PreventiveMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreventiveMaintenance
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "description",
            "category",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "frequency",
            "assigned_to",
            "on_delete",
            "last_completed",
            "next_due",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "asset_tag",
            "name",
            "description",
            "asset_type",
            "condition",
            "status",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "purchase_date",
            "purchase_cost",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AssetAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetAssignment
        fields = [
            "id",
            "id",
            "asset",
            "on_delete",
            "assigned_to",
            "on_delete",
            "room",
            "on_delete",
            "department",
            "assigned_date",
            "returned_date",
            "status",
            "condition_at_assignment",
            "condition_at_return",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AssetLifecycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetLifecycle
        fields = [
            "id",
            "id",
            "asset",
            "on_delete",
            "event",
            "event_date",
            "description",
            "cost",
            "performed_by",
            "on_delete",
            "notes",
            "attachments",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WarrantyClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarrantyClaim
        fields = [
            "id",
            "id",
            "asset",
            "on_delete",
            "claim_number",
            "issue_description",
            "claim_date",
            "warranty_provider",
            "contact_person",
            "contact_phone",
            "contact_email",
            "status",
            "resolution_date",
            "resolution_notes",
            "cost_covered",
            "cost_customer",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SpaceReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceReservation
        fields = [
            "id",
            "id",
            "room",
            "on_delete",
            "title",
            "purpose",
            "reserved_by",
            "on_delete",
            "date",
            "start_time",
            "end_time",
            "attendees_count",
            "status",
            "requires_av",
            "requires_refreshments",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UtilityTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtilityTracker
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "utility_type",
            "reading_date",
            "reading_value",
            "units",
            "cost",
            "previous_reading",
            "consumption",
            "notes",
            "recorded_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SafetyInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyInspection
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "inspection_type",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "scheduled_date",
            "completed_date",
            "inspector_name",
            "inspector_organization",
            "status",
            "overall_severity",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InfrastructureComplianceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureComplianceRecord
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "compliance_type",
            "description",
            "regulation_reference",
            "status",
            "last_audit_date",
            "next_audit_date",
            "expiry_date",
            "responsible_person",
            "on_delete",
            "document_url",
            "attachments",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VendorContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorContract
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "vendor_name",
            "contract_type",
            "title",
            "description",
            "contract_number",
            "start_date",
            "end_date",
            "renewal_date",
            "auto_renew",
            "value",
            "payment_frequency",
            "contact_person",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InfrastructureEmergencyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureEmergencyPlan
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "plan_type",
            "description",
            "procedures",
            "assembly_points",
            "emergency_contacts",
            "last_drill_date",
            "next_drill_date",
            "last_review_date",
            "document_url",
            "attachments",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InfrastructureReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "report_type",
            "description",
            "date_from",
            "date_to",
            "data",
            "summary",
            "generated_by",
            "on_delete",
            "file_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class EnergyMeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyMeter
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "meter_number",
            "meter_type",
            "installation_date",
            "last_reading_date",
            "last_reading_value",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EnergyReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyReading
        fields = [
            "id",
            "id",
            "meter",
            "on_delete",
            "reading_date",
            "reading_value",
            "units",
            "cost",
            "recorded_by",
            "on_delete",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class EnergyAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyAlert
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "meter",
            "on_delete",
            "alert_type",
            "severity",
            "status",
            "description",
            "threshold_value",
            "actual_value",
            "acknowledged_by",
            "on_delete",
            "resolved_at",
            "resolution_notes",
        ]
        read_only_fields = ["id", "created_at"]


class CCTVCameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = CCTVCamera
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "camera_name",
            "camera_id",
            "location_description",
            "stream_url",
            "recording_enabled",
            "storage_days",
            "status",
            "installation_date",
            "last_maintenance",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AccessControlPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessControlPoint
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "point_name",
            "access_type",
            "status",
            "access_start_time",
            "access_end_time",
            "restricted_access",
            "allowed_roles",
            "installation_date",
            "last_maintenance",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PestControlInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PestControlInspection
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "inspection_type",
            "status",
            "scheduled_date",
            "completed_date",
            "inspector_name",
            "pests_found",
            "treatment_applied",
            "follow_up_required",
            "treatment_cost",
            "report_file",
        ]
        read_only_fields = ["id", "created_at"]


class PestTreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PestTreatment
        fields = [
            "id",
            "id",
            "inspection",
            "on_delete",
            "building",
            "on_delete",
            "treatment_date",
            "treatment_type",
            "pest_target",
            "chemical_name",
            "safety_re_entry_hours",
            "cost",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WasteCollectionScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteCollectionSchedule
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "waste_type",
            "frequency",
            "collection_day",
            "collection_time",
            "vendor_name",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class GreenInitiativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GreenInitiative
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "building",
            "on_delete",
            "title",
            "description",
            "initiative_type",
            "status",
            "estimated_cost",
            "estimated_savings",
            "carbon_reduction_kg",
            "start_date",
            "target_end_date",
            "proposed_by",
        ]
        read_only_fields = ["id", "created_at"]


class WaterUsageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterUsageRecord
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "record_date",
            "usage_gallons",
            "cost",
            "leak_detected",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPerformance
        fields = [
            "id",
            "id",
            "vendor_contract",
            "on_delete",
            "service_type",
            "evaluation_date",
            "evaluator",
            "on_delete",
            "quality_rating",
            "timeliness_rating",
            "communication_rating",
            "value_rating",
            "comments",
            "would_rehire",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BuildingInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingInspection
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "inspection_type",
            "inspection_date",
            "inspector_name",
            "result",
            "findings",
            "violations",
            "follow_up_required",
            "follow_up_date",
            "corrective_actions",
            "report_file",
            "recorded_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class InfrastructureAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureAlert
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "alert_type",
            "severity",
            "status",
            "title",
            "description",
            "reported_by",
            "on_delete",
            "assigned_to",
        ]
        read_only_fields = ["id", "created_at"]


class FloorPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FloorPlan
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "floor_number",
            "floor_name",
            "plan_file",
            "total_rooms",
            "total_area_sqft",
            "description",
            "is_current",
            "uploaded_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RoomEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomEquipment
        fields = [
            "id",
            "id",
            "room",
            "on_delete",
            "equipment_type",
            "name",
            "asset_tag",
            "brand",
            "status",
            "purchase_date",
            "warranty_expiry",
            "last_maintenance",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "total_spots",
            "available_spots",
            "is_covered",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ParkingAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingAssignment
        fields = [
            "id",
            "id",
            "parking_lot",
            "on_delete",
            "assigned_to",
            "on_delete",
            "spot_number",
            "spot_type",
            "vehicle_plate",
            "is_active",
            "start_date",
            "end_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LightingScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LightingSchedule
        fields = [
            "id",
            "id",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "zone_name",
            "day_of_week",
            "on_time",
            "off_time",
            "brightness_level",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MaintenanceCostTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceCostTracking
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "building",
            "on_delete",
            "work_order",
            "on_delete",
            "cost_category",
            "amount",
            "vendor",
            "cost_date",
            "is_approved",
            "approved_by",
            "on_delete",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class InfrastructureMaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureMaintenanceRequest
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "building",
            "on_delete",
            "room",
            "on_delete",
            "requested_by",
            "on_delete",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
