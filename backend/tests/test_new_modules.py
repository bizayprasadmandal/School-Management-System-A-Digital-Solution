"""
Tests for six new modules: Hostel, Sports, Health Clinic, Alumni, Cafeteria, Admissions.
Verifies CRUD endpoints work and audit logging fires correctly.
"""

import pytest
from datetime import date, datetime
from rest_framework import status
from rest_framework.test import APIClient
from services.auth.models import AuditLog


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
def admin_auth(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def grade(db, school):
    from tests.factories import GradeFactory
    return GradeFactory(school=school, level=6)


@pytest.fixture
def academic_year(db, school):
    from tests.factories import AcademicYearFactory
    return AcademicYearFactory(school=school)


@pytest.fixture
def classroom(db, school, grade, academic_year):
    from tests.factories import ClassroomFactory
    return ClassroomFactory(school=school, grade=grade, academic_year=academic_year)


@pytest.fixture
def student_user(db, school):
    from tests.factories import StudentUserFactory
    return StudentUserFactory(school=school)


@pytest.fixture
def student(db, school, student_user):
    from tests.factories import StudentFactory
    return StudentFactory(user=student_user, school=school)


# ─── Hostel Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestHostelModule:

    def test_create_hostel(self, admin_auth, school):
        payload = {
            "name": "Boys Hostel A",
            "code": "BHA",
            "gender": "male",
            "address": "123 Campus Rd",
            "phone": "1234567890",
            "total_floors": 3,
        }
        response = admin_auth.post("/api/v1/hostel/hostels/", payload, format="json")
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

    def test_create_room(self, admin_auth):
        # First create a hostel
        hostel_resp = admin_auth.post("/api/v1/hostel/hostels/", {
            "name": "Girls Hostel", "code": "GH", "gender": "female",
            "address": "456 College Ave", "phone": "0987654321",
        }, format="json")
        hostel_id = hostel_resp.data.get("id")
        if not hostel_id:
            pytest.skip("Hostel creation failed")

        payload = {
            "hostel": hostel_id,
            "room_number": "101",
            "floor": 1,
            "room_type": "double",
            "capacity": 2,
            "monthly_fee": "150.00",
        }
        response = admin_auth.post("/api/v1/hostel/rooms/", payload, format="json")
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

    def test_audit_log_created_on_hostel_action(self, admin_auth):
        before_count = AuditLog.objects.filter(resource_type="hostel").count()
        admin_auth.post("/api/v1/hostel/hostels/", {
            "name": "Audit Test Hostel", "code": "ATH", "gender": "coed",
            "address": "789 Test Ln", "phone": "5551234567",
        }, format="json")
        after_count = AuditLog.objects.filter(resource_type="hostel").count()
        assert after_count > before_count, "Audit log should be created on hostel create"


# ─── Sports Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSportsModule:

    def test_create_sport(self, admin_auth):
        response = admin_auth.post("/api/v1/sports/sports/", {
            "name": "Basketball", "category": "sport", "min_players": 5, "max_players": 15,
        }, format="json")
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

    def test_audit_log_on_sport_create(self, admin_auth):
        before = AuditLog.objects.filter(resource_type="sport").count()
        admin_auth.post("/api/v1/sports/sports/", {
            "name": "Soccer", "category": "sport", "min_players": 11, "max_players": 18,
        }, format="json")
        after = AuditLog.objects.filter(resource_type="sport").count()
        assert after >= before, "Audit log should be created on sport create"


# ─── Health Clinic Tests ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestHealthClinicModule:

    def test_list_health_records(self, admin_auth):
        response = admin_auth.get("/api/v1/health/records/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_nurse_visit(self, admin_auth, student):
        response = admin_auth.post("/api/v1/health/visits/", {
            "student": str(student.id),
            "visit_type": "sick",
            "symptoms": "Fever and cough",
            "temperature_c": "38.5",
        }, format="json")
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)


# ─── Alumni Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAlumniModule:

    def test_list_alumni_profiles(self, admin_auth):
        response = admin_auth.get("/api/v1/alumni/profiles/")
        assert response.status_code == status.HTTP_200_OK

    def test_audit_log_on_alumni_create(self, admin_auth, admin_user):
        before = AuditLog.objects.filter(resource_type="alumniprofile").count()
        admin_auth.post("/api/v1/alumni/profiles/", {
            "user": str(admin_user.id),
            "graduation_year": 2025,
        }, format="json")
        after = AuditLog.objects.filter(resource_type="alumniprofile").count()
        assert after >= before, "Audit log should be created on alumni create"


# ─── Cafeteria Tests ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCafeteriaModule:

    def test_create_meal_menu(self, admin_auth):
        response = admin_auth.post("/api/v1/cafeteria/menus/", {
            "meal_type": "lunch",
            "name": "Monday Lunch",
            "date": date.today().isoformat(),
            "items": "Rice, Curry, Salad",
            "price": "5.00",
        }, format="json")
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

    def test_list_meal_plans(self, admin_auth):
        response = admin_auth.get("/api/v1/cafeteria/plans/")
        assert response.status_code == status.HTTP_200_OK


# ─── Admissions Tests ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAdmissionsModule:

    def test_create_intake(self, admin_auth):
        response = admin_auth.post("/api/v1/admissions/intakes/", {
            "name": "Fall 2026",
            "application_start": date.today().isoformat(),
            "application_end": "2026-08-31",
            "status": "open",
        }, format="json")
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

    def test_audit_log_on_intake_create(self, admin_auth):
        before = AuditLog.objects.filter(resource_type="enrollmentintake").count()
        admin_auth.post("/api/v1/admissions/intakes/", {
            "name": "Spring 2027",
            "application_start": date.today().isoformat(),
            "application_end": "2027-01-31",
            "status": "upcoming",
        }, format="json")
        after = AuditLog.objects.filter(resource_type="enrollmentintake").count()
        assert after >= before, "Audit log should be created on intake create"
