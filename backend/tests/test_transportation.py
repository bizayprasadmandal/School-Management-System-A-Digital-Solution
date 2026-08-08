"""Tests for Transportation Service — vehicles, drivers, routes, student routes, maintenance."""

from datetime import date, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

TRANSPORT_VEHICLES = f"{API_PREFIX}/transport/vehicles/"
TRANSPORT_DRIVERS = f"{API_PREFIX}/transport/drivers/"
TRANSPORT_ROUTES = f"{API_PREFIX}/transport/routes/"
TRANSPORT_ROUTE_STOPS = f"{API_PREFIX}/transport/route-stops/"
TRANSPORT_STUDENT_ROUTES = f"{API_PREFIX}/transport/student-routes/"
TRANSPORT_MAINTENANCE = f"{API_PREFIX}/transport/maintenance/"


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
class TestVehicles:

    def test_create_vehicle(self, admin_client, school):
        payload = {
            "plate_number": "ABC-1234",
            "vehicle_type": "bus",
            "capacity": 40,
            "model_name": "Toyota Coaster",
            "year": 2023,
        }
        r = admin_client.post(TRANSPORT_VEHICLES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["plate_number"] == "ABC-1234"

    def test_list_vehicles(self, admin_client, school):
        from services.transportation.models import Vehicle

        Vehicle.objects.create(
            school=school,
            plate_number="XYZ-5678",
            vehicle_type="bus",
            capacity=30,
        )
        r = admin_client.get(TRANSPORT_VEHICLES)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_teacher_cannot_create_vehicle(self, teacher_client):
        payload = {"plate_number": "TST-0001", "vehicle_type": "van", "capacity": 10}
        r = teacher_client.post(TRANSPORT_VEHICLES, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_tenant_isolation_vehicle(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        school_a = SchoolFactory(code="TPTA")
        school_b = SchoolFactory(code="TPTB")
        admin_a = AdminUserFactory(school=school_a)
        from services.transportation.models import Vehicle

        Vehicle.objects.create(
            school=school_b,
            plate_number="SEC-0001",
            vehicle_type="bus",
            capacity=20,
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(TRANSPORT_VEHICLES)
        plates = [v["plate_number"] for v in r.data["results"]]
        assert "SEC-0001" not in plates


@pytest.mark.django_db
class TestDrivers:

    def test_create_driver(self, admin_client, school):
        payload = {
            "full_name": "John Driver",
            "phone_number": "+1234567890",
            "license_number": "DL-2023-001",
            "license_expiry": (date.today() + timedelta(days=365)).isoformat(),
        }
        r = admin_client.post(TRANSPORT_DRIVERS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["license_number"] == "DL-2023-001"

    def test_search_drivers(self, admin_client, school):
        from services.transportation.models import Driver

        Driver.objects.create(
            school=school,
            full_name="Alice Smith",
            phone_number="+9876543210",
            license_number="DL-2024-002",
        )
        r = admin_client.get(f"{TRANSPORT_DRIVERS}?search=Alice")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestRoutes:

    def test_create_route(self, admin_client, school):
        from services.transportation.models import Driver, Vehicle

        vehicle = Vehicle.objects.create(
            school=school,
            plate_number="BUS-001",
            vehicle_type="bus",
            capacity=40,
        )
        driver = Driver.objects.create(
            school=school,
            full_name="Bob Driver",
            phone_number="+1111111111",
            license_number="DL-001",
        )
        payload = {
            "name": "Route A - North Side",
            "vehicle": vehicle.id,
            "driver": driver.id,
            "origin": "School",
            "destination": "North Terminal",
        }
        r = admin_client.post(TRANSPORT_ROUTES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Route A - North Side"

    def test_list_routes(self, admin_client, school):
        from services.transportation.models import Route

        Route.objects.create(
            school=school,
            name="Route B - South Side",
            origin="School",
            destination="South Terminal",
        )
        r = admin_client.get(TRANSPORT_ROUTES)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestRouteStops:

    def test_create_route_stop(self, admin_client, school):
        from services.transportation.models import Route

        route = Route.objects.create(
            school=school,
            name="Route A",
            origin="School",
            destination="Terminal",
        )
        payload = {
            "route": route.id,
            "name": "Main Street Stop",
            "address": "123 Main St",
            "stop_order": 1,
            "pickup_time": "07:15",
        }
        r = admin_client.post(TRANSPORT_ROUTE_STOPS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["stop_order"] == 1


@pytest.mark.django_db
class TestStudentRoutes:

    def test_assign_student_to_route(self, admin_client, school):
        from services.transportation.models import Route, RouteStop
        from tests.factories import StudentFactory

        pupil = StudentFactory(school=school)
        route = Route.objects.create(
            school=school,
            name="Route C",
            origin="School",
            destination="East End",
        )
        stop = RouteStop.objects.create(
            route=route,
            name="Park Stop",
            address="456 Park Ave",
            stop_order=1,
        )
        payload = {
            "student": pupil.id,
            "route": route.id,
            "pickup_stop": stop.id,
            "dropoff_stop": stop.id,
            "effective_from": date.today().isoformat(),
        }
        r = admin_client.post(TRANSPORT_STUDENT_ROUTES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_student_sees_own_route(self, db, school):
        from services.transportation.models import Route, RouteStop, StudentRoute
        from tests.factories import StudentFactory, StudentUserFactory

        student_user = StudentUserFactory(school=school)
        pupil = StudentFactory(user=student_user, school=school)
        route = Route.objects.create(
            school=school,
            name="Route D",
            origin="School",
            destination="West Side",
        )
        stop = RouteStop.objects.create(
            route=route,
            name="West Stop",
            address="789 West Rd",
            stop_order=1,
        )
        StudentRoute.objects.create(
            student=pupil,
            route=route,
            pickup_stop=stop,
            dropoff_stop=stop,
            effective_from=date.today(),
        )
        client = APIClient()
        client.force_authenticate(user=student_user)
        r = client.get(TRANSPORT_STUDENT_ROUTES)
        assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestVehicleMaintenance:

    def test_create_maintenance_record(self, admin_client, school):
        from services.transportation.models import Vehicle

        vehicle = Vehicle.objects.create(
            school=school,
            plate_number="BUS-002",
            vehicle_type="bus",
            capacity=50,
        )
        payload = {
            "vehicle": vehicle.id,
            "maintenance_type": "routine",
            "description": "Oil change and tire rotation",
            "scheduled_date": date.today().isoformat(),
            "cost": "250.00",
            "vendor_name": "Auto Service Inc.",
        }
        r = admin_client.post(TRANSPORT_MAINTENANCE, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["maintenance_type"] == "routine"

    def test_upcoming_maintenance(self, admin_client, school):
        from services.transportation.models import Vehicle, VehicleMaintenance

        vehicle = Vehicle.objects.create(
            school=school,
            plate_number="BUS-003",
            vehicle_type="bus",
            capacity=30,
        )
        VehicleMaintenance.objects.create(
            vehicle=vehicle,
            maintenance_type="routine",
            description="Annual inspection",
            scheduled_date=date.today() + timedelta(days=7),
            status="scheduled",
        )
        r = admin_client.get(f"{TRANSPORT_MAINTENANCE}?status=scheduled")
        assert r.status_code == status.HTTP_200_OK
        for m in r.data["results"]:
            assert m["status"] == "scheduled"
