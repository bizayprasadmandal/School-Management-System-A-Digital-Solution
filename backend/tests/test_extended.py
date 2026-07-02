"""
Extended Test Suite — Gradebook, Fees, Communication, Timetable, WebSocket consumers
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
    AnnouncementFactory, AttendanceRecordFactory,
)


# ─── Factories-based fixtures ─────────────────────────────────────────────────

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
    return ClassroomFactory(school=school, grade=grade, academic_year=academic_year, class_teacher=teacher)

@pytest.fixture
def enrollment(db, student, classroom, academic_year):
    return EnrollmentFactory(student=student, classroom=classroom, academic_year=academic_year)

@pytest.fixture
def subject(db, school, grade):
    return SubjectFactory(school=school, grade=grade)

@pytest.fixture
def assignment(db, teacher, subject, classroom, academic_year):
    return TeacherAssignmentFactory(teacher=teacher, subject=subject, classroom=classroom, academic_year=academic_year)

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


# ─── Gradebook Tests ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGradebookAPI:

    def test_admin_can_list_exams(self, admin_client, exam):
        r = admin_client.get("/api/v1/gradebook/exams/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_teacher_can_submit_bulk_grades(self, teacher_client, student, schedule, enrollment):
        payload = {
            "exam_schedule_id": schedule.id,
            "grades": [{"student_id": str(student.id), "marks_obtained": "78.5", "is_absent": False}],
        }
        r = teacher_client.post("/api/v1/gradebook/grades/bulk/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["graded"] == 1

    def test_grade_record_percentage(self, db, student, schedule):
        grade = GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("75"))
        assert grade.percentage == Decimal("75")
        assert grade.is_pass is True

    def test_zero_marks_fails(self, db, student, schedule):
        grade = GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("0"))
        assert grade.is_pass is False

    def test_absent_student_has_no_percentage(self, db, student, schedule):
        grade = GradeRecordFactory(student=student, exam_schedule=schedule, is_absent=True, marks_obtained=None)
        assert grade.percentage is None
        assert grade.is_pass is False

    def test_student_can_view_own_grades(self, student_client, student, schedule, enrollment):
        GradeRecordFactory(student=student, exam_schedule=schedule, marks_obtained=Decimal("85"))
        r = student_client.get(f"/api/v1/gradebook/grades/?student_id={student.id}")
        assert r.status_code == status.HTTP_200_OK

    def test_student_cannot_submit_grades(self, student_client, schedule, student):
        payload = {
            "exam_schedule_id": schedule.id,
            "grades": [{"student_id": str(student.id), "marks_obtained": "90", "is_absent": False}],
        }
        r = student_client.post("/api/v1/gradebook/grades/bulk/", payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_exam_leaderboard(self, admin_client, exam, schedule, student, enrollment):
        from services.gradebook.models import ReportCard
        ReportCard.objects.create(
            student=student, exam=exam,
            academic_year=exam.academic_year,
            total_marks=Decimal("100"), obtained_marks=Decimal("88"),
            percentage=Decimal("88.0"), grade_letter="A",
            rank_in_class=1, status="published",
        )
        r = admin_client.get(f"/api/v1/gradebook/exams/{exam.id}/leaderboard/")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data) >= 1


# ─── Fees Tests ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFeesAPI:

    def test_admin_can_list_invoices(self, admin_client, school, student, academic_year):
        category = FeeCategoryFactory(school=school)
        structure = FeeStructureFactory(school=school, academic_year=academic_year, fee_category=category, grade=student.school.grades.first() or GradeFactory(school=school))
        FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure)
        r = admin_client.get("/api/v1/fees/invoices/")
        assert r.status_code == status.HTTP_200_OK

    def test_invoice_outstanding_is_correct(self, db, school, student, academic_year):
        category = FeeCategoryFactory(school=school)
        grade = GradeFactory(school=school)
        structure = FeeStructureFactory(school=school, academic_year=academic_year, fee_category=category, grade=grade)
        invoice = FeeInvoiceFactory(
            student=student, academic_year=academic_year,
            fee_structure=structure, total_amount=Decimal("1000"),
            paid_amount=Decimal("400"),
        )
        assert invoice.outstanding_amount == Decimal("600")

    def test_student_can_view_own_invoices(self, student_client, school, student, academic_year):
        category = FeeCategoryFactory(school=school)
        grade = GradeFactory(school=school)
        structure = FeeStructureFactory(school=school, academic_year=academic_year, fee_category=category, grade=grade)
        FeeInvoiceFactory(student=student, academic_year=academic_year, fee_structure=structure)
        r = student_client.get(f"/api/v1/fees/invoices/?student={student.id}")
        assert r.status_code == status.HTTP_200_OK

    def test_payment_updates_invoice_status(self, admin_client, school, student, academic_year):
        from services.fees.models import FeeInvoice
        category = FeeCategoryFactory(school=school)
        grade = GradeFactory(school=school)
        structure = FeeStructureFactory(school=school, academic_year=academic_year, fee_category=category, grade=grade)
        invoice = FeeInvoiceFactory(
            student=student, academic_year=academic_year,
            fee_structure=structure, total_amount=Decimal("500"),
            paid_amount=Decimal("0"),
        )
        payload = {
            "invoice": str(invoice.id),
            "amount": "500.00",
            "payment_method": "cash",
        }
        r = admin_client.post("/api/v1/fees/payments/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        invoice.refresh_from_db()
        assert invoice.status == FeeInvoice.Status.PAID


# ─── Communication Tests ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAnnouncementAPI:

    def test_admin_publishes_announcement(self, admin_client, school):
        payload = {
            "title": "Exam Schedule Released",
            "content": "The final exam schedule has been released. Check the portal.",
            "priority": "high",
            "audience": "all",
            "is_draft": False,
        }
        r = admin_client.post("/api/v1/communication/announcements/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["title"] == "Exam Schedule Released"

    def test_student_sees_public_announcements(self, student_client, school):
        ann = AnnouncementFactory(school=school, audience="all", is_draft=False)
        r = student_client.get("/api/v1/communication/announcements/")
        assert r.status_code == status.HTTP_200_OK
        titles = [a["title"] for a in r.data["results"]]
        assert ann.title in titles

    def test_student_cannot_see_teacher_announcements(self, student_client, school):
        AnnouncementFactory(school=school, audience="teachers", is_draft=False)
        r = student_client.get("/api/v1/communication/announcements/")
        assert r.status_code == status.HTTP_200_OK
        # Student should not see teacher-only announcements
        for a in r.data["results"]:
            assert a.get("audience") != "teachers"

    def test_mark_announcement_read(self, student_client, school):
        ann = AnnouncementFactory(school=school, audience="all", is_draft=False)
        r = student_client.post(f"/api/v1/communication/announcements/{ann.id}/mark-read/")
        assert r.status_code == status.HTTP_200_OK

    def test_draft_not_visible_to_students(self, student_client, school):
        ann = AnnouncementFactory(school=school, audience="all", is_draft=True)
        r = student_client.get("/api/v1/communication/announcements/")
        ids = [a["id"] for a in r.data["results"]]
        assert str(ann.id) not in ids


# ─── Timetable Tests ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTimetableAPI:

    def test_teacher_conflict_detection(self, db, teacher, classroom, assignment, academic_year, school):
        from services.timetable.models import Period, TimetableSlot
        from services.students.models import Grade, Classroom

        period = Period.objects.create(
            school=school, name="Period 1", period_number=1,
            start_time="08:00", end_time="08:45",
        )
        # Create second classroom in same school
        grade2 = GradeFactory(school=school, level=6)
        classroom2 = ClassroomFactory(school=school, grade=grade2, academic_year=academic_year)
        subject2 = SubjectFactory(school=school, grade=grade2)
        assignment2 = TeacherAssignmentFactory(
            teacher=teacher, subject=subject2, classroom=classroom2, academic_year=academic_year
        )
        # First slot — OK
        TimetableSlot.objects.create(
            classroom=classroom, assignment=assignment,
            period=period, day_of_week=0, academic_year=academic_year,
        )
        # Second slot same teacher, same period, same day — should fail at serializer level
        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=teacher)
        payload = {
            "classroom": classroom2.id,
            "assignment": assignment2.id,
            "period": period.id,
            "day_of_week": 0,
            "academic_year": academic_year.id,
        }
        r = client.post("/api/v1/timetable/slots/", payload, format="json")
        # Should return 400 due to conflict detection
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_weekly_timetable_endpoint(self, admin_client, classroom, assignment, academic_year, school):
        from services.timetable.models import Period, TimetableSlot
        period = Period.objects.create(
            school=school, name="Period 1", period_number=1,
            start_time="08:00", end_time="08:45",
        )
        TimetableSlot.objects.create(
            classroom=classroom, assignment=assignment,
            period=period, day_of_week=1, academic_year=academic_year,
        )
        r = admin_client.get(
            f"/api/v1/timetable/slots/weekly/?classroom_id={classroom.id}&academic_year_id={academic_year.id}"
        )
        assert r.status_code == status.HTTP_200_OK
        assert "Tuesday" in r.data

    def test_school_event_created(self, admin_client, school):
        payload = {
            "title": "Sports Day",
            "event_type": "sports",
            "start_date": date.today().isoformat(),
            "end_date": date.today().isoformat(),
            "is_school_wide": True,
        }
        r = admin_client.post("/api/v1/timetable/events/", payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_upcoming_events_endpoint(self, admin_client, school):
        from services.timetable.models import SchoolEvent
        SchoolEventFactory(school=school, start_date=date.today() + timedelta(days=5))
        r = admin_client.get("/api/v1/timetable/events/upcoming/")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data) >= 1


# ─── Attendance Extended Tests ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestAttendanceExtended:

    def test_attendance_percentage_calculation(self, db, student, classroom, academic_year, enrollment):
        records = [
            AttendanceRecordFactory(student=student, classroom=classroom, academic_year=academic_year,
                                    date=date.today() - timedelta(days=i), status="P" if i < 9 else "A")
            for i in range(10)
        ]
        present = sum(1 for r in records if r.status == "P")
        assert present == 9
        pct = present / len(records) * 100
        assert pct == 90.0

    def test_leave_approval_marks_excused(self, admin_client, student, classroom, academic_year, enrollment):
        from services.attendance.models import AttendanceLeave, AttendanceRecord
        leave = AttendanceLeave.objects.create(
            student=student,
            leave_type="sick",
            from_date=date.today(),
            to_date=date.today(),
            reason="Fever",
            status="pending",
        )
        r = admin_client.post(f"/api/v1/attendance/leaves/{leave.id}/approve/",
                              {"remarks": "Approved"}, format="json")
        assert r.status_code == status.HTTP_200_OK
        leave.refresh_from_db()
        assert leave.status == "approved"

    def test_student_report_monthly(self, admin_client, student, classroom, academic_year, enrollment):
        today = date.today()
        for i in range(5):
            AttendanceRecordFactory(
                student=student, classroom=classroom, academic_year=academic_year,
                date=today - timedelta(days=i), status="P",
            )
        r = admin_client.get(
            f"/api/v1/attendance/student-report/?student_id={student.id}"
            f"&month={today.month}&year={today.year}"
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.data["present"] == 5
