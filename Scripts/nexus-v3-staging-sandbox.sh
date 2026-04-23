#!/bin/bash
# P-FU5 Nexus V3.0 merge: Vesper staging sandbox chroot
# Creates /opt/seed-vault/memory_v1/hub_bridge/staging for self-edit candidates BEFORE they touch live proxy.js.
# node --check gates staging writes; only on pass can promote to live.
set -euo pipefail

STAGING=/opt/seed-vault/memory_v1/hub_bridge/staging
LIVE_DIR=/opt/seed-vault/memory_v1/hub_bridge/app
MODE="${1:-init}"

case "$MODE" in
  init)
    if [ -d "$STAGING" ]; then echo "staging exists: $STAGING"; exit 0; fi
    mkdir -p "$STAGING/app"
    cp "$LIVE_DIR/proxy.js" "$STAGING/app/proxy-stage.js"
    cp -r "$LIVE_DIR/public" "$STAGING/app/public"
    cp "$LIVE_DIR/package.json" "$STAGING/app/" 2>/dev/null || true
    # Write-lock live dir metadata (doesn't block root but signals intent)
    chmod -R a-w "$STAGING" 2>/dev/null || true
    chmod -R u+w "$STAGING"
    echo "staging initialized at $STAGING (proxy-stage.js write-root-only)"
    ;;
  stage)
    # stage <source-path> writes into /staging/app/
    SRC="${2:?stage requires source path}"
    DEST="$STAGING/app/$(basename "$SRC")"
    cp "$SRC" "$DEST"
    echo "staged $SRC -> $DEST"
    # Gate: node --check
    if ! node --check "$DEST"; then
      echo "STAGE REJECTED: node --check failed"
      rm -f "$DEST"
      exit 1
    fi
    echo "stage-check PASS"
    ;;
  promote)
    # Promote staged file to live after verification
    STAGED="$STAGING/app/proxy-stage.js"
    if [ ! -f "$STAGED" ]; then echo "no staged proxy-stage.js"; exit 2; fi
    if ! node --check "$STAGED"; then echo "PROMOTE REJECTED: staged fails node --check"; exit 3; fi
    BACKUP="$LIVE_DIR/proxy.js.pre-promote-$(date -u +%Y%m%dT%H%M%SZ)"
    cp "$LIVE_DIR/proxy.js" "$BACKUP"
    cp "$STAGED" "$LIVE_DIR/proxy.js"
    echo "promoted $STAGED -> $LIVE_DIR/proxy.js (backup: $BACKUP)"
    ;;
  diff)
    diff -u "$LIVE_DIR/proxy.js" "$STAGING/app/proxy-stage.js" || true
    ;;
  *)
    echo "usage: $0 {init|stage <src>|promote|diff}"
    exit 1
    ;;
esac
