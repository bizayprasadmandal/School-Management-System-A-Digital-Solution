"""
Regression tests for the audit-hardening pass.

Each test pins a loophole found in the deep audit:

1.  Cross-tenant payment write (admin credits another school's invoice)
2.  Payment amount exceeding the invoice's outstanding balance
3.  Student self-grading via assessment submissions (+ signal crash → 500)
4.  Teacher grading a submission must not 500 (post_save signal regression)
5.  Bulk invoice generation with a foreign academic year
6.  TeamMember referencing a foreign team
7.  Bulk attendance referencing a foreign student
8.  Duplicate "Fee Payment Overdue" notifications (signal + task double-send)
9.  Unvalidated query params on reporting endpoints (400, not 500)
10. Client-supplied reset_url must match the app's own origin
11. X-School-ID header must not redirect a non-super-admin tenant (JWT clients)
12. Malformed X-School-ID header must not 500 the request
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from tests.factories import (
    AcademicYearFactory,
    AdminUserFactory,
    ClassroomFactory,
    FeeInvoiceFactory,
    SchoolFactory,
    StudentFactory,
    StudentUserFactory,
    TeacherAssignmentFactory,
    TeacherUserFactory,
)
from tests.url_helpers import FEES_PAYMENTS


@pytest.fixture
def api():
    return APIClient()


def _auth(client, user):
    client.force_authenticate(user=user)
    return client


# ─── 1+2. Payment write-path hardening ────────────────────────────────────────


class TestPaymentTenantScoping:
    def test_payment_cannot_reference_other_school_invoice(self, api, db):
        admin_a = AdminUserFactory()
        other_admin = AdminUserFactory()  # school B admin
        student_b = StudentFactory(school=other_admin.school)
        invoice_b = FeeInvoiceFactory(student=student_b)

        _auth(api, admin_a)
        resp = api.post(
            FEES_PAYMENTS,
            {"invoice": str(invoice_b.id), "amount": "100.00", "payment_method": "cash"},
            format="json",
        )
        assert resp.status_code == 400, resp.content
        invoice_b.refresh_from_db()
        assert invoice_b.paid_amount == Decimal("0.00")  # untouched

    def test_payment_amount_cannot_exceed_outstanding(self, api, db):
        admin = AdminUserFactory()
        student = StudentFactory(school=admin.school)
        invoice = FeeInvoiceFactory(student=student, total_amount=Decimal("500.00"))

        _auth(api, admin)
        resp = api.post(
            FEES_PAYMENTS,
            {"invoice": str(invoice.id), "amount": "600.00", "payment_method": "cash"},
            format="json",
        )
        assert resp.status_code == 400, resp.content
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("0.00")

    def test_legitimate_payment_still_works(self, api, db):
        admin = AdminUserFactory()
        student = StudentFactory(school=admin.school)
        invoice = FeeInvoiceFactory(student=student, total_amount=Decimal("500.00"))

        _auth(api, admin)
        resp = api.post(
            FEES_PAYMENTS,
            {"invoice": str(invoice.id), "amount": "200.00", "payment_method": "cash"},
            format="json",
        )
        assert resp.status_code == 201, resp.content
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("200.00")
        assert invoice.status == "partial"


# ─── 3+4. Assessment submissions ──────────────────────────────────────────────


class TestAssessmentSubmissionLockdown:
    def _make_assessment(self, school, teacher):
        from services.gradebook.models import Assessment

        academic_year = AcademicYearFactory(school=school)
        assignment = TeacherAssignmentFactory(
            teacher=teacher,
            academic_year=academic_year,
            is_primary=True,
        )
        return Assessment.objects.create(
            assignment=assignment,
            title="Math Homework 1",
            assessment_type="homework",
            due_date=timezone.localdate() + timedelta(days=7),
            max_marks=Decimal("100.00"),
        )

    def test_student_cannot_set_own_marks(self, api, db):
        school = SchoolFactory()
        student_user = StudentUserFactory(school=school)
        student = StudentFactory(user=student_user, school=school)
        teacher = TeacherUserFactory(school=school)
        assessment = self._make_assessment(school, teacher)

        _auth(api, student_user)
        resp = api.post(
            "/api/v1/gradebook/submissions/",
            {
                "assessment": str(assessment.id),
                "student": str(student.id),
                "marks_obtained": "95.00",
            },
            format="json",
        )
        assert resp.status_code == 400, resp.content  # self-grading rejected

    def test_student_can_submit_without_marks(self, api, db):
        school = SchoolFactory()
        student_user = StudentUserFactory(school=school)
        student = StudentFactory(user=student_user, school=school)
        teacher = TeacherUserFactory(school=school)
        assessment = self._make_assessment(school, teacher)

        _auth(api, student_user)
        resp = api.post(
            "/api/v1/gradebook/submissions/",
            {"assessment": str(assessment.id), "student": str(student.id)},
            format="json",
        )
        assert resp.status_code == 201, resp.content
        assert resp.json()["marks_obtained"] is None

    def test_teacher_grading_does_not_500(self, api, db):
        """Regression: post_save signal crashed on assessment.subject_name."""
        from services.gradebook.models import AssessmentSubmission

        school = SchoolFactory()
        student_user = StudentUserFactory(school=school)
        student = StudentFactory(user=student_user, school=school)
        teacher = TeacherUserFactory(school=school)
        assessment = self._make_assessment(school, teacher)

        sub = AssessmentSubmission.objects.create(assessment=assessment, student=student)

        _auth(api, teacher)
        resp = api.patch(
            f"/api/v1/gradebook/submissions/{sub.id}/",
            {"marks_obtained": "90.00"},
            format="json",
        )
        assert resp.status_code == 200, resp.content
        sub.refresh_from_db()
        assert sub.marks_obtained == Decimal("90.00")

    def test_student_cannot_grade_other_assessment(self, api, db):
        """The assessment must belong to the student's school."""
        school = SchoolFactory()
        other_school = SchoolFactory()
        student_user = StudentUserFactory(school=school)
        student = StudentFactory(user=student_user, school=school)
        foreign_teacher = TeacherUserFactory(school=other_school)
        foreign_assessment = self._make_assessment(other_school, foreign_teacher)

        _auth(api, student_user)
        resp = api.post(
            "/api/v1/gradebook/submissions/",
            {"assessment": str(foreign_assessment.id), "student": str(student.id)},
            format="json",
        )
        assert resp.status_code == 403, resp.content


