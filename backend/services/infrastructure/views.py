"""Infrastructure views."""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.exceptions import ValidationError
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
    serializer_class = BuildingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "code", "address"]
    filterset_fields = ["status", "is_active"]
    ordering = ["name"]

    def get_queryset(self):
        return Building.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "room_number"]
    filterset_fields = ["building", "room_type", "status"]
    ordering = ["building", "floor", "room_number"]

    def get_queryset(self):
        return Room.objects.filter(building__school=self.request.user.school).select_related("building")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class RoomAllocationViewSet(viewsets.ModelViewSet):
    serializer_class = RoomAllocationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["room__name", "event_name", "department"]
    filterset_fields = ["room", "allocation_type"]
    ordering = ["-effective_from"]

    def get_queryset(self):
        return RoomAllocation.objects.filter(room__building__school=self.request.user.school).select_related(
            "room__building", "teacher", "classroom"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class WorkOrderViewSet(viewsets.ModelViewSet):
    serializer_class = WorkOrderSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "category"]
    filterset_fields = ["status", "priority", "building", "assigned_to"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return WorkOrder.objects.filter(school=self.request.user.school).select_related(
            "building", "room", "reported_by", "assigned_to"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, reported_by=self.request.user)


class WorkOrderCommentViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderComment.objects.select_related("author").all()
    serializer_class = WorkOrderCommentSerializer
    permission_classes = [IsAuthenticated]


class PreventiveMaintenanceViewSet(viewsets.ModelViewSet):
    serializer_class = PreventiveMaintenanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description", "category"]
    filterset_fields = ["status", "frequency", "building"]
    ordering = ["next_due"]

    def get_queryset(self):
        return PreventiveMaintenance.objects.filter(school=self.request.user.school).select_related(
            "building", "room", "assigned_to"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "asset_tag", "description"]
    filterset_fields = ["asset_type", "condition", "status", "building"]
    ordering = ["name"]

    def get_queryset(self):
        return Asset.objects.filter(school=self.request.user.school).select_related("building", "room")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


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
    serializer_class = SpaceReservationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "purpose", "room__name"]
    filterset_fields = ["room", "status", "date"]
    ordering = ["-date"]

    def get_queryset(self):
        return SpaceReservation.objects.filter(room__building__school=self.request.user.school).select_related(
            "room__building", "reserved_by", "approved_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(reserved_by=self.request.user)


class UtilityTrackerViewSet(viewsets.ModelViewSet):
    queryset = UtilityTracker.objects.select_related("building", "recorded_by").all()
    serializer_class = UtilityTrackerSerializer
    permission_classes = [IsAuthenticated]


class SafetyInspectionViewSet(viewsets.ModelViewSet):
    serializer_class = SafetyInspectionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "inspector_name", "building__name"]
    filterset_fields = ["status", "inspection_type", "building", "overall_severity"]
    ordering = ["-scheduled_date"]

    def get_queryset(self):
        return SafetyInspection.objects.filter(school=self.request.user.school).select_related(
            "building", "room", "conducted_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InfrastructureComplianceRecordViewSet(viewsets.ModelViewSet):
    queryset = InfrastructureComplianceRecord.objects.select_related("responsible_person").all()
    serializer_class = InfrastructureComplianceRecordSerializer
    permission_classes = [IsAuthenticated]


class VendorContractViewSet(viewsets.ModelViewSet):
    serializer_class = VendorContractSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["vendor_name", "title", "contract_number", "contact_person"]
    filterset_fields = ["status", "contract_type"]
    ordering = ["-start_date"]

    def get_queryset(self):
        return VendorContract.objects.filter(school=self.request.user.school).select_related("created_by")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


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
    search_fields = ["meter_number", "building__name", "notes"]
    filterset_fields = ["building", "meter_type", "is_active"]
    ordering = ["meter_number"]

    def get_queryset(self):
        return EnergyMeter.objects.filter(building__school=self.request.user.school).select_related("building", "room")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        building = serializer.validated_data.get("building")
        if building and building.school_id != self.request.user.school_id:
            raise ValidationError({"building": "Building does not belong to your school."})
        serializer.save()


class EnergyReadingViewSet(viewsets.ModelViewSet):
    serializer_class = EnergyReadingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["meter__meter_number", "notes", "units"]
    filterset_fields = ["meter"]
    ordering = ["-reading_date"]

    def get_queryset(self):
        return EnergyReading.objects.filter(meter__building__school=self.request.user.school).select_related(
            "meter", "recorded_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        meter = serializer.validated_data.get("meter")
        if meter and meter.building.school_id != self.request.user.school_id:
            raise ValidationError({"meter": "Meter does not belong to your school."})
        serializer.save(recorded_by=self.request.user)


class EnergyAlertViewSet(viewsets.ModelViewSet):
    serializer_class = EnergyAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["building__name", "description", "meter__meter_number"]
    filterset_fields = ["building", "alert_type", "severity", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return EnergyAlert.objects.filter(building__school=self.request.user.school).select_related(
            "building", "meter", "acknowledged_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        building = serializer.validated_data.get("building")
        if building and building.school_id != self.request.user.school_id:
            raise ValidationError({"building": "Building does not belong to your school."})
        serializer.save()


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
    search_fields = ["spot_number", "vehicle_plate", "parking_lot__name"]
    filterset_fields = ["parking_lot", "spot_type", "is_active"]
    ordering = ["parking_lot__name", "spot_number"]

    def get_queryset(self):
        return ParkingAssignment.objects.filter(parking_lot__school=self.request.user.school).select_related(
            "parking_lot", "assigned_to"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        lot = serializer.validated_data.get("parking_lot")
        if lot and lot.school_id != self.request.user.school_id:
            raise ValidationError({"parking_lot": "Parking lot does not belong to your school."})
        serializer.save()


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
