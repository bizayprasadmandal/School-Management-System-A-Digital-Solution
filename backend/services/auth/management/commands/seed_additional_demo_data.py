"""
Management command: seed_additional_demo_data
Adds realistic attendance records, exam grades, fee invoices, and payments
to the existing demo school data.

Run this AFTER seed_demo_data has been executed at least once.

Usage: python manage.py seed_additional_demo_data
       python manage.py seed_additional_demo_data --days 45
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta, time
from decimal import Decimal
import random


# ─── Helpers ─────────────────────────────────────────────────────────────────

def weighted_choice(choices: list[tuple[str, float]]) -> str:
    """Pick from choices with weighted probabilities (must sum to 1.0)."""
    r = random.random()
    cumulative = 0.0
    for value, weight in choices:
        cumulative += weight
        if r <= cumulative:
            return value
    return choices[-1][0]


# ─── Command ─────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Seed additional demo data: attendance, grades, invoices, payments, timetable, messages, events."

    def add_arguments(self, parser):
        parser.add_argument("--days", default=30, type=int,
                            help="Number of school days of attendance to generate")
        parser.add_argument("--messages", default=500, type=int,
                            help="Number of direct messages to generate")

    def handle(self, *args, **options):
        # Lazy imports so the command can be copied/versioned cleanly
        from services.auth.models import User, UserRole
        from services.students.models import AcademicYear, Student, Classroom, Enrollment
        from services.academics.models import Subject, TeacherAssignment
        from services.attendance.models import AttendanceRecord
        from services.gradebook.models import (
            GradingScale, GradingScaleEntry, ExamType,
            Exam, ExamSchedule, Grade, ReportCard,
        )
        from services.fees.models import FeeCategory, FeeStructure, FeeInvoice, Payment
        from services.timetable.models import Period, TimetableSlot, SchoolEvent
        from services.academics.models import LessonPlan
        from services.communication.models import Announcement, DirectMessage

        # ── Resolve objects ────────────────────────────────────────────────
        school = User.objects.filter(role=UserRole.SCHOOL_ADMIN).first()
        if not school:
            self.stderr.write(self.style.ERROR(
                "No school admin found! Run seed_demo_data first."
            ))
            return
        school = school.school

        ay = AcademicYear.objects.filter(school=school, is_current=True).first()
        if not ay:
            self.stderr.write(self.style.ERROR("No current academic year found!"))
            return

        admin_user = User.objects.filter(school=school, role=UserRole.SCHOOL_ADMIN).first()
        teachers = list(User.objects.filter(school=school, role=UserRole.TEACHER))
        students_qs = Student.objects.filter(school=school, is_active=True)

        total = students_qs.count()
        if total == 0:
            self.stderr.write(self.style.ERROR("No students found! Run seed_demo_data first."))
            return

        self.stdout.write(f"Found {total} students, {len(teachers)} teachers, school: {school.name}")

        today = date.today()
        num_days = options["days"]

        # Track created counts for summary
        stats = {
            "assignments": 0, "exam_types": 0, "scale_entries": 0,
            "exams": 0, "schedules": 0, "grades": 0,
            "attendance": 0, "invoices": 0, "payments": 0, "report_cards": 0,
            "timetable_slots": 0, "lesson_plans": 0, "messages": 0,
            "events": 0, "announcements": 0,
        }

        # ── Seed within a single transaction for speed ──────────────────────
        with transaction.atomic():
            # ── 1. TeacherAssignments ───────────────────────────────────────
            self.stdout.write("  Seeding teacher assignments…")
            classrooms = list(Classroom.objects.filter(school=school, academic_year=ay))
            for cls in classrooms:
                subjects = list(Subject.objects.filter(school=school, grade=cls.grade))
                for idx, subject in enumerate(subjects):
                    teacher = teachers[idx % len(teachers)]
                    _, created = TeacherAssignment.objects.get_or_create(
                        teacher=teacher, subject=subject,
                        classroom=cls, academic_year=ay,
                        defaults={"is_primary": True},
                    )
                    if created:
                        stats["assignments"] += 1

            # ── 2. Grading Scale ────────────────────────────────────────────
            self.stdout.write("  Seeding grading scale…")
            scale, _ = GradingScale.objects.get_or_create(
                school=school, name="Standard (A-F)",
                defaults={"is_default": True},
            )
            grade_entries = [
                ("A+", 90, 100, 4.0, "Excellent"),
                ("A",  80, 89.99, 3.7, "Very Good"),
                ("B+", 75, 79.99, 3.3, "Good"),
                ("B",  70, 74.99, 3.0, "Above Average"),
                ("C",  60, 69.99, 2.5, "Average"),
                ("D",  50, 59.99, 2.0, "Below Average"),
                ("E",  40, 49.99, 1.5, "Poor"),
                ("F",   0, 39.99, 0.0, "Fail"),
            ]
            for letter, min_pct, max_pct, gpa, desc in grade_entries:
                _, created = GradingScaleEntry.objects.get_or_create(
                    scale=scale, grade_letter=letter,
                    defaults={
                        "min_percentage": Decimal(str(min_pct)),
                        "max_percentage": Decimal(str(max_pct)),
                        "grade_point": Decimal(str(gpa)),
                        "description": desc,
                    },
                )
                if created:
                    stats["scale_entries"] += 1

            # ── 3. Exam Types ───────────────────────────────────────────────
            self.stdout.write("  Seeding exam types…")
            exam_types_data = [
                ("Midterm Exam", Decimal("40.00"), True),
                ("Final Exam",   Decimal("60.00"), True),
                ("Quiz",         Decimal("10.00"), False),
            ]
            exam_types = {}
            for name, weightage, terminal in exam_types_data:
                et, created = ExamType.objects.get_or_create(
                    school=school, name=name,
                    defaults={"weightage": weightage, "is_terminal": terminal},
                )
                if created:
                    stats["exam_types"] += 1
                exam_types[name] = et

            # ── 4. Exams ───────────────────────────────────────────────────
            self.stdout.write("  Seeding exams…")
            schedule_dates = [
                (date(2024, 10, 28), date(2024, 11, 1),  "Term 1 Midterm Exams"),
                (date(2024, 12, 9),  date(2024, 12, 13), "Term 1 Final Exams"),
                (date(2025, 3, 3),   date(2025, 3, 7),   "Term 2 Midterm Exams"),
            ]
            all_exams = []
            subjects_list = list(Subject.objects.filter(school=school))
            for start_dt, end_dt, exam_name in schedule_dates:
                et = exam_types["Midterm Exam"] if "Midterm" in exam_name else exam_types["Final Exam"]
                exam, created = Exam.objects.get_or_create(
                    school=school, name=exam_name, academic_year=ay, exam_type=et,
                    defaults={
                        "description": f"{exam_name} for the {ay.name} academic year",
                        "start_date": start_dt, "end_date": end_dt,
                        "status": "completed", "created_by": admin_user,
                    },
                )
                if created:
                    stats["exams"] += 1
                    # Create schedules per classroom/subject
                    for cls in classrooms:
                        grade_subjects = [s for s in subjects_list if s.grade_id == cls.grade_id]
                        for subj in grade_subjects:
                            exam_day = start_dt + timedelta(days=random.randint(0, 4))
                            sched, sched_created = ExamSchedule.objects.get_or_create(
                                exam=exam, subject=subj, classroom=cls,
                                defaults={
                                    "date": exam_day,
                                    "start_time": time(9, 0),
                                    "end_time": time(11, 0),
                                    "venue": cls.room_number or "Hall A",
                                    "invigilator": random.choice(teachers) if teachers else None,
                                    "max_marks": Decimal("100"),
                                    "passing_marks": Decimal("40"),
                                },
                            )
                            if sched_created:
                                stats["schedules"] += 1
                    all_exams.append(exam)
                else:
                    all_exams.append(exam)

            # ── 5. Grade Records ────────────────────────────────────────────
            self.stdout.write("  Seeding exam grades for all students…")
            schedules = list(ExamSchedule.objects.filter(exam__school=school))
            for student in students_qs.iterator():
                enrollment = Enrollment.objects.filter(
                    student=student, academic_year=ay
                ).first()
                if not enrollment:
                    continue
                for sched in schedules:
                    if sched.classroom.grade_id != enrollment.classroom.grade_id:
                        continue
                    # 90% chance student was present, 10% absent
                    is_absent = random.random() < 0.08
                    marks = None
                    if not is_absent:
                        # Bell-curve-ish distribution centered at 72
                        mu, sigma = 72, 16
                        marks = max(0, min(100, round(random.gauss(mu, sigma), 1)))
                    _, created = Grade.objects.get_or_create(
                        student=student, exam_schedule=sched,
                        defaults={
                            "marks_obtained": Decimal(str(marks)) if marks is not None else None,
                            "is_absent": is_absent,
                            "remarks": "Absent" if is_absent else "",
                            "graded_by": random.choice(teachers) if teachers else None,
                        },
                    )
                    if created:
                        stats["grades"] += 1

            # ── 6. Report Cards ────────────────────────────────────────────
            self.stdout.write("  Generating report cards…")
            for student in students_qs.iterator():
                enrollment = Enrollment.objects.filter(
                    student=student, academic_year=ay
                ).first()
                if not enrollment:
                    continue
                for exam in all_exams:
                    grade_qs = Grade.objects.filter(
                        student=student, exam_schedule__exam=exam
                    )
                    total = sum(
                        (g.marks_obtained or 0) for g in grade_qs
                    )
                    max_possible = sum(
                        g.exam_schedule.max_marks for g in grade_qs
                    )
                    if max_possible == 0:
                        continue
                    pct = round((total / max_possible) * 100, 2)

                    # Determine grade letter
                    g_letter = "F"
                    for entry in grade_entries:
                        if entry[1] <= pct <= entry[2]:
                            g_letter = entry[0]
                            break

                    att_pct = None
                    att_count = AttendanceRecord.objects.filter(
                        student=student, academic_year=ay
                    ).count()
                    if att_count > 0:
                        present_count = AttendanceRecord.objects.filter(
                            student=student, academic_year=ay,
                            status__in=["P", "L"]
                        ).count()
                        att_pct = round((present_count / att_count) * 100, 2)

                    remarks_pool = [
                        "Good effort, keep it up!",
                        "Shows improvement, needs to focus more.",
                        "Excellent performance this term.",
                        "Needs to work on numerical concepts.",
                        "A pleasure to teach. Well done!",
                        "Has potential but must submit work on time.",
                        "Consistent performer. Well done!",
                        "Needs encouragement in group activities.",
                    ]

                    _, created = ReportCard.objects.get_or_create(
                        student=student, exam=exam, academic_year=ay,
                        defaults={
                            "total_marks": max_possible,
                            "obtained_marks": total,
                            "percentage": Decimal(str(pct)),
                            "grade_letter": g_letter,
                            "status": "published" if random.random() < 0.7 else "draft",
                            "teacher_remarks": random.choice(remarks_pool),
                            "attendance_percentage": Decimal(str(att_pct)) if att_pct else None,
                            "published_at": exam.end_date + timedelta(days=14),
                        },
                    )
                    if created:
                        stats["report_cards"] += 1

            # ── 7. Attendance Records ───────────────────────────────────────
            self.stdout.write(f"  Seeding {num_days} days of attendance records…")
            # Generate weekdays only (Mon-Fri), skipping weekends and random holidays
            attendance_dates = []
            cursor = today - timedelta(days=num_days * 2)  # buffer to find enough weekdays
            while len(attendance_dates) < num_days:
                if cursor.weekday() < 5:  # Mon=0, Fri=4
                    # ~5% chance of being a holiday (no attendance taken)
                    if random.random() > 0.05:
                        attendance_dates.append(cursor)
                cursor += timedelta(days=1)

            for student in students_qs.iterator():
                enrollment = Enrollment.objects.filter(
                    student=student, academic_year=ay
                ).first()
                if not enrollment:
                    continue
                for adate in attendance_dates:
                    # Weighted attendance distribution
                    status = weighted_choice([
                        ("P", 0.75),  # 75% present
                        ("A", 0.08),  # 8% absent
                        ("L", 0.10),  # 10% late
                        ("E", 0.05),  # 5% excused
                        ("H", 0.02),  # 2% half-day
                    ])
                    remarks = ""
                    if status == "L":
                        remarks = f"Arrived {random.randint(5, 30)} min late"
                    elif status == "A":
                        if random.random() < 0.3:
                            remarks = random.choice([
                                "Called in sick", "Family emergency",
                                "Medical appointment", "Traveling",
                            ])
                    elif status == "E":
                        remarks = "Prior intimation given"

                    _, created = AttendanceRecord.objects.get_or_create(
                        student=student, date=adate,
                        defaults={
                            "classroom": enrollment.classroom,
                            "academic_year": ay,
                            "status": status,
                            "recorded_by": random.choice(teachers) if teachers else None,
                            "remarks": remarks,
                            "notified_guardian": status in ("A", "L", "E"),
                        },
                    )
                    if created:
                        stats["attendance"] += 1

            # ── 8. Fee Invoices & Payments ─────────────────────────────────
            self.stdout.write("  Seeding fee invoices and payments…")
            fee_structures = list(FeeStructure.objects.filter(
                school=school, academic_year=ay, is_active=True
            ))
            months = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]

            for student in students_qs.iterator():
                enrollment = Enrollment.objects.filter(
                    student=student, academic_year=ay
                ).first()
                if not enrollment:
                    continue

                for month_idx, month_name in enumerate(months):
                    for fs in fee_structures:
                        if fs.grade_id != enrollment.classroom.grade_id:
                            continue

                        inv_month = 9 + month_idx  # Sep = 9
                        inv_year = 2024 if inv_month <= 12 else 2025
                        inv_month_adj = inv_month if inv_month <= 12 else inv_month - 12
                        due_dt = date(inv_year, inv_month_adj, fs.due_day)
                        inv_num = f"INV-{student.admission_number}-{month_name[:3]}-{fs.fee_category.name[:3].upper()}"

                        late = Decimal("0")
                        if due_dt < today:
                            days_overdue = (today - due_dt).days
                            late = min(fs.late_fee_per_day * days_overdue, Decimal("50"))

                        total_amt = fs.amount + late
                        # ~60% paid in full, 15% partial, 25% unpaid
                        pay_status = weighted_choice([
                            ("paid", 0.60),
                            ("partial", 0.15),
                            ("unpaid", 0.25),
                        ])

                        inv, inv_created = FeeInvoice.objects.get_or_create(
                            invoice_number=inv_num,
                            defaults={
                                "student": student,
                                "academic_year": ay,
                                "fee_structure": fs,
                                "due_date": due_dt,
                                "base_amount": fs.amount,
                                "late_fee": late,
                                "total_amount": total_amt,
                                "paid_amount": total_amt if pay_status == "paid"
                                              else (total_amt * Decimal("0.5")).quantize(Decimal("0.01"))
                                              if pay_status == "partial"
                                              else Decimal("0"),
                                "status": {"paid": "paid", "partial": "partial", "unpaid": "unpaid"}[pay_status],
                                "created_by": admin_user,
                            },
                        )
                        if inv_created:
                            stats["invoices"] += 1

                            # Create payment record for paid/partial
                            if pay_status in ("paid", "partial"):
                                pay_amt = inv.paid_amount
                                pay_method = random.choice(["cash", "bank_transfer", "card", "online"])
                                receipt_num = f"RCT-{student.admission_number}-{month_name[:3]}-{random.randint(1000, 9999)}"

                                Payment.objects.create(
                                    invoice=inv,
                                    amount=pay_amt,
                                    payment_method=pay_method,
                                    status="successful",
                                    receipt_number=receipt_num,
                                    paid_at=due_dt - timedelta(days=random.randint(0, 5)),
                                    collected_by=admin_user,
                                    notes=f"Payment for {month_name} {fs.fee_category.name}",
                                )
                                stats["payments"] += 1

            # ── 9. Timetable Slots ───────────────────────────────────────────
            self.stdout.write("  Seeding timetable slots…")
            periods = list(Period.objects.filter(school=school, is_break=False))
            days_of_week = [0, 1, 2, 3, 4]  # Mon–Fri
            for cls in classrooms:
                assignments = list(TeacherAssignment.objects.filter(
                    classroom=cls, academic_year=ay
                ))
                if not assignments:
                    continue
                for day in days_of_week:
                    for period in periods:
                        # Assign subjects to periods, cycling through the assignments
                        assignment = assignments[day % len(assignments)]
                        _, created = TimetableSlot.objects.get_or_create(
                            classroom=cls, period=period,
                            day_of_week=day, academic_year=ay,
                            defaults={
                                "assignment": assignment,
                                "room": cls.room_number or "",
                                "effective_from": ay.start_date,
                                "effective_to": ay.end_date,
                            },
                        )
                        if created:
                            stats["timetable_slots"] += 1
                        # Move to next assignment for the next period
                        assignments = assignments[1:] + [assignments[0]]

            # ── 10. Lesson Plans ──────────────────────────────────────────────
            self.stdout.write("  Seeding lesson plans…")
            lesson_topics = [
                ("Introduction to Algebra", "Understanding variables and expressions"),
                ("Parts of Speech", "Nouns, verbs, adjectives, and adverbs"),
                ("Solar System", "Planets, orbits, and the Sun"),
                ("World Geography", "Continents, oceans, and climate zones"),
                ("Programming Basics", "Loops, conditions, and functions"),
                ("Chemical Reactions", "Balancing equations and states of matter"),
                ("Ancient Civilizations", "Egypt, Greece, and Rome"),
                ("Data Analysis", "Mean, median, mode, and graphs"),
                ("Essay Writing", "Structure, arguments, and citations"),
                ("Photosynthesis", "Plant biology and energy conversion"),
            ]
            all_assignments = list(TeacherAssignment.objects.filter(academic_year=ay))
            for idx, assignment in enumerate(all_assignments):
                topic, objectives = lesson_topics[idx % len(lesson_topics)]
                # Create 2 lesson plans per assignment
                for week in range(2):
                    lesson_date = ay.start_date + timedelta(weeks=week + idx)
                    if lesson_date > ay.end_date:
                        lesson_date = ay.end_date - timedelta(days=7)
                    _, created = LessonPlan.objects.get_or_create(
                        assignment=assignment, title=topic,
                        date=lesson_date, duration_minutes=45,
                        defaults={
                            "topic": topic,
                            "objectives": objectives,
                            "content": f"Detailed lesson content for {topic}. "
                                       f"Covers key concepts with practical examples "
                                       f"and student activities.",
                            "resources": "Textbook, worksheet, presentation slides",
                            "status": random.choice(["draft", "approved", "completed"]),
                        },
                    )
                    if created:
                        stats["lesson_plans"] += 1

            # ── 11. Direct Messages ───────────────────────────────────────────
            self.stdout.write(f"  Seeding {options['messages']} direct messages…")
            message_templates = [
                "Good morning! Just checking in about {student}'s progress in {subject}.",
                "Could you please send the homework assignment for today?",
                "{student} will be absent tomorrow due to a medical appointment.",
                "Thank you for the extra help after class yesterday. It made a big difference!",
                "The fee payment for this month has been processed. Please confirm receipt.",
                "Reminder: Parent-Teacher meeting is scheduled for next Thursday at 4 PM.",
                "{student} has shown great improvement in {subject} this week!",
                "Could you please share the report card for {student}?",
                "The sports day has been rescheduled to next Friday.",
                "Thank you for your prompt response to my previous message.",
                "{student} forgot their lunch box today. Can someone help?",
                "Great news — {student} scored top marks in the recent {subject} test!",
                "Would you like to schedule a meeting to discuss {student}'s performance?",
                "The school will be closed on Monday for a public holiday.",
                "Please ensure {student} brings the completed permission slip by Friday.",
            ]
            subjects_list = list(Subject.objects.filter(school=school))
            student_users = list(User.objects.filter(
                school=school, role=UserRole.STUDENT, is_active=True
            ))
            parent_users = list(User.objects.filter(
                school=school, role=UserRole.PARENT, is_active=True
            ))

            # Teacher <-> Parent conversations
            for i in range(min(options["messages"], len(teachers) * len(parent_users) * 2)):
                teacher = teachers[i % len(teachers)]
                parent = parent_users[i % len(parent_users)]
                student_user = student_users[i % len(student_users)]
                subject_name = subjects_list[i % len(subjects_list)].name
                tmpl = message_templates[i % len(message_templates)]
                content = tmpl.format(
                    student=student_user.first_name,
                    subject=subject_name,
                )

                # Teacher sends to parent
                _, created = DirectMessage.objects.get_or_create(
                    sender=teacher, recipient=parent, content=content,
                    defaults={
                        "status": random.choice(["sent", "delivered", "read"]),
                        "sent_at": ay.start_date + timedelta(days=random.randint(1, 120)),
                        "read_at": None,
                    },
                )
                if created:
                    stats["messages"] += 1

                # Parent replies (50% chance)
                if random.random() < 0.5:
                    reply_content = random.choice([
                        "Thank you for the update!",
                        "I'll look into this right away.",
                        "Noted. Thanks for letting me know.",
                        "Can we discuss this further in the next PTM?",
                        "I appreciate your concern. Will take necessary action.",
                        "Got it, thanks!",
                    ])
                    _, created = DirectMessage.objects.get_or_create(
                        sender=parent, recipient=teacher, content=reply_content,
                        defaults={
                            "status": random.choice(["sent", "delivered", "read"]),
                            "sent_at": ay.start_date + timedelta(days=random.randint(1, 120)),
                        },
                    )
                    if created:
                        stats["messages"] += 1

            # ── 12. School Events ─────────────────────────────────────────────
            self.stdout.write("  Seeding school events…")
            events_data = [
                ("Independence Day Celebration", "school-wide celebration with cultural programs",
                 "cultural", date(2024, 8, 15), date(2024, 8, 15), True),
                ("Annual Sports Day", "Inter-house sports competitions and awards ceremony",
                 "sports", date(2024, 11, 20), date(2024, 11, 22), True),
                ("Parent-Teacher Meeting — Term 1", "Discuss student progress and report cards",
                 "ptm", date(2024, 12, 20), date(2024, 12, 20), True),
                ("Winter Break", "School closed for winter holidays",
                 "holiday", date(2024, 12, 23), date(2025, 1, 5), True),
                ("Science Fair", "Students showcase science projects and experiments",
                 "cultural", date(2025, 2, 10), date(2025, 2, 11), True),
                ("Field Trip — Science Museum", "Grade 5-6 educational visit to the National Science Museum",
                 "trip", date(2025, 3, 15), date(2025, 3, 15), False),
                ("Annual Day & Awards Ceremony", "Year-end celebration with prizes and performances",
                 "cultural", date(2025, 4, 10), date(2025, 4, 10), True),
                ("Spring Break", "School closed for spring holidays",
                 "holiday", date(2025, 4, 14), date(2025, 4, 20), True),
                ("Parent-Teacher Meeting — Term 2", "End-of-year progress discussion",
                 "ptm", date(2025, 5, 15), date(2025, 5, 15), True),
                ("Graduation Ceremony", "Farewell and graduation for Grade 6 students",
                 "cultural", date(2025, 6, 10), date(2025, 6, 10), True),
            ]
            for title, desc, etype, start_dt, end_dt, school_wide in events_data:
                _, created = SchoolEvent.objects.get_or_create(
                    school=school, title=title, start_date=start_dt,
                    defaults={
                        "description": desc,
                        "event_type": etype,
                        "end_date": end_dt,
                        "is_school_wide": school_wide,
                        "created_by": admin_user,
                    },
                )
                if created:
                    stats["events"] += 1

            # ── 13. Additional Announcements ──────────────────────────────────
            self.stdout.write("  Seeding additional announcements…")
            announcements_data = [
                ("Exam Schedule Released",
                 "The Term 1 final examination schedule has been published. Please check the timetable page for details.",
                 "high", "all"),
                ("Library Timings Extended",
                 "The school library will remain open until 5 PM during exam season.",
                 "normal", "students"),
                ("Staff Meeting Reminder",
                 "All staff members are requested to attend the monthly meeting on Friday at 3 PM in the conference hall.",
                 "normal", "staff"),
                ("Uniform Policy Update",
                 "Please note that winter uniforms are now mandatory. Students must wear blazers and sweaters.",
                 "normal", "students"),
                ("Emergency Drill Scheduled",
                 "A fire safety drill will be conducted on Wednesday at 10 AM. All students and staff must participate.",
                 "urgent", "all"),
                ("Sports Tryouts Open",
                 "Tryouts for the school basketball and football teams will be held next week. Interested students should sign up at the sports office.",
                 "normal", "students"),
                ("Fee Payment Deadline Extended",
                 "The deadline for Term 2 fee payment has been extended to January 20th. Late fee will apply after this date.",
                 "high", "parents"),
                ("New Computer Lab Inauguration",
                 "The new state-of-the-art computer lab will be inaugurated on February 5th. We invite all parents to the ceremony.",
                 "low", "all"),
            ]
            from services.communication.models import Announcement
            for title, content, priority, audience in announcements_data:
                _, created = Announcement.objects.get_or_create(
                    school=school, title=title,
                    defaults={
                        "content": content,
                        "priority": priority,
                        "audience": audience,
                        "is_draft": False,
                        "published_at": ay.start_date + timedelta(days=random.randint(1, 150)),
                        "created_by": admin_user,
                        "send_push": True,
                        "view_count": random.randint(50, 500),
                    },
                )
                if created:
                    stats["announcements"] += 1

        # ── Summary ────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS("\n✅ Additional demo data seeded!"))
        self.stdout.write("\n  Summary:")
        for key, label in [
            ("assignments", "Teacher assignments"),
            ("exam_types", "Exam types"),
            ("scale_entries", "Grading scale entries"),
            ("exams", "Exams"),
            ("schedules", "Exam schedules"),
            ("grades", "Student grades"),
            ("attendance", "Attendance records"),
            ("invoices", "Fee invoices"),
            ("payments", "Payment records"),
            ("report_cards", "Report cards"),
            ("timetable_slots", "Timetable slots"),
            ("lesson_plans", "Lesson plans"),
            ("messages", "Direct messages"),
            ("events", "School events"),
            ("announcements", "Announcements"),
        ]:
            self.stdout.write(f"    {label}: {'✅' if stats[key] > 0 else '⚪'} {stats[key]} created")
