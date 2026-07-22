"""HR & Payroll serializers."""

from rest_framework import serializers
from .models import Department, Employee, SalaryStructure, EmployeeSalary, Payslip, LeaveRequest, AccountantProfile
from services.auth.models import User


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id", "name", "code", "description", "head", "head_name",
            "is_active", "employee_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    head_name = serializers.CharField(source="head.full_name", read_only=True, default=None)

    def get_employee_count(self, obj):
        return obj.employees.count()


class EmployeeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.EmailField(required=False)
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    current_salary = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id", "user", "user_name", "user_email", "employee_id", "department",
            "department_name", "designation", "employment_type", "status",
            "joining_date", "exit_date", "phone", "address",
            "emergency_contact_name", "emergency_contact_phone",
            "bank_name", "bank_account_number", "bank_routing_number",
            "current_salary", "created_at", "updated_at",
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
            "id", "name", "designation", "department", "department_name",
            "basic_salary", "housing_allowance", "transport_allowance",
            "medical_allowance", "other_allowances",
            "tax_deduction", "pension_deduction", "other_deductions",
            "total_earnings", "total_deductions", "net_salary",
            "is_active", "created_at",
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
            "id", "employee", "employee_name", "structure", "structure_name",
            "basic_salary", "housing_allowance", "transport_allowance",
            "medical_allowance", "other_allowances",
            "tax_deduction", "pension_deduction", "other_deductions",
            "effective_from", "effective_to", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)
    employee_id_number = serializers.CharField(source="employee.employee_id", read_only=True)
    department_name = serializers.CharField(source="employee.department.name", read_only=True, default=None)

    class Meta:
        model = Payslip
        fields = [
            "id", "employee", "employee_name", "employee_id_number", "department_name",
            "period_start", "period_end",
            "basic_salary", "housing_allowance", "transport_allowance",
            "medical_allowance", "other_allowances",
            "tax_deduction", "pension_deduction", "other_deductions",
            "gross_pay", "total_deductions", "net_pay",
            "status", "payment_date", "payment_method", "notes",
            "generated_by", "created_at",
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
            "id", "employee", "employee_name", "employee_id_number",
            "leave_type", "from_date", "to_date", "total_days",
            "reason", "status", "reviewed_by", "reviewed_by_name",
            "review_notes", "reviewed_at", "created_at",
        ]
        read_only_fields = ["id", "created_at", "reviewed_at"]
