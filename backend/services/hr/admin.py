"""HR & Payroll — Django Admin registrations."""

from django.contrib import admin

from .models import (
    Applicant,
    BenefitPlan,
    Certification,
    Department,
    Employee,
    EmployeeBenefit,
    EmployeeSalary,
    InterviewSchedule,
    JobPosting,
    LeaveRequest,
    OnboardingChecklist,
    OnboardingProgress,
    OnboardingTask,
    OvertimeRequest,
    Payslip,
    PeerFeedback,
    PerformanceGoal,
    PerformanceReview,
    PerformanceReviewCycle,
    SalaryStructure,
    TimeEntry,
    Timesheet,
    TrainingEnrollment,
    TrainingProgram,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "school", "head", "is_active"]
    list_filter = ["is_active", "school"]
    search_fields = ["name", "code"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "user", "department", "designation", "employment_type", "status"]
    list_filter = ["status", "employment_type", "department"]
    search_fields = ["employee_id", "user__full_name", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ["name", "designation", "basic_salary", "net_salary", "is_active"]
    list_filter = ["is_active", "department"]
    search_fields = ["name", "designation"]


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ["employee", "basic_salary", "net_salary", "effective_from", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["employee__user__full_name"]
    readonly_fields = ["id", "created_at"]


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ["employee", "period_start", "period_end", "net_pay", "status"]
    list_filter = ["status"]
    search_fields = ["employee__user__full_name", "employee__employee_id"]
    readonly_fields = ["id", "created_at"]


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ["employee", "leave_type", "from_date", "to_date", "total_days", "status"]
    list_filter = ["leave_type", "status"]
    search_fields = ["employee__user__full_name", "reason"]
    readonly_fields = ["id", "created_at"]


# ---------------------------------------------------------------------------
# P1: Performance Management
# ---------------------------------------------------------------------------


@admin.register(PerformanceReviewCycle)
class PerformanceReviewCycleAdmin(admin.ModelAdmin):
    list_display = ["name", "start_date", "end_date", "status"]
    list_filter = ["status"]
    search_fields = ["name"]


@admin.register(PerformanceGoal)
class PerformanceGoalAdmin(admin.ModelAdmin):
    list_display = ["employee", "title", "cycle", "priority", "status", "progress_pct"]
    list_filter = ["status", "priority"]
    search_fields = ["title", "description"]


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ["employee", "cycle", "overall_rating", "status", "promotion_recommended"]
    list_filter = ["status", "overall_rating"]
    search_fields = ["employee__user__full_name"]


@admin.register(PeerFeedback)
class PeerFeedbackAdmin(admin.ModelAdmin):
    list_display = ["review", "reviewer", "feedback_type", "overall_score", "submitted_at"]
    list_filter = ["feedback_type"]


# ---------------------------------------------------------------------------
# P2: Recruitment & Onboarding
# ---------------------------------------------------------------------------


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ["title", "department", "employment_type", "status", "posted_date"]
    list_filter = ["status", "employment_type"]
    search_fields = ["title", "description"]


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "job_posting", "status"]
    list_filter = ["status"]
    search_fields = ["first_name", "last_name", "email"]


@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ["applicant", "interviewer", "interview_type", "scheduled_date", "status"]
    list_filter = ["interview_type", "status"]


@admin.register(OnboardingChecklist)
class OnboardingChecklistAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(OnboardingTask)
class OnboardingTaskAdmin(admin.ModelAdmin):
    list_display = ["title", "checklist", "order", "due_days_after_joining", "is_mandatory"]
    list_filter = ["is_mandatory"]


@admin.register(OnboardingProgress)
class OnboardingProgressAdmin(admin.ModelAdmin):
    list_display = ["employee", "task", "status", "completed_at"]
    list_filter = ["status"]


# ---------------------------------------------------------------------------
# P3: Time & Attendance
# ---------------------------------------------------------------------------


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ["employee", "date", "clock_in", "clock_out", "total_hours", "status"]
    list_filter = ["status", "date"]
    date_hierarchy = "date"


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ["employee", "week_start", "week_end", "total_hours", "status"]
    list_filter = ["status"]


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ["employee", "date", "hours", "status"]
    list_filter = ["status"]
    date_hierarchy = "date"


# ---------------------------------------------------------------------------
# P4: Benefits
# ---------------------------------------------------------------------------


@admin.register(BenefitPlan)
class BenefitPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "benefit_type", "provider", "employee_contribution", "is_active"]
    list_filter = ["benefit_type", "is_active"]
    search_fields = ["name", "provider"]


@admin.register(EmployeeBenefit)
class EmployeeBenefitAdmin(admin.ModelAdmin):
    list_display = ["employee", "plan", "status", "enrollment_date"]
    list_filter = ["status"]


# ---------------------------------------------------------------------------
# P5: Training & Development
# ---------------------------------------------------------------------------


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ["name", "training_type", "start_date", "status", "is_mandatory"]
    list_filter = ["training_type", "status", "is_mandatory"]
    search_fields = ["name", "description"]


@admin.register(TrainingEnrollment)
class TrainingEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["employee", "program", "status", "enrolled_date", "completed_date"]
    list_filter = ["status"]


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ["employee", "name", "issuing_organization", "expiry_date", "status"]
    list_filter = ["status"]
    search_fields = ["name", "issuing_organization"]
