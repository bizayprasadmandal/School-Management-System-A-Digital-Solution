"""
RBAC sweep — regression tests locking in the security fixes applied to the
custom admin-grade actions.

Proves, action by action, that students/parents are denied the admin/teacher
custom actions while the intended role is allowed, and that foreign-school
objects can never be reached through those actions.

Each test is self-contained (creates its own data), so this module runs
standalone and is safe for parallel execution:

    python -m pytest tests/test_rbac_actions.py -q
"""

from datetime import date
from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import (
    AcademicYearFactory,
    AdminUserFactory,
    ClassroomFactory,
    EnrollmentFactory,
    ExamFactory,
    ExamScheduleFactory,
    FeeCategoryFactory,
    FeeStructureFactory,
    GradeFactory,
    ParentUserFactory,
    SchoolFactory,
    StudentFactory,
    StudentUserFactory,
    TeacherUserFactory,
    UserFactory,
)
from tests.url_helpers import (
    ATTENDANCE_CLASSROOM_SUMMARY,
    ATTENDANCE_IMPORT_CSV,
    COMMUNICATION_MESSAGES,
    FEES_INVOICES_IMPORT_CSV,
    GRADEBOOK_GRADES_IMPORT_CSV,
    INVENTORY_ITEMS,
    INVENTORY_PURCHASE_ORDERS,
    REPORTING_DASHBOARD_STATS,
    STUDENTS_LIST,
    attendance_leave_approve,
)

API_PREFIX = "/api/v1"
GRADEBOOK_EXPORT_CSV = f"{API_PREFIX}/gradebook/grades/export-csv/"
HR_PAYSLIPS = f"{API_PREFIX}/hr/payslips/"
HR_LEAVES = f"{API_PREFIX}/hr/leave-requests/"
FEES_INVOICES_BULK_GENERATE = f"{API_PREFIX}/fees/invoices/bulk-generate/"
ATTENDANCE_LEAVES = f"{API_PREFIX}/attendance/leaves/"
CONFERENCES_SLOTS = f"{API_PREFIX}/conferences/conference-slots/"


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def school(db):
    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    return AdminUserFactory(school=school)


@pytest.fixture
def teacher(db, school):
    return TeacherUserFactory(school=school)


@pytest.fixture
def student(db, school):
    return StudentUserFactory(school=school)


@pytest.fixture
def parent(db, school):
    return ParentUserFactory(school=school)


def _auth(client, user):
    client.force_authenticate(user=user)
    return client


def _make_employee(school, seq):
    """Create a minimal HR employee tied to a unique user/email."""
    from services.hr.models import Department, Employee

    emp_user = UserFactory(school=school, role="teacher", email=f"emp-{seq}@test.edu")
    dept = Department.objects.create(school=school, name=f"Dept {seq}", code=f"DEP{seq}")
    return Employee.objects.create(
        school=school,
        user=emp_user,
        department=dept,
        employee_id=f"EMP-{seq:04d}",
        designation="Teacher",
        joining_date=date.today(),
    )


# ─── Gradebook: export-csv / import-csv ───────────────────────────────────────


class TestGradebookExportCsv:
    def test_export_csv_student_denied(self, api, school, student, db):
        exam = ExamFactory(school=school)
        resp = _auth(api, student).get(GRADEBOOK_EXPORT_CSV, {"exam_id": str(exam.id)})
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_export_csv_admin_allowed(self, api, school, admin, db):
        exam = ExamFactory(school=school)
        resp = _auth(api, admin).get(GRADEBOOK_EXPORT_CSV, {"exam_id": str(exam.id)})
        assert resp.status_code == status.HTTP_200_OK
        assert resp["Content-Type"].startswith("text/csv")


