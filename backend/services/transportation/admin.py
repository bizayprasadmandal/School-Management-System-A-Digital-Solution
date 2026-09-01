"""Transportation Management — Django Admin registrations."""

from django.contrib import admin

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


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["plate_number", "vehicle_type", "capacity", "status", "insurance_expiry", "is_active"]
    list_filter = ["vehicle_type", "status", "is_active", "school"]
    search_fields = ["plate_number", "model_name", "chassis_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone_number", "license_number", "status"]
    list_filter = ["status", "school"]
    search_fields = ["full_name", "phone_number", "license_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1
    fields = ["name", "address", "stop_order", "stop_type", "pickup_time", "dropoff_time"]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["name", "vehicle", "driver", "origin", "destination", "is_active"]
    list_filter = ["is_active", "school"]
    search_fields = ["name", "origin", "destination"]
    inlines = [RouteStopInline]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ["name", "route", "stop_order", "stop_type", "pickup_time"]
    list_filter = ["stop_type", "is_active"]
    search_fields = ["name", "address", "landmark"]
    readonly_fields = ["id", "created_at"]


@admin.register(StudentRoute)
class StudentRouteAdmin(admin.ModelAdmin):
    list_display = ["student", "route", "is_active", "effective_from", "effective_to"]
    list_filter = ["is_active"]
    search_fields = ["student__user__full_name", "route__name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(VehicleMaintenance)
class VehicleMaintenanceAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "maintenance_type", "status", "scheduled_date", "cost"]
    list_filter = ["maintenance_type", "status"]
    search_fields = ["vehicle__plate_number", "vendor_name", "invoice_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(TransportFee)
class TransportFeeAdmin(admin.ModelAdmin):
    list_display = ["student", "fee_type", "amount", "status", "due_date"]
    list_filter = ["fee_type", "status"]
    search_fields = ["student__user__full_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(VehicleInsurance)
class VehicleInsuranceAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "provider", "policy_number", "end_date", "status"]
    list_filter = ["insurance_type", "status"]
    search_fields = ["vehicle__plate_number", "policy_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(DailyTransportAttendance)
class DailyTransportAttendanceAdmin(admin.ModelAdmin):
    list_display = ["student", "route", "date", "status", "pickup_time"]
    list_filter = ["status", "attendance_type"]
    search_fields = ["student__user__full_name"]
    readonly_fields = ["id", "created_at"]


@admin.register(TransportIncidentReport)
class TransportIncidentReportAdmin(admin.ModelAdmin):
    list_display = ["incident_type", "severity", "status", "incident_date", "vehicle"]
    list_filter = ["incident_type", "severity", "status"]
    search_fields = ["description"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(VehicleInspection)
class VehicleInspectionAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "inspection_type", "result", "inspection_date"]
    list_filter = ["inspection_type", "result"]
    search_fields = ["vehicle__plate_number"]
    readonly_fields = ["id", "created_at"]


@admin.register(TripSchedule)
class TripScheduleAdmin(admin.ModelAdmin):
    list_display = ["title", "trip_type", "trip_date", "destination", "status"]
    list_filter = ["trip_type", "status"]
    search_fields = ["title", "destination"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "fuel_type", "liters", "total_cost", "fill_date"]
    list_filter = ["fuel_type"]
    search_fields = ["vehicle__plate_number"]
    readonly_fields = ["id", "created_at"]


@admin.register(TransportNotification)
class TransportNotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "notification_type", "status", "sent_at"]
    list_filter = ["notification_type", "status"]
    search_fields = ["title", "message"]
    readonly_fields = ["id", "created_at"]


@admin.register(TransportReport)
class TransportReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "date_from", "date_to", "created_at"]
    list_filter = ["report_type"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "document_type", "document_name", "expiry_date", "is_valid"]
    list_filter = ["document_type", "is_valid"]
    search_fields = ["vehicle__plate_number", "document_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
