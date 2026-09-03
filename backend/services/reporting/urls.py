from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "reporting_v1"
router = DefaultRouter()
router.register("", views.ReportingViewSet, basename="reporting")
router.register("templates", views.ReportTemplateViewSet, basename="report-template")
router.register("academic-performance", views.AcademicPerformanceReportViewSet, basename="academic-performance")
router.register("teacher-performance", views.TeacherPerformanceReportViewSet, basename="teacher-performance")
router.register("grade-trends", views.GradeTrendReportViewSet, basename="grade-trend")
router.register("scheduled", views.ScheduledReportViewSet, basename="scheduled-report")
router.register("year-over-year", views.YearOverYearReportViewSet, basename="year-over-year")
router.register("department", views.DepartmentReportViewSet, basename="department-report")
router.register("compliance", views.ComplianceReportViewSet, basename="compliance-report")
router.register("shares", views.ReportShareViewSet, basename="report-share")
router.register("student-progress", views.StudentProgressTrackingViewSet, basename="student-progress")


# ── Additional registrations (module expansion) ──
router.register(r"dashboard-widget", views.DashboardWidgetViewSet, basename="dashboard-widget")
router.register(r"dashboard-configuration", views.DashboardConfigurationViewSet, basename="dashboard-configuration")
router.register(
    r"dashboard-widget-placement", views.DashboardWidgetPlacementViewSet, basename="dashboard-widget-placement"
)
router.register(r"report-schedule", views.ReportScheduleViewSet, basename="report-schedule")
router.register(r"report-history", views.ReportHistoryViewSet, basename="report-history")
router.register(r"custom-report", views.CustomReportViewSet, basename="custom-report")
router.register(r"custom-report-execution", views.CustomReportExecutionViewSet, basename="custom-report-execution")
router.register(r"chart-configuration", views.ChartConfigurationViewSet, basename="chart-configuration")
router.register(r"k-p-i-definition", views.KPIDefinitionViewSet, basename="k-p-i-definition")
router.register(r"k-p-i-value", views.KPIValueViewSet, basename="k-p-i-value")
router.register(r"report-access-log", views.ReportAccessLogViewSet, basename="report-access-log")
router.register(r"report-comment", views.ReportCommentViewSet, basename="report-comment")
router.register(r"report-data-source", views.ReportDataSourceViewSet, basename="report-data-source")
router.register(r"report-bookmark", views.ReportBookmarkViewSet, basename="report-bookmark")
router.register(r"report-email-delivery", views.ReportEmailDeliveryViewSet, basename="report-email-delivery")
router.register(r"analytics-snapshot", views.AnalyticsSnapshotViewSet, basename="analytics-snapshot")
router.register(r"report-favorite", views.ReportFavoriteViewSet, basename="report-favorite")
router.register(
    r"report-template-parameter", views.ReportTemplateParameterViewSet, basename="report-template-parameter"
)
router.register(r"report-alert", views.ReportAlertViewSet, basename="report-alert")
router.register(r"report-export", views.ReportExportViewSet, basename="report-export")
router.register(r"report-insight", views.ReportInsightViewSet, basename="report-insight")
router.register(r"report-version", views.ReportVersionViewSet, basename="report-version")
router.register(r"report-folder", views.ReportFolderViewSet, basename="report-folder")
router.register(r"report-folder-item", views.ReportFolderItemViewSet, basename="report-folder-item")
router.register(r"report-access-control", views.ReportAccessControlViewSet, basename="report-access-control")
router.register(r"report-analytics", views.ReportAnalyticsViewSet, basename="report-analytics")
router.register(r"report-schedule-delivery", views.ReportScheduleDeliveryViewSet, basename="report-schedule-delivery")
router.register(r"report-data-cache", views.ReportDataCacheViewSet, basename="report-data-cache")
router.register(r"report-comparison", views.ReportComparisonViewSet, basename="report-comparison")
router.register(r"report-subscription", views.ReportSubscriptionViewSet, basename="report-subscription")

urlpatterns = [path("", include(router.urls))]
