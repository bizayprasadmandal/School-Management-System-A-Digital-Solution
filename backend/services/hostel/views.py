"""Hostel / Accommodation Management — Viewsets with school-scoped CRUD."""

import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Hostel, HostelRoom, HostelAllocation, HostelFee, HostelVisitor
from .serializers import (
    HostelSerializer, HostelRoomSerializer, HostelAllocationSerializer,
    HostelFeeSerializer, HostelVisitorSerializer,
)
from core.permissions import IsSchoolAdmin, IsSchoolMember
from core.pagination import StandardResultsSetPagination

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
        return HostelRoom.objects.filter(
            hostel__school=self.request.user.school
        ).select_related("hostel").prefetch_related("allocations")

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
    search_fields = ["student__user__full_name", "room__room_number"]
    filterset_fields = ["room", "student", "status", "is_paid"]

    def get_queryset(self):
        return HostelAllocation.objects.filter(
            room__hostel__school=self.request.user.school
        ).select_related("student__user", "room__hostel", "allocated_by")

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
        return HostelVisitor.objects.filter(
            hostel__school=self.request.user.school
        ).select_related("hostel", "student_visited__user", "checked_in_by")

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
