"""
Test Suite — Core service tests using pytest-django + factory-boy
"""

import pytest
from datetime import date
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import (
    AUTH_LOGIN,
    AUTH_TOKEN_REFRESH,
    STUDENTS_LIST,
    student_detail,
    student_attendance_summary,
    ATTENDANCE_BULK_RECORD,
    ATTENDANCE_CLASSROOM_SUMMARY,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory
    return SchoolFactory()


@pytest.fixture
def admin_user(db, school):
    from tests.factories import AdminUserFactory
    return AdminUserFactory(school=school)


@pytest.fixture
def unverified_user(db, school):
    """User with email_verified=False (default factories have verified=True)."""
    from tests.factories import UserFactory
    return UserFactory(
        school=school,
        email="unverified-login@school.edu",
        role="student",
        email_verified=False,
    )


@pytest.fixture
def verified_user(db, school):
    """User with email_verified=True (explicit)."""
    from tests.factories import UserFactory
    return UserFactory(
        school=school,
        email="verified-login@school.edu",
        role="student",
        email_verified=True,
    )


@pytest.fixture
def teacher_user(db, school):
    from tests.factories import TeacherUserFactory
    return TeacherUserFactory(school=school)


@pytest.fixture
def student_user(db, school):
    from tests.factories import StudentUserFactory
    return StudentUserFactory(school=school)


@pytest.fixture
def parent_user(db, school):
    from tests.factories import ParentUserFactory
    return ParentUserFactory(school=school)


@pytest.fixture
def academic_year(db, school):
    from tests.factories import AcademicYearFactory
    return AcademicYearFactory(school=school)


@pytest.fixture
def grade(db, school):
    from tests.factories import GradeFactory
    return GradeFactory(school=school, level=5)


@pytest.fixture
def classroom(db, school, grade, academic_year, teacher_user):
    from tests.factories import ClassroomFactory
    return ClassroomFactory(
        school=school, grade=grade, academic_year=academic_year, class_teacher=teacher_user
    )


@pytest.fixture
def student(db, school, student_user):
    from tests.factories import StudentFactory
    return StudentFactory(user=student_user, school=school)


@pytest.fixture
def enrollment(db, student, classroom, academic_year):
    from tests.factories import EnrollmentFactory
    return EnrollmentFactory(student=student, classroom=classroom, academic_year=academic_year)


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
    from tests.factories import GuardianFactory
    from services.students.models import StudentGuardian

    guardian = GuardianFactory(
        user=parent_user,
        first_name=parent_user.first_name,
        last_name=parent_user.last_name,
        email=parent_user.email,
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
        response = api_client.post(AUTH_LOGIN, {
            "email": admin_user.email,
            "password": "TestPass@1234",
        })
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["role"] == "school_admin"

    def test_login_wrong_password(self, api_client, admin_user):
        response = api_client.post(AUTH_LOGIN, {
            "email": admin_user.email,
            "password": "WrongPass@9999",
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unknown_email(self, api_client):
        response = api_client.post(AUTH_LOGIN, {
            "email": "ghost@school.edu",
            "password": "GhostPass@1234",
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_access_denied(self, api_client):
        response = api_client.get(STUDENTS_LIST)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, admin_user):
        login = api_client.post(AUTH_LOGIN, {
            "email": admin_user.email,
            "password": "TestPass@1234",
        })
        refresh_token = login.data["refresh"]
        response = api_client.post(AUTH_TOKEN_REFRESH, {"refresh": refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    # ── Email verification notification on login ─────────────────────

    def test_login_unverified_creates_in_app_notification(self, api_client, unverified_user):
        """
        When an unverified user logs in, an in-app Notification record
        should be created (via the Celery task, which runs synchronously
        thanks to CELERY_TASK_ALWAYS_EAGER).
        """
        from services.communication.models import Notification

        response = api_client.post(AUTH_LOGIN, {
            "email": unverified_user.email,
            "password": "TestPass@1234",
        })
        assert response.status_code == status.HTTP_200_OK

        notif = Notification.objects.filter(
            user=unverified_user, channel="in_app"
        ).first()
        assert notif is not None, "No in-app notification found after unverified login"
        assert notif.title == "Email not verified"
        assert "has not been verified" in notif.body
        assert notif.reference_type == "email_verification"
        assert notif.status == "sent"
        assert notif.sent_at is not None

    def test_login_unverified_notification_has_correct_body(self, api_client, unverified_user):
        """The notification body educates the user on next steps."""
        from services.communication.models import Notification

        api_client.post(AUTH_LOGIN, {
            "email": unverified_user.email,
            "password": "TestPass@1234",
        })

        notif = Notification.objects.filter(
            user=unverified_user, channel="in_app"
        ).first()
        assert notif is not None
        assert "profile settings" in notif.body.lower()
        assert "verification link" in notif.body.lower()

    def test_login_verified_does_not_create_notification(self, api_client, verified_user):
        """A user with email_verified=True should NOT get a notification on login."""
        from services.communication.models import Notification

        response = api_client.post(AUTH_LOGIN, {
            "email": verified_user.email,
            "password": "TestPass@1234",
        })
        assert response.status_code == status.HTTP_200_OK

        notif_count = Notification.objects.filter(
            user=verified_user, channel="in_app"
        ).count()
        assert notif_count == 0, (
            f"Expected 0 notifications for verified login, got {notif_count}"
        )


# ─── Student Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentAPI:

    def test_admin_can_list_students(self, admin_auth_client, student, school):
        response = admin_auth_client.get(STUDENTS_LIST)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_student_can_view_own_profile(self, student_auth_client, student):
        response = student_auth_client.get(student_detail(student.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["admission_number"] == student.admission_number

    def test_student_cannot_view_other_student(self, db, school):
        from tests.factories import StudentUserFactory, StudentFactory
        other_user = StudentUserFactory(school=school)
        other_student = StudentFactory(user=other_user, school=school)

        different_user = StudentUserFactory(school=school)
        client = APIClient()
        client.force_authenticate(user=different_user)
        response = client.get(student_detail(other_student.id))
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN
        ]

    def test_parent_can_view_child(self, parent_auth_client, student):
        response = parent_auth_client.get(student_detail(student.id))
        assert response.status_code == status.HTTP_200_OK

    def test_teacher_cannot_create_student(self, teacher_auth_client):
        response = teacher_auth_client.post(STUDENTS_LIST, {
            "first_name": "New", "last_name": "Student",
            "email": "new@testacademy.edu",
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_search_by_name(self, admin_auth_client, student):
        response = admin_auth_client.get(f"{STUDENTS_LIST}?search={student.user.first_name}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_student_filter_by_gender(self, admin_auth_client, student):
        response = admin_auth_client.get(f"{STUDENTS_LIST}?gender={student.gender}")
        assert response.status_code == status.HTTP_200_OK
        for s in response.data["results"]:
            assert s["gender"] == student.gender

    def test_student_attendance_summary(self, admin_auth_client, student, classroom, academic_year):
        from tests.factories import AttendanceRecordFactory
        AttendanceRecordFactory(
            student=student, classroom=classroom,
            academic_year=academic_year, date=date.today(), status="P",
        )
        response = admin_auth_client.get(student_attendance_summary(student.id))
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
        response = teacher_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
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
        teacher_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
        record = AttendanceRecord.objects.filter(student=student, date=today).first()
        assert record is not None
        assert record.status == "A"

    def test_classroom_summary(self, teacher_auth_client, student, classroom, academic_year, enrollment):
        from tests.factories import AttendanceRecordFactory
        today = date.today()
        AttendanceRecordFactory(
            student=student, classroom=classroom, academic_year=academic_year,
            date=today, status="P",
        )
        response = teacher_auth_client.get(
            f"{ATTENDANCE_CLASSROOM_SUMMARY}?classroom_id={classroom.id}&date={today}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["breakdown"]["present"] == 1

    def test_student_cannot_record_attendance(self, student_auth_client, student, classroom):
        payload = {
            "classroom_id": classroom.id,
            "date": date.today().isoformat(),
            "records": [{"student_id": str(student.id), "status": "P"}],
        }
        response = student_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
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
        teacher_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
        payload["records"][0]["status"] = "L"
        teacher_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
        count = AttendanceRecord.objects.filter(student=student, date=today).count()
        assert count == 1
        record = AttendanceRecord.objects.get(student=student, date=today)
        assert record.status == "L"


# ─── Tenant Isolation Tests ────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTenantIsolation:
    """Critical: Validate that users can't access other schools' data."""

    def test_user_cannot_access_other_school_students(self, db):
        from services.auth.models import School, User, UserRole
        from services.students.models import Student

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
        response = client.get(student_detail(student_b.id))
        assert response.status_code == status.HTTP_404_NOT_FOUND
