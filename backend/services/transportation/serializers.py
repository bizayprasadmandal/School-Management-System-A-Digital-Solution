"""Transportation Management serializers."""

from rest_framework import serializers

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


class VehicleSerializer(serializers.ModelSerializer):
    vehicle_type_display = serializers.CharField(source="get_vehicle_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    route_count = serializers.SerializerMethodField()
    maintenance_count = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "plate_number",
            "vehicle_type",
            "vehicle_type_display",
            "model_name",
            "year",
            "capacity",
            "color",
            "chassis_number",
            "engine_number",
            "insurance_number",
            "insurance_expiry",
            "fitness_expiry",
            "status",
            "status_display",
            "notes",
            "is_active",
            "route_count",
            "maintenance_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_route_count(self, obj):
        return getattr(obj, "route_count", obj.assigned_routes.count())

    def get_maintenance_count(self, obj):
        return getattr(obj, "maintenance_count", obj.maintenance_records.count())


class DriverSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True, default=None)

    class Meta:
        model = Driver
        fields = [
            "id",
            "employee",
            "employee_name",
            "user",
            "full_name",
            "phone_number",
            "email",
            "license_number",
            "license_expiry",
            "status",
            "status_display",
            "emergency_contact_name",
            "emergency_contact_phone",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RouteStopSerializer(serializers.ModelSerializer):
    stop_type_display = serializers.CharField(source="get_stop_type_display", read_only=True)

    class Meta:
        model = RouteStop
        fields = [
            "id",
            "route",
            "name",
            "address",
            "landmark",
            "latitude",
            "longitude",
            "stop_order",
            "stop_type",
            "stop_type_display",
            "pickup_time",
            "dropoff_time",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RouteSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate_number", read_only=True, default=None)
    driver_name = serializers.CharField(source="driver.full_name", read_only=True, default=None)
    stops = RouteStopSerializer(many=True, read_only=True)
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = [
            "id",
            "name",
            "description",
            "vehicle",
            "vehicle_plate",
            "driver",
            "driver_name",
            "origin",
            "destination",
            "estimated_duration_minutes",
            "operating_days",
            "is_active",
            "stops",
            "student_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_student_count(self, obj):
        return getattr(obj, "student_count", obj.student_assignments.filter(is_active=True).count())


class RouteStopDetailSerializer(serializers.ModelSerializer):
    """Used for nested CRUD within a Route."""

    class Meta:
        model = RouteStop
        fields = [
            "id",
            "route",
            "name",
            "address",
            "landmark",
            "latitude",
            "longitude",
            "stop_order",
            "stop_type",
            "pickup_time",
            "dropoff_time",
            "is_active",
        ]
        read_only_fields = ["id"]


class StudentRouteSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    route_name = serializers.CharField(source="route.name", read_only=True)
    pickup_stop_name = serializers.CharField(source="pickup_stop.name", read_only=True, default=None)
    dropoff_stop_name = serializers.CharField(source="dropoff_stop.name", read_only=True, default=None)

    class Meta:
        model = StudentRoute
        fields = [
            "id",
            "route",
            "route_name",
            "student",
            "student_name",
            "pickup_stop",
            "pickup_stop_name",
            "dropoff_stop",
            "dropoff_stop_name",
            "service_type",
            "fee_amount",
            "effective_from",
            "effective_to",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleMaintenanceSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate_number", read_only=True)
    maintenance_type_display = serializers.CharField(source="get_maintenance_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    performed_by_name = serializers.CharField(source="performed_by.full_name", read_only=True, default=None)

    class Meta:
        model = VehicleMaintenance
        fields = [
            "id",
            "vehicle",
            "vehicle_plate",
            "maintenance_type",
            "maintenance_type_display",
            "status",
            "status_display",
            "scheduled_date",
            "completed_date",
            "odometer_reading",
            "cost",
            "vendor_name",
            "invoice_number",
            "description",
            "notes",
            "performed_by",
            "performed_by_name",
            "next_service_date",
            "next_service_odometer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransportFeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    fee_type_display = serializers.CharField(source="get_fee_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = TransportFee
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleInsuranceSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate_number", read_only=True)
    insurance_type_display = serializers.CharField(source="get_insurance_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = VehicleInsurance
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DailyTransportAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    route_name = serializers.CharField(source="route.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = DailyTransportAttendance
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TransportIncidentReportSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate_number", read_only=True, default=None)
    driver_name = serializers.CharField(source="driver.full_name", read_only=True, default=None)
    incident_type_display = serializers.CharField(source="get_incident_type_display", read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = TransportIncidentReport
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleInspectionSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate_number", read_only=True)
    inspection_type_display = serializers.CharField(source="get_inspection_type_display", read_only=True)
    result_display = serializers.CharField(source="get_result_display", read_only=True)

    class Meta:
        model = VehicleInspection
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TripScheduleSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate_number", read_only=True, default=None)
    driver_name = serializers.CharField(source="driver.full_name", read_only=True, default=None)
    trip_type_display = serializers.CharField(source="get_trip_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = TripSchedule
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class FuelLogSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate_number", read_only=True)
    fuel_type_display = serializers.CharField(source="get_fuel_type_display", read_only=True)

    class Meta:
        model = FuelLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TransportNotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source="get_notification_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = TransportNotification
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TransportReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)

    class Meta:
        model = TransportReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class VehicleDocumentSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate_number", read_only=True)
    document_type_display = serializers.CharField(source="get_document_type_display", read_only=True)

    class Meta:
        model = VehicleDocument
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
