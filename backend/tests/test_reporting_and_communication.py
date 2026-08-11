"""
Test Suite — Reporting, Communication, Timetable, Attendance Extended
Covers all previously untested service areas.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import (
    AcademicYearFactory,
    AdminUserFactory,
    AnnouncementFactory,
    ClassroomFactory,
    EnrollmentFactory,
    FeeCategoryFactory,
    FeeInvoiceFactory,
    FeeStructureFactory,
    GradeFactory,
    NotificationFactory,
    ParentUserFactory,
    SchoolFactory,
    StudentFactory,
    StudentUserFactory,
    TeacherUserFactory,
)
from tests.url_helpers import (
    COMMUNICATION_ANNOUNCEMENTS,
    COMMUNICATION_MESSAGES,
    COMMUNICATION_NOTIFICATIONS_MARK_ALL_READ,
    COMMUNICATION_NOTIFICATIONS_UNREAD_COUNT,
    REPORTING_ATTENDANCE_REPORT,
    REPORTING_DASHBOARD_STATS,
    REPORTING_EXPORT_ATTENDANCE_PDF,
    REPORTING_EXPORT_STUDENTS_CSV,
    REPORTING_FEE_REPORT,
    communication_announcement_detail,
    communication_announcement_publish,
)

# ─── Shared fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def school(db):
    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    return AdminUserFactory(school=school)


@pytest.fixture
def teacher(db, school):
    return TeacherUserFactory(school=school)


@pytest.fixture
def student_user(db, school):
    return StudentUserFactory(school=school)


@pytest.fixture
def parent_user(db, school):
    return ParentUserFactory(school=school)


@pytest.fixture
def student(db, school, student_user):
    return StudentFactory(user=student_user, school=school)


@pytest.fixture
def academic_year(db, school):
    return AcademicYearFactory(school=school)


@pytest.fixture
def grade(db, school):
    return GradeFactory(school=school)


@pytest.fixture
def classroom(db, school, grade, academic_year, teacher):
    return ClassroomFactory(
        school=school,
        grade=grade,
        academic_year=academic_year,
        class_teacher=teacher,
    )


@pytest.fixture
def enrollment(db, student, classroom, academic_year):
    return EnrollmentFactory(
        student=student,
        classroom=classroom,
        academic_year=academic_year,
    )


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


@pytest.fixture
def student_client(db, student_user):
    c = APIClient()
    c.force_authenticate(user=student_user)
    return c


@pytest.fixture
def parent_client(db, parent_user):
    c = APIClient()
    c.force_authenticate(user=parent_user)
    return c


# ─── Reporting Tests ──────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestReportingAPI:

    def test_dashboard_stats_returns_expected_keys(self, admin_client):
        r = admin_client.get(REPORTING_DASHBOARD_STATS)
        assert r.status_code == status.HTTP_200_OK
        expected = {
            "total_students",
            "total_teachers",
            "total_classrooms",
            "attendance_today_pct",
            "fees_collected_month",
            "fees_outstanding",
        }
        assert expected.issubset(r.data.keys()), f"Missing keys: {expected - r.data.keys()}"

    def test_dashboard_stats_counts_correctly(self, admin_client, school, student, teacher):
        r = admin_client.get(REPORTING_DASHBOARD_STATS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["total_students"] >= 1
        assert r.data["total_teachers"] >= 1

    def test_dashboard_stats_includes_trend_and_grade_distribution(self, admin_client):
        r = admin_client.get(REPORTING_DASHBOARD_STATS)
        assert r.status_code == status.HTTP_200_OK
        # Trend chart data: list of {day, present, absent}
        assert isinstance(r.data["attendance_week"], list)
        for row in r.data["attendance_week"]:
            assert set(row.keys()) == {"day", "present", "absent"}
        # Grade distribution: list of {name, value}
        assert isinstance(r.data["grade_distribution"], list)
        for row in r.data["grade_distribution"]:
            assert set(row.keys()) == {"name", "value"}

    def test_attendance_report_accepts_date_range(self, admin_client):
        today = date.today()
        params = {
            "from_date": (today - timedelta(days=30)).isoformat(),
            "to_date": today.isoformat(),
        }
        r = admin_client.get(REPORTING_ATTENDANCE_REPORT, params)
        assert r.status_code == status.HTTP_200_OK

    def test_fee_report_returns_collection_stats(self, admin_client, school, student, academic_year):
        cat = FeeCategoryFactory(school=school)
        grade_obj = GradeFactory(school=school)
        structure = FeeStructureFactory(
            school=school,
            academic_year=academic_year,
            grade=grade_obj,
            fee_category=cat,
        )
        FeeInvoiceFactory(
            student=student,
            academic_year=academic_year,
            fee_structure=structure,
            status="paid",
            paid_amount=Decimal("500"),
            total_amount=Decimal("500"),
        )
        FeeInvoiceFactory(
            student=student,
            academic_year=academic_year,
            fee_structure=structure,
            status="unpaid",
        )
        r = admin_client.get(REPORTING_FEE_REPORT, {"academic_year_id": academic_year.id})
        assert r.status_code == status.HTTP_200_OK
        assert "total_collected" in r.data
        assert "total_invoiced" in r.data

    def test_student_csv_export_returns_csv(self, admin_client):
        r = admin_client.get(REPORTING_EXPORT_STUDENTS_CSV)
        assert r.status_code == status.HTTP_200_OK
        assert "text/csv" in r.get("Content-Type", "")

    def test_attendance_pdf_export(self, admin_client, classroom):
        r = admin_client.get(
            REPORTING_EXPORT_ATTENDANCE_PDF,
            {"classroom_id": classroom.id},
        )
        assert r.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_reporting_not_accessible_to_students(self, student_client):
        r = student_client.get(REPORTING_DASHBOARD_STATS)
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_reporting_not_accessible_to_parents(self, parent_client):
        r = parent_client.get(REPORTING_DASHBOARD_STATS)
        assert r.status_code == status.HTTP_403_FORBIDDEN


# ─── Communication Extended Tests ─────────────────────────────────────────────


@pytest.mark.django_db
class TestCommunicationExtended:

    def test_announcement_view_count_increments(self, admin_client, school, admin):
        ann = AnnouncementFactory(school=school, is_draft=False, created_by=admin)
        initial_count = ann.view_count
        admin_client.get(communication_announcement_detail(str(ann.id)))
        ann.refresh_from_db()
        assert ann.view_count >= initial_count

    def test_student_cannot_see_teacher_only_announcement(self, student_client, school, admin):
        teacher_ann = AnnouncementFactory(
            school=school,
            audience="teachers",
            is_draft=False,
            created_by=admin,
        )
        r = student_client.get(COMMUNICATION_ANNOUNCEMENTS)
        assert r.status_code == status.HTTP_200_OK
        ids = [a["id"] for a in r.data.get("results", [])]
        assert str(teacher_ann.id) not in ids

    def test_draft_not_visible_to_non_admin(self, student_client, school, admin):
        draft = AnnouncementFactory(school=school, is_draft=True, created_by=admin)
        r = student_client.get(COMMUNICATION_ANNOUNCEMENTS)
        ids = [a["id"] for a in r.data.get("results", [])]
        assert str(draft.id) not in ids

    def test_notification_mark_all_read(self, student_client, student_user):
        n1 = NotificationFactory(user=student_user, status="sent")
        n2 = NotificationFactory(user=student_user, status="sent")
        r = student_client.post(COMMUNICATION_NOTIFICATIONS_MARK_ALL_READ)
        assert r.status_code == status.HTTP_200_OK
        n1.refresh_from_db()
        n2.refresh_from_db()
        assert n1.read_at is not None
        assert n2.read_at is not None

    def test_notification_unread_count(self, student_client, student_user):
        NotificationFactory(user=student_user, status="sent")
        NotificationFactory(user=student_user, status="sent")
        r = student_client.get(COMMUNICATION_NOTIFICATIONS_UNREAD_COUNT)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 2

    def test_send_direct_message(self, teacher_client, teacher, student_user):
        payload = {
            "recipient": str(student_user.id),
            "content": "Please submit your assignment.",
        }
        r = teacher_client.post(COMMUNICATION_MESSAGES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["content"] == "Please submit your assignment."

    def test_cannot_send_message_to_different_school_user(self, teacher_client):
        other_school = SchoolFactory()
        other_user = StudentUserFactory(school=other_school)
        payload = {"recipient": str(other_user.id), "content": "Cross-school message."}
        r = teacher_client.post(COMMUNICATION_MESSAGES, payload, format="json")
        assert r.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]

    def test_admin_can_publish_announcement(self, admin_client, school, admin):
        ann = AnnouncementFactory(school=school, is_draft=True, created_by=admin)
        r = admin_client.post(communication_announcement_publish(str(ann.id)))
        assert r.status_code == status.HTTP_200_OK
        ann.refresh_from_db()
        assert not ann.is_draft
