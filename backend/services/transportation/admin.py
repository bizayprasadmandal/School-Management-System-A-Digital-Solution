"""Django Admin registrations for transportation."""

from django.contrib import admin

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


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "is_active", "created_at"]
    list_filter = ["school", "is_active", "status"]
    search_fields = ["id"]


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(StudentRoute)
class StudentRouteAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(VehicleMaintenance)
class VehicleMaintenanceAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(TransportFee)
class TransportFeeAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(VehicleInsurance)
class VehicleInsuranceAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(DailyTransportAttendance)
class DailyTransportAttendanceAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(TransportIncidentReport)
class TransportIncidentReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(VehicleInspection)
class VehicleInspectionAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(TripSchedule)
class TripScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(TransportNotification)
class TransportNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(TransportReport)
class TransportReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(VehicleGPSLog)
class VehicleGPSLogAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(GeofenceZone)
class GeofenceZoneAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(GeofenceAlert)
class GeofenceAlertAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(BusTracking)
class BusTrackingAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(StopETA)
class StopETAAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(DriverPerformance)
class DriverPerformanceAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(VehicleConditionReport)
class VehicleConditionReportAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(RouteOptimization)
class RouteOptimizationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(TransportationDailyReport)
class TransportationDailyReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ParentTransportAccess)
class ParentTransportAccessAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(TransportComplianceRecord)
class TransportComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentTransportProfile)
class StudentTransportProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(TransportAlert)
class TransportAlertAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(VehiclePool)
class VehiclePoolAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(TransportSchedule)
class TransportScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(TransportFeeStructure)
class TransportFeeStructureAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(TransportIncident)
class TransportIncidentAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(TransportBudget)
class TransportBudgetAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(TransportAuditLog)
class TransportAuditLogAdmin(admin.ModelAdmin):
    list_display = ["id", "school"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(TransportMonthlyReport)
class TransportMonthlyReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(TransportEmergencyContact)
class TransportEmergencyContactAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(VehicleAssignmentLog)
class VehicleAssignmentLogAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(TransportDriverSchedule)
class TransportDriverScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]
