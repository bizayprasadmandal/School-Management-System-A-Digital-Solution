"""
Global search API — tenant isolation and role gating.

The command palette's backend scans nine high-value entities in one request.
The headline properties this suite pins:

1. **Tenant isolation** — a record belonging to School B never appears in
   School A's results, for any query that matches both.
2. **Role gating** — an accountant gets invoices but never incidents; a
   student gets announcements but never staff/invoices.
3. **API contract** — short queries are rejected, anonymous callers get 401,
   and the response shape is ``{query, groups: [{key, label, results}]}``.
"""

from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from services.auth.models import User
from services.hostel.models import Hostel, HostelRoom
from services.hr.models import Employee
from services.library.models import Book
from services.transportation.models import Vehicle
from tests.factories import (
    AdminUserFactory,
    AnnouncementFactory,
    ApplicationFactory,
    FeeInvoiceFactory,
    SchoolFactory,
    StudentFactory,
    TeacherUserFactory,
)


def make_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def client_a():
    return APIClient()


@pytest.fixture
def school_a(db):
    return SchoolFactory(name="Alpha Academy")


@pytest.fixture
def school_b(db):
    return SchoolFactory(name="Beta High")


# ─── Contract ─────────────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_requires_auth(client_a):
    resp = client_a.get("/api/v1/search/", {"q": "john"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_short_query_rejected(school_a, client_a):
    admin = AdminUserFactory(school=school_a)
    client = make_client(admin)
    resp = client.get("/api/v1/search/", {"q": "j"})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_missing_query_rejected(school_a, client_a):
    admin = AdminUserFactory(school=school_a)
    client = make_client(admin)
    resp = client.get("/api/v1/search/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_no_results_shape(school_a, client_a):
    admin = AdminUserFactory(school=school_a)
    client = make_client(admin)
    resp = client.get("/api/v1/search/", {"q": "zzzznothing"})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["query"] == "zzzznothing"
    assert resp.data["groups"] == []


# ─── Students ─────────────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_finds_student_by_name(school_a, client_a):
    admin = AdminUserFactory(school=school_a, first_name="Marilyn", last_name="Vos")
    student_user = User.objects.create_user(
        email="marilyn.vos@student.alpha.edu",
        password="Student@1234",
        first_name="Marilyn",
        last_name="Vos",
        role="student",
        school=school_a,
    )
    StudentFactory(user=student_user)
    client = make_client(admin)
    resp = client.get("/api/v1/search/", {"q": "marilyn"})
    assert resp.status_code == 200
    groups = {g["key"]: g for g in resp.data["groups"]}
    assert "students" in groups
    hit = groups["students"]["results"][0]
    assert "Marilyn" in hit["title"]
    assert hit["url"].startswith("/admin/students/")


@pytest.mark.django_db
def test_student_tenant_isolation(school_a, school_b, client_a):
    """Same name in both schools — each admin only ever sees their own."""
    for school in (school_a, school_b):
        u = User.objects.create_user(
            email=f"duplicate-{school.pk}@students.edu",
            password="Student@1234",
            first_name="Duplicate",
            last_name="Name",
            role="student",
            school=school,
        )
        StudentFactory(user=u)
    admin_a = AdminUserFactory(school=school_a)
    resp = make_client(admin_a).get("/api/v1/search/", {"q": "duplicate"})
    groups = {g["key"]: g for g in resp.data["groups"]}
    hits = groups["students"]["results"]
    assert len(hits) == 1  # School B's twin is invisible
    admin_b = AdminUserFactory(school=school_b)
    resp_b = make_client(admin_b).get("/api/v1/search/", {"q": "duplicate"})
    groups_b = {g["key"]: g for g in resp_b.data["groups"]}
    assert len(groups_b["students"]["results"]) == 1


# ─── Role gating ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_accountant_sees_invoices_not_incidents(school_a, client_a):
    from decimal import Decimal

    student_user = User.objects.create_user(
        email="invstudent@alpha.edu", password="Student@1234", role="student", school=school_a
    )
    student = StudentFactory(user=student_user)
    FeeInvoiceFactory(
        invoice_number="INV-SEARCH-001",
        student=student,
        base_amount=Decimal("100.00"),
        total_amount=Decimal("100.00"),
    )
    accountant = User.objects.create_user(
        email="acct@alpha.edu",
        password="Acct@12345",
        role="accountant",
        school=school_a,
    )
    resp = make_client(accountant).get("/api/v1/search/", {"q": "INV-SEARCH"})
    keys = [g["key"] for g in resp.data["groups"]]
    assert "invoices" in keys
    assert "incidents" not in keys


@pytest.mark.django_db
def test_student_role_sees_announcements_only(school_a, client_a):
    AnnouncementFactory(school=school_a, title="Sports Day Announcement")
    student_user = User.objects.create_user(
        email="plainstudent@alpha.edu", password="Student@1234", role="student", school=school_a
    )
    resp = make_client(student_user).get("/api/v1/search/", {"q": "sports day"})
    keys = [g["key"] for g in resp.data["groups"]]
    assert "announcements" in keys
    assert "staff" not in keys and "invoices" not in keys and "incidents" not in keys


# ─── Secondary entities ───────────────────────────────────────────────────────


@pytest.mark.django_db
def test_finds_staff_by_employee_id(school_a, client_a):
    admin = AdminUserFactory(school=school_a)
    emp_user = TeacherUserFactory(school=school_a)
    Employee.objects.create(
        school=school_a,
        user=emp_user,
        employee_id=f"EMP-777-{str(school_a.pk)[:8]}",
        designation="Teacher",
        joining_date=date.today(),
    )
    resp = make_client(admin).get("/api/v1/search/", {"q": f"EMP-777-{str(school_a.pk)[:8]}"})
    groups = {g["key"]: g for g in resp.data["groups"]}
    assert groups["staff"]["results"][0]["subtitle"].startswith("Staff")


@pytest.mark.django_db
def test_finds_book_by_isbn(school_a, client_a):
    admin = AdminUserFactory(school=school_a)
    Book.objects.create(school=school_a, title="Quantum Gardening", author="L. Plant", isbn="978-SEARCH1")
    resp = make_client(admin).get("/api/v1/search/", {"q": "978-SEARCH1"})
    groups = {g["key"]: g for g in resp.data["groups"]}
    assert groups["books"]["results"][0]["title"] == "Quantum Gardening"


@pytest.mark.django_db
def test_finds_application_by_guardian(school_a, client_a):
    admin = AdminUserFactory(school=school_a)
    ApplicationFactory(school=school_a, first_name="Ivy", last_name="Chen", guardian_name="Mr. Chen Guardian")
    resp = make_client(admin).get("/api/v1/search/", {"q": "Mr. Chen"})
    groups = {g["key"]: g for g in resp.data["groups"]}
    assert groups["applications"]["results"][0]["title"] == "Ivy Chen"


@pytest.mark.django_db
def test_finds_vehicle_by_plate(school_a, client_a):
    admin = AdminUserFactory(school=school_a)
    Vehicle.objects.create(
        school=school_a, plate_number=f"BUS-42-{str(school_a.pk)[:6]}", vehicle_type="bus", capacity=30
    )
    resp = make_client(admin).get("/api/v1/search/", {"q": f"BUS-42-{str(school_a.pk)[:6]}"})
    groups = {g["key"]: g for g in resp.data["groups"]}
    assert groups["vehicles"]["results"][0]["title"].startswith("BUS-42")


@pytest.mark.django_db
def test_finds_hostel_room(school_a, client_a):
    admin = AdminUserFactory(school=school_a)
    hostel = Hostel.objects.create(school=school_a, name="East Hall")
    HostelRoom.objects.create(hostel=hostel, room_number="204", capacity=4)
    resp = make_client(admin).get("/api/v1/search/", {"q": "204"})
    groups = {g["key"]: g for g in resp.data["groups"]}
    assert groups["rooms"]["results"][0]["title"] == "Room 204"


# ─── Extended entities (checkouts, counseling, inventory) ─────────────────────


@pytest.mark.django_db
def test_finds_checkout_by_book_title(school_a, client_a):
    from datetime import timedelta

    from services.library.models import Checkout

    admin = AdminUserFactory(school=school_a)
    book = Book.objects.create(school=school_a, title="Algebra Basics", author="A. Mathematician", isbn="978-ALG1")
    student_user = User.objects.create_user(
        email="checkoutstudent@alpha.edu", password="Student@1234", role="student", school=school_a
    )
    student = StudentFactory(user=student_user)
    Checkout.objects.create(book=book, student=student, due_date=date.today() + timedelta(days=7))
    resp = make_client(admin).get("/api/v1/search/", {"q": "algebra"})
    groups = {g["key"]: g for g in resp.data["groups"]}
    assert "Algebra Basics" in groups["checkouts"]["results"][0]["title"]


@pytest.mark.django_db
def test_counseling_sessions_role_gated(school_a, client_a):
    """Sessions are sensitive: admins/counselors see hits, teachers must not."""
    from services.counseling.models import CounselingSession

    admin = AdminUserFactory(school=school_a)
    student_user = User.objects.create_user(
        email="counselstudent@alpha.edu", password="Student@1234", role="student", school=school_a
    )
    student = StudentFactory(user=student_user)
    CounselingSession.objects.create(
        school=school_a,
        counselor=admin,
        student=student,
        session_date=date.today(),
        start_time="10:00",
        presenting_issue="exam anxiety",
    )

    resp = make_client(admin).get("/api/v1/search/", {"q": "anxiety"})
    keys = [g["key"] for g in resp.data["groups"]]
    assert "sessions" in keys

    teacher = TeacherUserFactory(school=school_a)
    resp_teacher = make_client(teacher).get("/api/v1/search/", {"q": "anxiety"})
    keys_teacher = [g["key"] for g in resp_teacher.data["groups"]]
    assert "sessions" not in keys_teacher


@pytest.mark.django_db
def test_finds_inventory_by_sku(school_a, client_a):
    from services.inventory.models import InventoryItem

    admin = AdminUserFactory(school=school_a)
    InventoryItem.objects.create(school=school_a, name="Whiteboard Markers", sku="SKU-SEARCH-777")
    resp = make_client(admin).get("/api/v1/search/", {"q": "SKU-SEARCH"})
    groups = {g["key"]: g for g in resp.data["groups"]}
    assert groups["inventory"]["results"][0]["title"] == "Whiteboard Markers"
