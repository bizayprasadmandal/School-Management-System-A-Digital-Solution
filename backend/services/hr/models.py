"""HR & Payroll — Employee management, salary structures, payslips, leave tracking,
performance management, recruitment, time tracking, benefits, and training."""

import uuid

from django.db import models
from django.utils import timezone
from services.auth.models import School, User


class Department(models.Model):
    """School departments (e.g., Mathematics, Science, Administration)."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_departments"
        unique_together = [("school", "name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Staff/employee records linked to User accounts."""

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full-Time"
        PART_TIME = "part_time", "Part-Time"
        CONTRACT = "contract", "Contract"
        INTERN = "intern", "Intern"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On Leave"
        TERMINATED = "terminated", "Terminated"
        RESIGNED = "resigned", "Resigned"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="employees")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="employee_profile")
    employee_id = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )
    designation = models.CharField(max_length=100)
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    joining_date = models.DateField()
    exit_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_routing_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_employees"
        ordering = ["employee_id"]

    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"


class SalaryStructure(models.Model):
    """Salary template applied to employees based on designation/department."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="salary_structures")
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pension_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_salary_structures"
        ordering = ["name"]

    @property
    def total_earnings(self):
        return (
            self.basic_salary
            + self.housing_allowance
            + self.transport_allowance
            + self.medical_allowance
            + self.other_allowances
        )

    @property
    def total_deductions(self):
        return self.tax_deduction + self.pension_deduction + self.other_deductions

    @property
    def net_salary(self):
        return self.total_earnings - self.total_deductions

    def __str__(self):
        return self.name


class EmployeeSalary(models.Model):
    """Assignment of a salary structure to an employee with optional overrides."""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salaries")
    structure = models.ForeignKey(SalaryStructure, on_delete=models.SET_NULL, null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pension_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_employee_salaries"
        ordering = ["-effective_from"]

    @property
    def total_earnings(self):
        return (
            self.basic_salary
            + self.housing_allowance
            + self.transport_allowance
            + self.medical_allowance
            + self.other_allowances
        )

    @property
    def total_deductions(self):
        return self.tax_deduction + self.pension_deduction + self.other_deductions

    @property
    def net_salary(self):
        return self.total_earnings - self.total_deductions

    def __str__(self):
        return f"{self.employee} — {self.basic_salary} ({self.effective_from})"


class Payslip(models.Model):
    """Monthly/periodic payslip generated for each employee."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="payslips")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="payslips")
    period_start = models.DateField()
    period_end = models.DateField()
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pension_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_payslips",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_payslips"
        ordering = ["-period_start", "employee__employee_id"]
        unique_together = [("employee", "period_start", "period_end")]

    def __str__(self):
        return f"Payslip {self.employee.employee_id} - {self.period_start}"


class LeaveRequest(models.Model):
    """Staff leave request and approval workflow."""

    class LeaveType(models.TextChoices):
        ANNUAL = "annual", "Annual Leave"
        SICK = "sick", "Sick Leave"
        PERSONAL = "personal", "Personal Leave"
        MATERNITY = "maternity", "Maternity Leave"
        PATERNITY = "paternity", "Paternity Leave"
        UNPAID = "unpaid", "Unpaid Leave"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="leave_requests")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    from_date = models.DateField()
    to_date = models.DateField()
    total_days = models.PositiveSmallIntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leave_requests",
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_leave_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type} ({self.from_date} - {self.to_date})"


