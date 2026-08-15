"""
Infrastructure tasks — database backup automation, sent daily via Celery Beat.
"""

import logging
import os
import shutil
import subprocess
from datetime import datetime

from celery import shared_task

logger = logging.getLogger(__name__)

BACKUP_DIR = os.environ.get("SMS_BACKUP_DIR", "/backups")
PG_HOST = os.environ.get("PGHOST", "postgres")
PG_PORT = os.environ.get("PGPORT", "5432")
PG_USER = os.environ.get("PGUSER", "sms")
PG_PASSWORD = os.environ.get("PGPASSWORD", "sms")
PG_DATABASE = os.environ.get("PGDATABASE", "sms_db")
RETENTION_DAYS = int(os.environ.get("SMS_BACKUP_RETENTION_DAYS", "30"))
BACKUP_S3_BUCKET = os.environ.get("BACKUP_S3_BUCKET", "")
BACKUP_S3_PREFIX = os.environ.get("BACKUP_S3_PREFIX", "")
BACKUP_S3_REGION = os.environ.get("BACKUP_S3_REGION", "")


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
    env = os.environ.copy()
    env["PGPASSWORD"] = PG_PASSWORD

    cmd = [
        "pg_dump",
        "-h",
        PG_HOST,
        "-p",
        PG_PORT,
        "-U",
        PG_USER,
        "-d",
        PG_DATABASE,
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
