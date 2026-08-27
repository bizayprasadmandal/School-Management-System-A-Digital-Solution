"""
Management command: seed_teacher_schedules
Creates realistic teacher timetables with ~40 periods per week.
Usage: python manage.py seed_teacher_schedules
"""

import random

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Generate realistic teacher schedules with 40+ periods per week."

    def handle(self, *args, **options):
        from services.academics.models import TeacherAssignment
        from services.auth.models import School
        from services.students.models import AcademicYear, Classroom
        from services.timetable.models import Period, TimetableSlot

        self.stdout.write(self.style.MIGRATE_HEADING("📅 Seeding realistic teacher schedules…"))

        with transaction.atomic():
            # Get current school and academic year
            school = School.objects.filter(name__icontains="demo").first() or School.objects.first()
            if not school:
                self.stdout.write(self.style.ERROR("No school found. Run seed_demo_data first."))
                return

            ay = AcademicYear.objects.filter(school=school, is_current=True).first()
            if not ay:
                self.stdout.write(self.style.ERROR("No current academic year found."))
                return

            # Get periods (excluding breaks)
            periods = list(Period.objects.filter(school=school, is_break=False).order_by("period_number"))
            if not periods:
                self.stdout.write(self.style.ERROR("No periods found. Run seed_demo_data first."))
                return

            # Get classrooms
            classrooms = list(Classroom.objects.filter(school=school, academic_year=ay))
            if not classrooms:
                self.stdout.write(self.style.ERROR("No classrooms found."))
                return

            # Get teacher assignments
            assignments = list(
                TeacherAssignment.objects.filter(classroom__school=school, academic_year=ay).select_related(
                    "teacher", "subject", "classroom"
                )
            )

            if not assignments:
                self.stdout.write(self.style.ERROR("No teacher assignments found."))
                return

            # Group assignments by teacher
            teacher_assignments = {}
            for assignment in assignments:
                teacher_id = assignment.teacher_id
                if teacher_id not in teacher_assignments:
                    teacher_assignments[teacher_id] = []
                teacher_assignments[teacher_id].append(assignment)

            # Delete existing timetable slots for this academic year
            deleted_count, _ = TimetableSlot.objects.filter(classroom__school=school, academic_year=ay).delete()
            self.stdout.write(f"  Cleared {deleted_count} existing timetable slots")

            # Realistic schedule configuration
            # A teacher typically teaches 6-8 periods per day, 5 days = 30-40 periods/week
            DAYS_OF_WEEK = [0, 1, 2, 3, 4]  # Mon-Fri
            slots_created = 0
            teacher_stats = {}

            for teacher_id, teacher_assignments_list in teacher_assignments.items():
                # Each teacher gets a schedule
                # Distribute periods across the week realistically
                teacher_name = teacher_assignments_list[0].teacher.full_name

                # Create a schedule template for this teacher
                # Each day has specific periods assigned to specific classrooms
                daily_schedule = {}

                for day in DAYS_OF_WEEK:
                    # Randomly select which periods this teacher teaches on this day
                    # Ensure we don't exceed available periods
                    num_periods_today = random.randint(5, 8)
                    available_periods = periods.copy()

                    # Select periods for this day
                    selected_periods = random.sample(available_periods, min(num_periods_today, len(available_periods)))

                    daily_schedule[day] = []

                    for period in selected_periods:
                        # Select an assignment for this period
                        # Prefer assignments that haven't been used much
                        if teacher_assignments_list:
                            # Cycle through assignments
                            assignment = teacher_assignments_list[slots_created % len(teacher_assignments_list)]

                            # Check if this slot already exists
                            existing = TimetableSlot.objects.filter(
                                classroom=assignment.classroom, period=period, day_of_week=day, academic_year=ay
                            ).exists()

                            if not existing:
                                _, created = TimetableSlot.objects.get_or_create(
                                    classroom=assignment.classroom,
                                    period=period,
                                    day_of_week=day,
                                    academic_year=ay,
                                    defaults={
                                        "assignment": assignment,
                                        "room": assignment.classroom.room_number or "",
                                        "effective_from": ay.start_date,
                                        "effective_to": ay.end_date,
                                    },
                                )
                                if created:
                                    slots_created += 1
                                    daily_schedule[day].append(period.period_number)

                                    # Track teacher stats
                                    if teacher_name not in teacher_stats:
                                        teacher_stats[teacher_name] = {"total_periods": 0, "daily_breakdown": {}}
                                    teacher_stats[teacher_name]["total_periods"] += 1
                                    if day not in teacher_stats[teacher_name]["daily_breakdown"]:
                                        teacher_stats[teacher_name]["daily_breakdown"][day] = 0
                                    teacher_stats[teacher_name]["daily_breakdown"][day] += 1

            # Print summary
            self.stdout.write(f"\n✅ Created {slots_created} timetable slots")
            self.stdout.write("\n📊 Teacher Schedule Summary:")
            self.stdout.write("-" * 60)

            for teacher_name, stats in sorted(teacher_stats.items()):
                total = stats["total_periods"]
                daily = stats["daily_breakdown"]
                daily_str = ", ".join([f"Day {d}: {c}" for d, c in sorted(daily.items())])
                self.stdout.write(f"  {teacher_name}: {total} periods/week ({daily_str})")

            self.stdout.write(f"\n📈 Total teachers with schedules: {len(teacher_stats)}")
            avg = sum(s["total_periods"] for s in teacher_stats.values()) / len(teacher_stats)
            self.stdout.write(f"📈 Average periods per teacher: {avg:.1f}")
