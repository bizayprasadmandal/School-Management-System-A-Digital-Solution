"""
Celery application — configured for Django with auto-discovery of tasks
"""

import logging
import logging.config
import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging, task_failure
from django.conf import settings

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
    # Cleanup expired email verification tokens daily
    "cleanup-expired-verification-tokens": {
        "task": "services.auth.tasks.cleanup_expired_verification_tokens",
        "schedule": timedelta(hours=24),
        "options": {"expires": 3600},
    },
    # Warn users when their 2FA backup codes run low — daily
    "notify-low-backup-codes": {
        "task": "services.auth.tasks.notify_low_backup_codes",
        "schedule": timedelta(hours=24),
        "options": {"expires": 3600},
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
    "services.communication.services.send_sms_notification": {"queue": "notifications"},
    "services.gradebook.tasks.*": {"queue": "reports"},
    "services.reporting.*": {"queue": "reports"},
    "services.fees.tasks.*": {"queue": "default"},
    "services.attendance.tasks.*": {"queue": "default"},
}

app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.timezone = "UTC"
app.conf.task_track_started = True
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1  # Fair distribution across workers

# ─── Worker logging ────────────────────────────────────────────────────────────
# Celery installs its own log handlers by default, which would bypass Django's
# LOGGING configuration (JSON in production). Taking over via the
# `setup_logging` signal routes EVERY worker logger — the `celery.*` runtime
# loggers, `services.*` task modules, and `celery.task` — through the project's
# configured formatters, so task modules keep their `extra` context (e.g.
# {"invoice_count": n}) as real JSON fields.


@setup_logging.connect
def _configure_worker_logging(loglevel=None, logfile=None, **kwargs):
    logging.config.dictConfig(settings.LOGGING)


_SENSITIVE_ARG_KEYS = {"password", "token", "secret", "key", "authorization", "credentials"}


def _is_sensitive_key(key):
    """True for exact matches and for compound keys like `stripe_secret_key`.

    Words of 4+ chars match as substrings (catches `api_token`); the 3-char
    `key` matches exactly only, so innocuous keys like `monkey` stay visible.
    """
    lowered = key.lower()
    if lowered in _SENSITIVE_ARG_KEYS:
        return True
    return any(part in lowered for part in _SENSITIVE_ARG_KEYS if len(part) >= 4)


def _summarize(value, limit=200):
    """Compact, PII-safe representation of task args/kwargs for structured logs."""
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            if isinstance(k, str) and _is_sensitive_key(k):
                parts.append(f"{k}='***'")
            else:
                parts.append(f"{k}={_summarize(v, limit)}")
        return "{" + ", ".join(parts)[:limit] + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_summarize(v, limit) for v in value)[:limit] + "]"
    text = str(value)
    return text[:limit] + ("..." if len(text) > limit else "")


# ─── Task failure reporting ────────────────────────────────────────────────────
# Sentry forwarding for worker errors is handled by the `sentry-sdk` Celery
# integration, already enabled in `core.settings.production` (see
# `CeleryIntegration`). This handler additionally logs every failure as a
# structured line with task context, so failures are queryable even when a
# Sentry DSN isn't configured (e.g. staging).


@task_failure.connect
def _log_task_failure(sender=None, task_id=None, args=None, kwargs=None, retries=None, einfo=None, **extra):
    # A logging handler must never raise: a receiver exception would propagate
    # through Celery's signal machinery into the task failure/retry path.
    try:
        logger = logging.getLogger("celery.task")
        request = getattr(sender, "request", None)
        task_name = getattr(sender, "name", str(sender))
        logger.error(
            "Task %s failed (task_id=%s, queue=%s)",
            task_name,
            task_id,
            getattr(request, "queue", None),
            exc_info=getattr(einfo, "exception", None) if einfo is not None else None,
            # NB: keys are task_args/task_kwargs — `args`/`kwargs` are reserved
            # LogRecord attributes and would raise KeyError in makeRecord.
            extra={
                "task": task_name,
                "task_id": task_id,
                "task_args": _summarize(args) if args else None,
                "task_kwargs": _summarize(kwargs) if kwargs else None,
                "retries": (
                    retries if retries is not None else (getattr(request, "retries", 0) if request is not None else 0)
                ),
            },
        )
    except Exception:  # pragma: no cover — logging must never break task execution
        pass
