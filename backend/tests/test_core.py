"""
Test Suite — Core service tests using pytest-django + factory-boy
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def school(db):
    from services.auth.models import School
    return School.objects.create(
        name="Test Academy",
        code="TEST",
        subdomain="test",
        address="123 School Lane",
        phone="555-0100",
        email="admin@testacademy.edu",
        is_active=True,
    )


@pytest.fixture
def admin_user(db, school):
    from services.auth.models import User, UserRole
    user = User.objects.create_user(
        email="admin@testacademy.edu",
        password="AdminPass@1234",
        first_name="Alice",
        last_name="Admin",
        role=UserRole.SCHOOL_ADMIN,
        school=school,
        is_active=True,
    )
    return user


@pytest.fixture
def teacher_user(db, school):
    from services.auth.models import User, UserRole
    return User.objects.create_user(
        email="teacher@testacademy.edu",
        password="TeacherPass@1234",
        first_name="Bob",
        last_name="Teacher",
        role=UserRole.TEACHER,
        school=school,
        is_active=True,
    )


@pytest.fixture
def student_user(db, school):
    from services.auth.models import User, UserRole
    return User.objects.create_user(
        email="student@testacademy.edu",
        password="StudentPass@1234",
        first_name="Charlie",
        last_name="Student",
        role=UserRole.STUDENT,
        school=school,
        is_active=True,
    )


@pytest.fixture
def parent_user(db, school):
    from services.auth.models import User, UserRole
    return User.objects.create_user(
        email="parent@testacademy.edu",
        password="ParentPass@1234",
        first_name="Diana",
        last_name="Parent",
        role=UserRole.PARENT,
        school=school,
        is_active=True,
    )


@pytest.fixture
def academic_year(db, school):
    from services.students.models import AcademicYear
    return AcademicYear.objects.create(
        school=school,
        name="2024-2025",
        start_date=date(2024, 9, 1),
        end_date=date(2025, 6, 30),
        is_current=True,
    )


@pytest.fixture
def grade(db, school):
    from services.students.models import Grade
    return Grade.objects.create(school=school, name="Grade 5", level=5)


@pytest.fixture
def classroom(db, school, grade, academic_year, teacher_user):
    from services.students.models import Classroom
    return Classroom.objects.create(
        school=school,
        grade=grade,
        name="5A",
        capacity=35,
        class_teacher=teacher_user,
        academic_year=academic_year,
    )


@pytest.fixture
def student(db, school, student_user):
    from services.students.models import Student
    return Student.objects.create(
        user=student_user,
        school=school,
        admission_number="ADM-2024-001",
        date_of_birth=date(2012, 5, 15),
        gender="M",
        address="456 Student Ave",
        city="Testville",
        state="TS",
        country="Testland",
        admission_date=date(2024, 9, 1),
    )


@pytest.fixture
def enrollment(db, student, classroom, academic_year):
    from services.students.models import Enrollment
    return Enrollment.objects.create(
        student=student,
        classroom=classroom,
        academic_year=academic_year,
    )


@pytest.fixture
def admin_auth_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def teacher_auth_client(api_client, teacher_user):
    api_client.force_authenticate(user=teacher_user)
    return api_client


@pytest.fixture
def student_auth_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def parent_auth_client(api_client, parent_user, student):
    from services.students.models import Guardian, StudentGuardian
    guardian = Guardian.objects.create(
        user=parent_user,
        first_name=parent_user.first_name,
        last_name=parent_user.last_name,
        email=parent_user.email,
        phone="555-0200",
    )
    StudentGuardian.objects.create(
        student=student,
        guardian=guardian,
        relationship="mother",
        is_primary_contact=True,
        portal_access=True,
    )
    api_client.force_authenticate(user=parent_user)
    return api_client


# ─── Auth Tests ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAuthentication:

    def test_login_success(self, api_client, admin_user):
        response = api_client.post("/api/v1/auth/login/", {
            "email": "admin@testacademy.edu",
            "password": "AdminPass@1234",
        })
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["role"] == "school_admin"

    def test_login_wrong_password(self, api_client, admin_user):
        response = api_client.post("/api/v1/auth/login/", {
            "email": "admin@testacademy.edu",
            "password": "WrongPass@9999",
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unknown_email(self, api_client):
        response = api_client.post("/api/v1/auth/login/", {
            "email": "ghost@testacademy.edu",
            "password": "GhostPass@1234",
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_access_denied(self, api_client):
        response = api_client.get("/api/v1/students/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, admin_user):
        login = api_client.post("/api/v1/auth/login/", {
            "email": "admin@testacademy.edu",
            "password": "AdminPass@1234",
        })
        refresh_token = login.data["refresh"]
        response = api_client.post("/api/v1/auth/token/refresh/", {"refresh": refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


# ─── Student Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentAPI:

    def test_admin_can_list_students(self, admin_auth_client, student, school):
        response = admin_auth_client.get("/api/v1/students/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_student_can_view_own_profile(self, student_auth_client, student):
        response = student_auth_client.get(f"/api/v1/students/{student.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["admission_number"] == "ADM-2024-001"

    def test_student_cannot_view_other_student(
        self, db, school, student, academic_year
    ):
        from services.auth.models import User, UserRole
        from services.students.models import Student
        from rest_framework.test import APIClient

        other_user = User.objects.create_user(
            email="other@testacademy.edu", password="OtherPass@1234",
            first_name="Other", last_name="Student",
            role=UserRole.STUDENT, school=school,
        )
        other_student = Student.objects.create(
            user=other_user, school=school,
            admission_number="ADM-2024-002",
            date_of_birth=date(2012, 3, 10),
            gender="F", address="789 Other St",
            city="Testville", state="TS", country="Testland",
            admission_date=date(2024, 9, 1),
        )
        client = APIClient()
        client.force_authenticate(user=student.user)
        response = client.get(f"/api/v1/students/{other_student.id}/")
        # Student should not see another student's profile
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN
        ]

    def test_parent_can_view_child(self, parent_auth_client, student):
        response = parent_auth_client.get(f"/api/v1/students/{student.id}/")
        assert response.status_code == status.HTTP_200_OK

    def test_teacher_cannot_create_student(self, teacher_auth_client):
        response = teacher_auth_client.post("/api/v1/students/", {
            "first_name": "New", "last_name": "Student",
            "email": "new@testacademy.edu",
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_search_by_name(self, admin_auth_client, student):
        response = admin_auth_client.get("/api/v1/students/?search=Charlie")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_student_filter_by_gender(self, admin_auth_client, student):
        response = admin_auth_client.get("/api/v1/students/?gender=M")
        assert response.status_code == status.HTTP_200_OK
        for s in response.data["results"]:
            assert s["gender"] == "M"

    def test_student_attendance_summary(self, admin_auth_client, student, classroom, academic_year):
        from services.attendance.models import AttendanceRecord
        AttendanceRecord.objects.create(
            student=student, classroom=classroom,
            academic_year=academic_year, date=date.today(),
            status="P",
        )
        response = admin_auth_client.get(
            f"/api/v1/students/{student.id}/attendance-summary/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_days"] == 1
        assert response.data["present"] == 1
        assert response.data["attendance_percentage"] == 100.0


# ─── Attendance Tests ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAttendanceAPI:

    def test_bulk_record_attendance(
        self, teacher_auth_client, student, classroom, academic_year, enrollment
    ):
        payload = {
            "classroom_id": classroom.id,
            "date": date.today().isoformat(),
            "records": [
                {"student_id": str(student.id), "status": "P", "remarks": ""},
            ],
        }
        response = teacher_auth_client.post("/api/v1/attendance/bulk-record/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["recorded"] == 1

    def test_attendance_record_persists(
        self, teacher_auth_client, student, classroom, academic_year, enrollment
    ):
        from services.attendance.models import AttendanceRecord
        today = date.today()
        payload = {
            "classroom_id": classroom.id,
            "date": today.isoformat(),
            "records": [{"student_id": str(student.id), "status": "A"}],
        }
        teacher_auth_client.post("/api/v1/attendance/bulk-record/", payload, format="json")
        record = AttendanceRecord.objects.filter(student=student, date=today).first()
        assert record is not None
        assert record.status == "A"

    def test_classroom_summary(self, teacher_auth_client, student, classroom, academic_year, enrollment):
        from services.attendance.models import AttendanceRecord
        today = date.today()
        AttendanceRecord.objects.create(
            student=student, classroom=classroom, academic_year=academic_year,
            date=today, status="P",
        )
        response = teacher_auth_client.get(
            f"/api/v1/attendance/classroom-summary/?classroom_id={classroom.id}&date={today}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["breakdown"]["present"] == 1

    def test_student_cannot_record_attendance(
        self, student_auth_client, student, classroom
    ):
        payload = {
            "classroom_id": classroom.id,
            "date": date.today().isoformat(),
            "records": [{"student_id": str(student.id), "status": "P"}],
        }
        response = student_auth_client.post(
            "/api/v1/attendance/bulk-record/", payload, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_duplicate_attendance_upserts(
        self, teacher_auth_client, student, classroom, academic_year, enrollment
    ):
        from services.attendance.models import AttendanceRecord
        today = date.today()
        payload = {
            "classroom_id": classroom.id,
            "date": today.isoformat(),
            "records": [{"student_id": str(student.id), "status": "P"}],
        }
        teacher_auth_client.post("/api/v1/attendance/bulk-record/", payload, format="json")
        payload["records"][0]["status"] = "L"
        teacher_auth_client.post("/api/v1/attendance/bulk-record/", payload, format="json")
        count = AttendanceRecord.objects.filter(student=student, date=today).count()
        assert count == 1
        record = AttendanceRecord.objects.get(student=student, date=today)
        assert record.status == "L"


# ─── Gradebook Tests ───────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGradebook:

    def test_grade_percentage_calculation(self, db, student, classroom, academic_year):
        from services.gradebook.models import (
            ExamType, Exam, ExamSchedule, Grade as GradeRecord
        )
        from services.academics.models import Subject
        from services.auth.models import School

        school = student.school
        subject = Subject.objects.create(
            school=school, name="Mathematics", code="MATH",
            grade=classroom.grade, max_marks=100, pass_marks=40,
        )
        exam_type = ExamType.objects.create(school=school, name="Midterm", weightage=50)
        exam = Exam.objects.create(
            school=school, academic_year=academic_year, exam_type=exam_type,
            name="Midterm 2024", start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 10), status="completed",
        )
        schedule = ExamSchedule.objects.create(
            exam=exam, subject=subject, classroom=classroom,
            date=date(2024, 11, 5), start_time="09:00",
            end_time="11:00", max_marks=Decimal("100"),
            passing_marks=Decimal("40"),
        )
        grade_record = GradeRecord.objects.create(
            student=student, exam_schedule=schedule,
            marks_obtained=Decimal("75"),
        )
        assert grade_record.percentage == Decimal("75")
        assert grade_record.is_pass is True

    def test_absent_student_fails(self, db, student, classroom, academic_year):
        from services.gradebook.models import (
            ExamType, Exam, ExamSchedule, Grade as GradeRecord
        )
        from services.academics.models import Subject

        school = student.school
        subject = Subject.objects.create(
            school=school, name="Science", code="SCI",
            grade=classroom.grade, max_marks=100, pass_marks=35,
        )
        exam_type = ExamType.objects.create(school=school, name="Final", weightage=100)
        exam = Exam.objects.create(
            school=school, academic_year=academic_year, exam_type=exam_type,
            name="Final 2024", start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 10), status="completed",
        )
        schedule = ExamSchedule.objects.create(
            exam=exam, subject=subject, classroom=classroom,
            date=date(2024, 12, 5), start_time="10:00", end_time="12:00",
            max_marks=Decimal("100"), passing_marks=Decimal("35"),
        )
        grade_record = GradeRecord.objects.create(
            student=student, exam_schedule=schedule, is_absent=True,
        )
        assert grade_record.percentage is None
        assert grade_record.is_pass is False


# ─── Communication Tests ───────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCommunication:

    def test_admin_can_create_announcement(self, admin_auth_client, school):
        payload = {
            "title": "School Holiday Notice",
            "content": "School will be closed on Friday due to a public holiday.",
            "priority": "high",
            "audience": "all",
            "is_draft": False,
        }
        response = admin_auth_client.post(
            "/api/v1/communication/announcements/", payload, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "School Holiday Notice"

    def test_student_cannot_create_announcement(self, student_auth_client):
        response = student_auth_client.post(
            "/api/v1/communication/announcements/",
            {"title": "Test", "content": "Hello", "is_draft": False},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ─── Fee Tests ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFeeModels:

    def test_invoice_outstanding_calculation(self, db, student, academic_year, school):
        from services.fees.models import FeeCategory, FeeStructure, FeeInvoice
        from services.students.models import Grade

        grade = student.enrollments.filter(is_active=True).first()
        category = FeeCategory.objects.create(
            school=school, name="Tuition", recurrence="monthly",
        )
        classroom_grade = Grade.objects.get(classrooms__enrollments__student=student)
        structure = FeeStructure.objects.create(
            school=school, academic_year=academic_year,
            grade=classroom_grade,
            fee_category=category, amount=Decimal("500.00"),
        )
        invoice = FeeInvoice.objects.create(
            invoice_number="INV-2024-001",
            student=student,
            academic_year=academic_year,
            fee_structure=structure,
            due_date=date(2024, 10, 10),
            base_amount=Decimal("500.00"),
            total_amount=Decimal("500.00"),
            paid_amount=Decimal("200.00"),
        )
        assert invoice.outstanding_amount == Decimal("300.00")

    def test_scholarship_applied(self, db, student, academic_year, school):
        from services.fees.models import FeeCategory, Scholarship

        category = FeeCategory.objects.create(school=school, name="Transport")
        scholarship = Scholarship.objects.create(
            school=school, student=student, academic_year=academic_year,
            name="Merit Scholarship", discount_type="percent",
            discount_value=Decimal("50.00"),
            reason="Academic excellence",
        )
        scholarship.applies_to_categories.add(category)
        assert scholarship.discount_value == Decimal("50.00")
        assert category in scholarship.applies_to_categories.all()


# ─── Tenant Isolation Tests ────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTenantIsolation:

    def test_user_cannot_access_other_school_students(self, db):
        from services.auth.models import School, User, UserRole
        from services.students.models import Student
        from rest_framework.test import APIClient

        # School A
        school_a = School.objects.create(
            name="School A", code="SCHA", subdomain="scha",
            address="1 A St", phone="111", email="a@a.edu",
        )
        admin_a = User.objects.create_user(
            email="admin@a.edu", password="Pass@1234", first_name="Admin",
            last_name="A", role=UserRole.SCHOOL_ADMIN, school=school_a,
        )

        # School B
        school_b = School.objects.create(
            name="School B", code="SCHB", subdomain="schb",
            address="2 B St", phone="222", email="b@b.edu",
        )
        user_b = User.objects.create_user(
            email="student@b.edu", password="Pass@1234", first_name="Student",
            last_name="B", role=UserRole.STUDENT, school=school_b,
        )
        student_b = Student.objects.create(
            user=user_b, school=school_b, admission_number="SCH-B-001",
            date_of_birth=date(2012, 1, 1), gender="M",
            address="2 B Ave", city="B City", state="BS",
            country="BL", admission_date=date(2024, 9, 1),
        )

        # Admin A tries to access School B's student
        client = APIClient()
        client.force_authenticate(user=admin_a)
        response = client.get(f"/api/v1/students/{student_b.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
