"""HR & Payroll — Django Admin registrations."""

from django.contrib import admin
from .models import Department, Employee, SalaryStructure, EmployeeSalary, Payslip, LeaveRequest


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
