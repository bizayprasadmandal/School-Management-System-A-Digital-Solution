"""Hostel / Accommodation Management — Viewsets with school-scoped CRUD."""

import logging

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    CheckoutProcess,
    CommonAreaBooking,
    ComplaintManagement,
    EmergencyContact,
    Hostel,
    HostelAllocation,
    HostelAsset,
    HostelAssetTransfer,
    HostelAttendance,
    HostelAttendanceAlert,
    HostelEmergencyDrill,
    HostelEmergencyProtocol,
    HostelEvent,
    HostelEventParticipant,
    HostelFee,
    HostelFeedback,
    HostelFeePayment,
    HostelInspectionSchedule,
    HostelNotification,
    HostelReport,
    HostelRoom,
    HostelVisitor,
    InventoryManagement,
    LaundryService,
    LeaveManagement,
    MessAttendance,
    MessDietaryRequest,
    MessFeedback,
    MessManagement,
    MessMenuPlan,
    RoomInspection,
    RoomKey,
    RoomMaintenance,
    RoommateAssignment,
    RoommateMatchRequest,
    RoommatePreference,
    RoomTransfer,
    VisitorPass,
    WellnessCheck,
)
from .serializers import (
    CheckoutProcessSerializer,
    CommonAreaBookingSerializer,
    ComplaintManagementSerializer,
    EmergencyContactSerializer,
    HostelAllocationSerializer,
    HostelAssetSerializer,
    HostelAssetTransferSerializer,
    HostelAttendanceAlertSerializer,
    HostelAttendanceSerializer,
    HostelEmergencyDrillSerializer,
    HostelEmergencyProtocolSerializer,
    HostelEventParticipantSerializer,
    HostelEventSerializer,
    HostelFeedbackSerializer,
    HostelFeePaymentSerializer,
    HostelFeeSerializer,
    HostelInspectionScheduleSerializer,
    HostelNotificationSerializer,
    HostelReportSerializer,
    HostelRoomSerializer,
    HostelSerializer,
    HostelVisitorSerializer,
    InventoryManagementSerializer,
    LaundryServiceSerializer,
    LeaveManagementSerializer,
    MessAttendanceSerializer,
    MessDietaryRequestSerializer,
    MessFeedbackSerializer,
    MessManagementSerializer,
    MessMenuPlanSerializer,
    RoomInspectionSerializer,
    RoomKeySerializer,
    RoomMaintenanceSerializer,
    RoommateAssignmentSerializer,
    RoommateMatchRequestSerializer,
    RoommatePreferenceSerializer,
    RoomTransferSerializer,
    VisitorPassSerializer,
    WellnessCheckSerializer,
)

logger = logging.getLogger(__name__)


