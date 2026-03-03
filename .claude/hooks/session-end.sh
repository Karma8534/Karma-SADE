#!/bin/bash
# Ambient Knowledge Layer — Tier 1b: CC session-end → Vault ledger
# Posts session metadata to the vault when a Claude Code session ends.
# Non-blocking: failures are silent.

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | python -c "import sys,json; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null || echo "unknown")
REASON=$(echo "$INPUT" | python -c "import sys,json; print(json.load(sys.stdin).get('reason','unknown'))" 2>/dev/null || echo "unknown")

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
ID="amb_cc_session_${SESSION_ID:0:12}_$(date +%s)"

# Get git context
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
LAST_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")

PAYLOAD=$(cat <<ENDJSON
{
  "id": "${ID}",
  "type": "log",
  "tags": ["capture", "claude-code", "session-end", "${BRANCH}"],
  "content": {
    "source": "claude-code",
    "source_node": "P1",
    "summary": "CC session ended (${REASON}): branch ${BRANCH} at ${LAST_HASH}",
    "detail": {
      "session_id": "${SESSION_ID}",
      "reason": "${REASON}",
      "branch": "${BRANCH}",
      "last_commit": "${LAST_HASH}",
      "total_commits": "${COMMIT_COUNT}"
    },
    "captured_at": "${TIMESTAMP}"
  },
  "source": {"kind": "tool", "ref": "ambient:claude-code"},
  "confidence": 1.0,
  "verification": {
    "protocol_version": "v1",
    "verified_at": "${TIMESTAMP}",
    "verifier": "ambient-cc-session-hook",
    "status": "verified",
    "notes": "Auto-captured from CC session-end hook on P1"
  }
}
ENDJSON
)

# POST to vault via SSH (same path as git hook)
ssh vault-neo "curl -s -X POST http://127.0.0.1:8080/v1/memory \
  -H 'Content-Type: application/json' \
  -d '${PAYLOAD}'" > /dev/null 2>&1 &

exit 0
