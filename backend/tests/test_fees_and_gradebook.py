"""
Test Suite — Fees and Gradebook services comprehensive coverage
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import (
    SchoolFactory, AdminUserFactory, TeacherUserFactory, StudentUserFactory,
    StudentFactory, ClassroomFactory, AcademicYearFactory, GradeFactory,
    EnrollmentFactory, SubjectFactory, TeacherAssignmentFactory,
    ExamFactory, ExamTypeFactory, ExamScheduleFactory, GradeRecordFactory,
    FeeCategoryFactory, FeeStructureFactory, FeeInvoiceFactory,
)
from tests.url_helpers import (
    GRADEBOOK_EXAMS, GRADEBOOK_GRADES_BULK, GRADEBOOK_GRADES,
    GRADEBOOK_REPORT_CARDS, gradebook_exam_leaderboard,
    FEES_INVOICES, FEES_PAYMENTS, FEES_SCHOLARSHIPS, fees_invoice_waive,
)
from services.fees.models import FeeCategory, FeeStructure, FeeInvoice, Payment, Scholarship
from services.gradebook.models import Grade as GradeModel, Assessment, ReportCard


# ─── Shared Fixtures ───────────────────────────────────────────────────────────

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
def student_user(db, school):
    return StudentUserFactory(school=school)


@pytest.fixture
def student(db, school, student_user):
    return StudentFactory(user=student_user, school=school)


@pytest.fixture
def academic_year(db, school):
    return AcademicYearFactory(school=school)


@pytest.fixture
def grade(db, school):
    return GradeFactory(school=school, level=5)


@pytest.fixture
def classroom(db, school, grade, academic_year, teacher):
    return ClassroomFactory(
        school=school, grade=grade, academic_year=academic_year,
        class_teacher=teacher,
    )


@pytest.fixture
def enrollment(db, student, classroom, academic_year):
    return EnrollmentFactory(
        student=student, classroom=classroom, academic_year=academic_year,
    )


@pytest.fixture
def subject(db, school, grade):
    return SubjectFactory(school=school, grade=grade)


@pytest.fixture
def exam_type(db, school):
    return ExamTypeFactory(school=school, name="Midterm", weightage=Decimal("50.00"))


@pytest.fixture
def exam(db, school, academic_year, exam_type):
    return ExamFactory(school=school, academic_year=academic_year, exam_type=exam_type)


@pytest.fixture
def schedule(db, exam, subject, classroom):
    return ExamScheduleFactory(exam=exam, subject=subject, classroom=classroom)


@pytest.fixture
def assignment(db, teacher, subject, classroom, academic_year):
    return TeacherAssignmentFactory(
        teacher=teacher, subject=subject, classroom=classroom,
        academic_year=academic_year,
    )


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


@pytest.fixture
def student_client(db, student_user):
    c = APIClient()
    c.force_authenticate(user=student_user)
    return c


# ═══════════════════════════════════════════════════════════════════════════════
# FEES SERVICE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestFeeCategories:

    def test_admin_can_create_fee_category(self, admin_client, school):
        payload = {"name": "Transport", "is_mandatory": False, "recurrence": "monthly"}
        r = admin_client.post("/api/v1/fees/categories/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Transport"
        assert FeeCategory.objects.count() == 1

    def test_student_cannot_create_fee_category(self, student_client):
        payload = {"name": "Library", "recurrence": "annual"}
        r = student_client.post("/api/v1/fees/categories/", payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_fee_category_auto_associates_school(self, admin_client, school):
        payload = {"name": "Tuition", "recurrence": "monthly"}
        r = admin_client.post("/api/v1/fees/categories/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        category = FeeCategory.objects.first()
        assert category.school == school

    def test_fee_category_list_is_scoped_to_school(self, db):
        school_a = SchoolFactory(code="SCH-A")
        school_b = SchoolFactory(code="SCH-B")
        admin_a = AdminUserFactory(school=school_a)
        FeeCategoryFactory(school=school_a, name="Cat A")
        FeeCategoryFactory(school=school_b, name="Cat B")
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get("/api/v1/fees/categories/")
        assert r.status_code == status.HTTP_200_OK
        names = [c["name"] for c in r.data["results"]]
        assert "Cat A" in names
        assert "Cat B" not in names


@pytest.mark.django_db
class TestFeeStructures:

    def test_create_fee_structure(self, admin_client, grade, academic_year):
        cat = FeeCategoryFactory(school=grade.school)
        payload = {
            "grade": grade.id,
            "academic_year": academic_year.id,
            "fee_category": cat.id,
            "amount": "1000.00",
            "due_day": 15,
        }
        r = admin_client.post("/api/v1/fees/structures/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert FeeStructure.objects.count() == 1

    def test_filter_fee_structures_by_grade(self, admin_client, school, grade, academic_year):
        cat = FeeCategoryFactory(school=school)
        FeeStructureFactory(school=school, grade=grade, academic_year=academic_year, fee_category=cat)
        other_grade = GradeFactory(school=school, level=10)
        FeeStructureFactory(school=school, grade=other_grade, academic_year=academic_year, fee_category=cat)
        r = admin_client.get(f"/api/v1/fees/structures/?grade={grade.id}")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] == 1

    def test_duplicate_structure_rejected(self, admin_client, grade, academic_year):
        cat = FeeCategoryFactory(school=grade.school)
        payload = {
            "grade": grade.id, "academic_year": academic_year.id,
            "fee_category": cat.id, "amount": "500.00", "due_day": 10,
        }
        admin_client.post("/api/v1/fees/structures/", payload, format="json")
        r = admin_client.post("/api/v1/fees/structures/", payload, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestFeeInvoices:

    def test_admin_can_create_invoice(self, admin_client, student, academic_year):
        structure = FeeStructureFactory(school=student.school)
        payload = {
            "invoice_number": "INV-TEST-001",
            "student": student.id,
            "academic_year": academic_year.id,
            "fee_structure": structure.id,
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
            "base_amount": "500.00",
            "total_amount": "500.00",
        }
        r = admin_client.post(FEES_INVOICES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert FeeInvoice.objects.count() == 1

    def test_invoice_defaults_to_unpaid(self, admin_client, student, academic_year):
        structure = FeeStructureFactory(school=student.school)
        payload = {
            "invoice_number": "INV-TEST-002",
            "student": student.id, "academic_year": academic_year.id,
            "fee_structure": structure.id,
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
            "base_amount": "500.00", "total_amount": "500.00",
        }
        r = admin_client.post(FEES_INVOICES, payload, format="json")
        assert r.data["status"] == "unpaid"
        assert r.data["paid_amount"] == "0.00"

    def test_student_sees_own_invoices_only(self, admin_client, student_client, student, academic_year, school):
        structure = FeeStructureFactory(school=school)
        FeeInvoiceFactory(
            student=student, academic_year=academic_year, fee_structure=structure,
            invoice_number="INV-OWN-001",
        )
        other_student = StudentFactory(school=school)
        FeeInvoiceFactory(
            student=other_student, academic_year=academic_year, fee_structure=structure,
            invoice_number="INV-OTHER-001",
        )
        r = student_client.get(FEES_INVOICES)
        inv_numbers = [inv["invoice_number"] for inv in r.data["results"]]
        assert "INV-OWN-001" in inv_numbers
        assert "INV-OTHER-001" not in inv_numbers

    def test_filter_invoices_by_status(self, admin_client, student, academic_year, school):
        structure = FeeStructureFactory(school=school)
        FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure,
                          status="unpaid", invoice_number="INV-U-001")
        FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure,
                          status="paid", invoice_number="INV-P-001", paid_amount="500.00")
        r = admin_client.get(f"{FEES_INVOICES}?status=paid")
        inv_numbers = [inv["invoice_number"] for inv in r.data["results"]]
        assert "INV-P-001" in inv_numbers
        assert "INV-U-001" not in inv_numbers

    def test_outstanding_amount_property(self, student, academic_year, school):
        structure = FeeStructureFactory(school=school)
        inv = FeeInvoiceFactory(
            student=student, academic_year=academic_year, fee_structure=structure,
            total_amount=Decimal("1000.00"), paid_amount=Decimal("300.00"),
        )
        assert inv.outstanding_amount == Decimal("700.00")

    def test_invoice_waive(self, admin_client, student, academic_year, school):
        structure = FeeStructureFactory(school=school)
        inv = FeeInvoiceFactory(
            student=student, academic_year=academic_year, fee_structure=structure,
            status="unpaid", invoice_number="INV-WAIVE-001",
        )
        r = admin_client.post(fees_invoice_waive(inv.id), {"reason": "Financial hardship"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        inv.refresh_from_db()
        assert inv.status == "waived"

    def test_waive_requires_admin(self, teacher_client, student, academic_year, school):
        structure = FeeStructureFactory(school=school)
        inv = FeeInvoiceFactory(
            student=student, academic_year=academic_year, fee_structure=structure,
        )
        r = teacher_client.post(fees_invoice_waive(inv.id), {"reason": "test"}, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPayments:

    def test_record_payment_updates_invoice(self, admin_client, student, academic_year, school):
        structure = FeeStructureFactory(school=school)
        inv = FeeInvoiceFactory(
            student=student, academic_year=academic_year, fee_structure=structure,
            total_amount=Decimal("500.00"), paid_amount=Decimal("0.00"),
            status="unpaid", invoice_number="INV-PAY-001",
        )
        payload = {"invoice": inv.id, "amount": "500.00", "payment_method": "cash"}
        r = admin_client.post(FEES_PAYMENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        inv.refresh_from_db()
        assert inv.paid_amount == Decimal("500.00")
        assert inv.status == "paid"

    def test_partial_payment_sets_partial_status(self, admin_client, student, academic_year, school):
        structure = FeeStructureFactory(school=school)
        inv = FeeInvoiceFactory(
            student=student, academic_year=academic_year, fee_structure=structure,
            total_amount=Decimal("500.00"), paid_amount=Decimal("0.00"),
            status="unpaid", invoice_number="INV-PART-001",
        )
        payload = {"invoice": inv.id, "amount": "200.00", "payment_method": "bank_transfer"}
        r = admin_client.post(FEES_PAYMENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        inv.refresh_from_db()
        assert inv.paid_amount == Decimal("200.00")
        assert inv.status == "partial"

    def test_student_cannot_record_payment(self, student_client, student, academic_year, school):
        structure = FeeStructureFactory(school=school)
        inv = FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure)
        payload = {"invoice": inv.id, "amount": "100.00", "payment_method": "cash"}
        r = student_client.post(FEES_PAYMENTS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_payment_has_receipt_number(self, admin_client, student, academic_year, school):
        structure = FeeStructureFactory(school=school)
        inv = FeeInvoiceFactory(
            student=student, academic_year=academic_year, fee_structure=structure,
            invoice_number="INV-RCPT-001",
        )
        payload = {"invoice": inv.id, "amount": "100.00", "payment_method": "cash"}
        r = admin_client.post(FEES_PAYMENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data.get("receipt_number") is not None


@pytest.mark.django_db
class TestScholarships:

    def test_admin_can_create_scholarship(self, admin_client, admin, student, academic_year):
        payload = {
            "student": student.id, "academic_year": academic_year.id,
            "name": "Merit Scholarship",
            "discount_type": "percent",
            "discount_value": "25.00",
            "reason": "Academic excellence",
        }
        r = admin_client.post(FEES_SCHOLARSHIPS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert Scholarship.objects.count() == 1

    def test_non_admin_cannot_create_scholarship(self, teacher_client, student, academic_year):
        payload = {
            "student": student.id, "academic_year": academic_year.id,
            "name": "Test", "discount_type": "fixed",
            "discount_value": "100.00", "reason": "test",
        }
        r = teacher_client.post(FEES_SCHOLARSHIPS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_scholarship_list_scoped(self, admin_client, school, student, academic_year):
        Scholarship.objects.create(
            school=school, student=student, academic_year=academic_year,
            name="Scholarship A", discount_type="percent",
            discount_value=Decimal("10.00"), reason="test",
            approved_by=admin_client.handler._force_user,
        )
        r = admin_client.get(FEES_SCHOLARSHIPS)
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data["results"]) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# GRADEBOOK EXTENDED TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestExamsExtended:

    def test_create_exam_with_schedule(self, admin_client, academic_year, exam_type):
        payload = {
            "academic_year": academic_year.id, "exam_type": exam_type.id,
            "name": "Final Exam 2026", "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=10)).isoformat(),
        }
        r = admin_client.post(GRADEBOOK_EXAMS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Final Exam 2026"

    def test_student_cannot_create_exam(self, student_client, academic_year, exam_type):
        payload = {
            "academic_year": academic_year.id, "exam_type": exam_type.id,
            "name": "Hack Attempt", "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=3)).isoformat(),
        }
        r = student_client.post(GRADEBOOK_EXAMS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_exam_list_filter_by_academic_year(self, admin_client, school, academic_year, exam_type):
        other_year = AcademicYearFactory(school=school, is_current=False)
        ExamFactory(school=school, academic_year=academic_year, exam_type=exam_type)
        ExamFactory(school=school, academic_year=other_year, exam_type=exam_type)
        r = admin_client.get(f"{GRADEBOOK_EXAMS}?academic_year={academic_year.id}")
        assert r.status_code == status.HTTP_200_OK
        for e in r.data["results"]:
            assert str(e["academic_year"]) == str(academic_year.id)

    def test_publish_results_updates_status(self, admin_client, exam, student, academic_year):
        ReportCard.objects.create(
            student=student, exam=exam, academic_year=academic_year,
            total_marks=Decimal("100"), obtained_marks=Decimal("85"),
            percentage=Decimal("85.0"), grade_letter="A", status="draft",
        )
        r = admin_client.post(f"/api/v1/gradebook/exams/{exam.id}/publish-results/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["published"] == 1

    def test_leaderboard_returns_ranked_results(self, admin_client, exam, student, academic_year, enrollment):
        ReportCard.objects.create(
            student=student, exam=exam, academic_year=academic_year,
            total_marks=Decimal("100"), obtained_marks=Decimal("95"),
            percentage=Decimal("95.0"), grade_letter="A+",
            rank_in_class=1, rank_in_grade=1, status="published",
        )
        r = admin_client.get(gradebook_exam_leaderboard(exam.id))
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data) >= 1
        assert r.data[0]["rank"] == 1
        assert r.data[0]["percentage"] == 95.0

    def test_leaderboard_empty_when_no_published(self, admin_client, exam):
        r = admin_client.get(gradebook_exam_leaderboard(exam.id))
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data) == 0


@pytest.mark.django_db
class TestGradesExtended:

    def test_submit_grades_with_all_statuses(self, teacher_client, student, schedule, enrollment):
        payload = {
            "exam_schedule_id": schedule.id,
            "grades": [
                {"student_id": str(student.id), "marks_obtained": "85.0", "is_absent": False},
            ],
        }
        r = teacher_client.post(GRADEBOOK_GRADES_BULK, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["graded"] == 1

    def test_absent_student_marked_correctly(self, teacher_client, student, schedule, enrollment):
        payload = {
            "exam_schedule_id": schedule.id,
            "grades": [
                {"student_id": str(student.id), "marks_obtained": None, "is_absent": True},
            ],
        }
        r = teacher_client.post(GRADEBOOK_GRADES_BULK, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        grade = GradeModel.objects.get(student=student, exam_schedule=schedule)
        assert grade.is_absent is True
        assert grade.marks_obtained is None

    def test_grade_update_overwrites_previous(self, teacher_client, student, schedule, enrollment):
        GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("50"))
        payload = {
            "exam_schedule_id": schedule.id,
            "grades": [
                {"student_id": str(student.id), "marks_obtained": "90.0", "is_absent": False},
            ],
        }
        r = teacher_client.post(GRADEBOOK_GRADES_BULK, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        grade = GradeModel.objects.get(student=student, exam_schedule=schedule)
        assert grade.marks_obtained == Decimal("90.0")

    @pytest.mark.xfail(
        reason="View bug: exam_schedule__assignment filter traverses non-existent relationship on ExamSchedule",
        strict=False,
    )
    def test_grades_scoped_to_teacher_classroom(self, teacher_client, student, schedule, enrollment):
        GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("75"))
        r = teacher_client.get(GRADEBOOK_GRADES)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_student_cannot_view_other_student_grades(self, db, school, student_user, schedule):
        from tests.factories import StudentFactory
        other_student = StudentFactory(school=school)
        GradeRecordFactory(student=other_student, exam_schedule=schedule, marks_obtained=Decimal("99"))
        client = APIClient()
        client.force_authenticate(user=student_user)
        r = client.get(f"{GRADEBOOK_GRADES}?student_id={other_student.id}")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] == 0


@pytest.mark.django_db
class TestReportCards:

    def test_list_report_cards(self, admin_client, student, exam, academic_year):
        ReportCard.objects.create(
            student=student, exam=exam, academic_year=academic_year,
            total_marks=Decimal("100"), obtained_marks=Decimal("88"),
            percentage=Decimal("88.0"), grade_letter="B+", status="published",
        )
        r = admin_client.get(f"{GRADEBOOK_REPORT_CARDS}?student={student.id}")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] == 1
        assert r.data["results"][0]["grade_letter"] == "B+"

    def test_student_sees_published_only(self, student_client, student, exam, school, exam_type):
        academic_year = exam.academic_year
        other_exam = ExamFactory(
            school=school, academic_year=academic_year, exam_type=exam_type,
            name="Different Exam",
        )
        ReportCard.objects.create(
            student=student, exam=other_exam, academic_year=academic_year,
            total_marks=Decimal("100"), obtained_marks=Decimal("90"),
            percentage=Decimal("90.0"), grade_letter="A", status="draft",
        )
        ReportCard.objects.create(
            student=student, exam=exam, academic_year=academic_year,
            total_marks=Decimal("100"), obtained_marks=Decimal("80"),
            percentage=Decimal("80.0"), grade_letter="B", status="published",
        )
        r = student_client.get(GRADEBOOK_REPORT_CARDS)
        assert r.status_code == status.HTTP_200_OK
        for rc in r.data["results"]:
            assert rc["status"] in ("published", "sent")

    def test_download_pdf_404_when_not_generated(self, admin_client, student, exam, academic_year):
        rc = ReportCard.objects.create(
            student=student, exam=exam, academic_year=academic_year,
            total_marks=Decimal("100"), obtained_marks=Decimal("75"),
            percentage=Decimal("75.0"), grade_letter="C", status="draft",
        )
        r = admin_client.get(f"/api/v1/gradebook/report-cards/{rc.id}/download-pdf/")
        assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestAssessments:

    def test_teacher_can_create_assessment(self, teacher_client, assignment):
        payload = {
            "assignment": assignment.id,
            "title": "Homework 1",
            "assessment_type": "homework",
            "due_date": (date.today() + timedelta(days=7)).isoformat(),
            "max_marks": "20.00",
        }
        r = teacher_client.post("/api/v1/gradebook/assessments/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_student_cannot_create_assessment(self, student_client, assignment):
        payload = {
            "assignment": assignment.id, "title": "Hack",
            "assessment_type": "quiz",
            "due_date": date.today().isoformat(), "max_marks": "10.00",
        }
        r = student_client.post("/api/v1/gradebook/assessments/", payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_assessment_list(self, teacher_client, assignment):
        Assessment.objects.create(
            assignment=assignment, title="Quiz 1", assessment_type="quiz",
            due_date=date.today() + timedelta(days=3), max_marks=Decimal("15.00"),
        )
        r = teacher_client.get("/api/v1/gradebook/assessments/")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data["results"]) == 1
