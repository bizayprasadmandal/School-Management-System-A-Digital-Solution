from django.contrib import admin

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


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "is_public", "created_at"]
    list_filter = ["report_type", "is_public"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(AcademicPerformanceReport)
class AcademicPerformanceReportAdmin(admin.ModelAdmin):
    list_display = ["title", "academic_year", "average_score", "pass_rate", "created_at"]
    list_filter = ["academic_year"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]


@admin.register(TeacherPerformanceReport)
class TeacherPerformanceReportAdmin(admin.ModelAdmin):
    list_display = ["title", "teacher", "academic_year", "average_class_score", "created_at"]
    list_filter = ["academic_year"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]


@admin.register(GradeTrendReport)
class GradeTrendReportAdmin(admin.ModelAdmin):
    list_display = ["title", "trend_type", "academic_year", "trend_direction", "created_at"]
    list_filter = ["trend_type", "academic_year"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "frequency", "status", "last_generated"]
    list_filter = ["report_type", "frequency", "status"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(YearOverYearReport)
class YearOverYearReportAdmin(admin.ModelAdmin):
    list_display = ["title", "academic_year_from", "academic_year_to", "created_at"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]


@admin.register(DepartmentReport)
class DepartmentReportAdmin(admin.ModelAdmin):
    list_display = ["title", "department", "academic_year", "average_score", "created_at"]
    list_filter = ["department"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ["title", "compliance_type", "status", "due_date", "created_at"]
    list_filter = ["compliance_type", "status"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ReportShare)
class ReportShareAdmin(admin.ModelAdmin):
    list_display = ["title", "share_type", "access_level", "view_count", "created_at"]
    list_filter = ["share_type", "access_level"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(StudentProgressTracking)
class StudentProgressTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "title", "progress_type", "academic_year", "created_at"]
    list_filter = ["progress_type"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]
