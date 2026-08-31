"""HR & Payroll URL Configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccountantProfileView,
    ApplicantViewSet,
    BenefitPlanViewSet,
    CertificationViewSet,
    DepartmentViewSet,
    EmployeeBenefitViewSet,
    EmployeeSalaryViewSet,
    EmployeeViewSet,
    InterviewScheduleViewSet,
    JobPostingViewSet,
    LeaveRequestViewSet,
    OvertimeRequestViewSet,
    PayslipViewSet,
    PeerFeedbackViewSet,
    PerformanceGoalViewSet,
    PerformanceReviewCycleViewSet,
    PerformanceReviewViewSet,
    SalaryStructureViewSet,
    TimeEntryViewSet,
    TimesheetViewSet,
    TrainingEnrollmentViewSet,
    TrainingProgramViewSet,
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

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", AccountantProfileView.as_view(), name="accountant_profile"),
]
