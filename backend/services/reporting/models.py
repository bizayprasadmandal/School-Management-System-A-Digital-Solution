"""Reporting Service — Report models, templates, scheduled reports, and analytics."""

import uuid

from django.conf import settings
from django.db import models
from services.academics.models import Subject
from services.auth.models import School
from services.students.models import AcademicYear, Classroom, Student


class ReportTemplate(models.Model):
    """Reusable report templates."""

    class ReportType(models.TextChoices):
        ACADEMIC = "academic", "Academic Performance"
        ATTENDANCE = "attendance", "Attendance"
        FEE = "fee", "Fee Collection"
        ENROLLMENT = "enrollment", "Enrollment"
        DISCIPLINE = "discipline", "Discipline"
        HEALTH = "health", "Health"
        CUSTOM = "custom", "Custom"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="report_templates")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=ReportType.choices, default=ReportType.CUSTOM)
    config = models.JSONField(default=dict, blank=True, help_text="Report configuration as JSON")
    columns = models.JSONField(default=list, blank=True, help_text="List of column definitions")
    filters = models.JSONField(default=list, blank=True, help_text="Available filter options")
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "report_templates"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AcademicPerformanceReport(models.Model):
    """Subject/grade-wise performance analytics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_performance_reports")
    title = models.CharField(max_length=200)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grade = models.ForeignKey("students.Grade", on_delete=models.SET_NULL, null=True, blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    report_data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    highest_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lowest_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_academic_performance"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class TeacherPerformanceReport(models.Model):
    """Teacher analytics and performance metrics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teacher_performance_reports")
    title = models.CharField(max_length=200)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_performance_reports"
    )
    report_data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    average_class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    student_satisfaction = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    classes_taught = models.PositiveIntegerField(default=0)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_teacher_performance"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class GradeTrendReport(models.Model):
    """Grade trends over time."""

    class TrendType(models.TextChoices):
        OVER_TIME = "over_time", "Over Time"
        BY_SUBJECT = "by_subject", "By Subject"
        BY_CLASS = "by_class", "By Class"
        BY_STUDENT = "by_student", "By Student"
        COMPARISON = "comparison", "Comparison"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grade_trend_reports")
    title = models.CharField(max_length=200)
    trend_type = models.CharField(max_length=20, choices=TrendType.choices, default=TrendType.OVER_TIME)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grade = models.ForeignKey("students.Grade", on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    date_from = models.DateField()
    date_to = models.DateField()
    report_data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    trend_direction = models.CharField(max_length=20, blank=True, help_text="improving, declining, stable")
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_grade_trends"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ScheduledReport(models.Model):
    """Automated report generation and delivery."""

    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        SEMI_ANNUAL = "semi_annual", "Semi-Annual"
        ANNUAL = "annual", "Annual"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"

    class DeliveryMethod(models.TextChoices):
        EMAIL = "email", "Email"
        DASHBOARD = "dashboard", "Dashboard"
        BOTH = "both", "Both"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="scheduled_reports")
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=ReportTemplate.ReportType.choices)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.MONTHLY)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    delivery_method = models.CharField(max_length=20, choices=DeliveryMethod.choices, default=DeliveryMethod.EMAIL)
    recipients = models.JSONField(default=list, blank=True, help_text="List of recipient user IDs or emails")
    config = models.JSONField(default=dict, blank=True, help_text="Report configuration as JSON")
    last_generated = models.DateTimeField(null=True, blank=True)
    next_generation = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "report_scheduled_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_frequency_display()})"


