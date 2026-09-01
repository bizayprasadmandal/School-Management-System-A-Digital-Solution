"""URL Configuration for reporting."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicPerformanceReportViewSet,
    AnalyticsSnapshotViewSet,
    ChartConfigurationViewSet,
    ComplianceReportViewSet,
    CustomReportExecutionViewSet,
    CustomReportViewSet,
    DashboardConfigurationViewSet,
    DashboardWidgetPlacementViewSet,
    DashboardWidgetViewSet,
    DepartmentReportViewSet,
    GradeTrendReportViewSet,
    KPIDefinitionViewSet,
    KPIValueViewSet,
    ReportAccessControlViewSet,
    ReportAccessLogViewSet,
    ReportAlertViewSet,
    ReportAnalyticsViewSet,
    ReportBookmarkViewSet,
    ReportCommentViewSet,
    ReportComparisonViewSet,
    ReportDataCacheViewSet,
    ReportDataSourceViewSet,
    ReportEmailDeliveryViewSet,
    ReportExportViewSet,
    ReportFavoriteViewSet,
    ReportFolderItemViewSet,
    ReportFolderViewSet,
    ReportHistoryViewSet,
    ReportInsightViewSet,
    ReportScheduleDeliveryViewSet,
    ReportScheduleViewSet,
    ReportShareViewSet,
    ReportSubscriptionViewSet,
    ReportTemplateParameterViewSet,
    ReportTemplateViewSet,
    ReportVersionViewSet,
    ScheduledReportViewSet,
    StudentProgressTrackingViewSet,
    TeacherPerformanceReportViewSet,
    YearOverYearReportViewSet,
)

app_name = "reporting_v1"

router = DefaultRouter()
router.register(r"report-template", ReportTemplateViewSet, basename="report-template")
router.register(
    r"academic-performance-report", AcademicPerformanceReportViewSet, basename="academic-performance-report"
)
router.register(r"teacher-performance-report", TeacherPerformanceReportViewSet, basename="teacher-performance-report")
router.register(r"grade-trend-report", GradeTrendReportViewSet, basename="grade-trend-report")
router.register(r"scheduled-report", ScheduledReportViewSet, basename="scheduled-report")
router.register(r"year-over-year-report", YearOverYearReportViewSet, basename="year-over-year-report")
router.register(r"department-report", DepartmentReportViewSet, basename="department-report")
router.register(r"compliance-report", ComplianceReportViewSet, basename="compliance-report")
router.register(r"report-share", ReportShareViewSet, basename="report-share")
router.register(r"student-progress-tracking", StudentProgressTrackingViewSet, basename="student-progress-tracking")
router.register(r"dashboard-widget", DashboardWidgetViewSet, basename="dashboard-widget")
router.register(r"dashboard-configuration", DashboardConfigurationViewSet, basename="dashboard-configuration")
router.register(r"dashboard-widget-placement", DashboardWidgetPlacementViewSet, basename="dashboard-widget-placement")
router.register(r"report-schedule", ReportScheduleViewSet, basename="report-schedule")
router.register(r"report-history", ReportHistoryViewSet, basename="report-history")
router.register(r"custom-report", CustomReportViewSet, basename="custom-report")
router.register(r"custom-report-execution", CustomReportExecutionViewSet, basename="custom-report-execution")
router.register(r"chart-configuration", ChartConfigurationViewSet, basename="chart-configuration")
router.register(r"k-p-i-definition", KPIDefinitionViewSet, basename="k-p-i-definition")
router.register(r"k-p-i-value", KPIValueViewSet, basename="k-p-i-value")
router.register(r"report-access-log", ReportAccessLogViewSet, basename="report-access-log")
router.register(r"report-comment", ReportCommentViewSet, basename="report-comment")
router.register(r"report-data-source", ReportDataSourceViewSet, basename="report-data-source")
router.register(r"report-bookmark", ReportBookmarkViewSet, basename="report-bookmark")
router.register(r"report-email-delivery", ReportEmailDeliveryViewSet, basename="report-email-delivery")
router.register(r"analytics-snapshot", AnalyticsSnapshotViewSet, basename="analytics-snapshot")
router.register(r"report-favorite", ReportFavoriteViewSet, basename="report-favorite")
router.register(r"report-template-parameter", ReportTemplateParameterViewSet, basename="report-template-parameter")
router.register(r"report-alert", ReportAlertViewSet, basename="report-alert")
router.register(r"report-export", ReportExportViewSet, basename="report-export")
router.register(r"report-insight", ReportInsightViewSet, basename="report-insight")
router.register(r"report-version", ReportVersionViewSet, basename="report-version")
router.register(r"report-folder", ReportFolderViewSet, basename="report-folder")
router.register(r"report-folder-item", ReportFolderItemViewSet, basename="report-folder-item")
router.register(r"report-access-control", ReportAccessControlViewSet, basename="report-access-control")
router.register(r"report-analytics", ReportAnalyticsViewSet, basename="report-analytics")
router.register(r"report-schedule-delivery", ReportScheduleDeliveryViewSet, basename="report-schedule-delivery")
router.register(r"report-data-cache", ReportDataCacheViewSet, basename="report-data-cache")
router.register(r"report-comparison", ReportComparisonViewSet, basename="report-comparison")
router.register(r"report-subscription", ReportSubscriptionViewSet, basename="report-subscription")

urlpatterns = [
    path("", include(router.urls)),
]
