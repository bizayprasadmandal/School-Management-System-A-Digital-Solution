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
            "name",
            "description",
            "report_type",
            "config",
            "columns",
            "filters",
            "is_public",
            "created_by",
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
            "title",
            "academic_year",
            "grade",
            "classroom",
            "subject",
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
            "title",
            "academic_year",
            "teacher",
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
            "title",
            "trend_type",
            "academic_year",
            "grade",
            "subject",
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
            "title",
            "academic_year_from",
            "academic_year_to",
            "report_data",
            "summary",
            "enrollment_change",
            "performance_change",
            "attendance_change",
            "generated_by",
        ]
        read_only_fields = ["id", "created_at"]


class DepartmentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentReport
        fields = [
            "id",
            "school",
            "id",
            "title",
            "department",
            "academic_year",
            "report_data",
            "summary",
            "total_students",
            "total_teachers",
            "average_score",
            "generated_by",
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
            "title",
            "compliance_type",
            "academic_year",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentProgressTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProgressTracking
        fields = [
            "id",
            "school",
            "id",
            "student",
            "title",
            "progress_type",
            "academic_year",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class DashboardConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardConfiguration
        fields = ["id", "id", "user", "name", "is_default", "is_public", "columns", "theme", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "user"]


class DashboardWidgetPlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidgetPlacement
        fields = ["id", "id", "dashboard", "widget", "position", "custom_config", "is_visible"]
        read_only_fields = ["id"]


class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class ReportHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportHistory
        fields = [
            "id",
            "school",
            "id",
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
        ]
        read_only_fields = ["id", "created_at", "school"]


class CustomReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomReport
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class CustomReportExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomReportExecution
        fields = [
            "id",
            "id",
            "report",
            "status",
            "parameters",
            "result_file",
            "record_count",
            "started_at",
            "completed_at",
            "duration_seconds",
            "error_message",
            "executed_by",
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
            "name",
            "chart_type",
            "data_source",
            "query",
            "colors",
            "config",
            "created_by",
            "is_public",
            "total_views",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class KPIDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIDefinition
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class KPIValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIValue
        fields = ["id", "id", "kpi", "date", "value", "target_met", "trend", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class ReportAccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAccessLog
        fields = ["id", "id", "report_history", "user", "access_type", "ip_address", "accessed_at"]
        read_only_fields = ["id", "user"]


class ReportCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportComment
        fields = ["id", "id", "report_history", "user", "comment", "parent", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "user"]


class ReportDataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDataSource
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class ReportBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportBookmark
        fields = [
            "id",
            "id",
            "user",
            "report_type",
            "report_id",
            "name",
            "description",
            "saved_filters",
            "sort_order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]


class ReportEmailDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportEmailDelivery
        fields = [
            "id",
            "id",
            "report_history",
            "recipient",
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
        read_only_fields = ["id", "created_at", "school"]


class ReportFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFavorite
        fields = ["id", "id", "user", "report_type", "report_name", "report_config", "created_at"]
        read_only_fields = ["id", "created_at", "user"]


class ReportTemplateParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplateParameter
        fields = [
            "id",
            "id",
            "template",
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
        read_only_fields = ["id", "created_at", "school"]


class ReportExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExport
        fields = [
            "id",
            "school",
            "id",
            "report_type",
            "format",
            "status",
            "filters",
            "date_from",
            "date_to",
            "file",
            "record_count",
            "requested_by",
            "requested_at",
            "completed_at",
        ]
        read_only_fields = ["id", "school"]


class ReportInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportInsight
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "school"]


class ReportVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportVersion
        fields = [
            "id",
            "id",
            "template",
            "version_number",
            "config_snapshot",
            "is_current",
            "created_by",
            "created_at",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class ReportFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFolder
        fields = ["id", "school", "id", "name", "parent", "description", "owner", "is_shared", "created_at"]
        read_only_fields = ["id", "created_at", "school"]


class ReportFolderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFolderItem
        fields = ["id", "id", "folder", "item_type", "item_id", "name", "sort_order", "added_at"]
        read_only_fields = ["id"]


class ReportAccessControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAccessControl
        fields = [
            "id",
            "id",
            "report_type",
            "user",
            "role",
            "access_level",
            "is_active",
            "expires_at",
            "granted_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]


class ReportAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAnalytics
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "created_at", "school"]


class ReportScheduleDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportScheduleDelivery
        fields = [
            "id",
            "id",
            "schedule",
            "report_history",
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
            "cache_key",
            "report_type",
            "data",
            "data_hash",
            "created_at",
            "expires_at",
            "hit_count",
            "last_hit_at",
        ]
        read_only_fields = ["id", "created_at", "school"]


class ReportComparisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportComparison
        fields = [
            "id",
            "school",
            "id",
            "name",
            "report_type",
            "period_a_start",
            "period_a_end",
            "period_b_start",
            "period_b_end",
            "comparison_data",
            "highlights",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "school"]


class ReportSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSubscription
        fields = ["id", "id", "user", "report_type", "update_type", "is_active", "last_notified_at", "created_at"]
        read_only_fields = ["id", "created_at", "user"]


# ── Serializers restored from original module (expansion regression fix) ──


class DashboardStatsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_classrooms = serializers.IntegerField()
    attendance_today_pct = serializers.FloatField()
    fees_collected_month = serializers.FloatField()
    fees_outstanding = serializers.FloatField()
    student_delta_pct = serializers.FloatField()
    attendance_delta_pct = serializers.FloatField()


class AttendanceDailySerializer(serializers.Serializer):
    date = serializers.DateField()
    total = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()


class FeeStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
