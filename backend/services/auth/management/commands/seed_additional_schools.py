"""
Management command: seed_additional_schools
Creates additional schools with admin users and basic academic structure.
Does NOT duplicate the full demo data from seed_demo_data (which already
creates teachers, students, classrooms, etc. for the primary demo school).

Usage:
  python manage.py seed_additional_schools
  python manage.py seed_additional_schools --create-full-demo  # Also seed students/teachers
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from decimal import Decimal

SCHOOLS = [
    {
        "name": "Bright Future Academy",
        "subdomain": "brightfuture",
        "code": "BFA",
        "admin_email": "admin@brightfuture.edu",
        "admin_password": "Admin@1234",
        "address": "42 Innovation Drive, Knowledge City",
        "phone": "+1-555-BRIGHT",
    },
    {
        "name": "Green Valley School",
        "subdomain": "greenvalley",
        "code": "GVS",
        "admin_email": "admin@greenvalley.edu",
        "admin_password": "Admin@1234",
        "address": "12 Valley View Road, Education Hills",
        "phone": "+1-555-GREEN",
    },
]


class Command(BaseCommand):
    help = "Seed additional schools with admin accounts and basic structure."

    def add_arguments(self, parser):
        parser.add_argument(
            "--create-full-demo",
            action="store_true",
            help="Also create students, teachers, classrooms, and fees (like seed_demo_data).",
        )

    def _seed_full_demo(self, school, ay):
        """Create students, teachers, classrooms, and fees for the school."""
        from services.auth.models import User, UserRole
        from services.students.models import Grade, Classroom, Student, Guardian, StudentGuardian, Enrollment
        from services.academics.models import Subject, TeacherProfile
        from services.fees.models import FeeCategory, FeeStructure

        student_count = 0
        pwd_config = {
            "teacher": "Teacher@1234",
            "student": "Student@1234",
            "parent": "Parent@1234",
        }

        # ── Grades ─────────────────────────────────────────────────────────
        grade_data = [
            (1, "Grade 1"), (2, "Grade 2"), (3, "Grade 3"),
            (4, "Grade 4"), (5, "Grade 5"), (6, "Grade 6"),
        ]
        grades = {}
        for level, name in grade_data:
            g, _ = Grade.objects.get_or_create(school=school, level=level, defaults={"name": name})
            grades[level] = g

        # ── Subjects ───────────────────────────────────────────────────────
        core_subjects = ["Mathematics", "English", "Science", "Social Studies", "Computer Science"]
        for grade_level, grade_obj in grades.items():
            for sname in core_subjects:
                Subject.objects.get_or_create(
                    school=school, grade=grade_obj,
                    code=f"{sname[:3].upper()}{grade_level:02d}",
                    defaults={"name": sname, "is_core": True, "max_marks": 100, "pass_marks": 40},
                )

        # ── Teachers ────────────────────────────────────────────────────────
        teacher_names = [
            ("Alice", "Morgan"), ("Benjamin", "Clark"), ("Catherine", "Lee"),
            ("Daniel", "Wright"), ("Eleanor", "Hall"), ("Frank", "Adams"),
        ]
        teachers = []
        school_prefix = school.code.upper()  # e.g. BFA, GVS
        for idx, (fname, lname) in enumerate(teacher_names):
            email = f"{fname.lower()}.{lname.lower()}@{school.subdomain}.edu"
            u, created_u = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": fname, "last_name": lname,
                    "role": UserRole.TEACHER, "school": school, "is_active": True,
                },
            )
            if created_u:
                u.set_password(pwd_config["teacher"])
                u.email_verified = True
                u.save()
            # employee_id is globally unique — prefix with school code to avoid clashes
            emp_id = f"{school_prefix}-T{idx+1:03d}"
            TeacherProfile.objects.get_or_create(
                user=u, school=school,
                defaults={
                    "employee_id": emp_id,
                    "gender": "F" if idx % 2 == 0 else "M",
                    "qualification": "master",
                    "specialization": core_subjects[idx % len(core_subjects)],
                    "joining_date": date(2020, 8, 1),
                    "experience_years": 4 + idx,
                    "department": "Academic",
                    "address": f"{idx+1} Teacher Lane, Education City",
                },
            )
            teachers.append(u)
        self.stdout.write(f"    Teachers: {len(teachers)}")

        # ── Classrooms ─────────────────────────────────────────────────────
        classrooms = {}
        for grade_level in range(1, 5):  # Grades 1-4, 2 sections each
            for section in ["A", "B"]:
                teacher = teachers[(grade_level * 2 + ord(section) - ord("A")) % len(teachers)]
                cls, _ = Classroom.objects.get_or_create(
                    school=school, grade=grades[grade_level],
                    name=f"{grade_level}{section}", academic_year=ay,
                    defaults={"capacity": 30, "class_teacher": teacher, "room_number": f"R{grade_level}{section}"},
                )
                classrooms[f"{grade_level}{section}"] = cls

        # ── Students & Guardians ────────────────────────────────────────────
        first_names = ["Aiden","Emma","Liam","Olivia","Noah","Ava","William","Sophia","James","Isabella"]
        last_names = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis"]
        cls_keys = list(classrooms.keys())

        for i in range(60):  # 60 students per school
            fname = first_names[i % len(first_names)]
            lname = last_names[i % len(last_names)]
            email = f"student{i+1:04d}@{school.subdomain}.edu"
            su, created_u = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": fname, "last_name": lname,
                    "role": UserRole.STUDENT, "school": school, "is_active": True,
                },
            )
            if created_u:
                su.set_password(pwd_config["student"])
                su.email_verified = True
                su.save()

            dob = date(2010 - (i % 6), (i % 12) + 1, (i % 28) + 1)
            s, s_created = Student.objects.get_or_create(
                user=su, school=school,
                defaults={
                    "admission_number": f"ADM-{school.code}-{i+1:04d}",
                    "date_of_birth": dob,
                    "gender": "M" if i % 2 == 0 else "F",
                    "address": f"{i+1} Student Street",
                    "city": "Education City",
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
                    email=f"parent{i+1:04d}@{school.subdomain}.edu",
                    defaults={
                        "first_name": f"Parent{i+1}", "last_name": lname,
                        "role": UserRole.PARENT, "school": school, "is_active": True,
                    },
                )
                if _:
                    pu.set_password(pwd_config["parent"])
                    pu.email_verified = True
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

        self.stdout.write(f"    Students: {student_count}")

        # ── Fee Categories ─────────────────────────────────────────────────
        fee_cats = {
            "Tuition": ("monthly", Decimal("300.00")),
            "Transport": ("monthly", Decimal("70.00")),
            "Activity": ("quarterly", Decimal("100.00")),
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

    def handle(self, *args, **options):
        from services.auth.models import School, User, UserRole
        from services.students.models import AcademicYear

        self.stdout.write(self.style.MIGRATE_HEADING("🏫 Seeding additional schools…"))

        for school_config in SCHOOLS:
            name = school_config["name"]
            subdomain = school_config["subdomain"]
            code = school_config["code"]

            with transaction.atomic():
                # ── School ──────────────────────────────────────────────────────
                school, created = School.objects.get_or_create(
                    subdomain=subdomain,
                    defaults={
                        "name": name,
                        "code": code,
                        "address": school_config["address"],
                        "phone": school_config["phone"],
                        "email": school_config["admin_email"],
                        "website": f"https://{subdomain}.school.edu",
                        "timezone": "UTC",
                        "subscription_tier": "standard",
                    },
                )
                status = "✅ created" if created else "⚠️ already exists"
                self.stdout.write(f"  {name} ({status})")

                # ── Academic Year ────────────────────────────────────────────────
                ay, ay_created = AcademicYear.objects.get_or_create(
                    school=school, name="2024-2025",
                    defaults={
                        "start_date": date(2024, 9, 1),
                        "end_date": date(2025, 6, 30),
                        "is_current": True,
                    },
                )

                # ── Admin User ────────────────────────────────────────────────────
                admin_email = school_config["admin_email"]
                admin_pwd = school_config["admin_password"]
                admin, admin_created = User.objects.get_or_create(
                    email=admin_email,
                    defaults={
                        "first_name": name.split()[0],
                        "last_name": "Admin",
                        "role": UserRole.SCHOOL_ADMIN,
                        "school": school,
                        "is_active": True,
                        "is_staff": True,
                        "email_verified": True,
                    },
                )
                if admin_created:
                    admin.set_password(admin_pwd)
                    admin.save()

                self.stdout.write(f"    Admin: {admin_email} / {admin_pwd}")

                # ── Additional role users ─────────────────────────────────────────
                # Accountant
                accountant_user, acc_created = User.objects.get_or_create(
                    email=f"accountant@{subdomain}.edu",
                    defaults={
                        "first_name": "School", "last_name": "Accountant",
                        "role": UserRole.ACCOUNTANT, "school": school,
                        "is_active": True, "email_verified": True,
                    },
                )
                if acc_created:
                    accountant_user.set_password(admin_pwd)
                    accountant_user.save()

                # Librarian
                librarian_user, lib_created = User.objects.get_or_create(
                    email=f"librarian@{subdomain}.edu",
                    defaults={
                        "first_name": "School", "last_name": "Librarian",
                        "role": UserRole.LIBRARIAN, "school": school,
                        "is_active": True, "email_verified": True,
                    },
                )
                if lib_created:
                    librarian_user.set_password(admin_pwd)
                    librarian_user.save()

                # ── Full demo data (optional) ────────────────────────────────────
                if options["create_full_demo"]:
                    self.stdout.write(f"    Seeding full demo data for {name}…")
                    self._seed_full_demo(school, ay)

                # ── Payment Gateway Config ─────────────────────────────────────────
                from services.fees.models import PaymentGatewayConfig
                PaymentGatewayConfig.objects.get_or_create(
                    school=school,
                    defaults={
                        "stripe_enabled": True,
                        "khalti_enabled": False,
                        "esewa_enabled": False,
                    },
                )

        self.stdout.write(self.style.SUCCESS("\n✅ Additional schools seeded!"))

        self.stdout.write("\nNew school admin credentials:")
        for s in SCHOOLS:
            self.stdout.write(f"  {s['name']}:")
            self.stdout.write(f"    Admin:     {s['admin_email']} / {s['admin_password']}")
            self.stdout.write(f"    Accountant: accountant@{s['subdomain']}.edu / Admin@1234")
            self.stdout.write(f"    Librarian:  librarian@{s['subdomain']}.edu / Admin@1234")
            if options["create_full_demo"]:
                self.stdout.write(f"    Teacher:   alice.morgan@{s['subdomain']}.edu / Teacher@1234")
                self.stdout.write(f"    Student:   student0001@{s['subdomain']}.edu / Student@1234")
                self.stdout.write(f"    Parent:    parent0001@{s['subdomain']}.edu / Parent@1234")
