#!/bin/bash
# Karma SADE — Nightly Backup to DO Spaces (Decision #9)
# Backs up: FalkorDB data, ledger files, Memory files, self-model
# Target: DO Spaces (S3-compatible) ~$1/mo
set -euo pipefail

# ── Config from environment ──
DO_SPACES_BUCKET="${DO_SPACES_BUCKET:-karma-backups}"
DO_SPACES_REGION="${DO_SPACES_REGION:-nyc3}"
DO_SPACES_ENDPOINT="https://${DO_SPACES_REGION}.digitaloceanspaces.com"
DO_SPACES_ACCESS_KEY="${DO_SPACES_ACCESS_KEY:-}"
DO_SPACES_SECRET_KEY="${DO_SPACES_SECRET_KEY:-}"
BACKUP_DIR="/tmp/karma-backup"
TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
BACKUP_NAME="karma-backup-${TIMESTAMP}"
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Source paths (on the host / inside container)
MEMORY_V1="/opt/seed-vault/memory_v1"
LEDGER_DIR="${MEMORY_V1}/ledger"
MEMORY_DIR="${MEMORY_V1}/Memory"

echo "[BACKUP] Starting nightly backup — ${TIMESTAMP}"

# ── Preflight ──
if [ -z "${DO_SPACES_ACCESS_KEY}" ] || [ -z "${DO_SPACES_SECRET_KEY}" ]; then
    echo "[BACKUP] ERROR: DO_SPACES_ACCESS_KEY and DO_SPACES_SECRET_KEY must be set"
    echo "[BACKUP] Skipping upload — creating local backup only"
    UPLOAD=false
else
    UPLOAD=true
fi

mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# ── 1. Export FalkorDB data ──
echo "[BACKUP] Exporting FalkorDB graph..."
# Use redis-cli BGSAVE to trigger a snapshot, then copy the dump
docker exec anr-vault-db redis-cli BGSAVE 2>/dev/null || true
sleep 3
# Copy the RDB file from the FalkorDB container
docker cp anr-vault-db:/data/dump.rdb "${BACKUP_DIR}/${BACKUP_NAME}/falkordb-dump.rdb" 2>/dev/null || \
    echo "[BACKUP] WARNING: Could not export FalkorDB dump"

# ── 2. Copy ledger files ──
echo "[BACKUP] Copying ledger files..."
cp -r "${LEDGER_DIR}" "${BACKUP_DIR}/${BACKUP_NAME}/ledger" 2>/dev/null || \
    echo "[BACKUP] WARNING: Ledger directory not found"

# ── 3. Copy memory files ──
echo "[BACKUP] Copying memory files..."
cp -r "${MEMORY_DIR}" "${BACKUP_DIR}/${BACKUP_NAME}/Memory" 2>/dev/null || \
    echo "[BACKUP] WARNING: Memory directory not found"

# ── 4. Copy token usage ──
cp "${LEDGER_DIR}/token_usage.json" "${BACKUP_DIR}/${BACKUP_NAME}/" 2>/dev/null || true

# ── 5. Create tarball ──
echo "[BACKUP] Creating archive..."
cd "${BACKUP_DIR}"
tar czf "${BACKUP_FILE}" "${BACKUP_NAME}/"
BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
echo "[BACKUP] Archive: ${BACKUP_FILE} (${BACKUP_SIZE})"

# ── 6. Upload to DO Spaces ──
if [ "${UPLOAD}" = true ]; then
    echo "[BACKUP] Uploading to DO Spaces: ${DO_SPACES_BUCKET}/${BACKUP_NAME}.tar.gz"
    # Use aws cli with DO Spaces endpoint (S3-compatible)
    AWS_ACCESS_KEY_ID="${DO_SPACES_ACCESS_KEY}" \
    AWS_SECRET_ACCESS_KEY="${DO_SPACES_SECRET_KEY}" \
    aws s3 cp "${BACKUP_FILE}" \
        "s3://${DO_SPACES_BUCKET}/nightly/${BACKUP_NAME}.tar.gz" \
        --endpoint-url "${DO_SPACES_ENDPOINT}" \
        --no-progress
    echo "[BACKUP] Upload complete"

    # ── 7. Prune old backups (keep last 7 days) ──
    echo "[BACKUP] Pruning backups older than 7 days..."
    CUTOFF=$(date -u -d '7 days ago' +%Y%m%d 2>/dev/null || date -u -v-7d +%Y%m%d)
    AWS_ACCESS_KEY_ID="${DO_SPACES_ACCESS_KEY}" \
    AWS_SECRET_ACCESS_KEY="${DO_SPACES_SECRET_KEY}" \
    aws s3 ls "s3://${DO_SPACES_BUCKET}/nightly/" \
        --endpoint-url "${DO_SPACES_ENDPOINT}" 2>/dev/null | \
    while read -r line; do
        FILE=$(echo "$line" | awk '{print $NF}')
        FILE_DATE=$(echo "$FILE" | grep -o '[0-9]\{8\}' | head -1)
        if [ -n "${FILE_DATE}" ] && [ "${FILE_DATE}" -lt "${CUTOFF}" ] 2>/dev/null; then
            echo "[BACKUP] Pruning: ${FILE}"
            AWS_ACCESS_KEY_ID="${DO_SPACES_ACCESS_KEY}" \
            AWS_SECRET_ACCESS_KEY="${DO_SPACES_SECRET_KEY}" \
            aws s3 rm "s3://${DO_SPACES_BUCKET}/nightly/${FILE}" \
                --endpoint-url "${DO_SPACES_ENDPOINT}"
        fi
    done
else
    echo "[BACKUP] Upload skipped (no DO Spaces credentials)"
fi

# ── Cleanup local temp ──
rm -rf "${BACKUP_DIR}/${BACKUP_NAME}"
echo "[BACKUP] Done. Backup: ${BACKUP_FILE}"
