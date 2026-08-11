"""
Management command: seed_notification_templates
Ensure every school has the standard notification templates
(attendance alerts, fee due/overdue, report cards, announcements).

Idempotent — only creates missing templates; existing customizations are kept.

Usage:
  python manage.py seed_notification_templates
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed standard notification templates for all schools."

    def handle(self, *args, **options):
        from services.auth.models import School
        from services.communication.templates import ensure_school_notification_templates

        total_created = 0
        schools = 0
        for school in School.objects.all().iterator(chunk_size=200):
            schools += 1
            total_created += ensure_school_notification_templates(school)

        self.stdout.write(
            self.style.SUCCESS(f"Checked {schools} school(s); created {total_created} missing template(s).")
        )
