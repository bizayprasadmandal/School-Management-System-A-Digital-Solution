"""HR & Payroll — Django Admin registrations."""

from django.contrib import admin

from .models import (
    Applicant,
    BenefitPlan,
    Certification,
    DataRetentionPolicy,
    Department,
    Employee,
    EmployeeBenefit,
    EmployeeDocument,
    EmployeeProfileUpdate,
    EmployeeSalary,
    HRAuditLog,
    HRDashboardMetrics,
    InterviewSchedule,
    JobPosting,
    LeaveBalanceHR,
    LeaveRequest,
    OnboardingChecklist,
    OnboardingProgress,
    OnboardingTask,
    OvertimeRequest,
    Payslip,
    PayslipViewLog,
    PeerFeedback,
    PerformanceGoal,
    PerformanceReview,
    PerformanceReviewCycle,
    PolicyAcknowledgment,
    PolicyDocument,
    SalaryReport,
    SalaryStructure,
    TimeEntry,
    Timesheet,
    TrainingEnrollment,
    TrainingProgram,
    TurnoverReport,
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


# ---------------------------------------------------------------------------
# P6: Employee Self-Service
# ---------------------------------------------------------------------------


@admin.register(EmployeeProfileUpdate)
class EmployeeProfileUpdateAdmin(admin.ModelAdmin):
    list_display = ["employee", "field_name", "old_value", "new_value", "status"]
    list_filter = ["status"]
    search_fields = ["employee__user__full_name"]


@admin.register(PayslipViewLog)
class PayslipViewLogAdmin(admin.ModelAdmin):
    list_display = ["employee", "payslip", "viewed_at"]
    date_hierarchy = "viewed_at"


@admin.register(LeaveBalanceHR)
class LeaveBalanceHRAdmin(admin.ModelAdmin):
    list_display = ["employee", "leave_type", "year", "total_days", "used_days", "carried_over"]
    list_filter = ["leave_type", "year"]
    search_fields = ["employee__user__full_name"]


# ---------------------------------------------------------------------------
# P7: HR Analytics
# ---------------------------------------------------------------------------


@admin.register(HRDashboardMetrics)
class HRDashboardMetricsAdmin(admin.ModelAdmin):
    list_display = ["school", "total_employees", "active_employees", "calculated_at"]
    date_hierarchy = "calculated_at"


@admin.register(TurnoverReport)
class TurnoverReportAdmin(admin.ModelAdmin):
    list_display = ["school", "month", "total_employees_start", "new_hires", "separations", "turnover_rate"]
    date_hierarchy = "month"


@admin.register(SalaryReport)
class SalaryReportAdmin(admin.ModelAdmin):
    list_display = ["school", "month", "total_gross", "total_net", "headcount"]
    date_hierarchy = "month"


# ---------------------------------------------------------------------------
# P8: Document Management
# ---------------------------------------------------------------------------


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ["employee", "document_type", "title", "expiry_date", "is_verified"]
    list_filter = ["document_type", "is_verified"]
    search_fields = ["employee__user__full_name", "title"]


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "document_type", "version", "status", "effective_date"]
    list_filter = ["status", "document_type"]
    search_fields = ["title", "description"]


@admin.register(PolicyAcknowledgment)
class PolicyAcknowledgmentAdmin(admin.ModelAdmin):
    list_display = ["employee", "policy", "acknowledged_at"]
    list_filter = ["policy"]
    date_hierarchy = "acknowledged_at"


# ---------------------------------------------------------------------------
# P9: Compliance & Audit
# ---------------------------------------------------------------------------


@admin.register(HRAuditLog)
class HRAuditLogAdmin(admin.ModelAdmin):
    list_display = ["action_type", "model_name", "object_id", "performed_by", "created_at"]
    list_filter = ["action_type", "model_name"]
    search_fields = ["object_repr", "notes"]
    date_hierarchy = "created_at"
    readonly_fields = [
        "id",
        "school",
        "action_type",
        "model_name",
        "object_id",
        "object_repr",
        "old_values",
        "new_values",
        "performed_by",
        "ip_address",
        "notes",
        "created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ["model_name", "retention_days", "auto_delete", "last_purge_date", "is_active"]
    list_filter = ["is_active", "auto_delete"]
    search_fields = ["model_name"]