class YearOverYearReport(models.Model):
    """Compare academic years."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="year_over_year_reports")
    title = models.CharField(max_length=200)
    academic_year_from = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="yoy_from")
    academic_year_to = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="yoy_to")
    report_data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    enrollment_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performance_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    attendance_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_year_over_year"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class DepartmentReport(models.Model):
    """Department-wise analytics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="department_reports")
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    report_data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    total_students = models.PositiveIntegerField(default=0)
    total_teachers = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_department"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ComplianceReport(models.Model):
    """Compliance and regulatory reports."""

    class ComplianceType(models.TextChoices):
        GOVERNMENT = "government", "Government Reporting"
        ACCREDITATION = "accreditation", "Accreditation"
        INSURANCE = "insurance", "Insurance"
        FINANCIAL = "financial", "Financial Compliance"
        SAFETY = "safety", "Safety Compliance"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="compliance_reports")
    title = models.CharField(max_length=200)
    compliance_type = models.CharField(max_length=20, choices=ComplianceType.choices, default=ComplianceType.OTHER)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    submission_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    report_data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    submitted_to = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "report_compliance"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ReportShare(models.Model):
    """Share reports with stakeholders."""

    class ShareType(models.TextChoices):
        STUDENT = "student", "Student"
        PARENT = "parent", "Parent"
        TEACHER = "teacher", "Teacher"
        ADMIN = "admin", "Admin"
        EXTERNAL = "external", "External"

    class AccessLevel(models.TextChoices):
        VIEW = "view", "View Only"
        DOWNLOAD = "download", "Download"
        EDIT = "edit", "Edit"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="report_shares")
    title = models.CharField(max_length=200)
    share_type = models.CharField(max_length=20, choices=ShareType.choices)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.VIEW)
    report_url = models.URLField(max_length=500, blank=True)
    report_data = models.JSONField(default=dict, blank=True)
    shared_with = models.JSONField(default=list, blank=True, help_text="List of user IDs or emails")
    expires_at = models.DateTimeField(null=True, blank=True)
    password_protected = models.BooleanField(default=False)
    access_password = models.CharField(max_length=100, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "report_shares"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class StudentProgressTracking(models.Model):
    """Individual student progress tracking."""

    class ProgressType(models.TextChoices):
        ACADEMIC = "academic", "Academic Progress"
        BEHAVIORAL = "behavioral", "Behavioral Progress"
        ATTENDANCE = "attendance", "Attendance Progress"
        OVERALL = "overall", "Overall Progress"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_progress_tracking")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="reporting_progress_tracking")
    title = models.CharField(max_length=200)
    progress_type = models.CharField(max_length=20, choices=ProgressType.choices, default=ProgressType.OVERALL)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    report_data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_student_progress"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.title}"


# =============================================================================
# NEW MODELS: Dashboard Widgets
# =============================================================================


class DashboardWidget(models.Model):
    """Configurable dashboard widgets."""

    class WidgetType(models.TextChoices):
        CHART = "chart", "Chart"
        TABLE = "table", "Table"
        KPI = "kpi", "KPI Card"
        MAP = "map", "Map"
        LIST = "list", "List"
        CALENDAR = "calendar", "Calendar"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="dashboard_widgets")
    name = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=10, choices=WidgetType.choices)
    description = models.TextField(blank=True)
    # Configuration
    data_source = models.CharField(max_length=100, blank=True, help_text="API endpoint or data query")
    config = models.JSONField(default=dict, blank=True)
    refresh_interval_seconds = models.PositiveIntegerField(default=300)
    # Layout
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=1)
    height = models.PositiveIntegerField(default=1)
    # Access
    is_default = models.BooleanField(default=False)
    visible_to_roles = models.JSONField(default=list, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reporting_dashboard_widgets"
        ordering = ["position_y", "position_x"]

    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"


class DashboardConfiguration(models.Model):
    """User dashboard configurations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="dashboard_configs")
    name = models.CharField(max_length=200)
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    # Layout
    columns = models.PositiveIntegerField(default=2)
    theme = models.CharField(max_length=50, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reporting_dashboard_configs"

    def __str__(self):
        return f"{self.name} ({self.user.full_name})"


class DashboardWidgetPlacement(models.Model):
    """Widget placements in dashboards."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(DashboardConfiguration, on_delete=models.CASCADE, related_name="placements")
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE, related_name="placements")
    position = models.PositiveIntegerField(default=0)
    custom_config = models.JSONField(default=dict, blank=True)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = "reporting_dashboard_widget_placements"
        unique_together = [("dashboard", "widget")]

    def __str__(self):
        return f"{self.widget.name} in {self.dashboard.name}"


# =============================================================================
# NEW MODELS: Report Schedules & History
# =============================================================================


