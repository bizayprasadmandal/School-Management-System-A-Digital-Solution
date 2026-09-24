"""Give demo teachers a complete workspace (rerunnable, per school).

The generic seeder scatters rows without teacher ownership, so a real
teacher login can show empty tabs: gradebook assessments (teacher-filtered
via assignment), lesson plans (assignment__teacher), period attendance
(assignment__teacher), payslips (employee__user), and the inbox
(sender/recipient). This pass creates, for up to N teachers per school:

- 2 TeacherAssignments (subject + classroom from the school's own pools)
- 3 LessonPlans per assignment (past week)
- 2 Assessments per assignment (one open, one closed)
- PeriodAttendance for the roster of one classroom (yesterday)
- Employee record + 3 Payslips (last 3 months)
- 2 DirectMessages in/out with other staff

Usage (inside the backend container):
    python scripts/seed_teacher_workspace.py [School Name]
"""

import os
import random
import sys
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.apps import apps  # noqa: E402
from django.db import IntegrityError, transaction  # noqa: E402

from services.auth.models import School  # noqa: E402

MAX_TEACHERS = 8
MONTHS = 3


def get_school(name):
    try:
        return School.objects.get(name__iexact=name)
    except School.DoesNotExist:
        return School.objects.first()


def pick(model, **filters):
    return model.objects.filter(**filters).order_by("?").first()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    school = get_school(args[0]) if args else School.objects.first()
    print(f"school: {school.name}")

    User = apps.get_model("auth_service", "User")
    TeacherAssignment = apps.get_model("academics", "TeacherAssignment")
    LessonPlan = apps.get_model("academics", "LessonPlan")
    Assessment = apps.get_model("gradebook", "Assessment")
    PeriodAttendance = apps.get_model("attendance", "PeriodAttendance")
    Employee = apps.get_model("hr", "Employee")
    Payslip = apps.get_model("hr", "Payslip")
    DirectMessage = apps.get_model("communication", "DirectMessage")
    Subject = apps.get_model("academics", "Subject")
    Classroom = apps.get_model("students", "Classroom")
    AY = apps.get_model("students", "AcademicYear")

    ay = AY.objects.filter(school=school, is_current=True).first() or AY.objects.filter(
        school=school
    ).first()

    subjects = list(Subject.objects.filter(school=school))
    # Only classrooms that actually have enrolled students — assignments
    # pointing at empty classrooms leave the teacher with a dead roster
    classrooms = list(
        Classroom.objects.filter(school=school, enrollments__is_active=True).distinct()
    )
    teachers = list(
        User.objects.filter(role="teacher", school=school, is_active=True)[:MAX_TEACHERS]
    )
    print(
        f"teachers: {len(teachers)} | subjects: {len(subjects)} | "
        f"classrooms: {len(classrooms)} | ay: {ay}"
    )
    if not (teachers and subjects and classrooms and ay):
        print("nothing to do — missing teachers/subjects/classrooms/AY")
        return

    today = date.today()
    created = {"assign": 0, "plan": 0, "assess": 0, "patt": 0, "emp": 0, "payslip": 0, "dm": 0}

    for ti, teacher in enumerate(teachers):
        # ── TeacherAssignments (2 per teacher, unique classroom+subject) ────
        pairs = random.sample(
            [
                (s, c)
                for s in subjects
                for c in classrooms
                if not TeacherAssignment.objects.filter(
                    teacher=teacher, subject=s, classroom=c
                ).exists()
            ],
            min(2, len(subjects) * len(classrooms)),
        )
        assignments = list(TeacherAssignment.objects.filter(teacher=teacher))
        for s, c in pairs:
            a = TeacherAssignment.objects.create(
                teacher=teacher,
                subject=s,
                classroom=c,
                academic_year=ay,
                is_primary=True,
            )
            assignments.append(a)
            created["assign"] += 1

        # ── LessonPlans (3 per assignment, last week) ───────────────────────
        for a in assignments:
            if LessonPlan.objects.filter(assignment=a).exists():
                continue
            for i in range(3):
                LessonPlan.objects.create(
                    assignment=a,
                    title=f"Unit {i + 1}: {a.subject.name} fundamentals",
                    topic=f"Topic {i + 1}",
                    objectives="Students will master the unit objectives.",
                    content="Warm-up, guided practice, independent work, exit ticket.",
                    resources="Textbook ch. 1, worksheet pack",
                    date=today - timedelta(days=7 - i),
                    duration_minutes=45,
                    status="completed" if i < 2 else "planned",
                )
                created["plan"] += 1

        # ── Assessments (2 per assignment: one open, one closed) ────────────
        for a in assignments:
            if Assessment.objects.filter(assignment=a).exists():
                continue
            Assessment.objects.create(
                assignment=a,
                title=f"{a.subject.name} Quiz 1",
                assessment_type="quiz",
                due_date=today + timedelta(days=7),
                max_marks=Decimal("20"),
                description="Covers unit 1 material.",
            )
            Assessment.objects.create(
                assignment=a,
                title=f"{a.subject.name} Homework 1",
                assessment_type="homework",
                due_date=today - timedelta(days=3),
                max_marks=Decimal("10"),
                description="Practice problems ch. 1.",
            )
            created["assess"] += 2

        # ── PeriodAttendance (one past school day for first assignment) ─────
        a = assignments[0]
        if a and not PeriodAttendance.objects.filter(assignment=a).exists():
            roster = list(
                apps.get_model("students", "Enrollment")
                .objects.filter(classroom=a.classroom, is_active=True)
                .select_related("student")[:30]
            )
            att_date = today - timedelta(days=1)
            while att_date.weekday() >= 5:
                att_date -= timedelta(days=1)
            for row in roster:
                # PeriodAttendance.status is a 1-char code (P/A/L/E/H)
                PeriodAttendance.objects.create(
                    student=row.student,
                    assignment=a,
                    date=att_date,
                    period_number=1,
                    status=random.choices(["P", "A", "L"], weights=[90, 5, 5])[0],
                    recorded_by=teacher,
                )
                created["patt"] += 1

        # ── Employee + Payslips (last 3 months) ─────────────────────────────
        emp = Employee.objects.filter(user=teacher, school=school).first()
        if not emp:
            emp = Employee.objects.create(
                school=school,
                user=teacher,
                employee_id=f"EMP-{teacher.id.hex[:6].upper()}",
                designation="Teacher",
                employment_type="full_time",
                status="active",
                joining_date=today - timedelta(days=400 + ti * 30),
            )
            created["emp"] += 1
        if not Payslip.objects.filter(employee=emp).exists():
            base = Decimal("42000") + Decimal(ti * 1500)
            for m in range(MONTHS):
                month_start = (today.replace(day=1) - timedelta(days=30 * m)).replace(day=1)
                month_end = (month_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
                gross = base
                deductions = gross * Decimal("0.18")
                Payslip.objects.create(
                    school=school,
                    employee=emp,
                    period_start=month_start,
                    period_end=month_end,
                    basic_salary=gross * Decimal("0.7"),
                    housing_allowance=gross * Decimal("0.15"),
                    transport_allowance=gross * Decimal("0.1"),
                    medical_allowance=gross * Decimal("0.05"),
                    other_allowances=Decimal("0"),
                    tax_deduction=deductions * Decimal("0.6"),
                    pension_deduction=deductions * Decimal("0.3"),
                    other_deductions=deductions * Decimal("0.1"),
                    gross_pay=gross,
                    total_deductions=deductions,
                    net_pay=gross - deductions,
                    status="paid" if m > 0 else "pending",
                    payment_date=month_end if m > 0 else None,
                    payment_method="bank_transfer",
                )
                created["payslip"] += 1

        # ── ConferenceSlots (3 today: 2 open, 1 booked) ─────────────────────
        ConferenceSlot = apps.get_model("conferences", "ConferenceSlot")
        if not ConferenceSlot.objects.filter(teacher=teacher, date=today).exists():
            roster = list(
                apps.get_model("students", "Student")
                .objects.filter(school=school, enrollments__classroom__in=[
                    a.classroom for a in assignments
                ], enrollments__is_active=True)[:3]
            )
            from datetime import time as dtime

            for i, start_min in enumerate([9 * 60, 9 * 60 + 30, 10 * 60]):
                student = roster[i] if i < len(roster) else None
                ConferenceSlot.objects.create(
                    school=school,
                    teacher=teacher,
                    student=student,
                    date=today,
                    start_time=dtime(start_min // 60, start_min % 60),
                    end_time=dtime((start_min + 15) // 60, (start_min + 15) % 60),
                    is_booked=i == 2 and student is not None,
                    notes="Parent-teacher conference",
                )
                created["slots"] = created.get("slots", 0) + 1

        # ── DirectMessages (2 in/out with another staff member) ─────────────
        if not DirectMessage.objects.filter(sender=teacher).exists() and not DirectMessage.objects.filter(
            recipient=teacher
        ).exists():
            partner = next(
                (t for t in teachers if t.id != teacher.id),
                User.objects.filter(school=school, role="school_admin").first(),
            )
            if partner:
                DirectMessage.objects.create(
                    sender=partner,
                    recipient=teacher,
                    content="Hi! Sharing the term plan for our joint class — let me know your thoughts.",
                    status="read",
                    sent_at=timezone_now_minus(26),
                )
                DirectMessage.objects.create(
                    sender=teacher,
                    recipient=partner,
                    content="Thanks — looks great. I'll align my unit 2 timeline with yours.",
                    status="read",
                    sent_at=timezone_now_minus(25),
                )
                created["dm"] += 2

    print("\ncreated:", created)


def timezone_now_minus(hours):
    import django.utils.timezone as tz

    return tz.now() - timedelta(hours=hours)


if __name__ == "__main__":
    main()
