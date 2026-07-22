"""
Management command: seed_role_profiles_data
Creates demo accountant and librarian users + profile records, and creates
ParentProfile records for existing parent users.

Run this AFTER seed_demo_data has been executed at least once.

Usage:
    python manage.py seed_role_profiles_data
    python manage.py seed_role_profiles_data --flush
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date
import random


ACCOUNTANT_CERTIFICATIONS_POOL = [
    "Certified Public Accountant (CPA)",
    "Association of Chartered Certified Accountants (ACCA)",
    "Certified Management Accountant (CMA)",
    "Chartered Accountant (CA)",
    "Certified Internal Auditor (CIA)",
    "Certified Fraud Examiner (CFE)",
    "Chartered Financial Analyst (CFA)",
    "Certified Information Systems Auditor (CISA)",
]

LIBRARIAN_CERTIFICATIONS_POOL = [
    "Master of Library Science (MLS)",
    "American Library Association (ALA) Accreditation",
    "Certified School Librarian (CSL)",
    "Digital Library Certification",
    "Archives and Records Management Certification",
    "Children's Literature Specialist",
    "Information Science Professional (ISP)",
]

BIO_POOL_ACCOUNTANT = [
    "Experienced accountant with over 10 years in educational finance management.",
    "Dedicated to maintaining accurate financial records and ensuring compliance with regulatory standards.",
    "Passionate about financial transparency and helping schools optimize their budget allocation.",
    "Skilled in financial reporting, audit preparation, and fee collection management.",
    "Committed to providing clear financial guidance to students, parents, and staff.",
]

BIO_POOL_LIBRARIAN = [
    "Passionate about fostering a love for reading and research among students.",
    "Experienced in managing both physical and digital library resources.",
    "Dedicated to creating an inclusive and engaging library environment for all students.",
    "Skilled in cataloging, information literacy instruction, and collection development.",
    "Committed to supporting the academic curriculum through curated resources and research assistance.",
]


class Command(BaseCommand):
    help = "Seed demo accountant, librarian, and parent profile data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true",
            help="Delete existing role profile data first",
        )

    def handle(self, *args, **options):
        from services.auth.models import User, UserRole
        from services.hr.models import AccountantProfile
        from services.library.models import LibrarianProfile
        from services.students.models import ParentProfile

        # ── Find the demo school ──────────────────────────────────────────────
        school_admin = User.objects.filter(role=UserRole.SCHOOL_ADMIN).first()
        if not school_admin:
            self.stderr.write(self.style.ERROR(
                "No school admin found! Run seed_demo_data first."
            ))
            return

        school = school_admin.school
        stats = {
            "accountant": 0,
            "librarian": 0,
            "parent_profiles": 0,
        }

        # ── Flush ─────────────────────────────────────────────────────────────
        if options["flush"]:
            with transaction.atomic():
                deleted_acct = AccountantProfile.objects.filter(school=school).delete()[0]
                deleted_lib = LibrarianProfile.objects.filter(school=school).delete()[0]
                deleted_parent = ParentProfile.objects.filter(school=school).delete()[0]
            self.stdout.write(
                f"  Flushed {deleted_acct} accountant, {deleted_lib} librarian, "
                f"{deleted_parent} parent profiles"
            )

        with transaction.atomic():
            # ── 1. Accountant ─────────────────────────────────────────────────
            accountant_user = User.objects.filter(
                school=school, role=UserRole.ACCOUNTANT
            ).first()
            if not accountant_user:
                accountant_user = User.objects.create_user(
                    email="accountant@demo.edusphere.school",
                    password="Accountant@1234",
                    first_name="Priya",
                    last_name="Sharma",
                    school=school,
                    role=UserRole.ACCOUNTANT,
                    is_active=True,
                    is_staff=True,
                    email_verified=True,
                )
                self.stdout.write(
                    f"  Created accountant: {accountant_user.email} / Accountant@1234"
                )

            accountant_profile, created = AccountantProfile.objects.get_or_create(
                user=accountant_user,
                school=school,
                defaults={
                    "qualification": "Master of Commerce (Finance), CPA",
                    "specialization": "Financial Planning & Audit",
                    "experience_years": random.randint(5, 15),
                    "certifications": "; ".join(random.sample(
                        ACCOUNTANT_CERTIFICATIONS_POOL, random.randint(2, 4)
                    )),
                    "bio": random.choice(BIO_POOL_ACCOUNTANT),
                },
            )
            if created:
                stats["accountant"] += 1
                self.stdout.write(f"  Created AccountantProfile for {accountant_user.full_name}")

            # ── 2. Librarian ──────────────────────────────────────────────────
            librarian_user = User.objects.filter(
                school=school, role=UserRole.LIBRARIAN
            ).first()
            if not librarian_user:
                librarian_user = User.objects.create_user(
                    email="librarian@demo.edusphere.school",
                    password="Librarian@1234",
                    first_name="Michael",
                    last_name="Rodriguez",
                    school=school,
                    role=UserRole.LIBRARIAN,
                    is_active=True,
                    is_staff=True,
                    email_verified=True,
                )
                self.stdout.write(
                    f"  Created librarian: {librarian_user.email} / Librarian@1234"
                )

            library_sections = [
                "circulation", "reference", "cataloging", "periodicals",
                "digital", "archives", "children", "general",
            ]
            librarian_profile, created = LibrarianProfile.objects.get_or_create(
                user=librarian_user,
                school=school,
                defaults={
                    "library_section": random.choice(library_sections),
                    "qualification": "Master of Library & Information Science (MLIS)",
                    "experience_years": random.randint(3, 12),
                    "certifications": "; ".join(random.sample(
                        LIBRARIAN_CERTIFICATIONS_POOL, random.randint(2, 3)
                    )),
                    "bio": random.choice(BIO_POOL_LIBRARIAN),
                },
            )
            if created:
                stats["librarian"] += 1
                self.stdout.write(f"  Created LibrarianProfile for {librarian_user.full_name}")

            # ── 3. Parent Profiles ────────────────────────────────────────────
            parent_users = User.objects.filter(
                school=school, role=UserRole.PARENT, is_active=True
            ).select_related("school")

            for parent_user in parent_users:
                profile, created = ParentProfile.objects.get_or_create(
                    user=parent_user,
                    school=school,
                    defaults={
                        "occupation": random.choice([
                            "Teacher", "Engineer", "Doctor", "Business Owner",
                            "Software Developer", "Nurse", "Lawyer", "Accountant",
                            "Civil Servant", "Entrepreneur", "Architect",
                            "Marketing Manager", "Consultant", "Pharmacist",
                        ]),
                        "alternate_phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                        "address": f"{random.randint(1, 999)} Guardian Avenue, Knowledge City",
                        "emergency_contact_name": random.choice([
                            "Grandma Smith", "Uncle John", "Aunt Sarah",
                            "Mr. Johnson (Neighbor)", "Mrs. Davis (Friend)",
                        ]),
                        "emergency_contact_phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                        "bio": f"Parent of {parent_user.first_name}. "
                               f"Actively involved in school activities and "
                               f"committed to supporting their child's education.",
                    },
                )
                if created:
                    stats["parent_profiles"] += 1

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS("\n✅ Role profile demo data seeded!"))
        self.stdout.write(f"\n  Summary for {school.name}:")
        self.stdout.write(f"    Accountant profiles:  {'✅' if stats['accountant'] > 0 else '⚪'} {stats['accountant']} created")
        self.stdout.write(f"    Librarian profiles:   {'✅' if stats['librarian'] > 0 else '⚪'} {stats['librarian']} created")
        self.stdout.write(f"    Parent profiles:      {'✅' if stats['parent_profiles'] > 0 else '⚪'} {stats['parent_profiles']} created")
        self.stdout.write(f"\n  New login credentials (if created):")
        self.stdout.write(f"    Accountant: accountant@demo.edusphere.school / Accountant@1234")
        self.stdout.write(f"    Librarian:  librarian@demo.edusphere.school / Librarian@1234")
