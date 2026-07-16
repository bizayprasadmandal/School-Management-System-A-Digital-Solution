"""Tests for HR Service — Department, Employee, SalaryStructure, Payslip, LeaveRequest."""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

HR_DEPARTMENTS = f"{API_PREFIX}/hr/departments/"
HR_EMPLOYEES = f"{API_PREFIX}/hr/employees/"
HR_SALARY_STRUCTURES = f"{API_PREFIX}/hr/salary-structures/"
HR_PAYSLIPS = f"{API_PREFIX}/hr/payslips/"
HR_LEAVES = f"{API_PREFIX}/hr/leaves/"


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
        from tests.factories import SchoolFactory, AdminUserFactory
        from services.hr.models import Department
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
        dept = Department.objects.create(school=school, name="Science", code="SCI")
        payload = {
            "department": dept.id,
            "first_name": "John", "last_name": "Doe",
            "email": "john.doe@school.edu",
            "employee_id": "EMP001",
            "designation": "Senior Teacher",
            "employment_type": "permanent",
            "date_of_joining": date.today().isoformat(),
        }
        r = admin_client.post(HR_EMPLOYEES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["employee_id"] == "EMP001"

    def test_teacher_cannot_create_employee(self, teacher_client):
        payload = {
            "first_name": "Jane", "last_name": "Smith",
            "email": "jane@school.edu",
            "employee_id": "EMP002",
        }
        r = teacher_client.post(HR_EMPLOYEES, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_employees(self, admin_client, school):
        from services.hr.models import Department, Employee
        dept = Department.objects.create(school=school, name="English", code="ENG")
        Employee.objects.create(
            school=school, department=dept,
            first_name="Alice", last_name="Brown",
            email="alice@school.edu", employee_id="EMP003",
            designation="Teacher",
        )
        r = admin_client.get(HR_EMPLOYEES)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestSalaryStructures:

    def test_create_salary_structure(self, admin_client, school):
        from tests.factories import UserFactory
        emp_user = UserFactory(school=school, role="teacher")
        from services.hr.models import Department, Employee
        dept = Department.objects.create(school=school, name="Math", code="MATH")
        emp = Employee.objects.create(
            school=school, user=emp_user, department=dept,
            first_name="Bob", last_name="Wilson",
            email="bob@school.edu", employee_id="EMP010",
        )
        payload = {
            "employee": emp.id,
            "basic_salary": "50000.00",
            "allowances": "10000.00",
            "deductions": "5000.00",
            "effective_from": date.today().isoformat(),
        }
        r = admin_client.post(HR_SALARY_STRUCTURES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["basic_salary"] == "50000.00"


@pytest.mark.django_db
class TestPayslips:

    def test_generate_payslip(self, admin_client, school):
        from tests.factories import UserFactory
        from services.hr.models import Department, Employee, SalaryStructure
        emp_user = UserFactory(school=school, role="teacher")
        dept = Department.objects.create(school=school, name="Physics", code="PHY")
        emp = Employee.objects.create(
            school=school, user=emp_user, department=dept,
            first_name="Carol", last_name="Davis",
            email="carol@school.edu", employee_id="EMP020",
        )
        SalaryStructure.objects.create(
            school=school, employee=emp,
            basic_salary=Decimal("60000.00"),
            allowances=Decimal("12000.00"),
            deductions=Decimal("6000.00"),
            effective_from=date.today(),
        )
        payload = {
            "employee": emp.id,
            "month": date.today().month,
            "year": date.today().year,
        }
        r = admin_client.post(f"{HR_PAYSLIPS}generate-payslip/", payload, format="json")
        assert r.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    def test_list_payslips(self, admin_client, school):
        from tests.factories import UserFactory
        from services.hr.models import Department, Employee, Payslip
        emp_user = UserFactory(school=school, role="teacher")
        dept = Department.objects.create(school=school, name="Chem", code="CHEM")
        emp = Employee.objects.create(
            school=school, user=emp_user, department=dept,
            first_name="Dan", last_name="Evans",
            email="dan@school.edu", employee_id="EMP030",
        )
        Payslip.objects.create(
            school=school, employee=emp,
            month=date.today().month, year=date.today().year,
            basic_salary=Decimal("50000"), gross_pay=Decimal("60000"),
            net_pay=Decimal("54000"), status="generated",
        )
        r = admin_client.get(HR_PAYSLIPS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestLeaveRequests:

    def test_create_leave_request(self, admin_client, school):
        from tests.factories import UserFactory
        from services.hr.models import Department, Employee
        emp_user = UserFactory(school=school, role="teacher")
        dept = Department.objects.create(school=school, name="Arts", code="ART")
        emp = Employee.objects.create(
            school=school, user=emp_user, department=dept,
            first_name="Emma", last_name="Fox",
            email="emma@school.edu", employee_id="EMP040",
        )
        payload = {
            "employee": emp.id,
            "leave_type": "annual",
            "from_date": date.today().isoformat(),
            "to_date": (date.today() + timedelta(days=5)).isoformat(),
            "reason": "Vacation",
        }
        r = admin_client.post(HR_LEAVES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["status"] == "pending"

    def test_approve_leave(self, admin_client, school):
        from tests.factories import UserFactory
        from services.hr.models import Department, Employee, LeaveRequest
        emp_user = UserFactory(school=school, role="teacher")
        dept = Department.objects.create(school=school, name="Music", code="MUS")
        emp = Employee.objects.create(
            school=school, user=emp_user, department=dept,
            first_name="Frank", last_name="Green",
            email="frank@school.edu", employee_id="EMP050",
        )
        leave = LeaveRequest.objects.create(
            school=school, employee=emp,
            leave_type="sick", from_date=date.today(),
            to_date=date.today() + timedelta(days=2),
            reason="Sick leave", status="pending",
        )
        r = admin_client.post(f"{HR_LEAVES}{leave.id}/approve/")
        assert r.status_code == status.HTTP_200_OK
        leave.refresh_from_db()
        assert leave.status == "approved"

    def test_reject_leave(self, admin_client, school):
        from tests.factories import UserFactory
        from services.hr.models import Department, Employee, LeaveRequest
        emp_user = UserFactory(school=school, role="teacher")
        dept = Department.objects.create(school=school, name="Sports", code="SPO")
        emp = Employee.objects.create(
            school=school, user=emp_user, department=dept,
            first_name="Grace", last_name="Hill",
            email="grace@school.edu", employee_id="EMP060",
        )
        leave = LeaveRequest.objects.create(
            school=school, employee=emp,
            leave_type="personal", from_date=date.today(),
            to_date=date.today(), reason="Personal",
            status="pending",
        )
        r = admin_client.post(f"{HR_LEAVES}{leave.id}/reject/")
        assert r.status_code == status.HTTP_200_OK
        leave.refresh_from_db()
        assert leave.status == "rejected"
