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


# ---------------------------------------------------------------------------
# P1: Performance Management Tests
# ---------------------------------------------------------------------------


class TestPerformanceManagement:
    """Tests for performance management features."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_review_cycle(self):
        r = self.client.post(
            "/api/v1/hr/review-cycles/",
            {
                "name": "Annual Review 2026",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
                "status": "planning",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Annual Review 2026"

    def test_create_performance_goal(self):
        from services.hr.models import Employee
        from tests.factories import TeacherUserFactory

        teacher = TeacherUserFactory(school=self.school)
        employee = Employee.objects.create(
            user=teacher,
            school=self.school,
            employee_id="EMP001",
            designation="Teacher",
            joining_date="2024-01-01",
            address="Test Address",
        )
        cycle = self.client.post(
            "/api/v1/hr/review-cycles/",
            {
                "name": "Q1 2026",
                "start_date": "2026-01-01",
                "end_date": "2026-03-31",
                "status": "active",
            },
            format="json",
        ).data
        r = self.client.post(
            "/api/v1/hr/performance-goals/",
            {
                "employee": str(employee.id),
                "cycle": cycle["id"],
                "title": "Improve teaching scores",
                "priority": "high",
                "status": "in_progress",
                "progress_pct": 50,
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["title"] == "Improve teaching scores"

    def test_list_review_cycles(self):
        r = self.client.get("/api/v1/hr/review-cycles/")
        assert r.status_code == status.HTTP_200_OK

    def test_list_performance_goals(self):
        r = self.client.get("/api/v1/hr/performance-goals/")
        assert r.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# P2: Recruitment Tests
# ---------------------------------------------------------------------------


class TestRecruitment:
    """Tests for recruitment features."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_job_posting(self):
        r = self.client.post(
            "/api/v1/hr/job-postings/",
            {
                "title": "Math Teacher",
                "description": "Teach mathematics to grades 9-12",
                "designation": "Teacher",
                "employment_type": "full_time",
                "status": "open",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["title"] == "Math Teacher"

    def test_create_applicant(self):
        job = self.client.post(
            "/api/v1/hr/job-postings/",
            {
                "title": "Science Teacher",
                "description": "Teach science",
                "designation": "Teacher",
                "status": "open",
            },
            format="json",
        ).data
        r = self.client.post(
            "/api/v1/hr/applicants/",
            {
                "job_posting": job["id"],
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "status": "new",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["full_name"] == "John Doe"

    def test_advance_applicant_status(self):
        job = self.client.post(
            "/api/v1/hr/job-postings/",
            {
                "title": "Math Teacher",
                "description": "Teach math",
                "designation": "Teacher",
                "status": "open",
            },
            format="json",
        ).data
        applicant = self.client.post(
            "/api/v1/hr/applicants/",
            {
                "job_posting": job["id"],
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "status": "new",
            },
            format="json",
        ).data
        r = self.client.post(f"/api/v1/hr/applicants/{applicant['id']}/advance-status/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["status"] == "screening"

    def test_list_job_postings(self):
        r = self.client.get("/api/v1/hr/job-postings/")
        assert r.status_code == status.HTTP_200_OK

    def test_list_applicants(self):
        r = self.client.get("/api/v1/hr/applicants/")
        assert r.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# P3: Time Tracking Tests
# ---------------------------------------------------------------------------


class TestTimeTracking:
    """Tests for time tracking features."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_time_entry(self):
        from services.hr.models import Employee
        from tests.factories import TeacherUserFactory

        teacher = TeacherUserFactory(school=self.school)
        employee = Employee.objects.create(
            user=teacher,
            school=self.school,
            employee_id="EMP002",
            designation="Teacher",
            joining_date="2024-01-01",
            address="Test Address",
        )
        r = self.client.post(
            "/api/v1/hr/time-entries/",
            {
                "employee": str(employee.id),
                "date": "2026-08-31",
                "clock_in": "2026-08-31T09:00:00Z",
                "clock_out": "2026-08-31T17:30:00Z",
                "break_minutes": 60,
                "total_hours": "7.50",
                "overtime_hours": "0.00",
                "status": "pending",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED

    def test_list_time_entries(self):
        r = self.client.get("/api/v1/hr/time-entries/")
        assert r.status_code == status.HTTP_200_OK

    def test_list_timesheets(self):
        r = self.client.get("/api/v1/hr/timesheets/")
        assert r.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# P4: Benefits Tests
# ---------------------------------------------------------------------------


class TestBenefits:
    """Tests for benefits features."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_benefit_plan(self):
        r = self.client.post(
            "/api/v1/hr/benefit-plans/",
            {
                "name": "Health Insurance Basic",
                "benefit_type": "health",
                "provider": "Blue Cross",
                "employee_contribution": "100.00",
                "employer_contribution": "400.00",
                "is_active": True,
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Health Insurance Basic"

    def test_list_benefit_plans(self):
        r = self.client.get("/api/v1/hr/benefit-plans/")
        assert r.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# P5: Training Tests
# ---------------------------------------------------------------------------


class TestTraining:
    """Tests for training features."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_training_program(self):
        r = self.client.post(
            "/api/v1/hr/training-programs/",
            {
                "name": "Classroom Management Workshop",
                "description": "Learn effective classroom management techniques",
                "training_type": "workshop",
                "start_date": "2026-09-01",
                "duration_hours": "8.0",
                "status": "planned",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Classroom Management Workshop"

    def test_list_training_programs(self):
        r = self.client.get("/api/v1/hr/training-programs/")
        assert r.status_code == status.HTTP_200_OK

    def test_create_certification(self):
        from services.hr.models import Employee
        from tests.factories import TeacherUserFactory

        teacher = TeacherUserFactory(school=self.school)
        employee = Employee.objects.create(
            user=teacher,
            school=self.school,
            employee_id="EMP003",
            designation="Teacher",
            joining_date="2024-01-01",
            address="Test Address",
        )
        r = self.client.post(
            "/api/v1/hr/certifications/",
            {
                "employee": str(employee.id),
                "name": "Teaching License",
                "issuing_organization": "State Board of Education",
                "issue_date": "2024-01-01",
                "expiry_date": "2028-01-01",
                "status": "active",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Teaching License"

    def test_list_certifications(self):
        r = self.client.get("/api/v1/hr/certifications/")
        assert r.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# P6: Employee Self-Service Tests
# ---------------------------------------------------------------------------


class TestEmployeeSelfService:
    """Tests for employee self-service features."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        from services.hr.models import Employee
        from tests.factories import AdminUserFactory, SchoolFactory, TeacherUserFactory

        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.teacher = TeacherUserFactory(school=self.school)
        self.employee = Employee.objects.create(
            user=self.teacher,
            school=self.school,
            employee_id="EMP100",
            designation="Teacher",
            joining_date="2024-01-01",
            address="Test Address",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_profile_update(self):
        self.client.force_authenticate(self.teacher)
        r = self.client.post(
            "/api/v1/hr/profile-updates/",
            {
                "field_name": "phone",
                "old_value": "+1-555-0000",
                "new_value": "+1-555-1234",
                "status": "pending",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED

    def test_approve_profile_update(self):
        from services.hr.models import EmployeeProfileUpdate

        update = EmployeeProfileUpdate.objects.create(
            employee=self.employee,
            field_name="phone",
            old_value="+1-555-0000",
            new_value="+1-555-1234",
        )
        r = self.client.post(f"/api/v1/hr/profile-updates/{update.id}/approve/")
        assert r.status_code == status.HTTP_200_OK
        update.refresh_from_db()
        assert update.status == "approved"

    def test_list_profile_updates(self):
        r = self.client.get("/api/v1/hr/profile-updates/")
        assert r.status_code == status.HTTP_200_OK

    def test_create_leave_balance(self):
        r = self.client.post(
            "/api/v1/hr/hr-leave-balances/",
            {
                "employee": str(self.employee.id),
                "leave_type": "annual",
                "year": 2026,
                "total_days": 20,
                "used_days": 5,
                "carried_over": 3,
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["remaining_days"] == 18

    def test_my_leave_balance(self):
        from services.hr.models import LeaveBalanceHR

        LeaveBalanceHR.objects.create(
            employee=self.employee,
            leave_type="annual",
            year=2026,
            total_days=20,
            used_days=5,
        )
        self.client.force_authenticate(self.teacher)
        r = self.client.get("/api/v1/hr/hr-leave-balances/my-balance/")
        assert r.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# P7: HR Analytics Tests
# ---------------------------------------------------------------------------


class TestHRAnalytics:
    """Tests for HR analytics features."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_get_dashboard_metrics(self):
        r = self.client.get("/api/v1/hr/hr-dashboard/metrics/")
        assert r.status_code == status.HTTP_200_OK
        assert "active_employees" in r.data

    def test_create_turnover_report(self):
        r = self.client.post(
            "/api/v1/hr/turnover-reports/",
            {
                "month": "2026-08-01",
                "total_employees_start": 50,
                "new_hires": 5,
                "separations": 2,
                "turnover_rate": "4.00",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED

    def test_create_salary_report(self):
        r = self.client.post(
            "/api/v1/hr/salary-reports/",
            {
                "month": "2026-08-01",
                "total_gross": "500000.00",
                "total_deductions": "100000.00",
                "total_net": "400000.00",
                "headcount": 50,
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED

    def test_list_turnover_reports(self):
        r = self.client.get("/api/v1/hr/turnover-reports/")
        assert r.status_code == status.HTTP_200_OK

    def test_list_salary_reports(self):
        r = self.client.get("/api/v1/hr/salary-reports/")
        assert r.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# P8: Document Management Tests
# ---------------------------------------------------------------------------


class TestDocumentManagement:
    """Tests for document management features."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_employee_document(self):
        from services.hr.models import Employee
        from tests.factories import TeacherUserFactory

        teacher = TeacherUserFactory(school=self.school)
        employee = Employee.objects.create(
            user=teacher,
            school=self.school,
            employee_id="EMP200",
            designation="Teacher",
            joining_date="2024-01-01",
            address="Test Address",
        )
        r = self.client.post(
            "/api/v1/hr/employee-documents/",
            {
                "employee": str(employee.id),
                "document_type": "contract",
                "title": "Employment Contract 2026",
                "file_url": "https://example.com/contract.pdf",
                "expiry_date": "2027-12-31",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["title"] == "Employment Contract 2026"

    def test_create_policy(self):
        r = self.client.post(
            "/api/v1/hr/policies/",
            {
                "title": "Leave Policy 2026",
                "description": "Annual leave policy",
                "content": "Full policy content here",
                "document_type": "leave_policy",
                "version": "1.0",
                "status": "active",
                "effective_date": "2026-01-01",
                "requires_acknowledgment": True,
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["requires_acknowledgment"] is True

    def test_acknowledge_policy(self):
        from services.hr.models import PolicyDocument

        policy = PolicyDocument.objects.create(
            school=self.school,
            title="Test Policy",
            content="Test content",
            status="active",
            requires_acknowledgment=True,
            uploaded_by=self.admin,
        )
        r = self.client.post(f"/api/v1/hr/policies/{policy.id}/acknowledge/")
        assert r.status_code == status.HTTP_201_CREATED

    def test_list_documents(self):
        r = self.client.get("/api/v1/hr/employee-documents/")
        assert r.status_code == status.HTTP_200_OK

    def test_list_policies(self):
        r = self.client.get("/api/v1/hr/policies/")
        assert r.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# P9: Compliance Tests
# ---------------------------------------------------------------------------


class TestCompliance:
    """Tests for compliance and audit features."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_list_audit_logs(self):
        r = self.client.get("/api/v1/hr/audit-logs/")
        assert r.status_code == status.HTTP_200_OK

    def test_audit_logs_read_only(self):
        r = self.client.post(
            "/api/v1/hr/audit-logs/",
            {"model_name": "Employee", "action_type": "create"},
            format="json",
        )
        assert r.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestPayrollRun:
    """Bulk payroll-run: one payslip per salaried employee for a period."""

    @staticmethod
    def _make_salaried_employee(school, email, basic="50000.00"):
        from services.hr.models import Department, Employee, EmployeeSalary
        from tests.factories import UserFactory

        emp_user = UserFactory(school=school, role="teacher", email=email)
        dept = Department.objects.create(school=school, name=f"Dept {email[:6]}", code=email[:6].upper())
        emp = Employee.objects.create(
            school=school,
            user=emp_user,
            department=dept,
            employee_id=f"EMP-{email[:8].upper()}",
            designation="Teacher",
            joining_date=date.today(),
        )
        EmployeeSalary.objects.create(
            employee=emp,
            basic_salary=Decimal(basic),
            effective_from=date.today(),
        )
        return emp

    def test_run_creates_payslips_with_summary(self, admin_client, school):
        self._make_salaried_employee(school, "run-a@school.edu", basic="50000.00")
        self._make_salaried_employee(school, "run-b@school.edu", basic="60000.00")
        r = admin_client.post(
            f"{HR_PAYSLIPS}payroll-run/",
            {"period_start": "2026-09-01", "period_end": "2026-09-30"},
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["created"] == 2
        assert r.data["existing"] == 0
        assert Decimal(r.data["total_net"]) == Decimal("110000.00")

    def test_run_is_idempotent_per_period(self, admin_client, school):
        self._make_salaried_employee(school, "run-c@school.edu")
        payload = {"period_start": "2026-09-01", "period_end": "2026-09-30"}
        r1 = admin_client.post(f"{HR_PAYSLIPS}payroll-run/", payload, format="json")
        r2 = admin_client.post(f"{HR_PAYSLIPS}payroll-run/", payload, format="json")
        assert r1.status_code == status.HTTP_201_CREATED
        assert r2.status_code == status.HTTP_200_OK
        assert r2.data["created"] == 0
        assert r2.data["existing"] == 1

    def test_run_filters_by_department(self, admin_client, school):
        from services.hr.models import Employee, EmployeeSalary
        from tests.factories import UserFactory

        emp = self._make_salaried_employee(school, "run-d@school.edu")
        other_user = UserFactory(school=school, role="teacher", email="run-e@school.edu")
        other_emp = Employee.objects.create(
            school=school,
            user=other_user,
            department=emp.department,
            employee_id="EMP-RUN-E",
            designation="Teacher",
            joining_date=date.today(),
        )
        EmployeeSalary.objects.create(employee=other_emp, basic_salary=Decimal("70000.00"), effective_from=date.today())
        r = admin_client.post(
            f"{HR_PAYSLIPS}payroll-run/",
            {
                "period_start": "2026-09-01",
                "period_end": "2026-09-30",
                "employee_ids": [str(emp.id)],
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["created"] == 1

    def test_run_without_salaries_is_empty(self, admin_client, school):
        r = admin_client.post(
            f"{HR_PAYSLIPS}payroll-run/",
            {"period_start": "2026-09-01", "period_end": "2026-09-30"},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.data["created"] == 0

    def test_run_requires_period(self, admin_client, school):
        r = admin_client.post(f"{HR_PAYSLIPS}payroll-run/", {}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
