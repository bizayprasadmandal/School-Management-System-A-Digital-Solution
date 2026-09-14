"""
Seed rich academic history tied to a school's existing students/classrooms.

Fills the thin spots the other seeders leave behind, strictly scoped to ONE
school (School.objects.first()) so the demo login actually sees the data:

  infrastructure  - teacher assignments, subjects per grade, exam types,
                    exams, and exam schedules (created if missing)
  timetable       - slots for every active classroom (5 days x teaching periods)
  assessments     - per teacher assignment, with submissions for the class
  grades          - per exam schedule x enrolled student
  fees            - invoices (+ payments) per student from the fee structures
  attendance      - weekday history for the last N days

Idempotent: every write is get_or_create or bulk_create(ignore_conflicts);
re-running tops up only what is missing.

Usage:
    python manage.py seed_academic_history
    python manage.py seed_academic_history --days 90 --assessments 6
"""

import random
from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from faker import Faker
from services.auth.models import School, User
from services.students.models import AcademicYear, Enrollment

Faker.seed(7)
random.seed(7)

ASSESSMENT_TYPES = ["homework", "quiz", "project", "classwork", "lab"]
MAX_MARKS_CYCLE = [20, 25, 50, 100]
PAYMENT_METHODS = ["cash", "bank_transfer", "card", "online", "mobile"]
CORE_SUBJECTS = [
    "Mathematics",
    "English",
    "Science",
    "Social Studies",
    "Computer Science",
]


