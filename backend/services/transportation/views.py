"""Transportation Management — Viewsets with school-scoped CRUD."""

import logging

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Driver, Route, RouteStop, StudentRoute, Vehicle, VehicleMaintenance
from .serializers import (
    DriverSerializer,
    RouteSerializer,
    RouteStopDetailSerializer,
    StudentRouteSerializer,
    VehicleMaintenanceSerializer,
    VehicleSerializer,
)

logger = logging.getLogger(__name__)


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["plate_number", "model_name", "chassis_number"]
    filterset_fields = ["vehicle_type", "status", "is_active"]
    ordering_fields = ["plate_number", "year", "capacity"]
    ordering = ["plate_number"]

    def get_queryset(self):
        return Vehicle.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class DriverViewSet(viewsets.ModelViewSet):
    serializer_class = DriverSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["full_name", "phone_number", "license_number"]
    filterset_fields = ["status"]

    def get_queryset(self):
        return Driver.objects.filter(school=self.request.user.school).select_related("employee__user", "user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "origin", "destination"]
    filterset_fields = ["is_active", "vehicle", "driver"]

    def get_queryset(self):
        return (
            Route.objects.filter(school=self.request.user.school)
            .select_related("vehicle", "driver")
            .prefetch_related("stops")
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RouteStopViewSet(viewsets.ModelViewSet):
    serializer_class = RouteStopDetailSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["route", "stop_type", "is_active"]

    def get_queryset(self):
        return RouteStop.objects.filter(route__school=self.request.user.school).select_related("route")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class StudentRouteViewSet(viewsets.ModelViewSet):
    serializer_class = StudentRouteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "route__name"]
    filterset_fields = ["route", "student", "is_active"]

    def get_queryset(self):
        return StudentRoute.objects.filter(route__school=self.request.user.school).select_related(
            "route", "student__user", "pickup_stop", "dropoff_stop"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class VehicleMaintenanceViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleMaintenanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["vendor_name", "invoice_number", "description"]
    filterset_fields = ["vehicle", "maintenance_type", "status"]

    def get_queryset(self):
        return VehicleMaintenance.objects.filter(vehicle__school=self.request.user.school).select_related(
            "vehicle", "performed_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)