class ReportSchedule(models.Model):
    """Scheduled report generation."""

    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        DISABLED = "disabled", "Disabled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_schedules")
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50)
    frequency = models.CharField(max_length=10, choices=Frequency.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Schedule
    day_of_week = models.CharField(max_length=10, blank=True)
    day_of_month = models.PositiveIntegerField(null=True, blank=True)
    time_of_day = models.TimeField()
    # Delivery
    recipients = models.ManyToManyField("auth_service.User", blank=True, related_name="report_subscriptions")
    email_delivery = models.BooleanField(default=True)
    format = models.CharField(
        max_length=10, choices=[("pdf", "PDF"), ("csv", "CSV"), ("excel", "Excel")], default="pdf"
    )
    # Filters
    filters = models.JSONField(default=dict, blank=True)
    # Status
    last_generated = models.DateTimeField(null=True, blank=True)
    next_generation = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reporting_schedules"

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class ReportHistory(models.Model):
    """History of generated reports."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATING = "generating", "Generating"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_history")
    report_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # File
    file = models.FileField(upload_to="reporting/history/", null=True, blank=True)
    file_size_bytes = models.PositiveIntegerField(default=0)
    format = models.CharField(max_length=10, default="pdf")
    # Filters used
    filters_applied = models.JSONField(default=dict, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    record_count = models.PositiveIntegerField(default=0)
    # Generation
    generated_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    scheduled = models.ForeignKey(ReportSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    generation_time_seconds = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # Sharing
    shared_with = models.ManyToManyField("auth_service.User", blank=True, related_name="shared_reports")
    is_public = models.BooleanField(default=False)
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Custom Report Builder
# =============================================================================


class CustomReport(models.Model):
    """Custom report builder."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="custom_reports")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    # Data sources
    data_sources = models.JSONField(default=list, help_text="List of data sources/models")
    # Filters
    default_filters = models.JSONField(default=dict, blank=True)
    available_filters = models.JSONField(default=list, blank=True)
    # Columns
    columns = models.JSONField(default=list, help_text="Report columns configuration")
    # Sorting
    default_sort = models.JSONField(default=dict, blank=True)
    # Grouping
    group_by = models.JSONField(default=list, blank=True)
    # Aggregations
    aggregations = models.JSONField(default=list, blank=True)
    # Charts
    chart_config = models.JSONField(default=dict, blank=True)
    # Access
    created_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=False)
    viewable_roles = models.JSONField(default=list, blank=True)
    # Usage
    total_runs = models.PositiveIntegerField(default=0)
    last_run_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reporting_custom_reports"

    def __str__(self):
        return self.name


