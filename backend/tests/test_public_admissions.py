"""Tests for public admissions API (no authentication required)."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from services.admissions.models import Application, ApplicationTimelineEvent, EnrollmentIntake
from services.auth.models import School


class PublicAdmissionsTestBase(TestCase):
    """Shared fixtures for public admissions tests."""

    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(name="Test School", slug="test-school")

        today = timezone.now().date()
        self.open_intake = EnrollmentIntake.objects.create(
            school=self.school,
            name="Fall 2026",
            academic_year="2025-26",
            application_start=today - timedelta(days=30),
            application_end=today + timedelta(days=30),
            enrollment_date=today + timedelta(days=60),
            status="open",
            description="Fall intake for new students",
        )
        self.closed_intake = EnrollmentIntake.objects.create(
            school=self.school,
            name="Spring 2026",
            academic_year="2025-26",
            application_start=today - timedelta(days=90),
            application_end=today - timedelta(days=10),
            status="closed",
        )


class PublicIntakeListTest(PublicAdmissionsTestBase):
    """GET /api/v1/admissions/public/intakes/"""

    def test_lists_open_intakes(self):
        response = self.client.get("/api/v1/admissions/public/intakes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Fall 2026")
        self.assertEqual(response.data[0]["status"], "open")

    def test_excludes_closed_intakes(self):
        response = self.client.get("/api/v1/admissions/public/intakes/")
        names = [i["name"] for i in response.data]
        self.assertNotIn("Spring 2026", names)

    def test_does_not_require_auth(self):
        """Public endpoint should work without authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/admissions/public/intakes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_school_slug(self):
        other_school = School.objects.create(name="Other", slug="other")
        EnrollmentIntake.objects.create(
            school=other_school,
            name="Other Intake",
            application_start=timezone.now().date() - timedelta(days=10),
            application_end=timezone.now().date() + timedelta(days=10),
            status="open",
        )
        response = self.client.get("/api/v1/admissions/public/intakes/", {"school": "other"})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Other Intake")


class PublicApplicationSubmitTest(PublicAdmissionsTestBase):
    """POST /api/v1/admissions/public/apply/"""

    VALID_DATA = {
        "first_name": "Ram",
        "last_name": "Sharma",
        "date_of_birth": "2015-05-15",
        "gender": "male",
        "email": "ram@example.com",
        "phone": "+977-9841000000",
        "applying_for_grade": "Grade 6",
        "guardian_name": "Shyam Sharma",
        "guardian_phone": "+977-9841000001",
        "guardian_email": "shyam@example.com",
        "guardian_relation": "Father",
    }

    def test_submit_application_success(self):
        data = {**self.VALID_DATA, "intake": str(self.open_intake.id)}
        response = self.client.post("/api/v1/admissions/public/apply/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("application_number", response.data)
        self.assertEqual(response.data["status"], "submitted")
        self.assertTrue(response.data["application_number"].startswith("APP-"))

    def test_creates_timeline_event(self):
        data = {**self.VALID_DATA, "intake": str(self.open_intake.id)}
        self.client.post("/api/v1/admissions/public/apply/", data, format="json")
        app = Application.objects.get(application_number__startswith="APP-")
        self.assertEqual(app.timeline.count(), 1)
        self.assertEqual(app.timeline.first().stage, ApplicationTimelineEvent.Stage.SUBMITTED)

    def test_rejects_closed_intake(self):
        data = {**self.VALID_DATA, "intake": str(self.closed_intake.id)}
        response = self.client.post("/api/v1/admissions/public/apply/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_missing_required_fields(self):
        response = self.client.post("/api/v1/admissions/public/apply/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", str(response.data))

    def test_does_not_require_auth(self):
        data = {**self.VALID_DATA, "intake": str(self.open_intake.id)}
        self.client.force_authenticate(user=None)
        response = self.client.post("/api/v1/admissions/public/apply/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rejects_uniqueness_violation(self):
        data = {**self.VALID_DATA, "intake": str(self.open_intake.id)}
        self.client.post("/api/v1/admissions/public/apply/", data, format="json")
        # Submit again with same email - should still succeed (different app numbers)
        response = self.client.post("/api/v1/admissions/public/apply/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_max_applications_cap(self):
        self.open_intake.max_applications = 1
        self.open_intake.save()
        data = {**self.VALID_DATA, "intake": str(self.open_intake.id)}
        self.client.post("/api/v1/admissions/public/apply/", data, format="json")
        # Second application should fail
        data2 = {
            **self.VALID_DATA,
            "email": "other@example.com",
            "intake": str(self.open_intake.id),
        }
        response = self.client.post("/api/v1/admissions/public/apply/", data2, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PublicApplicationStatusTest(PublicAdmissionsTestBase):
    """GET /api/v1/admissions/public/status/<number>/"""

    def setUp(self):
        super().setUp()
        self.app = Application.objects.create(
            school=self.school,
            intake=self.open_intake,
            application_number="APP-202608-TEST01",
            status="submitted",
            first_name="Ram",
            last_name="Sharma",
            date_of_birth="2015-05-15",
            gender="male",
            email="ram@example.com",
            phone="+977-9841000000",
            applying_for_grade="Grade 6",
            guardian_name="Shyam Sharma",
            guardian_phone="+977-9841000001",
            guardian_email="shyam@example.com",
            guardian_relation="Father",
            submitted_at=timezone.now(),
        )

    def test_returns_application_status(self):
        response = self.client.get("/api/v1/admissions/public/status/APP-202608-TEST01/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["application_number"], "APP-202608-TEST01")
        self.assertEqual(response.data["status"], "submitted")
        self.assertEqual(response.data["first_name"], "Ram")

    def test_returns_timeline(self):
        ApplicationTimelineEvent.objects.create(
            application=self.app,
            stage=ApplicationTimelineEvent.Stage.SUBMITTED,
        )
        response = self.client.get("/api/v1/admissions/public/status/APP-202608-TEST01/")
        self.assertEqual(len(response.data["timeline"]), 1)

    def test_returns_404_for_unknown_number(self):
        response = self.client.get("/api/v1/admissions/public/status/APP-999999-XXXXXX/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_does_not_require_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/admissions/public/status/APP-202608-TEST01/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_does_not_expose_internal_fields(self):
        response = self.client.get("/api/v1/admissions/public/status/APP-202608-TEST01/")
        self.assertNotIn("school", response.data)
        self.assertNotIn("review_notes", response.data)
        self.assertNotIn("linked_student", response.data)