# ─── 5. Bulk invoice generation ───────────────────────────────────────────────


class TestBulkGenerateTenantScoping:
    def test_foreign_academic_year_rejected(self, api, db):
        from tests.factories import FeeCategoryFactory, FeeStructureFactory, GradeFactory

        admin = AdminUserFactory()
        school = admin.school
        academic_year = AcademicYearFactory(school=school, is_current=True)
        grade = GradeFactory(school=school)
        fee_category = FeeCategoryFactory(school=school)
        structure = FeeStructureFactory(
            school=school,
            academic_year=academic_year,
            grade=grade,
            fee_category=fee_category,
        )
        foreign_year = AcademicYearFactory(school=SchoolFactory())

        _auth(api, admin)
        resp = api.post(
            "/api/v1/fees/invoices/bulk-generate/",
            {"fee_structure_id": structure.id, "academic_year_id": str(foreign_year.id)},
            format="json",
        )
        assert resp.status_code == 403, resp.content


# ─── 6. TeamMember write validation ───────────────────────────────────────────


class TestTeamMemberTenantScoping:
    def test_foreign_team_rejected(self, api, db):
        from services.sports.models import Sport, Team

        admin = AdminUserFactory()
        school = admin.school
        student = StudentFactory(school=school)
        foreign_school = SchoolFactory()
        foreign_sport = Sport.objects.create(school=foreign_school, name="Football")
        foreign_team = Team.objects.create(
            school=foreign_school,
            sport=foreign_sport,
            name="Foreign FC",
        )

        _auth(api, admin)
        resp = api.post(
            "/api/v1/sports/team-members/",
            {"team": str(foreign_team.id), "student": str(student.id), "role": "member"},
            format="json",
        )
        assert resp.status_code == 403, resp.content


# ─── 7. Bulk attendance write validation ──────────────────────────────────────


