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

    def add_arguments(self, parser):
        parser.add_argument(
            "--all-schools",
            action="store_true",
            help="Generate schedules for all schools (default: demo school only)",
        )

    def handle(self, *args, **options):
        from services.academics.models import TeacherAssignment
        from services.auth.models import School
        from services.students.models import AcademicYear
        from services.timetable.models import Period, TimetableSlot

        self.stdout.write(self.style.MIGRATE_HEADING("📅 Seeding realistic teacher schedules…"))

        with transaction.atomic():
            # Determine which schools to process
            all_schools = options["all_schools"]
            if all_schools:
                schools = School.objects.all()
                self.stdout.write(f"  Processing ALL {schools.count()} schools")
            else:
                schools = School.objects.filter(name__icontains="demo")
                if not schools.exists():
                    schools = School.objects.all()[:1]
                self.stdout.write(f"  Processing {schools.count()} school(s)")

            if not schools.exists():
                self.stdout.write(self.style.ERROR("No schools found. Run seed_demo_data first."))
                return

            total_slots_all = 0
            all_teacher_stats = {}

            for school in schools:
                self.stdout.write(f"\n🏫 Processing: {school.name}")

                ay = AcademicYear.objects.filter(school=school, is_current=True).first()
                if not ay:
                    self.stdout.write(f"  ⚠️  No current academic year for {school.name}, skipping")
                    continue

                # Get periods (excluding breaks)
                periods = list(Period.objects.filter(school=school, is_break=False).order_by("period_number"))
                if not periods:
                    self.stdout.write(f"  ⚠️  No periods for {school.name}, skipping")
                    continue

                # Get teacher assignments
                assignments = list(
                    TeacherAssignment.objects.filter(classroom__school=school, academic_year=ay).select_related(
                        "teacher", "subject", "classroom"
                    )
                )

                if not assignments:
                    self.stdout.write(f"  ⚠️  No teacher assignments for {school.name}, skipping")
                    continue

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
                DAYS_OF_WEEK = [0, 1, 2, 3, 4]  # Mon-Fri
                slots_created = 0
                teacher_stats = {}

                for teacher_id, teacher_assignments_list in teacher_assignments.items():
                    teacher_name = teacher_assignments_list[0].teacher.full_name
                    daily_schedule = {}

                    for day in DAYS_OF_WEEK:
                        num_periods_today = random.randint(5, 8)
                        available_periods = periods.copy()
                        selected_periods = random.sample(
                            available_periods, min(num_periods_today, len(available_periods))
                        )
                        daily_schedule[day] = []

                        for period in selected_periods:
                            if teacher_assignments_list:
                                assignment = teacher_assignments_list[slots_created % len(teacher_assignments_list)]

                                existing = TimetableSlot.objects.filter(
                                    classroom=assignment.classroom,
                                    period=period,
                                    day_of_week=day,
                                    academic_year=ay,
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

                                        if teacher_name not in teacher_stats:
                                            teacher_stats[teacher_name] = {
                                                "total_periods": 0,
                                                "daily_breakdown": {},
                                            }
                                        teacher_stats[teacher_name]["total_periods"] += 1
                                        if day not in teacher_stats[teacher_name]["daily_breakdown"]:
                                            teacher_stats[teacher_name]["daily_breakdown"][day] = 0
                                        teacher_stats[teacher_name]["daily_breakdown"][day] += 1

                total_slots_all += slots_created
                all_teacher_stats.update(teacher_stats)

                self.stdout.write(f"  ✅ Created {slots_created} timetable slots for {school.name}")
                for tname, stats in sorted(teacher_stats.items()):
                    total = stats["total_periods"]
                    self.stdout.write(f"    📊 {tname}: {total} periods/week")

            # Print final summary
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"✅ TOTAL: Created {total_slots_all} timetable slots across {schools.count()} school(s)")
            if all_teacher_stats:
                avg = sum(s["total_periods"] for s in all_teacher_stats.values()) / len(all_teacher_stats)
                self.stdout.write(f"📈 Average periods per teacher: {avg:.1f}")
