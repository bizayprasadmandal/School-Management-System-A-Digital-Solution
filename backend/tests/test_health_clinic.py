"""Tests for Health Clinic Service — HealthRecord, NurseVisit, Immunization, MedicationLog."""

from datetime import date, datetime, timezone

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

HEALTH_RECORDS = f"{API_PREFIX}/health/records/"
HEALTH_VISITS = f"{API_PREFIX}/health/visits/"
HEALTH_IMMUNIZATIONS = f"{API_PREFIX}/health/immunizations/"
HEALTH_MEDICATIONS = f"{API_PREFIX}/health/medication-logs/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory

    return AdminUserFactory(school=school)


@pytest.fixture
def nurse(db, school):
    from tests.factories import TeacherUserFactory

    return TeacherUserFactory(school=school)


@pytest.fixture
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


@pytest.fixture
def nurse_client(db, nurse):
    c = APIClient()
    c.force_authenticate(user=nurse)
    return c


@pytest.mark.django_db
class TestHealthRecords:

    def test_create_health_record(self, admin_client, school):
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "blood_type": "O+",
            "allergies": "Penicillin",
            "chronic_conditions": "Asthma",
            "emergency_contact_name": "Jane Doe",
            "emergency_contact_phone": "+1234567890",
        }
        r = admin_client.post(HEALTH_RECORDS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["blood_type"] == "O+"

    def test_list_records(self, admin_client, school):
        from services.health_clinic.models import HealthRecord
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        HealthRecord.objects.create(
            school=school,
            student=pupil,
            blood_type="A+",
            chronic_conditions="None",
        )
        r = admin_client.get(HEALTH_RECORDS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_tenant_isolation(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory, StudentFactory

        school_a = SchoolFactory(code="HLTA")
        school_b = SchoolFactory(code="HLTB")
        admin_a = AdminUserFactory(school=school_a)
        pupil_b = StudentFactory(school=school_b)
        from services.health_clinic.models import HealthRecord

        HealthRecord.objects.create(
            school=school_b,
            student=pupil_b,
            blood_type="B-",
            chronic_conditions="Diabetes",
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(HEALTH_RECORDS)
        assert r.data["count"] == 0


@pytest.mark.django_db
class TestNurseVisits:

    def test_create_visit(self, admin_client, school):
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "visit_type": "sick",
            "symptoms": "Headache, fever",
            "diagnosis": "Common cold",
            "treatment": "Rest and hydration",
            "temperature_c": "38.5",
        }
        r = admin_client.post(HEALTH_VISITS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert "fever" in r.data["symptoms"]

    def test_list_visits(self, admin_client, school, admin):
        from services.health_clinic.models import NurseVisit
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        NurseVisit.objects.create(
            school=school,
            student=pupil,
            visit_type="sick",
            symptoms="Cough",
            diagnosis="Allergies",
            treated_by=admin,
        )
        r = admin_client.get(HEALTH_VISITS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestImmunizations:

    def test_create_immunization(self, admin_client, school):
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "vaccine_name": "MMR",
            "date_administered": date.today().isoformat(),
            "dose_number": 2,
            "administered_by": "School Nurse",
        }
        r = admin_client.post(HEALTH_IMMUNIZATIONS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["vaccine_name"] == "MMR"

    def test_list_immunizations(self, admin_client, school):
        from services.health_clinic.models import Immunization
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        Immunization.objects.create(
            student=pupil,
            vaccine_name="Hepatitis B",
            date_administered=date.today(),
            dose_number=1,
            administered_by="Nurse",
        )
        r = admin_client.get(HEALTH_IMMUNIZATIONS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestMedicationLogs:

    def test_create_medication_log(self, admin_client, school):
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "medication_name": "Amoxicillin",
            "dosage": "500mg",
            "route": "Oral",
            "time_administered": datetime.now(timezone.utc).isoformat(),
        }
        r = admin_client.post(HEALTH_MEDICATIONS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["medication_name"] == "Amoxicillin"

    def test_list_medications(self, admin_client, school):
        from services.health_clinic.models import MedicationLog
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        MedicationLog.objects.create(
            student=pupil,
            medication_name="Ibuprofen",
            dosage="200mg",
            time_administered=datetime.now(timezone.utc),
        )
        r = admin_client.get(HEALTH_MEDICATIONS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1