class CustomReportExecution(models.Model):
    """Custom report execution records."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(CustomReport, on_delete=models.CASCADE, related_name="executions")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Parameters
    parameters = models.JSONField(default=dict, blank=True)
    # Output
    result_file = models.FileField(upload_to="reporting/custom/", null=True, blank=True)
    record_count = models.PositiveIntegerField(default=0)
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # Error
    error_message = models.TextField(blank=True)
    # Metadata
    executed_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_custom_report_executions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.report.name} - {self.get_status_display()} ({self.created_at})"


# =============================================================================
# NEW MODELS: Data Visualization
# =============================================================================


class ChartConfiguration(models.Model):
    """Chart configurations for reports."""

    class ChartType(models.TextChoices):
        BAR = "bar", "Bar Chart"
        LINE = "line", "Line Chart"
        PIE = "pie", "Pie Chart"
        DOUGHNUT = "doughnut", "Doughnut Chart"
        SCATTER = "scatter", "Scatter Plot"
        AREA = "area", "Area Chart"
        HEATMAP = "heatmap", "Heat Map"
        TABLE = "table", "Data Table"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="chart_configurations")
    name = models.CharField(max_length=200)
    chart_type = models.CharField(max_length=10, choices=ChartType.choices)
    # Data
    data_source = models.CharField(max_length=100)
    query = models.TextField(blank=True, help_text="SQL or API query")
    # Styling
    colors = models.JSONField(default=list, blank=True)
    config = models.JSONField(default=dict, blank=True)
    # Access
    created_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    # Usage
    total_views = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reporting_chart_configurations"

    def __str__(self):
        return f"{self.name} ({self.get_chart_type_display()})"


# =============================================================================
# NEW MODELS: KPI Tracking
# =============================================================================


class KPIDefinition(models.Model):
    """Key Performance Indicator definitions."""

    class KPICategory(models.TextChoices):
        ACADEMIC = "academic", "Academic"
        FINANCIAL = "financial", "Financial"
        OPERATIONS = "operations", "Operations"
        STUDENT_LIFE = "student_life", "Student Life"
        STAFF = "staff", "Staff"

    class DataType(models.TextChoices):
        NUMBER = "number", "Number"
        PERCENTAGE = "percentage", "Percentage"
        CURRENCY = "currency", "Currency"
        RATIO = "ratio", "Ratio"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="kpi_definitions")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=15, choices=KPICategory.choices)
    data_type = models.CharField(max_length=15, choices=DataType.choices)
    # Target
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    min_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # Thresholds
    warning_threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    critical_threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # Calculation
    formula = models.TextField(blank=True, help_text="How to calculate this KPI")
    data_source = models.CharField(max_length=100, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reporting_kpi_definitions"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class KPIValue(models.Model):
    """KPI values over time."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kpi = models.ForeignKey(KPIDefinition, on_delete=models.CASCADE, related_name="values")
    date = models.DateField()
    value = models.DecimalField(max_digits=12, decimal_places=2)
    target_met = models.BooleanField(default=False)
    trend = models.CharField(max_length=10, blank=True, help_text="up, down, stable")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_kpi_values"
        unique_together = [("kpi", "date")]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.kpi.name}: {self.value} ({self.date})"


# =============================================================================
# NEW MODELS: Report Sharing
# =============================================================================


