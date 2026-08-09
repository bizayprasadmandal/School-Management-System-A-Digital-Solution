"""
Management command: seed_operational_data

Creates the operational records the admin pages expect so they render real
data instead of empty states (Exams, HR, Admissions, Events, and the pages
gated on a current academic year like Timetable and Reports):

  * a CURRENT academic year (the previous seed data only ever created one
    for 2024-2025, so queries gated on useCurrentAcademicYear() stayed empty)
  * gradebook ExamType + Exam records for that year
  * HR Department + Employee records (linked to existing staff users)
  * admissions EnrollmentIntake periods
  * timetable SchoolEvent records (in the current month, so the month view
    actually displays them)

Idempotent — safe to run repeatedly. Seeds every school by default; target a
single school with --school <code-or-subdomain>.

Usage:
    python manage.py seed_operational_data
    python manage.py seed_operational_data --school demo
"""

from calendar import monthrange
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from services.admissions.models import EnrollmentIntake
from services.auth.models import School, User, UserRole
from services.gradebook.models import Exam, ExamType
from services.hr.models import Department, Employee
from services.students.models import AcademicYear
from services.timetable.models import SchoolEvent

# Role -> (designation, department name)
STAFF_MAP = {
    UserRole.SCHOOL_ADMIN: ("School Administrator", "Administration"),
    UserRole.TEACHER: ("Teacher", "Academics"),
    UserRole.ACCOUNTANT: ("Accountant", "Finance & Accounts"),
    UserRole.LIBRARIAN: ("Librarian", "Library"),
    UserRole.COUNSELOR: ("Counselor", "Academics"),
}

EXAM_TYPE_DATA = [
    ("Midterm Examination", "30.00", True),
    ("Final Examination", "50.00", True),
    ("Quiz", "10.00", False),
    ("Assignment", "10.00", False),
]

EVENT_DATA = [
    ("Science Fair", SchoolEvent.EventType.CULTURAL, "Annual science exhibition and project showcase"),
    ("Sports Day", SchoolEvent.EventType.SPORTS, "Inter-house athletics and games"),
    ("Parent-Teacher Meeting", SchoolEvent.EventType.PTM, "Semester progress discussions"),
    ("Public Holiday", SchoolEvent.EventType.HOLIDAY, "School closed for public holiday"),
    ("Field Trip", SchoolEvent.EventType.TRIP, "Educational excursion for students"),
]


