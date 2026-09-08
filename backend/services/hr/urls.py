"""HR & Payroll URL Configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccountantProfileView,
    AccountantProfileViewSet,
    ApplicantViewSet,
    BenefitPlanViewSet,
    CertificationViewSet,
    DataRetentionPolicyViewSet,
    DepartmentViewSet,
    EmployeeBenefitViewSet,
    EmployeeDocumentViewSet,
    EmployeeProfileUpdateViewSet,
    EmployeeSalaryViewSet,
    EmployeeViewSet,
    HRAuditLogViewSet,
    HRDashboardMetricsViewSet,
    HRDashboardViewSet,
    InterviewScheduleViewSet,
    JobPostingViewSet,
    LeaveBalanceHRViewSet,
    LeaveRequestViewSet,
    OnboardingChecklistViewSet,
    OnboardingProgressViewSet,
    OnboardingTaskViewSet,
    OvertimeRequestViewSet,
    PayslipViewLogViewSet,
    PayslipViewSet,
    PeerFeedbackViewSet,
    PerformanceGoalViewSet,
    PerformanceReviewCycleViewSet,
    PerformanceReviewViewSet,
    PolicyAcknowledgmentViewSet,
    PolicyDocumentViewSet,
    SalaryReportViewSet,
    SalaryStructureViewSet,
    TimeEntryViewSet,
    TimesheetViewSet,
    TrainingEnrollmentViewSet,
    TrainingProgramViewSet,
    TurnoverReportViewSet,
)

app_name = "hr_v1"

router = DefaultRouter()
# Core HR
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"salary-structures", SalaryStructureViewSet, basename="salary-structure")
router.register(r"employee-salaries", EmployeeSalaryViewSet, basename="employee-salary")
router.register(r"payslips", PayslipViewSet, basename="payslip")
router.register(r"leave-requests", LeaveRequestViewSet, basename="leave-request")
# P1: Performance
router.register(r"review-cycles", PerformanceReviewCycleViewSet, basename="review-cycle")
router.register(r"performance-goals", PerformanceGoalViewSet, basename="performance-goal")
router.register(r"performance-reviews", PerformanceReviewViewSet, basename="performance-review")
router.register(r"peer-feedbacks", PeerFeedbackViewSet, basename="peer-feedback")
# P2: Recruitment
router.register(r"job-postings", JobPostingViewSet, basename="job-posting")
router.register(r"applicants", ApplicantViewSet, basename="applicant")
router.register(r"interviews", InterviewScheduleViewSet, basename="interview")
# P3: Time
router.register(r"time-entries", TimeEntryViewSet, basename="time-entry")
router.register(r"timesheets", TimesheetViewSet, basename="timesheet")
router.register(r"overtime-requests", OvertimeRequestViewSet, basename="overtime-request")
# P4: Benefits
router.register(r"benefit-plans", BenefitPlanViewSet, basename="benefit-plan")
router.register(r"employee-benefits", EmployeeBenefitViewSet, basename="employee-benefit")
# P5: Training
router.register(r"training-programs", TrainingProgramViewSet, basename="training-program")
router.register(r"training-enrollments", TrainingEnrollmentViewSet, basename="training-enrollment")
router.register(r"certifications", CertificationViewSet, basename="certification")
# P6: Self-Service
router.register(r"profile-updates", EmployeeProfileUpdateViewSet, basename="profile-update")
router.register(r"hr-leave-balances", LeaveBalanceHRViewSet, basename="hr-leave-balance")
# P7: Analytics
router.register(r"hr-dashboard", HRDashboardViewSet, basename="hr-dashboard")
router.register(r"turnover-reports", TurnoverReportViewSet, basename="turnover-report")
router.register(r"salary-reports", SalaryReportViewSet, basename="salary-report")
# P8: Documents
router.register(r"employee-documents", EmployeeDocumentViewSet, basename="employee-document")
router.register(r"policies", PolicyDocumentViewSet, basename="policy")
router.register(r"policy-acknowledgments", PolicyAcknowledgmentViewSet, basename="policy-acknowledgment")
# P9: Compliance
router.register(r"audit-logs", HRAuditLogViewSet, basename="audit-log")
# P10: Expanded HR
router.register(r"accountant-profiles", AccountantProfileViewSet, basename="accountant-profile")
router.register(r"data-retention-policies", DataRetentionPolicyViewSet, basename="data-retention-policy")
router.register(r"hr-dashboard-metrics", HRDashboardMetricsViewSet, basename="hr-dashboard-metrics")
router.register(r"onboarding-checklists", OnboardingChecklistViewSet, basename="onboarding-checklist")
router.register(r"onboarding-progress", OnboardingProgressViewSet, basename="onboarding-progress")
router.register(r"onboarding-tasks", OnboardingTaskViewSet, basename="onboarding-task")
router.register(r"payslip-view-logs", PayslipViewLogViewSet, basename="payslip-view-log")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", AccountantProfileView.as_view(), name="accountant_profile"),
]