class ReportAccessLog(models.Model):
    """Track report access."""

    class AccessType(models.TextChoices):
        VIEW = "view", "View"
        DOWNLOAD = "download", "Download"
        SHARE = "share", "Share"
        EXPORT = "export", "Export"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_history = models.ForeignKey(ReportHistory, on_delete=models.CASCADE, related_name="access_logs")
    user = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    access_type = models.CharField(max_length=10, choices=AccessType.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_access_logs"
        ordering = ["-accessed_at"]

    def __str__(self):
        return f"{self.get_access_type_display()} - {self.report_history.title}"


class ReportComment(models.Model):
    """Comments on reports."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_history = models.ForeignKey(ReportHistory, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="report_comments")
    comment = models.TextField()
    # Threading
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reporting_comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user.full_name} on {self.report_history.title}"


# =============================================================================
# NEW MODELS: Data Sources
# =============================================================================


class ReportDataSource(models.Model):
    """Data source configurations for reports."""

    class SourceType(models.TextChoices):
        MODEL = "model", "Django Model"
        VIEW = "view", "Database View"
        API = "api", "External API"
        SQL = "sql", "Raw SQL"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_data_sources")
    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=10, choices=SourceType.choices)
    # Connection
    model_path = models.CharField(max_length=200, blank=True, help_text="e.g., students.Student")
    view_name = models.CharField(max_length=200, blank=True)
    api_url = models.URLField(max_length=500, blank=True)
    sql_query = models.TextField(blank=True)
    # Schema
    fields = models.JSONField(default=list, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reporting_data_sources"

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


# =============================================================================
# NEW MODELS: Report Bookmarks
# =============================================================================


class ReportBookmark(models.Model):
    """Bookmarked reports for quick access."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="report_bookmarks")
    report_type = models.CharField(max_length=50)
    report_id = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Saved filters
    saved_filters = models.JSONField(default=dict, blank=True)
    # Ordering
    sort_order = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_bookmarks"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.name} ({self.user.full_name})"


# =============================================================================
# NEW MODELS: Report Email Delivery
# =============================================================================


class ReportEmailDelivery(models.Model):
    """Track report email deliveries."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        BOUNCED = "bounced", "Bounced"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_history = models.ForeignKey(ReportHistory, on_delete=models.CASCADE, related_name="email_deliveries")
    recipient = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="report_email_deliveries")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    subject = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_email_deliveries"

    def __str__(self):
        return f"Report Email to {self.recipient.full_name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Analytics Snapshots
# =============================================================================


class AnalyticsSnapshot(models.Model):
    """Point-in-time analytics snapshots."""

    class SnapshotType(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        TERM = "term", "Term"
        YEARLY = "yearly", "Yearly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="analytics_snapshots")
    snapshot_type = models.CharField(max_length=10, choices=SnapshotType.choices)
    snapshot_date = models.DateField()
    # Data
    data = models.JSONField(default=dict)
    # Students
    total_students = models.PositiveIntegerField(default=0)
    total_staff = models.PositiveIntegerField(default=0)
    # Academic
    avg_attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Financial
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    # Enrollment
    new_enrollments = models.PositiveIntegerField(default=0)
    dropouts = models.PositiveIntegerField(default=0)
    retention_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_analytics_snapshots"
        unique_together = [("school", "snapshot_type", "snapshot_date")]
        ordering = ["-snapshot_date"]

    def __str__(self):
        return f"{self.get_snapshot_type_display()} Snapshot - {self.snapshot_date}"


class ReportFavorite(models.Model):
    """User favorite reports."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="report_favorites")
    report_type = models.CharField(max_length=50)
    report_name = models.CharField(max_length=200)
    report_config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_favorites"
        unique_together = [("user", "report_type", "report_name")]

    def __str__(self):
        return f"{self.report_name} ({self.user.full_name})"


class ReportTemplateParameter(models.Model):
    """Parameters for report templates."""

    class ParamType(models.TextChoices):
        DATE = "date", "Date"
        SELECT = "select", "Dropdown"
        TEXT = "text", "Text Input"
        NUMBER = "number", "Number"
        BOOLEAN = "boolean", "Boolean"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name="parameters")
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    param_type = models.CharField(max_length=15, choices=ParamType.choices)
    is_required = models.BooleanField(default=True)
    default_value = models.CharField(max_length=200, blank=True)
    options = models.JSONField(default=list, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_template_parameters"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.display_name} ({self.get_param_type_display()})"


class ReportAlert(models.Model):
    """Alerts based on report data thresholds."""

    class AlertType(models.TextChoices):
        THRESHOLD = "threshold", "Threshold Breach"
        TREND = "trend", "Trend Alert"
        ANOMALY = "anomaly", "Anomaly Detection"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        TRIGGERED = "triggered", "Triggered"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_alerts")
    name = models.CharField(max_length=200)
    alert_type = models.CharField(max_length=10, choices=AlertType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    metric = models.CharField(max_length=100)
    threshold_value = models.DecimalField(max_digits=12, decimal_places=2)
    notify_users = models.ManyToManyField("auth_service.User", blank=True, related_name="report_alerts")
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    trigger_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_alerts"

    def __str__(self):
        return f"{self.name} ({self.get_alert_type_display()})"


class ReportExport(models.Model):
    """Report export history."""

    class Format(models.TextChoices):
        PDF = "pdf", "PDF"
        CSV = "csv", "CSV"
        EXCEL = "excel", "Excel"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATING = "generating", "Generating"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_exports")
    report_type = models.CharField(max_length=50)
    format = models.CharField(max_length=10, choices=Format.choices, default=Format.PDF)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    filters = models.JSONField(default=dict, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to="reporting/exports/", null=True, blank=True)
    record_count = models.PositiveIntegerField(default=0)
    requested_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "reporting_exports"
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.report_type} ({self.get_format_display()}) - {self.get_status_display()}"


class ReportInsight(models.Model):
    """AI-generated insights from reports."""

    class InsightType(models.TextChoices):
        TREND = "trend", "Trend Insight"
        ANOMALY = "anomaly", "Anomaly"
        RECOMMENDATION = "recommendation", "Recommendation"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_insights")
    insight_type = models.CharField(max_length=15, choices=InsightType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    metric = models.CharField(max_length=100, blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    change_percentage = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    priority = models.CharField(max_length=10, default="medium")
    is_read = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_insights"
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.title} ({self.get_insight_type_display()})"


class ReportVersion(models.Model):
    """Version control for reports."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField(default=1)
    config_snapshot = models.JSONField(default=dict)
    is_current = models.BooleanField(default=False)
    created_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "reporting_versions"
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.template.name} v{self.version_number}"


class ReportFolder(models.Model):
    """Folders for organizing reports."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_folders")
    name = models.CharField(max_length=200)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    description = models.TextField(blank=True)
    owner = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_folders"

    def __str__(self):
        return self.name


class ReportFolderItem(models.Model):
    """Items in report folders."""

    class ItemType(models.TextChoices):
        REPORT = "report", "Report"
        FOLDER = "folder", "Sub-folder"
        BOOKMARK = "bookmark", "Bookmark"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(ReportFolder, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=10, choices=ItemType.choices)
    item_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_folder_items"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()})"


class ReportAccessControl(models.Model):
    """Access control for reports."""

    class AccessLevel(models.TextChoices):
        VIEW = "view", "View Only"
        EDIT = "edit", "Edit"
        ADMIN = "admin", "Full Access"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=50)
    user = models.ForeignKey(
        "auth_service.User", on_delete=models.CASCADE, null=True, blank=True, related_name="report_access_controls"
    )
    role = models.CharField(max_length=50, blank=True)
    access_level = models.CharField(max_length=10, choices=AccessLevel.choices)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    granted_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_access_controls"

    def __str__(self):
        target = self.user.full_name if self.user else self.role
        return f"{self.report_type} - {target} ({self.get_access_level_display()})"


