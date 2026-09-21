"""
Wide API coverage — Hostel, Transportation & Inventory CRUD endpoints.

These three modules carried the thinnest test suites relative to their
size (8/13/20 tests against 39-40 models each). This suite pins the
breadth: parametrized create-through-the-API for 31 simple-payload
viewsets, plus tenant isolation and 401 handling.

A failure here is a real bug — typically a viewset doing a plain
``serializer.save()`` while its model/serializer expects the view to
inject ``school`` (POST 400/500), or a serializer field name drift.

Parents (hostel, room, vehicle, route, ...) are created once in a
fixture; each spec builds its payload from them.
"""

from datetime import date, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import AcademicYearFactory, AdminUserFactory, SchoolFactory, StudentFactory

TODAY = date.today()
NEXT_WEEK = TODAY + timedelta(days=7)


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def parents(db):
    """Parent rows every payload may reference — all inside ONE school.

    The student is the anchor: StudentFactory creates its own school, so
    every other parent row (and the admin user) must derive from
    ``student.school`` or cross-school validation and tenant filters
    correctly reject the payloads.
    """
    from services.hostel.models import Hostel, HostelAllocation, HostelAsset, HostelEvent, HostelRoom
    from services.inventory.models import Supplier, Warehouse, WarehouseZone
    from services.transportation.models import Driver, Route, Vehicle

    student = StudentFactory()
    school = student.school
    hostel = Hostel.objects.create(school=student.school, name="Wide Hall")
    room = HostelRoom.objects.create(hostel=hostel, room_number="W-101", capacity=2)
    allocation = HostelAllocation.objects.create(student=student, room=room, check_in_date=TODAY)
    vehicle = Vehicle.objects.create(
        school=student.school, plate_number=f"WIDE-{str(student.school.pk)[:6]}", capacity=30
    )
    driver = Driver.objects.create(school=student.school, full_name="Wide Driver", phone_number="+977-9800000000")
    route = Route.objects.create(school=student.school, name="Wide Route", origin="A", destination="B")
    warehouse = Warehouse.objects.create(school=student.school, name="Wide Warehouse", code="WW1")
    zone = WarehouseZone.objects.create(warehouse=warehouse, name="Wide Zone", zone_type="storage")
    supplier = Supplier.objects.create(school=student.school, name="Wide Supplier", phone="+977-9811111111")
    event = HostelEvent.objects.create(hostel=hostel, title="Wide Event", event_date=TODAY, start_time="10:00")
    asset = HostelAsset.objects.create(hostel=hostel, asset_name="Wide Asset")

    return {
        "school": school,
        "student": student,
        "hostel": hostel,
        "room": room,
        "allocation": allocation,
        "vehicle": vehicle,
        "driver": driver,
        "route": route,
        "warehouse": warehouse,
        "zone": zone,
        "supplier": supplier,
        "event": event,
        "asset": asset,
    }


@pytest.fixture
def admin(parents):
    client = APIClient()
    user = AdminUserFactory(school=parents["school"])
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def other_school_hostel(db):
    """A second school with its own hostel — for the isolation test."""
    from services.hostel.models import Hostel

    other = SchoolFactory()
    AcademicYearFactory(school=other, is_current=True)
    return Hostel.objects.create(school=other, name="Other Hall")


# ─── Create specs ─────────────────────────────────────────────────────────────
# (url path, payload builder receiving the parents dict)
# school / user fields are injected server-side where the model needs them.

HOSTEL_SPECS = [
    ("hostels/", lambda p: {"name": "Spec Hostel"}),
    (
        "visitors/",
        lambda p: {
            "hostel": p["hostel"].id,
            "student_visited": p["student"].id,
            "visitor_name": "Wide Visitor",
            "in_time": "2026-09-21T10:30:00Z",
        },
    ),
    ("roommate-assignment/", lambda p: {"room": p["room"].id, "student": p["student"].id}),
    ("room-key/", lambda p: {"room": p["room"].id, "key_number": "WK-1"}),
    (
        "common-area-booking/",
        lambda p: {
            "hostel": p["hostel"].id,
            "student": p["student"].id,
            "area_type": "study",
            "booking_date": TODAY,
            "start_time": "10:00",
            "end_time": "11:00",
        },
    ),
    ("mess-menu-plan/", lambda p: {"hostel": p["hostel"].id, "meal_type": "lunch", "day_of_week": "monday"}),
    ("hostel-asset/", lambda p: {"hostel": p["hostel"].id, "asset_name": "Spec Fan"}),
    (
        "hostel-event/",
        lambda p: {"hostel": p["hostel"].id, "title": "Spec Event", "event_date": TODAY, "start_time": "10:00"},
    ),
    ("hostel-event-participant/", lambda p: {"event": p["event"].id, "student": p["student"].id}),
    (
        "hostel-emergency-protocol/",
        lambda p: {
            "hostel": p["hostel"].id,
            "emergency_type": "fire",
            "title": "Spec Protocol",
            "description": "Steps",
            "procedures": "Evacuate",
            "contacts": "Front desk",
        },
    ),
    ("hostel-emergency-drill/", lambda p: {"hostel": p["hostel"].id, "drill_date": NEXT_WEEK, "start_time": "09:00"}),
    ("hostel-inspection-schedule/", lambda p: {"hostel": p["hostel"].id}),
    (
        "mess-feedback/",
        lambda p: {
            "hostel": p["hostel"].id,
            "student": p["student"].id,
            "meal_type": "lunch",
            "rating": 4,
            "meal_date": TODAY,
        },
    ),
]

