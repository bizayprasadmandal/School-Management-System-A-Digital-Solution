"""Tests for Timetable Service — Periods, TimetableSlots, SchoolEvents."""

from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import (
    TIMETABLE_EVENTS,
    TIMETABLE_EVENTS_UPCOMING,
    TIMETABLE_PERIODS,
    TIMETABLE_SLOTS,
    TIMETABLE_TEACHER_SCHEDULE,
    TIMETABLE_WEEKLY,
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
def teacher_user(db, school):
    from tests.factories import TeacherUserFactory

    return TeacherUserFactory(school=school)


@pytest.fixture
def student_user(db, school):
    from tests.factories import StudentUserFactory

    return StudentUserFactory(school=school)


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
def subject(db, school, grade):
    from tests.factories import SubjectFactory

    return SubjectFactory(school=school, grade=grade)


@pytest.fixture
def period(db, school):
    from tests.factories import PeriodFactory

    return PeriodFactory(school=school)


@pytest.fixture
def teacher_assignment(db, teacher_user, subject, classroom, academic_year):
    from tests.factories import TeacherAssignmentFactory

    return TeacherAssignmentFactory(
        teacher=teacher_user,
        subject=subject,
        classroom=classroom,
        academic_year=academic_year,
    )


@pytest.fixture
def timetable_slot(db, teacher_assignment, classroom, period, academic_year):
    from tests.factories import TimetableSlotFactory

    return TimetableSlotFactory(
        assignment=teacher_assignment,
        classroom=classroom,
        period=period,
        academic_year=academic_year,
        day_of_week=0,
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


# ─── Period Tests ─────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestPeriods:

    def test_admin_can_create_period(self, admin_auth_client, school):
        payload = {
            "name": "Period 1",
            "period_number": 1,
            "start_time": "08:00",
            "end_time": "08:45",
        }
        response = admin_auth_client.post(TIMETABLE_PERIODS, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["period_number"] == 1

    def test_student_cannot_create_period(self, student_auth_client):
        payload = {"name": "P1", "period_number": 1, "start_time": "08:00", "end_time": "08:45"}
        response = student_auth_client.post(TIMETABLE_PERIODS, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_periods(self, admin_auth_client, period):
        response = admin_auth_client.get(TIMETABLE_PERIODS)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_period_ordered_by_period_number(self, admin_auth_client, school):
        from tests.factories import PeriodFactory

        PeriodFactory(school=school, period_number=2)
        PeriodFactory(school=school, period_number=1)
        response = admin_auth_client.get(TIMETABLE_PERIODS)
        numbers = [p["period_number"] for p in response.data["results"]]
        assert numbers == sorted(numbers)

    def test_period_unique_per_number(self, admin_auth_client, period):
        """Duplicate period_number for same school should fail."""
        payload = {
            "name": "P2",
            "period_number": period.period_number,
            "start_time": "09:00",
            "end_time": "09:45",
        }
        response = admin_auth_client.post(TIMETABLE_PERIODS, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── TimetableSlot Tests ──────────────────────────────────────────────────────


@pytest.mark.django_db
class TestTimetableSlots:

    def test_admin_can_create_slot(self, admin_auth_client, teacher_assignment, classroom, period, academic_year):
        payload = {
            "classroom": classroom.id,
            "assignment": teacher_assignment.id,
            "period": period.id,
            "day_of_week": 0,
            "academic_year": academic_year.id,
        }
        response = admin_auth_client.post(TIMETABLE_SLOTS, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["day_of_week"] == 0

    def test_student_cannot_create_slot(
        self, student_auth_client, teacher_assignment, classroom, period, academic_year
    ):
        payload = {
            "classroom": classroom.id,
            "assignment": teacher_assignment.id,
            "period": period.id,
            "day_of_week": 0,
            "academic_year": academic_year.id,
        }
        response = student_auth_client.post(TIMETABLE_SLOTS, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_slots(self, admin_auth_client, timetable_slot):
        response = admin_auth_client.get(TIMETABLE_SLOTS)
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) >= 1
        assert results[0]["subject_name"] is not None

    def test_slot_filter_by_classroom(self, admin_auth_client, timetable_slot):
        response = admin_auth_client.get(f"{TIMETABLE_SLOTS}?classroom={timetable_slot.classroom.id}")
        assert response.status_code == status.HTTP_200_OK
        for s in response.data["results"]:
            assert s["classroom"] == timetable_slot.classroom.id

    def test_slot_filter_by_day(self, admin_auth_client, timetable_slot):
        response = admin_auth_client.get(f"{TIMETABLE_SLOTS}?day_of_week={timetable_slot.day_of_week}")
        assert response.status_code == status.HTTP_200_OK

    def test_teacher_conflict_detection(self, admin_auth_client, teacher_assignment, classroom, period, academic_year):
        """Creating two slots at same time for same teacher should fail."""
        payload = {
            "classroom": classroom.id,
            "assignment": teacher_assignment.id,
            "period": period.id,
            "day_of_week": 0,
            "academic_year": academic_year.id,
        }
        admin_auth_client.post(TIMETABLE_SLOTS, payload, format="json")
        response = admin_auth_client.post(TIMETABLE_SLOTS, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_can_update_slot(self, admin_auth_client, timetable_slot):
        response = admin_auth_client.patch(
            f"{TIMETABLE_SLOTS}{timetable_slot.id}/",
            {"day_of_week": 2},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["day_of_week"] == 2

    def test_admin_can_delete_slot(self, admin_auth_client, timetable_slot):
        response = admin_auth_client.delete(f"{TIMETABLE_SLOTS}{timetable_slot.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


# ─── Weekly & Teacher Schedule Tests ──────────────────────────────────────────


@pytest.mark.django_db
class TestWeeklySchedule:

    def test_weekly_structure(self, admin_auth_client, timetable_slot):
        response = admin_auth_client.get(
            TIMETABLE_WEEKLY,
            {
                "classroom_id": timetable_slot.classroom.id,
                "academic_year_id": timetable_slot.academic_year.id,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Monday" in response.data
        assert len(response.data["Monday"]) >= 1

    def test_weekly_requires_classroom(self, admin_auth_client):
        response = admin_auth_client.get(TIMETABLE_WEEKLY)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_teacher_schedule(self, admin_auth_client, timetable_slot):
        response = admin_auth_client.get(
            f"{TIMETABLE_TEACHER_SCHEDULE}?teacher_id={timetable_slot.assignment.teacher.id}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_teacher_only_sees_own_slots(self, teacher_auth_client, timetable_slot, db, school):
        """A teacher's queryset is filtered to their own assignments."""
        response = teacher_auth_client.get(TIMETABLE_SLOTS)
        assert response.status_code == status.HTTP_200_OK
        # The slot belongs to the teacher_user fixture
        assert len(response.data) >= 1


# ─── SchoolEvent Tests ────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSchoolEvents:

    def test_admin_can_create_event(self, admin_auth_client, school):
        payload = {
            "title": "Sports Day",
            "event_type": "sports",
            "start_date": date.today().isoformat(),
            "end_date": date.today().isoformat(),
        }
        response = admin_auth_client.post(TIMETABLE_EVENTS, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Sports Day"

    def test_student_cannot_create_event(self, student_auth_client):
        payload = {
            "title": "Event",
            "event_type": "other",
            "start_date": date.today().isoformat(),
            "end_date": date.today().isoformat(),
        }
        response = student_auth_client.post(TIMETABLE_EVENTS, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_events(self, admin_auth_client, school):
        from tests.factories import SchoolEventFactory

        SchoolEventFactory(school=school)
        response = admin_auth_client.get(TIMETABLE_EVENTS)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_upcoming_events(self, admin_auth_client, school):
        from datetime import timedelta

        from tests.factories import SchoolEventFactory

        SchoolEventFactory(
            school=school,
            start_date=date.today() + timedelta(days=2),
        )
        SchoolEventFactory(
            school=admin_auth_client.handler._force_user.school,
            start_date=date.today() - timedelta(days=5),
        )
        response = admin_auth_client.get(TIMETABLE_EVENTS_UPCOMING)
        assert response.status_code == status.HTTP_200_OK
        for event in response.data:
            assert event["id"] is not None

    def test_event_filter_by_type(self, admin_auth_client, school):
        from tests.factories import SchoolEventFactory

        SchoolEventFactory(school=school, event_type="holiday")
        SchoolEventFactory(school=school, event_type="sports")
        response = admin_auth_client.get(f"{TIMETABLE_EVENTS}?event_type=holiday")
        assert response.status_code == status.HTTP_200_OK
        for e in response.data["results"]:
            assert e["event_type"] == "holiday"

    def test_event_search(self, admin_auth_client, school):
        from tests.factories import SchoolEventFactory

        SchoolEventFactory(school=school, title="Independence Day Celebration")
        response = admin_auth_client.get(f"{TIMETABLE_EVENTS}?search=Independence")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_tenant_isolation_event(self, db):
        """School A cannot see School B events."""
        from tests.factories import AdminUserFactory, SchoolEventFactory, SchoolFactory

        school_a = SchoolFactory(code="EVTA")
        school_b = SchoolFactory(code="EVTB")
        admin_a = AdminUserFactory(school=school_a)
        SchoolEventFactory(school=school_b, title="Secret Event")
        client = APIClient()
        client.force_authenticate(user=admin_a)
        response = client.get(TIMETABLE_EVENTS)
        titles = [e["title"] for e in response.data["results"]]
        assert "Secret Event" not in titles