class ReportAnalytics(models.Model):
    """Report usage analytics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_usage_analytics")
    date = models.DateField()
    total_reports_generated = models.PositiveIntegerField(default=0)
    total_reports_viewed = models.PositiveIntegerField(default=0)
    total_reports_exported = models.PositiveIntegerField(default=0)
    by_type_breakdown = models.JSONField(default=dict, blank=True)
    top_reports = models.JSONField(default=list, blank=True)
    active_users = models.PositiveIntegerField(default=0)
    avg_generation_time = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_usage_analytics"
        unique_together = [("school", "date")]

    def __str__(self):
        return f"Report Analytics - {self.date}"


class ReportScheduleDelivery(models.Model):
    """Track scheduled report deliveries."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.CASCADE, related_name="deliveries")
    report_history = models.ForeignKey(ReportHistory, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    recipient_count = models.PositiveIntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_schedule_deliveries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Delivery - {self.schedule.name} ({self.get_status_display()})"


class ReportDataCache(models.Model):
    """Cache for report data to improve performance."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_data_caches")
    cache_key = models.CharField(max_length=255, unique=True)
    report_type = models.CharField(max_length=50)
    # Data
    data = models.JSONField(default=dict)
    data_hash = models.CharField(max_length=64, blank=True)
    # Validity
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    # Usage
    hit_count = models.PositiveIntegerField(default=0)
    last_hit_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "reporting_data_caches"
        indexes = [
            models.Index(fields=["cache_key", "expires_at"]),
        ]

    def __str__(self):
        return f"Cache: {self.cache_key} ({self.hit_count} hits)"


class ReportComparison(models.Model):
    """Compare reports across periods."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="report_comparisons")
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50)
    # Periods
    period_a_start = models.DateField()
    period_a_end = models.DateField()
    period_b_start = models.DateField()
    period_b_end = models.DateField()
    # Results
    comparison_data = models.JSONField(default=dict)
    highlights = models.TextField(blank=True)
    # Metadata
    created_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_comparisons"

    def __str__(self):
        return f"{self.name} ({self.report_type})"


class ReportSubscription(models.Model):
    """Subscribe to report updates."""

    class UpdateType(models.TextChoices):
        NEW_DATA = "new_data", "New Data Available"
        THRESHOLD = "threshold", "Threshold Breached"
        SCHEDULED = "scheduled", "Scheduled Report Ready"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="report_update_subscriptions")
    report_type = models.CharField(max_length=50)
    update_type = models.CharField(max_length=15, choices=UpdateType.choices)
    is_active = models.BooleanField(default=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reporting_subscriptions"
        unique_together = [("user", "report_type", "update_type")]

    def __str__(self):
        return f"{self.report_type} - {self.get_update_type_display()} ({self.user.full_name})"
