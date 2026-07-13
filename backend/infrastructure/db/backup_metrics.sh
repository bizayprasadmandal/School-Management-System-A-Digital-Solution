#!/bin/bash
# Prometheus node_exporter textfile collector — Database Backup Metrics
#
# This script exports backup-related metrics in the Prometheus textfile
# format so that node_exporter's --collector.textfile.directory can scrape
# them. Run this via cron every 5 minutes:
#
#   */5 * * * * root /opt/sms/infrastructure/db/backup_metrics.sh
#
# Exported metrics:
#   sms_backup_age_hours      — Age of the latest backup file in hours
#   sms_backup_size_bytes     — Size of the latest backup file in bytes
#   sms_backup_verify_status  — 1 if the last verification passed, 0 otherwise
#   sms_backup_count          — Total number of backup files in the directory
#   sms_backup_oldest_days    — Age of the oldest backup file in days
#
# Output is written to the path specified by NODE_TEXTFILE_DIR, defaulting to
# /var/lib/node_exporter/textfile/ which is the standard location for
# node_exporter's textfile collector.

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────

BACKUP_DIR="${SMS_BACKUP_DIR:-/backups}"
OUTPUT_DIR="${NODE_TEXTFILE_DIR:-/var/lib/node_exporter/textfile}"
OUTPUT_FILE="${OUTPUT_DIR}/sms_backup.prom.$$"    # Write to temp file, then atomic rename
OUTPUT_FINAL="${OUTPUT_DIR}/sms_backup.prom"
VERIFY_FLAG="${SMS_VERIFY_FLAG:-/tmp/sms_backup_verified}"

# ── Ensure output directory exists ──────────────────────────────────────────

mkdir -p "$OUTPUT_DIR"

# ── Gather metrics ──────────────────────────────────────────────────────────

# Find the latest backup file
LATEST=$(ls -t "${BACKUP_DIR}"/sms-daily-*.sql.gz 2>/dev/null | head -1)

if [ -n "$LATEST" ] && [ -f "$LATEST" ]; then
    AGE_HOURS=$(( ($(date +%s) - $(stat -c %Y "$LATEST" 2>/dev/null || stat -f %m "$LATEST")) / 3600 ))
    SIZE_BYTES=$(stat -c %s "$LATEST" 2>/dev/null || stat -f %z "$LATEST")
else
    AGE_HOURS=9999
    SIZE_BYTES=0
fi

# Count total backup files
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/sms-daily-*.sql.gz 2>/dev/null | wc -l)

# Find oldest backup file age in days
OLDEST=$(ls -tr "${BACKUP_DIR}"/sms-daily-*.sql.gz 2>/dev/null | head -1)
if [ -n "$OLDEST" ] && [ -f "$OLDEST" ]; then
    OLDEST_DAYS=$(( ($(date +%s) - $(stat -c %Y "$OLDEST" 2>/dev/null || stat -f %m "$OLDEST")) / 86400 ))
else
    OLDEST_DAYS=0
fi

# Verification status: 1 if the flag file exists and is fresh (< 2 hours old)
VERIFY_STATUS=0
FLAG_AGE=9999
if [ -f "$VERIFY_FLAG" ]; then
    FLAG_STAT=$(stat -c %Y "$VERIFY_FLAG" 2>/dev/null || stat -f %m "$VERIFY_FLAG" 2>/dev/null || echo "")
    if [ -n "$FLAG_STAT" ]; then
        FLAG_AGE=$(( $(date +%s) - FLAG_STAT ))
        if [ "$FLAG_AGE" -lt 7200 ]; then  # 2 hours
            VERIFY_STATUS=1
        fi
    fi
fi

# ── Write metrics ───────────────────────────────────────────────────────────

cat > "$OUTPUT_FILE" <<EOF
# HELP sms_backup_age_hours Age of the latest database backup file in hours
# TYPE sms_backup_age_hours gauge
sms_backup_age_hours ${AGE_HOURS}
# HELP sms_backup_size_bytes Size of the latest database backup file in bytes
# TYPE sms_backup_size_bytes gauge
sms_backup_size_bytes ${SIZE_BYTES}
# HELP sms_backup_verify_status Status of the last backup verification (1 = verified, 0 = not verified or stale)
# TYPE sms_backup_verify_status gauge
sms_backup_verify_status ${VERIFY_STATUS}
# HELP sms_backup_count Total number of backup files in the backup directory
# TYPE sms_backup_count gauge
sms_backup_count ${BACKUP_COUNT}
# HELP sms_backup_oldest_days Age of the oldest backup file in days
# TYPE sms_backup_oldest_days gauge
sms_backup_oldest_days ${OLDEST_DAYS}
EOF

# ── Atomic rename to prevent partial reads ───────────────────────────────────

mv "$OUTPUT_FILE" "$OUTPUT_FINAL"
