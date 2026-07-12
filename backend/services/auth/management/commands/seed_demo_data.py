"""
Management command: seed_demo_data
Creates a complete demo school with realistic data for showcasing the system.
Usage: python manage.py seed_demo_data [--school-name "Demo Academy"]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = "Seed a demo school with realistic students, teachers, and academic data."

    def add_arguments(self, parser):
        parser.add_argument("--school-name", default="EduSphere Demo Academy", type=str)
        parser.add_argument("--students", default=120, type=int, help="Number of students to create")
        parser.add_argument("--flush", action="store_true", help="Delete existing demo data first")

    def handle(self, *args, **options):
        from services.auth.models import School, User, UserRole
        from services.students.models import (
            AcademicYear, Grade, Classroom, Student, Guardian,
            StudentGuardian, Enrollment,
        )
        from services.academics.models import Subject, TeacherProfile, TeacherAssignment
        from services.fees.models import FeeCategory, FeeStructure
        from services.timetable.models import Period, SchoolEvent
        from services.communication.models import Announcement, NotificationTemplate

        self.stdout.write(self.style.MIGRATE_HEADING("🎓 Seeding demo school data…"))

        with transaction.atomic():
            # ── School ──────────────────────────────────────────────────────
            school, created = School.objects.get_or_create(
                subdomain="demo",
                defaults={
                    "name": options["school_name"],
                    "code": "DEMO",
                    "address": "1 Education Boulevard, Knowledge City",
                    "phone": "+1-555-SCHOOL",
                    "email": "admin@demo.edusphere.school",
                    "website": "https://demo.edusphere.school",
                    "timezone": "UTC",
                    "subscription_tier": "premium",
                },
            )
            status = "created" if created else "already exists"
            self.stdout.write(f"  School: {school.name} ({status})")

            # ── Academic Year ────────────────────────────────────────────────
            ay, _ = AcademicYear.objects.get_or_create(
                school=school, name="2024-2025",
                defaults={"start_date": date(2024, 9, 1), "end_date": date(2025, 6, 30), "is_current": True},
            )

            # ── Admin User ────────────────────────────────────────────────────
            admin, _ = User.objects.get_or_create(
                email="admin@demo.edusphere.school",
                defaults={
                    "first_name": "Alex", "last_name": "Administrator",
                    "role": UserRole.SCHOOL_ADMIN, "school": school, "is_active": True, "is_staff": True,
                },
            )
            if _:
                admin.set_password("Admin@1234")
                admin.save()
                self.stdout.write("  Admin: admin@demo.edusphere.school / Admin@1234")

            # ── Grades ─────────────────────────────────────────────────────────
            grade_data = [
                (1, "Grade 1"), (2, "Grade 2"), (3, "Grade 3"),
                (4, "Grade 4"), (5, "Grade 5"), (6, "Grade 6"),
                (7, "Grade 7"), (8, "Grade 8"), (9, "Grade 9"),
                (10, "Grade 10"), (11, "Grade 11"), (12, "Grade 12"),
            ]
            grades = {}
            for level, name in grade_data:
                g, _ = Grade.objects.get_or_create(school=school, level=level, defaults={"name": name})
                grades[level] = g

            # ── Subjects ───────────────────────────────────────────────────────
            core_subjects = ["Mathematics", "English", "Science", "Social Studies", "Computer Science"]
            elective_subjects = ["Art", "Music", "Physical Education"]
            all_subjects = {}
            for grade_level, grade_obj in list(grades.items())[:6]:  # Grades 1-6
                all_subjects[grade_level] = []
                for idx, sname in enumerate(core_subjects):
                    s, _ = Subject.objects.get_or_create(
                        school=school, grade=grade_obj,
                        code=f"{sname[:3].upper()}{grade_level:02d}",
                        defaults={"name": sname, "is_core": True, "max_marks": 100, "pass_marks": 40},
                    )
                    all_subjects[grade_level].append(s)

            # ── Teachers ────────────────────────────────────────────────────────
            teacher_names = [
                ("Sarah", "Mitchell"), ("James", "Thompson"), ("Emily", "Chen"),
                ("Robert", "Johnson"), ("Maria", "Garcia"), ("David", "Williams"),
                ("Lisa", "Anderson"), ("Michael", "Brown"),
            ]
            teachers = []
            for idx, (fname, lname) in enumerate(teacher_names):
                email = f"{fname.lower()}.{lname.lower()}@demo.edusphere.school"
                u, created_u = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "first_name": fname, "last_name": lname,
                        "role": UserRole.TEACHER, "school": school, "is_active": True,
                    },
                )
                if created_u:
                    u.set_password("Teacher@1234")
                    u.save()
                tp, _ = TeacherProfile.objects.get_or_create(
                    user=u, school=school,
                    defaults={
                        "employee_id": f"EMP{idx+1:04d}",
                        "gender": "F" if idx % 2 == 0 else "M",
                        "qualification": "master",
                        "specialization": core_subjects[idx % len(core_subjects)],
                        "joining_date": date(2020, 8, 1),
                        "experience_years": 4 + idx,
                        "department": "Academic",
                        "address": "456 Teacher Lane",
                    },
                )
                teachers.append(u)
            self.stdout.write(f"  Teachers: {len(teachers)} created/found (password: Teacher@1234)")

            # ── Classrooms ─────────────────────────────────────────────────────
            classrooms = {}
            for grade_level in range(1, 7):
                for section in ["A", "B"]:
                    teacher = teachers[(grade_level * 2 + ord(section) - ord("A")) % len(teachers)]
                    cls, _ = Classroom.objects.get_or_create(
                        school=school, grade=grades[grade_level],
                        name=f"{grade_level}{section}", academic_year=ay,
                        defaults={"capacity": 35, "class_teacher": teacher, "room_number": f"R{grade_level}{section}"},
                    )
                    classrooms[f"{grade_level}{section}"] = cls

            # ── Students & Guardians ────────────────────────────────────────────
            first_names = ["Aiden","Emma","Liam","Olivia","Noah","Ava","William","Sophia","James","Isabella",
                           "Oliver","Mia","Benjamin","Charlotte","Elijah","Amelia","Lucas","Harper","Mason","Evelyn"]
            last_names = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Taylor"]

            student_count = 0
            cls_keys = list(classrooms.keys())
            for i in range(options["students"]):
                fname = first_names[i % len(first_names)]
                lname = last_names[i % len(last_names)]
                email = f"student{i+1:03d}@demo.edusphere.school"
                su, created_u = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "first_name": fname, "last_name": lname,
                        "role": UserRole.STUDENT, "school": school, "is_active": True,
                    },
                )
                if created_u:
                    su.set_password("Student@1234")
                    su.save()

                dob = date(2010 - (i % 6), (i % 12) + 1, (i % 28) + 1)
                s, s_created = Student.objects.get_or_create(
                    user=su, school=school,
                    defaults={
                        "admission_number": f"ADM-2024-{i+1:04d}",
                        "date_of_birth": dob,
                        "gender": "M" if i % 2 == 0 else "F",
                        "address": f"{i+1} Student Street",
                        "city": "Knowledge City",
                        "state": "Education State",
                        "country": "Learnland",
                        "admission_date": date(2024, 9, 1),
                    },
                )
                if s_created:
                    cls_key = cls_keys[i % len(cls_keys)]
                    Enrollment.objects.get_or_create(
                        student=s, academic_year=ay,
                        defaults={"classroom": classrooms[cls_key], "status": "active", "is_active": True},
                    )
                    # Guardian
                    pu, _ = User.objects.get_or_create(
                        email=f"parent{i+1:03d}@demo.edusphere.school",
                        defaults={
                            "first_name": f"Parent{i+1}", "last_name": lname,
                            "role": UserRole.PARENT, "school": school, "is_active": True,
                        },
                    )
                    if _:
                        pu.set_password("Parent@1234")
                        pu.save()
                    g, _ = Guardian.objects.get_or_create(
                        email=pu.email,
                        defaults={"user": pu, "first_name": f"Parent{i+1}", "last_name": lname,
                                  "phone": f"+1555{i:07d}", "is_primary": True},
                    )
                    StudentGuardian.objects.get_or_create(
                        student=s, guardian=g,
                        defaults={"relationship": "father" if i % 2 == 0 else "mother",
                                  "is_primary_contact": True, "portal_access": True},
                    )
                    student_count += 1

            self.stdout.write(f"  Students: {student_count} created (password: Student@1234)")

            # ── Fee Categories & Structures ────────────────────────────────────
            fee_cats = {
                "Tuition": ("monthly", Decimal("350.00")),
                "Transport": ("monthly", Decimal("80.00")),
                "Activity": ("quarterly", Decimal("120.00")),
                "Library": ("annual", Decimal("50.00")),
            }
            for cat_name, (recurrence, amount) in fee_cats.items():
                cat, _ = FeeCategory.objects.get_or_create(
                    school=school, name=cat_name,
                    defaults={"recurrence": recurrence, "is_mandatory": cat_name in ["Tuition", "Activity"]},
                )
                for grade_obj in grades.values():
                    FeeStructure.objects.get_or_create(
                        school=school, academic_year=ay, grade=grade_obj, fee_category=cat,
                        defaults={"amount": amount, "due_day": 10, "late_fee_per_day": Decimal("5.00")},
                    )

            # ── Periods ────────────────────────────────────────────────────────
            periods_data = [
                (1, "Period 1", "08:00", "08:45"), (2, "Period 2", "08:50", "09:35"),
                (3, "Period 3", "09:40", "10:25"), (0, "Break",    "10:25", "10:45"),
                (4, "Period 4", "10:45", "11:30"), (5, "Period 5", "11:35", "12:20"),
                (8, "Lunch",   "12:20", "13:00"), (6, "Period 6", "13:00", "13:45"),
                (7, "Period 7", "13:50", "14:35"),
            ]
            for num, name, start, end in periods_data:
                Period.objects.get_or_create(
                    school=school, name=name,
                    defaults={"period_number": num, "start_time": start,
                              "end_time": end, "is_break": num == 0},
                )

            # ── Notification Templates ─────────────────────────────────────────
            templates = [
                ("attendance_absent", "Attendance Alert",
                 "Dear Parent, {{student_name}} was absent on {{date}}. Please contact the school.",
                 "{{student_name}} absent on {{date}}",
                 "Attendance Alert", "{{student_name}} was absent today."),
                ("fee_due", "Fee Reminder",
                 "Dear {{student_name}}, your fee payment of ${{amount}} is due on {{due_date}}.",
                 "Fee due: ${{amount}} by {{due_date}}",
                 "Fee Reminder", "Payment of ${{amount}} due on {{due_date}}."),
                ("report_card_published", "Report Card Available",
                 "{{student_name}}'s {{exam_name}} results are now available on the portal.",
                 "{{exam_name}} results available",
                 "Results Available", "Your {{exam_name}} report card is ready."),
            ]
            for event_type, email_subj, email_body, sms_body, push_title, push_body in templates:
                NotificationTemplate.objects.get_or_create(
                    school=school, event_type=event_type,
                    defaults={
                        "name": event_type.replace("_", " ").title(),
                        "email_subject": email_subj, "email_body": email_body,
                        "sms_body": sms_body, "push_title": push_title,
                        "push_body": push_body, "is_active": True,
                    },
                )

            # ── Welcome Announcement ────────────────────────────────────────────
            Announcement.objects.get_or_create(
                school=school, title="Welcome to EduSphere Demo!",
                defaults={
                    "content": "Welcome to the EduSphere School Management System demo. "
                               "Explore all features including attendance, grades, fees, and more.",
                    "priority": "normal", "audience": "all",
                    "is_draft": False, "send_push": True, "created_by": admin,
                },
            )

        self.stdout.write(self.style.SUCCESS("\n✅ Demo school seeded successfully!"))
        self.stdout.write("\nLogin credentials:")
        self.stdout.write(f"  Admin:   admin@demo.edusphere.school  / Admin@1234")
        self.stdout.write(f"  Teacher: sarah.mitchell@demo.edusphere.school / Teacher@1234")
        self.stdout.write(f"  Student: student001@demo.edusphere.school / Student@1234")
        self.stdout.write(f"  Parent:  parent001@demo.edusphere.school  / Parent@1234")
        self.stdout.write(f"\nSchool subdomain: demo.localhost:8000")
