#!/bin/bash
# Karma SADE — Nightly Backup (Decision #9)
# Backs up: FalkorDB dump, ledger files, Memory files
# Phase 1: Local backup with 7-day rotation
# Phase 2: DO Spaces upload (when credentials are configured)
set -euo pipefail

# ── Config ──
BACKUP_ROOT="/opt/seed-vault/memory_v1/backups"
TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
BACKUP_NAME="karma-backup-${TIMESTAMP}"
BACKUP_DIR="${BACKUP_ROOT}/${BACKUP_NAME}"
BACKUP_FILE="${BACKUP_ROOT}/${BACKUP_NAME}.tar.gz"
KEEP_DAYS=7
LOG_FILE="/opt/seed-vault/memory_v1/backups/karma-backup.log"

# DO Spaces (Phase 2 — uncomment and set when ready)
# DO_SPACES_BUCKET="karma-backups"
# DO_SPACES_REGION="nyc3"
# DO_SPACES_ENDPOINT="https://${DO_SPACES_REGION}.digitaloceanspaces.com"
# DO_SPACES_ACCESS_KEY=""
# DO_SPACES_SECRET_KEY=""

# Source paths
MEMORY_V1="/opt/seed-vault/memory_v1"
LEDGER_DIR="${MEMORY_V1}/ledger"
MEMORY_DIR="${MEMORY_V1}/Memory"

log() { echo "[BACKUP $(date -u +%H:%M:%S)] $1" | tee -a "${LOG_FILE}"; }

log "Starting nightly backup — ${TIMESTAMP}"
mkdir -p "${BACKUP_DIR}"

# ── 1. FalkorDB snapshot ──
log "Triggering FalkorDB BGSAVE..."
docker exec falkordb redis-cli BGSAVE 2>/dev/null || log "WARNING: BGSAVE command failed"
sleep 3
docker cp falkordb:/data/dump.rdb "${BACKUP_DIR}/falkordb-dump.rdb" 2>/dev/null || \
    log "WARNING: Could not copy FalkorDB dump"

# ── 2. PostgreSQL dump ──
log "Dumping PostgreSQL..."
docker exec anr-vault-db pg_dump -U memory memoryvault > "${BACKUP_DIR}/postgres-dump.sql" 2>/dev/null || \
    log "WARNING: PostgreSQL dump failed (may not exist)"

# ── 3. Ledger files ──
log "Copying ledger files..."
if [ -d "${LEDGER_DIR}" ]; then
    cp -r "${LEDGER_DIR}" "${BACKUP_DIR}/ledger"
    LEDGER_COUNT=$(find "${BACKUP_DIR}/ledger" -type f | wc -l)
    log "Ledger: ${LEDGER_COUNT} files"
else
    log "WARNING: Ledger directory not found at ${LEDGER_DIR}"
fi

# ── 4. Memory files ──
log "Copying memory files..."
if [ -d "${MEMORY_DIR}" ]; then
    cp -r "${MEMORY_DIR}" "${BACKUP_DIR}/Memory"
else
    log "WARNING: Memory directory not found at ${MEMORY_DIR}"
fi

# ── 5. Compose .env (contains API keys — critical for recovery) ──
log "Backing up compose .env..."
cp "${MEMORY_V1}/compose/.env" "${BACKUP_DIR}/compose-env.bak" 2>/dev/null || \
    log "WARNING: Could not backup compose .env"

# ── 6. Create tarball ──
log "Creating archive..."
cd "${BACKUP_ROOT}"
tar czf "${BACKUP_FILE}" "${BACKUP_NAME}/"
rm -rf "${BACKUP_DIR}"
BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
log "Archive: ${BACKUP_FILE} (${BACKUP_SIZE})"

# ── 7. Prune old local backups (keep last KEEP_DAYS days) ──
log "Pruning backups older than ${KEEP_DAYS} days..."
PRUNED=0
find "${BACKUP_ROOT}" -name "karma-backup-*.tar.gz" -mtime +${KEEP_DAYS} -type f | while read -r old; do
    log "Pruning: $(basename ${old})"
    rm -f "${old}"
    PRUNED=$((PRUNED + 1))
done
log "Pruned ${PRUNED} old backup(s)"

# ── 8. DO Spaces upload (Phase 2) ──
# Uncomment below after: (1) install aws-cli, (2) set credentials above
# if [ -n "${DO_SPACES_ACCESS_KEY:-}" ] && [ -n "${DO_SPACES_SECRET_KEY:-}" ]; then
#     log "Uploading to DO Spaces..."
#     AWS_ACCESS_KEY_ID="${DO_SPACES_ACCESS_KEY}" \
#     AWS_SECRET_ACCESS_KEY="${DO_SPACES_SECRET_KEY}" \
#     aws s3 cp "${BACKUP_FILE}" \
#         "s3://${DO_SPACES_BUCKET}/nightly/${BACKUP_NAME}.tar.gz" \
#         --endpoint-url "${DO_SPACES_ENDPOINT}" \
#         --no-progress
#     log "Upload complete"
# fi

# ── Summary ──
TOTAL_BACKUPS=$(ls -1 "${BACKUP_ROOT}"/karma-backup-*.tar.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "${BACKUP_ROOT}" 2>/dev/null | cut -f1)
log "Done. ${TOTAL_BACKUPS} backup(s) on disk (${TOTAL_SIZE} total)"
