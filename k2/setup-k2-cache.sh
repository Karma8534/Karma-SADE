#!/bin/bash
# setup-k2-cache.sh — One-time K2 cache bootstrap
# Run once on K2 after git pull to initialize cache + install cron
# Usage: bash /mnt/c/dev/Karma/k2/setup-k2-cache.sh

set -euo pipefail

CACHE="/mnt/c/dev/Karma/k2/cache"
SCRIPT="/mnt/c/dev/Karma/k2/sync-from-vault.sh"
VAULT_SSH="root@100.92.67.70"

echo "=== K2 Cache Setup ==="

# 1. Create cache directory structure
echo "[1/5] Creating cache directories..."
mkdir -p "$CACHE"/{identity,ledger,graph,corrections,observations}
touch "$CACHE/observations/k2_local_observations.jsonl"
touch "$CACHE/.sync_log"
echo "      $CACHE/ created"

# 2. Make sync script executable
chmod +x "$SCRIPT"
echo "[2/5] sync-from-vault.sh marked executable"

# 3. Test vault-neo SSH
echo "[3/5] Testing vault-neo SSH (root@100.92.67.70)..."
if ssh -o ConnectTimeout=8 -o BatchMode=yes "$VAULT_SSH" "echo vault-neo OK" 2>/dev/null; then
  echo "      vault-neo reachable"
else
  echo "      ERROR: Cannot reach vault-neo. Check Tailscale + SSH keys."
  echo "      Run: ssh root@100.92.67.70 manually to debug"
  exit 1
fi

# 4. Run initial pull
echo "[4/5] Running initial pull from vault-neo..."
bash "$SCRIPT" pull
echo "      Initial pull complete"

# 5. Install cron jobs (idempotent — removes existing entries first)
echo "[5/5] Installing cron jobs..."
CRON_PULL="0 */6 * * * $SCRIPT pull >> $CACHE/.sync_log 2>&1"
CRON_PUSH="0 * * * * $SCRIPT push >> $CACHE/.sync_log 2>&1"

(crontab -l 2>/dev/null | grep -v "sync-from-vault"; \
 echo "$CRON_PULL"; echo "$CRON_PUSH") | crontab -

echo "      Installed:"
crontab -l | grep sync-from-vault

echo ""
echo "=== Setup Complete ==="
echo "Cache: $CACHE"
echo "Last sync: $(cat $CACHE/.last_sync 2>/dev/null || echo 'none')"
echo ""
echo "Verify:"
echo "  bash $SCRIPT status"
echo "  cat $CACHE/identity/identity.json | python3 -m json.tool | head -10"
