#!/bin/bash
# Step 4.3: Ledger Rotation
# Monthly cron: gzip JSONL ledgers > 50K lines.
# Run: 0 3 1 * * /opt/seed-vault/memory_v1/tools/ledger_rotate.sh >> /opt/seed-vault/memory_v1/ledger/rotation.log 2>&1

VAULT_DIR="/opt/seed-vault/memory_v1"
ARCHIVE_DIR="/opt/seed-vault/backups/ledger_archive"
LOG_PREFIX="[LEDGER_ROTATE $(date -u +%Y-%m-%dT%H:%M:%SZ)]"
LINE_THRESHOLD=50000

mkdir -p "$ARCHIVE_DIR"

for LEDGER in "$VAULT_DIR"/ledger/*.jsonl "$VAULT_DIR"/*.jsonl; do
    [ -f "$LEDGER" ] || continue
    
    LINE_COUNT=$(wc -l < "$LEDGER" 2>/dev/null)
    if [ "$LINE_COUNT" -gt "$LINE_THRESHOLD" ] 2>/dev/null; then
        BASENAME=$(basename "$LEDGER")
        MONTH=$(date -u +%Y-%m)
        ARCHIVE_NAME="${BASENAME%.jsonl}_${MONTH}.jsonl.gz"
        
        echo "$LOG_PREFIX Rotating $BASENAME ($LINE_COUNT lines > $LINE_THRESHOLD threshold)"
        
        # Archive the file
        gzip -c "$LEDGER" > "$ARCHIVE_DIR/$ARCHIVE_NAME"
        
        if [ -f "$ARCHIVE_DIR/$ARCHIVE_NAME" ]; then
            # Truncate original to last 1000 lines (keep recent data)
            tail -1000 "$LEDGER" > "${LEDGER}.tmp"
            mv "${LEDGER}.tmp" "$LEDGER"
            
            NEW_COUNT=$(wc -l < "$LEDGER")
            echo "$LOG_PREFIX Archived to $ARCHIVE_NAME. Trimmed to $NEW_COUNT lines."
        else
            echo "$LOG_PREFIX ERROR: Archive failed for $BASENAME"
        fi
    fi
done

echo "$LOG_PREFIX Rotation complete."
