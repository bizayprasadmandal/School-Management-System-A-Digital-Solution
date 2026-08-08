"""Tests for Hostel Service — Hostel, HostelRoom, HostelAllocation, HostelFee, HostelVisitor."""

from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

HOSTEL_HOSTELS = f"{API_PREFIX}/hostel/hostels/"
HOSTEL_ROOMS = f"{API_PREFIX}/hostel/rooms/"
HOSTEL_ALLOCATIONS = f"{API_PREFIX}/hostel/allocations/"
HOSTEL_FEES = f"{API_PREFIX}/hostel/fees/"
HOSTEL_VISITORS = f"{API_PREFIX}/hostel/visitors/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory

    return AdminUserFactory(school=school)


@pytest.fixture
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


@pytest.mark.django_db
class TestHostels:

    def test_create_hostel(self, admin_client, school):
        payload = {
            "name": "Boys Hostel A",
            "total_rooms": 20,
            "capacity_per_room": 4,
            "warden_name": "Mr. Johnson",
        }
        r = admin_client.post(HOSTEL_HOSTELS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Boys Hostel A"

    def test_list_hostels(self, admin_client, school):
        from services.hostel.models import Hostel

        Hostel.objects.create(school=school, name="Girls Hostel B")
        r = admin_client.get(HOSTEL_HOSTELS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_tenant_isolation_hostel(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        school_a = SchoolFactory(code="HSTA")
        school_b = SchoolFactory(code="HSTB")
        admin_a = AdminUserFactory(school=school_a)
        from services.hostel.models import Hostel

        Hostel.objects.create(school=school_b, name="Secret Hostel")
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(HOSTEL_HOSTELS)
        names = [h["name"] for h in r.data["results"]]
        assert "Secret Hostel" not in names


@pytest.mark.django_db
class TestHostelRooms:

    def test_create_room(self, admin_client, school):
        from services.hostel.models import Hostel

        hostel = Hostel.objects.create(school=school, name="Hostel A")
        payload = {
            "hostel": hostel.id,
            "room_number": "101",
            "capacity": 4,
            "room_type": "dormitory",
            "floor": 1,
        }
        r = admin_client.post(HOSTEL_ROOMS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["room_number"] == "101"


@pytest.mark.django_db
class TestHostelAllocations:

    def test_create_allocation(self, admin_client, school):
        from services.hostel.models import Hostel, HostelRoom
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        hostel = Hostel.objects.create(school=school, name="Hostel A")
        room = HostelRoom.objects.create(
            hostel=hostel,
            room_number="101",
            capacity=4,
        )
        payload = {
            "student": pupil.id,
            "room": room.id,
            "check_in_date": date.today().isoformat(),
        }
        r = admin_client.post(HOSTEL_ALLOCATIONS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_checkout_updates_occupied_beds(self, admin_client, school):
        from services.hostel.models import Hostel, HostelAllocation, HostelRoom
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        hostel = Hostel.objects.create(school=school, name="Hostel A")
        room = HostelRoom.objects.create(
            hostel=hostel,
            room_number="101",
            capacity=4,
        )
        alloc = HostelAllocation.objects.create(
            student=pupil,
            room=room,
            check_in_date=date.today(),
        )
        r = admin_client.post(f"{HOSTEL_ALLOCATIONS}{alloc.id}/checkout/")
        assert r.status_code == status.HTTP_200_OK
        room.refresh_from_db()
        assert room.occupied_beds == 0
        alloc.refresh_from_db()
        assert alloc.status == "checked_out"


@pytest.mark.django_db
class TestHostelFees:

    def test_create_fee(self, admin_client, school):
        from services.hostel.models import Hostel

        hostel = Hostel.objects.create(school=school, name="Hostel A")
        payload = {
            "hostel": hostel.id,
            "name": "Monthly Hostel Fee",
            "amount": "500.00",
            "billing_cycle": "monthly",
            "room_type": "double",
        }
        r = admin_client.post(HOSTEL_FEES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["amount"] == "500.00"


@pytest.mark.django_db
class TestHostelVisitors:

    def test_create_visitor(self, admin_client, school):
        from services.hostel.models import Hostel
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        hostel = Hostel.objects.create(school=school, name="Hostel A")
        payload = {
            "hostel": hostel.id,
            "visitor_name": "Parent Name",
            "phone": "+1234567890",
            "student_visited": pupil.id,
            "relationship": "father",
            "in_time": "2026-08-08T10:00:00Z",
            "purpose": "Visit",
        }
        r = admin_client.post(HOSTEL_VISITORS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["visitor_name"] == "Parent Name"
