"""Tests for Alumni Service — AlumniProfile, AlumniEvent, AlumniDonation, AlumniChapter."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

ALUMNI_PROFILES = f"{API_PREFIX}/alumni/profiles/"
ALUMNI_EVENTS = f"{API_PREFIX}/alumni/events/"
ALUMNI_DONATIONS = f"{API_PREFIX}/alumni/donations/"
ALUMNI_CHAPTERS = f"{API_PREFIX}/alumni/chapters/"


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
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


@pytest.fixture
def teacher_client(db, teacher):
    c = APIClient()
    c.force_authenticate(user=teacher)
    return c


@pytest.mark.django_db
class TestAlumniProfiles:

    @pytest.fixture
    def user(self, school):
        from tests.factories import UserFactory

        return UserFactory(school=school)

    def test_create_alumni_profile(self, admin_client, school, user):
        payload = {
            "user": user.id,
            "graduation_year": 2020,
            "occupation": "Software Engineer",
            "employer": "Tech Corp",
        }
        r = admin_client.post(ALUMNI_PROFILES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["graduation_year"] == 2020
        assert r.data["user_name"] == user.full_name

    def test_list_profiles(self, admin_client, school, user):
        from services.alumni.models import AlumniProfile

        AlumniProfile.objects.create(
            school=school,
            user=user,
            graduation_year=2021,
        )
        r = admin_client.get(ALUMNI_PROFILES)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_search_by_name(self, admin_client, school):
        from services.alumni.models import AlumniProfile
        from tests.factories import UserFactory

        alice = UserFactory(school=school, first_name="Alice", last_name="Johnson")
        AlumniProfile.objects.create(
            school=school,
            user=alice,
            graduation_year=2022,
        )
        r = admin_client.get(f"{ALUMNI_PROFILES}?search=Alice")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_tenant_isolation(self, db):
        from services.alumni.models import AlumniProfile
        from tests.factories import AdminUserFactory, SchoolFactory, UserFactory

        school_a = SchoolFactory(code="ALMA")
        school_b = SchoolFactory(code="ALMB")
        admin_a = AdminUserFactory(school=school_a)
        bob = UserFactory(school=school_b, email="bob@secret.com")
        AlumniProfile.objects.create(
            school=school_b,
            user=bob,
            graduation_year=2020,
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(ALUMNI_PROFILES)
        emails = [p["user_email"] for p in r.data["results"]]
        assert "bob@secret.com" not in emails


@pytest.mark.django_db
class TestAlumniEvents:

    def test_create_event(self, admin_client, school):
        payload = {
            "title": "Homecoming 2025",
            "description": "Annual homecoming event",
            "event_date": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat(),
            "location": "School Auditorium",
            "status": "published",
        }
        r = admin_client.post(ALUMNI_EVENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["title"] == "Homecoming 2025"

    def test_student_cannot_create_event(self, db, school):
        from tests.factories import StudentUserFactory

        client = APIClient()
        client.force_authenticate(user=StudentUserFactory(school=school))
        payload = {"title": "Test", "event_date": datetime.now(timezone.utc).isoformat()}
        r = client.post(ALUMNI_EVENTS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAlumniDonations:

    @pytest.fixture
    def profile(self, school):
        from services.alumni.models import AlumniProfile
        from tests.factories import UserFactory

        donor = UserFactory(school=school, first_name="Donor", last_name="Adams")
        return AlumniProfile.objects.create(
            school=school,
            user=donor,
            graduation_year=2019,
        )

    def test_record_donation(self, admin_client, school, profile):
        payload = {
            "alumni": profile.id,
            "amount": "500.00",
            "fund_type": "scholarship",
            "payment_method": "bank_transfer",
        }
        r = admin_client.post(ALUMNI_DONATIONS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["amount"] == "500.00"

    def test_donation_list(self, admin_client, school, profile):
        from services.alumni.models import AlumniDonation

        AlumniDonation.objects.create(
            school=school,
            alumni=profile,
            amount=Decimal("250.00"),
            fund_type="infrastructure",
        )
        r = admin_client.get(ALUMNI_DONATIONS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestAlumniChapters:

    def test_create_chapter(self, admin_client, school):
        payload = {
            "name": "New York Chapter",
            "city": "New York",
            "country": "USA",
            "description": "For alumni in the NYC area",
        }
        r = admin_client.post(ALUMNI_CHAPTERS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "New York Chapter"

    def test_chapter_list_filter_by_city(self, admin_client, school):
        from services.alumni.models import AlumniChapter

        AlumniChapter.objects.create(
            school=school,
            name="LA Chapter",
            city="Los Angeles",
            country="USA",
        )
        r = admin_client.get(f"{ALUMNI_CHAPTERS}?search=Los Angeles")
        assert r.status_code == status.HTTP_200_OK
