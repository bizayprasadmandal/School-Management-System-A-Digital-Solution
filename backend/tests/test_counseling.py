"""
Counseling service — coverage for appointments, referrals, dashboard stats,
and counselor profile endpoints, including tenant isolation.

Run standalone:

    python -m pytest tests/test_counseling.py -q
"""

import datetime

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from services.counseling.models import CounselingAppointment, CounselorProfile, StudentReferral
from tests.factories import (
    AdminUserFactory,
    SchoolFactory,
    StudentFactory,
    StudentUserFactory,
    TeacherUserFactory,
    UserFactory,
)

API_PREFIX = "/api/v1"
APPOINTMENTS_URL = f"{API_PREFIX}/counseling/appointments/"
REFERRALS_URL = f"{API_PREFIX}/counseling/referrals/"
DASHBOARD_URL = f"{API_PREFIX}/counseling/dashboard/stats/"
PROFILE_URL = f"{API_PREFIX}/counseling/profile/"


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def school(db):
    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    return AdminUserFactory(school=school)


@pytest.fixture
def student(db, school):
    return StudentUserFactory(school=school)


@pytest.fixture
def teacher(db, school):
    return TeacherUserFactory(school=school)


def _auth(client, user):
    client.force_authenticate(user=user)
    return client


def _make_student(school):
    return StudentFactory(school=school)


def _make_counselor(school, email):
    return UserFactory(school=school, role="counselor", email=email)


def _make_appointment(school, counselor, student, **kwargs):
    defaults = dict(
        appointment_type=CounselingAppointment.AppointmentType.ACADEMIC,
        scheduled_date=datetime.date(2026, 9, 15),
        scheduled_time=datetime.time(10, 0),
        duration_minutes=30,
        reason="Academic support",
    )
    defaults.update(kwargs)
    return CounselingAppointment.objects.create(school=school, counselor=counselor, student=student, **defaults)


def _make_referral(school, student, referred_by, **kwargs):
    defaults = dict(
        category=StudentReferral.ReferralCategory.ACADEMIC,
        priority=StudentReferral.Priority.MEDIUM,
        reason="Student is struggling with coursework",
    )
    defaults.update(kwargs)
    return StudentReferral.objects.create(school=school, student=student, referred_by=referred_by, **defaults)


# ===== Create endpoints: write-only flags no longer cause 500 =====


class TestCreateEndpoints:
    def test_create_appointment_with_send_reminder_flag(self, api, school, admin, db):
        """`send_reminder` is a write-only flag (not a model field) - popped at
        write-only `send_reminder` BooleanField that is not a model field;
                DRF create() passes it to Model.objects.create() -> TypeError -> 500.
                Fixed: create()/update() pop the flag before saving."""
        counselor = _make_counselor(school, "counselor-appt@school.edu")
        pupil = _make_student(school)
        payload = {
            "counselor": str(counselor.id),
            "student": str(pupil.id),
            "appointment_type": "academic",
            "scheduled_date": "2026-09-15",
            "scheduled_time": "10:00:00",
            "duration_minutes": 30,
            "reason": "Needs help with math",
            "send_reminder": True,
        }
        resp = _auth(api, admin).post(APPOINTMENTS_URL, payload, format="json")
        assert resp.status_code == 201, resp.content
        assert CounselingAppointment.objects.filter(student=pupil).exists()

    def test_create_referral_with_notify_counselor_flag(self, api, school, admin, db):
        """`notify_counselor` is a write-only flag (not a model field) - popped
        at save time; creation must succeed."""
        pupil = _make_student(school)
        payload = {
            "student": str(pupil.id),
            "category": "academic",
            "priority": "medium",
            "reason": "Student needs academic support urgently",
            "notify_counselor": True,
        }
        resp = _auth(api, admin).post(REFERRALS_URL, payload, format="json")
        assert resp.status_code == 201, resp.content
        assert StudentReferral.objects.filter(student=pupil).exists()


# ===== Appointments: list / retrieve / isolation =====


