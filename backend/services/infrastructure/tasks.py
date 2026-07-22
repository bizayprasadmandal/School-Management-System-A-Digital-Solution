"""
Infrastructure tasks — database backup automation, sent daily via Celery Beat.
"""

import os
import subprocess
import logging
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


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,  # 5 min between retries
    queue="default",
)
def create_database_backup(self):
    """
    Create a PostgreSQL dump of the primary database, compress it with gzip,
    and store it in BACKUP_DIR. Old backups beyond RETENTION_DAYS are pruned.
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"sms_daily_{timestamp}.sql.gz"
    filepath = os.path.join(BACKUP_DIR, filename)

    # Build pg_dump command
    env = os.environ.copy()
    env["PGPASSWORD"] = PG_PASSWORD

    cmd = [
        "pg_dump",
        "-h", PG_HOST,
        "-p", PG_PORT,
        "-U", PG_USER,
        "-d", PG_DATABASE,
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

    # Prune old backups
    pruned = _prune_old_backups()
    if pruned:
        logger.info("Pruned %d old backup(s)", pruned)

    return {
        "filename": filename,
        "size_bytes": file_size,
        "pruned_count": pruned,
    }


def _prune_old_backups() -> int:
    """Delete backup files older than RETENTION_DAYS."""
    import time
    now = time.time()
    cutoff = now - (RETENTION_DAYS * 86400)
    count = 0

    if not os.path.isdir(BACKUP_DIR):
        return 0

    for fname in os.listdir(BACKUP_DIR):
        if fname.startswith("sms_daily_") and fname.endswith(".sql.gz"):
            fpath = os.path.join(BACKUP_DIR, fname)
            try:
                if os.path.getmtime(fpath) < cutoff:
                    os.remove(fpath)
                    count += 1
            except OSError:
                continue

    return count
