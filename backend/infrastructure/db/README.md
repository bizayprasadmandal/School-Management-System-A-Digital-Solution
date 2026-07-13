# Database Backup & Verification

Scripts and procedures for PostgreSQL backup management, verification, and disaster recovery
for the SMS application database.

---

## Table of Contents

- [Overview](#overview)
- [Backup Verification Script](#backup-verification-script)
- [Automated Backup Strategy](#automated-backup-strategy)
- [Disaster Recovery](#disaster-recovery)
- [Monitoring & Alerts](#monitoring--alerts)
- [Compliance & Auditing](#compliance--auditing)
- [Troubleshooting](#troubleshooting)

---

## Overview

The SMS application uses PostgreSQL (RDS / Cloud SQL / self-hosted) as its primary database.
The backup strategy follows the 3-2-1 rule:

- **3** copies of data (1 primary + 2 backups)
- **2** different media types (disk + S3/object storage)
- **1** copy off-site (cross-region or separate bucket)

| Backup type | Frequency | Retention | Method |
|-------------|-----------|-----------|--------|
| Automated snapshot | Daily | 30 days | RDS automated snapshots / `pg_dump` cron |
| Transaction logs (WAL) | Continuous | 7 days | `pg_archive` or RDS PITR |
| Manual export | Weekly | 90 days | `pg_dump` → gzip → S3 |
| Verification | After every manual backup | N/A | `verify_backup.sh` |

---

## Backup Verification Script

### Purpose

`verify_backup.sh` tests that a `pg_dump` compressed backup (`.sql.gz`) can
be successfully restored to a temporary PostgreSQL database. It validates:

1. **File integrity** — the `.gz` archive is not corrupted.
2. **Restore success** — the SQL dump can be applied without errors.
3. **Data integrity** — key tables contain the expected row counts.
4. **Cleanup** — the temporary database is dropped after verification.

### Usage

```bash
# From the infrastructure/db/ directory
./verify_backup.sh /path/to/backup-2025-01-15.sql.gz
```

### Prerequisites

| Tool | Purpose |
|------|---------|
| `psql` (PostgreSQL client) | Execute SQL statements |
| `createdb` / `dropdb` | Create and destroy temporary databases |
| `gunzip` | Decompress `.gz` backups |
| `stat` | Check file size |

Install on macOS:

```bash
brew install postgresql@16
# Add to PATH (if not linked):
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
```

Install on Ubuntu/Debian:

```bash
sudo apt-get install postgresql-client
```

### Configuration

The script reads these environment variables (with defaults):

| Variable | Default | Description |
|----------|---------|-------------|
| `PGHOST` | `localhost` | PostgreSQL host |
| `PGPORT` | `5432` | PostgreSQL port |
| `PGUSER` | `sms` | Database user |
| `PGPASSWORD` | `sms` | Database password |

Override for remote databases:

```bash
PGHOST=production-rds.aws.com \
PGUSER=backup_user \
PGPASSWORD=securepass \
./verify_backup.sh backup-2025-01-15.sql.gz
```

### What the Script Does

```
[1/5] Checking file integrity...
  File size: 47M
  ✓ GZip integrity check passed

[2/5] Creating verification database: sms_backup_verify_1736908800
  ✓ Database created

[3/5] Restoring backup...
  ✓ Restore completed in 3247ms

[4/5] Verifying data integrity...
  ✓ schools:          5
  ✓ users:            142
  ✓ students:         1287
  ✓ enrollments:      1492
  ✓ invoices:         8456
  ✓ payments:         12394

[5/5] Verification complete

=========================================
  BACKUP VERIFICATION PASSED
=========================================
Backup:     backup-2025-01-15.sql.gz
Restore:    3247ms
Completed:  Wed Jan 15 03:15:22 UTC 2025

Verification database 'sms_backup_verify_1736908800' will be dropped.
```

### Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Backup verified successfully |
| 1 | File not found / usage error |
| 2 | GZip integrity check failed |
| 3 | Could not create temporary database |

### Cron Job Setup

Schedule nightly verification 30 minutes after the backup completes:

```bash
# crontab — runs daily at 2:30 AM
30 2 * * * /opt/sms/infrastructure/db/verify_backup.sh \
  /backups/sms-daily-$(date +\%Y-\%m-\%d).sql.gz \
  >> /var/log/sms-backup-verify.log 2>&1
```

### Slack / Email Alerts

Wrap the script to send notifications:

```bash
#!/bin/bash
# /opt/sms/infrastructure/db/verify_and_notify.sh

BACKUP_FILE="$1"
LOG=$(mktemp)

if ./verify_backup.sh "$BACKUP_FILE" > "$LOG" 2>&1; then
  curl -X POST -H "Content-Type: application/json" \
    -d '{"text":"✅ Backup verified: '"$BACKUP_FILE"'"}' \
    "${SLACK_WEBHOOK_URL}"
else
  curl -X POST -H "Content-Type: application/json" \
    -d '{"text":"❌ Backup verification FAILED: '"$BACKUP_FILE"'"}' \
    "${SLACK_WEBHOOK_URL}"
  cat "$LOG" | mail -s "BACKUP VERIFICATION FAILED: $BACKUP_FILE" ops@school.edu
fi

rm "$LOG"
```

---

## Automated Backup Strategy

### Daily Production Backup (`pg_dump`)

```bash
#!/bin/bash
# /opt/sms/infrastructure/db/daily_backup.sh

BACKUP_DIR="/backups"
DB_NAME="sms_db"
DATE=$(date +%Y-%m-%d)
FILENAME="${BACKUP_DIR}/sms-daily-${DATE}.sql.gz"
RETENTION_DAYS=90

# Step 1 — Dump and compress
pg_dump \
  -h "$PGHOST" \
  -U "$PGUSER" \
  -d "$DB_NAME" \
  --no-owner \
  --no-acl \
  --compress=9 \
  -f "$FILENAME"

# Step 2 — Upload to S3
aws s3 cp "$FILENAME" "s3://sms-backups/daily/${DATE}/"

# Step 3 — Verify immediately
cd /opt/sms/infrastructure/db
./verify_backup.sh "$FILENAME"

# Step 4 — Prune old backups
find "$BACKUP_DIR" -name "sms-daily-*.sql.gz" -mtime +$RETENTION_DAYS -delete
```

### RDS Automated Snapshots

For AWS RDS, automated daily snapshots are configured via Terraform
(`infrastructure/terraform/main.tf`):

```hcl
resource "aws_db_instance" "sms_postgres" {
  backup_retention_period = 30
  backup_window           = "01:00-02:00"
  maintenance_window      = "sun:03:00-04:00"
  copy_tags_to_snapshot   = true
  deletion_protection     = true
}
```

### Cross-Region Replication

For DR compliance, copy snapshots to a secondary region:

```bash
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier arn:aws:rds:us-east-1:123456:snapshot:sms-manual-2025-01-15 \
  --target-db-snapshot-identifier sms-dr-2025-01-15 \
  --source-region us-east-1 \
  --region eu-west-1
```

---

## Disaster Recovery

### Recovery Time Objectives (RTO) / Recovery Point Objectives (RPO)

| Tier | Scenario | RTO | RPO | Method |
|------|----------|:---:|:---:|--------|
| 1 | Accidental data loss (row/schema) | 1 hour | 5 min | PITR (WAL logs) |
| 2 | Database corruption | 4 hours | 24 hours | Latest verified snapshot |
| 3 | Region outage | 8 hours | 1 hour | Cross-region replica |

### Point-in-Time Recovery (PITR)

```bash
# Step 1 — Find the target timestamp
aws rds describe-db-instances --db-instance-identifier sms-postgres

# Step 2 — Restore to a specific time (5-minute granularity on RDS)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier sms-postgres \
  --target-db-instance-identifier sms-postgres-pitr \
  --restore-time "2025-01-15T14:30:00Z"

# Step 3 — Verify data integrity
PGHOST=sms-postgres-pitr.aws.com ./verify_backup.sh

# Step 4 — Promote to primary
# Update DNS / load balancer target group to point at the restored instance
```

### Full Restore from Snapshot

```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier sms-postgres \
  --query 'DBSnapshots[?Status==`available`].[DBSnapshotIdentifier,SnapshotCreateTime]' \
  --output table

# Restore the most recent verified snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier sms-postgres-restored \
  --db-snapshot-identifier sms-manual-2025-01-15 \
  --vpc-security-group-ids sg-12345 \
  --db-subnet-group-name sms-subnet-group
```

### Backup Verification Runbook

If `verify_backup.sh` fails:

1. **Check the exit code** and error message.
2. **Verify disk space** on the database host `df -h`.
3. **Check PostgreSQL logs** for corruption indicators.
4. **Test an older backup** to determine if corruption is recent.
5. **If all recent backups fail**, escalate to infrastructure lead and consider
   PITR from WAL archives.
6. **If a single backup fails**, delete it, re-run the backup job, and re-verify.

---

## Monitoring & Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|:--------:|--------|
| Backup verification failed | Script exits non-zero | **P1** | Alert on-call via PagerDuty |
| Backup age > 36 hours | Latest backup timestamp | **P2** | Investigate cron job health |
| Restore time > 30 minutes | `verify_backup.sh` elapsed time | **P3** | Review database size growth |
| Disk space < 20% on backup host | `df` check | **P2** | Prune old backups or expand volume |

### Prometheus / Grafana — Backup Metrics

> 📄 **Script:** `infrastructure/db/backup_metrics.sh`  
> 📄 **Prometheus rules:** `infrastructure/monitoring/rules/backup_alerts.yml`

Export backup metrics via the node_exporter [textfile collector](https://github.com/prometheus/node_exporter#textfile-collector).

#### Setup

1. **Install the script** on the backup host:

   ```bash
   sudo install -m 755 infrastructure/db/backup_metrics.sh \
     /opt/sms/infrastructure/db/backup_metrics.sh
   ```

2. **Configure node_exporter** with the `--collector.textfile.directory` flag:

   ```bash
   # In your node_exporter systemd unit or container args:
   --collector.textfile.directory=/var/lib/node_exporter/textfile
   ```

3. **Create the cron job** (`/etc/cron.d/sms-backup-metrics`):

   ```bash
   */5 * * * * root /opt/sms/infrastructure/db/backup_metrics.sh
   ```

#### Exported Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `sms_backup_age_hours` | gauge | Age of the latest backup in hours (9999 = none) |
| `sms_backup_size_bytes` | gauge | Size of the latest backup in bytes |
| `sms_backup_verify_status` | gauge | 1 if last verification passed and fresh (< 2h), 0 otherwise |
| `sms_backup_count` | gauge | Total backup files in the directory |
| `sms_backup_oldest_days` | gauge | Age of the oldest backup in days |

#### Prometheus Alerts

The file `infrastructure/monitoring/rules/backup_alerts.yml` defines these alerts:

| Alert | Severity | Condition |
|-------|:--------:|-----------|
| `BackupMissing` | 🔴 P1 | No backup older than 36 hours |
| `BackupVerificationStale` | 🟡 P2 | Last verification > 2 hours ago |
| `BackupSizeAnomaly` | 🟡 P2 | Backup < 1 MB (possible corruption) |
| `BackupJobStopped` | 🟡 P2 | Zero backup files found |
| `BackupRetentionTooShort` | 🔵 P3 | Oldest backup < 30 days |
| `BackupGrowthAccelerating` | 🔵 P3 | Growth > 50 MB/day |

Apply the rules to Prometheus by adding to the `rule_files` section of your
Prometheus config:

```yaml
rule_files:
  - "/etc/prometheus/rules/*.yml"
```

---

## Compliance & Auditing

| Requirement | How it's met |
|-------------|-------------|
| Backup verification log | Every `verify_backup.sh` run produces a timestamped log |
| Retention policy | 30-day automated snapshots, 90-day manual exports |
| Encryption at rest | RDS encryption + S3 server-side encryption (SSE-S3) |
| Encryption in transit | TLS for all database connections |
| Access control | IAM roles restrict S3 bucket access to backup automation only |
| Cross-region DR | Manual snapshot copy to secondary region quarterly |

### Log Format

Each verification run is logged to a file. Example log entry:

```
=========================================
  SMS Database Backup Verification
=========================================
Backup file: /backups/sms-daily-2025-01-15.sql.gz
Started at:  Wed Jan 15 03:00:22 UTC 2025

[1/5] Checking file integrity...
  File size: 47M
  ✓ GZip integrity check passed
[2/5] Creating verification database: sms_backup_verify_1736908800
  ✓ Database created
[3/5] Restoring backup...
  ✓ Restore completed in 3247ms
[4/5] Verifying data integrity...
  ✓ schools:          5
  ✓ users:            142
  ✓ students:         1287
  ✓ enrollments:      1492
  ✓ invoices:         8456
  ✓ payments:         12394
[5/5] Verification complete

=========================================
  BACKUP VERIFICATION PASSED
=========================================
Backup:     /backups/sms-daily-2025-01-15.sql.gz
Restore:    3247ms
Completed:  Wed Jan 15 03:00:52 UTC 2025
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `psql: FATAL: password authentication failed` | Wrong `PGPASSWORD` | Check `.env` or secret store |
| `createdb: error: could not connect to server` | PostgreSQL not running | `docker compose up -d postgres` or check RDS status |
| `gunzip: invalid compressed data` | Backup file is corrupted | Re-run the backup job |
| `ERROR: relation "schools" does not exist` | Backup from wrong database | Verify `DB_NAME` matches the application database |
| `ERROR: must be owner of extension pgcrypto` | Missing `--no-owner` in `pg_dump` | Add `--no-owner` flag to dump command |
| `numfmt: command not found` | macOS / minimal Linux | Install `coreutils` (`brew install coreutils`) or remove `numfmt` from script |
| `stat: illegal option -- c` | BSD `stat` (macOS) vs GNU `stat` | The script handles both with `||` fallback |
| Verification DB already exists | Previous run didn't clean up | `dropdb sms_backup_verify_*` or wait for 60s timeout |
| Restore takes > 10 minutes | Very large database | Consider `pg_restore --jobs=4` for parallel restore |

### Quick Connectivity Test

```bash
PGPASSWORD=sms psql -h localhost -U sms -d sms_db -c "SELECT count(*) FROM users;"
```
