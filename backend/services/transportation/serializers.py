"""Serializers for transportation."""

from rest_framework import serializers

from .models import (
    BusTracking,
    DailyTransportAttendance,
    Driver,
    DriverLicense,
    DriverPerformance,
    FuelLog,
    GeofenceAlert,
    GeofenceZone,
    ParentTransportAccess,
    Route,
    RouteOptimization,
    RouteStop,
    StopETA,
    StudentRoute,
    StudentTransportProfile,
    TransportAlert,
    TransportationDailyReport,
    TransportAuditLog,
    TransportBudget,
    TransportComplianceRecord,
    TransportDriverSchedule,
    TransportEmergencyContact,
    TransportFee,
    TransportFeeStructure,
    TransportIncident,
    TransportIncidentReport,
    TransportMonthlyReport,
    TransportNotification,
    TransportReport,
    TransportSchedule,
    TripSchedule,
    Vehicle,
    VehicleAssignmentLog,
    VehicleConditionReport,
    VehicleDocument,
    VehicleGPSLog,
    VehicleInspection,
    VehicleInsurance,
    VehicleMaintenance,
    VehiclePool,
)


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "school",
            "id",
            "plate_number",
            "vehicle_type",
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
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]

    def validate_plate_number(self, value):
        # Plate numbers are globally unique — a duplicate would hit the DB
        # constraint and 500; surface a clean 400 instead.
        if (
            Vehicle.objects.filter(plate_number__iexact=value)
            .exclude(pk=self.instance.pk if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(f"A vehicle with plate '{value}' already exists.")
        return value


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            "id",
            "school",
            "id",
            "employee",
            "user",
            "full_name",
            "phone_number",
            "email",
            "license_number",
            "license_expiry",
            "status",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "vehicle",
            "driver",
            "origin",
            "destination",
            "estimated_duration_minutes",
            "operating_days",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]

    def validate(self, attrs):
        # Duplicate (school, name) would hit the DB unique constraint → 500.
        name = attrs.get("name")
        if name:
            user = self.context["request"].user
            if Route.objects.filter(school_id=user.school_id, name__iexact=name).exists():
                raise serializers.ValidationError({"detail": f"A route named '{name}' already exists."})
        return attrs


class RouteStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteStop
        fields = [
            "id",
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
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRoute
        fields = [
            "id",
            "id",
            "route",
            "student",
            "pickup_stop",
            "dropoff_stop",
            "service_type",
            "fee_amount",
            "effective_from",
            "effective_to",
            "is_active",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMaintenance
        fields = [
            "id",
            "id",
            "vehicle",
            "maintenance_type",
            "status",
            "scheduled_date",
            "completed_date",
            "odometer_reading",
            "cost",
            "vendor_name",
            "invoice_number",
            "description",
            "notes",
            "performed_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransportFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportFee
        fields = [
            "id",
            "school",
            "id",
            "student",
            "route",
            "fee_type",
            "amount",
            "paid_amount",
            "status",
            "due_date",
            "paid_date",
            "academic_year",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleInsurance
        fields = [
            "id",
            "id",
            "vehicle",
            "insurance_type",
            "provider",
            "policy_number",
            "start_date",
            "end_date",
            "premium_amount",
            "coverage_amount",
            "status",
            "document_url",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DailyTransportAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTransportAttendance
        fields = [
            "id",
            "school",
            "id",
            "student",
            "route",
            "vehicle",
            "date",
            "attendance_type",
            "status",
            "pickup_time",
            "dropoff_time",
            "pickup_stop",
        ]
        read_only_fields = ["id", "created_at"]


class TransportIncidentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportIncidentReport
        fields = [
            "id",
            "school",
            "id",
            "incident_type",
            "severity",
            "status",
            "vehicle",
            "route",
            "driver",
            "incident_date",
            "incident_time",
            "location",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleInspection
        fields = [
            "id",
            "id",
            "vehicle",
            "inspection_type",
            "inspection_date",
            "inspector_name",
            "result",
            "odometer_reading",
            "exterior_check",
            "interior_check",
            "tires_check",
            "lights_check",
            "brakes_check",
            "signals_check",
            "emergency_equipment",
        ]
        read_only_fields = ["id", "created_at"]


class TripScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripSchedule
        fields = [
            "id",
            "school",
            "id",
            "title",
            "trip_type",
            "destination",
            "trip_date",
            "departure_time",
            "return_time",
            "vehicle",
            "driver",
            "route",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FuelLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelLog
        fields = [
            "id",
            "id",
            "vehicle",
            "fuel_type",
            "fill_date",
            "odometer_reading",
            "liters",
            "cost_per_liter",
            "total_cost",
            "station_name",
            "invoice_number",
            "filled_by",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TransportNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportNotification
        fields = [
            "id",
            "school",
            "id",
            "notification_type",
            "title",
            "message",
            "route",
            "vehicle",
            "recipients",
            "status",
            "sent_at",
            "sent_by",
        ]
        read_only_fields = ["id", "created_at"]


class TransportReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportReport
        fields = [
            "id",
            "school",
            "id",
            "title",
            "report_type",
            "date_from",
            "date_to",
            "report_data",
            "summary",
            "generated_by",
            "file_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class VehicleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDocument
        fields = [
            "id",
            "id",
            "vehicle",
            "document_type",
            "document_name",
            "document_number",
            "issue_date",
            "expiry_date",
            "issued_by",
            "document_url",
            "notes",
            "is_valid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleGPSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleGPSLog
        fields = [
            "id",
            "id",
            "vehicle",
            "latitude",
            "longitude",
            "speed_kmh",
            "heading",
            "timestamp",
            "ignition_on",
            "battery_level",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class GeofenceZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeofenceZone
        fields = [
            "id",
            "school",
            "name",
            "zone_type",
            "center_latitude",
            "center_longitude",
            "radius_meters",
            "polygon_coordinates",
            "is_active",
            "alert_on_entry",
            "alert_on_exit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class GeofenceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeofenceAlert
        fields = [
            "id",
            "id",
            "vehicle",
            "zone",
            "gps_log",
            "alert_type",
            "status",
            "description",
            "speed_recorded",
            "speed_limit",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BusTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusTracking
        fields = [
            "id",
            "id",
            "vehicle",
            "route",
            "status",
            "scheduled_start",
            "scheduled_end",
            "actual_start",
            "actual_end",
            "current_stop",
            "next_stop",
            "estimated_arrival",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StopETASerializer(serializers.ModelSerializer):
    class Meta:
        model = StopETA
        fields = [
            "id",
            "id",
            "tracking",
            "stop",
            "scheduled_time",
            "estimated_time",
            "actual_time",
            "students_expected",
            "students_picked_up",
            "students_dropped",
            "delay_minutes",
            "delay_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DriverLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLicense
        fields = [
            "id",
            "id",
            "driver",
            "license_number",
            "license_type",
            "issue_date",
            "expiry_date",
            "issuing_authority",
            "endorsements",
            "restrictions",
            "license_image",
            "is_valid",
            "suspension_reason",
            "suspension_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DriverPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverPerformance
        fields = [
            "id",
            "id",
            "driver",
            "evaluation_date",
            "evaluator",
            "safety_rating",
            "punctuality_rating",
            "vehicle_care_rating",
            "student_interaction_rating",
            "overall_rating",
            "total_trips",
            "accidents",
            "complaints",
            "compliments",
        ]
        read_only_fields = ["id", "created_at"]


class VehicleConditionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleConditionReport
        fields = [
            "id",
            "id",
            "vehicle",
            "driver",
            "report_type",
            "report_date",
            "tires_condition",
            "brakes_condition",
            "lights_condition",
            "mirrors_condition",
            "body_condition",
            "interior_condition",
            "fuel_level",
            "mileage",
        ]
        read_only_fields = ["id", "created_at"]


class RouteOptimizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteOptimization
        fields = [
            "id",
            "school",
            "id",
            "route",
            "optimization_date",
            "original_distance_km",
            "original_time_minutes",
            "original_fuel_cost",
            "optimized_distance_km",
            "optimized_time_minutes",
            "optimized_fuel_cost",
            "distance_saved_km",
            "time_saved_minutes",
            "fuel_saved",
        ]
        read_only_fields = ["id", "created_at"]


class TransportationDailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportationDailyReport
        fields = [
            "id",
            "school",
            "id",
            "date",
            "total_vehicles_active",
            "total_trips_completed",
            "total_routes_served",
            "total_students_transport",
            "avg_occupancy_rate",
            "total_fuel_consumed",
            "total_fuel_cost",
            "total_incidents",
            "total_delays",
            "avg_delay_minutes",
            "vehicles_maintained",
        ]
        read_only_fields = ["id", "created_at"]


class ParentTransportAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentTransportAccess
        fields = [
            "id",
            "school",
            "id",
            "parent",
            "student",
            "tracking_enabled",
            "notifications_enabled",
            "email_alerts",
            "sms_alerts",
            "alert_pickup",
            "alert_dropoff",
            "alert_delay",
            "alert_incident",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransportComplianceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportComplianceRecord
        fields = [
            "id",
            "school",
            "id",
            "compliance_type",
            "status",
            "vehicle",
            "driver",
            "document_number",
            "issue_date",
            "expiry_date",
            "issued_by",
            "document_file",
            "alert_days_before",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentTransportProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTransportProfile
        fields = [
            "id",
            "school",
            "id",
            "student",
            "assigned_route",
            "assigned_stop",
            "needs_morning",
            "needs_evening",
            "has_disability",
            "disability_notes",
            "needs_wheelchair",
            "needs_escort",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransportAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportAlert
        fields = [
            "id",
            "school",
            "id",
            "vehicle",
            "route",
            "alert_type",
            "severity",
            "status",
            "title",
            "description",
            "affected_students",
            "affected_routes",
            "estimated_delay_minutes",
        ]
        read_only_fields = ["id", "created_at"]


class VehiclePoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePool
        fields = [
            "id",
            "school",
            "id",
            "vehicle",
            "pool_type",
            "status",
            "booked_by",
            "purpose",
            "destination",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportSchedule
        fields = [
            "id",
            "school",
            "id",
            "route",
            "day_of_week",
            "pickup_start",
            "pickup_end",
            "dropoff_start",
            "dropoff_end",
            "vehicle",
            "driver",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransportFeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportFeeStructure
        fields = [
            "id",
            "school",
            "id",
            "name",
            "fee_type",
            "amount",
            "route",
            "min_distance_km",
            "max_distance_km",
            "sibling_discount",
            "early_bird_discount",
            "is_active",
            "academic_year",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransportIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportIncident
        fields = [
            "id",
            "school",
            "id",
            "vehicle",
            "route",
            "driver",
            "incident_type",
            "severity",
            "status",
            "description",
            "location",
            "incident_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransportBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportBudget
        fields = [
            "id",
            "school",
            "id",
            "academic_year",
            "fuel_budget",
            "maintenance_budget",
            "insurance_budget",
            "salary_budget",
            "new_vehicle_budget",
            "miscellaneous_budget",
            "total_budget",
            "fuel_spent",
            "maintenance_spent",
            "insurance_spent",
            "salary_spent",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransportAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportAuditLog
        fields = [
            "id",
            "school",
            "id",
            "user",
            "action_type",
            "target_model",
            "target_id",
            "description",
            "old_values",
            "new_values",
            "ip_address",
            "timestamp",
        ]
        read_only_fields = ["id"]


class TransportMonthlyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportMonthlyReport
        fields = [
            "id",
            "school",
            "id",
            "month",
            "year",
            "total_operational_days",
            "total_trips",
            "total_routes_active",
            "vehicles_active",
            "vehicles_maintained",
            "avg_fleet_age_years",
            "total_students_served",
            "avg_daily_riders",
            "total_fuel_liters",
            "total_fuel_cost",
        ]
        read_only_fields = ["id", "created_at"]


class TransportEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportEmergencyContact
        fields = [
            "id",
            "school",
            "id",
            "name",
            "role",
            "phone",
            "alternate_phone",
            "email",
            "organization",
            "is_primary",
            "is_active",
            "priority_order",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleAssignmentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleAssignmentLog
        fields = [
            "id",
            "id",
            "vehicle",
            "route",
            "driver",
            "assignment_date",
            "assignment_type",
            "start_time",
            "end_time",
            "purpose",
            "assigned_by",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class TransportDriverScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportDriverSchedule
        fields = [
            "id",
            "school",
            "id",
            "driver",
            "date",
            "shift_type",
            "start_time",
            "end_time",
            "routes_assigned",
            "total_distance_km",
            "total_hours",
            "overtime_hours",
            "is_available",
            "is_on_leave",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ── Serializers restored from original module (expansion regression fix) ──


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
