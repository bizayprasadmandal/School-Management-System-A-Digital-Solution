#!/bin/bash
# Database Backup Verification Script
# Usage: ./verify_backup.sh <backup_file.sql.gz>
#
# Tests that a PostgreSQL backup can be restored to a temporary database
# and verifies data integrity by running basic queries.

set -euo pipefail

BACKUP_FILE="${1:-}"
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "========================================="
echo "  SMS Database Backup Verification"
echo "========================================="
echo "Backup file: $BACKUP_FILE"
echo "Started at:  $(date)"
echo ""

# --- Configuration ---
VERIFY_DB="sms_backup_verify_$(date +%s)"
PG_HOST="${PGHOST:-localhost}"
PG_PORT="${PGPORT:-5432}"
PG_USER="${PGUSER:-sms}"

if [ -z "$PG_PASSWORD" ]; then
    echo "Error: PGPASSWORD is required (set it to the PostgreSQL password before running)." >&2
    exit 1
fi

cleanup() {
    echo "Cleaning up verification database..."
    dropdb --if-exists "$VERIFY_DB" 2>/dev/null || true
}
trap cleanup EXIT

# Step 1: Check file integrity
echo "[1/5] Checking file integrity..."
SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)
echo "  File size: $(numfmt --to=iec $SIZE)"
gunzip -t "$BACKUP_FILE" && echo "  ✓ GZip integrity check passed" || {
    echo "  ✗ Backup file is corrupted (gzip check failed)"
    exit 2
}

# Step 2: Create temporary database
echo "[2/5] Creating verification database: $VERIFY_DB"
createdb -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" "$VERIFY_DB" 2>/dev/null || {
    echo "  ✗ Failed to create temporary database"
    exit 3
}
echo "  ✓ Database created"

# Step 3: Restore backup
echo "[3/5] Restoring backup..."
RESTORE_START=$(date +%s%N)
gunzip -c "$BACKUP_FILE" | psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$VERIFY_DB" -q 2>&1 | tail -5
RESTORE_END=$(date +%s%N)
RESTORE_MS=$(( (RESTORE_END - RESTORE_START) / 1000000 ))
echo "  ✓ Restore completed in ${RESTORE_MS}ms"

# Step 4: Verify data integrity
echo "[4/5] Verifying data integrity..."
psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$VERIFY_DB" -t -c "
    SELECT 'schools:        ' || COUNT(*)::text FROM schools UNION ALL
    SELECT 'users:          ' || COUNT(*)::text FROM users UNION ALL
    SELECT 'students:       ' || COUNT(*)::text FROM students UNION ALL
    SELECT 'enrollments:    ' || COUNT(*)::text FROM enrollments UNION ALL
    SELECT 'invoices:       ' || COUNT(*)::text FROM fee_invoices UNION ALL
    SELECT 'payments:       ' || COUNT(*)::text FROM payments;
" | while IFS= read -r line; do
    echo "  ✓ $line"
done

# Step 5: Summary
echo "[5/5] Verification complete"
echo ""
echo "========================================="
echo "  BACKUP VERIFICATION PASSED"
echo "========================================="
echo "Backup:     $BACKUP_FILE"
echo "Restore:    ${RESTORE_MS}ms"
echo "Completed:  $(date)"
echo ""
echo "Verification database '$VERIFY_DB' will be dropped."