class Command(BaseCommand):
    help = "Seed timetable, assessments, grades, invoices, and attendance history for existing students."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=60,
            help="Weekdays of attendance history to backfill.",
        )
        parser.add_argument(
            "--assessments",
            type=int,
            default=4,
            help="Assessments to create per teacher assignment.",
        )

    # ─── small helpers ──────────────────────────────────────────────────────

    def ability(self, student_id):
        """Stable per-student ability in [50, 95) so marks stay coherent."""
        try:
            return 50 + (int(student_id) % 45)
        except (TypeError, ValueError):
            return 50 + (hash(str(student_id)) % 45)

    def mark(self, student_id, max_marks):
        val = random.gauss(self.ability(student_id) / 100, 0.09) * max_marks
        return round(max(0, min(max_marks, val)), 1)

    def weekday_dates(self, n_days):
        dates, d = [], timezone.localdate()
        while len(dates) < n_days:
            if d.weekday() < 5:
                dates.append(d)
            d -= timedelta(days=1)
        return list(reversed(dates))

    def bulk(self, model, rows, chunk=1000):
        """bulk_create with conflict tolerance; returns actually-inserted count."""
        made = 0
        for i in range(0, len(rows), chunk):
            returned = model.objects.bulk_create(rows[i : i + chunk], ignore_conflicts=True)
            made += sum(1 for obj in returned if obj.pk is not None)
        return made

    # ─── infrastructure builders ────────────────────────────────────────────

    def ensure_subjects(self, school, grades):
        """Ensure each grade has at least the core subjects available."""
        Subject = self.apps.get_model("academics", "Subject")
        made = 0
        for grade in grades:
            have = set(Subject.objects.filter(school=school, grade=grade).values_list("name", flat=True))
            for name in CORE_SUBJECTS:
                if name in have:
                    continue
                subj, created = Subject.objects.get_or_create(
                    school=school,
                    grade=grade,
                    name=name,
                    defaults={
                        "code": f"{name[:3].upper()}-{grade.id}",
                        "max_marks": 100,
                        "pass_marks": 35,
                        "is_core": True,
                        "is_active": True,
                    },
                )
                made += created
        return made

    def ensure_teacher_assignments(self, school, ay, classrooms, grades_with_subjects):
        """5 teacher assignments per classroom, round-robin across teachers."""
        TA = self.apps.get_model("academics", "TeacherAssignment")
        Subject = self.apps.get_model("academics", "Subject")
        teachers = list(User.objects.filter(school=school, role="teacher"))
        if not teachers:
            self.stderr.write("  no teachers found for school — cannot assign")
            return {}
        made = 0
        assignments_by_class = {}
        idx = 0
        for classroom in classrooms:
            subjects = list(Subject.objects.filter(school=school, grade=classroom.grade).order_by("name")[:5])
            for subject in subjects:
                ta, created = TA.objects.get_or_create(
                    teacher=teachers[idx % len(teachers)],
                    subject=subject,
                    classroom=classroom,
                    academic_year=ay,
                )
                idx += 1
                made += created
                assignments_by_class.setdefault(classroom.id, []).append(ta)
        self.stdout.write(self.style.SUCCESS(f"  teacher assignments ensured: +{made}"))
        return assignments_by_class

    def ensure_exam_infrastructure(self, school, ay, classrooms, assignments_by_class):
        """ExamTypes, Exams (Midterm/Final), and schedules per (exam, subject, class)."""
        ExamType = self.apps.get_model("gradebook", "ExamType")
        Exam = self.apps.get_model("gradebook", "Exam")
        Schedule = self.apps.get_model("gradebook", "ExamSchedule")
        today = timezone.localdate()
        start = ay.start_date or (today - timedelta(days=200))

        types = {}
        for name, weight, terminal in (
            ("Midterm", 30, True),
            ("Final", 50, True),
            ("Unit Test", 10, False),
        ):
            et, _ = ExamType.objects.get_or_create(
                school=school,
                name=name,
                defaults={"weightage": weight, "is_terminal": terminal},
            )
            types[name] = et

        exams = {}
        for name in ("Midterm", "Final"):
            exam, created = Exam.objects.get_or_create(
                school=school,
                academic_year=ay,
                exam_type=types[name],
                name=name,
                defaults={
                    "start_date": start + timedelta(days=60 if name == "Midterm" else 150),
                    "end_date": start + timedelta(days=68 if name == "Midterm" else 158),
                },
            )
            exams[name] = exam

        made_sched = 0
        schedules_by_class = {}
        for classroom in classrooms:
            tas = assignments_by_class.get(classroom.id) or []
            for name in ("Midterm", "Final"):
                exam = exams[name]
                offset = 0 if name == "Midterm" else 90
                for j, ta in enumerate(tas):
                    subj = ta.subject
                    sched, created = Schedule.objects.get_or_create(
                        exam=exam,
                        subject=subj,
                        classroom=classroom,
                        defaults={
                            "date": start + timedelta(days=offset + j),
                            "start_time": time(9 + (j % 4), 0),
                            "end_time": time(9 + (j % 4), 45),
                            "max_marks": 100,
                            "passing_marks": 35,
                        },
                    )
                    made_sched += created
                    schedules_by_class.setdefault(classroom.id, []).append(sched)
        self.stdout.write(self.style.SUCCESS(f"  exam schedules ensured: +{made_sched}"))
        return schedules_by_class

    # ─── data seeders ───────────────────────────────────────────────────────

    def seed_timetable(self, ay, classrooms, assignments_by_class, periods):
        Slot = self.apps.get_model("timetable", "TimetableSlot")
        teaching = sorted(
            [p for p in periods if not any(k in (p.name or "").lower() for k in ("break", "lunch"))],
            key=lambda p: p.start_time or time(9, 0),
        )
        made = 0
        for classroom in classrooms:
            tas = assignments_by_class.get(classroom.id) or []
            if not tas:
                continue
            for day in range(5):
                for idx, period in enumerate(teaching):
                    ta = tas[(day * len(teaching) + idx) % len(tas)]
                    _, created = Slot.objects.get_or_create(
                        classroom=classroom,
                        period=period,
                        day_of_week=day,
                        academic_year=ay,
                        defaults={
                            "assignment": ta,
                            "room": f"R{(idx % 6) + 1}{classroom.id % 10}",
                            "effective_from": ay.start_date,
                            "effective_to": ay.end_date,
                        },
                    )
                    made += created
        return made

    def seed_assessments(self, assignments_by_class, n_per):
        Assessment = self.apps.get_model("gradebook", "Assessment")
        Submission = self.apps.get_model("gradebook", "AssessmentSubmission")
        today = timezone.localdate()
        made_a = made_s = 0
        sub_rows = []
        for classroom_id, tas in assignments_by_class.items():
            students = list(
                Enrollment.objects.filter(classroom_id=classroom_id, academic_year=self.ay, is_active=True).values_list(
                    "student_id", flat=True
                )
            )
            for ta in tas:
                if Assessment.objects.filter(assignment=ta).count() >= n_per:
                    continue
                subject = ta.subject.name if ta.subject and ta.subject.name else "General"
                for i in range(n_per - Assessment.objects.filter(assignment=ta).count()):
                    atype = ASSESSMENT_TYPES[(ta.id + i) % len(ASSESSMENT_TYPES)]
                    due = today - timedelta(days=((ta.id + i * 13) % 150) + 2)
                    a = Assessment.objects.create(
                        assignment=ta,
                        title=f"{atype.title()} {i + 1} — {subject[:24]}",
                        assessment_type=atype,
                        due_date=due,
                        max_marks=MAX_MARKS_CYCLE[(ta.id + i) % len(MAX_MARKS_CYCLE)],
                    )
                    made_a += 1
                    for sid in students:
                        late = random.random() < 0.15
                        submitted = datetime.combine(
                            due - timedelta(days=0 if late else 1),
                            time(random.randint(8, 20), random.randint(0, 59)),
                        )
                        if settings.USE_TZ:
                            submitted = timezone.make_aware(submitted)
                        sub_rows.append(
                            Submission(
                                assessment=a,
                                student_id=sid,
                                marks_obtained=self.mark(sid, a.max_marks),
                                submitted_at=submitted,
                                is_late=late,
                                remarks="",
                            )
                        )
        made_s = self.bulk(Submission, sub_rows, chunk=2000)
        return made_a, made_s

    def seed_grades(self, schedules_by_class, enrollments_by_class):
        Grade = self.apps.get_model("gradebook", "Grade")
        teacher = User.objects.filter(school=self.school, role="teacher").first()
        rows = []
        for classroom_id, schedules in schedules_by_class.items():
            for sched in schedules:
                for student in enrollments_by_class.get(classroom_id, []):
                    rows.append(
                        Grade(
                            student=student,
                            exam_schedule=sched,
                            marks_obtained=self.mark(student.id, float(sched.max_marks or 100)),
                            graded_by=teacher,
                        )
                    )
        return self.bulk(Grade, rows, chunk=2000)

    def seed_invoices(self, ay, enrollments):
        Invoice = self.apps.get_model("fees", "FeeInvoice")
        Payment = self.apps.get_model("fees", "Payment")
        FeeStructure = self.apps.get_model("fees", "FeeStructure")
        admin = User.objects.filter(school=self.school, role="school_admin").first()
        today = timezone.localdate()
        prefix = (ay.name or "AY").replace("-", "")
        existing = set(Invoice.objects.filter(academic_year=ay).values_list("invoice_number", flat=True))
        inv_rows = []
        start = ay.start_date or (today - timedelta(days=300))
        span = ((ay.end_date or today) - start).days or 300
        for n, enr in enumerate(enrollments):
            structures = FeeStructure.objects.filter(academic_year=ay, grade=enr.classroom.grade)
            for fs in structures:
                number = f"INV-{prefix}-{enr.student.admission_number or enr.student_id}-{fs.id}"
                if number in existing:
                    continue
                existing.add(number)
                due = start + timedelta(days=(fs.id * 17 + n * 3) % span)
                base = float(fs.amount or 0)
                roll = random.random()
                if roll < 0.62:
                    status, paid = "paid", base
                elif roll < 0.80:
                    status, paid = "partial", round(base * random.uniform(0.3, 0.7), 2)
                elif roll < 0.93:
                    status, paid = ("overdue" if due < today else "unpaid"), 0.0
                else:
                    status, paid = "unpaid", 0.0
                inv_rows.append(
                    Invoice(
                        invoice_number=number,
                        student=enr.student,
                        academic_year=ay,
                        fee_structure=fs,
                        due_date=due,
                        base_amount=base,
                        discount_amount=0,
                        late_fee=0,
                        total_amount=base,
                        paid_amount=paid,
                        status=status,
                        created_by=admin,
                    )
                )
        made_inv = self.bulk(Invoice, inv_rows, chunk=1000)

        pay_rows = []
        have = set(Payment.objects.values_list("invoice_id", flat=True))
        for inv in Invoice.objects.filter(academic_year=ay, paid_amount__gt=0):
            if inv.id in have:
                continue
            pay_rows.append(
                Payment(
                    invoice=inv,
                    amount=inv.paid_amount,
                    payment_method=random.choice(PAYMENT_METHODS),
                )
            )
        made_pay = self.bulk(Payment, pay_rows, chunk=1000)
        return made_inv, made_pay

    def seed_attendance(self, ay, enrollments_by_class, teachers_by_class, days):
        Record = self.apps.get_model("attendance", "AttendanceRecord")
        dates = self.weekday_dates(days)
        have = set(Record.objects.filter(academic_year=ay).values_list("student_id", "date"))
        rows = []
        now = timezone.now()
        for classroom_id, students in enrollments_by_class.items():
            teacher = teachers_by_class.get(classroom_id)
            for student in students:
                for date in dates:
                    if (student.id, date) in have:
                        continue
                    roll = random.random()
                    status = "P" if roll < 0.92 else "A" if roll < 0.96 else "L" if roll < 0.98 else "E"
                    rows.append(
                        Record(
                            student=student,
                            classroom_id=classroom_id,
                            academic_year=ay,
                            date=date,
                            status=status,
                            recorded_by=teacher,
                            recorded_at=now,
                            remarks="",
                            notified_guardian=status in ("A", "L"),
                        )
                    )
        return self.bulk(Record, rows, chunk=2000)

    # ─── entry point ────────────────────────────────────────────────────────

    def handle(self, *args, **options):
        from django.apps import apps as dj_apps

        self.apps = dj_apps

        school = School.objects.first()
        if not school:
            self.stderr.write("No school found — run seed_demo_data first.")
            return
        self.school = school

        ay = (
            AcademicYear.objects.filter(school=school)
            .annotate(n=Count("enrollment", filter=None, distinct=True))
            .order_by("-n")
            .first()
        )
        if not ay:
            self.stderr.write("No academic year for the school — run seed_demo_data first.")
            return
        self.ay = ay

        enrollments = list(
            Enrollment.objects.filter(academic_year=ay, is_active=True).select_related(
                "student", "classroom", "classroom__grade"
            )
        )
        if not enrollments:
            self.stderr.write(f"No active enrollments for {ay} — nothing to seed against.")
            return
        classrooms = sorted({e.classroom for e in enrollments}, key=lambda c: c.id)
        grades = sorted({c.grade for c in classrooms if c.grade}, key=lambda g: g.id)
        enrollments_by_class = {}
        for e in enrollments:
            enrollments_by_class.setdefault(e.classroom_id, []).append(e.student)

        self.stdout.write(
            f"Seeding academic history for {school} — {ay.name}: "
            f"{len(enrollments)} students, {len(classrooms)} classrooms"
        )

        n_subj = self.ensure_subjects(school, grades)
        self.stdout.write(self.style.SUCCESS(f"  subjects ensured: +{n_subj}"))

        assignments_by_class = self.ensure_teacher_assignments(school, ay, classrooms, grades)
        teachers_by_class = {cid: (tas[0].teacher if tas else None) for cid, tas in assignments_by_class.items()}

        schedules_by_class = self.ensure_exam_infrastructure(school, ay, classrooms, assignments_by_class)

        periods = list(dj_apps.get_model("timetable", "Period").objects.all())
        n_slots = self.seed_timetable(ay, classrooms, assignments_by_class, periods)
        self.stdout.write(self.style.SUCCESS(f"  timetable slots created: {n_slots}"))

        n_a, n_s = self.seed_assessments(assignments_by_class, options["assessments"])
        self.stdout.write(self.style.SUCCESS(f"  assessments: {n_a}, submissions: {n_s}"))

        n_g = self.seed_grades(schedules_by_class, enrollments_by_class)
        self.stdout.write(self.style.SUCCESS(f"  grades: {n_g}"))

        n_inv, n_pay = self.seed_invoices(ay, enrollments)
        self.stdout.write(self.style.SUCCESS(f"  invoices: {n_inv}, payments: {n_pay}"))

        n_att = self.seed_attendance(ay, enrollments_by_class, teachers_by_class, options["days"])
        self.stdout.write(self.style.SUCCESS(f"  attendance records: {n_att}"))

        self.stdout.write(self.style.SUCCESS("Done."))
