"""Transportation Management — Django Admin registrations."""

from django.contrib import admin
from .models import Vehicle, Driver, Route, RouteStop, StudentRoute, VehicleMaintenance


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
