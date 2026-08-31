"""HR & Payroll serializers."""

from rest_framework import serializers

from .models import (
    AccountantProfile,
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


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "code",
            "description",
            "head",
            "head_name",
            "is_active",
            "employee_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    head_name = serializers.CharField(source="head.full_name", read_only=True, default=None)

    def get_employee_count(self, obj):
        return getattr(obj, "employee_count", obj.employees.count())


class EmployeeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.EmailField(required=False)
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    current_salary = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "employee_id",
            "department",
            "department_name",
            "designation",
            "employment_type",
            "status",
            "joining_date",
            "exit_date",
            "phone",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "bank_name",
            "bank_account_number",
            "bank_routing_number",
            "current_salary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "user": {"required": False},
        }

    def validate_department(self, value):
        if not value:
            return None
        return value

    def validate_user_email(self, value):
        if value:
            from services.auth.models import User

            if not User.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError(f"No user found with email '{value}'. Create the user first.")
        return value

    def get_current_salary(self, obj):
        salary = obj.salaries.filter(is_active=True).order_by("-effective_from").first()
        if salary is None:
            return None
        return EmployeeSalarySerializer(salary).data

    def create(self, validated_data):
        user_email = validated_data.pop("user_email", None)
        if user_email:
            from services.auth.models import User

            user = User.objects.filter(email__iexact=user_email).first()
            validated_data["user"] = user
        return super().create(validated_data)


class SalaryStructureSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    net_salary = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SalaryStructure
        fields = [
            "id",
            "name",
            "designation",
            "department",
            "department_name",
            "basic_salary",
            "housing_allowance",
            "transport_allowance",
            "medical_allowance",
            "other_allowances",
            "tax_deduction",
            "pension_deduction",
            "other_deductions",
            "total_earnings",
            "total_deductions",
            "net_salary",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_department(self, value):
        if not value:
            return None
        return value


class EmployeeSalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    structure_name = serializers.CharField(source="structure.name", read_only=True, default=None)

    class Meta:
        model = EmployeeSalary
        fields = [
            "id",
            "employee",
            "employee_name",
            "structure",
            "structure_name",
            "basic_salary",
            "housing_allowance",
            "transport_allowance",
            "medical_allowance",
            "other_allowances",
            "tax_deduction",
            "pension_deduction",
            "other_deductions",
            "effective_from",
            "effective_to",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    employee_id_number = serializers.CharField(source="employee.employee_id", read_only=True)
    department_name = serializers.CharField(source="employee.department.name", read_only=True, default=None)

    class Meta:
        model = Payslip
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_id_number",
            "department_name",
            "period_start",
            "period_end",
            "basic_salary",
            "housing_allowance",
            "transport_allowance",
            "medical_allowance",
            "other_allowances",
            "tax_deduction",
            "pension_deduction",
            "other_deductions",
            "gross_pay",
            "total_deductions",
            "net_pay",
            "status",
            "payment_date",
            "payment_method",
            "notes",
            "generated_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AccountantProfileSerializer(serializers.ModelSerializer):
    """Full accountant profile — for admin view."""

    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = AccountantProfile
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AccountantSelfProfileSerializer(serializers.ModelSerializer):
    """Limited fields that accountants can edit themselves."""

    class Meta:
        model = AccountantProfile
        fields = ["qualification", "specialization", "experience_years", "certifications", "bio"]


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    employee_id_number = serializers.CharField(source="employee.employee_id", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_id_number",
            "leave_type",
            "from_date",
            "to_date",
            "total_days",
            "reason",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "review_notes",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "reviewed_at"]


# ---------------------------------------------------------------------------
# P1: Performance Management Serializers
# ---------------------------------------------------------------------------


class PerformanceReviewCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReviewCycle
        fields = [
            "id",
            "school",
            "name",
            "description",
            "start_date",
            "end_date",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PerformanceGoalSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    cycle_name = serializers.CharField(source="cycle.name", read_only=True)

    class Meta:
        model = PerformanceGoal
        fields = [
            "id",
            "employee",
            "employee_name",
            "cycle",
            "cycle_name",
            "title",
            "description",
            "category",
            "priority",
            "status",
            "target_value",
            "current_value",
            "unit",
            "progress_pct",
            "start_date",
            "target_date",
            "completed_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PerformanceReviewSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    cycle_name = serializers.CharField(source="cycle.name", read_only=True)
    reviewer_name = serializers.CharField(source="reviewer.full_name", read_only=True, default=None)
    rating_display = serializers.CharField(read_only=True)
    goals = PerformanceGoalSerializer(many=True, read_only=True)

    class Meta:
        model = PerformanceReview
        fields = [
            "id",
            "employee",
            "employee_name",
            "cycle",
            "cycle_name",
            "reviewer",
            "reviewer_name",
            "status",
            "overall_rating",
            "rating_display",
            "strengths",
            "areas_for_improvement",
            "goals_summary",
            "development_plan",
            "self_comments",
            "manager_comments",
            "hr_comments",
            "next_review_date",
            "promotion_recommended",
            "salary_revision_pct",
            "goals",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PeerFeedbackSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.full_name", read_only=True)
    employee_name = serializers.CharField(source="review.employee.user.full_name", read_only=True)

    class Meta:
        model = PeerFeedback
        fields = [
            "id",
            "review",
            "employee_name",
            "reviewer",
            "reviewer_name",
            "feedback_type",
            "strengths",
            "improvements",
            "collaboration_score",
            "communication_score",
            "overall_score",
            "comments",
            "is_anonymous",
            "submitted_at",
        ]
        read_only_fields = ["id", "submitted_at"]


# ---------------------------------------------------------------------------
# P2: Recruitment & Onboarding Serializers
# ---------------------------------------------------------------------------


class JobPostingSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    applicant_count = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = [
            "id",
            "school",
            "department",
            "department_name",
            "title",
            "description",
            "requirements",
            "responsibilities",
            "employment_type",
            "designation",
            "salary_range_min",
            "salary_range_max",
            "location",
            "positions_count",
            "status",
            "posted_date",
            "closing_date",
            "posted_by",
            "applicant_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_applicant_count(self, obj):
        return obj.applicants.count()


class ApplicantSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job_posting.title", read_only=True)
    full_name = serializers.CharField(read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)

    class Meta:
        model = Applicant
        fields = [
            "id",
            "job_posting",
            "job_title",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "resume_url",
            "cover_letter",
            "status",
            "source",
            "notes",
            "rejection_reason",
            "reviewed_by",
            "reviewed_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InterviewScheduleSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    interviewer_name = serializers.CharField(source="interviewer.full_name", read_only=True)

    class Meta:
        model = InterviewSchedule
        fields = [
            "id",
            "applicant",
            "applicant_name",
            "interviewer",
            "interviewer_name",
            "interview_type",
            "scheduled_date",
            "scheduled_time",
            "duration_minutes",
            "location",
            "status",
            "rating",
            "feedback",
            "recommendation",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_applicant_name(self, obj):
        return obj.applicant.full_name


class OnboardingChecklistSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)

    class Meta:
        model = OnboardingChecklist
        fields = [
            "id",
            "school",
            "name",
            "description",
            "department",
            "department_name",
            "is_active",
            "task_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_task_count(self, obj):
        return obj.tasks.count()


class OnboardingTaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default=None)

    class Meta:
        model = OnboardingTask
        fields = [
            "id",
            "checklist",
            "title",
            "description",
            "assigned_to",
            "assigned_to_name",
            "order",
            "due_days_after_joining",
            "is_mandatory",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class OnboardingProgressSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = OnboardingProgress
        fields = [
            "id",
            "employee",
            "employee_name",
            "task",
            "task_title",
            "status",
            "completed_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ---------------------------------------------------------------------------
# P3: Time & Attendance Serializers
# ---------------------------------------------------------------------------


class TimeEntrySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = TimeEntry
        fields = [
            "id",
            "employee",
            "employee_name",
            "date",
            "clock_in",
            "clock_out",
            "break_minutes",
            "total_hours",
            "overtime_hours",
            "status",
            "approved_by",
            "approved_by_name",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimesheetSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = Timesheet
        fields = [
            "id",
            "employee",
            "employee_name",
            "week_start",
            "week_end",
            "total_hours",
            "total_overtime",
            "status",
            "submitted_at",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OvertimeRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)

    class Meta:
        model = OvertimeRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "date",
            "hours",
            "reason",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "review_notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# ---------------------------------------------------------------------------
# P4: Benefits Management Serializers
# ---------------------------------------------------------------------------


class BenefitPlanSerializer(serializers.ModelSerializer):
    total_contribution = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = BenefitPlan
        fields = [
            "id",
            "school",
            "name",
            "benefit_type",
            "description",
            "provider",
            "employee_contribution",
            "employer_contribution",
            "total_contribution",
            "is_active",
            "enrollment_start",
            "enrollment_end",
            "enrollment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_enrollment_count(self, obj):
        return obj.enrollments.filter(status="enrolled").count()


class EmployeeBenefitSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    plan_type = serializers.CharField(source="plan.benefit_type", read_only=True)

    class Meta:
        model = EmployeeBenefit
        fields = [
            "id",
            "employee",
            "employee_name",
            "plan",
            "plan_name",
            "plan_type",
            "status",
            "enrollment_date",
            "effective_from",
            "effective_to",
            "dependents_count",
            "employee_contribution",
            "employer_contribution",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ---------------------------------------------------------------------------
# P5: Training & Development Serializers
# ---------------------------------------------------------------------------


class TrainingProgramSerializer(serializers.ModelSerializer):
    enrollment_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = TrainingProgram
        fields = [
            "id",
            "school",
            "name",
            "description",
            "training_type",
            "provider",
            "instructor",
            "start_date",
            "end_date",
            "duration_hours",
            "max_participants",
            "cost_per_participant",
            "status",
            "location",
            "is_mandatory",
            "created_by",
            "created_by_name",
            "enrollment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TrainingEnrollmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    program_name = serializers.CharField(source="program.name", read_only=True)

    class Meta:
        model = TrainingEnrollment
        fields = [
            "id",
            "program",
            "program_name",
            "employee",
            "employee_name",
            "status",
            "enrolled_date",
            "completed_date",
            "score",
            "certificate_url",
            "hours_attended",
            "feedback",
            "rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "enrolled_date", "created_at", "updated_at"]


class CertificationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)

    class Meta:
        model = Certification
        fields = [
            "id",
            "employee",
            "employee_name",
            "name",
            "issuing_organization",
            "credential_id",
            "issue_date",
            "expiry_date",
            "status",
            "document_url",
            "notes",
            "is_expired",
            "days_until_expiry",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
