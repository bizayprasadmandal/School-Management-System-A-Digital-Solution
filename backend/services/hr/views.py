"""HR & Payroll — Viewsets with school-scoped CRUD and payroll actions."""

import logging
from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Department, Employee, SalaryStructure, EmployeeSalary, Payslip, LeaveRequest
from .serializers import (
    DepartmentSerializer, EmployeeSerializer, SalaryStructureSerializer,
    EmployeeSalarySerializer, PayslipSerializer, LeaveRequestSerializer,
)
from core.permissions import IsSchoolAdmin, IsSchoolMember
from core.pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "code"]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return Department.objects.filter(school=self.request.user.school).prefetch_related("employees")

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
    search_fields = ["user__full_name", "employee_id", "designation", "user__email"]
    filterset_fields = ["department", "status", "employment_type"]
    ordering_fields = ["joining_date", "employee_id"]
    ordering = ["employee_id"]

    def get_queryset(self):
        return Employee.objects.filter(
            school=self.request.user.school
        ).select_related("user", "department").prefetch_related("salaries")

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


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSalarySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "is_active"]

    def get_queryset(self):
        return EmployeeSalary.objects.filter(
            employee__school=self.request.user.school
        ).select_related("employee__user", "structure")

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
        return Payslip.objects.filter(
            school=self.request.user.school
        ).select_related("employee__user", "employee__department")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
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
    search_fields = ["employee__user__full_name", "reason"]
    filterset_fields = ["employee", "leave_type", "status"]

    def get_queryset(self):
        return LeaveRequest.objects.filter(
            school=self.request.user.school
        ).select_related("employee__user", "reviewed_by")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
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
