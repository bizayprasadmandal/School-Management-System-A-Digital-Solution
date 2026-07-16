"""Tests for Behavior Service — Incident, Referral."""

import pytest
from datetime import date
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

BEHAVIOR_INCIDENTS = f"{API_PREFIX}/behavior/incidents/"
BEHAVIOR_REFERRALS = f"{API_PREFIX}/behavior/referrals/"


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
def student(db, school):
    from tests.factories import StudentUserFactory
    return StudentUserFactory(school=school)


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
def student_client(db, student):
    c = APIClient()
    c.force_authenticate(user=student)
    return c


@pytest.mark.django_db
class TestIncidents:

    def test_teacher_can_report_incident(self, teacher_client, school):
        from tests.factories import StudentFactory, StudentUserFactory
        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "incident_type": "disruptive_behavior",
            "description": "Talking during class",
            "location": "Classroom 3A",
            "severity": "minor",
        }
        r = teacher_client.post(BEHAVIOR_INCIDENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["severity"] == "minor"

    def test_student_cannot_report_incident(self, student_client):
        payload = {
            "student": 9999, "incident_type": "other",
            "description": "Test", "severity": "minor",
        }
        r = student_client.post(BEHAVIOR_INCIDENTS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_incidents(self, admin_client, school):
        from tests.factories import StudentFactory
        from services.behavior.models import Incident
        pupil = StudentFactory(school=school)
        Incident.objects.create(
            school=school, student=pupil,
            incident_type="bullying", description="Verbal altercation",
            severity="moderate", reported_by=admin_client.handler._force_user,
        )
        r = admin_client.get(BEHAVIOR_INCIDENTS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_filter_by_severity(self, admin_client, school):
        from tests.factories import StudentFactory
        from services.behavior.models import Incident
        pupil = StudentFactory(school=school)
        Incident.objects.create(
            school=school, student=pupil,
            incident_type="other", description="Minor issue",
            severity="minor", reported_by=admin_client.handler._force_user,
        )
        r = admin_client.get(f"{BEHAVIOR_INCIDENTS}?severity=minor")
        assert r.status_code == status.HTTP_200_OK
        for i in r.data["results"]:
            assert i["severity"] == "minor"

    def test_tenant_isolation(self, db):
        from tests.factories import SchoolFactory, AdminUserFactory, StudentFactory
        from services.behavior.models import Incident
        school_a = SchoolFactory(code="BEHA")
        school_b = SchoolFactory(code="BEHB")
        admin_a = AdminUserFactory(school=school_a)
        pupil_b = StudentFactory(school=school_b)
        Incident.objects.create(
            school=school_b, student=pupil_b,
            incident_type="cheating", description="Caught cheating",
            severity="major", reported_by=admin_a,
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(BEHAVIOR_INCIDENTS)
        assert r.data["count"] == 0


@pytest.mark.django_db
class TestReferrals:

    def test_create_referral(self, admin_client, school):
        from tests.factories import StudentFactory
        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "referral_type": "counseling",
            "reason": "Needs academic support",
            "referred_to": "School Counselor",
        }
        r = admin_client.post(BEHAVIOR_REFERRALS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_list_referrals(self, admin_client, school):
        from tests.factories import StudentFactory
        from services.behavior.models import Referral
        pupil = StudentFactory(school=school)
        Referral.objects.create(
            school=school, student=pupil,
            referral_type="counseling", reason="Behavioral support",
            referred_to="Guidance Office",
            referred_by=admin_client.handler._force_user,
        )
        r = admin_client.get(BEHAVIOR_REFERRALS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1
