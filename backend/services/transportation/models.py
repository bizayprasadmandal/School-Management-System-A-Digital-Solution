"""Transportation Management — Vehicles, routes, student assignments, maintenance."""

import uuid

from django.conf import settings
from django.db import models
from services.auth.models import School, User
from services.hr.models import Employee


class Vehicle(models.Model):
    """School vehicles (buses, vans) used for student transportation."""

    class VehicleType(models.TextChoices):
        BUS = "bus", "Bus"
        MINI_BUS = "mini_bus", "Mini Bus"
        VAN = "van", "Van"
        SUV = "suv", "SUV"
        SEDAN = "sedan", "Sedan"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        IN_MAINTENANCE = "in_maintenance", "In Maintenance"
        RETIRED = "retired", "Retired"
        OUT_OF_SERVICE = "out_of_service", "Out of Service"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="vehicles")
    plate_number = models.CharField(max_length=30, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices, default=VehicleType.BUS)
    model_name = models.CharField(max_length=100, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    capacity = models.PositiveSmallIntegerField(help_text="Maximum number of students")
    color = models.CharField(max_length=50, blank=True)
    chassis_number = models.CharField(max_length=50, blank=True)
    engine_number = models.CharField(max_length=50, blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    fitness_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_vehicles"
        ordering = ["plate_number"]

    def __str__(self):
        return f"{self.plate_number} ({self.get_vehicle_type_display()})"


class Driver(models.Model):
    """Drivers assigned to school vehicles — linked to Employee or standalone."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On Leave"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="drivers")
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driver_records",
        help_text="Link to HR employee record if applicable",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driver_profiles",
    )
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_drivers"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Route(models.Model):
    """Bus routes with start/end points and assigned vehicle/driver."""

    class WeekDay(models.TextChoices):
        MONDAY = "monday", "Monday"
        TUESDAY = "tuesday", "Tuesday"
        WEDNESDAY = "wednesday", "Wednesday"
        THURSDAY = "thursday", "Thursday"
        FRIDAY = "friday", "Friday"
        SATURDAY = "saturday", "Saturday"
        SUNDAY = "sunday", "Sunday"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_routes")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_routes",
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_routes",
    )
    origin = models.CharField(max_length=255, help_text="Starting point / depot")
    destination = models.CharField(max_length=255, help_text="School location")
    estimated_duration_minutes = models.PositiveSmallIntegerField(default=30)
    operating_days = models.CharField(
        max_length=100,
        blank=True,
        help_text="Comma-separated days: monday,tuesday,wednesday,thursday,friday",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_routes"
        unique_together = [("school", "name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class RouteStop(models.Model):
    """Individual stops along a route with pickup/dropoff times and order."""

    class StopType(models.TextChoices):
        PICKUP = "pickup", "Pickup"
        DROPOFF = "dropoff", "Dropoff"
        BOTH = "both", "Both"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="stops",
    )
    name = models.CharField(max_length=200, help_text="e.g. Main Gate, City Center")
    address = models.CharField(max_length=255, blank=True)
    landmark = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    stop_order = models.PositiveSmallIntegerField(help_text="Order along the route (1 = first)")
    stop_type = models.CharField(max_length=20, choices=StopType.choices, default=StopType.BOTH)
    pickup_time = models.TimeField(null=True, blank=True, help_text="Estimated pickup time at this stop")
    dropoff_time = models.TimeField(null=True, blank=True, help_text="Estimated dropoff time at this stop")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_route_stops"
        ordering = ["route", "stop_order"]
        unique_together = [("route", "stop_order")]

    def __str__(self):
        return f"{self.name} (Stop #{self.stop_order})"


class StudentRoute(models.Model):
    """Many-to-many relationship assigning students to specific route stops."""

    class PickupDropoff(models.TextChoices):
        PICKUP = "pickup", "Pickup Only"
        DROPOFF = "dropoff", "Dropoff Only"
        BOTH = "both", "Both"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="student_assignments")
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="transport_assignments",
    )
    pickup_stop = models.ForeignKey(
        RouteStop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pickup_students",
    )
    dropoff_stop = models.ForeignKey(
        RouteStop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dropoff_students",
    )
    service_type = models.CharField(
        max_length=20,
        choices=PickupDropoff.choices,
        default=PickupDropoff.BOTH,
    )
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_student_assignments"
        unique_together = [("route", "student", "effective_from")]
        ordering = ["route", "student"]

    def __str__(self):
        return f"{self.student} on {self.route}"


class VehicleMaintenance(models.Model):
    """Maintenance and service records for vehicles."""

    class MaintenanceType(models.TextChoices):
        ROUTINE = "routine", "Routine Service"
        REPAIR = "repair", "Repair"
        INSPECTION = "inspection", "Inspection"
        TIRE = "tire", "Tire Change"
        ENGINE = "engine", "Engine Service"
        BODY = "body", "Body Work"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )
    maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    odometer_reading = models.PositiveIntegerField(null=True, blank=True, help_text="Odometer at service (km)")
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vendor_name = models.CharField(max_length=150, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_maintenance",
    )
    next_service_date = models.DateField(null=True, blank=True)
    next_service_odometer = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_maintenance"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.get_maintenance_type_display()} ({self.scheduled_date})"


class TransportFee(models.Model):
    """Transportation fees for students."""

    class FeeType(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        TERM = "term", "Term"
        ANNUAL = "annual", "Annual"
        ONE_TIME = "one_time", "One-Time"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        WAIVED = "waived", "Waived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_fees")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="transport_fees")
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    fee_type = models.CharField(max_length=20, choices=FeeType.choices, default=FeeType.MONTHLY)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    academic_year = models.ForeignKey("students.AcademicYear", on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_fees"
        ordering = ["-due_date"]

    def __str__(self):
        return f"{self.student} - {self.get_fee_type_display()} ({self.amount})"


class VehicleInsurance(models.Model):
    """Vehicle insurance tracking."""

    class InsuranceType(models.TextChoices):
        COMPREHENSIVE = "comprehensive", "Comprehensive"
        THIRD_PARTY = "third_party", "Third Party"
        LIABILITY = "liability", "Liability"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        PENDING_RENEWAL = "pending_renewal", "Pending Renewal"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="insurance_records")
    insurance_type = models.CharField(max_length=20, choices=InsuranceType.choices, default=InsuranceType.COMPREHENSIVE)
    provider = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    document_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_vehicle_insurance"
        ordering = ["-end_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.provider} ({self.policy_number})"


class DailyTransportAttendance(models.Model):
    """Daily student attendance on transport."""

    class AttendanceType(models.TextChoices):
        PICKUP = "pickup", "Pickup"
        DROPOFF = "dropoff", "Dropoff"
        BOTH = "both", "Both"

    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_attendance")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="transport_attendance")
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    attendance_type = models.CharField(max_length=20, choices=AttendanceType.choices, default=AttendanceType.BOTH)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    pickup_time = models.TimeField(null=True, blank=True)
    dropoff_time = models.TimeField(null=True, blank=True)
    pickup_stop = models.ForeignKey(
        RouteStop, on_delete=models.SET_NULL, null=True, blank=True, related_name="pickup_attendance"
    )
    dropoff_stop = models.ForeignKey(
        RouteStop, on_delete=models.SET_NULL, null=True, blank=True, related_name="dropoff_attendance"
    )
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_daily_attendance"
        ordering = ["-date", "student"]
        unique_together = [("student", "route", "date", "attendance_type")]

    def __str__(self):
        return f"{self.student} - {self.date} ({self.get_status_display()})"


class TransportIncidentReport(models.Model):
    """Transport incident tracking."""

    class IncidentType(models.TextChoices):
        ACCIDENT = "accident", "Accident"
        BREAKDOWN = "breakdown", "Breakdown"
        MEDICAL = "medical", "Medical Emergency"
        BEHAVIORAL = "behavioral", "Behavioral"
        ROUTE_DELAY = "route_delay", "Route Delay"
        VEHICLE_DAMAGE = "vehicle_damage", "Vehicle Damage"
        WEATHER = "weather", "Weather Related"
        OTHER = "other", "Other"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        REPORTED = "reported", "Reported"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_incidents")
    incident_type = models.CharField(max_length=20, choices=IncidentType.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.LOW)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    incident_date = models.DateField()
    incident_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    students_involved = models.JSONField(default=list, blank=True)
    injuries_reported = models.BooleanField(default=False)
    injury_details = models.TextField(blank=True)
    witnesses = models.TextField(blank=True)
    police_report = models.BooleanField(default=False)
    police_report_number = models.CharField(max_length=50, blank=True)
    insurance_claim = models.BooleanField(default=False)
    insurance_claim_number = models.CharField(max_length=50, blank=True)
    corrective_actions = models.TextField(blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transport_incidents_resolved",
    )
    resolved_date = models.DateField(null=True, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_incidents"
        ordering = ["-incident_date"]

    def __str__(self):
        return f"{self.get_incident_type_display()} - {self.incident_date}"


class VehicleInspection(models.Model):
    """Pre-trip safety inspections."""

    class InspectionType(models.TextChoices):
        PRE_TRIP = "pre_trip", "Pre-Trip"
        POST_TRIP = "post_trip", "Post-Trip"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        ANNUAL = "annual", "Annual"

    class Result(models.TextChoices):
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"
        NEEDS_REPAIR = "needs_repair", "Needs Repair"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="inspections")
    inspection_type = models.CharField(max_length=20, choices=InspectionType.choices, default=InspectionType.PRE_TRIP)
    inspection_date = models.DateField()
    inspector_name = models.CharField(max_length=150)
    result = models.CharField(max_length=20, choices=Result.choices, default=Result.PASS)
    odometer_reading = models.PositiveIntegerField(null=True, blank=True)
    exterior_check = models.BooleanField(default=True)
    interior_check = models.BooleanField(default=True)
    tires_check = models.BooleanField(default=True)
    lights_check = models.BooleanField(default=True)
    brakes_check = models.BooleanField(default=True)
    signals_check = models.BooleanField(default=True)
    emergency_equipment = models.BooleanField(default=True)
    first_aid_kit = models.BooleanField(default=True)
    fire_extinguisher = models.BooleanField(default=True)
    defects_found = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_inspections"
        ordering = ["-inspection_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.get_inspection_type_display()} ({self.inspection_date})"


class TripSchedule(models.Model):
    """Field trip scheduling."""

    class TripType(models.TextChoices):
        FIELD_TRIP = "field_trip", "Field Trip"
        SPORTS_EVENT = "sports_event", "Sports Event"
        CULTURAL_EVENT = "cultural_event", "Cultural Event"
        EXAMINATION = "examination", "Examination"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="trip_schedules")
    title = models.CharField(max_length=200)
    trip_type = models.CharField(max_length=20, choices=TripType.choices, default=TripType.FIELD_TRIP)
    destination = models.CharField(max_length=255)
    trip_date = models.DateField()
    departure_time = models.TimeField()
    return_time = models.TimeField(null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    expected_students = models.PositiveIntegerField(default=0)
    actual_students = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    purpose = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="trip_approvals"
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="trip_creations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_trip_schedules"
        ordering = ["-trip_date"]

    def __str__(self):
        return f"{self.title} ({self.trip_date})"


class FuelLog(models.Model):
    """Fuel tracking and costs."""

    class FuelType(models.TextChoices):
        DIESEL = "diesel", "Diesel"
        PETROL = "petrol", "Petrol"
        CNG = "cng", "CNG"
        ELECTRIC = "electric", "Electric"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="fuel_logs")
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, default=FuelType.DIESEL)
    fill_date = models.DateField()
    odometer_reading = models.PositiveIntegerField()
    liters = models.DecimalField(max_digits=8, decimal_places=2)
    cost_per_liter = models.DecimalField(max_digits=8, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    station_name = models.CharField(max_length=200, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    filled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_fuel_logs"
        ordering = ["-fill_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.liters}L ({self.fill_date})"


class TransportNotification(models.Model):
    """Transport notifications to parents/students."""

    class NotificationType(models.TextChoices):
        DELAY = "delay", "Delay Alert"
        CANCELLATION = "cancellation", "Cancellation"
        ROUTE_CHANGE = "route_change", "Route Change"
        PICKUP_COMPLETE = "pickup_complete", "Pickup Complete"
        DROPOFF_COMPLETE = "dropoff_complete", "Dropoff Complete"
        INCIDENT = "incident", "Incident"
        FEE_REMINDER = "fee_reminder", "Fee Reminder"
        GENERAL = "general", "General"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_notifications")
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices, default=NotificationType.GENERAL
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    recipients = models.JSONField(default=list, blank=True, help_text="List of recipient IDs or emails")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_notification_type_display()})"


class TransportReport(models.Model):
    """Transport analytics and reports."""

    class ReportType(models.TextChoices):
        ROUTE_SUMMARY = "route_summary", "Route Summary"
        VEHICLE_STATUS = "vehicle_status", "Vehicle Status"
        FUEL_CONSUMPTION = "fuel_consumption", "Fuel Consumption"
        INCIDENT_SUMMARY = "incident_summary", "Incident Summary"
        FEE_COLLECTION = "fee_collection", "Fee Collection"
        ATTENDANCE_SUMMARY = "attendance_summary", "Attendance Summary"
        MAINTENANCE_COST = "maintenance_cost", "Maintenance Cost"
        GENERAL = "general", "General Report"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_reports")
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=25, choices=ReportType.choices, default=ReportType.GENERAL)
    date_from = models.DateField()
    date_to = models.DateField()
    report_data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"


class VehicleDocument(models.Model):
    """Vehicle document management."""

    class DocumentType(models.TextChoices):
        REGISTRATION = "registration", "Registration"
        INSURANCE = "insurance", "Insurance"
        PERMIT = "permit", "Permit"
        FITNESS = "fitness", "Fitness Certificate"
        POLLUTION = "pollution", "Pollution Certificate"
        TAX = "tax", "Tax Receipt"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    document_name = models.CharField(max_length=200)
    document_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issued_by = models.CharField(max_length=200, blank=True)
    document_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_vehicle_documents"
        ordering = ["expiry_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.get_document_type_display()}"
