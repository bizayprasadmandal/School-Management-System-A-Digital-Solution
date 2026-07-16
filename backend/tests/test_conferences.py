"""Tests for Conferences Service — ConferenceSlot, Zoom integration."""

import pytest
from datetime import date, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

CONFERENCES_SLOTS = f"{API_PREFIX}/conferences/conference-slots/"


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
def student_user(db, school):
    from tests.factories import StudentUserFactory
    return StudentUserFactory(school=school)


@pytest.fixture
def parent_user(db, school):
    from tests.factories import ParentUserFactory
    return ParentUserFactory(school=school)


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


@pytest.fixture
def slot(db, school, teacher):
    from services.conferences.models import ConferenceSlot
    return ConferenceSlot.objects.create(
        school=school,
        teacher=teacher,
        date=date.today(),
        start_time="09:00",
        end_time="09:30",
        is_booked=False,
    )


@pytest.mark.django_db
class TestConferenceSlots:

    def test_admin_can_create_slot(self, admin_client, school, teacher):
        payload = {
            "teacher": teacher.id,
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "10:00",
            "end_time": "10:30",
        }
        r = admin_client.post(CONFERENCES_SLOTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_teacher_can_create_slot(self, teacher_client, school, teacher):
        payload = {
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "start_time": "11:00",
            "end_time": "11:30",
        }
        r = teacher_client.post(CONFERENCES_SLOTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_student_cannot_create_slot(self, student_client):
        payload = {
            "date": "2025-06-01", "start_time": "08:00", "end_time": "08:30",
        }
        r = student_client.post(CONFERENCES_SLOTS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_available_slots(self, student_client, slot):
        r = student_client.get(f"{CONFERENCES_SLOTS}?is_booked=False")
        assert r.status_code == status.HTTP_200_OK
        ids = [s["id"] for s in r.data.get("results", [])]
        assert str(slot.id) in ids

    def test_book_slot(self, student_client, slot):
        r = student_client.post(f"{CONFERENCES_SLOTS}{slot.id}/book/")
        assert r.status_code == status.HTTP_200_OK
        slot.refresh_from_db()
        assert slot.is_booked is True

    def test_book_already_booked_slot(self, student_client, slot):
        slot.is_booked = True
        slot.save()
        r = student_client.post(f"{CONFERENCES_SLOTS}{slot.id}/book/")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_booking(self, slot, student_client):
        from tests.factories import StudentFactory
        pupil = StudentFactory(school=slot.school)
        slot.is_booked = True
        slot.booked_by = student_client.handler._force_user
        slot.student = pupil
        slot.save()
        r = student_client.post(f"{CONFERENCES_SLOTS}{slot.id}/cancel-booking/")
        assert r.status_code == status.HTTP_200_OK
        slot.refresh_from_db()
        assert slot.is_booked is False

    def test_teacher_sees_own_slots_only(self, db, school, teacher):
        from tests.factories import TeacherUserFactory
        from services.conferences.models import ConferenceSlot
        other_teacher = TeacherUserFactory(school=school)
        ConferenceSlot.objects.create(
            school=school, teacher=other_teacher,
            date=date.today(), start_time="14:00", end_time="14:30",
        )
        client = APIClient()
        client.force_authenticate(user=other_teacher)
        r = client.get(CONFERENCES_SLOTS)
        assert r.status_code == status.HTTP_200_OK

    def test_parent_can_book_for_child(self, parent_client, slot):
        from tests.factories import StudentFactory
        pupil = StudentFactory(school=slot.school)
        from tests.factories import GuardianFactory
        from services.students.models import StudentGuardian
        parent = parent_client.handler._force_user
        guardian = GuardianFactory(
            user=parent, first_name=parent.first_name,
            last_name=parent.last_name, email=parent.email,
        )
        StudentGuardian.objects.create(
            student=pupil, guardian=guardian,
            relationship="father", is_primary_contact=True, portal_access=True,
        )
        r = parent_client.post(
            f"{CONFERENCES_SLOTS}{slot.id}/book/",
            {"student_id": str(pupil.id)},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK

    def test_parent_cannot_book_for_non_child(self, parent_client, slot):
        from tests.factories import StudentFactory
        other_pupil = StudentFactory(school=slot.school)
        r = parent_client.post(
            f"{CONFERENCES_SLOTS}{slot.id}/book/",
            {"student_id": str(other_pupil.id)},
            format="json",
        )
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_complete_slot(self, admin_client, slot, teacher):
        slot.is_booked = True
        slot.save()
        r = admin_client.post(f"{CONFERENCES_SLOTS}{slot.id}/complete/")
        assert r.status_code == status.HTTP_200_OK
        slot.refresh_from_db()
        assert slot.status == "completed"

    def test_tenant_isolation(self, db):
        from tests.factories import SchoolFactory, AdminUserFactory
        from services.conferences.models import ConferenceSlot
        school_a = SchoolFactory(code="CONFA")
        school_b = SchoolFactory(code="CONFB")
        admin_a = AdminUserFactory(school=school_a)
        teacher_b = AdminUserFactory(school=school_b)
        ConferenceSlot.objects.create(
            school=school_b, teacher=teacher_b,
            date=date.today(), start_time="09:00", end_time="09:30",
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(CONFERENCES_SLOTS)
        assert r.data["count"] == 0
