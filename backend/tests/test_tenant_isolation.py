"""
Tenant-isolation regression tests.

Verify that school-scoped write paths reject objects from other schools:
  - student creation (classroom)
  - student promotion (classroom + academic year)
  - bulk grade submission (exam schedule)
  - grade CSV import (exam schedule)
  - purchase order creation (inventory item)
  - library checkout (book, student)
  - hostel (warden, assistant warden, room's hostel, allocation student/room,
    fee hostel, visitor hostel/student_visited)
  - inventory (item category/supplier, stock movement item)
  - health clinic (student on records/visits/immunizations/medication logs)
"""

import json
from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import (
    AcademicYearFactory,
    AdminUserFactory,
    ClassroomFactory,
    EnrollmentFactory,
    ExamFactory,
    ExamScheduleFactory,
    SchoolFactory,
    StudentFactory,
    TeacherUserFactory,
)
from tests.url_helpers import (
    ATTENDANCE_STUDENT_REPORT,
    GRADEBOOK_GRADES_BULK,
    GRADEBOOK_GRADES_IMPORT_CSV,
    HEALTH_IMMUNIZATIONS,
    HEALTH_MEDICATION_LOGS,
    HEALTH_NURSE_VISITS,
    HEALTH_RECORDS,
    HOSTEL_ALLOCATIONS,
    HOSTEL_FEES,
    HOSTEL_HOSTELS,
    HOSTEL_ROOMS,
    HOSTEL_VISITORS,
    INVENTORY_ITEMS,
    INVENTORY_PURCHASE_ORDERS,
    INVENTORY_STOCK_MOVEMENTS,
    LIBRARY_CHECKOUTS,
    STUDENTS_LIST,
    STUDENTS_PROMOTE,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def school_a(db):
    return SchoolFactory()


@pytest.fixture
def school_b(db):
    return SchoolFactory()


def _auth(client, user):
    client.force_authenticate(user=user)
    return client


# ─── Student creation ─────────────────────────────────────────────────────────


def test_student_create_rejects_foreign_school_classroom(api_client, school_a, school_b):
    admin = AdminUserFactory(school=school_a, email="admin-a@test.edu", email_verified=True)
    foreign_classroom = ClassroomFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        STUDENTS_LIST,
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@test.edu",
            "password": "Str0ngPass!",
            "admission_number": "ADM-FOREIGN-1",
            "date_of_birth": "2015-01-01",
            "gender": "F",
            "address": "1 Main St",
            "city": "KTM",
            "state": "Bagmati",
            "country": "NP",
            "admission_date": date.today().isoformat(),
            "classroom_id": foreign_classroom.id,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "not found in your school" in str(resp.data)


# ─── Student promotion ────────────────────────────────────────────────────────


def test_promote_rejects_foreign_school_classroom(api_client, school_a, school_b):
    admin = AdminUserFactory(school=school_a, email="admin-b@test.edu", email_verified=True)
    ay_a = AcademicYearFactory(school=school_a)
    classroom_a = ClassroomFactory(school=school_a)
    foreign_classroom = ClassroomFactory(school=school_b)
    student = StudentFactory(school=school_a)
    EnrollmentFactory(student=student, classroom=classroom_a, academic_year=ay_a)

    resp = _auth(api_client, admin).post(
        STUDENTS_PROMOTE,
        {
            "student_ids": [str(student.id)],
            "target_classroom_id": foreign_classroom.id,
            "academic_year_id": ay_a.id,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Target classroom not found in your school" in resp.data["error"]
    # No enrollment created into the foreign classroom
    assert student.enrollments.filter(classroom=foreign_classroom).count() == 0


def test_promote_rejects_foreign_school_academic_year(api_client, school_a, school_b):
    admin = AdminUserFactory(school=school_a, email="admin-c@test.edu", email_verified=True)
    ay_a = AcademicYearFactory(school=school_a)
    classroom_a = ClassroomFactory(school=school_a)
    foreign_year = AcademicYearFactory(school=school_b)
    student = StudentFactory(school=school_a)
    EnrollmentFactory(student=student, classroom=classroom_a, academic_year=ay_a)

    resp = _auth(api_client, admin).post(
        STUDENTS_PROMOTE,
        {
            "student_ids": [str(student.id)],
            "target_classroom_id": classroom_a.id,
            "academic_year_id": foreign_year.id,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid academic year" in resp.data["error"]


# ─── Bulk grade submission ────────────────────────────────────────────────────


def test_bulk_grades_rejects_foreign_school_exam_schedule(api_client, school_a, school_b):
    teacher = TeacherUserFactory(school=school_a, email="teacher-a@test.edu", email_verified=True)
    foreign_exam = ExamFactory(school=school_b)
    foreign_schedule = ExamScheduleFactory(exam=foreign_exam)

    resp = _auth(api_client, teacher).post(
        GRADEBOOK_GRADES_BULK,
        {
            "exam_schedule_id": foreign_schedule.id,
            "grades": [{"student_id": "00000000-0000-0000-0000-000000000000", "marks_obtained": 90}],
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "not found in your school" in str(resp.data)


# ─── Grade CSV import ─────────────────────────────────────────────────────────


def test_grade_csv_import_rejects_foreign_school_exam_schedule(api_client, school_a, school_b):
    teacher = TeacherUserFactory(school=school_a, email="teacher-b@test.edu", email_verified=True)
    foreign_exam = ExamFactory(school=school_b)
    foreign_schedule = ExamScheduleFactory(exam=foreign_exam)

    csv_text = "admission_number,exam_schedule_id,marks_obtained\n" f"ADM-X,{foreign_schedule.id},90\n"
    resp = _auth(api_client, teacher).post(
        GRADEBOOK_GRADES_IMPORT_CSV,
        {"csv_data": csv_text},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["imported"] == 0
    assert any("not found in your school" in e for e in resp.data["errors"])


# ─── Inventory purchase order ─────────────────────────────────────────────────


def test_purchase_order_rejects_foreign_school_item(api_client, school_a, school_b):
    from services.inventory.models import InventoryItem

    admin = AdminUserFactory(school=school_a, email="admin-d@test.edu", email_verified=True)
    foreign_item = InventoryItem.objects.create(school=school_b, name="Foreign Pens", sku="FOREIGN-001", unit_price=10)

    resp = _auth(api_client, admin).post(
        INVENTORY_PURCHASE_ORDERS,
        {
            "order_number": "PO-TENANT-001",
            "order_date": date.today().isoformat(),
            "items_data": json.dumps([{"item": str(foreign_item.id), "quantity_ordered": 5}]),
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "not found in your school" in resp.data["error"]
    # No purchase order should have been created (no partial state)
    from services.inventory.models import PurchaseOrder

    assert PurchaseOrder.objects.filter(order_number="PO-TENANT-001").count() == 0


# ─── Library checkout ─────────────────────────────────────────────────────────


def test_checkout_rejects_foreign_school_book(api_client, school_a, school_b):
    from services.library.models import Book

    admin = AdminUserFactory(school=school_a, email="admin-lib-a@test.edu", email_verified=True)
    student = StudentFactory(school=school_a)
    foreign_book = Book.objects.create(school=school_b, title="Foreign Book", author="X")

    resp = _auth(api_client, admin).post(
        LIBRARY_CHECKOUTS,
        {"book": foreign_book.id, "student": str(student.id), "due_date": "2026-09-01"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Book not found in your school." in str(resp.data)
    assert student.book_checkouts.count() == 0


def test_checkout_rejects_foreign_school_student(api_client, school_a, school_b):
    from services.library.models import Book

    admin = AdminUserFactory(school=school_a, email="admin-lib-b@test.edu", email_verified=True)
    book = Book.objects.create(school=school_a, title="Local Book", author="X", total_copies=2)
    foreign_student = StudentFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        LIBRARY_CHECKOUTS,
        {"book": book.id, "student": str(foreign_student.id), "due_date": "2026-09-01"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Student not found in your school." in str(resp.data)
    assert foreign_student.book_checkouts.count() == 0


# ─── Hostel ───────────────────────────────────────────────────────────────────


def test_hostel_rejects_foreign_school_warden(api_client, school_a, school_b):
    admin = AdminUserFactory(school=school_a, email="admin-hostel-a@test.edu", email_verified=True)
    foreign_warden = TeacherUserFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        HOSTEL_HOSTELS,
        {"name": "Sunrise Hostel", "warden": str(foreign_warden.id)},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Warden must be in your school." in str(resp.data)


def test_hostel_rejects_foreign_school_assistant_warden(api_client, school_a, school_b):
    admin = AdminUserFactory(school=school_a, email="admin-hostel-b@test.edu", email_verified=True)
    foreign_warden = TeacherUserFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        HOSTEL_HOSTELS,
        {"name": "Sunset Hostel", "assistant_warden": str(foreign_warden.id)},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Assistant warden must be in your school." in str(resp.data)


def test_hostel_room_rejects_foreign_school_hostel(api_client, school_a, school_b):
    from services.hostel.models import Hostel

    admin = AdminUserFactory(school=school_a, email="admin-hostel-c@test.edu", email_verified=True)
    foreign_hostel = Hostel.objects.create(school=school_b, name="Foreign Hostel")

    resp = _auth(api_client, admin).post(
        HOSTEL_ROOMS,
        {"hostel": str(foreign_hostel.id), "room_number": "B-101"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Hostel not found in your school." in str(resp.data)


def test_hostel_allocation_rejects_foreign_school_room(api_client, school_a, school_b):
    from services.hostel.models import Hostel, HostelRoom

    admin = AdminUserFactory(school=school_a, email="admin-hostel-d@test.edu", email_verified=True)
    student = StudentFactory(school=school_a)
    foreign_hostel = Hostel.objects.create(school=school_b, name="Foreign Hostel")
    foreign_room = HostelRoom.objects.create(hostel=foreign_hostel, room_number="B-101")

    resp = _auth(api_client, admin).post(
        HOSTEL_ALLOCATIONS,
        {"student": str(student.id), "room": str(foreign_room.id), "check_in_date": "2026-09-01"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Room not found in your school." in str(resp.data)
    assert student.hostel_allocations.count() == 0


def test_hostel_allocation_rejects_foreign_school_student(api_client, school_a, school_b):
    from services.hostel.models import Hostel, HostelRoom

    admin = AdminUserFactory(school=school_a, email="admin-hostel-e@test.edu", email_verified=True)
    hostel = Hostel.objects.create(school=school_a, name="Local Hostel")
    room = HostelRoom.objects.create(hostel=hostel, room_number="A-101")
    foreign_student = StudentFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        HOSTEL_ALLOCATIONS,
        {"student": str(foreign_student.id), "room": str(room.id), "check_in_date": "2026-09-01"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Student not found in your school." in str(resp.data)


def test_hostel_fee_rejects_foreign_school_hostel(api_client, school_a, school_b):
    from services.hostel.models import Hostel

    admin = AdminUserFactory(school=school_a, email="admin-hostel-f@test.edu", email_verified=True)
    foreign_hostel = Hostel.objects.create(school=school_b, name="Foreign Hostel")

    resp = _auth(api_client, admin).post(
        HOSTEL_FEES,
        {"name": "Monthly Fee", "hostel": str(foreign_hostel.id), "amount": "100.00"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Hostel not found in your school." in str(resp.data)


def test_hostel_visitor_rejects_foreign_school_hostel(api_client, school_a, school_b):
    from services.hostel.models import Hostel

    admin = AdminUserFactory(school=school_a, email="admin-hostel-g@test.edu", email_verified=True)
    student = StudentFactory(school=school_a)
    foreign_hostel = Hostel.objects.create(school=school_b, name="Foreign Hostel")

    resp = _auth(api_client, admin).post(
        HOSTEL_VISITORS,
        {
            "hostel": str(foreign_hostel.id),
            "visitor_name": "John Doe",
            "student_visited": str(student.id),
            "in_time": "2026-09-01T10:00:00Z",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Hostel not found in your school." in str(resp.data)


def test_hostel_visitor_rejects_foreign_school_student_visited(api_client, school_a, school_b):
    from services.hostel.models import Hostel

    admin = AdminUserFactory(school=school_a, email="admin-hostel-h@test.edu", email_verified=True)
    hostel = Hostel.objects.create(school=school_a, name="Local Hostel")
    foreign_student = StudentFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        HOSTEL_VISITORS,
        {
            "hostel": str(hostel.id),
            "visitor_name": "Jane Roe",
            "student_visited": str(foreign_student.id),
            "in_time": "2026-09-01T10:00:00Z",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Student not found in your school." in str(resp.data)


# ─── Inventory item / stock movement ──────────────────────────────────────────


def test_inventory_item_rejects_foreign_school_category(api_client, school_a, school_b):
    from services.inventory.models import Category

    admin = AdminUserFactory(school=school_a, email="admin-inv-a@test.edu", email_verified=True)
    foreign_category = Category.objects.create(school=school_b, name="Foreign Category")

    resp = _auth(api_client, admin).post(
        INVENTORY_ITEMS,
        {
            "name": "Pens",
            "sku": "SKU-TENANT-A",
            "category": str(foreign_category.id),
            "unit": "piece",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Category not found in your school." in str(resp.data)


def test_inventory_item_rejects_foreign_school_supplier(api_client, school_a, school_b):
    from services.inventory.models import Supplier

    admin = AdminUserFactory(school=school_a, email="admin-inv-b@test.edu", email_verified=True)
    foreign_supplier = Supplier.objects.create(school=school_b, name="Foreign Supplier", phone="+1-555-0001")

    resp = _auth(api_client, admin).post(
        INVENTORY_ITEMS,
        {
            "name": "Pens",
            "sku": "SKU-TENANT-B",
            "supplier": str(foreign_supplier.id),
            "unit": "piece",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Supplier not found in your school." in str(resp.data)


def test_stock_movement_rejects_foreign_school_item(api_client, school_a, school_b):
    from services.inventory.models import InventoryItem

    admin = AdminUserFactory(school=school_a, email="admin-inv-c@test.edu", email_verified=True)
    foreign_item = InventoryItem.objects.create(school=school_b, name="Foreign Pens", sku="FOREIGN-002")

    resp = _auth(api_client, admin).post(
        INVENTORY_STOCK_MOVEMENTS,
        {"item": str(foreign_item.id), "movement_type": "adjustment", "quantity": 5},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Item not found in your school." in str(resp.data)


# ─── Attendance ──────────────────────────────────────────────────────────────


def test_student_report_rejects_foreign_school_student(api_client, school_a, school_b):
    """The monthly attendance report must not leak another school's student data."""
    admin = AdminUserFactory(school=school_a, email="admin-att@test.edu", email_verified=True)
    foreign_student = StudentFactory(school=school_b)

    resp = _auth(api_client, admin).get(
        ATTENDANCE_STUDENT_REPORT,
        {"student_id": str(foreign_student.id), "month": 8, "year": 2026},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "Student not found" in str(resp.data)


# ─── Health clinic ────────────────────────────────────────────────────────────


def test_health_record_rejects_foreign_school_student(api_client, school_a, school_b):
    admin = AdminUserFactory(school=school_a, email="admin-health-a@test.edu", email_verified=True)
    foreign_student = StudentFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        HEALTH_RECORDS,
        {"student": str(foreign_student.id), "blood_type": "O+"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Student not found in your school." in str(resp.data)


def test_nurse_visit_rejects_foreign_school_student(api_client, school_a, school_b):
    admin = AdminUserFactory(school=school_a, email="admin-health-b@test.edu", email_verified=True)
    foreign_student = StudentFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        HEALTH_NURSE_VISITS,
        {"student": str(foreign_student.id), "visit_type": "sick"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Student not found in your school." in str(resp.data)


def test_immunization_rejects_foreign_school_student(api_client, school_a, school_b):
    admin = AdminUserFactory(school=school_a, email="admin-health-c@test.edu", email_verified=True)
    foreign_student = StudentFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        HEALTH_IMMUNIZATIONS,
        {
            "student": str(foreign_student.id),
            "vaccine_name": "BCG",
            "date_administered": "2026-01-01",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Student not found in your school." in str(resp.data)


def test_medication_log_rejects_foreign_school_student(api_client, school_a, school_b):
    admin = AdminUserFactory(school=school_a, email="admin-health-d@test.edu", email_verified=True)
    foreign_student = StudentFactory(school=school_b)

    resp = _auth(api_client, admin).post(
        HEALTH_MEDICATION_LOGS,
        {
            "student": str(foreign_student.id),
            "medication_name": "Paracetamol",
            "dosage": "500mg",
            "time_administered": "2026-09-01T10:00:00Z",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Student not found in your school." in str(resp.data)
