#!/bin/bash
# sync-from-vault.sh — K2 <-> vault-neo canonical state sync
# Usage: sync-from-vault.sh pull | push
#
# pull: copies identity files + ledger snapshot from vault-neo to local cache
# push: sends k2_local_observations.jsonl entries to vault-neo /v1/ambient API
#
# K2 cache: /mnt/c/dev/Karma/k2/cache/
# vault-neo Tailscale: root@100.92.67.70
#
# Cron:
#   0 */6 * * * /mnt/c/dev/Karma/k2/sync-from-vault.sh pull  >> /mnt/c/dev/Karma/k2/cache/.sync_log 2>&1
#   0 * * * *   /mnt/c/dev/Karma/k2/sync-from-vault.sh push  >> /mnt/c/dev/Karma/k2/cache/.sync_log 2>&1

set -euo pipefail

MODE="${1:-pull}"
VAULT_SSH="root@100.92.67.70"
VAULT_REPO="/home/neo/karma-sade"
VAULT_LEDGER="/opt/seed-vault/memory_v1/ledger/memory.jsonl"
CACHE="/mnt/c/dev/Karma/k2/cache"
LOG="$CACHE/.sync_log"

# Ensure cache dirs exist (idempotent)
mkdir -p "$CACHE"/{identity,ledger,graph,corrections,observations}

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
log() { echo "[$TS] $*" | tee -a "$LOG"; }

case "$MODE" in

  pull)
    log "PULL start"

    # Test vault-neo reachability first
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$VAULT_SSH" "echo ok" >/dev/null 2>&1; then
      log "PULL failed — vault-neo unreachable. Using cached state."
      exit 1
    fi

    # Identity spine (from git repo on vault-neo)
    rsync -az --no-perms --checksum \
      "$VAULT_SSH:$VAULT_REPO/identity.json"   "$CACHE/identity/" && log "  identity.json synced"
    rsync -az --no-perms --checksum \
      "$VAULT_SSH:$VAULT_REPO/invariants.json" "$CACHE/identity/" && log "  invariants.json synced"
    rsync -az --no-perms --checksum \
      "$VAULT_SSH:$VAULT_REPO/direction.md"    "$CACHE/identity/" && log "  direction.md synced"

    # Corrections log (may not exist yet — don't fail)
    rsync -az --no-perms --checksum \
      "$VAULT_SSH:$VAULT_REPO/Memory/corrections-log.md" \
      "$CACHE/corrections/" 2>/dev/null \
      && log "  corrections-log.md synced" \
      || log "  corrections-log.md not found (skipped)"

    # Ledger snapshot — last 500 entries only (<500MB constraint)
    ssh "$VAULT_SSH" "tail -500 $VAULT_LEDGER" > "$CACHE/ledger/memory.jsonl"
    LINES=$(wc -l < "$CACHE/ledger/memory.jsonl")
    log "  ledger snapshot: $LINES lines"

    # Record sync timestamp
    echo "$TS" > "$CACHE/.last_sync"
    log "PULL complete"
    ;;

  push)
    OBS="$CACHE/observations/k2_local_observations.jsonl"

    if [ ! -s "$OBS" ]; then
      log "PUSH skipped — no observations pending"
      exit 0
    fi

    COUNT=$(wc -l < "$OBS")
    log "PUSH start — $COUNT observations"

    # Fetch capture token from vault-neo (never stored locally)
    if ! TOKEN=$(ssh -o ConnectTimeout=5 -o BatchMode=yes "$VAULT_SSH" \
        "cat /opt/seed-vault/memory_v1/hub_auth/hub.capture.token.txt" 2>/dev/null); then
      log "PUSH failed — vault-neo unreachable, observations retained"
      exit 1
    fi

    SENT=0
    FAILED=0
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time 10 \
        -X POST https://hub.arknexus.net/v1/ambient \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$line")
      if [[ "$STATUS" =~ ^2 ]]; then
        SENT=$((SENT+1))
      else
        FAILED=$((FAILED+1))
        log "  WARN: /v1/ambient returned $STATUS"
      fi
    done < "$OBS"

    if [ "$FAILED" -eq 0 ]; then
      # Clear only after clean push — idempotent (safe to retry if partial)
      > "$OBS"
      log "PUSH complete — $SENT sent, file cleared"
    else
      log "PUSH partial — $SENT sent, $FAILED failed. File retained for retry."
      exit 1
    fi
    ;;

  status)
    echo "=== K2 Cache Status ==="
    if [ -f "$CACHE/.last_sync" ]; then
      LAST=$(cat "$CACHE/.last_sync")
      echo "Last pull: $LAST"
    else
      echo "Last pull: never"
    fi
    echo "Identity files:"
    for f in identity.json invariants.json direction.md; do
      [ -f "$CACHE/identity/$f" ] && echo "  $f: $(stat -c %y $CACHE/identity/$f 2>/dev/null)" || echo "  $f: MISSING"
    done
    echo "Ledger: $(wc -l < $CACHE/ledger/memory.jsonl 2>/dev/null || echo 0) entries"
    echo "Pending observations: $(wc -l < $CACHE/observations/k2_local_observations.jsonl 2>/dev/null || echo 0)"
    ;;

  *)
    echo "Usage: $0 pull|push|status" >&2
    exit 1
    ;;
esac
