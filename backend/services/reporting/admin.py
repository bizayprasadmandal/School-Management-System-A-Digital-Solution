"""Django Admin registrations for reporting."""

from django.contrib import admin

from .models import (
    AcademicPerformanceReport,
    AnalyticsSnapshot,
    ChartConfiguration,
    ComplianceReport,
    CustomReport,
    CustomReportExecution,
    DashboardConfiguration,
    DashboardWidget,
    DashboardWidgetPlacement,
    DepartmentReport,
    GradeTrendReport,
    KPIDefinition,
    KPIValue,
    ReportAccessControl,
    ReportAccessLog,
    ReportAlert,
    ReportAnalytics,
    ReportBookmark,
    ReportComment,
    ReportComparison,
    ReportDataCache,
    ReportDataSource,
    ReportEmailDelivery,
    ReportExport,
    ReportFavorite,
    ReportFolder,
    ReportFolderItem,
    ReportHistory,
    ReportInsight,
    ReportSchedule,
    ReportScheduleDelivery,
    ReportShare,
    ReportSubscription,
    ReportTemplate,
    ReportTemplateParameter,
    ReportVersion,
    ScheduledReport,
    StudentProgressTracking,
    TeacherPerformanceReport,
    YearOverYearReport,
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["name"]


@admin.register(AcademicPerformanceReport)
class AcademicPerformanceReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(TeacherPerformanceReport)
class TeacherPerformanceReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(GradeTrendReport)
class GradeTrendReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(YearOverYearReport)
class YearOverYearReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(DepartmentReport)
class DepartmentReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(ReportShare)
class ReportShareAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(StudentProgressTracking)
class StudentProgressTrackingAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(DashboardConfiguration)
class DashboardConfigurationAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    list_filter = []
    search_fields = ["name"]


@admin.register(DashboardWidgetPlacement)
class DashboardWidgetPlacementAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(CustomReport)
class CustomReportAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(CustomReportExecution)
class CustomReportExecutionAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ChartConfiguration)
class ChartConfigurationAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["name"]


@admin.register(KPIDefinition)
class KPIDefinitionAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(KPIValue)
class KPIValueAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ReportAccessLog)
class ReportAccessLogAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ReportDataSource)
class ReportDataSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(ReportBookmark)
class ReportBookmarkAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    list_filter = []
    search_fields = ["name"]


@admin.register(ReportEmailDelivery)
class ReportEmailDeliveryAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ReportFavorite)
class ReportFavoriteAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ReportTemplateParameter)
class ReportTemplateParameterAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    list_filter = []
    search_fields = ["name"]


@admin.register(ReportAlert)
class ReportAlertAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(ReportInsight)
class ReportInsightAdmin(admin.ModelAdmin):
    list_display = ["id", "school"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ReportVersion)
class ReportVersionAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ReportFolder)
class ReportFolderAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["name"]


@admin.register(ReportFolderItem)
class ReportFolderItemAdmin(admin.ModelAdmin):
    list_display = ["name"]
    list_filter = []
    search_fields = ["name"]


@admin.register(ReportAccessControl)
class ReportAccessControlAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(ReportAnalytics)
class ReportAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ReportScheduleDelivery)
class ReportScheduleDeliveryAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ReportDataCache)
class ReportDataCacheAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ReportComparison)
class ReportComparisonAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["name"]


@admin.register(ReportSubscription)
class ReportSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]
