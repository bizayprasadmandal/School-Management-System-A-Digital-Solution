"""Infrastructure views."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
from .serializers import (
    AssetAssignmentSerializer,
    AssetLifecycleSerializer,
    AssetSerializer,
    BuildingSerializer,
    InfrastructureComplianceRecordSerializer,
    InfrastructureEmergencyPlanSerializer,
    InfrastructureReportSerializer,
    PreventiveMaintenanceSerializer,
    RoomAllocationSerializer,
    RoomSerializer,
    SafetyInspectionSerializer,
    SpaceReservationSerializer,
    UtilityTrackerSerializer,
    VendorContractSerializer,
    WarrantyClaimSerializer,
    WorkOrderCommentSerializer,
    WorkOrderSerializer,
)


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [IsAuthenticated]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related("building").all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]


class RoomAllocationViewSet(viewsets.ModelViewSet):
    queryset = RoomAllocation.objects.select_related("room").all()
    serializer_class = RoomAllocationSerializer
    permission_classes = [IsAuthenticated]


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.select_related("building", "room", "reported_by", "assigned_to").all()
    serializer_class = WorkOrderSerializer
    permission_classes = [IsAuthenticated]


class WorkOrderCommentViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderComment.objects.select_related("author").all()
    serializer_class = WorkOrderCommentSerializer
    permission_classes = [IsAuthenticated]


class PreventiveMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = PreventiveMaintenance.objects.select_related("building", "room", "assigned_to").all()
    serializer_class = PreventiveMaintenanceSerializer
    permission_classes = [IsAuthenticated]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related("building", "room").all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]


class AssetAssignmentViewSet(viewsets.ModelViewSet):
    queryset = AssetAssignment.objects.select_related("asset", "assigned_to", "room").all()
    serializer_class = AssetAssignmentSerializer
    permission_classes = [IsAuthenticated]


class AssetLifecycleViewSet(viewsets.ModelViewSet):
    queryset = AssetLifecycle.objects.select_related("asset", "performed_by").all()
    serializer_class = AssetLifecycleSerializer
    permission_classes = [IsAuthenticated]


class WarrantyClaimViewSet(viewsets.ModelViewSet):
    queryset = WarrantyClaim.objects.select_related("asset", "reported_by").all()
    serializer_class = WarrantyClaimSerializer
    permission_classes = [IsAuthenticated]


class SpaceReservationViewSet(viewsets.ModelViewSet):
    queryset = SpaceReservation.objects.select_related("room", "room__building", "reserved_by", "approved_by").all()
    serializer_class = SpaceReservationSerializer
    permission_classes = [IsAuthenticated]


class UtilityTrackerViewSet(viewsets.ModelViewSet):
    queryset = UtilityTracker.objects.select_related("building", "recorded_by").all()
    serializer_class = UtilityTrackerSerializer
    permission_classes = [IsAuthenticated]


class SafetyInspectionViewSet(viewsets.ModelViewSet):
    queryset = SafetyInspection.objects.select_related("building", "room", "conducted_by").all()
    serializer_class = SafetyInspectionSerializer
    permission_classes = [IsAuthenticated]


class InfrastructureComplianceRecordViewSet(viewsets.ModelViewSet):
    queryset = InfrastructureComplianceRecord.objects.select_related("responsible_person").all()
    serializer_class = InfrastructureComplianceRecordSerializer
    permission_classes = [IsAuthenticated]


class VendorContractViewSet(viewsets.ModelViewSet):
    queryset = VendorContract.objects.select_related("created_by").all()
    serializer_class = VendorContractSerializer
    permission_classes = [IsAuthenticated]


class InfrastructureEmergencyPlanViewSet(viewsets.ModelViewSet):
    queryset = InfrastructureEmergencyPlan.objects.select_related("reviewed_by").all()
    serializer_class = InfrastructureEmergencyPlanSerializer
    permission_classes = [IsAuthenticated]


class InfrastructureReportViewSet(viewsets.ModelViewSet):
    queryset = InfrastructureReport.objects.select_related("generated_by").all()
    serializer_class = InfrastructureReportSerializer
    permission_classes = [IsAuthenticated]