class HostelViewSet(viewsets.ModelViewSet):
    serializer_class = HostelSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "code", "address"]
    filterset_fields = ["gender", "status"]

    def get_queryset(self):
        return Hostel.objects.filter(school=self.request.user.school).prefetch_related("rooms")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class HostelRoomViewSet(viewsets.ModelViewSet):
    serializer_class = HostelRoomSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["room_number"]
    filterset_fields = ["hostel", "floor", "room_type", "is_active", "has_ac"]

    def get_queryset(self):
        return (
            HostelRoom.objects.filter(hostel__school=self.request.user.school)
            .select_related("hostel")
            .prefetch_related("allocations")
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class HostelAllocationViewSet(viewsets.ModelViewSet):
    serializer_class = HostelAllocationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "room__room_number"]
    filterset_fields = ["room", "student", "status", "is_paid"]

    def get_queryset(self):
        return HostelAllocation.objects.filter(room__hostel__school=self.request.user.school).select_related(
            "student__user", "room__hostel", "allocated_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(allocated_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="checkout")
    def checkout(self, request, pk=None):
        """Check out a student from their hostel room."""
        allocation = self.get_object()
        if allocation.status != HostelAllocation.Status.ACTIVE:
            return Response({"detail": "Student is already checked out."}, status=400)
        allocation.status = HostelAllocation.Status.CHECKED_OUT
        allocation.check_out_date = request.data.get("check_out_date", timezone.now().date())
        allocation.notes = request.data.get("notes", allocation.notes)
        allocation.save()
        return Response(HostelAllocationSerializer(allocation).data)


class HostelFeeViewSet(viewsets.ModelViewSet):
    serializer_class = HostelFeeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["hostel", "room_type", "is_active", "billing_cycle"]

    def get_queryset(self):
        return HostelFee.objects.filter(school=self.request.user.school).select_related("hostel")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class HostelVisitorViewSet(viewsets.ModelViewSet):
    serializer_class = HostelVisitorSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["visitor_name", "phone", "purpose"]
    filterset_fields = ["hostel", "student_visited"]

    def get_queryset(self):
        return HostelVisitor.objects.filter(hostel__school=self.request.user.school).select_related(
            "hostel", "student_visited__user", "checked_in_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(checked_in_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="checkout")
    def checkout_visitor(self, request, pk=None):
        """Record visitor checkout time."""
        visitor = self.get_object()
        visitor.out_time = timezone.now()
        visitor.notes = request.data.get("notes", visitor.notes)
        visitor.save()
        return Response(HostelVisitorSerializer(visitor).data)


# =============================================================================
# Room Maintenance ViewSets
# =============================================================================


class RoomMaintenanceViewSet(viewsets.ModelViewSet):
    serializer_class = RoomMaintenanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["room__room_number", "description"]
    filterset_fields = ["room", "maintenance_type", "status", "priority"]
    ordering_fields = ["reported_date", "scheduled_date"]
    ordering = ["-reported_date"]

    def get_queryset(self):
        return RoomMaintenance.objects.filter(room__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Hostel Attendance ViewSets
# =============================================================================


class HostelAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = HostelAttendanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["allocation__student__user__first_name", "allocation__student__user__last_name"]
    filterset_fields = ["allocation", "status", "date", "is_in_campus"]
    ordering_fields = ["date"]
    ordering = ["-date"]

    def get_queryset(self):
        return HostelAttendance.objects.filter(allocation__room__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


# =============================================================================
# Leave Management ViewSets
# =============================================================================


class LeaveManagementViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["allocation__student__user__first_name", "allocation__student__user__last_name", "reason"]
    filterset_fields = ["allocation", "leave_type", "status"]
    ordering_fields = ["from_date", "created_at"]
    ordering = ["-from_date"]

    def get_queryset(self):
        return LeaveManagement.objects.filter(allocation__room__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a leave request."""

        leave = self.get_object()
        if leave.status != LeaveManagement.Status.PENDING:
            return Response({"detail": "Only pending leave requests can be approved."}, status=400)
        leave.status = LeaveManagement.Status.APPROVED
        leave.approved_by = request.user
        leave.approved_at = timezone.now()
        leave.save(update_fields=["status", "approved_by", "approved_at"])
        return Response(LeaveManagementSerializer(leave).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a leave request."""
        leave = self.get_object()
        if leave.status != LeaveManagement.Status.PENDING:
            return Response({"detail": "Only pending leave requests can be rejected."}, status=400)
        leave.status = LeaveManagement.Status.REJECTED
        leave.rejection_reason = request.data.get("reason", "")
        leave.save(update_fields=["status", "rejection_reason"])
        return Response(LeaveManagementSerializer(leave).data)


# =============================================================================
# Mess Management ViewSets
# =============================================================================


class MessAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = MessAttendanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["mess_menu", "allocation", "status"]

    def get_queryset(self):
        return MessAttendance.objects.filter(mess_menu__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class MessManagementViewSet(viewsets.ModelViewSet):
    serializer_class = MessManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["description"]
    filterset_fields = ["hostel", "meal_type", "is_vegetarian", "date"]
    ordering_fields = ["date"]
    ordering = ["-date"]

    def get_queryset(self):
        return MessManagement.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# =============================================================================
# Complaint Management ViewSets
# =============================================================================


class ComplaintManagementViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["hostel", "complaint_type", "status", "priority"]
    ordering_fields = ["created_at", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return ComplaintManagement.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Room Inspection ViewSets
# =============================================================================


class RoomInspectionViewSet(viewsets.ModelViewSet):
    serializer_class = RoomInspectionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["room__room_number"]
    filterset_fields = ["room", "inspection_type", "status", "has_issues"]
    ordering_fields = ["scheduled_date"]
    ordering = ["-scheduled_date"]

    def get_queryset(self):
        return RoomInspection.objects.filter(room__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(inspected_by=self.request.user)


# =============================================================================
# Inventory Management ViewSets
# =============================================================================


class InventoryManagementViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["item_name", "asset_tag"]
    filterset_fields = ["hostel", "item_category", "status"]
    ordering_fields = ["item_name", "created_at"]
    ordering = ["item_name"]

    def get_queryset(self):
        return InventoryManagement.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Hostel Reports ViewSets
# =============================================================================


class HostelReportViewSet(viewsets.ModelViewSet):
    serializer_class = HostelReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "summary"]
    filterset_fields = ["hostel", "report_type", "status"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return HostelReport.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


# =============================================================================
# Emergency Contacts ViewSets
# =============================================================================


class EmergencyContactViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyContactSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "phone_primary"]
    filterset_fields = ["hostel", "contact_type", "is_active"]
    ordering_fields = ["contact_type", "name"]
    ordering = ["contact_type", "name"]

    def get_queryset(self):
        return EmergencyContact.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Room Transfer ViewSets
# =============================================================================


class RoomTransferViewSet(viewsets.ModelViewSet):
    serializer_class = RoomTransferSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["allocation__student__user__first_name", "allocation__student__user__last_name", "reason"]
    filterset_fields = ["allocation", "status", "from_room", "to_room"]
    ordering_fields = ["created_at", "transfer_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return RoomTransfer.objects.filter(allocation__room__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a room transfer."""

        transfer = self.get_object()
        if transfer.status != RoomTransfer.Status.PENDING:
            return Response({"detail": "Only pending transfers can be approved."}, status=400)
        transfer.status = RoomTransfer.Status.APPROVED
        transfer.approved_by = request.user
        transfer.approved_at = timezone.now()
        transfer.save(update_fields=["status", "approved_by", "approved_at"])
        return Response(RoomTransferSerializer(transfer).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a room transfer."""
        transfer = self.get_object()
        if transfer.status != RoomTransfer.Status.PENDING:
            return Response({"detail": "Only pending transfers can be rejected."}, status=400)
        transfer.status = RoomTransfer.Status.REJECTED
        transfer.rejection_reason = request.data.get("reason", "")
        transfer.save(update_fields=["status", "rejection_reason"])
        return Response(RoomTransferSerializer(transfer).data)


# =============================================================================
# Checkout Process ViewSets
# =============================================================================


class CheckoutProcessViewSet(viewsets.ModelViewSet):
    serializer_class = CheckoutProcessSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["allocation__student__user__first_name", "allocation__student__user__last_name"]
    filterset_fields = ["allocation", "status", "room_inspected", "keys_returned"]
    ordering_fields = ["checkout_date", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return CheckoutProcess.objects.filter(allocation__room__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Hostel Notifications ViewSets
# =============================================================================


class HostelNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = HostelNotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "message"]
    filterset_fields = ["hostel", "notification_type", "status", "is_priority"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return HostelNotification.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# =============================================================================
# Hostel Feedback ViewSets
# =============================================================================


class HostelFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = HostelFeedbackSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["comment", "suggestion"]
    filterset_fields = ["hostel", "feedback_type", "rating", "is_anonymous"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["school_admin", "super_admin"]:
            return HostelFeedback.objects.filter(hostel__school=user.school)
        # Students see their own feedback
        return HostelFeedback.objects.filter(hostel__school=user.school, allocation__student__user=user)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# ── Additional ViewSets (module expansion) ──


class RoommatePreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = RoommatePreferenceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return RoommatePreference.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RoommateAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = RoommateAssignmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return RoommateAssignment.objects.filter(room__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class RoomKeyViewSet(viewsets.ModelViewSet):
    serializer_class = RoomKeySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return RoomKey.objects.filter(room__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class LaundryServiceViewSet(viewsets.ModelViewSet):
    serializer_class = LaundryServiceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return LaundryService.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CommonAreaBookingViewSet(viewsets.ModelViewSet):
    serializer_class = CommonAreaBookingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return CommonAreaBooking.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class WellnessCheckViewSet(viewsets.ModelViewSet):
    serializer_class = WellnessCheckSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return WellnessCheck.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class VisitorPassViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorPassSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return VisitorPass.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RoommateMatchRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RoommateMatchRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return RoommateMatchRequest.objects.filter(requester__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class MessMenuPlanViewSet(viewsets.ModelViewSet):
    serializer_class = MessMenuPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return MessMenuPlan.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class MessDietaryRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MessDietaryRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return MessDietaryRequest.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class HostelAssetViewSet(viewsets.ModelViewSet):
    serializer_class = HostelAssetSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return HostelAsset.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class HostelAssetTransferViewSet(viewsets.ModelViewSet):
    serializer_class = HostelAssetTransferSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return HostelAssetTransfer.objects.filter(asset__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class HostelEventViewSet(viewsets.ModelViewSet):
    serializer_class = HostelEventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return HostelEvent.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class HostelEventParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = HostelEventParticipantSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return HostelEventParticipant.objects.filter(event__hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class HostelEmergencyProtocolViewSet(viewsets.ModelViewSet):
    serializer_class = HostelEmergencyProtocolSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return HostelEmergencyProtocol.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class HostelEmergencyDrillViewSet(viewsets.ModelViewSet):
    serializer_class = HostelEmergencyDrillSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return HostelEmergencyDrill.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class HostelFeePaymentViewSet(viewsets.ModelViewSet):
    serializer_class = HostelFeePaymentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return HostelFeePayment.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        payment = serializer.save(school=self.request.user.school)
        self._post_to_books(payment, self.request.user)

    def perform_update(self, serializer):
        payment = serializer.save()
        self._post_to_books(payment, self.request.user)

    def _post_to_books(self, payment, user):
        """Post a paid/partial hostel fee payment to the revenue books."""
        from services.fees.ledger import post_revenue

        if payment.status not in (HostelFeePayment.Status.PAID, HostelFeePayment.Status.PARTIAL):
            return
        allocation = payment.allocation
        student = getattr(allocation, "student", None)
        post_revenue(
            school=payment.school,
            amount=payment.amount_paid,
            reference_type="hostel_fee_payment",
            reference_id=str(payment.id),
            description=(f"Hostel fee payment — {student or allocation} " f"({payment.billing_period or 'period'})"),
            student=student,
            payment_method=payment.payment_method,
            user=user,
        )


class HostelInspectionScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = HostelInspectionScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return HostelInspectionSchedule.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class MessFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = MessFeedbackSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return MessFeedback.objects.filter(hostel__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class HostelAttendanceAlertViewSet(viewsets.ModelViewSet):
    serializer_class = HostelAttendanceAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return HostelAttendanceAlert.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
