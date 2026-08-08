"""Tests for Attendance Service — Records, bulk recording, leaves, streaks."""

from datetime import date, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import ATTENDANCE_BULK_RECORD, ATTENDANCE_CLASSROOM_SUMMARY, ATTENDANCE_STUDENT_REPORT

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
        school=school,
        grade=grade,
        academic_year=academic_year,
        class_teacher=teacher_user,
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


# ─── Attendance Record Tests ──────────────────────────────────────────────────


@pytest.mark.django_db
class TestAttendanceRecords:

    def test_bulk_record_success(self, teacher_auth_client, student, classroom):
        payload = {
            "classroom_id": classroom.id,
            "date": date.today().isoformat(),
            "records": [{"student_id": str(student.id), "status": "P"}],
        }
        response = teacher_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["recorded"] == 1

    def test_bulk_record_upserts(self, teacher_auth_client, student, classroom):
        """Duplicate date+student should update, not create a second record."""
        from services.attendance.models import AttendanceRecord

        payload = {
            "classroom_id": classroom.id,
            "date": date.today().isoformat(),
            "records": [{"student_id": str(student.id), "status": "P"}],
        }
        teacher_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
        payload["records"][0]["status"] = "A"
        teacher_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")

        records = AttendanceRecord.objects.filter(student=student, date=date.today())
        assert records.count() == 1
        assert records.first().status == "A"

    def test_student_cannot_record(self, student_auth_client, student, classroom):
        payload = {
            "classroom_id": classroom.id,
            "date": date.today().isoformat(),
            "records": [{"student_id": str(student.id), "status": "P"}],
        }
        response = student_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_bulk_record_max_limit(self, teacher_auth_client, classroom):
        """Sending more than MAX_BULK_RECORDS (50) should be blocked."""
        payload = {
            "classroom_id": classroom.id,
            "date": date.today().isoformat(),
            "records": [{"student_id": "fake", "status": "P"}] * 51,
        }
        response = teacher_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_record_invalid_classroom(self, teacher_auth_client, student):
        """Non-existent classroom returns 400."""
        payload = {
            "classroom_id": 9999,
            "date": date.today().isoformat(),
            "records": [{"student_id": str(student.id), "status": "P"}],
        }
        response = teacher_auth_client.post(ATTENDANCE_BULK_RECORD, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── Attendance Summary Tests ─────────────────────────────────────────────────


@pytest.mark.django_db
class TestAttendanceSummary:

    def test_classroom_summary(self, teacher_auth_client, student, classroom, academic_year, enrollment):
        from tests.factories import AttendanceRecordFactory

        today = date.today()
        AttendanceRecordFactory(
            student=student,
            classroom=classroom,
            academic_year=academic_year,
            date=today,
            status="P",
        )
        response = teacher_auth_client.get(f"{ATTENDANCE_CLASSROOM_SUMMARY}?classroom_id={classroom.id}&date={today}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["breakdown"]["present"] == 1
        assert response.data["total_students"] >= 1

    def test_classroom_summary_missing_classroom(self, teacher_auth_client):
        response = teacher_auth_client.get(ATTENDANCE_CLASSROOM_SUMMARY)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_student_report(self, teacher_auth_client, student, classroom, academic_year, enrollment):
        from tests.factories import AttendanceRecordFactory

        today = date.today()
        AttendanceRecordFactory(
            student=student,
            classroom=classroom,
            academic_year=academic_year,
            date=today,
            status="P",
        )
        response = teacher_auth_client.get(
            ATTENDANCE_STUDENT_REPORT,
            {"student_id": student.id, "month": today.month, "year": today.year},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_school_days"] >= 1

    def test_student_report_missing_student_id(self, teacher_auth_client):
        response = teacher_auth_client.get(ATTENDANCE_STUDENT_REPORT)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── Attendance Streak Tests ──────────────────────────────────────────────────


@pytest.mark.django_db
class TestAttendanceStreak:

    def test_streak_zero_when_no_records(self, teacher_auth_client, student, classroom, academic_year, enrollment):
        response = teacher_auth_client.get(f"/api/v1/attendance/streak/?student_id={student.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["current_streak"] == 0
        assert response.data["longest_streak"] == 0

    def test_streak_computes_correctly(
        self, teacher_auth_client, teacher_user, student, classroom, academic_year, enrollment
    ):
        from services.attendance.models import AttendanceRecord

        today = date.today()
        # Create 3 consecutive present records ending today
        for i in range(3):
            AttendanceRecord.objects.create(
                student=student,
                classroom=classroom,
                academic_year=academic_year,
                date=today - timedelta(days=2 - i),
                status="P",
                recorded_by=teacher_user,
            )
        response = teacher_auth_client.get(f"/api/v1/attendance/streak/?student_id={student.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["current_streak"] == 3
        assert response.data["longest_streak"] == 3

    def test_streak_student_not_found(self, teacher_auth_client):
        response = teacher_auth_client.get("/api/v1/attendance/streak/?student_id=00000000-0000-0000-0000-000000000000")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_streak_missing_student_id(self, teacher_auth_client):
        response = teacher_auth_client.get("/api/v1/attendance/streak/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── Attendance Leave Tests ───────────────────────────────────────────────────


@pytest.mark.django_db
class TestAttendanceLeaves:

    def test_student_can_create_leave(self, student_auth_client, student):
        payload = {
            "student": student.id,
            "leave_type": "sick",
            "from_date": date.today().isoformat(),
            "to_date": (date.today() + timedelta(days=2)).isoformat(),
            "reason": "Feeling unwell",
        }
        response = student_auth_client.post("/api/v1/attendance/leaves/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "pending"

    def test_admin_can_approve_leave(self, admin_auth_client, student):
        from services.attendance.models import AttendanceLeave

        leave = AttendanceLeave.objects.create(
            student=student,
            leave_type="family",
            from_date=date.today(),
            to_date=date.today() + timedelta(days=1),
            reason="Family event",
            status="pending",
        )
        response = admin_auth_client.post(
            f"/api/v1/attendance/leaves/{leave.id}/approve/",
            {"remarks": "Approved"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "approved"

    def test_admin_can_reject_leave(self, admin_auth_client, student):
        from services.attendance.models import AttendanceLeave

        leave = AttendanceLeave.objects.create(
            student=student,
            leave_type="other",
            from_date=date.today(),
            to_date=date.today(),
            reason="No reason",
            status="pending",
        )
        response = admin_auth_client.post(
            f"/api/v1/attendance/leaves/{leave.id}/reject/",
            {"remarks": "Not valid"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "rejected"

    def test_list_leaves_filtered_by_school(self, admin_auth_client, student):
        from tests.factories import SchoolFactory, StudentFactory, StudentUserFactory

        other_school = SchoolFactory(code="OTHERL")
        other_user = StudentUserFactory(school=other_school)
        other_student = StudentFactory(user=other_user, school=other_school)

        from services.attendance.models import AttendanceLeave

        AttendanceLeave.objects.create(
            student=other_student,
            leave_type="sick",
            from_date=date.today(),
            to_date=date.today(),
            reason="Sick",
        )
        response = admin_auth_client.get("/api/v1/attendance/leaves/")
        assert response.status_code == status.HTTP_200_OK
        # Admin's school has no leaves (only other school's) — list endpoints
        # are paginated, so check the count.
        assert response.data["count"] == 0

    def test_student_leave_total_days(self, student, classroom, academic_year):
        from services.attendance.models import AttendanceLeave

        leave = AttendanceLeave.objects.create(
            student=student,
            leave_type="sick",
            from_date=date(2025, 3, 10),
            to_date=date(2025, 3, 12),
            reason="Sick",
        )
        assert leave.total_days == 3
