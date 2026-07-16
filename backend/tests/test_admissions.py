"""Tests for Admissions Service — EnrollmentIntake, Application, ApplicationDocument, ApplicationReview."""

import pytest
from datetime import date
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
        start_date=date(2025, 1, 1),
        end_date=date(2025, 6, 30),
        total_seats=100,
        available_seats=100,
        is_open=True,
    )


# ─── EnrollmentIntake Tests ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestEnrollmentIntakes:

    def test_admin_can_create_intake(self, admin_client, school):
        payload = {
            "name": "Spring 2026", "total_seats": 80,
            "start_date": "2026-01-01", "end_date": "2026-06-30",
            "is_open": True,
        }
        r = admin_client.post(ADMISSIONS_INTAKES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Spring 2026"

    def test_student_cannot_create_intake(self, student_client):
        payload = {"name": "Test Intake", "total_seats": 50}
        r = student_client.post(ADMISSIONS_INTAKES, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_intakes(self, admin_client, intake):
        r = admin_client.get(ADMISSIONS_INTAKES)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_intake_available_seats_decrements(self, admin_client, intake, school):
        from services.admissions.models import Application
        student = Application.objects.create(
            intake=intake,
            first_name="John", last_name="Doe",
            email="john@example.com",
            date_of_birth=date(2010, 1, 1),
            status="admitted",
        )
        intake.refresh_from_db()
        assert intake.available_seats == 99
        assert intake.filled_seats == 1

    def test_intake_closed_when_full(self, admin_client, intake, school):
        intake.available_seats = 0
        intake.save()
        from services.admissions.models import Application
        r = admin_client.post(
            f"{ADMISSIONS_APPLICATIONS}",
            {
                "intake": intake.id,
                "first_name": "Jane", "last_name": "Doe",
                "email": "jane@example.com",
                "date_of_birth": "2010-01-01",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_tenant_isolation_intake(self, db):
        from tests.factories import SchoolFactory, AdminUserFactory
        from services.admissions.models import EnrollmentIntake
        school_a = SchoolFactory(code="ADMA")
        school_b = SchoolFactory(code="ADMB")
        admin_a = AdminUserFactory(school=school_a)
        EnrollmentIntake.objects.create(
            school=school_b, name="B Only",
            start_date=date.today(), end_date=date(2025, 12, 31),
            total_seats=50, available_seats=50,
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(ADMISSIONS_INTAKES)
        names = [i["name"] for i in r.data["results"]]
        assert "B Only" not in names


# ─── Application Tests ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestApplications:

    def test_create_application(self, admin_client, intake):
        payload = {
            "intake": intake.id,
            "first_name": "Alice", "last_name": "Smith",
            "email": "alice@example.com",
            "date_of_birth": "2012-03-15",
            "phone": "+1234567890",
        }
        r = admin_client.post(ADMISSIONS_APPLICATIONS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["status"] == "pending"

    def test_application_defaults_to_pending(self, admin_client, intake):
        payload = {
            "intake": intake.id,
            "first_name": "Bob", "last_name": "Brown",
            "email": "bob@example.com",
            "date_of_birth": "2011-07-22",
        }
        r = admin_client.post(ADMISSIONS_APPLICATIONS, payload, format="json")
        assert r.data["status"] == "pending"

    def test_list_applications(self, admin_client, intake):
        from services.admissions.models import Application
        Application.objects.create(
            intake=intake,
            first_name="Charlie", last_name="Davis",
            email="charlie@example.com",
            date_of_birth=date(2010, 5, 10),
        )
        r = admin_client.get(ADMISSIONS_APPLICATIONS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_filter_application_by_status(self, admin_client, intake):
        from services.admissions.models import Application
        Application.objects.create(
            intake=intake,
            first_name="Diana", last_name="Evans",
            email="diana@example.com",
            date_of_birth=date(2010, 8, 15),
            status="pending",
        )
        r = admin_client.get(f"{ADMISSIONS_APPLICATIONS}?status=pending")
        assert r.status_code == status.HTTP_200_OK
        for a in r.data["results"]:
            assert a["status"] == "pending"

    def test_application_submit_action(self, admin_client, intake):
        from services.admissions.models import Application
        app = Application.objects.create(
            intake=intake,
            first_name="Eve", last_name="Fox",
            email="eve@example.com",
            date_of_birth=date(2010, 2, 28),
            status="draft",
        )
        r = admin_client.post(f"{ADMISSIONS_APPLICATIONS}{app.id}/submit/")
        assert r.status_code == status.HTTP_200_OK
        app.refresh_from_db()
        assert app.status == "pending"

    def test_update_status_action(self, admin_client, intake):
        from services.admissions.models import Application
        app = Application.objects.create(
            intake=intake,
            first_name="Frank", last_name="Green",
            email="frank@example.com",
            date_of_birth=date(2010, 11, 5),
            status="pending",
        )
        r = admin_client.post(
            f"{ADMISSIONS_APPLICATIONS}{app.id}/update-status/",
            {"status": "admitted", "remarks": "Approved"},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        app.refresh_from_db()
        assert app.status == "admitted"

    def test_non_admin_cannot_update_status(self, teacher_client, intake):
        from services.admissions.models import Application
        app = Application.objects.create(
            intake=intake,
            first_name="Grace", last_name="Hill",
            email="grace@example.com",
            date_of_birth=date(2010, 4, 20),
            status="pending",
        )
        r = teacher_client.post(
            f"{ADMISSIONS_APPLICATIONS}{app.id}/update-status/",
            {"status": "admitted"},
            format="json",
        )
        assert r.status_code == status.HTTP_403_FORBIDDEN


# ─── ApplicationReview Tests ──────────────────────────────────────────────────

@pytest.mark.django_db
class TestApplicationReviews:

    def test_create_review(self, admin_client, intake, admin):
        from services.admissions.models import Application
        app = Application.objects.create(
            intake=intake,
            first_name="Henry", last_name="Irwin",
            email="henry@example.com",
            date_of_birth=date(2010, 9, 12),
            status="reviewed",
        )
        payload = {
            "application": app.id,
            "reviewer_notes": "Strong candidate",
            "score": 85,
            "decision": "approve",
        }
        r = admin_client.post(ADMISSIONS_REVIEWS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_review_requires_valid_application(self, admin_client):
        payload = {
            "application": 9999,
            "reviewer_notes": "Test",
            "score": 50,
            "decision": "pending",
        }
        r = admin_client.post(ADMISSIONS_REVIEWS, payload, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
