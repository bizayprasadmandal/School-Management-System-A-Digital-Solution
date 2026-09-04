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
    serializer_class = WorkOrderCommentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["comment", "work_order__title"]
    filterset_fields = ["work_order", "author"]
    ordering = ["created_at"]

    def get_queryset(self):
        return WorkOrderComment.objects.filter(work_order__school=self.request.user.school).select_related(
            "work_order", "author"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        work_order = serializer.validated_data.get("work_order")
        if work_order and work_order.school_id != self.request.user.school_id:
            raise ValidationError({"work_order": "Work order does not belong to your school."})
        serializer.save(author=self.request.user)


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
    serializer_class = AssetAssignmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["asset__name", "asset__asset_tag", "department"]
    filterset_fields = ["asset", "room", "status"]
    ordering = ["-assigned_date"]

    def get_queryset(self):
        return AssetAssignment.objects.filter(asset__school=self.request.user.school).select_related(
            "asset", "assigned_to", "room"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        asset = serializer.validated_data.get("asset")
        if asset and asset.school_id != self.request.user.school_id:
            raise ValidationError({"asset": "Asset does not belong to your school."})
        serializer.save()


class AssetLifecycleViewSet(viewsets.ModelViewSet):
    serializer_class = AssetLifecycleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["asset__name", "asset__asset_tag", "event", "description"]
    filterset_fields = ["asset", "event"]
    ordering = ["-event_date"]

    def get_queryset(self):
        return AssetLifecycle.objects.filter(asset__school=self.request.user.school).select_related(
            "asset", "performed_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        asset = serializer.validated_data.get("asset")
        if asset and asset.school_id != self.request.user.school_id:
            raise ValidationError({"asset": "Asset does not belong to your school."})
        serializer.save(performed_by=self.request.user)


class WarrantyClaimViewSet(viewsets.ModelViewSet):
    serializer_class = WarrantyClaimSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["claim_number", "asset__name", "asset__asset_tag", "warranty_provider"]
    filterset_fields = ["asset", "status"]
    ordering = ["-claim_date"]

    def get_queryset(self):
        return WarrantyClaim.objects.filter(asset__school=self.request.user.school).select_related(
            "asset", "reported_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        asset = serializer.validated_data.get("asset")
        if asset and asset.school_id != self.request.user.school_id:
            raise ValidationError({"asset": "Asset does not belong to your school."})
        serializer.save(reported_by=self.request.user)


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
    serializer_class = UtilityTrackerSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["building__name", "utility_type", "notes"]
    filterset_fields = ["building", "utility_type"]
    ordering = ["-reading_date"]

    def get_queryset(self):
        return UtilityTracker.objects.filter(building__school=self.request.user.school).select_related(
            "building", "recorded_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        building = serializer.validated_data.get("building")
        if building and building.school_id != self.request.user.school_id:
            raise ValidationError({"building": "Building does not belong to your school."})
        serializer.save(recorded_by=self.request.user)


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
    serializer_class = InfrastructureComplianceRecordSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "regulation_reference", "compliance_type"]
    filterset_fields = ["status", "compliance_type"]
    ordering = ["-next_audit_date"]

    def get_queryset(self):
        return InfrastructureComplianceRecord.objects.filter(school=self.request.user.school).select_related(
            "responsible_person"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


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
    serializer_class = InfrastructureEmergencyPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "plan_type", "description"]
    filterset_fields = ["plan_type", "is_active"]
    ordering = ["title"]

    def get_queryset(self):
        return InfrastructureEmergencyPlan.objects.filter(school=self.request.user.school).select_related("reviewed_by")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InfrastructureReportViewSet(viewsets.ModelViewSet):
    serializer_class = InfrastructureReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "report_type", "description"]
    filterset_fields = ["report_type"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return InfrastructureReport.objects.filter(school=self.request.user.school).select_related("generated_by")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, generated_by=self.request.user)


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
    search_fields = ["camera_name", "camera_id", "building__name", "location_description"]
    filterset_fields = ["building", "status", "recording_enabled"]
    ordering = ["camera_name"]

    def get_queryset(self):
        return CCTVCamera.objects.filter(building__school=self.request.user.school).select_related("building", "room")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        building = serializer.validated_data.get("building")
        if building and building.school_id != self.request.user.school_id:
            raise ValidationError({"building": "Building does not belong to your school."})
        serializer.save()


class AccessControlPointViewSet(viewsets.ModelViewSet):
    serializer_class = AccessControlPointSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["point_name", "building__name", "notes"]
    filterset_fields = ["building", "access_type", "status", "restricted_access"]
    ordering = ["point_name"]

    def get_queryset(self):
        return AccessControlPoint.objects.filter(building__school=self.request.user.school).select_related(
            "building", "room"
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


class PestControlInspectionViewSet(viewsets.ModelViewSet):
    serializer_class = PestControlInspectionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["building__name", "inspector_name", "pests_found"]
    filterset_fields = ["building", "inspection_type", "status"]
    ordering = ["-scheduled_date"]

    def get_queryset(self):
        return PestControlInspection.objects.filter(building__school=self.request.user.school).select_related(
            "building", "room"
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


class PestTreatmentViewSet(viewsets.ModelViewSet):
    serializer_class = PestTreatmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["building__name", "treatment_type", "pest_target", "chemical_name"]
    filterset_fields = ["building"]
    ordering = ["-treatment_date"]

    def get_queryset(self):
        return PestTreatment.objects.filter(building__school=self.request.user.school).select_related(
            "building", "inspection"
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


class WasteCollectionScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = WasteCollectionScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["building__name", "vendor_name", "waste_type"]
    filterset_fields = ["building", "waste_type", "frequency", "is_active"]
    ordering = ["building__name"]

    def get_queryset(self):
        return WasteCollectionSchedule.objects.filter(building__school=self.request.user.school).select_related(
            "building"
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


class GreenInitiativeViewSet(viewsets.ModelViewSet):
    serializer_class = GreenInitiativeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description", "building__name"]
    filterset_fields = ["status", "initiative_type", "building"]
    ordering = ["-start_date"]

    def get_queryset(self):
        return GreenInitiative.objects.filter(school=self.request.user.school).select_related("building", "proposed_by")

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
    search_fields = ["building__name", "notes"]
    filterset_fields = ["building", "leak_detected"]
    ordering = ["-record_date"]

    def get_queryset(self):
        return WaterUsageRecord.objects.filter(building__school=self.request.user.school).select_related("building")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        building = serializer.validated_data.get("building")
        if building and building.school_id != self.request.user.school_id:
            raise ValidationError({"building": "Building does not belong to your school."})
        serializer.save()


class VendorPerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = VendorPerformanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["vendor_contract__vendor_name", "service_type", "comments"]
    filterset_fields = ["vendor_contract", "service_type"]
    ordering = ["-evaluation_date"]

    def get_queryset(self):
        return VendorPerformance.objects.filter(vendor_contract__school=self.request.user.school).select_related(
            "vendor_contract", "evaluator"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        contract = serializer.validated_data.get("vendor_contract")
        if contract and contract.school_id != self.request.user.school_id:
            raise ValidationError({"vendor_contract": "Contract does not belong to your school."})
        serializer.save(evaluator=self.request.user)


class BuildingInspectionViewSet(viewsets.ModelViewSet):
    serializer_class = BuildingInspectionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["building__name", "inspector_name", "findings"]
    filterset_fields = ["building", "inspection_type", "result"]
    ordering = ["-inspection_date"]

    def get_queryset(self):
        return BuildingInspection.objects.filter(building__school=self.request.user.school).select_related(
            "building", "recorded_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        building = serializer.validated_data.get("building")
        if building and building.school_id != self.request.user.school_id:
            raise ValidationError({"building": "Building does not belong to your school."})
        serializer.save(recorded_by=self.request.user)


class InfrastructureAlertViewSet(viewsets.ModelViewSet):
    serializer_class = InfrastructureAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description", "building__name"]
    filterset_fields = ["alert_type", "severity", "status", "building"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return InfrastructureAlert.objects.filter(school=self.request.user.school).select_related(
            "building", "room", "reported_by", "assigned_to"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, reported_by=self.request.user)


class FloorPlanViewSet(viewsets.ModelViewSet):
    serializer_class = FloorPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["building__name", "floor_name", "description"]
    filterset_fields = ["building", "is_current"]
    ordering = ["building__name", "floor_number"]

    def get_queryset(self):
        return FloorPlan.objects.filter(building__school=self.request.user.school).select_related(
            "building", "uploaded_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        building = serializer.validated_data.get("building")
        if building and building.school_id != self.request.user.school_id:
            raise ValidationError({"building": "Building does not belong to your school."})
        serializer.save(uploaded_by=self.request.user)


class RoomEquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = RoomEquipmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "asset_tag", "brand"]
    filterset_fields = ["room", "equipment_type", "status"]
    ordering = ["name"]

    def get_queryset(self):
        return RoomEquipment.objects.filter(room__building__school=self.request.user.school).select_related("room")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        room = serializer.validated_data.get("room")
        if room and room.building.school_id != self.request.user.school_id:
            raise ValidationError({"room": "Room does not belong to your school."})
        serializer.save()


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
    search_fields = ["zone_name", "building__name", "day_of_week"]
    filterset_fields = ["building", "room", "is_active"]
    ordering = ["building__name", "on_time"]

    def get_queryset(self):
        return LightingSchedule.objects.filter(building__school=self.request.user.school).select_related(
            "building", "room"
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


class MaintenanceCostTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceCostTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["building__name", "vendor", "work_order__title"]
    filterset_fields = ["cost_category", "building", "is_approved"]
    ordering = ["-cost_date"]

    def get_queryset(self):
        return MaintenanceCostTracking.objects.filter(school=self.request.user.school).select_related(
            "building", "work_order", "approved_by"
        )

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
    search_fields = ["title", "description", "building__name"]
    filterset_fields = ["status", "priority", "building"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return InfrastructureMaintenanceRequest.objects.filter(school=self.request.user.school).select_related(
            "building", "room", "requested_by", "assigned_to"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, requested_by=self.request.user)
