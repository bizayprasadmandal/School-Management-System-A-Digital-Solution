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
    AnnouncementFactory, AttendanceRecordFactory, PeriodFactory,
    TimetableSlotFactory, SchoolEventFactory,
)
from tests.url_helpers import (
    GRADEBOOK_EXAMS, GRADEBOOK_GRADES_BULK, GRADEBOOK_GRADES,
    gradebook_exam_leaderboard,
    FEES_INVOICES, FEES_PAYMENTS, FEES_SCHOLARSHIPS, fees_invoice_waive,
    COMMUNICATION_ANNOUNCEMENTS, communication_announcement_mark_read,
    COMMUNICATION_NOTIFICATIONS_MARK_ALL_READ,
    COMMUNICATION_NOTIFICATIONS_UNREAD_COUNT, COMMUNICATION_MESSAGES,
    communication_announcement_detail, communication_announcement_publish,
    TIMETABLE_SLOTS, TIMETABLE_PERIODS, TIMETABLE_EVENTS,
    TIMETABLE_WEEKLY, TIMETABLE_TEACHER_SCHEDULE, TIMETABLE_EVENTS_UPCOMING,
    ATTENDANCE_BULK_RECORD, ATTENDANCE_STUDENT_REPORT,
    ATTENDANCE_CLASSROOM_SUMMARY, attendance_leave_approve,
    STUDENTS_LIST, student_detail, AUTH_ME, AUTH_PROFILE,
    AUTH_CHANGE_PASSWORD, AUTH_PASSWORD_RESET, AUTH_LOGIN,
    ACADEMICS_SUBJECTS, ACADEMICS_ASSIGNMENTS, ACADEMICS_MY_ASSIGNMENTS,
    ACADEMICS_LESSON_PLANS, ACADEMICS_TEACHER_PROFILES,
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
def assignment(db, teacher, subject, classroom, academic_year):
    return TeacherAssignmentFactory(
        teacher=teacher, subject=subject, classroom=classroom,
        academic_year=academic_year,
    )


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
        r = admin_client.get(GRADEBOOK_EXAMS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_teacher_can_submit_bulk_grades(
        self, teacher_client, student, schedule, enrollment
    ):
        payload = {
            "exam_schedule_id": schedule.id,
            "grades": [{
                "student_id": str(student.id), "marks_obtained": "78.5",
                "is_absent": False,
            }],
        }
        r = teacher_client.post(GRADEBOOK_GRADES_BULK, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["graded"] == 1

    def test_grade_record_percentage(self, db, student, schedule):
        grade = GradeRecordFactory(
            student=student, exam_schedule=schedule, marks_obtained=Decimal("75"),
        )
        assert grade.percentage == Decimal("75")
        assert grade.is_pass is True

    def test_zero_marks_fails(self, db, student, schedule):
        grade = GradeRecordFactory(
            student=student, exam_schedule=schedule, marks_obtained=Decimal("0"),
        )
        assert grade.is_pass is False

    def test_absent_student_has_no_percentage(self, db, student, schedule):
        grade = GradeRecordFactory(
            student=student, exam_schedule=schedule,
            is_absent=True, marks_obtained=None,
        )
        assert grade.percentage is None
        assert grade.is_pass is False

    def test_student_can_view_own_grades(
        self, student_client, student, schedule, enrollment
    ):
        GradeRecordFactory(
            student=student, exam_schedule=schedule, marks_obtained=Decimal("85"),
        )
        r = student_client.get(f"{GRADEBOOK_GRADES}?student_id={student.id}")
        assert r.status_code == status.HTTP_200_OK

    def test_student_cannot_submit_grades(self, student_client, schedule, student):
        payload = {
            "exam_schedule_id": schedule.id,
            "grades": [{
                "student_id": str(student.id), "marks_obtained": "90",
                "is_absent": False,
            }],
        }
        r = student_client.post(GRADEBOOK_GRADES_BULK, payload, format="json")
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
        r = admin_client.get(gradebook_exam_leaderboard(exam.id))
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data) >= 1
