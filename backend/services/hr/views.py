"""HR & Payroll — Viewsets with school-scoped CRUD and payroll actions."""

import logging

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
from .serializers import (
    ApplicantSerializer,
    BenefitPlanSerializer,
    CertificationSerializer,
    DepartmentSerializer,
    EmployeeBenefitSerializer,
    EmployeeSalarySerializer,
    EmployeeSerializer,
    InterviewScheduleSerializer,
    JobPostingSerializer,
    LeaveRequestSerializer,
    OvertimeRequestSerializer,
    PayslipSerializer,
    PeerFeedbackSerializer,
    PerformanceGoalSerializer,
    PerformanceReviewCycleSerializer,
    PerformanceReviewSerializer,
    SalaryStructureSerializer,
    TimeEntrySerializer,
    TimesheetSerializer,
    TrainingEnrollmentSerializer,
    TrainingProgramSerializer,
)

logger = logging.getLogger(__name__)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "code"]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return Department.objects.filter(school=self.request.user.school).annotate(employee_count=Count("employees"))

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "employee_id",
        "designation",
        "user__email",
    ]
    filterset_fields = ["department", "status", "employment_type"]
    ordering_fields = ["joining_date", "employee_id"]
    ordering = ["employee_id"]

    def get_queryset(self):
        return (
            Employee.objects.filter(school=self.request.user.school)
            .select_related("user", "department")
            .prefetch_related("salaries")
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SalaryStructureViewSet(viewsets.ModelViewSet):
    serializer_class = SalaryStructureSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "designation"]
    filterset_fields = ["department", "is_active"]

    def get_queryset(self):
        return SalaryStructure.objects.filter(school=self.request.user.school).select_related("department")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AccountantProfileView(generics.RetrieveUpdateAPIView):
    """Get/update the authenticated accountant's own profile."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            from .serializers import AccountantSelfProfileSerializer

            return AccountantSelfProfileSerializer
        from .serializers import AccountantProfileSerializer

        return AccountantProfileSerializer

    def get_object(self):
        from .models import AccountantProfile

        profile, _ = AccountantProfile.objects.get_or_create(
            user=self.request.user,
            school=self.request.user.school,
        )
        return profile


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSalarySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "is_active"]

    def get_queryset(self):
        return EmployeeSalary.objects.filter(employee__school=self.request.user.school).select_related(
            "employee__user", "structure"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="generate-payslip")
    def generate_payslip(self, request, pk=None):
        """Generate a payslip from an employee's current salary for a given period."""
        emp_salary = self.get_object()
        employee = emp_salary.employee
        period_start = request.data.get("period_start")
        period_end = request.data.get("period_end")
        if not period_start or not period_end:
            return Response({"error": "period_start and period_end are required"}, status=400)

        from django.db import transaction

        with transaction.atomic():
            payslip, created = Payslip.objects.get_or_create(
                school=employee.school,
                employee=employee,
                period_start=period_start,
                period_end=period_end,
                defaults={
                    "basic_salary": emp_salary.basic_salary,
                    "housing_allowance": emp_salary.housing_allowance,
                    "transport_allowance": emp_salary.transport_allowance,
                    "medical_allowance": emp_salary.medical_allowance,
                    "other_allowances": emp_salary.other_allowances,
                    "tax_deduction": emp_salary.tax_deduction,
                    "pension_deduction": emp_salary.pension_deduction,
                    "other_deductions": emp_salary.other_deductions,
                    "gross_pay": emp_salary.total_earnings,
                    "total_deductions": emp_salary.total_deductions,
                    "net_pay": emp_salary.net_salary,
                    "generated_by": request.user,
                },
            )
        return Response(PayslipSerializer(payslip).data, status=201 if created else 200)


