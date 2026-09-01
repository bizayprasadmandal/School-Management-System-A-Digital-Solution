"""Transportation Management — Viewsets with school-scoped CRUD."""

import logging

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import (
    DailyTransportAttendance,
    Driver,
    FuelLog,
    Route,
    RouteStop,
    StudentRoute,
    TransportFee,
    TransportIncidentReport,
    TransportNotification,
    TransportReport,
    TripSchedule,
    Vehicle,
    VehicleDocument,
    VehicleInspection,
    VehicleInsurance,
    VehicleMaintenance,
)
from .serializers import (
    DailyTransportAttendanceSerializer,
    DriverSerializer,
    FuelLogSerializer,
    RouteSerializer,
    RouteStopDetailSerializer,
    StudentRouteSerializer,
    TransportFeeSerializer,
    TransportIncidentReportSerializer,
    TransportNotificationSerializer,
    TransportReportSerializer,
    TripScheduleSerializer,
    VehicleDocumentSerializer,
    VehicleInspectionSerializer,
    VehicleInsuranceSerializer,
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
        return Vehicle.objects.filter(school=self.request.user.school).annotate(
            route_count=Count("assigned_routes", distinct=True),
            maintenance_count=Count("maintenance_records", distinct=True),
        )

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
            .annotate(student_count=Count("student_assignments", filter=Q(student_assignments__is_active=True)))
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


class TransportFeeViewSet(viewsets.ModelViewSet):
    serializer_class = TransportFeeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    filterset_fields = ["student", "route", "fee_type", "status"]

    def get_queryset(self):
        return TransportFee.objects.filter(school=self.request.user.school).select_related("student__user", "route")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class VehicleInsuranceViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleInsuranceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vehicle", "insurance_type", "status"]

    def get_queryset(self):
        return VehicleInsurance.objects.filter(vehicle__school=self.request.user.school).select_related("vehicle")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class DailyTransportAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = DailyTransportAttendanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "route", "date", "status"]

    def get_queryset(self):
        return DailyTransportAttendance.objects.filter(school=self.request.user.school).select_related(
            "student__user", "route", "vehicle"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            recorded_by=self.request.user,
        )


class TransportIncidentReportViewSet(viewsets.ModelViewSet):
    serializer_class = TransportIncidentReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["description", "location"]
    filterset_fields = ["incident_type", "severity", "status"]

    def get_queryset(self):
        return TransportIncidentReport.objects.filter(school=self.request.user.school).select_related(
            "vehicle", "route", "driver"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            reported_by=self.request.user,
        )


class VehicleInspectionViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleInspectionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vehicle", "inspection_type", "result"]

    def get_queryset(self):
        return VehicleInspection.objects.filter(vehicle__school=self.request.user.school).select_related("vehicle")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class TripScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = TripScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "destination"]
    filterset_fields = ["trip_type", "status"]

    def get_queryset(self):
        return TripSchedule.objects.filter(school=self.request.user.school).select_related("vehicle", "driver", "route")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            created_by=self.request.user,
        )


class FuelLogViewSet(viewsets.ModelViewSet):
    serializer_class = FuelLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vehicle", "fuel_type"]

    def get_queryset(self):
        return FuelLog.objects.filter(vehicle__school=self.request.user.school).select_related("vehicle")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(filled_by=self.request.user)


class TransportNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = TransportNotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["notification_type", "status"]

    def get_queryset(self):
        return TransportNotification.objects.filter(school=self.request.user.school).select_related("route", "vehicle")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            sent_by=self.request.user,
        )


class TransportReportViewSet(viewsets.ModelViewSet):
    serializer_class = TransportReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report_type"]

    def get_queryset(self):
        return TransportReport.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            generated_by=self.request.user,
        )


class VehicleDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleDocumentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vehicle", "document_type", "is_valid"]

    def get_queryset(self):
        return VehicleDocument.objects.filter(vehicle__school=self.request.user.school).select_related("vehicle")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()