TRANSPORT_SPECS = [
    ("drivers/", lambda p: {"full_name": "Spec Driver", "phone_number": "+977-9822222222"}),
    ("routes/", lambda p: {"name": "Spec Route", "origin": "Gate", "destination": "Depot"}),
    ("route-stops/", lambda p: {"route": p["route"].id, "name": "Spec Stop", "stop_order": 1}),
    (
        "vehicle-g-p-s-log/",
        lambda p: {
            "vehicle": p["vehicle"].id,
            "latitude": 27.7,
            "longitude": 85.3,
            "timestamp": "2026-09-21T10:00:00Z",
        },
    ),
    (
        "geofence-zone/",
        lambda p: {"name": "Spec Zone", "zone_type": "school", "center_latitude": 27.7, "center_longitude": 85.3},
    ),
    (
        "driver-license/",
        lambda p: {"driver": p["driver"].id, "license_number": "WDL-1", "issue_date": TODAY, "expiry_date": NEXT_WEEK},
    ),
    ("driver-performance/", lambda p: {"driver": p["driver"].id, "evaluation_date": TODAY}),
    (
        "vehicle-condition-report/",
        lambda p: {"vehicle": p["vehicle"].id, "report_type": "pre_trip", "report_date": TODAY},
    ),
    (
        "vehicle-assignment-log/",
        lambda p: {"vehicle": p["vehicle"].id, "assignment_date": TODAY, "assignment_type": "route"},
    ),
]

INVENTORY_SPECS = [
    ("categories/", lambda p: {"name": "Spec Category"}),
    ("suppliers/", lambda p: {"name": "Spec Supplier", "phone": "+977-9833333333"}),
    ("warehouse/", lambda p: {"name": "Spec Warehouse", "code": "SW1"}),
    ("warehouse-zone/", lambda p: {"warehouse": p["warehouse"].id, "name": "Spec Zone", "zone_type": "storage"}),
    ("warehouse-location/", lambda p: {"zone": p["zone"].id}),
    ("purchase-requisition/", lambda p: {"requisition_number": "WPR-1"}),
    (
        "supplier-rating/",
        lambda p: {
            "supplier": p["supplier"].id,
            "quality_rating": 4,
            "delivery_rating": 4,
            "price_rating": 3,
            "overall_rating": 4,
        },
    ),
    ("inventory-budget/", lambda p: {"fiscal_year": 2026, "total_budget": "100000.00"}),
    ("inventory-catalog/", lambda p: {"name": "Spec Catalog", "effective_date": TODAY}),
]

ALL_SPECS = (
    [("hostel/" + path, fn, "hostel") for path, fn in HOSTEL_SPECS]
    + [("transport/" + path, fn, "transport") for path, fn in TRANSPORT_SPECS]
    + [("inventory/" + path, fn, "inventory") for path, fn in INVENTORY_SPECS]
)


# ─── Tests ────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
@pytest.mark.parametrize("path,payload_fn,_mod", ALL_SPECS, ids=[s[0] for s in ALL_SPECS])
def test_create_and_list(admin, parents, path, payload_fn, _mod):
    """POST creates a row; it shows up in the tenant-scoped list."""
    payload = payload_fn(parents)
    resp = admin.post(f"/api/v1/{path}", payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED, f"POST {path}: {resp.data}"
    list_resp = admin.get(f"/api/v1/{path}")
    assert list_resp.status_code == status.HTTP_200_OK
    results = list_resp.data["results"] if isinstance(list_resp.data, dict) else list_resp.data
    assert any(row.get("id") == resp.data["id"] for row in results), f"created row not listed at {path}"


@pytest.mark.django_db
def test_tenant_isolation(admin, parents, other_school_hostel):
    """Another school's hostel never appears in our lists."""
    resp = admin.get("/api/v1/hostel/hostels/")
    results = resp.data["results"] if isinstance(resp.data, dict) else resp.data
    ids = {str(row["id"]) for row in results}
    assert str(other_school_hostel.id) not in ids
    assert str(parents["hostel"].id) in ids


@pytest.mark.django_db
def test_anonymous_gets_401(db):
    client = APIClient()
    assert client.get("/api/v1/hostel/hostels/").status_code == status.HTTP_401_UNAUTHORIZED
    assert client.get("/api/v1/transport/vehicles/").status_code == status.HTTP_401_UNAUTHORIZED
    assert client.get("/api/v1/inventory/items/").status_code == status.HTTP_401_UNAUTHORIZED
