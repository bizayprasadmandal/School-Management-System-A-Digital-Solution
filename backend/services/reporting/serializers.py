"""Reporting serializers — lightweight response shapes for analytics endpoints."""

from rest_framework import serializers

from .models import (
    AcademicPerformanceReport,
    ComplianceReport,
    DepartmentReport,
    GradeTrendReport,
    ReportShare,
    ReportTemplate,
    ScheduledReport,
    StudentProgressTracking,
    TeacherPerformanceReport,
    YearOverYearReport,
)


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


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AcademicPerformanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPerformanceReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TeacherPerformanceReportSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)

    class Meta:
        model = TeacherPerformanceReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class GradeTrendReportSerializer(serializers.ModelSerializer):
    trend_type_display = serializers.CharField(source="get_trend_type_display", read_only=True)

    class Meta:
        model = GradeTrendReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ScheduledReportSerializer(serializers.ModelSerializer):
    frequency_display = serializers.CharField(source="get_frequency_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ScheduledReport
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class YearOverYearReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearOverYearReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class DepartmentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ComplianceReportSerializer(serializers.ModelSerializer):
    compliance_type_display = serializers.CharField(source="get_compliance_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ComplianceReport
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ReportShareSerializer(serializers.ModelSerializer):
    share_type_display = serializers.CharField(source="get_share_type_display", read_only=True)
    access_level_display = serializers.CharField(source="get_access_level_display", read_only=True)

    class Meta:
        model = ReportShare
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentProgressTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    progress_type_display = serializers.CharField(source="get_progress_type_display", read_only=True)

    class Meta:
        model = StudentProgressTracking
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
