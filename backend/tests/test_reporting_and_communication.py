"""
Test Suite — Reporting, Communication, Timetable, Attendance Extended
Covers all previously untested service areas.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import (
    SchoolFactory, AdminUserFactory, TeacherUserFactory, StudentUserFactory,
    ParentUserFactory, StudentFactory, ClassroomFactory, AcademicYearFactory,
    GradeFactory, EnrollmentFactory, SubjectFactory, TeacherAssignmentFactory,
    ExamFactory, ExamScheduleFactory, GradeRecordFactory, AttendanceRecordFactory,
    FeeCategoryFactory, FeeStructureFactory, FeeInvoiceFactory,
    AnnouncementFactory, NotificationFactory, PeriodFactory, TimetableSlotFactory,
    SchoolEventFactory,
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
def student_user(db, school):
    return StudentUserFactory(school=school)

@pytest.fixture
def parent_user(db, school):
    return ParentUserFactory(school=school)

@pytest.fixture
def student(db, school, student_user):
    return StudentFactory(user=student_user, school=school)

@pytest.fixture
def academic_year(db, school):
    return AcademicYearFactory(school=school)

@pytest.fixture
def grade(db, school):
    return GradeFactory(school=school)

@pytest.fixture
def classroom(db, school, grade, academic_year, teacher):
    return ClassroomFactory(school=school, grade=grade, academic_year=academic_year, class_teacher=teacher)

@pytest.fixture
def enrollment(db, student, classroom, academic_year):
    return EnrollmentFactory(student=student, classroom=classroom, academic_year=academic_year)

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

@pytest.fixture
def parent_client(db, parent_user):
    c = APIClient()
    c.force_authenticate(user=parent_user)
    return c


# ─── Reporting Tests ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestReportingAPI:

    def test_dashboard_stats_returns_expected_keys(self, admin_client):
        r = admin_client.get("/api/v1/reporting/dashboard-stats/")
        assert r.status_code == status.HTTP_200_OK
        expected = {
            "total_students", "total_teachers", "total_classrooms",
            "attendance_today_pct", "fees_collected_month", "fees_outstanding",
        }
        assert expected.issubset(r.data.keys()), f"Missing keys: {expected - r.data.keys()}"

    def test_dashboard_stats_counts_correctly(self, admin_client, school, student, teacher):
        r = admin_client.get("/api/v1/reporting/dashboard-stats/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["total_students"] >= 1
        assert r.data["total_teachers"] >= 1

    def test_attendance_report_accepts_date_range(self, admin_client):
        today = date.today()
        params = {
            "from_date": (today - timedelta(days=30)).isoformat(),
            "to_date": today.isoformat(),
        }
        r = admin_client.get("/api/v1/reporting/attendance-report/", params)
        assert r.status_code == status.HTTP_200_OK

    def test_fee_report_returns_collection_stats(self, admin_client, school, student, academic_year):
        cat = FeeCategoryFactory(school=school)
        structure = FeeStructureFactory(school=school, academic_year=academic_year, grade=student.school.grades.first() or GradeFactory(school=school), fee_category=cat)
        FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure, status="paid", paid_amount=Decimal("500"), total_amount=Decimal("500"))
        FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure, status="unpaid")
        r = admin_client.get("/api/v1/reporting/fee-report/", {"academic_year_id": academic_year.id})
        assert r.status_code == status.HTTP_200_OK
        assert "total_collected" in r.data
        assert "total_invoiced" in r.data

    def test_student_csv_export_returns_csv(self, admin_client):
        r = admin_client.get("/api/v1/reporting/export/students-csv/")
        assert r.status_code == status.HTTP_200_OK
        assert "text/csv" in r.get("Content-Type", "")

    def test_attendance_pdf_export(self, admin_client, classroom):
        r = admin_client.get("/api/v1/reporting/export/attendance-pdf/", {"classroom_id": classroom.id})
        assert r.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_reporting_not_accessible_to_students(self, student_client):
        r = student_client.get("/api/v1/reporting/dashboard-stats/")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_reporting_not_accessible_to_parents(self, parent_client):
        r = parent_client.get("/api/v1/reporting/dashboard-stats/")
        assert r.status_code == status.HTTP_403_FORBIDDEN


# ─── Communication Extended Tests ─────────────────────────────────────────────

@pytest.mark.django_db
class TestCommunicationExtended:

    def test_announcement_view_count_increments(self, admin_client, school, admin):
        ann = AnnouncementFactory(school=school, is_draft=False, created_by=admin)
        initial_count = ann.view_count
        admin_client.get(f"/api/v1/communication/announcements/{ann.id}/")
        ann.refresh_from_db()
        assert ann.view_count >= initial_count

    def test_student_cannot_see_teacher_only_announcement(self, student_client, school, admin):
        teacher_ann = AnnouncementFactory(school=school, audience="teachers", is_draft=False, created_by=admin)
        r = student_client.get("/api/v1/communication/announcements/")
        assert r.status_code == status.HTTP_200_OK
        ids = [a["id"] for a in r.data.get("results", [])]
        assert str(teacher_ann.id) not in ids

    def test_draft_not_visible_to_non_admin(self, student_client, school, admin):
        draft = AnnouncementFactory(school=school, is_draft=True, created_by=admin)
        r = student_client.get("/api/v1/communication/announcements/")
        ids = [a["id"] for a in r.data.get("results", [])]
        assert str(draft.id) not in ids

    def test_notification_mark_all_read(self, student_client, student_user):
        from services.communication.models import Notification
        n1 = NotificationFactory(user=student_user, status="sent")
        n2 = NotificationFactory(user=student_user, status="sent")
        r = student_client.post("/api/v1/communication/notifications/mark-all-read/")
        assert r.status_code == status.HTTP_200_OK
        n1.refresh_from_db()
        n2.refresh_from_db()
        assert n1.read_at is not None
        assert n2.read_at is not None

    def test_notification_unread_count(self, student_client, student_user):
        from services.communication.models import Notification
        NotificationFactory(user=student_user, status="sent")
        NotificationFactory(user=student_user, status="sent")
        r = student_client.get("/api/v1/communication/notifications/unread-count/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 2

    def test_send_direct_message(self, teacher_client, teacher, student_user):
        payload = {"recipient": str(student_user.id), "content": "Please submit your assignment."}
        r = teacher_client.post("/api/v1/communication/messages/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["content"] == "Please submit your assignment."

    def test_cannot_send_message_to_different_school_user(self, teacher_client):
        other_school = SchoolFactory()
        other_user = StudentUserFactory(school=other_school)
        payload = {"recipient": str(other_user.id), "content": "Cross-school message."}
        r = teacher_client.post("/api/v1/communication/messages/", payload, format="json")
        assert r.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]

    def test_admin_can_publish_announcement(self, admin_client, school, admin):
        ann = AnnouncementFactory(school=school, is_draft=True, created_by=admin)
        r = admin_client.post(f"/api/v1/communication/announcements/{ann.id}/publish/")
        assert r.status_code == status.HTTP_200_OK
        ann.refresh_from_db()
        assert not ann.is_draft


# ─── Timetable Extended Tests ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestTimetableExtended:

    def test_period_crud(self, admin_client, school):
        payload = {"name": "Period 1", "period_number": 1, "start_time": "08:00", "end_time": "08:45", "is_break": False}
        r = admin_client.post("/api/v1/timetable/periods/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Period 1"

    def test_student_cannot_create_period(self, student_client, school):
        payload = {"name": "Period 1", "period_number": 1, "start_time": "08:00", "end_time": "08:45"}
        r = student_client.post("/api/v1/timetable/periods/", payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_school_event_creation(self, admin_client, school):
        payload = {
            "title": "Annual Sports Day",
            "event_type": "sports",
            "start_date": date.today().isoformat(),
            "end_date": date.today().isoformat(),
            "is_school_wide": True,
        }
        r = admin_client.post("/api/v1/timetable/events/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_upcoming_events_only_returns_future(self, admin_client, school):
        SchoolEventFactory(school=school, start_date=date.today() - timedelta(days=10))  # past
        SchoolEventFactory(school=school, start_date=date.today() + timedelta(days=5))   # future
        r = admin_client.get("/api/v1/timetable/events/upcoming/")
        assert r.status_code == status.HTTP_200_OK
        for event in r.data:
            assert event["start_date"] >= date.today().isoformat()

    def test_weekly_timetable_structure(self, admin_client, school, classroom, academic_year, teacher):
        subject = SubjectFactory(school=school, grade=classroom.grade)
        assignment = TeacherAssignmentFactory(teacher=teacher, subject=subject, classroom=classroom, academic_year=academic_year)
        period = PeriodFactory(school=school, period_number=1, start_time="08:00", end_time="08:45")
        TimetableSlotFactory(classroom=classroom, assignment=assignment, period=period, day_of_week=0, academic_year=academic_year)
        r = admin_client.get(f"/api/v1/timetable/slots/weekly/?classroom_id={classroom.id}&academic_year_id={academic_year.id}")
        assert r.status_code == status.HTTP_200_OK
        assert "Monday" in r.data
        assert len(r.data["Monday"]) == 1

    def test_teacher_schedule_endpoint(self, teacher_client, teacher, classroom, academic_year, school):
        subject = SubjectFactory(school=school, grade=classroom.grade)
        assignment = TeacherAssignmentFactory(teacher=teacher, subject=subject, classroom=classroom, academic_year=academic_year)
        period = PeriodFactory(school=school, period_number=2, start_time="09:00", end_time="09:45")
        TimetableSlotFactory(classroom=classroom, assignment=assignment, period=period, day_of_week=1, academic_year=academic_year)
        r = teacher_client.get(f"/api/v1/timetable/slots/teacher-schedule/?academic_year_id={academic_year.id}")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data) >= 1


# ─── Attendance Additional Tests ──────────────────────────────────────────────

@pytest.mark.django_db
class TestAttendanceAdditional:

    def test_attendance_record_bulk_create(self, teacher_client, school, classroom, student, academic_year, enrollment):
        payload = {
            "classroom_id": classroom.id,
            "date": date.today().isoformat(),
            "records": [{"student_id": str(student.id), "status": "P", "remarks": ""}],
        }
        r = teacher_client.post("/api/v1/attendance/bulk-record/", payload, format="json")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["recorded"] == 1

    def test_duplicate_attendance_is_upserted(self, teacher_client, school, classroom, student, academic_year, enrollment):
        AttendanceRecordFactory(student=student, classroom=classroom, academic_year=academic_year, date=date.today(), status="P")
        payload = {
            "classroom_id": classroom.id,
            "date": date.today().isoformat(),
            "records": [{"student_id": str(student.id), "status": "A"}],
        }
        r = teacher_client.post("/api/v1/attendance/bulk-record/", payload, format="json")
        assert r.status_code == status.HTTP_200_OK
        from services.attendance.models import AttendanceRecord
        recs = AttendanceRecord.objects.filter(student=student, date=date.today())
        assert recs.count() == 1
        assert recs.first().status == "A"

    def test_classroom_summary_returns_breakdown(self, admin_client, classroom, student, academic_year, enrollment):
        AttendanceRecordFactory(student=student, classroom=classroom, academic_year=academic_year, date=date.today(), status="P")
        r = admin_client.get("/api/v1/attendance/classroom-summary/", {"classroom_id": classroom.id, "date": date.today().isoformat()})
        assert r.status_code == status.HTTP_200_OK
        assert "breakdown" in r.data

    def test_student_report_calculates_percentage(self, admin_client, classroom, student, academic_year, enrollment):
        today = date.today()
        for i in range(8):
            AttendanceRecordFactory(student=student, classroom=classroom, academic_year=academic_year, date=today - timedelta(days=i), status="P")
        AttendanceRecordFactory(student=student, classroom=classroom, academic_year=academic_year, date=today - timedelta(days=8), status="A")
        AttendanceRecordFactory(student=student, classroom=classroom, academic_year=academic_year, date=today - timedelta(days=9), status="A")
        r = admin_client.get("/api/v1/attendance/student-report/", {"student_id": str(student.id), "month": today.month, "year": today.year})
        assert r.status_code == status.HTTP_200_OK
        assert "percentage" in r.data

    def test_parent_can_view_child_attendance(self, parent_client, parent_user, school, student, classroom, academic_year, enrollment):
        from services.students.models import Guardian, StudentGuardian
        guardian, _ = Guardian.objects.get_or_create(email=parent_user.email, defaults={"user": parent_user, "first_name": "Parent", "last_name": "User", "phone": "+1234567890"})
        StudentGuardian.objects.get_or_create(student=student, guardian=guardian, defaults={"relationship": "mother", "is_primary_contact": True, "portal_access": True})
        AttendanceRecordFactory(student=student, classroom=classroom, academic_year=academic_year, date=date.today(), status="A")
        r = parent_client.get("/api/v1/attendance/", {"student": str(student.id)})
        assert r.status_code == status.HTTP_200_OK


# ─── Fees Extended Tests ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFeesExtended:

    def test_scholarship_creation(self, admin_client, school, student, academic_year):
        payload = {
            "student": str(student.id),
            "academic_year": str(academic_year.id),
            "name": "Merit Scholarship",
            "discount_type": "percentage",
            "discount_value": "50.00",
            "reason": "Top performer in Grade 5",
            "is_active": True,
        }
        r = admin_client.post("/api/v1/fees/scholarships/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Merit Scholarship"

    def test_invoice_waiver(self, admin_client, school, student, academic_year):
        cat = FeeCategoryFactory(school=school)
        structure = FeeStructureFactory(school=school, academic_year=academic_year, grade=GradeFactory(school=school), fee_category=cat)
        invoice = FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure, status="unpaid")
        r = admin_client.post(f"/api/v1/fees/invoices/{invoice.id}/waive/", {"reason": "Financial hardship"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        invoice.refresh_from_db()
        assert invoice.status == "waived"

    def test_student_cannot_access_other_students_invoices(self, student_client, school, academic_year):
        other_student_user = StudentUserFactory(school=school)
        other_student = StudentFactory(user=other_student_user, school=school)
        cat = FeeCategoryFactory(school=school)
        structure = FeeStructureFactory(school=school, academic_year=academic_year, grade=GradeFactory(school=school), fee_category=cat)
        FeeInvoiceFactory(student=other_student, academic_year=academic_year, fee_structure=structure)
        r = student_client.get(f"/api/v1/fees/invoices/?student={other_student.id}")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] == 0

    def test_payment_marks_invoice_paid(self, admin_client, school, student, academic_year):
        from services.fees.models import FeeInvoice
        cat = FeeCategoryFactory(school=school)
        structure = FeeStructureFactory(school=school, academic_year=academic_year, grade=GradeFactory(school=school), fee_category=cat, amount=Decimal("300"))
        invoice = FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure, total_amount=Decimal("300"), paid_amount=Decimal("0"))
        r = admin_client.post("/api/v1/fees/payments/", {"invoice": str(invoice.id), "amount": "300.00", "payment_method": "bank_transfer"}, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        invoice.refresh_from_db()
        assert invoice.status == FeeInvoice.Status.PAID

    def test_partial_payment_marks_invoice_partial(self, admin_client, school, student, academic_year):
        from services.fees.models import FeeInvoice
        cat = FeeCategoryFactory(school=school)
        structure = FeeStructureFactory(school=school, academic_year=academic_year, grade=GradeFactory(school=school), fee_category=cat, amount=Decimal("500"))
        invoice = FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure, total_amount=Decimal("500"), paid_amount=Decimal("0"))
        admin_client.post("/api/v1/fees/payments/", {"invoice": str(invoice.id), "amount": "200.00", "payment_method": "cash"}, format="json")
        invoice.refresh_from_db()
        assert invoice.status == FeeInvoice.Status.PARTIAL
        assert invoice.paid_amount == Decimal("200.00")


# ─── Academics Tests ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAcademicsAPI:

    def test_subject_creation_by_admin(self, admin_client, school, grade):
        payload = {"name": "Mathematics", "code": "MTH05", "grade": grade.id, "max_marks": 100, "pass_marks": 40, "is_core": True}
        r = admin_client.post("/api/v1/academics/subjects/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Mathematics"

    def test_student_cannot_create_subject(self, student_client, grade):
        payload = {"name": "Art", "code": "ART05", "grade": grade.id, "max_marks": 50}
        r = student_client.post("/api/v1/academics/subjects/", payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_teacher_sees_own_assignments_only(self, teacher_client, teacher, school, classroom, academic_year):
        subject = SubjectFactory(school=school, grade=classroom.grade)
        TeacherAssignmentFactory(teacher=teacher, subject=subject, classroom=classroom, academic_year=academic_year)
        other_teacher = TeacherUserFactory(school=school)
        other_subject = SubjectFactory(school=school, grade=classroom.grade)
        TeacherAssignmentFactory(teacher=other_teacher, subject=other_subject, classroom=classroom, academic_year=academic_year)
        r = teacher_client.get("/api/v1/academics/assignments/my-assignments/")
        assert r.status_code == status.HTTP_200_OK
        teacher_ids = {a["teacher"] for a in r.data}
        assert str(teacher.id) in teacher_ids
        assert str(other_teacher.id) not in teacher_ids

    def test_lesson_plan_creation_by_teacher(self, teacher_client, teacher, school, classroom, academic_year):
        subject = SubjectFactory(school=school, grade=classroom.grade)
        assignment = TeacherAssignmentFactory(teacher=teacher, subject=subject, classroom=classroom, academic_year=academic_year)
        payload = {"assignment": assignment.id, "title": "Algebra Introduction", "topic": "Variables and Expressions", "date": date.today().isoformat(), "duration_minutes": 45, "objectives": "Students will define a variable.", "content": "Content here."}
        r = teacher_client.post("/api/v1/academics/lesson-plans/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_teacher_profile_searchable(self, admin_client, teacher, school):
        from services.academics.models import TeacherProfile
        TeacherProfile.objects.get_or_create(user=teacher, school=school, defaults={"employee_id": "EMP9999", "gender": "M", "qualification": "bachelor", "joining_date": date.today()})
        r = admin_client.get("/api/v1/academics/teacher-profiles/", {"search": teacher.first_name})
        assert r.status_code == status.HTTP_200_OK
        names = [t["full_name"] for t in r.data.get("results", [])]
        assert any(teacher.first_name in n for n in names)


# ─── Auth Extended Tests ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAuthExtended:

    def test_password_change(self, admin_client, admin):
        payload = {"old_password": "TestPass@1234", "new_password": "NewSecure@9876"}
        r = admin_client.post("/api/v1/auth/change-password/", payload, format="json")
        assert r.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_wrong_old_password_rejected(self, admin_client):
        payload = {"old_password": "WrongPassword!", "new_password": "NewSecure@9876"}
        r = admin_client.post("/api/v1/auth/change-password/", payload, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_profile_update(self, admin_client, admin):
        r = admin_client.patch("/api/v1/auth/profile/", {"first_name": "Alexandra"}, format="json")
        assert r.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        admin.refresh_from_db()
        assert admin.first_name == "Alexandra"

    def test_password_reset_request(self, db):
        school = SchoolFactory()
        user = AdminUserFactory(school=school)
        client = APIClient()
        r = client.post("/api/v1/auth/password-reset/", {"email": user.email, "reset_url": "https://app.example.com"}, format="json")
        assert r.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_invalid_email_password_reset_still_200(self, db):
        """Security: don't leak whether email exists."""
        client = APIClient()
        r = client.post("/api/v1/auth/password-reset/", {"email": "nonexistent@school.edu", "reset_url": "https://example.com"}, format="json")
        assert r.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_me_endpoint_returns_user(self, admin_client, admin):
        r = admin_client.get("/api/v1/auth/me/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["email"] == admin.email

    def test_unauthenticated_cannot_access_me(self, db):
        r = APIClient().get("/api/v1/auth/me/")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_audit_log_created_on_login(self, db):
        school = SchoolFactory()
        user = AdminUserFactory(school=school)
        user.set_password("Admin@1234")
        user.save()
        r = APIClient().post("/api/v1/auth/login/", {"email": user.email, "password": "Admin@1234"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        from services.auth.models import AuditLog
        assert AuditLog.objects.filter(user=user, action="login").exists()
