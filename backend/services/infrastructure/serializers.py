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
        read_only_fields = ["id", "school", "created_at", "updated_at"]


class RoomSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_type_display = serializers.CharField(source="get_room_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "id",
            "building",
            "building_name",
            "name",
            "room_number",
            "floor",
            "room_type",
            "room_type_display",
            "status",
            "status_display",
            "capacity",
            "area_sqft",
            "has_projector",
            "has_smartboard",
            "has_ac",
            "has_wifi",
            "has_computers",
            "computer_count",
        ]
        read_only_fields = ["id", "building_name", "room_type_display", "status_display", "created_at", "updated_at"]


class RoomAllocationSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    room_building_name = serializers.CharField(source="room.building.name", read_only=True)
    allocation_type_display = serializers.CharField(source="get_allocation_type_display", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = RoomAllocation
        fields = [
            "id",
            "id",
            "room",
            "room_name",
            "room_building_name",
            "allocation_type",
            "allocation_type_display",
            "classroom",
            "teacher",
            "teacher_name",
            "department",
            "event_name",
            "effective_from",
            "effective_to",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "room_name",
            "room_building_name",
            "allocation_type_display",
            "teacher_name",
            "created_at",
            "updated_at",
        ]


class WorkOrderSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)

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
            "priority_display",
            "status",
            "status_display",
            "building",
            "building_name",
            "room",
            "room_name",
            "reported_by",
            "reported_by_name",
            "assigned_to",
            "assigned_to_name",
        ]
        read_only_fields = [
            "id",
            "school",
            "building_name",
            "room_name",
            "priority_display",
            "status_display",
            "reported_by_name",
            "assigned_to_name",
            "created_at",
            "updated_at",
        ]


class WorkOrderCommentSerializer(serializers.ModelSerializer):
    work_order_title = serializers.CharField(source="work_order.title", read_only=True)
    author_name = serializers.CharField(source="author.full_name", read_only=True, default="")

    class Meta:
        model = WorkOrderComment
        fields = [
            "id",
            "work_order",
            "work_order_title",
            "author",
            "author_name",
            "comment",
            "attachments",
            "created_at",
        ]
        read_only_fields = ["id", "work_order_title", "author", "author_name", "created_at"]


class PreventiveMaintenanceSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True)
    frequency_display = serializers.CharField(source="get_frequency_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)

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
            "building_name",
            "room",
            "room_name",
            "frequency",
            "frequency_display",
            "status",
            "status_display",
            "assigned_to",
            "assigned_to_name",
            "last_completed",
            "next_due",
        ]
        read_only_fields = [
            "id",
            "school",
            "building_name",
            "room_name",
            "frequency_display",
            "status_display",
            "assigned_to_name",
            "created_at",
            "updated_at",
        ]


class AssetSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True)
    asset_type_display = serializers.CharField(source="get_asset_type_display", read_only=True)
    condition_display = serializers.CharField(source="get_condition_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

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
            "asset_type_display",
            "condition",
            "condition_display",
            "status",
            "status_display",
            "building",
            "building_name",
            "room",
            "room_name",
            "purchase_date",
            "purchase_cost",
        ]
        read_only_fields = [
            "id",
            "school",
            "building_name",
            "room_name",
            "asset_type_display",
            "condition_display",
            "status_display",
            "created_at",
            "updated_at",
        ]


class AssetAssignmentSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    asset_tag = serializers.CharField(source="asset.asset_tag", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default="")
    room_name = serializers.CharField(source="room.name", read_only=True, default="")
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AssetAssignment
        fields = [
            "id",
            "asset",
            "asset_name",
            "asset_tag",
            "assigned_to",
            "assigned_to_name",
            "room",
            "room_name",
            "department",
            "assigned_date",
            "returned_date",
            "status",
            "status_display",
            "condition_at_assignment",
            "condition_at_return",
            "notes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "asset_name",
            "asset_tag",
            "assigned_to_name",
            "room_name",
            "status_display",
            "created_at",
            "updated_at",
        ]


class AssetLifecycleSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    asset_tag = serializers.CharField(source="asset.asset_tag", read_only=True)
    event_display = serializers.CharField(source="get_event_display", read_only=True)
    performed_by_name = serializers.CharField(source="performed_by.full_name", read_only=True, default="")

    class Meta:
        model = AssetLifecycle
        fields = [
            "id",
            "asset",
            "asset_name",
            "asset_tag",
            "event",
            "event_display",
            "event_date",
            "description",
            "cost",
            "performed_by",
            "performed_by_name",
            "notes",
            "attachments",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "asset_name",
            "asset_tag",
            "event_display",
            "performed_by",
            "performed_by_name",
            "created_at",
        ]


class WarrantyClaimSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    asset_tag = serializers.CharField(source="asset.asset_tag", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = WarrantyClaim
        fields = [
            "id",
            "asset",
            "asset_name",
            "asset_tag",
            "claim_number",
            "issue_description",
            "claim_date",
            "warranty_provider",
            "contact_person",
            "contact_phone",
            "contact_email",
            "status",
            "status_display",
            "resolution_date",
            "resolution_notes",
            "cost_covered",
            "cost_customer",
            "created_at",
        ]
        read_only_fields = ["id", "asset_name", "asset_tag", "status_display", "created_at", "updated_at"]


class SpaceReservationSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    room_building_name = serializers.CharField(source="room.building.name", read_only=True)
    reserved_by_name = serializers.CharField(source="reserved_by.full_name", read_only=True)
    purpose_display = serializers.CharField(source="get_purpose_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SpaceReservation
        fields = [
            "id",
            "id",
            "room",
            "room_name",
            "room_building_name",
            "title",
            "purpose",
            "purpose_display",
            "reserved_by",
            "reserved_by_name",
            "date",
            "start_time",
            "end_time",
            "attendees_count",
            "status",
            "status_display",
            "requires_av",
            "requires_refreshments",
            "notes",
        ]
        read_only_fields = [
            "id",
            "room_name",
            "room_building_name",
            "reserved_by",
            "reserved_by_name",
            "purpose_display",
            "status_display",
            "created_at",
            "updated_at",
        ]


class UtilityTrackerSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    utility_type_display = serializers.CharField(source="get_utility_type_display", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.full_name", read_only=True, default="")

    class Meta:
        model = UtilityTracker
        fields = [
            "id",
            "building",
            "building_name",
            "utility_type",
            "utility_type_display",
            "reading_date",
            "reading_value",
            "units",
            "cost",
            "previous_reading",
            "consumption",
            "notes",
            "recorded_by",
            "recorded_by_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "building_name",
            "utility_type_display",
            "recorded_by",
            "recorded_by_name",
            "created_at",
        ]


class SafetyInspectionSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True, default="")
    room_name = serializers.CharField(source="room.name", read_only=True, default="")
    inspection_type_display = serializers.CharField(source="get_inspection_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    severity_display = serializers.CharField(source="get_overall_severity_display", read_only=True)

    class Meta:
        model = SafetyInspection
        fields = [
            "id",
            "school",
            "title",
            "inspection_type",
            "inspection_type_display",
            "building",
            "building_name",
            "room",
            "room_name",
            "scheduled_date",
            "completed_date",
            "inspector_name",
            "inspector_organization",
            "status",
            "status_display",
            "overall_severity",
            "severity_display",
            "findings",
            "recommendations",
            "corrective_actions",
            "next_inspection_date",
        ]
        read_only_fields = [
            "id",
            "school",
            "building_name",
            "room_name",
            "inspection_type_display",
            "status_display",
            "severity_display",
            "created_at",
            "updated_at",
        ]


class InfrastructureComplianceRecordSerializer(serializers.ModelSerializer):
    compliance_type_display = serializers.CharField(source="get_compliance_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    responsible_person_name = serializers.CharField(source="responsible_person.full_name", read_only=True, default="")

    class Meta:
        model = InfrastructureComplianceRecord
        fields = [
            "id",
            "school",
            "title",
            "compliance_type",
            "compliance_type_display",
            "description",
            "regulation_reference",
            "status",
            "status_display",
            "last_audit_date",
            "next_audit_date",
            "expiry_date",
            "responsible_person",
            "responsible_person_name",
            "document_url",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "compliance_type_display",
            "status_display",
            "responsible_person_name",
            "created_at",
            "updated_at",
        ]


class VendorContractSerializer(serializers.ModelSerializer):
    contract_type_display = serializers.CharField(source="get_contract_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default="")

    class Meta:
        model = VendorContract
        fields = [
            "id",
            "school",
            "vendor_name",
            "contract_type",
            "contract_type_display",
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
            "contact_phone",
            "contact_email",
            "sla_description",
            "status",
            "status_display",
            "created_by",
            "created_by_name",
        ]
        read_only_fields = [
            "id",
            "school",
            "contract_type_display",
            "status_display",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]


class InfrastructureEmergencyPlanSerializer(serializers.ModelSerializer):
    plan_type_display = serializers.CharField(source="get_plan_type_display", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default="")

    class Meta:
        model = InfrastructureEmergencyPlan
        fields = [
            "id",
            "school",
            "title",
            "plan_type",
            "plan_type_display",
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
            "reviewed_by",
            "reviewed_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "plan_type_display",
            "reviewed_by",
            "reviewed_by_name",
            "created_at",
            "updated_at",
        ]


class InfrastructureReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default="")

    class Meta:
        model = InfrastructureReport
        fields = [
            "id",
            "school",
            "title",
            "report_type",
            "report_type_display",
            "description",
            "date_from",
            "date_to",
            "data",
            "summary",
            "generated_by",
            "generated_by_name",
            "file_url",
            "created_at",
        ]
        read_only_fields = ["id", "school", "report_type_display", "generated_by", "generated_by_name", "created_at"]


class EnergyMeterSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True, default="")
    meter_type_display = serializers.CharField(source="get_meter_type_display", read_only=True)

    class Meta:
        model = EnergyMeter
        fields = [
            "id",
            "building",
            "building_name",
            "room",
            "room_name",
            "meter_number",
            "meter_type",
            "meter_type_display",
            "installation_date",
            "last_reading_date",
            "last_reading_value",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "building_name",
            "room_name",
            "meter_type_display",
            "last_reading_date",
            "last_reading_value",
            "created_at",
            "updated_at",
        ]


class EnergyReadingSerializer(serializers.ModelSerializer):
    meter_number = serializers.CharField(source="meter.meter_number", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.full_name", read_only=True, default="")

    class Meta:
        model = EnergyReading
        fields = [
            "id",
            "meter",
            "meter_number",
            "reading_date",
            "reading_value",
            "units",
            "cost",
            "recorded_by",
            "recorded_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "meter_number", "recorded_by", "recorded_by_name", "created_at"]


class EnergyAlertSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    meter_number = serializers.CharField(source="meter.meter_number", read_only=True, default="")
    alert_type_display = serializers.CharField(source="get_alert_type_display", read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = EnergyAlert
        fields = [
            "id",
            "building",
            "building_name",
            "meter",
            "meter_number",
            "alert_type",
            "alert_type_display",
            "severity",
            "severity_display",
            "status",
            "status_display",
            "description",
            "threshold_value",
            "actual_value",
            "acknowledged_by",
            "resolved_at",
            "resolution_notes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "building_name",
            "meter_number",
            "alert_type_display",
            "severity_display",
            "status_display",
            "created_at",
        ]


class CCTVCameraSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True, default="")
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = CCTVCamera
        fields = [
            "id",
            "building",
            "building_name",
            "room",
            "room_name",
            "camera_name",
            "camera_id",
            "location_description",
            "stream_url",
            "recording_enabled",
            "storage_days",
            "status",
            "status_display",
            "installation_date",
            "last_maintenance",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "building_name", "room_name", "status_display", "created_at", "updated_at"]


class AccessControlPointSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True, default="")
    access_type_display = serializers.CharField(source="get_access_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AccessControlPoint
        fields = [
            "id",
            "building",
            "building_name",
            "room",
            "room_name",
            "point_name",
            "access_type",
            "access_type_display",
            "status",
            "status_display",
            "access_start_time",
            "access_end_time",
            "restricted_access",
            "allowed_roles",
            "installation_date",
            "last_maintenance",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "building_name",
            "room_name",
            "access_type_display",
            "status_display",
            "created_at",
            "updated_at",
        ]


class PestControlInspectionSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True, default="")
    inspection_type_display = serializers.CharField(source="get_inspection_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PestControlInspection
        fields = [
            "id",
            "building",
            "building_name",
            "room",
            "room_name",
            "inspection_type",
            "inspection_type_display",
            "status",
            "status_display",
            "scheduled_date",
            "completed_date",
            "inspector_name",
            "pests_found",
            "treatment_applied",
            "follow_up_required",
            "treatment_cost",
            "report_file",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "building_name",
            "room_name",
            "inspection_type_display",
            "status_display",
            "created_at",
        ]


class PestTreatmentSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)

    class Meta:
        model = PestTreatment
        fields = [
            "id",
            "inspection",
            "building",
            "building_name",
            "treatment_date",
            "treatment_type",
            "pest_target",
            "chemical_name",
            "safety_re_entry_hours",
            "cost",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "building_name", "created_at"]


class WasteCollectionScheduleSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    waste_type_display = serializers.CharField(source="get_waste_type_display", read_only=True)
    frequency_display = serializers.CharField(source="get_frequency_display", read_only=True)

    class Meta:
        model = WasteCollectionSchedule
        fields = [
            "id",
            "building",
            "building_name",
            "waste_type",
            "waste_type_display",
            "frequency",
            "frequency_display",
            "collection_day",
            "collection_time",
            "vendor_name",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "building_name", "waste_type_display", "frequency_display", "created_at"]


class GreenInitiativeSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True, default="")
    initiative_type_display = serializers.CharField(source="get_initiative_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    proposed_by_name = serializers.CharField(source="proposed_by.full_name", read_only=True, default="")

    class Meta:
        model = GreenInitiative
        fields = [
            "id",
            "school",
            "building",
            "building_name",
            "title",
            "description",
            "initiative_type",
            "initiative_type_display",
            "status",
            "status_display",
            "estimated_cost",
            "estimated_savings",
            "carbon_reduction_kg",
            "start_date",
            "target_end_date",
            "proposed_by",
            "proposed_by_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "building_name",
            "initiative_type_display",
            "status_display",
            "proposed_by",
            "proposed_by_name",
            "created_at",
        ]


class WaterUsageRecordSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)

    class Meta:
        model = WaterUsageRecord
        fields = [
            "id",
            "building",
            "building_name",
            "record_date",
            "usage_gallons",
            "cost",
            "leak_detected",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "building_name", "created_at"]


class VendorPerformanceSerializer(serializers.ModelSerializer):
    vendor_contract_name = serializers.CharField(source="vendor_contract.vendor_name", read_only=True)
    service_type_display = serializers.CharField(source="get_service_type_display", read_only=True)
    evaluator_name = serializers.CharField(source="evaluator.full_name", read_only=True, default="")

    class Meta:
        model = VendorPerformance
        fields = [
            "id",
            "vendor_contract",
            "vendor_contract_name",
            "service_type",
            "service_type_display",
            "evaluation_date",
            "evaluator",
            "evaluator_name",
            "quality_rating",
            "timeliness_rating",
            "communication_rating",
            "value_rating",
            "comments",
            "would_rehire",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "vendor_contract_name",
            "service_type_display",
            "evaluator",
            "evaluator_name",
            "created_at",
        ]


class BuildingInspectionSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    inspection_type_display = serializers.CharField(source="get_inspection_type_display", read_only=True)
    result_display = serializers.CharField(source="get_result_display", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.full_name", read_only=True, default="")

    class Meta:
        model = BuildingInspection
        fields = [
            "id",
            "building",
            "building_name",
            "inspection_type",
            "inspection_type_display",
            "inspection_date",
            "inspector_name",
            "result",
            "result_display",
            "findings",
            "violations",
            "follow_up_required",
            "follow_up_date",
            "corrective_actions",
            "report_file",
            "recorded_by",
            "recorded_by_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "building_name",
            "inspection_type_display",
            "result_display",
            "recorded_by",
            "recorded_by_name",
            "created_at",
        ]


class InfrastructureAlertSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True, default="")
    room_name = serializers.CharField(source="room.name", read_only=True, default="")
    alert_type_display = serializers.CharField(source="get_alert_type_display", read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True, default="")
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default="")

    class Meta:
        model = InfrastructureAlert
        fields = [
            "id",
            "school",
            "building",
            "building_name",
            "room",
            "room_name",
            "alert_type",
            "alert_type_display",
            "severity",
            "severity_display",
            "status",
            "status_display",
            "title",
            "description",
            "reported_by",
            "reported_by_name",
            "assigned_to",
            "assigned_to_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "building_name",
            "room_name",
            "alert_type_display",
            "severity_display",
            "status_display",
            "reported_by",
            "reported_by_name",
            "assigned_to_name",
            "created_at",
        ]


class FloorPlanSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True, default="")

    class Meta:
        model = FloorPlan
        fields = [
            "id",
            "building",
            "building_name",
            "floor_number",
            "floor_name",
            "plan_file",
            "total_rooms",
            "total_area_sqft",
            "description",
            "is_current",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "building_name", "uploaded_by", "uploaded_by_name", "created_at"]


class RoomEquipmentSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    equipment_type_display = serializers.CharField(source="get_equipment_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = RoomEquipment
        fields = [
            "id",
            "room",
            "room_name",
            "equipment_type",
            "equipment_type_display",
            "name",
            "asset_tag",
            "brand",
            "status",
            "status_display",
            "purchase_date",
            "warranty_expiry",
            "last_maintenance",
            "notes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "room_name",
            "equipment_type_display",
            "status_display",
            "created_at",
        ]


class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = [
            "id",
            "school",
            "name",
            "total_spots",
            "available_spots",
            "is_covered",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "school", "created_at"]


class ParkingAssignmentSerializer(serializers.ModelSerializer):
    parking_lot_name = serializers.CharField(source="parking_lot.name", read_only=True)
    spot_type_display = serializers.CharField(source="get_spot_type_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default="")

    class Meta:
        model = ParkingAssignment
        fields = [
            "id",
            "parking_lot",
            "parking_lot_name",
            "assigned_to",
            "assigned_to_name",
            "spot_number",
            "spot_type",
            "spot_type_display",
            "vehicle_plate",
            "is_active",
            "start_date",
            "end_date",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "parking_lot_name",
            "spot_type_display",
            "assigned_to_name",
            "created_at",
        ]


class LightingScheduleSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True, default="")

    class Meta:
        model = LightingSchedule
        fields = [
            "id",
            "building",
            "building_name",
            "room",
            "room_name",
            "zone_name",
            "day_of_week",
            "on_time",
            "off_time",
            "brightness_level",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "building_name", "room_name", "created_at"]


class MaintenanceCostTrackingSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True, default="")
    work_order_title = serializers.CharField(source="work_order.title", read_only=True, default="")
    cost_category_display = serializers.CharField(source="get_cost_category_display", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default="")

    class Meta:
        model = MaintenanceCostTracking
        fields = [
            "id",
            "school",
            "building",
            "building_name",
            "work_order",
            "work_order_title",
            "cost_category",
            "cost_category_display",
            "amount",
            "vendor",
            "cost_date",
            "is_approved",
            "approved_by",
            "approved_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "building_name",
            "work_order_title",
            "cost_category_display",
            "approved_by",
            "approved_by_name",
            "created_at",
        ]


class InfrastructureMaintenanceRequestSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True, default="")
    room_name = serializers.CharField(source="room.name", read_only=True, default="")
    requested_by_name = serializers.CharField(source="requested_by.full_name", read_only=True, default="")
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default="")

    class Meta:
        model = InfrastructureMaintenanceRequest
        fields = [
            "id",
            "school",
            "building",
            "building_name",
            "room",
            "room_name",
            "requested_by",
            "requested_by_name",
            "title",
            "description",
            "priority",
            "priority_display",
            "status",
            "status_display",
            "assigned_to",
            "assigned_to_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "building_name",
            "room_name",
            "requested_by",
            "requested_by_name",
            "priority_display",
            "status_display",
            "assigned_to",
            "assigned_to_name",
            "created_at",
            "updated_at",
        ]