class PayslipViewSet(viewsets.ModelViewSet):
    serializer_class = PayslipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["employee", "status", "payment_date"]
    ordering = ["-period_start"]

    def get_queryset(self):
        return Payslip.objects.filter(school=self.request.user.school).select_related(
            "employee__user", "employee__department"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "approve", "mark_paid"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """Approve a draft payslip for payment."""
        payslip = self.get_object()
        if payslip.status != Payslip.Status.DRAFT:
            return Response({"detail": "Only draft payslips can be approved."}, status=400)
        payslip.status = Payslip.Status.APPROVED
        payslip.save(update_fields=["status"])
        return Response(PayslipSerializer(payslip).data)

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        """Mark an approved payslip as paid."""
        payslip = self.get_object()
        if payslip.status != Payslip.Status.APPROVED:
            return Response({"detail": "Only approved payslips can be marked paid."}, status=400)
        payslip.status = Payslip.Status.PAID
        payslip.payment_date = request.data.get("payment_date", timezone.now().date())
        payslip.payment_method = request.data.get("payment_method", "")
        payslip.save(update_fields=["status", "payment_date", "payment_method"])
        return Response(PayslipSerializer(payslip).data)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["employee__user__first_name", "employee__user__last_name", "reason"]
    filterset_fields = ["employee", "leave_type", "status"]

    def get_queryset(self):
        return LeaveRequest.objects.filter(school=self.request.user.school).select_related(
            "employee__user", "reviewed_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "approve", "reject"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        leave = self.get_object()
        if leave.status != LeaveRequest.Status.PENDING:
            return Response({"detail": "Only pending requests can be approved."}, status=400)
        leave.status = LeaveRequest.Status.APPROVED
        leave.reviewed_by = request.user
        leave.review_notes = request.data.get("review_notes", "")
        leave.reviewed_at = timezone.now()
        leave.save()
        return Response(LeaveRequestSerializer(leave).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        leave = self.get_object()
        if leave.status != LeaveRequest.Status.PENDING:
            return Response({"detail": "Only pending requests can be rejected."}, status=400)
        leave.status = LeaveRequest.Status.REJECTED
        leave.reviewed_by = request.user
        leave.review_notes = request.data.get("review_notes", "")
        leave.reviewed_at = timezone.now()
        leave.save()
        return Response(LeaveRequestSerializer(leave).data)


# ---------------------------------------------------------------------------
# P1: Performance Management ViewSets
# ---------------------------------------------------------------------------


class PerformanceReviewCycleViewSet(viewsets.ModelViewSet):
    serializer_class = PerformanceReviewCycleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["name"]

    def get_queryset(self):
        return PerformanceReviewCycle.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class PerformanceGoalViewSet(viewsets.ModelViewSet):
    serializer_class = PerformanceGoalSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["employee", "cycle", "status", "priority"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return PerformanceGoal.objects.filter(employee__school=self.request.user.school).select_related(
            "employee__user", "cycle"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=False, methods=["get"], url_path="my-goals")
    def my_goals(self, request):
        if request.user.role != "employee":
            return Response({"detail": "Employee only."}, status=403)
        qs = self.get_queryset().filter(employee__user=request.user)
        return Response(PerformanceGoalSerializer(qs, many=True).data)


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    serializer_class = PerformanceReviewSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["employee", "cycle", "status", "overall_rating"]
    search_fields = ["employee__user__first_name", "employee__user__last_name"]

    def get_queryset(self):
        return (
            PerformanceReview.objects.filter(employee__school=self.request.user.school)
            .select_related("employee__user", "cycle", "reviewer")
            .prefetch_related("goals")
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="submit-self-review")
    def submit_self_review(self, request, pk=None):
        review = self.get_object()
        review.self_comments = request.data.get("self_comments", "")
        review.status = PerformanceReview.Status.MANAGER_REVIEW
        review.save(update_fields=["self_comments", "status", "updated_at"])
        return Response(PerformanceReviewSerializer(review).data)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        review = self.get_object()
        review.overall_rating = request.data.get("overall_rating", review.overall_rating)
        review.strengths = request.data.get("strengths", review.strengths)
        review.areas_for_improvement = request.data.get("areas_for_improvement", review.areas_for_improvement)
        review.development_plan = request.data.get("development_plan", review.development_plan)
        review.status = PerformanceReview.Status.COMPLETED
        review.save()
        return Response(PerformanceReviewSerializer(review).data)


class PeerFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = PeerFeedbackSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["review", "feedback_type"]

    def get_queryset(self):
        return PeerFeedback.objects.filter(review__employee__school=self.request.user.school).select_related(
            "review__employee__user", "reviewer"
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


# ---------------------------------------------------------------------------
# P2: Recruitment ViewSets
# ---------------------------------------------------------------------------


class JobPostingViewSet(viewsets.ModelViewSet):
    serializer_class = JobPostingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["department", "status", "employment_type"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return JobPosting.objects.filter(school=self.request.user.school).select_related("department")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, posted_by=self.request.user)


class ApplicantViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicantSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["job_posting", "status"]
    search_fields = ["first_name", "last_name", "email"]

    def get_queryset(self):
        return Applicant.objects.filter(job_posting__school=self.request.user.school).select_related(
            "job_posting", "reviewed_by"
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["post"], url_path="advance-status")
    def advance_status(self, request, pk=None):
        applicant = self.get_object()
        transitions = {
            "new": "screening",
            "screening": "interview",
            "interview": "offer",
            "offer": "hired",
        }
        next_status = transitions.get(applicant.status)
        if not next_status:
            return Response({"detail": f"Cannot advance from {applicant.status}"}, status=400)
        applicant.status = next_status
        applicant.reviewed_by = request.user
        applicant.save(update_fields=["status", "reviewed_by", "updated_at"])
        return Response(ApplicantSerializer(applicant).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        applicant = self.get_object()
        applicant.status = "rejected"
        applicant.rejection_reason = request.data.get("reason", "")
        applicant.reviewed_by = request.user
        applicant.save(update_fields=["status", "rejection_reason", "reviewed_by", "updated_at"])
        return Response(ApplicantSerializer(applicant).data)


class InterviewScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["applicant", "interviewer", "status"]

    def get_queryset(self):
        return InterviewSchedule.objects.filter(applicant__job_posting__school=self.request.user.school).select_related(
            "applicant", "interviewer"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# ---------------------------------------------------------------------------
# P3: Time Tracking ViewSets
# ---------------------------------------------------------------------------


class TimeEntryViewSet(viewsets.ModelViewSet):
    serializer_class = TimeEntrySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["employee", "date", "status"]
    ordering_fields = ["date"]
    ordering = ["-date"]

    def get_queryset(self):
        user = self.request.user
        qs = TimeEntry.objects.filter(employee__school=user.school).select_related("employee__user", "approved_by")
        if user.role == "employee":
            qs = qs.filter(employee__user=user)
        return qs

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        if self.action in ["update", "partial_update", "destroy", "approve"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        entry = self.get_object()
        entry.status = "approved"
        entry.approved_by = request.user
        entry.save(update_fields=["status", "approved_by", "updated_at"])
        return Response(TimeEntrySerializer(entry).data)


class TimesheetViewSet(viewsets.ModelViewSet):
    serializer_class = TimesheetSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "status"]

    def get_queryset(self):
        user = self.request.user
        qs = Timesheet.objects.filter(employee__school=user.school).select_related("employee__user", "approved_by")
        if user.role == "employee":
            qs = qs.filter(employee__user=user)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["post"], url_path="submit")
    def submit_timesheet(self, request, pk=None):
        ts = self.get_object()
        ts.status = "submitted"
        ts.submitted_at = timezone.now()
        ts.save(update_fields=["status", "submitted_at"])
        return Response(TimesheetSerializer(ts).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        ts = self.get_timesheet()
        ts.status = "approved"
        ts.approved_by = request.user
        ts.approved_at = timezone.now()
        ts.save(update_fields=["status", "approved_by", "approved_at"])
        return Response(TimesheetSerializer(ts).data)


class OvertimeRequestViewSet(viewsets.ModelViewSet):
    serializer_class = OvertimeRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "status"]

    def get_queryset(self):
        user = self.request.user
        qs = OvertimeRequest.objects.filter(employee__school=user.school).select_related(
            "employee__user", "reviewed_by"
        )
        if user.role == "employee":
            qs = qs.filter(employee__user=user)
        return qs

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        if self.action in ["update", "partial_update", "destroy", "approve", "reject"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        ot = self.get_object()
        ot.status = "approved"
        ot.reviewed_by = request.user
        ot.save(update_fields=["status", "reviewed_by"])
        return Response(OvertimeRequestSerializer(ot).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        ot = self.get_object()
        ot.status = "rejected"
        ot.reviewed_by = request.user
        ot.review_notes = request.data.get("review_notes", "")
        ot.save(update_fields=["status", "reviewed_by", "review_notes"])
        return Response(OvertimeRequestSerializer(ot).data)


# ---------------------------------------------------------------------------
# P4: Benefits ViewSets
# ---------------------------------------------------------------------------


class BenefitPlanViewSet(viewsets.ModelViewSet):
    serializer_class = BenefitPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["benefit_type", "is_active"]
    search_fields = ["name", "provider"]

    def get_queryset(self):
        return BenefitPlan.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class EmployeeBenefitViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeBenefitSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "plan", "status"]

    def get_queryset(self):
        return EmployeeBenefit.objects.filter(employee__school=self.request.user.school).select_related(
            "employee__user", "plan"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="enroll")
    def enroll(self, request, pk=None):
        benefit = self.get_object()
        benefit.status = "enrolled"
        benefit.save(update_fields=["status", "updated_at"])
        return Response(EmployeeBenefitSerializer(benefit).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        benefit = self.get_object()
        benefit.status = "cancelled"
        benefit.save(update_fields=["status", "updated_at"])
        return Response(EmployeeBenefitSerializer(benefit).data)

    @action(detail=False, methods=["get"], url_path="my-benefits")
    def my_benefits(self, request):
        if request.user.role != "employee":
            return Response({"detail": "Employee only."}, status=403)
        qs = self.get_queryset().filter(employee__user=request.user, status="enrolled")
        return Response(EmployeeBenefitSerializer(qs, many=True).data)


# ---------------------------------------------------------------------------
# P5: Training ViewSets
# ---------------------------------------------------------------------------


class TrainingProgramViewSet(viewsets.ModelViewSet):
    serializer_class = TrainingProgramSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["training_type", "status", "is_mandatory"]
    search_fields = ["name", "description", "instructor"]

    def get_queryset(self):
        from django.db.models import Count

        return (
            TrainingProgram.objects.filter(school=self.request.user.school)
            .select_related("created_by")
            .annotate(enrollment_count=Count("enrollments"))
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class TrainingEnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = TrainingEnrollmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["program", "employee", "status"]

    def get_queryset(self):
        return TrainingEnrollment.objects.filter(program__school=self.request.user.school).select_related(
            "employee__user", "program"
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        enrollment = self.get_object()
        enrollment.status = "completed"
        enrollment.completed_date = timezone.now().date()
        enrollment.score = request.data.get("score", enrollment.score)
        enrollment.feedback = request.data.get("feedback", "")
        enrollment.save(update_fields=["status", "completed_date", "score", "feedback", "updated_at"])
        return Response(TrainingEnrollmentSerializer(enrollment).data)

    @action(detail=False, methods=["get"], url_path="my-trainings")
    def my_trainings(self, request):
        if request.user.role != "employee":
            return Response({"detail": "Employee only."}, status=403)
        qs = self.get_queryset().filter(employee__user=request.user)
        return Response(TrainingEnrollmentSerializer(qs, many=True).data)


class CertificationViewSet(viewsets.ModelViewSet):
    serializer_class = CertificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["employee", "status"]
    search_fields = ["name", "issuing_organization"]

    def get_queryset(self):
        user = self.request.user
        qs = Certification.objects.filter(employee__school=user.school).select_related("employee__user")
        if user.role == "employee":
            qs = qs.filter(employee__user=user)
        return qs

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], url_path="expiring")
    def expiring(self, request):
        from datetime import timedelta

        threshold = timezone.now().date() + timedelta(days=30)
        qs = self.get_queryset().filter(
            expiry_date__lte=threshold,
            expiry_date__gte=timezone.now().date(),
            status="active",
        )
        return Response(CertificationSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="my-certifications")
    def my_certifications(self, request):
        if request.user.role != "employee":
            return Response({"detail": "Employee only."}, status=403)
        qs = self.get_queryset().filter(employee__user=request.user)
        return Response(CertificationSerializer(qs, many=True).data)
