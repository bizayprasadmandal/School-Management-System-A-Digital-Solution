"""
Test Suite — Gap-Closure Features
Covers the audit-trail and analytics/import gaps identified in the
real-world product audit:

  1. Grade-change audit log (create/update/delete/bulk/import + history endpoint)
  2. Reporting analytics: at-risk students, enrollment funnel, fee forecast
  3. Attendance CSV bulk import
  4. Fee invoice CSV bulk import
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from services.gradebook.models import Grade
from tests.factories import (
    AcademicYearFactory,
    AdminUserFactory,
    ApplicationFactory,
    AttendanceRecordFactory,
    ClassroomFactory,
    EnrollmentFactory,
    EnrollmentIntakeFactory,
    ExamScheduleFactory,
    FeeCategoryFactory,
    FeeInvoiceFactory,
    FeeStructureFactory,
    GradeFactory,
    GradeRecordFactory,
    SchoolFactory,
    StudentFactory,
    TeacherUserFactory,
)
from tests.url_helpers import (
    ATTENDANCE_IMPORT_CSV,
    FEES_INVOICES_IMPORT_CSV,
    GRADEBOOK_GRADES,
    GRADEBOOK_GRADES_BULK,
    GRADEBOOK_GRADES_HISTORY,
    GRADEBOOK_GRADES_IMPORT_CSV,
    GRADEBOOK_PROPOSALS,
    REPORTING_AT_RISK_STUDENTS,
    REPORTING_ENROLLMENT_FUNNEL,
    REPORTING_FEE_FORECAST,
    admissions_application_accept_offer,
    admissions_application_complete_tour,
    admissions_application_enroll,
    admissions_application_schedule_tour,
    admissions_application_send_offer,
    admissions_application_update_status,
    gradebook_proposal_approve,
    gradebook_proposal_reject,
)

# ─── Shared fixtures ──────────────────────────────────────────────────────────


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
def api():
    return APIClient()


def auth(client, user, password="TestPass@1234"):
    client.force_authenticate(user=user)
    return client


# ─── Grade-change audit trail ─────────────────────────────────────────────────


class TestGradeAuditTrail:
    def test_create_grade_logs_audit_entry(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school)
        auth(api, teacher)
        resp = api.post(
            GRADEBOOK_GRADES,
            {"student": str(student.id), "exam_schedule": schedule.id, "marks_obtained": "85.00", "is_absent": False},
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.content

        # Audit trail review is admin-only; re-auth as an admin to read it.
        auth(api, admin)
        entries = api.get(GRADEBOOK_GRADES_HISTORY).json()
        assert len(entries) == 1
        assert entries[0]["action"] == "create"
        assert entries[0]["student_name"] == student.user.full_name
        assert entries[0]["marks_obtained_new"] == 85.00
        assert entries[0]["marks_obtained_old"] is None
        assert entries[0]["changed_by"] == teacher.full_name

    def test_update_grade_captures_old_and_new_values(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school, invigilator=teacher)
        grade = GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("50.00"))
        auth(api, teacher)

        resp = api.patch(
            f"{GRADEBOOK_GRADES}{grade.id}/",
            {"marks_obtained": "90.00"},
            format="json",
        )
        assert resp.status_code == 200, resp.content

        auth(api, admin)
        history = api.get(GRADEBOOK_GRADES_HISTORY).json()
        # The factory-created grade predates the view, so only the update is logged.
        assert len(history) == 1
        assert history[0]["action"] == "update"
        assert history[0]["marks_obtained_old"] == 50.00
        assert history[0]["marks_obtained_new"] == 90.00

    def test_delete_grade_logs_audit_entry(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school, invigilator=teacher)
        grade = GradeRecordFactory(student=student, exam_schedule=schedule)
        auth(api, teacher)

        resp = api.delete(f"{GRADEBOOK_GRADES}{grade.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        auth(api, admin)
        history = api.get(GRADEBOOK_GRADES_HISTORY).json()
        assert any(e["action"] == "delete" for e in history)

    def test_bulk_submit_logs_audit_entries(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school)
        auth(api, teacher)

        resp = api.post(
            GRADEBOOK_GRADES_BULK,
            {
                "exam_schedule_id": schedule.id,
                "grades": [
                    {"student_id": str(student.id), "marks_obtained": "77.50", "is_absent": False},
                ],
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.content

        auth(api, admin)
        history = api.get(GRADEBOOK_GRADES_HISTORY).json()
        assert len(history) == 1
        assert history[0]["action"] == "create"
        assert history[0]["marks_obtained_new"] == 77.50

    def test_import_csv_logs_audit_entries(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school)
        auth(api, teacher)

        csv_data = (
            "admission_number,exam_schedule_id,marks_obtained,is_absent,remarks\n"
            f"{student.admission_number},{schedule.id},66.00,false,good\n"
        )
        resp = api.post(GRADEBOOK_GRADES_IMPORT_CSV, {"csv_data": csv_data}, format="json")
        assert resp.status_code == 200, resp.content
        assert resp.json()["imported"] == 1

        auth(api, admin)
        history = api.get(GRADEBOOK_GRADES_HISTORY).json()
        assert len(history) == 1
        assert history[0]["action"] == "create"
        assert history[0]["marks_obtained_new"] == 66.00

    def test_history_is_tenant_scoped(self, api, school, admin, teacher, db):
        from services.gradebook.models import record_grade_change

        other_school = SchoolFactory()
        other_admin = AdminUserFactory(school=other_school)
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school)
        grade = GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("70.00"))
        record_grade_change(grade, "create", admin)

        # An audit entry in ANOTHER school must not leak into this school's history.
        other_student = StudentFactory(school=other_school)
        other_schedule = ExamScheduleFactory(exam__school=other_school, classroom__school=other_school)
        other_grade = GradeRecordFactory(
            student=other_student, exam_schedule=other_schedule, marks_obtained=Decimal("80.00")
        )
        record_grade_change(other_grade, "create", other_admin)

        auth(api, admin)
        history = api.get(GRADEBOOK_GRADES_HISTORY).json()
        names = {e["admission_number"] for e in history}
        assert other_student.admission_number not in names
        assert student.admission_number in names


# ─── Grade-change approval workflow ──────────────────────────────────────────


class TestGradeApprovalWorkflow:
    @staticmethod
    def _publish_report_card(student, schedule):
        from django.utils import timezone
        from services.gradebook.models import ReportCard

        return ReportCard.objects.create(
            student=student,
            exam=schedule.exam,
            academic_year=schedule.exam.academic_year,
            status="published",
            published_at=timezone.now(),
        )

    def test_update_published_grade_becomes_proposal_not_applied(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school, invigilator=teacher)
        grade = GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("50.00"))
        self._publish_report_card(student, schedule)

        auth(api, teacher)
        resp = api.patch(f"{GRADEBOOK_GRADES}{grade.id}/", {"marks_obtained": "90.00"}, format="json")
        assert resp.status_code == status.HTTP_202_ACCEPTED, resp.content
        assert resp.json()["status"] == "pending_approval"

        # Grade untouched; proposal created
        grade.refresh_from_db()
        assert grade.marks_obtained == Decimal("50.00")

        auth(api, admin)
        data = api.get(GRADEBOOK_PROPOSALS).json()
        assert len(data["results"]) == 1
        prop = data["results"][0]
        assert prop["status"] == "proposed"
        assert prop["action"] == "update"
        assert float(prop["marks_obtained_new"]) == 90.0
        assert float(prop["marks_obtained_current"]) == 50.0
        assert prop["proposed_by"] == teacher.full_name

    def test_approve_applies_change_and_writes_audit(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school, invigilator=teacher)
        grade = GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("50.00"))
        self._publish_report_card(student, schedule)

        auth(api, teacher)
        proposed = api.patch(f"{GRADEBOOK_GRADES}{grade.id}/", {"marks_obtained": "90.00"}, format="json").json()

        auth(api, admin)
        resp = api.post(gradebook_proposal_approve(proposed["proposal_id"]), {}, format="json")
        assert resp.status_code == 200, resp.content
        assert resp.json()["status"] == "approved"

        grade.refresh_from_db()
        assert grade.marks_obtained == Decimal("90.00")

        # Approval lands in the immutable audit trail as a normal update
        history = api.get(GRADEBOOK_GRADES_HISTORY).json()
        assert any(
            e["action"] == "update" and e["marks_obtained_old"] == 50.0 and e["marks_obtained_new"] == 90.0
            for e in history
        )

    def test_reject_leaves_grade_unchanged(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school, invigilator=teacher)
        grade = GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("50.00"))
        self._publish_report_card(student, schedule)

        auth(api, teacher)
        proposed = api.patch(f"{GRADEBOOK_GRADES}{grade.id}/", {"marks_obtained": "90.00"}, format="json").json()

        auth(api, admin)
        resp = api.post(
            gradebook_proposal_reject(proposed["proposal_id"]), {"notes": "Incorrect re-mark"}, format="json"
        )
        assert resp.status_code == 200, resp.content
        assert resp.json()["status"] == "rejected"

        grade.refresh_from_db()
        assert grade.marks_obtained == Decimal("50.00")

        # No audit entry is written for a rejected change
        history = api.get(GRADEBOOK_GRADES_HISTORY).json()
        assert not any(e["marks_obtained_new"] == 90.0 for e in history)

        prop = api.get(GRADEBOOK_PROPOSALS).json()["results"][0]
        assert prop["status"] == "rejected"
        assert prop["review_notes"] == "Incorrect re-mark"

    def test_delete_published_grade_requires_approval(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school, invigilator=teacher)
        grade = GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("50.00"))
        self._publish_report_card(student, schedule)

        auth(api, teacher)
        resp = api.delete(f"{GRADEBOOK_GRADES}{grade.id}/")
        assert resp.status_code == status.HTTP_202_ACCEPTED, resp.content
        assert Grade.objects.filter(id=grade.id).exists()  # still there

        auth(api, admin)
        prop = api.get(GRADEBOOK_PROPOSALS).json()["results"][0]
        assert prop["action"] == "delete"
        api.post(gradebook_proposal_approve(prop["id"]), {}, format="json")

        assert not Grade.objects.filter(id=grade.id).exists()
        history = api.get(GRADEBOOK_GRADES_HISTORY).json()
        assert any(e["action"] == "delete" for e in history)

    def test_bulk_submit_splits_published_and_unpublished(self, api, school, admin, teacher, db):
        published_student = StudentFactory(school=school)
        unpublished_student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school)
        self._publish_report_card(published_student, schedule)

        auth(api, teacher)
        resp = api.post(
            GRADEBOOK_GRADES_BULK,
            {
                "exam_schedule_id": schedule.id,
                "grades": [
                    {"student_id": str(published_student.id), "marks_obtained": "85.00", "is_absent": False},
                    {"student_id": str(unpublished_student.id), "marks_obtained": "75.00", "is_absent": False},
                ],
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.content
        data = resp.json()
        assert data["graded"] == 1
        assert data["pending_approval"] == 1

        # Only the unpublished student's grade was created directly
        assert Grade.objects.filter(student=unpublished_student).exists()
        assert not Grade.objects.filter(student=published_student).exists()

    def test_create_new_grade_on_published_exam_proposes_then_applies(self, api, school, admin, teacher, db):
        student = StudentFactory(school=school)
        schedule = ExamScheduleFactory(exam__school=school, classroom__school=school, invigilator=teacher)
        self._publish_report_card(student, schedule)

        auth(api, teacher)
        resp = api.post(
            GRADEBOOK_GRADES,
            {"student": str(student.id), "exam_schedule": schedule.id, "marks_obtained": "88.00", "is_absent": False},
            format="json",
        )
        # Retroactive grade on a published exam also goes through approval
        assert resp.status_code == status.HTTP_202_ACCEPTED, resp.content
        assert not Grade.objects.filter(student=student, exam_schedule=schedule).exists()

        auth(api, admin)
        prop = api.get(GRADEBOOK_PROPOSALS).json()["results"][0]
        assert prop["action"] == "create"
        api.post(gradebook_proposal_approve(prop["id"]), {}, format="json")

        grade = Grade.objects.get(student=student, exam_schedule=schedule)
        assert grade.marks_obtained == Decimal("88.00")

    def test_proposals_are_tenant_scoped(self, api, school, admin, teacher, db):
        from services.gradebook.models import create_grade_change_proposal

        other_school = SchoolFactory()
        other_admin = AdminUserFactory(school=other_school)
        other_student = StudentFactory(school=other_school)
        other_schedule = ExamScheduleFactory(exam__school=other_school, classroom__school=other_school)
        create_grade_change_proposal(
            student=other_student,
            exam_schedule=other_schedule,
            action="update",
            proposed_by=other_admin,
        )

        own_student = StudentFactory(school=school)
        own_schedule = ExamScheduleFactory(exam__school=school, classroom__school=school)
        create_grade_change_proposal(student=own_student, exam_schedule=own_schedule, action="update")

        auth(api, admin)
        data = api.get(GRADEBOOK_PROPOSALS).json()
        names = {p["student_name"] for p in data["results"]}
        assert own_student.user.full_name in names
        assert other_student.user.full_name not in names


# ─── Standard notification templates (all schools) ───────────────────────────


class TestStandardNotificationTemplates:
    def test_new_school_auto_seeds_standard_templates(self, school, db):
        """A newly created school gets the 5 standard templates via post_save."""
        from services.communication.models import NotificationTemplate

        event_types = set(NotificationTemplate.objects.filter(school=school).values_list("event_type", flat=True))
        assert event_types == {
            "attendance_absent",
            "fee_due",
            "fee_overdue",
            "report_card_published",
            "announcement",
        }

    def test_seed_command_is_idempotent(self, school, db):
        """Running the seed command twice never duplicates templates."""
        from django.core.management import call_command
        from services.communication.models import NotificationTemplate

        call_command("seed_notification_templates", verbosity=0)
        call_command("seed_notification_templates", verbosity=0)
        assert NotificationTemplate.objects.filter(school=school).count() == 5

    def test_send_fee_reminders_routes_through_template_and_dedupes(self, school, db):
        """Invoices due in 3 days get a template-rendered reminder, once per invoice."""
        from services.communication.models import Notification
        from services.fees.tasks import send_fee_reminders

        student = StudentFactory(school=school)
        FeeInvoiceFactory(
            student=student,
            academic_year=AcademicYearFactory(school=school),
            due_date=date.today() + timedelta(days=3),
            status="unpaid",
        )

        result = send_fee_reminders()
        assert result["reminders_sent"] == 1

        reminder = Notification.objects.filter(user=student.user, title="Fee Reminder", channel="in_app").first()
        assert reminder is not None
        assert "Fee Reminder" in reminder.title
        assert reminder.reference_type == "fee_invoice"

        # Dedupe: a second run must not send again for the same invoice.
        assert send_fee_reminders()["reminders_sent"] == 0
        assert Notification.objects.filter(user=student.user, title="Fee Reminder", channel="in_app").count() == 1


# ─── Analytics: at-risk, funnel, forecast ─────────────────────────────────────


class TestAnalytics:
    def test_at_risk_students_flags_low_attendance(self, api, school, admin, db):
        student = StudentFactory(school=school)
        academic_year = AcademicYearFactory(school=school)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=academic_year)
        EnrollmentFactory(student=student, classroom=classroom, academic_year=academic_year)

        # 2 records in the window: 1 present, 1 absent -> 50% < 80% threshold
        today = date.today()
        AttendanceRecordFactory(
            student=student, classroom=classroom, academic_year=academic_year, date=today, status="P"
        )
        AttendanceRecordFactory(
            student=student,
            classroom=classroom,
            academic_year=academic_year,
            date=today - timedelta(days=1),
            status="A",
        )

        auth(api, admin)
        resp = api.get(REPORTING_AT_RISK_STUDENTS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["students"][0]["admission_number"] == student.admission_number
        assert data["students"][0]["attendance_pct"] == 50.0
        assert "low_attendance" in data["students"][0]["reasons"]

    def test_at_risk_students_excludes_healthy_students(self, api, school, admin, db):
        student = StudentFactory(school=school)
        academic_year = AcademicYearFactory(school=school)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=academic_year)
        EnrollmentFactory(student=student, classroom=classroom, academic_year=academic_year)
        AttendanceRecordFactory(
            student=student, classroom=classroom, academic_year=academic_year, date=date.today(), status="P"
        )

        auth(api, admin)
        resp = api.get(REPORTING_AT_RISK_STUDENTS)
        assert resp.json()["count"] == 0

    def test_enrollment_funnel_counts_by_stage(self, api, school, admin, db):
        intake = EnrollmentIntakeFactory(school=school)
        ApplicationFactory(school=school, intake=intake, status="submitted")
        ApplicationFactory(school=school, intake=intake, status="submitted")
        ApplicationFactory(school=school, intake=intake, status="accepted")
        ApplicationFactory(school=school, intake=intake, status="enrolled")

        auth(api, admin)
        resp = api.get(REPORTING_ENROLLMENT_FUNNEL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_applications"] == 4
        by_stage = {s["stage"]: s["count"] for s in data["funnel"]}
        assert by_stage["submitted"] == 2
        assert by_stage["accepted"] == 1
        assert by_stage["enrolled"] == 1
        assert data["conversion"]["accepted_to_enrolled"] == 100.0

    def test_fee_forecast_returns_windows_and_history(self, api, school, admin, db):
        student = StudentFactory(school=school)
        academic_year = AcademicYearFactory(school=school)
        fee_category = FeeCategoryFactory(school=school)
        structure = FeeStructureFactory(
            school=school, academic_year=academic_year, grade=GradeFactory(school=school), fee_category=fee_category
        )
        FeeInvoiceFactory(
            student=student,
            academic_year=academic_year,
            fee_structure=structure,
            due_date=date.today() + timedelta(days=10),
            total_amount=Decimal("500.00"),
        )

        auth(api, admin)
        resp = api.get(REPORTING_FEE_FORECAST)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["forecast_90d"]) == 3
        assert data["forecast_90d"][0]["expected"] == 500.00
        assert len(data["history_3m"]) == 3


# ─── Attendance CSV import ────────────────────────────────────────────────────


class TestAttendanceImport:
    def test_import_creates_records(self, api, school, teacher, db):
        academic_year = AcademicYearFactory(school=school)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=academic_year)
        student = StudentFactory(school=school)
        EnrollmentFactory(student=student, classroom=classroom, academic_year=academic_year)

        auth(api, teacher)
        csv_data = (
            "admission_number,date,status,remarks\n"
            f"{student.admission_number},{date.today().isoformat()},P,on time\n"
            f"{student.admission_number},{(date.today() - timedelta(days=1)).isoformat()},A,sick\n"
        )
        resp = api.post(ATTENDANCE_IMPORT_CSV, {"csv_data": csv_data}, format="json")
        assert resp.status_code == 200, resp.content
        assert resp.json()["imported"] == 2
        assert resp.json()["errors"] == []

    def test_import_rejects_unknown_student_and_bad_status(self, api, school, teacher, db):
        academic_year = AcademicYearFactory(school=school)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=academic_year)
        student = StudentFactory(school=school)
        EnrollmentFactory(student=student, classroom=classroom, academic_year=academic_year)

        auth(api, teacher)
        csv_data = (
            "admission_number,date,status\n"
            "ADM-UNKNOWN,2026-08-10,P\n"
            f"{student.admission_number},{date.today().isoformat()},X\n"
        )
        resp = api.post(ATTENDANCE_IMPORT_CSV, {"csv_data": csv_data}, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["imported"] == 0
        assert len(data["errors"]) == 2

    def test_import_bad_date_and_no_enrollment_are_row_errors(self, api, school, teacher, db):
        """
        Unparseable dates and students without an active enrollment must be
        per-row errors, never a 500 for the whole import.
        """
        AcademicYearFactory(school=school)
        student = StudentFactory(school=school)  # no active enrollment

        auth(api, teacher)
        csv_data = "admission_number,date,status\n" f"{student.admission_number},not-a-date,P\n"
        resp = api.post(ATTENDANCE_IMPORT_CSV, {"csv_data": csv_data}, format="json")
        assert resp.status_code == 200, resp.content
        data = resp.json()
        assert data["imported"] == 0
        assert len(data["errors"]) >= 1


# ─── Fee invoice CSV import ───────────────────────────────────────────────────


class TestFeeInvoiceImport:
    def test_import_creates_invoices(self, api, school, admin, db):
        academic_year = AcademicYearFactory(school=school)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=academic_year)
        student = StudentFactory(school=school)
        EnrollmentFactory(student=student, classroom=classroom, academic_year=academic_year)
        fee_category = FeeCategoryFactory(school=school, name="Tuition")
        FeeStructureFactory(
            school=school,
            academic_year=academic_year,
            grade=classroom.grade,
            fee_category=fee_category,
            amount=Decimal("500.00"),
        )

        auth(api, admin)
        csv_data = (
            "admission_number,fee_category_name,due_date,amount,discount_amount,notes\n"
            f"{student.admission_number},Tuition,2026-09-10,500.00,0,Term fee\n"
        )
        resp = api.post(FEES_INVOICES_IMPORT_CSV, {"csv_data": csv_data}, format="json")
        assert resp.status_code == 200, resp.content
        data = resp.json()
        assert data["imported"] == 1
        assert len(data["invoice_numbers"]) == 1
        assert data["errors"] == []

    def test_import_requires_existing_fee_structure(self, api, school, admin, db):
        academic_year = AcademicYearFactory(school=school)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=academic_year)
        student = StudentFactory(school=school)
        EnrollmentFactory(student=student, classroom=classroom, academic_year=academic_year)

        auth(api, admin)
        csv_data = (
            "admission_number,fee_category_name,due_date,amount\n"
            f"{student.admission_number},Missing Category,2026-09-10,500.00\n"
        )
        resp = api.post(FEES_INVOICES_IMPORT_CSV, {"csv_data": csv_data}, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["imported"] == 0
        assert any("no fee structure" in e for e in data["errors"])


# ─── Admissions CRM pipeline (inquiry → tour → offer → enrolled) ─────────────


class TestAdmissionsPipeline:
    def test_schedule_tour_records_date_and_timeline(self, api, school, admin, db):
        app = ApplicationFactory(school=school, intake=EnrollmentIntakeFactory(school=school))
        auth(api, admin)
        resp = api.post(admissions_application_schedule_tour(app.id), {"tour_date": "2026-09-15"}, format="json")
        assert resp.status_code == 200, resp.content
        data = resp.json()
        assert data["tour_date"] == "2026-09-15"
        assert any(t["stage"] == "tour_scheduled" and t["created_by_name"] == admin.full_name for t in data["timeline"])

    def test_complete_tour_requires_scheduled_tour(self, api, school, admin, db):
        app = ApplicationFactory(school=school, intake=EnrollmentIntakeFactory(school=school))
        auth(api, admin)

        resp = api.post(admissions_application_complete_tour(app.id), {}, format="json")
        assert resp.status_code == 400

        api.post(admissions_application_schedule_tour(app.id), {"tour_date": "2026-09-15"}, format="json")
        resp = api.post(admissions_application_complete_tour(app.id), {}, format="json")
        assert resp.status_code == 200, resp.content
        assert resp.json()["toured_at"] is not None
        assert any(t["stage"] == "tour_completed" for t in resp.json()["timeline"])

    def test_send_offer_marks_accepted_and_sets_timeline(self, api, school, admin, db):
        app = ApplicationFactory(school=school, intake=EnrollmentIntakeFactory(school=school), status="shortlisted")
        auth(api, admin)
        resp = api.post(admissions_application_send_offer(app.id), {}, format="json")
        assert resp.status_code == 200, resp.content
        data = resp.json()
        assert data["status"] == "accepted"
        assert data["offer_sent_at"] is not None
        assert any(t["stage"] == "offer_sent" for t in data["timeline"])

    def test_send_offer_rejects_early_stages(self, api, school, admin, db):
        app = ApplicationFactory(school=school, intake=EnrollmentIntakeFactory(school=school), status="submitted")
        auth(api, admin)
        resp = api.post(admissions_application_send_offer(app.id), {}, format="json")
        assert resp.status_code == 400

    def test_accept_offer_requires_sent_offer(self, api, school, admin, db):
        app = ApplicationFactory(school=school, intake=EnrollmentIntakeFactory(school=school), status="accepted")
        auth(api, admin)
        resp = api.post(admissions_application_accept_offer(app.id), {}, format="json")
        assert resp.status_code == 400

        app.offer_sent_at = timezone.now()
        app.save(update_fields=["offer_sent_at"])
        resp = api.post(admissions_application_accept_offer(app.id), {}, format="json")
        assert resp.status_code == 200, resp.content
        assert resp.json()["offer_accepted_at"] is not None

    def test_enroll_creates_student_links_application(self, api, school, admin, db):
        from services.auth.models import User

        academic_year = AcademicYearFactory(school=school)
        classroom = ClassroomFactory(school=school, grade=GradeFactory(school=school), academic_year=academic_year)
        app = ApplicationFactory(
            school=school,
            intake=EnrollmentIntakeFactory(school=school),
            status="accepted",
            offer_sent_at=timezone.now(),
            email="candidate@example.com",
        )
        auth(api, admin)
        resp = api.post(admissions_application_enroll(app.id), {"classroom_id": str(classroom.id)}, format="json")
        assert resp.status_code == 200, resp.content
        data = resp.json()
        assert data["status"] == "enrolled"
        assert data["linked_student"] is not None
        assert data["generated_password"]  # secure password surfaced to the admin

        app.refresh_from_db()
        student = app.linked_student
        assert student.school == school
        assert student.enrollments.filter(classroom=classroom, academic_year=academic_year).exists()
        assert User.objects.filter(email=app.email, school=school).exists()
        assert any(t["stage"] == "enrolled" for t in data["timeline"])

    def test_enroll_rejects_wrong_status_or_classroom(self, api, school, admin, db):
        other_school = SchoolFactory()
        other_classroom = ClassroomFactory(school=other_school, grade=GradeFactory(school=other_school))
        app = ApplicationFactory(
            school=school,
            intake=EnrollmentIntakeFactory(school=school),
            status="accepted",
            offer_sent_at=timezone.now(),
        )
        auth(api, admin)

        # Classroom from another school -> 400
        resp = api.post(admissions_application_enroll(app.id), {"classroom_id": str(other_classroom.id)}, format="json")
        assert resp.status_code == 400

        # Not-accepted application -> 400
        app2 = ApplicationFactory(school=school, intake=EnrollmentIntakeFactory(school=school), status="submitted")
        resp = api.post(
            admissions_application_enroll(app2.id), {"classroom_id": str(other_classroom.id)}, format="json"
        )
        assert resp.status_code == 400

    def test_update_status_logs_timeline_and_is_admin_only(self, api, school, admin, teacher, db):
        app = ApplicationFactory(school=school, intake=EnrollmentIntakeFactory(school=school))
        auth(api, teacher)
        resp = api.post(admissions_application_update_status(app.id), {"status": "under_review"}, format="json")
        assert resp.status_code == 403

        auth(api, admin)
        resp = api.post(admissions_application_update_status(app.id), {"status": "under_review"}, format="json")
        assert resp.status_code == 200, resp.content
        assert any(
            t["stage"] == "status_changed" and "submitted → under_review" in t["note"] for t in resp.json()["timeline"]
        )

    def test_pipeline_actions_are_tenant_scoped(self, api, school, admin, db):
        other_school = SchoolFactory()
        other_app = ApplicationFactory(
            school=other_school,
            intake=EnrollmentIntakeFactory(school=other_school),
            status="shortlisted",
        )
        auth(api, admin)

        # Schedule a tour on another school's application -> 404 (scoped queryset)
        resp = api.post(admissions_application_schedule_tour(other_app.id), {"tour_date": "2026-09-15"}, format="json")
        assert resp.status_code == 404

        # Send an offer on another school's application -> 404
        resp = api.post(admissions_application_send_offer(other_app.id), {}, format="json")
        assert resp.status_code == 404
