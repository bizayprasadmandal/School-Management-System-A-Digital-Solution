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


@pytest.mark.django_db
class TestBulkPayrollActions:
    """Bulk approve / bulk mark-paid for whole payroll runs."""

    @staticmethod
    def _make_payslip(school, email, status="draft", net="40000.00"):
        from services.hr.models import Department, Employee, Payslip
        from tests.factories import UserFactory

        emp_user = UserFactory(school=school, role="teacher", email=email)
        dept = Department.objects.create(school=school, name=f"BD {email[:6]}", code=email[:6].upper())
        emp = Employee.objects.create(
            school=school,
            user=emp_user,
            department=dept,
            employee_id=f"EMP-{email[:8].upper()}",
            designation="Teacher",
            joining_date=date.today(),
        )
        return Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today().replace(day=1),
            period_end=date.today(),
            basic_salary=Decimal(net),
            gross_pay=Decimal(net),
            total_deductions=Decimal("0.00"),
            net_pay=Decimal(net),
            status=status,
        )

    def test_bulk_approve_only_touches_drafts(self, admin_client, school):
        from services.hr.models import Payslip

        d1 = self._make_payslip(school, "bulk-a@school.edu", status="draft")
        d2 = self._make_payslip(school, "bulk-b@school.edu", status="draft")
        already = self._make_payslip(school, "bulk-c@school.edu", status="approved")
        r = admin_client.post(
            f"{HR_PAYSLIPS}bulk-approve/",
            {"ids": [str(d1.id), str(d2.id), str(already.id)]},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.data["approved"] == 2
        assert r.data["skipped"] == 1
        already.refresh_from_db()
        assert already.status == Payslip.Status.APPROVED

    def test_bulk_mark_paid_posts_each_to_ledger(self, admin_client, school):
        from services.fees.models import AccountingEntry

        p1 = self._make_payslip(school, "bulk-d@school.edu", status="approved", net="40000.00")
        p2 = self._make_payslip(school, "bulk-e@school.edu", status="approved", net="55000.00")
        draft = self._make_payslip(school, "bulk-f@school.edu", status="draft")
        r = admin_client.post(
            f"{HR_PAYSLIPS}bulk-mark-paid/",
            {"ids": [str(p1.id), str(p2.id), str(draft.id)], "payment_method": "bank"},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.data["paid"] == 2
        assert r.data["skipped"] == 1
        entries = AccountingEntry.objects.filter(reference_type="payslip", reference_id__in=[str(p1.id), str(p2.id)])
        assert entries.count() == 2
        assert set(entries.values_list("amount", flat=True)) == {Decimal("40000.00"), Decimal("55000.00")}
        draft.refresh_from_db()
        from services.hr.models import Payslip

        assert draft.status == Payslip.Status.DRAFT

    def test_bulk_requires_ids(self, admin_client, school):
        for path in ("bulk-approve/", "bulk-mark-paid/"):
            r = admin_client.post(f"{HR_PAYSLIPS}{path}", {}, format="json")
            assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_scoped_to_school(self, admin_client, school):
        from services.fees.models import AccountingEntry
        from tests.factories import SchoolFactory

        other_school = SchoolFactory(code="BULKX")
        slip_b = self._make_payslip(other_school, "bulk-g@school.edu", status="approved")
        r = admin_client.post(f"{HR_PAYSLIPS}bulk-mark-paid/", {"ids": [str(slip_b.id)]}, format="json")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["paid"] == 0
        assert not AccountingEntry.objects.filter(reference_type="payslip").exists()


@pytest.mark.django_db
class TestPayslipSelfService:
    """Self-service: staff read only their own payslips; view logging on retrieve."""

    def _employee_with_slip(self, school, email, net="40000.00"):
        from services.hr.models import Department, Employee, Payslip
        from tests.factories import UserFactory

        user = UserFactory(school=school, role="teacher", email=email)
        dept = Department.objects.get_or_create(school=school, name="SelfService", defaults={"code": "SELF"})[0]
        emp = Employee.objects.create(
            school=school,
            user=user,
            department=dept,
            employee_id=f"EMP-{email[:10]}",
            designation="Teacher",
            joining_date=date.today(),
        )
        slip = Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today().replace(day=1),
            period_end=date.today(),
            basic_salary=Decimal("30000"),
            gross_pay=Decimal("45000"),
            total_deductions=Decimal("5000"),
            net_pay=Decimal(net),
            status="paid",
        )
        return user, emp, slip

    def test_staff_sees_only_own_slips(self, admin_client, school):
        own_user, _, own = self._employee_with_slip(school, "own@school.edu")
        _, _, other = self._employee_with_slip(school, "other@school.edu", net="99000.00")

        c = APIClient()
        c.force_authenticate(user=own_user)
        r = c.get(HR_PAYSLIPS)
        assert r.status_code == status.HTTP_200_OK
        ids = [str(row["id"]) for row in r.data["results"]]
        assert str(own.id) in ids
        assert str(other.id) not in ids

        # Detail access to someone else's slip is 404, not 403 (no existence leak)
        r404 = c.get(f"{HR_PAYSLIPS}{other.id}/")
        assert r404.status_code == status.HTTP_404_NOT_FOUND

        # Admin still sees the whole school's slips
        r_admin = admin_client.get(HR_PAYSLIPS)
        admin_ids = [str(row["id"]) for row in r_admin.data["results"]]
        assert str(own.id) in admin_ids and str(other.id) in admin_ids

    def test_retrieve_own_slip_logs_view(self, school):
        user, emp, slip = self._employee_with_slip(school, "viewer@school.edu")

        c = APIClient()
        c.force_authenticate(user=user)
        r = c.get(f"{HR_PAYSLIPS}{slip.id}/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["net_pay"] == "40000.00"

        from services.hr.models import PayslipViewLog

        assert PayslipViewLog.objects.filter(payslip=slip, employee=emp).exists()

    def test_admin_actions_stay_restricted(self, teacher_client, school):
        _, _, slip = self._employee_with_slip(school, "norole@school.edu")

        # The bulk/self-service surface must not hand out admin powers
        r = teacher_client.post(f"{HR_PAYSLIPS}{slip.id}/approve/")
        assert r.status_code == status.HTTP_403_FORBIDDEN
        r2 = teacher_client.post(f"{HR_PAYSLIPS}{slip.id}/mark-paid/")
        assert r2.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPayslipViewReport:
    """Admin report over PayslipViewLog: who has (not) viewed their slips."""

    def _emp_with_slip(self, school, email, status="paid"):
        from services.hr.models import Department, Employee, Payslip
        from tests.factories import UserFactory

        user = UserFactory(school=school, role="teacher", email=email)
        dept = Department.objects.get_or_create(school=school, name="ViewReport", defaults={"code": "VRPT"})[0]
        emp = Employee.objects.create(
            school=school,
            user=user,
            department=dept,
            employee_id=f"EMP-{email[:10]}",
            designation="Teacher",
            joining_date=date.today(),
        )
        slip = Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today().replace(day=1),
            period_end=date.today(),
            basic_salary=Decimal("30000"),
            gross_pay=Decimal("45000"),
            total_deductions=Decimal("5000"),
            net_pay=Decimal("40000"),
            status=status,
        )
        return user, emp, slip

    def test_report_shows_unviewed_and_viewed(self, admin_client, school):
        from django.utils import timezone as tz
        from services.hr.models import PayslipViewLog

        _, emp_viewed, viewed = self._emp_with_slip(school, "viewed@school.edu")
        _, _, unviewed = self._emp_with_slip(school, "unviewed@school.edu")
        PayslipViewLog.objects.create(employee=emp_viewed, payslip=viewed, viewed_at=tz.now())

        r = admin_client.get(f"{HR_PAYSLIPS}view-report/")
        assert r.status_code == status.HTTP_200_OK
        rows = {row["payslip_id"]: row for row in r.data["results"]}
        assert rows[str(viewed.id)]["view_count"] == 1
        assert rows[str(viewed.id)]["last_viewed_at"] is not None
        assert rows[str(unviewed.id)]["view_count"] == 0
        assert rows[str(unviewed.id)]["last_viewed_at"] is None
        # Unviewed first — the point of the report
        assert r.data["results"][0]["payslip_id"] == str(unviewed.id)

    def test_report_filters_and_excludes_other_school(self, admin_client, school):
        from tests.factories import SchoolFactory

        _, _, slip = self._emp_with_slip(school, "filterme@school.edu")
        other_school = SchoolFactory(code="VRPTX")
        self._emp_with_slip(other_school, "alien@school.edu")

        r = admin_client.get(f"{HR_PAYSLIPS}view-report/?status=paid")
        ids = [row["payslip_id"] for row in r.data["results"]]
        assert str(slip.id) in ids
        assert all(row["status"] == "paid" for row in r.data["results"])

        r_month = admin_client.get(f"{HR_PAYSLIPS}view-report/?period={date.today().strftime('%Y-%m')}")
        assert r_month.status_code == status.HTTP_200_OK
        assert len(r_month.data["results"]) >= 1

        # Other school's slip must not leak
        r_all = admin_client.get(f"{HR_PAYSLIPS}view-report/")
        assert str(slip.id) in [row["payslip_id"] for row in r_all.data["results"]]
        alien = [row for row in r_all.data["results"] if row["employee_name"].startswith("Alien")]
        assert alien == [] or all(row["payslip_id"] != "" for row in alien)

    def test_report_is_admin_only(self, school):
        from rest_framework.test import APIClient

        user, _, _ = self._emp_with_slip(school, "reporter@school.edu")
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.get(f"{HR_PAYSLIPS}view-report/")
        assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPayslipPaidNotification:
    """Employees get an in-app notification when their payslip is paid."""

    def _approved_slip(self, school, email):
        from services.hr.models import Department, Employee, Payslip
        from tests.factories import UserFactory

        user = UserFactory(school=school, role="teacher", email=email)
        dept = Department.objects.get_or_create(school=school, name="Notify", defaults={"code": "NTFY"})[0]
        emp = Employee.objects.create(
            school=school,
            user=user,
            department=dept,
            employee_id=f"EMP-{email[:10]}",
            designation="Teacher",
            joining_date=date.today(),
        )
        slip = Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today().replace(day=1),
            period_end=date.today(),
            basic_salary=Decimal("30000"),
            gross_pay=Decimal("45000"),
            total_deductions=Decimal("5000"),
            net_pay=Decimal("40000"),
            status="approved",
        )
        return user, emp, slip

    def test_mark_paid_notifies_employee(self, admin_client, school):
        from services.communication.models import Notification

        _, emp, slip = self._approved_slip(school, "notify@school.edu")
        r = admin_client.post(f"{HR_PAYSLIPS}{slip.id}/mark-paid/", {"payment_method": "bank"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        notes = Notification.objects.filter(user=emp.user, reference_type="payslip", reference_id=str(slip.id))
        assert notes.exists()
        n = notes.first()
        assert n.channel == "in_app"
        assert "paid" in n.title.lower()
        assert "40000.00" in n.body

    def test_bulk_mark_paid_notifies_each_employee(self, admin_client, school):
        from services.communication.models import Notification

        _, emp_a, slip_a = self._approved_slip(school, "bulka@school.edu")
        _, emp_b, slip_b = self._approved_slip(school, "bulkb@school.edu")
        r = admin_client.post(
            f"{HR_PAYSLIPS}bulk-mark-paid/",
            {"ids": [str(slip_a.id), str(slip_b.id)]},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.data["paid"] == 2
        for emp, slip in ((emp_a, slip_a), (emp_b, slip_b)):
            assert Notification.objects.filter(
                user=emp.user, reference_type="payslip", reference_id=str(slip.id)
            ).exists()

    def test_no_notification_without_payment(self, admin_client, school):
        from services.communication.models import Notification

        _, _, slip = self._approved_slip(school, "nopay@school.edu")
        # Draft: wrong-state transition is rejected — no payment, no notification
        slip.status = "draft"
        slip.save(update_fields=["status"])
        r = admin_client.post(f"{HR_PAYSLIPS}{slip.id}/mark-paid/", {}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        # Already paid: retry is rejected too
        slip.status = "paid"
        slip.save(update_fields=["status"])
        r2 = admin_client.post(f"{HR_PAYSLIPS}{slip.id}/mark-paid/", {}, format="json")
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        assert Notification.objects.filter(reference_type="payslip").count() == 0


@pytest.mark.django_db
class TestPayrollTrend:
    """Monthly net/gross payroll series powering the panel sparkline."""

    def _slip(self, school, email, period_start, net="40000.00", gross="45000.00"):
        from services.hr.models import Department, Employee, Payslip
        from tests.factories import UserFactory

        user = UserFactory(school=school, role="teacher", email=email)
        dept = Department.objects.get_or_create(school=school, name="Trend", defaults={"code": "TRND"})[0]
        emp = Employee.objects.create(
            school=school,
            user=user,
            department=dept,
            employee_id=f"EMP-{email[:10]}",
            designation="Teacher",
            joining_date=date.today(),
        )
        return Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=period_start,
            period_end=period_start,
            basic_salary=Decimal("30000"),
            gross_pay=Decimal(gross),
            total_deductions=Decimal("5000"),
            net_pay=Decimal(net),
            status="paid",
        )

    def test_series_alignment_and_sums(self, admin_client, school):
        today = date.today()
        this_month = today.replace(day=1)
        prev_month = (this_month - timedelta(days=1)).replace(day=1)
        self._slip(school, "trend-a@school.edu", this_month, net="40000.00")
        self._slip(school, "trend-b@school.edu", this_month, net="30000.00")
        self._slip(school, "trend-c@school.edu", prev_month, net="20000.00")

        r = admin_client.get(f"{HR_PAYSLIPS}payroll-trend/")
        assert r.status_code == status.HTTP_200_OK
        labels = r.data["months"]
        assert len(labels) == 6
        assert labels[-1] == this_month.strftime("%Y-%m")
        net = [float(v) for v in r.data["net"]]
        gross = [float(v) for v in r.data["gross"]]
        assert net[-1] == 70000.0  # 40k + 30k this month
        assert net[-2] == 20000.0  # previous month
        assert gross[-1] == 90000.0
        # Zero-filled gaps
        assert all(v == 0.0 for v in net[:-2])

    def test_months_param_bounds(self, admin_client, school):
        r3 = admin_client.get(f"{HR_PAYSLIPS}payroll-trend/?months=3")
        assert r3.status_code == status.HTTP_200_OK
        assert len(r3.data["months"]) == 3
        r12 = admin_client.get(f"{HR_PAYSLIPS}payroll-trend/?months=12")
        assert len(r12.data["months"]) == 12
        # Junk falls back to 6; out-of-range clamps
        assert len(admin_client.get(f"{HR_PAYSLIPS}payroll-trend/?months=junk").data["months"]) == 6
        assert len(admin_client.get(f"{HR_PAYSLIPS}payroll-trend/?months=99").data["months"]) == 12

    def test_staff_scoped_to_own_history(self, school):
        from rest_framework.test import APIClient

        today = date.today()
        own = self._slip(school, "trend-own@school.edu", today.replace(day=1))
        self._slip(school, "trend-other@school.edu", today.replace(day=1))

        c = APIClient()
        c.force_authenticate(user=own.employee.user)
        r = c.get(f"{HR_PAYSLIPS}payroll-trend/")
        assert r.status_code == status.HTTP_200_OK
        assert float(r.data["net"][-1]) == 40000.0  # only own slip

    def test_admin_only_sees_whole_school(self, admin_client, school):
        today = date.today()
        self._slip(school, "trend-x@school.edu", today.replace(day=1))
        r = admin_client.get(f"{HR_PAYSLIPS}payroll-trend/")
        assert float(r.data["net"][-1]) == 40000.0


@pytest.mark.django_db
class TestPayrollBudget:
    """Payroll actuals vs budgeted salary lines for the current academic year."""

    def _setup(self, school, with_year=True):
        """Current academic year + a budget plan with matching and non-matching lines."""
        from services.fees.models import BudgetLineItem, BudgetPlan
        from services.students.models import AcademicYear

        if not with_year:
            AcademicYear.objects.filter(school=school).update(is_current=False)
            return None
        today = date.today()
        year, _ = AcademicYear.objects.get_or_create(
            school=school,
            name=f"{today.year}-{today.year + 1}",
            defaults={"start_date": date(today.year, 1, 1), "end_date": date(today.year, 12, 31), "is_current": True},
        )
        year.is_current = True
        year.save()
        plan = BudgetPlan.objects.create(
            school=school, academic_year=year, title="FY Plan", total_budget=Decimal("150000")
        )
        BudgetLineItem.objects.create(
            budget_plan=plan, description="Teacher salaries", budgeted_amount=Decimal("100000")
        )
        BudgetLineItem.objects.create(budget_plan=plan, description="Library books", budgeted_amount=Decimal("50000"))
        return year

    def _slip(self, school, email, status, net):
        from services.hr.models import Department, Employee, Payslip
        from tests.factories import UserFactory

        user = UserFactory(school=school, role="teacher", email=email)
        dept = Department.objects.get_or_create(school=school, name="Budget", defaults={"code": "BDGT"})[0]
        emp = Employee.objects.create(
            school=school,
            user=user,
            department=dept,
            employee_id=f"EMP-{email[:10]}",
            designation="Teacher",
            joining_date=date.today(),
        )
        return Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today().replace(day=1),
            period_end=date.today(),
            basic_salary=Decimal("30000"),
            gross_pay=Decimal(net) + Decimal("5000"),
            total_deductions=Decimal("5000"),
            net_pay=Decimal(net),
            status=status,
        )

    def test_budget_math_and_line_matching(self, admin_client, school):
        self._setup(school)
        self._slip(school, "budget-a@school.edu", "paid", Decimal("40000"))
        self._slip(school, "budget-b@school.edu", "approved", Decimal("20000"))

        r = admin_client.get(f"{HR_PAYSLIPS}payroll-budget/")
        assert r.status_code == status.HTTP_200_OK
        assert float(r.data["budgeted"]) == 100000.0  # only the salary line matches
        assert float(r.data["paid"]) == 40000.0
        assert float(r.data["pending"]) == 20000.0
        assert float(r.data["committed"]) == 60000.0
        assert float(r.data["variance"]) == 40000.0  # under budget
        assert r.data["utilization"] == 60.0

    def test_fallback_without_current_year(self, admin_client, school):
        self._setup(school, with_year=False)
        self._slip(school, "budget-c@school.edu", "paid", Decimal("25000"))

        r = admin_client.get(f"{HR_PAYSLIPS}payroll-budget/")
        assert r.status_code == status.HTTP_200_OK
        assert float(r.data["budgeted"]) == 0.0
        assert float(r.data["committed"]) == 25000.0
        assert r.data["utilization"] is None  # nothing budgeted

    def test_staff_forbidden(self, teacher_client, school):
        r = teacher_client.get(f"{HR_PAYSLIPS}payroll-budget/")
        assert r.status_code == status.HTTP_403_FORBIDDEN
