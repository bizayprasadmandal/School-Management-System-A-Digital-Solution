"""Infrastructure views."""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

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
from .serializers import (
    AccessControlPointSerializer,
    AssetAssignmentSerializer,
    AssetLifecycleSerializer,
    AssetSerializer,
    BuildingInspectionSerializer,
    BuildingSerializer,
    CCTVCameraSerializer,
    EnergyAlertSerializer,
    EnergyMeterSerializer,
    EnergyReadingSerializer,
    FloorPlanSerializer,
    GreenInitiativeSerializer,
    InfrastructureAlertSerializer,
    InfrastructureComplianceRecordSerializer,
    InfrastructureEmergencyPlanSerializer,
    InfrastructureMaintenanceRequestSerializer,
    InfrastructureReportSerializer,
    LightingScheduleSerializer,
    MaintenanceCostTrackingSerializer,
    ParkingAssignmentSerializer,
    ParkingLotSerializer,
    PestControlInspectionSerializer,
    PestTreatmentSerializer,
    PreventiveMaintenanceSerializer,
    RoomAllocationSerializer,
    RoomEquipmentSerializer,
    RoomSerializer,
    SafetyInspectionSerializer,
    SpaceReservationSerializer,
    UtilityTrackerSerializer,
    VendorContractSerializer,
    VendorPerformanceSerializer,
    WarrantyClaimSerializer,
    WasteCollectionScheduleSerializer,
    WaterUsageRecordSerializer,
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


# ── Additional ViewSets (module expansion) ──


class EnergyMeterViewSet(viewsets.ModelViewSet):
    serializer_class = EnergyMeterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return EnergyMeter.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class EnergyReadingViewSet(viewsets.ModelViewSet):
    serializer_class = EnergyReadingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return EnergyReading.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class EnergyAlertViewSet(viewsets.ModelViewSet):
    serializer_class = EnergyAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return EnergyAlert.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CCTVCameraViewSet(viewsets.ModelViewSet):
    serializer_class = CCTVCameraSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return CCTVCamera.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AccessControlPointViewSet(viewsets.ModelViewSet):
    serializer_class = AccessControlPointSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return AccessControlPoint.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PestControlInspectionViewSet(viewsets.ModelViewSet):
    serializer_class = PestControlInspectionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return PestControlInspection.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PestTreatmentViewSet(viewsets.ModelViewSet):
    serializer_class = PestTreatmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return PestTreatment.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class WasteCollectionScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = WasteCollectionScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return WasteCollectionSchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class GreenInitiativeViewSet(viewsets.ModelViewSet):
    serializer_class = GreenInitiativeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return GreenInitiative.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class WaterUsageRecordViewSet(viewsets.ModelViewSet):
    serializer_class = WaterUsageRecordSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return WaterUsageRecord.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class VendorPerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = VendorPerformanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return VendorPerformance.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BuildingInspectionViewSet(viewsets.ModelViewSet):
    serializer_class = BuildingInspectionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return BuildingInspection.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InfrastructureAlertViewSet(viewsets.ModelViewSet):
    serializer_class = InfrastructureAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InfrastructureAlert.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class FloorPlanViewSet(viewsets.ModelViewSet):
    serializer_class = FloorPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return FloorPlan.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RoomEquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = RoomEquipmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return RoomEquipment.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ParkingLotViewSet(viewsets.ModelViewSet):
    serializer_class = ParkingLotSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ParkingLot.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ParkingAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = ParkingAssignmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ParkingAssignment.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class LightingScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = LightingScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return LightingSchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MaintenanceCostTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceCostTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return MaintenanceCostTracking.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InfrastructureMaintenanceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = InfrastructureMaintenanceRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InfrastructureMaintenanceRequest.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
