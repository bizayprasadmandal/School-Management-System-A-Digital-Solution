"""
Seed the demo users required by the Playwright e2e suite (frontend/web/e2e).

The specs log in as real accounts (admin@school.edu, teacher@school.edu, ...),
so those users must exist in the backend with the exact credentials the specs
use. This command is idempotent — safe to run against an existing database.

Usage:
    python manage.py seed_e2e_data
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from services.auth.models import School, User

# Credentials the Playwright specs (frontend/web/e2e/helpers.ts + specs) use.
E2E_USERS = [
    {
        "email": "admin@school.edu",
        "password": "Admin@1234",
        "role": "school_admin",
        "first_name": "Admin",
        "last_name": "User",
        "is_staff": True,
    },
    {
        "email": "teacher@school.edu",
        "password": "Teacher@1234",
        "role": "teacher",
        "first_name": "Demo",
        "last_name": "Teacher",
    },
    {
        "email": "student@school.edu",
        "password": "Student@1234",
        "role": "student",
        "first_name": "Demo",
        "last_name": "Student",
    },
    {
        "email": "parent@school.edu",
        "password": "Parent@1234",
        "role": "parent",
        "first_name": "Demo",
        "last_name": "Parent",
    },
    {
        "email": "accountant@school.edu",
        "password": "TestPass@1234",
        "role": "accountant",
        "first_name": "Demo",
        "last_name": "Accountant",
    },
    {
        "email": "librarian@school.edu",
        "password": "TestPass@1234",
        "role": "librarian",
        "first_name": "Demo",
        "last_name": "Librarian",
    },
    {
        "email": "counselor@school.edu",
        "password": "TestPass@1234",
        "role": "counselor",
        "first_name": "Demo",
        "last_name": "Counselor",
    },
]


class Command(BaseCommand):
    help = "Seed the demo users required by the Playwright e2e suite."

    @transaction.atomic
    def handle(self, *args, **options):
        school, _ = School.objects.get_or_create(
            code="E2E",
            defaults={
                "name": "E2E Test School",
                "subdomain": "e2e",
                "address": "123 Test Street",
                "phone": "+10000000000",
                "email": "e2e@school.edu",
                "website": "https://example.com",
            },
        )

        results = []
        for data in E2E_USERS:
            user, was_created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "school": school,
                    "role": data["role"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "is_active": True,
                    "email_verified": True,
                    "is_staff": data.get("is_staff", False),
                },
            )
            # Keep tenant, role, and credentials in sync on re-runs so the
            # e2e specs always authenticate against the expected accounts.
            user.school = school
            user.role = data["role"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.is_active = True
            user.email_verified = True
            user.is_staff = data.get("is_staff", False)
            user.set_password(data["password"])
            user.save()
            results.append((data["email"], was_created))

        self.stdout.write(self.style.SUCCESS(f"E2E school ready: {school.name} ({school.code})"))
        for email, was_created in results:
            status = "created" if was_created else "updated"
            self.stdout.write(f"  {email} [{status}]")
