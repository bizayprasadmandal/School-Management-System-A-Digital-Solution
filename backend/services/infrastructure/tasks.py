"""
Infrastructure tasks — database backup automation, sent daily via Celery Beat.
"""

import logging
import os
import shutil
import subprocess
from datetime import datetime
from decimal import Decimal

from celery import shared_task

logger = logging.getLogger(__name__)

BACKUP_DIR = os.environ.get("SMS_BACKUP_DIR", "/backups")
RETENTION_DAYS = int(os.environ.get("SMS_BACKUP_RETENTION_DAYS", "30"))
BACKUP_S3_BUCKET = os.environ.get("BACKUP_S3_BUCKET", "")
BACKUP_S3_PREFIX = os.environ.get("BACKUP_S3_PREFIX", "")
BACKUP_S3_REGION = os.environ.get("BACKUP_S3_REGION", "")


def _pg_connection() -> dict:
    """Resolve pg_dump connection settings.

    Explicit PG* environment variables win; otherwise the Django
    ``DATABASES["default"]`` configuration (derived from DATABASE_URL) is
    used. This keeps the backup in sync with whatever database the app
    actually connects to — docker-compose, Kubernetes (sms-postgres-svc),
    or a local override — instead of hardcoding a default host.
    """
    from django.conf import settings

    db = settings.DATABASES["default"]
    return {
        "host": os.environ.get("PGHOST") or db.get("HOST") or "postgres",
        "port": os.environ.get("PGPORT") or db.get("PORT") or "5432",
        "user": os.environ.get("PGUSER") or db.get("USER") or "sms",
        "password": (
            os.environ.get("PGPASSWORD") if os.environ.get("PGPASSWORD") is not None else db.get("PASSWORD") or ""
        ),
        "database": os.environ.get("PGDATABASE") or db.get("NAME") or "sms_db",
    }


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,  # 5 min between retries
    queue="default",
)
def create_database_backup(self):
    """
    Create a PostgreSQL dump of the primary database, compress it with gzip,
    and store it in BACKUP_DIR (filename pattern sms-daily-<ts>.sql.gz, the
    convention used by the monitoring/verification scripts). If
    BACKUP_S3_BUCKET is set, also upload a copy to S3. Old backups beyond
    RETENTION_DAYS are pruned.
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"sms-daily-{timestamp}.sql.gz"
    filepath = os.path.join(BACKUP_DIR, filename)

    # Build pg_dump command
    conn = _pg_connection()
    env = os.environ.copy()
    env["PGPASSWORD"] = conn["password"]

    cmd = [
        "pg_dump",
        "-h",
        conn["host"],
        "-p",
        conn["port"],
        "-U",
        conn["user"],
        "-d",
        conn["database"],
        "--no-owner",
        "--no-acl",
        "--format=plain",  # plain text format pipes well through gzip
    ]

    logger.info("Starting database backup to %s", filepath)

    try:
        with open(filepath, "wb") as f:
            gzip_proc = subprocess.Popen(["gzip"], stdin=subprocess.PIPE, stdout=f)
            dump_proc = subprocess.Popen(cmd, stdout=gzip_proc.stdin, stderr=subprocess.PIPE, env=env)
            _, stderr = dump_proc.communicate()
            gzip_proc.stdin.close()
            gzip_proc.wait()
    except Exception as exc:
        logger.error("Backup failed: %s", exc)
        # Clean up partial file
        if os.path.exists(filepath):
            os.remove(filepath)
        raise self.retry(exc=exc)

    if dump_proc.returncode != 0:
        error_msg = stderr.decode() if stderr else "pg_dump returned non-zero exit code"
        logger.error("Backup failed: %s", error_msg)
        if os.path.exists(filepath):
            os.remove(filepath)
        raise self.retry(Exception(error_msg))

    file_size = os.path.getsize(filepath)
    logger.info("Backup completed: %s (%d bytes)", filepath, file_size)

    # Optional offsite copy — failure here must never lose the local backup.
    uploaded = _upload_to_s3(filepath, filename)

    # Prune old backups
    pruned = _prune_old_backups()
    if pruned:
        logger.info("Pruned %d old backup(s)", pruned)

    return {
        "filename": filename,
        "size_bytes": file_size,
        "uploaded_to_s3": uploaded,
        "pruned_count": pruned,
    }


def _upload_to_s3(filepath: str, filename: str) -> bool:
    """Upload a backup file to S3 via the aws CLI if BACKUP_S3_BUCKET is set.

    Failure-tolerant: logs a warning and returns False rather than raising,
    so the local backup is always preserved.
    """
    if not BACKUP_S3_BUCKET:
        return False

    if shutil.which("aws") is None:
        logger.warning(
            "BACKUP_S3_BUCKET is set but the 'aws' CLI is not installed in this "
            "container; skipping S3 upload for %s",
            filename,
        )
        return False

    prefix = f"{BACKUP_S3_PREFIX.rstrip('/')}/" if BACKUP_S3_PREFIX else ""
    s3_uri = f"s3://{BACKUP_S3_BUCKET}/{prefix}{filename}"
    cmd = ["aws", "s3", "cp", filepath, s3_uri]
    if BACKUP_S3_REGION:
        cmd += ["--region", BACKUP_S3_REGION]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if result.returncode != 0:
            logger.error("S3 upload failed for %s: %s", filename, result.stderr.strip())
            return False
        logger.info("Uploaded backup %s to %s", filename, s3_uri)
        return True
    except Exception as exc:
        logger.error("S3 upload failed for %s: %s", filename, exc)
        return False


def _prune_old_backups() -> int:
    """Delete backup files older than RETENTION_DAYS."""
    import time

    now = time.time()
    cutoff = now - (RETENTION_DAYS * 86400)
    count = 0

    if not os.path.isdir(BACKUP_DIR):
        return 0

    for fname in os.listdir(BACKUP_DIR):
        if fname.startswith("sms-daily-") and fname.endswith(".sql.gz"):
            fpath = os.path.join(BACKUP_DIR, fname)
            try:
                if os.path.getmtime(fpath) < cutoff:
                    os.remove(fpath)
                    count += 1
            except OSError:
                continue

    return count


# ── Asset depreciation engine ──────────────────────────────────────────────────

# Straight-line useful life (years) per asset type. Monthly expense =
# purchase_cost / (years * 12); current value floors at zero once fully
# depreciated.
DEPRECIATION_YEARS = {
    "furniture": 10,
    "electronics": 5,
    "it_device": 3,
    "projector": 5,
    "network": 5,
    "safety": 8,
    "sports": 6,
    "musical": 10,
    "lab": 8,
    "other": 5,
}

DEPRECIATION_ACCOUNT_DEBIT = ("5100", "Depreciation Expense")
DEPRECIATION_ACCOUNT_CREDIT = ("1900", "Accumulated Depreciation")


def _months_elapsed(today, purchase_date) -> int:
    """Whole months between purchase_date and today (>= 0)."""
    months = (today.year - purchase_date.year) * 12 + (today.month - purchase_date.month)
    return max(months, 0)


def _eligible_for_depreciation(today, school=None):
    """Active assets that still carry depreciable value, with their math."""
    from services.infrastructure.models import Asset

    qs = Asset.objects.filter(is_active=True).exclude(status__in=[Asset.Status.RETIRED, Asset.Status.DISPOSED])
    if school is not None:
        qs = qs.filter(school=school)
    for asset in qs:
        if not asset.purchase_date or not asset.purchase_cost or asset.purchase_cost <= 0:
            continue
        years = DEPRECIATION_YEARS.get(asset.asset_type, DEPRECIATION_YEARS["other"])
        life_months = years * 12
        monthly = (asset.purchase_cost / life_months).quantize(Decimal("0.01"))
        elapsed = _months_elapsed(today, asset.purchase_date)
        yield asset, monthly, elapsed, life_months


@shared_task(bind=True, max_retries=3, default_retry_delay=300, queue="default")
def run_monthly_depreciation(self, school_id=None):
    """Post one month of straight-line asset depreciation to the books.

    Recomputes each active asset's ``current_value`` from its purchase cost
    and age (deterministic, so re-runs are idempotent), then posts the
    aggregated monthly expense for the school: Dr 5100 Depreciation Expense /
    Cr 1900 Accumulated Depreciation, keyed on ``DEPR-<yyyy-mm>-<school>``
    so a retried beat schedule never double-posts.
    """
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from services.auth.models import School
    from services.fees.ledger import post_revenue
    from services.fees.models import AccountingEntry
    from services.infrastructure.models import Asset

    today = timezone.now().date()
    month_key = today.strftime("%Y-%m")
    schools = School.objects.filter(is_active=True)
    if school_id:
        schools = schools.filter(id=school_id)

    totals = {"assets_updated": 0, "expense_posted": Decimal("0.00"), "schools": 0}
    for school in schools:
        expense = Decimal("0.00")
        updated = 0
        for asset, monthly, elapsed, life_months in _eligible_for_depreciation(today, school):
            if elapsed <= 0:
                continue  # purchased this month — no full-month expense yet
            depreciated = min(monthly * elapsed, asset.purchase_cost)
            new_value = (asset.purchase_cost - depreciated).quantize(Decimal("0.01"))
            if new_value < 0:
                new_value = Decimal("0.00")
            if new_value != asset.current_value:
                Asset.objects.filter(pk=asset.pk).update(current_value=new_value)
                updated += 1
            if elapsed <= life_months:
                expense += monthly

        if expense <= 0:
            continue

        admin = (
            get_user_model()
            .objects.filter(school=school, role__in=["school_admin", "super_admin"])
            .order_by("date_joined")
            .first()
        )
        for entry_type, account in (
            (AccountingEntry.EntryType.DEBIT, DEPRECIATION_ACCOUNT_DEBIT),
            (AccountingEntry.EntryType.CREDIT, DEPRECIATION_ACCOUNT_CREDIT),
        ):
            post_revenue(
                school=school,
                amount=expense,
                reference_type="depreciation",
                reference_id=f"{month_key}-{school.id}",
                description=f"Asset depreciation — {month_key}",
                transaction_type="other",
                entry_type=entry_type,
                account_code=account[0],
                account_name=account[1],
                user=admin,
            )
        totals["schools"] += 1
        totals["expense_posted"] += expense
        totals["assets_updated"] += updated

    logger.info("run_monthly_depreciation completed for %s", month_key, extra=dict(totals))
    return {**totals, "expense_posted": float(totals["expense_posted"]), "month": month_key}


# ── Preventive maintenance → work orders ──────────────────────────────────────

PM_FREQUENCY_DAYS = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
    "quarterly": 91,
    "semi_annual": 182,
    "annual": 365,
}


@shared_task(bind=True, max_retries=3, default_retry_delay=300, queue="default")
def generate_due_pm_work_orders(self, school_id=None):
    """Create work orders for preventive-maintenance schedules coming due.

    For every ACTIVE schedule with ``next_due <= today``: open a
    ``[PM] <title>`` work order (scheduled on the due date, due a week
    later, category/assignee/cost copied from the schedule) and advance
    ``next_due`` by the schedule frequency. Deduplicated — a schedule with
    an already-open ``[PM]`` work order is skipped, so re-runs never spawn
    duplicates.
    """
    from datetime import timedelta

    from django.utils import timezone
    from services.infrastructure.models import PreventiveMaintenance, WorkOrder

    today = timezone.now().date()
    schedules = PreventiveMaintenance.objects.filter(status=PreventiveMaintenance.Status.ACTIVE).select_related(
        "school", "building", "room", "assigned_to"
    )
    if school_id:
        schedules = schedules.filter(school_id=school_id)

    created = 0
    for pm in schedules:
        if pm.next_due > today:
            continue
        open_wo = WorkOrder.objects.filter(
            school=pm.school,
            title=f"[PM] {pm.title}",
            status__in=[WorkOrder.Status.OPEN, WorkOrder.Status.IN_PROGRESS, WorkOrder.Status.ON_HOLD],
        ).exists()
        if open_wo:
            continue
        WorkOrder.objects.create(
            school=pm.school,
            title=f"[PM] {pm.title}",
            description=pm.description or f"Auto-generated from preventive maintenance schedule: {pm.title}",
            category=pm.category,
            priority=WorkOrder.Priority.MEDIUM,
            building=pm.building,
            room=pm.room,
            assigned_to=pm.assigned_to,
            estimated_cost=pm.estimated_cost,
            scheduled_date=pm.next_due,
            due_date=pm.next_due + timedelta(days=7),
            notes=f"Auto-generated from PM schedule #{pm.pk} ({pm.get_frequency_display()})",
        )
        pm.next_due = pm.next_due + timedelta(days=PM_FREQUENCY_DAYS.get(pm.frequency, 30))
        pm.save(update_fields=["next_due", "updated_at"])
        created += 1

    logger.info("generate_due_pm_work_orders completed", extra={"work_orders_created": created})
    return {"work_orders_created": created}
