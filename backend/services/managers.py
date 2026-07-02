"""
Custom QuerySet Managers — chainable, school-scoped querysets for all major services.
Import and use as: Student.objects.active().for_school(school)
"""

from django.db import models
from django.utils import timezone


# ─── Students ─────────────────────────────────────────────────────────────────

class StudentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)

    def for_school(self, school):
        return self.filter(school=school)

    def for_classroom(self, classroom):
        return self.filter(
            enrollments__classroom=classroom,
            enrollments__is_active=True
        ).distinct()

    def for_grade(self, grade):
        return self.filter(
            enrollments__classroom__grade=grade,
            enrollments__is_active=True
        ).distinct()

    def for_academic_year(self, academic_year):
        return self.filter(
            enrollments__academic_year=academic_year,
            enrollments__is_active=True
        ).distinct()

    def with_full_profile(self):
        return self.select_related("user", "school").prefetch_related(
            "enrollments__classroom__grade",
            "guardians__user",
        )

    def gender(self, gender_code):
        return self.filter(gender=gender_code)

    def admitted_between(self, start, end):
        return self.filter(admission_date__range=[start, end])


class StudentManager(models.Manager):
    def get_queryset(self):
        return StudentQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def for_school(self, school):
        return self.get_queryset().for_school(school)


# ─── Attendance ────────────────────────────────────────────────────────────────

class AttendanceQuerySet(models.QuerySet):
    def for_school(self, school):
        return self.filter(student__school=school)

    def for_student(self, student):
        return self.filter(student=student)

    def for_classroom(self, classroom):
        return self.filter(classroom=classroom)

    def for_date(self, date):
        return self.filter(date=date)

    def for_date_range(self, start, end):
        return self.filter(date__range=[start, end])

    def for_month(self, year, month):
        return self.filter(date__year=year, date__month=month)

    def present(self):
        return self.filter(status__in=["P", "L"])

    def absent(self):
        return self.filter(status="A")

    def late(self):
        return self.filter(status="L")

    def excused(self):
        return self.filter(status="E")

    def unnotified(self):
        return self.filter(status="A", notified_guardian=False)

    def attendance_percentage(self):
        """Return attendance percentage across this queryset."""
        total = self.count()
        if total == 0:
            return 0.0
        present = self.present().count()
        return round(present / total * 100, 2)


class AttendanceManager(models.Manager):
    def get_queryset(self):
        return AttendanceQuerySet(self.model, using=self._db)

    def for_school(self, school):
        return self.get_queryset().for_school(school)

    def today(self):
        return self.get_queryset().for_date(timezone.now().date())


# ─── Fee Invoice ──────────────────────────────────────────────────────────────

class FeeInvoiceQuerySet(models.QuerySet):
    def for_school(self, school):
        return self.filter(student__school=school)

    def for_student(self, student):
        return self.filter(student=student)

    def unpaid(self):
        return self.filter(status__in=["unpaid", "partial"])

    def overdue(self):
        return self.filter(status="overdue")

    def paid(self):
        return self.filter(status="paid")

    def due_before(self, date):
        return self.filter(due_date__lte=date)

    def for_academic_year(self, academic_year):
        return self.filter(academic_year=academic_year)

    def total_outstanding(self):
        from django.db.models import Sum, F, ExpressionWrapper, DecimalField
        result = self.unpaid().aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("total_amount") - F("paid_amount"),
                    output_field=DecimalField()
                )
            )
        )
        return result["total"] or 0

    def total_collected(self):
        from django.db.models import Sum
        return self.paid().aggregate(total=Sum("paid_amount"))["total"] or 0


class FeeInvoiceManager(models.Manager):
    def get_queryset(self):
        return FeeInvoiceQuerySet(self.model, using=self._db)

    def for_school(self, school):
        return self.get_queryset().for_school(school)

    def unpaid(self):
        return self.get_queryset().unpaid()

    def overdue(self):
        return self.get_queryset().overdue()


# ─── Grade (Gradebook) ────────────────────────────────────────────────────────

class GradeQuerySet(models.QuerySet):
    def for_student(self, student):
        return self.filter(student=student)

    def for_exam(self, exam):
        return self.filter(exam_schedule__exam=exam)

    def for_subject(self, subject):
        return self.filter(exam_schedule__subject=subject)

    def passed(self):
        from django.db.models import F
        return self.filter(
            is_absent=False,
            marks_obtained__gte=F("exam_schedule__passing_marks")
        )

    def failed(self):
        from django.db.models import F
        return self.filter(
            is_absent=False,
            marks_obtained__lt=F("exam_schedule__passing_marks")
        )

    def absent(self):
        return self.filter(is_absent=True)

    def average_percentage(self):
        from django.db.models import Avg, F, ExpressionWrapper, FloatField
        return self.filter(is_absent=False, marks_obtained__isnull=False).aggregate(
            avg=Avg(
                ExpressionWrapper(
                    F("marks_obtained") * 100.0 / F("exam_schedule__max_marks"),
                    output_field=FloatField()
                )
            )
        )["avg"]


class GradeManager(models.Manager):
    def get_queryset(self):
        return GradeQuerySet(self.model, using=self._db)

    def for_student(self, student):
        return self.get_queryset().for_student(student)


# ─── Announcement ─────────────────────────────────────────────────────────────

class AnnouncementQuerySet(models.QuerySet):
    def for_school(self, school):
        return self.filter(school=school)

    def published(self):
        return self.filter(is_draft=False, published_at__isnull=False)

    def active(self):
        return self.published().filter(
            models.Q(expires_at__isnull=True) |
            models.Q(expires_at__gt=timezone.now())
        )

    def for_audience(self, role):
        audience_map = {
            "student":      ["all", "students"],
            "parent":       ["all", "parents"],
            "teacher":      ["all", "teachers", "staff"],
            "school_admin": ["all", "teachers", "students", "parents", "staff"],
        }
        allowed = audience_map.get(role, ["all"])
        return self.filter(audience__in=allowed)

    def urgent(self):
        return self.filter(priority="urgent")


class AnnouncementManager(models.Manager):
    def get_queryset(self):
        return AnnouncementQuerySet(self.model, using=self._db)

    def active_for_school(self, school):
        return self.get_queryset().for_school(school).active()
