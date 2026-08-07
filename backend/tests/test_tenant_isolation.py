"""
Tenant-isolation regression tests.

Verify that school-scoped write paths reject objects from other schools:
  - student creation (classroom)
  - student promotion (classroom + academic year)
  - bulk grade submission (exam schedule)
  - grade CSV import (exam schedule)
  - purchase order creation (inventory item)
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
    GRADEBOOK_GRADES_BULK,
    GRADEBOOK_GRADES_IMPORT_CSV,
    INVENTORY_PURCHASE_ORDERS,
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