class AccountantProfile(models.Model):
    """Extended accountant profile — professional information for self-service editing."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="accountant_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="accountant_profiles")
    qualification = models.CharField(
        max_length=100, blank=True, help_text="Professional qualification (e.g., ACCA, CPA, MBA Finance)"
    )
    specialization = models.CharField(
        max_length=100, blank=True, help_text="Area of expertise (e.g., Taxation, Audit, Financial Planning)"
    )
    experience_years = models.PositiveSmallIntegerField(default=0, help_text="Years of professional experience")
    certifications = models.TextField(blank=True, help_text="Professional certifications and licenses")
    bio = models.TextField(blank=True, help_text="Professional biography")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accountant_profiles"
        verbose_name = "Accountant Profile"
        verbose_name_plural = "Accountant Profiles"

    def __str__(self):
        return f"{self.user.full_name} — Accountant Profile"


# ---------------------------------------------------------------------------
# P1: Performance Management
# ---------------------------------------------------------------------------


class PerformanceReviewCycle(models.Model):
    """Defines a review period (e.g., Q1 2026, Annual 2026)."""

    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="review_cycles")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNING)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_review_cycles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_review_cycles"
        unique_together = [("school", "name")]
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.start_date} — {self.end_date})"


class PerformanceGoal(models.Model):
    """Individual or team goal set for an employee."""

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="goals")
    cycle = models.ForeignKey(PerformanceReviewCycle, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True, help_text="e.g. Teaching, Administration, Research")
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NOT_STARTED)
    target_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, blank=True, help_text="e.g. %, count, score")
    progress_pct = models.PositiveSmallIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_performance_goals"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["employee", "cycle"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.employee}"


class PerformanceReview(models.Model):
    """Formal performance review for an employee."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SELF_REVIEW = "self_review", "Awaiting Self-Review"
        MANAGER_REVIEW = "manager_review", "Awaiting Manager Review"
        HR_REVIEW = "hr_review", "Awaiting HR Review"
        COMPLETED = "completed", "Completed"
        APPEALED = "appealed", "Appealed"

    class Rating(models.TextChoices):
        EXCEPTIONAL = "5", "Exceptional (5)"
        EXCEEDS = "4", "Exceeds Expectations (4)"
        MEETS = "3", "Meets Expectations (3)"
        NEEDS_IMPROVEMENT = "2", "Needs Improvement (2)"
        UNSATISFACTORY = "1", "Unsatisfactory (1)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="performance_reviews")
    cycle = models.ForeignKey(PerformanceReviewCycle, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="conducted_reviews")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    overall_rating = models.CharField(max_length=2, choices=Rating.choices, null=True, blank=True)
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    goals_summary = models.TextField(blank=True, help_text="Summary of goal achievement")
    development_plan = models.TextField(blank=True, help_text="Future development actions")
    self_comments = models.TextField(blank=True, help_text="Employee self-assessment")
    manager_comments = models.TextField(blank=True)
    hr_comments = models.TextField(blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    promotion_recommended = models.BooleanField(default=False)
    salary_revision_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Recommended salary revision percentage"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_performance_reviews"
        unique_together = [("employee", "cycle")]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["employee", "cycle"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Review: {self.employee} — {self.cycle.name}"

    @property
    def rating_display(self):
        return self.get_overall_rating_display() or "Not rated"


class PeerFeedback(models.Model):
    """Peer feedback submitted during a review cycle."""

    class FeedbackType(models.TextChoices):
        PEER = "peer", "Peer Feedback"
        SUBORDINATE = "subordinate", "Subordinate Feedback"
        SELF = "self", "Self Feedback"
        CUSTOMER = "customer", "External Feedback"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(PerformanceReview, on_delete=models.CASCADE, related_name="peer_feedbacks")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedback_given")
    feedback_type = models.CharField(max_length=15, choices=FeedbackType.choices, default=FeedbackType.PEER)
    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    collaboration_score = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 scale")
    communication_score = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 scale")
    overall_score = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 scale")
    comments = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_peer_feedbacks"
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["review", "feedback_type"]),
        ]

    def __str__(self):
        return f"Feedback by {self.reviewer} for {self.review.employee}"


# ---------------------------------------------------------------------------
# P2: Recruitment & Onboarding
# ---------------------------------------------------------------------------


