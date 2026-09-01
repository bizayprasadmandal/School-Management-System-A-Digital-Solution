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
