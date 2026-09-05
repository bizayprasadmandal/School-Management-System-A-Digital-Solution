"""Seed the RBAC permission catalog + baseline roles for demo/testing.

- Permission catalog is global (no school). Idempotent by codename.
- Roles + RolePermissions are created for every school that has none.

Usage:
    python manage.py seed_rbac_data
    python manage.py seed_rbac_data --roles-only
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from services.auth.models import Permission, Role, RolePermission, School

# module -> list of (verb, description) codenames that make sense in an SIS
CATALOG = {
    "students": [
        ("view", "View student records"),
        ("add", "Create student records"),
        ("change", "Edit student records"),
        ("delete", "Delete student records"),
    ],
    "teachers": [
        ("view", "View teacher records"),
        ("add", "Create teacher records"),
        ("change", "Edit teacher records"),
        ("delete", "Delete teacher records"),
    ],
    "academics": [
        ("view", "View academics"),
        ("manage_classes", "Manage classes and sections"),
        ("manage_curriculum", "Manage curriculum and syllabus"),
    ],
    "attendance": [
        ("view", "View attendance records"),
        ("mark", "Mark attendance"),
        ("manage", "Manage attendance settings"),
    ],
    "gradebook": [
        ("view", "View grades and report cards"),
        ("manage", "Manage assessments and grading"),
        ("publish", "Publish report cards"),
    ],
    "timetable": [
        ("view", "View timetable"),
        ("manage", "Manage timetable and periods"),
    ],
    "exams": [
        ("view", "View exams and results"),
        ("manage", "Manage exams and scheduling"),
    ],
    "fees": [
        ("view", "View fee records"),
        ("collect", "Collect payments"),
        ("manage", "Manage fees and invoicing"),
        ("refund", "Process refunds"),
    ],
    "hr": [
        ("view", "View HR records"),
        ("manage", "Manage staff, payroll, and leave"),
    ],
    "library": [
        ("view", "View library catalog"),
        ("manage", "Manage books, circulation, and fines"),
    ],
    "inventory": [
        ("view", "View inventory"),
        ("manage", "Manage stock and suppliers"),
    ],
    "hostel": [
        ("view", "View hostel records"),
        ("manage", "Manage rooms and allocations"),
    ],
    "transport": [
        ("view", "View transport records"),
        ("manage", "Manage vehicles, drivers, and routes"),
    ],
    "cafeteria": [
        ("view", "View cafeteria records"),
        ("manage", "Manage menus, inventory, and sales"),
    ],
    "sports": [
        ("view", "View sports records"),
        ("manage", "Manage teams, fixtures, and coaching"),
    ],
    "behavior": [
        ("view", "View behavior records"),
        ("manage", "Manage incidents, awards, and referrals"),
    ],
    "counseling": [
        ("view", "View counseling records"),
        ("manage", "Manage sessions, referrals, and plans"),
    ],
    "health": [
        ("view", "View health records"),
        ("manage", "Manage clinic visits and immunizations"),
    ],
    "admissions": [
        ("view", "View admissions applications"),
        ("manage", "Manage applications and enrollment"),
    ],
    "alumni": [
        ("view", "View alumni records"),
        ("manage", "Manage alumni engagement"),
    ],
    "communication": [
        ("view", "View announcements and messages"),
        ("send", "Send announcements and bulk messages"),
        ("manage", "Manage communication settings"),
    ],
    "conferences": [
        ("view", "View conferences and meetings"),
        ("manage", "Manage meetings, Zoom, and recordings"),
    ],
    "reporting": [
        ("view", "View reports"),
        ("export", "Export data"),
        ("manage", "Manage report schedules"),
    ],
    "infrastructure": [
        ("view", "View infrastructure records"),
        ("manage", "Manage buildings, rooms, assets, and maintenance"),
    ],
    "auth": [
        ("view", "View auth and security records"),
        ("manage_roles", "Manage roles and permissions"),
        ("manage_users", "Manage users, sessions, and API keys"),
    ],
}


def seed_permission_catalog():
    """Idempotently create the global permission catalog."""
    created = 0
    for module, verbs in CATALOG.items():
        for verb, label in verbs:
            name = f"{label} ({module}.{verb})"
            codename = f"{module}.{verb}"
            _, was_created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    "name": name,
                    "description": label,
                    "permission_type": (
                        Permission.PermissionType.MODULE if verb == "view" else Permission.PermissionType.ACTION
                    ),
                    "module": module,
                },
            )
            if was_created:
                created += 1
    return created


@transaction.atomic
def seed_roles_for_school(school):
    """Give each school an 'Administrator' role with the full catalog."""
    if Role.objects.filter(school=school, name="Administrator").exists():
        return False
    role = Role.objects.create(
        school=school,
        name="Administrator",
        description="School-wide administrator with full access",
        level=100,
        is_active=True,
        is_system_role=False,
    )
    for permission in Permission.objects.filter(is_active=True):
        RolePermission.objects.create(role=role, permission=permission, granted=True)
    return True


class Command(BaseCommand):
    help = "Seed the global RBAC permission catalog and baseline admin roles."

    def add_arguments(self, parser):
        parser.add_argument(
            "--roles-only",
            action="store_true",
            help="Only ensure baseline roles exist; skip the permission catalog.",
        )

    def handle(self, *args, **options):
        if not options["roles_only"]:
            created = seed_permission_catalog()
            self.stdout.write(self.style.SUCCESS(f"✅ Permission catalog ready ({created} new)."))
        else:
            self.stdout.write(self.style.WARNING("Skipping permission catalog (--roles-only)."))

        made = 0
        for school in School.objects.filter(is_active=True):
            if seed_roles_for_school(school):
                made += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Baseline admin role ensured for {made} school(s)."))