class JobPosting(models.Model):
    """Job posting for open positions."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        FILLED = "filled", "Filled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="job_postings")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    employment_type = models.CharField(
        max_length=20,
        choices=Employee.EmploymentType.choices,
        default=Employee.EmploymentType.FULL_TIME,
    )
    designation = models.CharField(max_length=100)
    salary_range_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_range_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    positions_count = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    posted_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="posted_jobs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_job_postings"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "status"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.department or 'General'}"


class Applicant(models.Model):
    """Job applicant record."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        SCREENING = "screening", "Screening"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer Extended"
        HIRED = "hired", "Hired"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="applicants")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    resume_url = models.URLField(max_length=500, blank=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
    source = models.CharField(max_length=50, blank=True, help_text="e.g. Website, Referral, LinkedIn")
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_applicants"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_applicants"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["job_posting", "status"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.job_posting.title}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class InterviewSchedule(models.Model):
    """Interview scheduling for applicants."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    class InterviewType(models.TextChoices):
        PHONE = "phone", "Phone Screen"
        VIDEO = "video", "Video Call"
        IN_PERSON = "in_person", "In-Person"
        PANEL = "panel", "Panel Interview"
        TECHNICAL = "technical", "Technical Assessment"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="interviews")
    interviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conducted_interviews")
    interview_type = models.CharField(max_length=15, choices=InterviewType.choices)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 rating")
    feedback = models.TextField(blank=True)
    recommendation = models.CharField(
        max_length=20,
        blank=True,
        choices=[("hire", "Hire"), ("maybe", "Maybe"), ("no_hire", "Don't Hire")],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_interview_schedules"
        ordering = ["scheduled_date", "scheduled_time"]
        indexes = [
            models.Index(fields=["applicant", "status"]),
        ]

    def __str__(self):
        return f"Interview: {self.applicant} — {self.scheduled_date}"


class OnboardingChecklist(models.Model):
    """Onboarding task checklist for new hires."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="onboarding_checklists")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_onboarding_checklists"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OnboardingTask(models.Model):
    """Individual onboarding task within a checklist."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checklist = models.ForeignKey(OnboardingChecklist, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="onboarding_tasks"
    )
    order = models.PositiveSmallIntegerField(default=0)
    due_days_after_joining = models.PositiveSmallIntegerField(default=0, help_text="Days after employee joining date")
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_onboarding_tasks"
        ordering = ["order"]
        indexes = [
            models.Index(fields=["checklist", "order"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.checklist.name}"


class OnboardingProgress(models.Model):
    """Tracks an employee's progress through onboarding tasks."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="onboarding_progress")
    task = models.ForeignKey(OnboardingTask, on_delete=models.CASCADE, related_name="progress")
    status = models.CharField(
        max_length=15,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ],
        default="pending",
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_onboarding_progress"
        unique_together = [("employee", "task")]
        indexes = [
            models.Index(fields=["employee", "status"]),
        ]

    def __str__(self):
        return f"{self.employee} — {self.task.title} ({self.status})"


# ---------------------------------------------------------------------------
# P3: Time & Attendance (HR side)
# ---------------------------------------------------------------------------


class TimeEntry(models.Model):
    """Daily time tracking for employees."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="time_entries")
    date = models.DateField()
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    break_minutes = models.PositiveSmallIntegerField(default=0)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_time_entries"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_time_entries"
        unique_together = [("employee", "date")]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["employee", "date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.employee} — {self.date} ({self.total_hours}h)"

    def calculate_hours(self):
        """Calculate total and overtime hours."""
        if self.clock_in and self.clock_out:
            from datetime import timedelta

            work_duration = self.clock_out - self.clock_in
            break_duration = timedelta(minutes=self.break_minutes)
            net_duration = work_duration - break_duration
            self.total_hours = round(net_duration.total_seconds() / 3600, 2)
            # Standard 8-hour day
            self.overtime_hours = max(0, self.total_hours - 8)
        return self.total_hours


class Timesheet(models.Model):
    """Weekly timesheet aggregating daily entries."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="timesheets")
    week_start = models.DateField(help_text="Monday of the week")
    week_end = models.DateField()
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_overtime = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_timesheets"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_timesheets"
        unique_together = [("employee", "week_start")]
        ordering = ["-week_start"]
        indexes = [
            models.Index(fields=["employee", "week_start"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Timesheet: {self.employee} — {self.week_start} to {self.week_end}"

    def calculate_totals(self):
        """Aggregate daily time entries for the week."""
        entries = TimeEntry.objects.filter(
            employee=self.employee,
            date__gte=self.week_start,
            date__lte=self.week_end,
        )
        self.total_hours = sum(e.total_hours for e in entries)
        self.total_overtime = sum(e.overtime_hours for e in entries)
        return self.total_hours


class OvertimeRequest(models.Model):
    """Request for overtime approval."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="overtime_requests")
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_overtime"
    )
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_overtime_requests"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["employee", "status"]),
        ]

    def __str__(self):
        return f"{self.employee} — {self.date} ({self.hours}h)"


# ---------------------------------------------------------------------------
# P4: Benefits Management
# ---------------------------------------------------------------------------


class BenefitPlan(models.Model):
    """Available benefit plans (health insurance, retirement, etc.)."""

    class BenefitType(models.TextChoices):
        HEALTH = "health", "Health Insurance"
        DENTAL = "dental", "Dental Insurance"
        VISION = "vision", "Vision Insurance"
        LIFE = "life", "Life Insurance"
        RETIREMENT = "retirement", "Retirement Plan"
        DISABILITY = "disability", "Disability Insurance"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="benefit_plans")
    name = models.CharField(max_length=255)
    benefit_type = models.CharField(max_length=15, choices=BenefitType.choices)
    description = models.TextField(blank=True)
    provider = models.CharField(max_length=255, blank=True)
    employee_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    employer_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    enrollment_start = models.DateField(null=True, blank=True)
    enrollment_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_benefit_plans"
        ordering = ["benefit_type", "name"]
        indexes = [
            models.Index(fields=["school", "benefit_type"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_benefit_type_display()})"

    @property
    def total_contribution(self):
        return self.employee_contribution + self.employer_contribution


class EmployeeBenefit(models.Model):
    """Employee enrollment in a benefit plan."""

    class Status(models.TextChoices):
        ENROLLED = "enrolled", "Enrolled"
        PENDING = "pending", "Pending"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="benefits")
    plan = models.ForeignKey(BenefitPlan, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    enrollment_date = models.DateField()
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    dependents_count = models.PositiveSmallIntegerField(default=0)
    employee_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    employer_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_employee_benefits"
        unique_together = [("employee", "plan")]
        ordering = ["-enrollment_date"]
        indexes = [
            models.Index(fields=["employee", "status"]),
        ]

    def __str__(self):
        return f"{self.employee} → {self.plan.name} ({self.status})"


# ---------------------------------------------------------------------------
# P5: Training & Development
# ---------------------------------------------------------------------------


class TrainingProgram(models.Model):
    """Training course or program."""

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class TrainingType(models.TextChoices):
        WORKSHOP = "workshop", "Workshop"
        SEMINAR = "seminar", "Seminar"
        COURSE = "course", "Online Course"
        CERTIFICATION = "certification", "Certification"
        CONFERENCE = "conference", "Conference"
        ON_JOB = "on_job", "On-the-Job Training"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="training_programs")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    training_type = models.CharField(max_length=15, choices=TrainingType.choices)
    provider = models.CharField(max_length=255, blank=True)
    instructor = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    duration_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    max_participants = models.PositiveSmallIntegerField(null=True, blank=True)
    cost_per_participant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNED)
    location = models.CharField(max_length=255, blank=True)
    is_mandatory = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_trainings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_training_programs"
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["school", "status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_date})"

    @property
    def enrollment_count(self):
        return self.enrollments.count()


class TrainingEnrollment(models.Model):
    """Employee enrollment in a training program."""

    class Status(models.TextChoices):
        ENROLLED = "enrolled", "Enrolled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        DROPPED = "dropped", "Dropped"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name="enrollments")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="training_enrollments")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ENROLLED)
    enrolled_date = models.DateField(auto_now_add=True)
    completed_date = models.DateField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    certificate_url = models.URLField(max_length=500, blank=True)
    hours_attended = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    feedback = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 rating")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_training_enrollments"
        unique_together = [("program", "employee")]
        ordering = ["-enrolled_date"]
        indexes = [
            models.Index(fields=["employee", "status"]),
        ]

    def __str__(self):
        return f"{self.employee} → {self.program.name}"


class Certification(models.Model):
    """Employee certifications and licenses tracking."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        PENDING_RENEWAL = "pending_renewal", "Pending Renewal"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    document_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_certifications"
        ordering = ["-expiry_date"]
        indexes = [
            models.Index(fields=["employee", "status"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.employee}"

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    @property
    def days_until_expiry(self):
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None
