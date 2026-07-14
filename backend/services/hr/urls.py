"""HR & Payroll URL Configuration."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, EmployeeViewSet, SalaryStructureViewSet,
    EmployeeSalaryViewSet, PayslipViewSet, LeaveRequestViewSet,
)

app_name = "hr_v1"

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"salary-structures", SalaryStructureViewSet, basename="salary-structure")
router.register(r"employee-salaries", EmployeeSalaryViewSet, basename="employee-salary")
router.register(r"payslips", PayslipViewSet, basename="payslip")
router.register(r"leave-requests", LeaveRequestViewSet, basename="leave-request")

urlpatterns = [
    path("", include(router.urls)),
]
