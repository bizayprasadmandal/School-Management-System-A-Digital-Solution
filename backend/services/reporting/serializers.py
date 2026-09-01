"""Serializers for reporting."""

from rest_framework import serializers

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


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "report_type",
            "config",
            "columns",
            "filters",
            "is_public",
            "created_by",
            "on_delete",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AcademicPerformanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPerformanceReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "academic_year",
            "on_delete",
            "grade",
            "on_delete",
            "classroom",
            "on_delete",
            "subject",
            "on_delete",
            "report_data",
            "summary",
            "average_score",
        ]
        read_only_fields = ["id", "created_at"]


class TeacherPerformanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherPerformanceReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "academic_year",
            "on_delete",
            "teacher",
            "on_delete",
            "report_data",
            "summary",
            "average_class_score",
            "student_satisfaction",
            "attendance_rate",
            "classes_taught",
            "generated_by",
        ]
        read_only_fields = ["id", "created_at"]


class GradeTrendReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeTrendReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "trend_type",
            "academic_year",
            "on_delete",
            "grade",
            "on_delete",
            "subject",
            "on_delete",
            "date_from",
            "date_to",
            "report_data",
            "summary",
        ]
        read_only_fields = ["id", "created_at"]


class ScheduledReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "report_type",
            "frequency",
            "status",
            "delivery_method",
            "recipients",
            "config",
            "last_generated",
            "next_generation",
            "created_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class YearOverYearReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearOverYearReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "academic_year_from",
            "on_delete",
            "academic_year_to",
            "on_delete",
            "report_data",
            "summary",
            "enrollment_change",
            "performance_change",
            "attendance_change",
            "generated_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class DepartmentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "department",
            "academic_year",
            "on_delete",
            "report_data",
            "summary",
            "total_students",
            "total_teachers",
            "average_score",
            "generated_by",
            "on_delete",
            "file_url",
        ]
        read_only_fields = ["id", "created_at"]


class ComplianceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "compliance_type",
            "academic_year",
            "on_delete",
            "submission_date",
            "due_date",
            "status",
            "report_data",
            "summary",
            "submitted_to",
            "reference_number",
            "generated_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReportShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportShare
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "share_type",
            "access_level",
            "report_url",
            "report_data",
            "shared_with",
            "expires_at",
            "password_protected",
            "access_password",
            "view_count",
            "shared_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentProgressTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProgressTracking
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "title",
            "progress_type",
            "academic_year",
            "on_delete",
            "date_from",
            "date_to",
            "report_data",
            "summary",
            "strengths",
            "areas_for_improvement",
        ]
        read_only_fields = ["id", "created_at"]


class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "widget_type",
            "description",
            "data_source",
            "config",
            "refresh_interval_seconds",
            "position_x",
            "position_y",
            "width",
            "height",
            "is_default",
            "visible_to_roles",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DashboardConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardConfiguration
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "name",
            "is_default",
            "is_public",
            "columns",
            "theme",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DashboardWidgetPlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidgetPlacement
        fields = [
            "id",
            "id",
            "dashboard",
            "on_delete",
            "widget",
            "on_delete",
            "position",
            "custom_config",
            "is_visible",
        ]
        read_only_fields = ["id"]


