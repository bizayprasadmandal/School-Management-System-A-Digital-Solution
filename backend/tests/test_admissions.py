"""Tests for Admissions Service — intakes, applications, documents, reviews."""

from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

ADMISSIONS_INTAKES = f"{API_PREFIX}/admissions/intakes/"
ADMISSIONS_APPLICATIONS = f"{API_PREFIX}/admissions/applications/"
ADMISSIONS_REVIEWS = f"{API_PREFIX}/admissions/reviews/"


# ─── Fixtures ─────────────────────────────────────────────────────────────────


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
def intake(db, school):
    from services.admissions.models import EnrollmentIntake

    return EnrollmentIntake.objects.create(
        school=school,
        name="Fall 2025",
        application_start=date(2025, 1, 1),
        application_end=date(2025, 6, 30),
        status="open",
    )


@pytest.fixture
def app_payload(intake):
    return {
        "intake": intake.id,
        "first_name": "Alice",
        "last_name": "Smith",
        "date_of_birth": "2012-03-15",
        "gender": "female",
        "email": "alice@example.com",
        "phone": "+1234567890",
        "applying_for_grade": "5",
    }


# ─── EnrollmentIntake Tests ───────────────────────────────────────────────────


@pytest.mark.django_db
class TestEnrollmentIntakes:

    def test_admin_can_create_intake(self, admin_client, school):
        payload = {
            "name": "Spring 2026",
            "application_start": "2026-01-01",
            "application_end": "2026-06-30",
            "status": "upcoming",
        }
        r = admin_client.post(ADMISSIONS_INTAKES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Spring 2026"

    def test_student_cannot_create_intake(self, student_client):
        payload = {"name": "Test Intake"}
        r = student_client.post(ADMISSIONS_INTAKES, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_intakes(self, admin_client, intake):
        r = admin_client.get(ADMISSIONS_INTAKES)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_intake_counts_applications(self, admin_client, intake):
        from services.admissions.models import Application

        Application.objects.create(
            school=intake.school,
            intake=intake,
            application_number="APP-TEST-001",
            first_name="John",
            last_name="Doe",
            date_of_birth=date(2010, 1, 1),
            gender="male",
            email="john@example.com",
            phone="+1234",
            applying_for_grade="6",
            status="submitted",
        )
        r = admin_client.get(f"{ADMISSIONS_INTAKES}{intake.id}/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["application_count"] == 1

    def test_tenant_isolation_intake(self, db):
        from services.admissions.models import EnrollmentIntake
        from tests.factories import AdminUserFactory, SchoolFactory

        school_a = SchoolFactory(code="ADMA")
        school_b = SchoolFactory(code="ADMB")
        admin_a = AdminUserFactory(school=school_a)
        EnrollmentIntake.objects.create(
            school=school_b,
            name="B Only",
            application_start=date.today(),
            application_end=date(2025, 12, 31),
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(ADMISSIONS_INTAKES)
        names = [i["name"] for i in r.data["results"]]
        assert "B Only" not in names


# ─── Application Tests ────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestApplications:

    def test_create_application(self, admin_client, app_payload):
        r = admin_client.post(ADMISSIONS_APPLICATIONS, app_payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["status"] == "draft"
        assert r.data["application_number"]  # auto-generated

    def test_application_defaults_to_draft(self, admin_client, app_payload):
        r = admin_client.post(ADMISSIONS_APPLICATIONS, app_payload, format="json")
        assert r.data["status"] == "draft"

    def test_list_applications(self, admin_client, intake, app_payload):
        admin_client.post(ADMISSIONS_APPLICATIONS, app_payload, format="json")
        r = admin_client.get(ADMISSIONS_APPLICATIONS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_filter_application_by_status(self, admin_client, intake, app_payload):
        admin_client.post(ADMISSIONS_APPLICATIONS, app_payload, format="json")
        r = admin_client.get(f"{ADMISSIONS_APPLICATIONS}?status=draft")
        assert r.status_code == status.HTTP_200_OK
        for a in r.data["results"]:
            assert a["status"] == "draft"

    def test_application_submit_action(self, admin_client, intake, app_payload):
        created = admin_client.post(ADMISSIONS_APPLICATIONS, app_payload, format="json")
        assert created.status_code == status.HTTP_201_CREATED
        app_id = created.data["id"]
        r = admin_client.post(f"{ADMISSIONS_APPLICATIONS}{app_id}/submit/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["status"] == "submitted"
        assert r.data["submitted_at"] is not None

    def test_update_status_action(self, admin_client, intake, app_payload):
        from services.admissions.models import Application

        app = Application.objects.create(
            school=intake.school,
            intake=intake,
            application_number="APP-TEST-002",
            first_name="Frank",
            last_name="Green",
            date_of_birth=date(2010, 11, 5),
            gender="male",
            email="frank@example.com",
            phone="+1234",
            applying_for_grade="6",
            status="submitted",
        )
        # Follow the valid pipeline: submitted → under_review → shortlisted → accepted
        for target in ["under_review", "shortlisted", "accepted"]:
            r = admin_client.post(
                f"{ADMISSIONS_APPLICATIONS}{app.id}/update-status/",
                {"status": target, "review_notes": f"Moved to {target}"},
                format="json",
            )
            assert r.status_code == status.HTTP_200_OK, f"Failed to transition to {target}: {r.data}"
        app.refresh_from_db()
        assert app.status == "accepted"
        assert app.review_notes == "Moved to accepted"

    def test_non_admin_cannot_update_status(self, teacher_client, intake, app_payload):
        from services.admissions.models import Application

        app = Application.objects.create(
            school=intake.school,
            intake=intake,
            application_number="APP-TEST-003",
            first_name="Grace",
            last_name="Hill",
            date_of_birth=date(2010, 4, 20),
            gender="female",
            email="grace@example.com",
            phone="+1234",
            applying_for_grade="6",
            status="submitted",
        )
        r = teacher_client.post(
            f"{ADMISSIONS_APPLICATIONS}{app.id}/update-status/",
            {"status": "accepted"},
            format="json",
        )
        assert r.status_code == status.HTTP_403_FORBIDDEN


# ─── ApplicationReview Tests ──────────────────────────────────────────────────


@pytest.mark.django_db
class TestApplicationReviews:

    def test_create_review(self, admin_client, intake):
        from services.admissions.models import Application

        app = Application.objects.create(
            school=intake.school,
            intake=intake,
            application_number="APP-TEST-004",
            first_name="Henry",
            last_name="Irwin",
            date_of_birth=date(2010, 9, 12),
            gender="male",
            email="henry@example.com",
            phone="+1234",
            applying_for_grade="6",
            status="under_review",
        )
        payload = {
            "application": app.id,
            "score": 85,
            "recommendation": "Strongly Recommend",
            "notes": "Strong candidate",
        }
        r = admin_client.post(ADMISSIONS_REVIEWS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["reviewer_name"] is not None

    def test_review_requires_valid_application(self, admin_client):
        payload = {
            "application": 9999,
            "score": 50,
        }
        r = admin_client.post(ADMISSIONS_REVIEWS, payload, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
