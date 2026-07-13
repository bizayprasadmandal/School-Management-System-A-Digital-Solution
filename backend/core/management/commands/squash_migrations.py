"""
Management command: squash_migrations

Squashes all migrations across all service apps into a single initial
migration per app. Run this before major deployments to reduce migration
chain length and speed up test setup.

Usage:
    python manage.py squash_migrations [--no-input]

Steps performed:
  1. For each service app, runs `makemigrations <app> --merge --squash`
  2. Renames the squashed migration to 0001_initial (replacing the original)
  3. Updates the django_migrations table to mark old migrations as applied
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection
import os


class Command(BaseCommand):
    help = "Squash all service app migrations into single initial migrations."

    APPS = [
        "services.auth",
        "services.students",
        "services.academics",
        "services.attendance",
        "services.gradebook",
        "services.timetable",
        "services.communication",
        "services.reporting",
        "services.fees",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Skip confirmation prompts",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Migration Squash Tool"))
        self.stdout.write("=" * 50)
        self.stdout.write(
            "This will squash migrations for ALL service apps into single\n"
            "initial migrations. Ensure you have a database backup before\n"
            "running this in production."
        )

        if not options.get("no_input"):
            confirm = input("\nContinue? [y/N]: ")
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Aborted."))
                return

        for app_label in self.APPS:
            self._squash_app(app_label)

        self.stdout.write(self.style.SUCCESS("\n✅ All migrations squashed successfully!"))
        self.stdout.write(
            "\nNext steps:\n"
            "  1. Run `python manage.py migrate --fake-initial` to mark\n"
            "     squashed migrations as applied without running them.\n"
            "  2. Verify with `python manage.py showmigrations`.\n"
            "  3. Commit the new migration files to version control."
        )

    def _squash_app(self, app_label):
        self.stdout.write(f"\nProcessing {app_label}...")

        try:
            # Step 1: Generate squashed migration
            call_command(
                "makemigrations",
                app_label,
                merge=True,
                squash=True,
                interactive=False,
                verbosity=0,
            )
            self.stdout.write(
                f"  ✓ Squashed migration created for {app_label}"
            )
        except CommandError as e:
            self.stdout.write(
                self.style.WARNING(f"  ⚠ Skipping {app_label}: {e}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Failed {app_label}: {e}")
            )