class TestGradebookImportCsv:
    def test_import_csv_student_denied(self, api, school, student, db):
        resp = _auth(api, student).post(
            GRADEBOOK_GRADES_IMPORT_CSV, {"csv_data": "admission_number,exam_schedule_id\n"}, format="json"
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_import_csv_admin_allowed(self, api, school, admin, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school)
        csv_text = (
            "admission_number,exam_schedule_id,marks_obtained,is_absent,remarks\n"
            f"{student.admission_number},{schedule.id},66.00,false,good\n"
        )
        resp = _auth(api, admin).post(GRADEBOOK_GRADES_IMPORT_CSV, {"csv_data": csv_text}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["imported"] == 1


# ─── HR: payslip approve / mark-paid, leave approve / reject ─────────────────


class TestHrPayslipActions:
    def test_payslip_approve_student_denied(self, api, school, student, db):
        from services.hr.models import Payslip

        emp = _make_employee(school, 1)
        payslip = Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today(),
            period_end=date.today(),
            basic_salary=50000,
            gross_pay=60000,
            total_deductions=6000,
            net_pay=54000,
            status="draft",
        )
        resp = _auth(api, student).post(f"{HR_PAYSLIPS}{payslip.id}/approve/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_payslip_approve_admin_allowed(self, api, school, admin, db):
        from services.hr.models import Payslip

        emp = _make_employee(school, 2)
        payslip = Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today(),
            period_end=date.today(),
            basic_salary=50000,
            gross_pay=60000,
            total_deductions=6000,
            net_pay=54000,
            status="draft",
        )
        resp = _auth(api, admin).post(f"{HR_PAYSLIPS}{payslip.id}/approve/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        payslip.refresh_from_db()
        assert payslip.status == "approved"

    def test_payslip_mark_paid_student_denied(self, api, school, student, db):
        from services.hr.models import Payslip

        emp = _make_employee(school, 3)
        payslip = Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today(),
            period_end=date.today(),
            basic_salary=50000,
            gross_pay=60000,
            total_deductions=6000,
            net_pay=54000,
            status="approved",
        )
        resp = _auth(api, student).post(f"{HR_PAYSLIPS}{payslip.id}/mark-paid/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_payslip_mark_paid_admin_allowed(self, api, school, admin, db):
        from services.hr.models import Payslip

        emp = _make_employee(school, 4)
        payslip = Payslip.objects.create(
            school=school,
            employee=emp,
            period_start=date.today(),
            period_end=date.today(),
            basic_salary=50000,
            gross_pay=60000,
            total_deductions=6000,
            net_pay=54000,
            status="approved",
        )
        resp = _auth(api, admin).post(f"{HR_PAYSLIPS}{payslip.id}/mark-paid/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        payslip.refresh_from_db()
        assert payslip.status == "paid"


class TestHrLeaveActions:
    def _leave(self, school, emp, seq):
        from services.hr.models import LeaveRequest

        return LeaveRequest.objects.create(
            school=school,
            employee=emp,
            leave_type="sick",
            from_date=date.today(),
            to_date=date.today(),
            total_days=1,
            reason=f"Reason {seq}",
            status="pending",
        )

    def test_leave_approve_student_denied(self, api, school, student, db):
        emp = _make_employee(school, 5)
        leave = self._leave(school, emp, 5)
        resp = _auth(api, student).post(f"{HR_LEAVES}{leave.id}/approve/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_leave_approve_admin_allowed(self, api, school, admin, db):
        emp = _make_employee(school, 6)
        leave = self._leave(school, emp, 6)
        resp = _auth(api, admin).post(f"{HR_LEAVES}{leave.id}/approve/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        leave.refresh_from_db()
        assert leave.status == "approved"

    def test_leave_reject_student_denied(self, api, school, student, db):
        emp = _make_employee(school, 7)
        leave = self._leave(school, emp, 7)
        resp = _auth(api, student).post(f"{HR_LEAVES}{leave.id}/reject/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_leave_reject_admin_allowed(self, api, school, admin, db):
        emp = _make_employee(school, 8)
        leave = self._leave(school, emp, 8)
        resp = _auth(api, admin).post(f"{HR_LEAVES}{leave.id}/reject/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        leave.refresh_from_db()
        assert leave.status == "rejected"


# ─── Fees: invoice import-csv / bulk-generate ────────────────────────────────


class TestFeesInvoiceActions:
    def test_invoice_import_student_denied(self, api, school, student, db):
        resp = _auth(api, student).post(
            FEES_INVOICES_IMPORT_CSV,
            {"csv_data": "admission_number,fee_category_name,due_date,amount\n"},
            format="json",
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_invoice_import_admin_allowed(self, api, school, admin, db):
        year = AcademicYearFactory(school=school, is_current=True)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=year)
        student = StudentFactory(school=school)
        EnrollmentFactory(student=student, classroom=classroom, academic_year=year)
        fee_category = FeeCategoryFactory(school=school, name="Tuition")
        FeeStructureFactory(
            school=school, academic_year=year, grade=classroom.grade, fee_category=fee_category, amount=500
        )

        csv_text = (
            "admission_number,fee_category_name,due_date,amount,discount_amount,notes\n"
            f"{student.admission_number},Tuition,2026-09-10,500.00,0,term fee\n"
        )
        resp = _auth(api, admin).post(FEES_INVOICES_IMPORT_CSV, {"csv_data": csv_text}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["imported"] == 1

    def test_bulk_generate_student_denied(self, api, school, student, db):
        resp = _auth(api, student).post(
            FEES_INVOICES_BULK_GENERATE, {"fee_structure_id": "00000000-0000-0000-0000-000000000000"}, format="json"
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_bulk_generate_foreign_school_structure_403(self, api, school, admin, db):
        other_school = SchoolFactory()
        foreign_structure = FeeStructureFactory(school=other_school)
        resp = _auth(api, admin).post(
            FEES_INVOICES_BULK_GENERATE,
            {"fee_structure_id": str(foreign_structure.id), "academic_year_id": "00000000-0000-0000-0000-000000000000"},
            format="json",
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert "not found in your school" in str(resp.data)


# ─── Attendance: record import / leave approve+reject / classroom summary ────


class TestAttendanceImport:
    def test_import_csv_student_denied(self, api, school, student, db):
        resp = _auth(api, student).post(
            ATTENDANCE_IMPORT_CSV, {"csv_data": "admission_number,date,status\n"}, format="json"
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_import_csv_admin_allowed(self, api, school, admin, db):
        year = AcademicYearFactory(school=school, is_current=True)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=year)
        student = StudentFactory(school=school)
        EnrollmentFactory(student=student, classroom=classroom, academic_year=year)

        csv_text = (
            "admission_number,date,status,remarks\n"
            f"{student.admission_number},{date.today().isoformat()},P,on time\n"
        )
        resp = _auth(api, admin).post(ATTENDANCE_IMPORT_CSV, {"csv_data": csv_text}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["imported"] == 1


class TestAttendanceLeaveActions:
    def _leave(self, student_profile):
        from services.attendance.models import AttendanceLeave

        return AttendanceLeave.objects.create(
            student=student_profile,
            leave_type="sick",
            from_date=date.today(),
            to_date=date.today(),
            reason="Sick",
            status="pending",
        )

    def test_student_cannot_approve_own_leave(self, api, school, student, db):
        pupil = StudentFactory(user=student, school=school)
        leave = self._leave(pupil)
        resp = _auth(api, student).post(attendance_leave_approve(leave.id), {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        leave.refresh_from_db()
        assert leave.status == "pending"

    def test_admin_can_approve_leave(self, api, school, admin, db):
        pupil = StudentFactory(school=school)
        leave = self._leave(pupil)
        resp = _auth(api, admin).post(attendance_leave_approve(leave.id), {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        leave.refresh_from_db()
        assert leave.status == "approved"

    def test_student_cannot_reject_own_leave(self, api, school, student, db):
        pupil = StudentFactory(user=student, school=school)
        leave = self._leave(pupil)
        resp = _auth(api, student).post(f"{ATTENDANCE_LEAVES}{leave.id}/reject/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        leave.refresh_from_db()
        assert leave.status == "pending"

    def test_admin_can_reject_leave(self, api, school, admin, db):
        pupil = StudentFactory(school=school)
        leave = self._leave(pupil)
        resp = _auth(api, admin).post(f"{ATTENDANCE_LEAVES}{leave.id}/reject/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        leave.refresh_from_db()
        assert leave.status == "rejected"


class TestAttendanceClassroomSummary:
    def test_foreign_school_classroom_403(self, api, school, admin, db):
        other_school = SchoolFactory()
        foreign_classroom = ClassroomFactory(
            school=other_school,
            grade=GradeFactory(school=other_school),
            academic_year=AcademicYearFactory(school=other_school),
        )
        resp = _auth(api, admin).get(ATTENDANCE_CLASSROOM_SUMMARY, {"classroom_id": str(foreign_classroom.id)})
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert "not found in your school" in str(resp.data)


# ─── Students: restore / documents ───────────────────────────────────────────


class TestStudentRestore:
    def test_restore_student_denied(self, api, school, student, db):
        pupil = StudentFactory(school=school)
        resp = _auth(api, student).post(f"{STUDENTS_LIST}{pupil.id}/restore/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_restore_admin_allowed(self, api, school, admin, db):
        pupil = StudentFactory(school=school)
        pupil.is_active = False
        pupil.save(update_fields=["is_active"])
        resp = _auth(api, admin).post(f"{STUDENTS_LIST}{pupil.id}/restore/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert "restored" in resp.json()["detail"].lower()
        pupil.refresh_from_db()
        assert pupil.is_active is True


class TestStudentDocuments:
    def test_documents_post_student_denied(self, api, school, student, db):
        pupil = StudentFactory(school=school)
        upload = SimpleUploadedFile("cert.pdf", b"%PDF-1.4 test content", content_type="application/pdf")
        resp = _auth(api, student).post(
            f"{STUDENTS_LIST}{pupil.id}/documents/",
            {"document_type": "birth_cert", "title": "BC", "file": upload},
            format="multipart",
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_documents_post_admin_allowed(self, api, school, admin, db):
        pupil = StudentFactory(school=school)
        upload = SimpleUploadedFile("cert.pdf", b"%PDF-1.4 test content", content_type="application/pdf")
        resp = _auth(api, admin).post(
            f"{STUDENTS_LIST}{pupil.id}/documents/",
            {"document_type": "birth_cert", "title": "BC", "file": upload},
            format="multipart",
        )
        assert resp.status_code == status.HTTP_201_CREATED


# ─── Inventory: adjust-stock / receive-items ─────────────────────────────────


class TestInventoryActions:
    def test_adjust_stock_student_denied(self, api, school, student, db):
        from services.inventory.models import InventoryItem

        item = InventoryItem.objects.create(school=school, name="Pens", sku="SKU-ADJ-1")
        resp = _auth(api, student).post(
            f"{INVENTORY_ITEMS}{item.id}/adjust-stock/", {"movement_type": "adjustment", "quantity": 5}, format="json"
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_adjust_stock_teacher_allowed(self, api, school, teacher, db):
        from services.inventory.models import InventoryItem

        item = InventoryItem.objects.create(school=school, name="Pens", sku="SKU-ADJ-2")
        resp = _auth(api, teacher).post(
            f"{INVENTORY_ITEMS}{item.id}/adjust-stock/", {"movement_type": "adjustment", "quantity": 5}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert item.current_stock == 5

    def test_receive_items_student_denied(self, api, school, student, db):
        from services.inventory.models import PurchaseOrder

        po = PurchaseOrder.objects.create(school=school, order_number="PO-RBAC-1", order_date=date.today())
        resp = _auth(api, student).post(f"{INVENTORY_PURCHASE_ORDERS}{po.id}/receive/", {"items": []}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_receive_items_admin_allowed(self, api, school, admin, db):
        from services.inventory.models import InventoryItem, PurchaseOrder, PurchaseOrderItem

        item = InventoryItem.objects.create(school=school, name="Pens", sku="SKU-RX-2")
        po = PurchaseOrder.objects.create(school=school, order_number="PO-RBAC-2", order_date=date.today())
        PurchaseOrderItem.objects.create(
            purchase_order=po, item=item, quantity_ordered=10, unit_price=10, total_price=100
        )
        resp = _auth(api, admin).post(
            f"{INVENTORY_PURCHASE_ORDERS}{po.id}/receive/",
            {"items": [{"item_id": str(item.id), "quantity_received": 5}]},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert item.current_stock == 5


# ─── Conferences: create-zoom / delete-zoom / complete ───────────────────────


class TestConferenceZoomActions:
    def _slot(self, school, teacher):
        from services.conferences.models import ConferenceSlot

        return ConferenceSlot.objects.create(
            school=school,
            teacher=teacher,
            date=date.today(),
            start_time="09:00",
            end_time="09:30",
            is_booked=False,
        )

    def test_create_zoom_student_denied(self, api, school, student, db):
        slot = self._slot(school, TeacherUserFactory(school=school))
        resp = _auth(api, student).post(f"{CONFERENCES_SLOTS}{slot.id}/create-zoom/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @mock.patch(
        "services.conferences.zoom_service.create_meeting",
        return_value={
            "id": "123456",
            "join_url": "https://zoom.us/j/123456",
            "start_url": "https://zoom.us/s/123456",
            "password": "",
        },
    )
    def test_create_zoom_admin_allowed(self, mock_meeting, api, school, admin, db):
        slot = self._slot(school, TeacherUserFactory(school=school))
        slot.is_booked = True
        slot.save()
        resp = _auth(api, admin).post(f"{CONFERENCES_SLOTS}{slot.id}/create-zoom/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        slot.refresh_from_db()
        assert slot.is_zoom_created is True

    def test_delete_zoom_student_denied(self, api, school, student, db):
        slot = self._slot(school, TeacherUserFactory(school=school))
        resp = _auth(api, student).post(f"{CONFERENCES_SLOTS}{slot.id}/delete-zoom/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @mock.patch("services.conferences.zoom_service.delete_meeting", return_value=True)
    def test_delete_zoom_admin_allowed(self, mock_delete, api, school, admin, db):
        slot = self._slot(school, TeacherUserFactory(school=school))
        slot.is_booked = True
        slot.is_zoom_created = True
        slot.zoom_meeting_id = "123456"
        slot.save()
        resp = _auth(api, admin).post(f"{CONFERENCES_SLOTS}{slot.id}/delete-zoom/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        slot.refresh_from_db()
        assert slot.is_zoom_created is False

    def test_complete_student_denied(self, api, school, student, db):
        slot = self._slot(school, TeacherUserFactory(school=school))
        slot.is_booked = True
        slot.save()
        resp = _auth(api, student).post(f"{CONFERENCES_SLOTS}{slot.id}/complete/", {}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_complete_teacher_allowed(self, api, school, teacher, db):
        slot = self._slot(school, teacher)
        slot.is_booked = True
        slot.save()
        resp = _auth(api, teacher).post(f"{CONFERENCES_SLOTS}{slot.id}/complete/", {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        from services.conferences.models import ConferenceSlot

        assert not ConferenceSlot.objects.filter(pk=slot.pk).exists()


# ─── Communication: cross-school conversation ────────────────────────────────


class TestCommunicationCrossSchool:
    def test_conversation_with_other_school_user_403(self, api, school, admin, db):
        other_school = SchoolFactory()
        other_user = UserFactory(school=other_school)
        resp = _auth(api, admin).get(f"{COMMUNICATION_MESSAGES}conversation/{other_user.id}/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert "your school" in str(resp.data)


# ─── Reporting: spoofed X-School-ID header must not leak other school data ───


class TestReportingDashboardSpoof:
    def test_dashboard_stats_ignores_spoofed_school_header(self, api, school, admin, db):
        other_school = SchoolFactory()
        for _ in range(3):
            StudentFactory(school=school)
        for _ in range(5):
            StudentFactory(school=other_school)

        resp = _auth(api, admin).get(REPORTING_DASHBOARD_STATS, HTTP_X_SCHOOL_ID=str(other_school.id))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total_students"] == 3  # caller's school, never the spoofed one


# ─── Tenant middleware: authenticated users cannot be re-scoped via header ────


class TestTenantMiddlewareSpoof:
    def test_middleware_keeps_authenticated_users_own_school(self, db, admin):
        from core.middleware.tenant import TenantMiddleware
        from django.http import HttpResponse
        from rest_framework.test import APIRequestFactory

        other_school = SchoolFactory()
        captured = {}

        def get_response(request):
            captured["school"] = request.school
            return HttpResponse("ok")

        request = APIRequestFactory().get("/api/v1/gradebook/exams/", HTTP_X_SCHOOL_ID=str(other_school.id))
        request.user = admin
        TenantMiddleware(get_response)(request)
        assert captured["school"] == admin.school
        assert captured["school"] != other_school

    def test_spoofed_header_end_to_end_returns_own_school_data(self, api, school, admin, db):
        """A tenant-scoped endpoint must serve school A data when an
        authenticated school-A user sends X-School-ID: <school_b>."""
        other_school = SchoolFactory()
        year = AcademicYearFactory(school=school, is_current=True)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=year)
        resp = _auth(api, admin).get(
            ATTENDANCE_CLASSROOM_SUMMARY,
            {"classroom_id": str(classroom.id), "date": date.today().isoformat()},
            HTTP_X_SCHOOL_ID=str(other_school.id),
        )
        # If the header had re-scoped the tenant to school B, this classroom
        # lookup would have failed with 403. It must resolve against school A.
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total_students"] == 0
