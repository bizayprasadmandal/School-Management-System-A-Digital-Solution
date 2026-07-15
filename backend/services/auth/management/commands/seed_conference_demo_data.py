"""
Management command: seed_conference_demo_data
Creates conference slots with bookings and mock Zoom meeting data
so the full parent-teacher-Zoom flow can be tested end-to-end.

Since Zoom credentials (Account ID / Client ID / Client Secret) are not
configured in demo environments, this command seeds placeholder Zoom data
(meeting IDs, join URLs, passwords) directly on the ConferenceSlot model.
The URLs point to placeholder zoom.us links for demonstration.

Usage: python manage.py seed_conference_demo_data
       python manage.py seed_conference_demo_data --days 7 --slots-per-teacher 3
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta, time
import random


# ─── Mock Zoom data generator ────────────────────────────────────────────────

def _mock_zoom_details(index: int) -> dict:
    """Generate mock Zoom meeting data simulating real Zoom API responses."""
    meeting_id = random.randint(100_000_000, 999_999_999)
    passcode = f"{random.randint(100000, 999999)}"
    return {
        "zoom_meeting_id": str(meeting_id),
        "zoom_join_url": f"https://zoom.us/j/{meeting_id}?pwd={passcode}",
        "zoom_start_url": f"https://zoom.us/s/{meeting_id}?zak=zk_mock_{index}",
        "zoom_password": passcode,
        "is_zoom_created": True,
    }


class Command(BaseCommand):
    help = "Seed conference slots with bookings and mock Zoom meeting data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", default=5, type=int,
            help="Number of future days to create slots for"
        )
        parser.add_argument(
            "--slots-per-teacher", default=3, type=int,
            help="Number of time slots per teacher per day"
        )

    def handle(self, *args, **options):
        from services.auth.models import User, UserRole
        from services.students.models import Student
        from services.conferences.models import ConferenceSlot

        school = User.objects.filter(role=UserRole.SCHOOL_ADMIN).first()
        if not school:
            self.stderr.write(self.style.ERROR(
                "No school admin found! Run seed_demo_data first."
            ))
            return
        school = school.school

        teachers = list(User.objects.filter(
            school=school, role=UserRole.TEACHER, is_active=True
        ))
        if not teachers:
            self.stderr.write(self.style.ERROR("No teachers found!"))
            return

        students = list(Student.objects.filter(
            school=school, is_active=True
        ))
        if not students:
            self.stderr.write(self.style.ERROR("No students found!"))
            return

        num_days = options["days"]
        slots_per_teacher = options["slots_per_teacher"]
        today = date.today()
        stats = {"created": 0, "booked": 0, "zoomed": 0}

        time_slots = [
            (time(8, 0), time(8, 30)),
            (time(9, 0), time(9, 30)),
            (time(10, 0), time(10, 30)),
            (time(11, 0), time(11, 30)),
            (time(13, 0), time(13, 30)),
            (time(14, 0), time(14, 30)),
            (time(15, 0), time(15, 30)),
        ]

        with transaction.atomic():
            for day_offset in range(num_days):
                slot_date = today + timedelta(days=day_offset)
                # Skip weekends
                if slot_date.weekday() >= 5:
                    continue

                for teacher in teachers:
                    # Pick random time slots for this teacher
                    chosen_slots = random.sample(
                        time_slots,
                        min(slots_per_teacher, len(time_slots))
                    )
                    for start_time, end_time in chosen_slots:
                        # 40% chance this slot is booked
                        is_booked = random.random() < 0.40
                        student = None
                        booked_by = None
                        zoom_data = {}

                        if is_booked:
                            student = random.choice(students)
                            booked_by = teacher
                            # 60% of booked slots get a mock Zoom meeting
                            if random.random() < 0.60:
                                zoom_data = _mock_zoom_details(stats["created"])

                        slot, created = ConferenceSlot.objects.get_or_create(
                            school=school,
                            teacher=teacher,
                            date=slot_date,
                            start_time=start_time,
                            end_time=end_time,
                            defaults={
                                "student": student,
                                "is_booked": is_booked,
                                "booked_by": booked_by,
                                "notes": random.choice([
                                    "",
                                    "Discuss academic progress",
                                    "Review recent test scores",
                                    "Behavioral discussion",
                                    "Career guidance talk",
                                    "Homework improvement plan",
                                ]),
                                **zoom_data,
                            },
                        )

                        if created:
                            stats["created"] += 1
                            if is_booked:
                                stats["booked"] += 1
                                if zoom_data:
                                    stats["zoomed"] += 1

        # ── Summary ────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS("\n✅ Conference demo data seeded!"))
        self.stdout.write(f"\n  Summary for {school.name}:")
        self.stdout.write(f"    Total slots created:  {stats['created']}")
        self.stdout.write(f"    Booked slots:         {stats['booked']}")
        self.stdout.write(f"    With Zoom meetings:   {stats['zoomed']}")
        self.stdout.write(f"    Available slots:      {stats['created'] - stats['booked']}")
        self.stdout.write(f"\n  Teachers: {len(teachers)}, Students: {len(students)}")
        self.stdout.write(f"  Date range: {today} → {today + timedelta(days=num_days - 1)}")
        self.stdout.write("\n  Mock Zoom data was seeded for demonstration.")
        self.stdout.write("  Replace ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, and ZOOM_CLIENT_SECRET")
        self.stdout.write("  in your .env to create real Zoom meetings via the API.")
