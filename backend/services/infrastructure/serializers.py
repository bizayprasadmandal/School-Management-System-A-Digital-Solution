"""Infrastructure serializers."""

from rest_framework import serializers

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


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)

    class Meta:
        model = Room
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomAllocation
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class WorkOrderCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = WorkOrderComment
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class WorkOrderSerializer(serializers.ModelSerializer):
    comments = WorkOrderCommentSerializer(many=True, read_only=True)
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.get_full_name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)

    class Meta:
        model = WorkOrder
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PreventiveMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreventiveMaintenance
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AssetSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True)

    class Meta:
        model = Asset
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AssetAssignmentSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source="asset.asset_tag", read_only=True)
    asset_name = serializers.CharField(source="asset.name", read_only=True)

    class Meta:
        model = AssetAssignment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AssetLifecycleSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source="asset.asset_tag", read_only=True)

    class Meta:
        model = AssetLifecycle
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class WarrantyClaimSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source="asset.asset_tag", read_only=True)

    class Meta:
        model = WarrantyClaim
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class SpaceReservationSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    building_name = serializers.CharField(source="room.building.name", read_only=True)
    reserved_by_name = serializers.CharField(source="reserved_by.get_full_name", read_only=True)

    class Meta:
        model = SpaceReservation
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class UtilityTrackerSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)

    class Meta:
        model = UtilityTracker
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SafetyInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyInspection
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class InfrastructureComplianceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureComplianceRecord
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class VendorContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorContract
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class InfrastructureEmergencyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureEmergencyPlan
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class InfrastructureReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)

    class Meta:
        model = InfrastructureReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