class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "report_type",
            "frequency",
            "status",
            "day_of_week",
            "day_of_month",
            "time_of_day",
            "recipients",
            "email_delivery",
            "format",
            "filters",
            "last_generated",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReportHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportHistory
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "report_type",
            "title",
            "status",
            "file",
            "file_size_bytes",
            "format",
            "filters_applied",
            "date_from",
            "date_to",
            "record_count",
            "generated_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class CustomReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "status",
            "data_sources",
            "default_filters",
            "available_filters",
            "columns",
            "default_sort",
            "group_by",
            "aggregations",
            "chart_config",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomReportExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomReportExecution
        fields = [
            "id",
            "id",
            "report",
            "on_delete",
            "status",
            "parameters",
            "result_file",
            "record_count",
            "started_at",
            "completed_at",
            "duration_seconds",
            "error_message",
            "executed_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ChartConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartConfiguration
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "chart_type",
            "data_source",
            "query",
            "colors",
            "config",
            "created_by",
            "on_delete",
            "is_public",
            "total_views",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class KPIDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIDefinition
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "category",
            "data_type",
            "target_value",
            "min_value",
            "max_value",
            "warning_threshold",
            "critical_threshold",
            "formula",
            "data_source",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class KPIValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIValue
        fields = ["id", "id", "kpi", "on_delete", "date", "value", "target_met", "trend", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class ReportAccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAccessLog
        fields = [
            "id",
            "id",
            "report_history",
            "on_delete",
            "user",
            "on_delete",
            "access_type",
            "ip_address",
            "accessed_at",
        ]
        read_only_fields = ["id"]


class ReportCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportComment
        fields = [
            "id",
            "id",
            "report_history",
            "on_delete",
            "user",
            "on_delete",
            "comment",
            "parent",
            "on_delete",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReportDataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDataSource
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "source_type",
            "model_path",
            "view_name",
            "api_url",
            "sql_query",
            "fields",
            "is_active",
            "last_synced_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReportBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportBookmark
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "report_type",
            "report_id",
            "name",
            "description",
            "saved_filters",
            "sort_order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReportEmailDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportEmailDelivery
        fields = [
            "id",
            "id",
            "report_history",
            "on_delete",
            "recipient",
            "on_delete",
            "status",
            "subject",
            "message",
            "sent_at",
            "delivered_at",
            "error_message",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "snapshot_type",
            "snapshot_date",
            "data",
            "total_students",
            "total_staff",
            "avg_attendance",
            "avg_gpa",
            "pass_rate",
            "total_revenue",
            "total_expenses",
            "new_enrollments",
            "dropouts",
        ]
        read_only_fields = ["id", "created_at"]


class ReportFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFavorite
        fields = ["id", "id", "user", "on_delete", "report_type", "report_name", "report_config", "created_at"]
        read_only_fields = ["id", "created_at"]


class ReportTemplateParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplateParameter
        fields = [
            "id",
            "id",
            "template",
            "on_delete",
            "name",
            "display_name",
            "param_type",
            "is_required",
            "default_value",
            "options",
            "sort_order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReportAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAlert
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "alert_type",
            "status",
            "metric",
            "threshold_value",
            "notify_users",
            "last_triggered_at",
            "trigger_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReportExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "report_type",
            "format",
            "status",
            "filters",
            "date_from",
            "date_to",
            "file",
            "record_count",
            "requested_by",
            "on_delete",
            "requested_at",
            "completed_at",
        ]
        read_only_fields = ["id"]


class ReportInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportInsight
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "insight_type",
            "title",
            "description",
            "metric",
            "value",
            "change_percentage",
            "priority",
            "is_read",
            "generated_at",
        ]
        read_only_fields = ["id"]


class ReportVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportVersion
        fields = [
            "id",
            "id",
            "template",
            "on_delete",
            "version_number",
            "config_snapshot",
            "is_current",
            "created_by",
            "on_delete",
            "created_at",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class ReportFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFolder
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "parent",
            "on_delete",
            "description",
            "owner",
            "on_delete",
            "is_shared",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReportFolderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFolderItem
        fields = ["id", "id", "folder", "on_delete", "item_type", "item_id", "name", "sort_order", "added_at"]
        read_only_fields = ["id"]


class ReportAccessControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAccessControl
        fields = [
            "id",
            "id",
            "report_type",
            "user",
            "on_delete",
            "role",
            "access_level",
            "is_active",
            "expires_at",
            "granted_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReportAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAnalytics
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "date",
            "total_reports_generated",
            "total_reports_viewed",
            "total_reports_exported",
            "by_type_breakdown",
            "top_reports",
            "active_users",
            "avg_generation_time",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReportScheduleDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportScheduleDelivery
        fields = [
            "id",
            "id",
            "schedule",
            "on_delete",
            "report_history",
            "on_delete",
            "status",
            "recipient_count",
            "sent_at",
            "error_message",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReportDataCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDataCache
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "cache_key",
            "report_type",
            "data",
            "data_hash",
            "created_at",
            "expires_at",
            "hit_count",
            "last_hit_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReportComparisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportComparison
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "report_type",
            "period_a_start",
            "period_a_end",
            "period_b_start",
            "period_b_end",
            "comparison_data",
            "highlights",
            "created_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReportSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSubscription
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "report_type",
            "update_type",
            "is_active",
            "last_notified_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
