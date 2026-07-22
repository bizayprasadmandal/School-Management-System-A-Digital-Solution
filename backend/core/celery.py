"""
Celery application — configured for Django with auto-discovery of tasks
"""

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

app = Celery("sms")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ─── Periodic task schedule ───────────────────────────────────────────────────
app.conf.beat_schedule = {
    # Attendance reports on 1st of each month at 1 AM
    "monthly-attendance-report": {
        "task": "services.attendance.tasks.generate_monthly_attendance_report",
        "schedule": crontab(hour=1, minute=0, day_of_month=1),
    },
    # Mark overdue invoices daily at midnight
    "mark-overdue-invoices": {
        "task": "services.fees.tasks.mark_overdue_invoices",
        "schedule": crontab(hour=0, minute=5),
    },
    # Send fee reminders 3 days before due date — runs daily at 8 AM
    "fee-due-reminders": {
        "task": "services.fees.tasks.send_fee_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    # Cleanup expired password reset tokens daily
    "cleanup-expired-tokens": {
        "task": "services.auth.tasks.cleanup_expired_tokens",
        "schedule": crontab(hour=2, minute=0),
    },
    # Generate timetable conflicts report every Sunday at 11 PM
    "timetable-conflict-check": {
        "task": "services.timetable.tasks.check_timetable_conflicts",
        "schedule": crontab(hour=23, minute=0, day_of_week=0),
    },
    # Daily database backup at 3 AM
    "daily-database-backup": {
        "task": "services.infrastructure.tasks.create_database_backup",
        "schedule": crontab(hour=3, minute=0),
    },
}

app.conf.task_routes = {
    "services.communication.services.send_push_notification": {"queue": "notifications"},
    "services.communication.services.send_email_notification": {"queue": "notifications"},
    "services.communication.services.send_sms_notification":  {"queue": "notifications"},
    "services.gradebook.tasks.*":  {"queue": "reports"},
    "services.reporting.*":        {"queue": "reports"},
    "services.fees.tasks.*":       {"queue": "default"},
    "services.attendance.tasks.*": {"queue": "default"},
}

app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.timezone = "UTC"
app.conf.task_track_started = True
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1  # Fair distribution across workers
