"""
Management command: seed_counseling_demo_data
Creates sample counseling appointments and student referrals so the counselor
appointments and referrals pages have realistic demo data.

Usage:
    python manage.py seed_counseling_demo_data
    python manage.py seed_counseling_demo_data --appointments 20 --referrals 15
    python manage.py seed_counseling_demo_data --flush
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta, time
import random


REASONS = [
    "Student has been struggling with math concepts and needs additional support.",
    "Showing signs of anxiety before exams. Would benefit from stress management strategies.",
    "Frequent tardiness to first period class. Need to explore underlying causes.",
    "Recent decline in academic performance across multiple subjects.",
    "Student expressed interest in career counseling for college planning.",
    "Social withdrawal observed during group activities. May need coping strategies.",
    "Family circumstances may be affecting focus and classroom participation.",
    "Repeated behavioral incidents in class. Requires behavioral intervention plan.",
    "Student shows exceptional aptitude in science. Discuss advanced placement options.",
    "Concerns about peer relationships and social integration.",
    "Attendance has dropped significantly over the past month. Check on wellbeing.",
    "Student reported feeling overwhelmed with extracurricular workload.",
    "Displaying signs of perfectionism affecting academic performance.",
    "Recent family relocation may be impacting student's adjustment.",
    "Expressed interest in transferring to advanced mathematics track.",
]

NOTES = [
    "",
    "Student was receptive during initial conversation. Agreed to follow-up session.",
    "Parent contacted and supportive of counseling intervention.",
    "Teacher reports improvement since last session.",
    "Student completed initial assessment questionnaire. Results attached.",
    "",
    "",
    "Student attends regularly and is making good progress.",
    "Recommended consultation with school psychologist for further evaluation.",
    "",
]

INTERVENTION_PLANS = [
    "",
    "Weekly check-in sessions for 4 weeks to monitor progress.",
    "Refer to academic support program for additional tutoring.",
    "Coordinate with classroom teachers to implement accommodations.",
    "Develop anxiety management plan with breathing techniques and breaks.",
    "Schedule parent-teacher-counselor conference to align support strategies.",
    "",
    "Create behavior monitoring chart with daily check-ins.",
    "Connect with college counseling resources and career assessment tools.",
    "Implement peer mentoring program with designated buddy.",
]

OUTCOMES = [
    "",
    "Student showed improvement in class participation. Continuing weekly sessions.",
    "Attendance improved after implementing morning check-in routine.",
    "Test scores improved after additional tutoring support was arranged.",
    "Student reported reduced anxiety using breathing techniques.",
    "Parent conference held successfully. Support plan implemented at home.",
    "",
    "Behavior incidents reduced significantly. Student responding well to monitoring.",
    "Student enrolled in advanced placement program. Ongoing academic monitoring.",
    "",
]


class Command(BaseCommand):
    help = "Seed demo counseling appointments and referrals."

    def add_arguments(self, parser):
        parser.add_argument(
            "--appointments", default=15, type=int,
            help="Number of counseling appointments to create",
        )
        parser.add_argument(
            "--referrals", default=10, type=int,
            help="Number of student referrals to create",
        )
        parser.add_argument(
            "--flush", action="store_true",
            help="Delete existing counseling demo data first",
        )

    def handle(self, *args, **options):
        from services.auth.models import User, UserRole
        from services.students.models import Student
        from services.counseling.models import CounselingAppointment, StudentReferral

        # ── Find or create a counselor ────────────────────────────────────
        school_admin = User.objects.filter(role=UserRole.SCHOOL_ADMIN).first()
        if not school_admin:
            self.stderr.write(self.style.ERROR(
                "No school admin found! Run seed_demo_data first."
            ))
            return
        school = school_admin.school

        teachers = list(User.objects.filter(
            school=school, role=UserRole.TEACHER, is_active=True
        ))
        students = list(Student.objects.filter(
            school=school, is_active=True
        ))

        if not students:
            self.stderr.write(self.style.ERROR(
                "No students found! Run seed_demo_data first."
            ))
            return

        # Create a counselor user if none exists
        counselor = User.objects.filter(school=school, role=UserRole.COUNSELOR).first()
        if not counselor:
            counselor = User.objects.create_user(
                email="counselor@demo.edusphere.school",
                password="Counselor@1234",
                first_name="Sarah",
                last_name="Thompson",
                school=school,
                role=UserRole.COUNSELOR,
                is_active=True,
                email_verified=True,
            )
            self.stdout.write(f"  Created counselor: {counselor.email} / Counselor@1234")

        # ── Flush existing data ───────────────────────────────────────────
        if options["flush"]:
            with transaction.atomic():
                deleted_appts = CounselingAppointment.objects.filter(
                    school=school
                ).delete()[0]
                deleted_refs = StudentReferral.objects.filter(
                    school=school
                ).delete()[0]
            self.stdout.write(
                f"  Flushed {deleted_appts} appointments and "
                f"{deleted_refs} referrals"
            )

        num_appointments = options["appointments"]
        num_referrals = options["referrals"]
        stats = {
            "appointments": 0,
            "completed": 0,
            "cancelled": 0,
            "no_show": 0,
            "referrals": 0,
            "urgent_refs": 0,
            "closed_refs": 0,
        }

        today = date.today()

        # ── Appointment time slots ────────────────────────────────────────
        time_slots = [
            time(8, 0), time(9, 0), time(10, 0), time(11, 0),
            time(13, 0), time(14, 0), time(15, 0), time(16, 0),
        ]
        appointment_types = [
            "academic", "career", "personal", "behavioral",
            "college", "group", "other",
        ]
        locations = [
            "Counseling Office - Room 102", "Virtual Meeting Room",
            "Library Conference Room", "", "Wellness Center",
        ]

        with transaction.atomic():
            # ── Seed Appointments ─────────────────────────────────────────
            for i in range(num_appointments):
                student = random.choice(students)
                # Mix of past and future dates
                if i < num_appointments * 0.4:
                    # Past appointments (completed, cancelled, no-show)
                    days_ago = random.randint(1, 14)
                    sched_date = today - timedelta(days=days_ago)
                    sched_time = random.choice(time_slots)
                    status_choices = ["completed", "completed", "completed",
                                      "cancelled", "no_show"]
                    status = random.choice(status_choices)
                    duration = random.choice([15, 30, 30, 45, 60])
                    notes = random.choice(NOTES)
                    follow_up = random.random() < 0.15
                    follow_up_date = (
                        today + timedelta(days=random.randint(1, 7))
                        if follow_up else None
                    )
                else:
                    # Future appointments (scheduled)
                    days_ahead = random.randint(0, 14)
                    sched_date = today + timedelta(days=days_ahead)
                    sched_time = random.choice(time_slots)
                    status = "scheduled"
                    duration = random.choice([15, 30, 30, 45, 60])
                    notes = ""
                    follow_up = False
                    follow_up_date = None

                CounselingAppointment.objects.create(
                    school=school,
                    counselor=counselor,
                    student=student,
                    appointment_type=random.choice(appointment_types),
                    status=status,
                    scheduled_date=sched_date,
                    scheduled_time=sched_time,
                    duration_minutes=duration,
                    location=random.choice(locations),
                    reason=random.choice(REASONS),
                    notes=notes,
                    follow_up_needed=follow_up,
                    follow_up_date=follow_up_date,
                    created_by=(
                        counselor if status == "scheduled"
                        else random.choice(teachers) if teachers
                        else counselor
                    ),
                )
                stats["appointments"] += 1
                if status == "completed":
                    stats["completed"] += 1
                elif status == "cancelled":
                    stats["cancelled"] += 1
                elif status == "no_show":
                    stats["no_show"] += 1

            # ── Seed Referrals ────────────────────────────────────────────
            referral_categories = [
                "academic", "attendance", "behavior", "emotional",
                "family", "social", "safety", "other",
            ]
            priorities_list = ["low", "medium", "medium", "high", "urgent"]
            status_list = [
                "pending", "pending", "under_review", "contacted",
                "actioned", "actioned", "closed", "declined",
            ]

            for i in range(num_referrals):
                student = random.choice(students)
                referred_by = random.choice(teachers) if teachers else school_admin
                category = random.choice(referral_categories)
                priority = random.choice(priorities_list)
                status = random.choice(status_list)
                is_actioned = status in ("actioned", "closed")
                is_closed = status == "closed"
                is_confidential = random.random() < 0.15

                reason = random.choice(REASONS)

                # Create referral at a past date for realism
                days_ago = random.randint(1, 20)
                action_taken_at = None
                outcome = ""
                intervention_plan = ""

                if is_actioned or is_closed:
                    action_taken_at = timezone.now() - timedelta(
                        days=random.randint(0, days_ago)
                    )
                    intervention_plan = random.choice(INTERVENTION_PLANS)
                    outcome = random.choice(OUTCOMES)

                StudentReferral.objects.create(
                    school=school,
                    student=student,
                    referred_by=referred_by,
                    assigned_to=counselor if random.random() < 0.7 else None,
                    category=category,
                    priority=priority,
                    status=status,
                    reason=reason,
                    notes=random.choice(NOTES[:5]) if random.random() < 0.5 else "",
                    intervention_plan=intervention_plan,
                    outcome=outcome,
                    action_taken_at=action_taken_at,
                    follow_up_date=(
                        today + timedelta(days=random.randint(1, 14))
                        if is_actioned and random.random() < 0.3
                        else None
                    ),
                    is_confidential=is_confidential,
                )
                stats["referrals"] += 1
                if priority == "urgent":
                    stats["urgent_refs"] += 1
                if is_closed:
                    stats["closed_refs"] += 1

        # ── Summary ───────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS("\n✅ Counseling demo data seeded!"))
        self.stdout.write(f"\n  Summary for {school.name}:")
        self.stdout.write(f"    Appointments created: {stats['appointments']}")
        self.stdout.write(f"      ├ Completed:         {stats['completed']}")
        self.stdout.write(f"      ├ Cancelled:         {stats['cancelled']}")
        self.stdout.write(f"      ├ No-show:           {stats['no_show']}")
        self.stdout.write(f"      └ Scheduled:         "
                          f"{stats['appointments'] - stats['completed'] - stats['cancelled'] - stats['no_show']}")
        self.stdout.write(f"    Referrals created:    {stats['referrals']}")
        self.stdout.write(f"      ├ Urgent:            {stats['urgent_refs']}")
        self.stdout.write(f"      └ Closed:            {stats['closed_refs']}")
        self.stdout.write(f"\n  Counselor: {counselor.full_name} "
                          f"<{counselor.email}>")
        self.stdout.write(f"  Students: {len(students)}, Teachers: {len(teachers) if teachers else 0}")