class TestAppointmentList:
    def test_admin_sees_school_appointments(self, api, school, admin, db):
        _make_appointment(school, _make_counselor(school, "c1@school.edu"), _make_student(school))
        resp = _auth(api, admin).get(APPOINTMENTS_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["count"] == 1

    def test_list_excludes_other_school(self, api, school, admin, db):
        _make_appointment(school, _make_counselor(school, "c2@school.edu"), _make_student(school))
        other_school = SchoolFactory()
        _make_appointment(other_school, _make_counselor(other_school, "c3@school.edu"), _make_student(other_school))
        resp = _auth(api, admin).get(APPOINTMENTS_URL)
        assert resp.json()["count"] == 1

    def test_counselor_sees_only_own_appointments(self, api, school, admin, db):
        counselor = _make_counselor(school, "c4@school.edu")
        other = _make_counselor(school, "c5@school.edu")
        _make_appointment(school, counselor, _make_student(school))
        _make_appointment(school, other, _make_student(school))
        resp = _auth(api, counselor).get(APPOINTMENTS_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["count"] == 1


class TestAppointmentRetrieve:
    def test_retrieve_own_school(self, api, school, admin, db):
        appt = _make_appointment(school, _make_counselor(school, "c6@school.edu"), _make_student(school))
        resp = _auth(api, admin).get(f"{APPOINTMENTS_URL}{appt.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == str(appt.id)

    def test_retrieve_other_school_404(self, api, school, admin, db):
        other_school = SchoolFactory()
        foreign_appt = _make_appointment(
            other_school, _make_counselor(other_school, "c7@school.edu"), _make_student(other_school)
        )
        resp = _auth(api, admin).get(f"{APPOINTMENTS_URL}{foreign_appt.id}/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ===== Appointments: PATCH + lifecycle actions =====


class TestAppointmentUpdateAndActions:
    def test_patch_updates_fields(self, api, school, admin, db):
        appt = _make_appointment(school, _make_counselor(school, "c8@school.edu"), _make_student(school))
        resp = _auth(api, admin).patch(f"{APPOINTMENTS_URL}{appt.id}/", {"notes": "Session notes"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        appt.refresh_from_db()
        assert appt.notes == "Session notes"

    def test_complete_action(self, api, school, admin, db):
        appt = _make_appointment(school, _make_counselor(school, "c9@school.edu"), _make_student(school))
        resp = _auth(api, admin).post(f"{APPOINTMENTS_URL}{appt.id}/complete/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        appt.refresh_from_db()
        assert appt.status == CounselingAppointment.Status.COMPLETED

    def test_cancel_action(self, api, school, admin, db):
        appt = _make_appointment(school, _make_counselor(school, "c10@school.edu"), _make_student(school))
        resp = _auth(api, admin).post(f"{APPOINTMENTS_URL}{appt.id}/cancel/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        appt.refresh_from_db()
        assert appt.status == CounselingAppointment.Status.CANCELLED

    def test_no_show_action(self, api, school, admin, db):
        appt = _make_appointment(school, _make_counselor(school, "c11@school.edu"), _make_student(school))
        resp = _auth(api, admin).post(f"{APPOINTMENTS_URL}{appt.id}/no_show/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        appt.refresh_from_db()
        assert appt.status == CounselingAppointment.Status.NO_SHOW


# ===== Referrals: list / retrieve / isolation =====


class TestReferralList:
    def test_admin_sees_school_referrals(self, api, school, admin, db):
        _make_referral(school, _make_student(school), admin)
        resp = _auth(api, admin).get(REFERRALS_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["count"] == 1

    def test_list_excludes_other_school(self, api, school, admin, db):
        _make_referral(school, _make_student(school), admin)
        other_school = SchoolFactory()
        other_admin = AdminUserFactory(school=other_school)
        _make_referral(other_school, _make_student(other_school), other_admin)
        resp = _auth(api, admin).get(REFERRALS_URL)
        assert resp.json()["count"] == 1

    def test_teacher_sees_only_own_referrals(self, api, school, teacher, db):
        _make_referral(school, _make_student(school), teacher)
        other_teacher = TeacherUserFactory(school=school, email="other-teacher@school.edu")
        _make_referral(school, _make_student(school), other_teacher)
        resp = _auth(api, teacher).get(REFERRALS_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["count"] == 1

    def test_retrieve_other_school_404(self, api, school, admin, db):
        other_school = SchoolFactory()
        other_admin = AdminUserFactory(school=other_school)
        foreign_ref = _make_referral(other_school, _make_student(other_school), other_admin)
        resp = _auth(api, admin).get(f"{REFERRALS_URL}{foreign_ref.id}/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ===== Referrals: PATCH + workflow actions =====


class TestReferralWorkflow:
    def test_patch_updates_fields(self, api, school, admin, db):
        referral = _make_referral(school, _make_student(school), admin)
        resp = _auth(api, admin).patch(f"{REFERRALS_URL}{referral.id}/", {"priority": "high"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        referral.refresh_from_db()
        assert referral.priority == StudentReferral.Priority.HIGH

    def test_assign_sets_counselor_and_under_review(self, api, school, admin, db):
        referral = _make_referral(school, _make_student(school), admin)
        counselor = _make_counselor(school, "assignee@school.edu")
        resp = _auth(api, admin).post(
            f"{REFERRALS_URL}{referral.id}/assign/", {"assigned_to": str(counselor.id)}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK
        referral.refresh_from_db()
        assert referral.assigned_to == counselor
        assert referral.status == StudentReferral.Status.UNDER_REVIEW

    def test_assign_foreign_school_counselor_404(self, api, school, admin, db):
        referral = _make_referral(school, _make_student(school), admin)
        other_school = SchoolFactory()
        foreign_counselor = _make_counselor(other_school, "foreign@school.edu")
        resp = _auth(api, admin).post(
            f"{REFERRALS_URL}{referral.id}/assign/", {"assigned_to": str(foreign_counselor.id)}, format="json"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        referral.refresh_from_db()
        assert referral.assigned_to is None

    def test_action_taken_records_outcome(self, api, school, admin, db):
        referral = _make_referral(school, _make_student(school), admin)
        resp = _auth(api, admin).post(
            f"{REFERRALS_URL}{referral.id}/action_taken/",
            {"outcome": "Counselor provided study strategies."},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        referral.refresh_from_db()
        assert referral.status == StudentReferral.Status.ACTIONED
        assert referral.outcome == "Counselor provided study strategies."

    def test_close_action(self, api, school, admin, db):
        referral = _make_referral(school, _make_student(school), admin)
        resp = _auth(api, admin).post(f"{REFERRALS_URL}{referral.id}/close/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        referral.refresh_from_db()
        assert referral.status == StudentReferral.Status.CLOSED

    def test_reopen_action(self, api, school, admin, db):
        referral = _make_referral(school, _make_student(school), admin, status=StudentReferral.Status.CLOSED)
        resp = _auth(api, admin).post(f"{REFERRALS_URL}{referral.id}/reopen/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        referral.refresh_from_db()
        assert referral.status == StudentReferral.Status.UNDER_REVIEW


# ===== Referral create validation (serializer-level; API create is bugged) =====


class TestReferralCreateValidation:
    def test_reason_must_be_at_least_10_chars(self, db):
        from services.counseling.serializers import StudentReferralCreateUpdateSerializer

        pupil = _make_student(SchoolFactory())
        serializer = StudentReferralCreateUpdateSerializer(data={"student": str(pupil.id), "reason": "short"})
        assert not serializer.is_valid()
        assert "Reason must be at least 10 characters." in str(serializer.errors["reason"])


# ===== Dashboard stats =====


class TestDashboardStats:
    def test_student_forbidden(self, api, school, student, db):
        resp = _auth(api, student).get(DASHBOARD_URL)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_allowed(self, api, school, admin, db):
        resp = _auth(api, admin).get(DASHBOARD_URL)
        assert resp.status_code == status.HTTP_200_OK
        for key in (
            "today_appointments",
            "upcoming_appointments",
            "appointments_completed",
            "pending_referrals",
            "urgent_referrals",
            "referrals_resolved",
            "total_appointments",
            "total_referrals",
        ):
            assert key in resp.json()

    def test_counselor_counts_only_own_appointments(self, api, school, admin, db):
        counselor = _make_counselor(school, "dash-counselor@school.edu")
        other = _make_counselor(school, "dash-other@school.edu")
        _make_appointment(school, counselor, _make_student(school))
        _make_appointment(school, counselor, _make_student(school))
        _make_appointment(school, other, _make_student(school))
        resp = _auth(api, counselor).get(DASHBOARD_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total_appointments"] == 2


# ===== Counselor profile =====


class TestCounselorProfile:
    def test_get_returns_or_creates_profile(self, api, school, admin, db):
        resp = _auth(api, admin).get(PROFILE_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["user"] == str(admin.id)

    def test_patch_updates_bio(self, api, school, admin, db):
        CounselorProfile.objects.create(school=school, user=admin)
        resp = _auth(api, admin).patch(PROFILE_URL, {"bio": "Lead counselor."}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        admin.refresh_from_db()
        assert admin.counselor_profile.bio == "Lead counselor."

    def test_profiles_are_per_user(self, api, school, admin, db):
        other = AdminUserFactory(school=school, email="second-admin@school.edu")
        CounselorProfile.objects.create(school=school, user=admin, bio="Admin bio")
        CounselorProfile.objects.create(school=school, user=other, bio="Other bio")
        resp = _auth(api, admin).get(PROFILE_URL)
        assert resp.json()["bio"] == "Admin bio"
