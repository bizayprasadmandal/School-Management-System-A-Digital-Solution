"""Tests for Behavior Service — Incident, Referral."""

import pytest
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
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "incident_type": "disruptive_behavior",
            "description": "Talking during class",
            "location": "Classroom 3A",
            "severity": "low",
        }
        r = teacher_client.post(BEHAVIOR_INCIDENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["severity"] == "low"

    def test_student_cannot_report_incident(self, student_client):
        payload = {
            "student": 9999,
            "incident_type": "other",
            "description": "Test",
            "severity": "low",
        }
        r = student_client.post(BEHAVIOR_INCIDENTS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_incidents(self, admin_client, school):
        from services.behavior.models import Incident
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        Incident.objects.create(
            school=school,
            student=pupil,
            incident_type="bullying",
            description="Verbal altercation",
            severity="medium",
            reported_by=admin_client.handler._force_user,
        )
        r = admin_client.get(BEHAVIOR_INCIDENTS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_filter_by_severity(self, admin_client, school):
        from services.behavior.models import Incident
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        Incident.objects.create(
            school=school,
            student=pupil,
            incident_type="other",
            description="Minor issue",
            severity="low",
            reported_by=admin_client.handler._force_user,
        )
        r = admin_client.get(f"{BEHAVIOR_INCIDENTS}?severity=low")
        assert r.status_code == status.HTTP_200_OK
        for i in r.data["results"]:
            assert i["severity"] == "low"

    def test_tenant_isolation(self, db):
        from services.behavior.models import Incident
        from tests.factories import AdminUserFactory, SchoolFactory, StudentFactory

        school_a = SchoolFactory(code="BEHA")
        school_b = SchoolFactory(code="BEHB")
        admin_a = AdminUserFactory(school=school_a)
        pupil_b = StudentFactory(school=school_b)
        Incident.objects.create(
            school=school_b,
            student=pupil_b,
            incident_type="cheating",
            description="Caught cheating",
            severity="high",
            reported_by=admin_a,
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(BEHAVIOR_INCIDENTS)
        assert r.data["count"] == 0


@pytest.mark.django_db
class TestReferrals:

    def test_create_referral(self, admin_client, school):
        from services.behavior.models import Incident
        from tests.factories import StudentFactory, TeacherUserFactory

        pupil = StudentFactory(school=school)
        counselor = TeacherUserFactory(school=school)
        incident = Incident.objects.create(
            school=school,
            student=pupil,
            incident_type="counseling",
            description="Needs academic support",
            severity="low",
            reported_by=admin_client.handler._force_user,
        )
        payload = {
            "incident": incident.id,
            "reason": "Needs academic support",
            "referred_to": counselor.id,
        }
        r = admin_client.post(BEHAVIOR_REFERRALS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_list_referrals(self, admin_client, school):
        from services.behavior.models import Incident, Referral
        from tests.factories import StudentFactory, TeacherUserFactory

        pupil = StudentFactory(school=school)
        counselor = TeacherUserFactory(school=school)
        incident = Incident.objects.create(
            school=school,
            student=pupil,
            incident_type="counseling",
            description="Behavioral concern",
            severity="low",
            reported_by=admin_client.handler._force_user,
        )
        Referral.objects.create(
            incident=incident,
            referred_to=counselor,
            referred_by=admin_client.handler._force_user,
            reason="Behavioral support",
        )
        r = admin_client.get(BEHAVIOR_REFERRALS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1
