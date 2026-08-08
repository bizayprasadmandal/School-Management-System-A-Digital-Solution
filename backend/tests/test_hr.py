"""Tests for HR Service — Department, Employee, SalaryStructure, Payslip, LeaveRequest."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

HR_DEPARTMENTS = f"{API_PREFIX}/hr/departments/"
HR_EMPLOYEES = f"{API_PREFIX}/hr/employees/"
HR_SALARY_STRUCTURES = f"{API_PREFIX}/hr/salary-structures/"
HR_EMPLOYEE_SALARIES = f"{API_PREFIX}/hr/employee-salaries/"
HR_PAYSLIPS = f"{API_PREFIX}/hr/payslips/"
HR_LEAVES = f"{API_PREFIX}/hr/leave-requests/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory

    return AdminUserFactory(school=school)


@pytest.fixture
def teacher(db, school):
    from tests.factories import TeacherUserFactory

    return TeacherUserFactory(school=school)


@pytest.fixture
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


@pytest.fixture
def teacher_client(db, teacher):
    c = APIClient()
    c.force_authenticate(user=teacher)
    return c


@pytest.mark.django_db
class TestDepartments:

    def test_admin_can_create_department(self, admin_client, school):
        payload = {"name": "Mathematics", "code": "MATH", "head_name": "Dr. Smith"}
        r = admin_client.post(HR_DEPARTMENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Mathematics"

    def test_list_departments(self, admin_client, school):
        from services.hr.models import Department

        Department.objects.create(school=school, name="Science", code="SCI")
        r = admin_client.get(HR_DEPARTMENTS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_tenant_isolation_department(self, db):
        from services.hr.models import Department
        from tests.factories import AdminUserFactory, SchoolFactory

        school_a = SchoolFactory(code="HRA")
        school_b = SchoolFactory(code="HRB")
        admin_a = AdminUserFactory(school=school_a)
        Department.objects.create(school=school_b, name="Secret Dept", code="SEC")
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(HR_DEPARTMENTS)
        names = [d["name"] for d in r.data["results"]]
        assert "Secret Dept" not in names


@pytest.mark.django_db
class TestEmployees:

    def test_create_employee(self, admin_client, school):
        from services.hr.models import Department
        from tests.factories import UserFactory

        dept = Department.objects.create(school=school, name="Science", code="SCI")
        UserFactory(school=school, email="john.doe@school.edu", role="teacher")
        payload = {
            "department": dept.id,
            "user_email": "john.doe@school.edu",
            "employee_id": "EMP001",
            "designation": "Senior Teacher",
            "employment_type": "full_time",
            "joining_date": date.today().isoformat(),
        }
        r = admin_client.post(HR_EMPLOYEES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["employee_id"] == "EMP001"

    def test_teacher_cannot_create_employee(self, teacher_client):
        payload = {
            "user_email": "jane@school.edu",
            "employee_id": "EMP002",
            "designation": "Teacher",
        }
        r = teacher_client.post(HR_EMPLOYEES, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_employees(self, admin_client, school):
        from services.hr.models import Department, Employee
        from tests.factories import UserFactory

        dept = Department.objects.create(school=school, name="English", code="ENG")
        emp_user = UserFactory(school=school, email="alice@school.edu", role="teacher")
        Employee.objects.create(
            school=school,
            user=emp_user,
            department=dept,
            employee_id="EMP003",
            designation="Teacher",
            joining_date=date.today(),
        )
        r = admin_client.get(HR_EMPLOYEES)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestSalaryStructures:

    def test_create_salary_structure(self, admin_client, school):
        from services.hr.models import Department

        dept = Department.objects.create(school=school, name="Math", code="MATH")
        payload = {
            "name": "Senior Teacher Scale",
            "designation": "Senior Teacher",
            "department": dept.id,
            "basic_salary": "50000.00",
            "housing_allowance": "10000.00",
            "tax_deduction": "5000.00",
        }
        r = admin_client.post(HR_SALARY_STRUCTURES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["basic_salary"] == "50000.00"


@pytest.mark.django_db
class TestPayslips:

    def test_generate_payslip(self, admin_client, school):
        from services.hr.models import Department, Employee, EmployeeSalary
        from tests.factories import UserFactory

        emp_user = UserFactory(school=school, role="teacher", email="carol@school.edu")
        dept = Department.objects.create(school=school, name="Physics", code="PHY")
        emp = Employee.objects.create(
            school=school,
            user=emp_user,
            department=dept,
            employee_id="EMP020",
            designation="Teacher",
            joining_date=date.today(),
        )
        salary = EmployeeSalary.objects.create(
            employee=emp,
            basic_salary=Decimal("60000.00"),
            housing_allowance=Decimal("12000.00"),
            tax_deduction=Decimal("6000.00"),
            effective_from=date.today(),
        )
        payload = {
            "period_start": date.today().replace(day=1).isoformat(),
            "period_end": date.today().isoformat(),
        }
        r = admin_client.post(
            f"{HR_EMPLOYEE_SALARIES}{salary.id}/generate-payslip/",
            payload,
            format="json",
        )
        assert r.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    def test_list_payslips(self, admin_client, school):
        from services.hr.models import Department, Employee, Payslip
        from tests.factories import UserFactory

        emp_user = UserFactory(school=school, role="teacher", email="dan@school.edu")
        dept = Department.objects.create(school=school, name="Chem", code="CHEM")
        emp = Employee.objects.create(
            school=school,
            user=emp_user,
            department=dept,
            employee_id="EMP030",
            designation="Teacher",
            joining_date=date.today(),
        )
        Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today().replace(day=1),
            period_end=date.today(),
            basic_salary=Decimal("50000"),
            gross_pay=Decimal("60000"),
            total_deductions=Decimal("6000"),
            net_pay=Decimal("54000"),
            status="draft",
        )
        r = admin_client.get(HR_PAYSLIPS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestLeaveRequests:

    def test_create_leave_request(self, admin_client, school):
        from services.hr.models import Department, Employee
        from tests.factories import UserFactory

        emp_user = UserFactory(school=school, role="teacher", email="emma@school.edu")
        dept = Department.objects.create(school=school, name="Arts", code="ART")
        emp = Employee.objects.create(
            school=school,
            user=emp_user,
            department=dept,
            employee_id="EMP040",
            designation="Teacher",
            joining_date=date.today(),
        )
        payload = {
            "employee": emp.id,
            "leave_type": "annual",
            "from_date": date.today().isoformat(),
            "to_date": (date.today() + timedelta(days=5)).isoformat(),
            "total_days": 6,
            "reason": "Vacation",
        }
        r = admin_client.post(HR_LEAVES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["status"] == "pending"

    def test_approve_leave(self, admin_client, school):
        from services.hr.models import Department, Employee, LeaveRequest
        from tests.factories import UserFactory

        emp_user = UserFactory(school=school, role="teacher", email="frank@school.edu")
        dept = Department.objects.create(school=school, name="Music", code="MUS")
        emp = Employee.objects.create(
            school=school,
            user=emp_user,
            department=dept,
            employee_id="EMP050",
            designation="Teacher",
            joining_date=date.today(),
        )
        leave = LeaveRequest.objects.create(
            school=school,
            employee=emp,
            leave_type="sick",
            from_date=date.today(),
            to_date=date.today() + timedelta(days=2),
            total_days=3,
            reason="Sick leave",
            status="pending",
        )
        r = admin_client.post(f"{HR_LEAVES}{leave.id}/approve/")
        assert r.status_code == status.HTTP_200_OK
        leave.refresh_from_db()
        assert leave.status == "approved"

    def test_reject_leave(self, admin_client, school):
        from services.hr.models import Department, Employee, LeaveRequest
        from tests.factories import UserFactory

        emp_user = UserFactory(school=school, role="teacher", email="grace@school.edu")
        dept = Department.objects.create(school=school, name="Sports", code="SPO")
        emp = Employee.objects.create(
            school=school,
            user=emp_user,
            department=dept,
            employee_id="EMP060",
            designation="Teacher",
            joining_date=date.today(),
        )
        leave = LeaveRequest.objects.create(
            school=school,
            employee=emp,
            leave_type="personal",
            from_date=date.today(),
            to_date=date.today(),
            total_days=1,
            reason="Personal",
            status="pending",
        )
        r = admin_client.post(f"{HR_LEAVES}{leave.id}/reject/")
        assert r.status_code == status.HTTP_200_OK
        leave.refresh_from_db()
        assert leave.status == "rejected"
