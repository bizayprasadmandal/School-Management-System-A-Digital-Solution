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
            "allocation_type",
            "classroom",
            "teacher",
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
            "title",
            "description",
            "category",
            "priority",
            "status",
            "building",
            "room",
            "reported_by",
            "assigned_to",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WorkOrderCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderComment
        fields = ["id", "id", "work_order", "author", "comment", "attachments", "created_at"]
        read_only_fields = ["id", "created_at"]


class PreventiveMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreventiveMaintenance
        fields = [
            "id",
            "school",
            "id",
            "title",
            "description",
            "category",
            "building",
            "room",
            "frequency",
            "assigned_to",
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
            "asset_tag",
            "name",
            "description",
            "asset_type",
            "condition",
            "status",
            "building",
            "room",
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
            "assigned_to",
            "room",
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
            "event",
            "event_date",
            "description",
            "cost",
            "performed_by",
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
            "title",
            "purpose",
            "reserved_by",
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
            "utility_type",
            "reading_date",
            "reading_value",
            "units",
            "cost",
            "previous_reading",
            "consumption",
            "notes",
            "recorded_by",
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
            "title",
            "inspection_type",
            "building",
            "room",
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
            "title",
            "compliance_type",
            "description",
            "regulation_reference",
            "status",
            "last_audit_date",
            "next_audit_date",
            "expiry_date",
            "responsible_person",
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
            "title",
            "report_type",
            "description",
            "date_from",
            "date_to",
            "data",
            "summary",
            "generated_by",
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
            "room",
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
            "reading_date",
            "reading_value",
            "units",
            "cost",
            "recorded_by",
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
            "meter",
            "alert_type",
            "severity",
            "status",
            "description",
            "threshold_value",
            "actual_value",
            "acknowledged_by",
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
            "room",
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
            "room",
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
            "room",
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
            "building",
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
            "building",
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
            "service_type",
            "evaluation_date",
            "evaluator",
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
        ]
        read_only_fields = ["id", "created_at"]


class InfrastructureAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureAlert
        fields = [
            "id",
            "school",
            "id",
            "building",
            "room",
            "alert_type",
            "severity",
            "status",
            "title",
            "description",
            "reported_by",
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
            "floor_number",
            "floor_name",
            "plan_file",
            "total_rooms",
            "total_area_sqft",
            "description",
            "is_current",
            "uploaded_by",
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
            "assigned_to",
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
            "room",
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
            "building",
            "work_order",
            "cost_category",
            "amount",
            "vendor",
            "cost_date",
            "is_approved",
            "approved_by",
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
            "building",
            "room",
            "requested_by",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