class Command(BaseCommand):
    help = "Seed a current academic year, exams, employees, intakes, and events per school."

    def add_arguments(self, parser):
        parser.add_argument(
            "--school",
            type=str,
            default="",
            help="Only seed the school with this code or subdomain (default: all schools).",
        )

    def _current_academic_year(self):
        """Return (name, start_date, end_date) for the school year containing today.

        School years run September-June; anything from July onward belongs to the
        year that starts in September of the current calendar year.
        """
        today = timezone.localdate()
        start_year = today.year if today.month >= 7 else today.year - 1
        return f"{start_year}-{start_year + 1}", date(start_year, 9, 1), date(start_year + 1, 6, 30)

    # NOTE: no outer @transaction.atomic — each school commits in its own
    # transaction (see the loop) so one school failing never rolls back the rest.
    def handle(self, *args, **options):
        schools = School.objects.all().order_by("code")
        if options["school"]:
            schools = schools.filter(code=options["school"])
            if not schools.exists():
                # allow subdomain matching too
                schools = School.objects.filter(subdomain=options["school"])
            if not schools.exists():
                raise CommandError(f"No school found with code or subdomain '{options['school']}'")

        ay_name, ay_start, ay_end = self._current_academic_year()
        today = timezone.localdate()

        for school in schools:
            with transaction.atomic():
                created = {
                    "academic_year": 0,
                    "exam_types": 0,
                    "exams": 0,
                    "departments": 0,
                    "employees": 0,
                    "intakes": 0,
                    "events": 0,
                }

                admin = (
                    User.objects.filter(school=school, role=UserRole.SCHOOL_ADMIN, is_active=True).first()
                    or User.objects.filter(school=school, role=UserRole.SCHOOL_ADMIN).first()
                )

                # ── Current academic year ─────────────────────────────────────
                ay, ay_created = AcademicYear.objects.get_or_create(
                    school=school,
                    name=ay_name,
                    defaults={"start_date": ay_start, "end_date": ay_end},
                )
                if not ay.is_current:
                    ay.is_current = True  # save() clears other current years for the school
                    ay.save(update_fields=["is_current"])
                created["academic_year"] = 1 if ay_created else 0

                # ── Exams ─────────────────────────────────────────────────────
                exam_types = {}
                for name, weightage, terminal in EXAM_TYPE_DATA:
                    et, et_created = ExamType.objects.get_or_create(
                        school=school,
                        name=name,
                        defaults={"weightage": weightage, "is_terminal": terminal},
                    )
                    exam_types[name] = et
                    created["exam_types"] += 1 if et_created else 0

                exam_specs = [
                    (
                        "Midterm Examination",
                        "Midterm 2026",
                        ay_start.replace(month=10, day=27),
                        5,
                        Exam.Status.SCHEDULED,
                    ),
                    (
                        "Final Examination",
                        "Final Examination",
                        ay_end.replace(month=3, day=15),
                        11,
                        Exam.Status.SCHEDULED,
                    ),
                    ("Quiz", "Quiz 1", ay_start.replace(month=11, day=10), 1, Exam.Status.COMPLETED),
                    ("Quiz", "Quiz 2", ay_start.replace(month=1, day=20), 1, Exam.Status.SCHEDULED),
                ]
                for et_name, exam_name, start, span, status in exam_specs:
                    # start/end dates stay inside the academic year
                    end = min(start + timedelta(days=span - 1), ay_end)
                    _, exam_created = Exam.objects.get_or_create(
                        school=school,
                        academic_year=ay,
                        name=exam_name,
                        defaults={
                            "exam_type": exam_types[et_name],
                            "description": f"{et_name} for {ay_name}",
                            "start_date": start,
                            "end_date": end,
                            "status": status,
                            "created_by": admin,
                        },
                    )
                    created["exams"] += 1 if exam_created else 0

                # ── HR: departments + employees ───────────────────────────────
                departments = {}
                for dept_name in ["Academics", "Administration", "Finance & Accounts", "Library", "IT & Maintenance"]:
                    dept, dept_created = Department.objects.get_or_create(
                        school=school,
                        name=dept_name,
                        defaults={"code": dept_name[:3].upper(), "head": admin, "is_active": True},
                    )
                    departments[dept_name] = dept
                    created["departments"] += 1 if dept_created else 0

                staff_users = list(
                    User.objects.filter(school=school, role__in=STAFF_MAP.keys(), is_active=True).order_by(
                        "role", "email"
                    )
                )
                for idx, user in enumerate(staff_users, start=1):
                    designation, dept_name = STAFF_MAP[user.role]
                    _, emp_created = Employee.objects.get_or_create(
                        school=school,
                        user=user,
                        defaults={
                            "employee_id": f"{school.code}-EMP-{idx:03d}",
                            "department": departments[dept_name],
                            "designation": designation,
                            "employment_type": Employee.EmploymentType.FULL_TIME,
                            "status": Employee.Status.ACTIVE,
                            "joining_date": date(today.year - 3, 8, 1),
                            "phone": user.phone or "+1-555-0100",
                            "address": "School campus",
                        },
                    )
                    created["employees"] += 1 if emp_created else 0

                # ── Admissions: intake periods ────────────────────────────────
                intake_specs = [
                    (
                        f"Fall {ay_name.split('-')[0]} Intake",
                        EnrollmentIntake.Status.OPEN,
                        today - timedelta(days=30),
                        today + timedelta(days=60),
                    ),
                    (
                        f"Spring {ay_name.split('-')[1]} Intake",
                        EnrollmentIntake.Status.UPCOMING,
                        today + timedelta(days=90),
                        today + timedelta(days=180),
                    ),
                    (
                        f"Summer {ay_name.split('-')[0]} Intake",
                        EnrollmentIntake.Status.CLOSED,
                        today - timedelta(days=120),
                        today - timedelta(days=60),
                    ),
                ]
                for name, status, start, end in intake_specs:
                    _, intake_created = EnrollmentIntake.objects.get_or_create(
                        school=school,
                        name=name,
                        defaults={
                            "academic_year": ay_name,
                            "application_start": start,
                            "application_end": end,
                            "status": status,
                            "max_applications": 200,
                            "description": f"Enrollment period for {ay_name}",
                        },
                    )
                    created["intakes"] += 1 if intake_created else 0

                # ── Events: in the current month so the calendar view shows them ─
                last_day = monthrange(today.year, today.month)[1]
                event_days = [
                    min(5, last_day),
                    min(12, last_day),
                    min(18, last_day),
                    min(24, last_day),
                    min(28, last_day),
                ]
                for (title, etype, desc), day in zip(EVENT_DATA, event_days):
                    ev_start = today.replace(day=day)
                    _, event_created = SchoolEvent.objects.get_or_create(
                        school=school,
                        title=title,
                        start_date=ev_start,
                        defaults={
                            "description": desc,
                            "event_type": etype,
                            "end_date": ev_start,
                            "start_time": "10:00",
                            "end_time": "12:00",
                            "venue": "School Campus",
                            "is_school_wide": True,
                            "created_by": admin,
                        },
                    )
                    created["events"] += 1 if event_created else 0

            counts = ", ".join(f"{k}: {v}" for k, v in created.items())
            self.stdout.write(self.style.SUCCESS(f"  {school.code} ({school.name}): {counts}"))

        # Plain ASCII — the management command can run on Windows consoles (cp1252).
        self.stdout.write(self.style.SUCCESS("\nOperational data seeded."))
        self.stdout.write(f"  Current academic year: {ay_name} ({ay_start} - {ay_end})")