class TestBulkAttendanceTenantScoping:
    def test_foreign_student_rejected(self, api, db):
        teacher = TeacherUserFactory()
        school = teacher.school
        classroom = ClassroomFactory(school=school, class_teacher=teacher)
        foreign_student = StudentFactory()  # different school

        _auth(api, teacher)
        resp = api.post(
            "/api/v1/attendance/bulk-record/",
            {
                "classroom_id": classroom.id,
                "date": timezone.localdate().isoformat(),
                "records": [{"student_id": foreign_student.id, "status": "P"}],
            },
            format="json",
        )
        assert resp.status_code == 400, resp.content


# ─── 8. Duplicate overdue notifications ───────────────────────────────────────


class TestOverdueNotifications:
    def test_student_gets_single_overdue_notification(self, db):
        from services.communication.models import Notification
        from services.fees.tasks import mark_overdue_invoices

        school = SchoolFactory()
        student = StudentFactory(school=school)
        FeeInvoiceFactory(
            student=student,
            academic_year=AcademicYearFactory(school=school),
            due_date=timezone.localdate() - timedelta(days=2),
            status="unpaid",
        )

        result = mark_overdue_invoices()
        assert result["marked_overdue"] == 1

        count = Notification.objects.filter(
            user=student.user,
            channel="in_app",
            reference_type="fee_invoice",
            title="Fee Payment Overdue",
        ).count()
        assert count == 1, "student must receive exactly one in-app overdue notification"


# ─── 9. Query-param guards ────────────────────────────────────────────────────


class TestReportingParamGuards:
    def test_at_risk_rejects_bad_days(self, api, db):
        admin = AdminUserFactory()
        _auth(api, admin)
        resp = api.get("/api/v1/reporting/at-risk-students/?days=abc")
        assert resp.status_code == 400, resp.content

    def test_at_risk_rejects_bad_threshold(self, api, db):
        admin = AdminUserFactory()
        _auth(api, admin)
        resp = api.get("/api/v1/reporting/at-risk-students/?attendance_threshold=nope")
        assert resp.status_code == 400, resp.content


# ─── 10. Email URL origin validation ──────────────────────────────────────────


class TestEmailUrlOrigin:
    def test_reset_url_foreign_origin_rejected(self, api, db):
        from tests.url_helpers import AUTH_PASSWORD_RESET

        admin = AdminUserFactory()
        _auth(api, admin)
        resp = api.post(
            AUTH_PASSWORD_RESET,
            {"email": admin.email, "reset_url": "https://evil.example.com/phish"},
            format="json",
        )
        assert resp.status_code == 400, resp.content

    def test_reset_url_own_origin_allowed(self, api, db):
        from tests.url_helpers import AUTH_PASSWORD_RESET

        admin = AdminUserFactory()
        _auth(api, admin)
        resp = api.post(
            AUTH_PASSWORD_RESET,
            {"email": admin.email, "reset_url": "http://localhost:3000/reset-password/abc"},
            format="json",
        )
        assert resp.status_code == 200, resp.content


# ─── 11+12. Tenant middleware header guard ────────────────────────────────────


class TestTenantMiddlewareHeaderGuard:
    @staticmethod
    def _run_middleware(request):
        from core.middleware.tenant import TenantMiddleware

        mw = TenantMiddleware(lambda r: None)
        mw(request)
        return request.school

    def test_non_super_jwt_header_ignored(self, db):
        from django.test import RequestFactory
        from rest_framework_simplejwt.tokens import AccessToken

        admin = AdminUserFactory()
        other_school = AdminUserFactory().school
        token = AccessToken.for_user(admin)

        request = RequestFactory().get(
            "/api/v1/students/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
            HTTP_X_SCHOOL_ID=str(other_school.id),
        )
        assert self._run_middleware(request) == admin.school

    def test_super_admin_header_honored(self, db):
        from django.test import RequestFactory
        from rest_framework_simplejwt.tokens import AccessToken
        from tests.factories import UserFactory

        super_user = UserFactory(role="super_admin")
        target_school = AdminUserFactory().school
        token = AccessToken.for_user(super_user)

        request = RequestFactory().get(
            "/api/v1/students/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
            HTTP_X_SCHOOL_ID=str(target_school.id),
        )
        assert self._run_middleware(request) == target_school

    def test_malformed_header_does_not_500(self, db):
        from django.test import RequestFactory

        request = RequestFactory().get(
            "/api/v1/students/",
            HTTP_X_SCHOOL_ID="not-a-uuid",
        )
        # Must not raise ValueError; anonymous requests fall through to None.
        assert self._run_middleware(request) is None
