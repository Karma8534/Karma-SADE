#!/usr/bin/env bash
# build_hub.sh — Safeguarded hub-bridge Docker build
#
# Enforces correct build context (hub-bridge root, NOT app/).
# Running from inside app/ is a known pitfall that causes lib/ to be unreachable.
#
# Usage (from hub-bridge/):
#   ./build_hub.sh              — full build, tag hub-bridge:latest
#   ./build_hub.sh --dry-run    — print the command, do not execute
#   ./build_hub.sh --tag myapp:v2  — custom tag
#
# Deployment pattern (vault-neo):
#   cd /opt/seed-vault/memory_v1/hub_bridge && ./build_hub.sh
#   docker compose -f compose.hub.yml up -d hub-bridge

set -euo pipefail

# ── Pre-flight: reject if run from inside app/ ────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CWD="$(pwd)"

# Normalise: strip trailing slash
CWD="${CWD%/}"

if [[ "$CWD" == */app ]]; then
  echo "[ERROR] build_hub.sh was called from inside app/:" >&2
  echo "        $CWD" >&2
  echo "[ERROR] The build context must be the hub-bridge root (parent of app/)." >&2
  echo "        Run: cd .. && ./build_hub.sh" >&2
  exit 1
fi

# ── Validate that we're in a hub-bridge root (app/Dockerfile must exist) ──────
if [[ ! -f "$CWD/app/Dockerfile" ]]; then
  echo "[ERROR] app/Dockerfile not found in current directory:" >&2
  echo "        $CWD" >&2
  echo "[ERROR] Run build_hub.sh from the hub-bridge root directory." >&2
  exit 1
fi

# ── Parse args ────────────────────────────────────────────────────────────────
DRY_RUN=0
TAG="hub-bridge:latest"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)   DRY_RUN=1 ;;
    --tag)       shift; TAG="$1" ;;
    --tag=*)     TAG="${1#--tag=}" ;;
    *)           echo "[WARN] Unknown arg: $1" >&2 ;;
  esac
  shift
done

# ── Build ─────────────────────────────────────────────────────────────────────
CMD="docker build -f app/Dockerfile -t $TAG ."

if [[ $DRY_RUN -eq 1 ]]; then
  echo "[DRY-RUN] $CMD"
  echo "[DRY-RUN] Context: $CWD"
  exit 0
fi

echo "[BUILD] Context : $CWD"
echo "[BUILD] Command : $CMD"
$CMD
echo "[BUILD] Done    : $TAG"
