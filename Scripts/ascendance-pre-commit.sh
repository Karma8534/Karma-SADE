#!/bin/bash
# Ascendance pre-commit hook -- plan v2 Phase 4.2 + directive v3 G10.
# 1) Scope whitelist for ascendance-run commits.
# 2) Two-pass secret scan (excludes tests/fixtures/, Logs/).
# 3) ascendance-run commits require MEMORY.md staged + contains current SESSION_ID.
# 4) Banned-label scan in evidence/** + MEMORY.md Ascendance section.
# Non-ascendance commits: only secret scan + MEMORY.md-touched gate.
set -euo pipefail

STAGED=$(git diff --cached --name-only)
if [ -z "$STAGED" ]; then exit 0; fi

WHITELIST_META='^(\.git/|\.claude/worktrees/|\.gitignore$|MEMORY\.md$|cc-session-brief\.md$)'
MEM_NEEDED=0
while IFS= read -r f; do
  if ! echo "$f" | grep -qE "$WHITELIST_META"; then MEM_NEEDED=1; break; fi
done <<< "$STAGED"

ASCENDANCE_MODE=0
if echo "$STAGED" | grep -qE '^evidence/(ascendance-run-|ascendance-dry-run-)'; then ASCENDANCE_MODE=1; fi
if echo "$STAGED" | grep -qE '^\.gsd/phase-ascendance-.*-SUMMARY\.md$'; then ASCENDANCE_MODE=1; fi
COMMIT_MSG_FILE=".git/COMMIT_EDITMSG"
if [ -f "$COMMIT_MSG_FILE" ]; then
  FIRST_LINE=$(head -n 1 "$COMMIT_MSG_FILE" 2>/dev/null || echo '')
  if echo "$FIRST_LINE" | grep -qE '^(ascendance-run|feat\(ascendance-run\))'; then ASCENDANCE_MODE=1; fi
fi

SECRET_REGEX='(Bearer [A-Za-z0-9_\-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_\-]{35}|ghp_[0-9A-Za-z]{36}|sk-[0-9A-Za-z]{32,}|-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|"password"\s*:\s*"[^"]{6,}"|"api_key"\s*:\s*"[^"]{8,}")'
SECRET_EXCLUDE='(^tests/fixtures/|^Logs/|^\.git/|\.pyc$|\.lock$)'
SECRET_HITS=0
while IFS= read -r f; do
  if echo "$f" | grep -qE "$SECRET_EXCLUDE"; then continue; fi
  if [ ! -f "$f" ]; then continue; fi
  if git diff --cached -- "$f" | grep -aE "$SECRET_REGEX" >/dev/null 2>&1; then
    echo "SECRET MATCH in: $f"
    SECRET_HITS=$((SECRET_HITS+1))
  fi
done <<< "$STAGED"
if [ "$SECRET_HITS" -gt 0 ]; then
  echo ""
  echo "PRE-COMMIT FAIL: secret pattern detected in $SECRET_HITS file(s). Remove before committing."
  exit 1
fi

if [ "$ASCENDANCE_MODE" -eq 0 ]; then
  if [ "$MEM_NEEDED" -eq 1 ] && ! echo "$STAGED" | grep -qE '^MEMORY\.md$'; then
    echo "PRE-COMMIT FAIL: code staged without MEMORY.md update. Stage MEMORY.md or mark commit as ascendance-run."
    exit 1
  fi
  exit 0
fi

SCOPE_WHITELIST_RE='^(evidence/ascendance-run-[^/]+/|evidence/ascendance-dry-run-[^/]+/|evidence/plan-run-[^/]+/|MEMORY\.md$|\.gsd/phase-ascendance-.*-SUMMARY\.md$|\.gsd/phase-ascendance-.*-PLAN\.md$|\.gsd/phase-ascendance-.*-CONTEXT\.md$|\.gsd/ascendance-build-checkpoint\.json$|Karma2/cc-scope-index\.md$|Karma2/PLAN\.md$|Karma2/PLAN-ARCHIVED-.*\.md$|Scripts/phase[0-9].*-harness\.ps1$|Scripts/ascendance-.*\.ps1$|Scripts/ritual-recorder\.ps1$|Scripts/install-ascendance-hooks\.ps1$|Scripts/leveldb_latest\.ps1$|Scripts/cc_server_p1\.py$|Scripts/test_cc_server_atomic_rename\.py$|Scripts/ascendance-pre-commit\.sh$|Scripts/nexus_consistency_check\.py$|\.claude/hooks/arknexus-tracker\.py$|\.claude/hooks/pre-commit$|Tests/ascendance/.*\.ps1$|frontend/src/.*\.(tsx|ts|css)$|docs/ForColby/ascendance-.*\.md$|nexus-tauri/src-tauri/.*\.(rs|toml)$)'
OFFSCOPE=0
while IFS= read -r f; do
  if ! echo "$f" | grep -qE "$SCOPE_WHITELIST_RE"; then
    echo "OUT-OF-SCOPE: $f"
    OFFSCOPE=$((OFFSCOPE+1))
  fi
done <<< "$STAGED"
if [ "$OFFSCOPE" -gt 0 ]; then
  echo ""
  echo "PRE-COMMIT FAIL: $OFFSCOPE path(s) outside ascendance-run commit scope. G10 whitelist enforced."
  exit 1
fi

if ! echo "$STAGED" | grep -qE '^MEMORY\.md$'; then
  echo "PRE-COMMIT FAIL: ascendance-run commit missing staged MEMORY.md."
  exit 1
fi
SID=""
CKPT=".gsd/ascendance-build-checkpoint.json"
if [ -f "$CKPT" ]; then
  SID=$(grep -oE '"session_id"\s*:\s*"[^"]*"' "$CKPT" | head -n 1 | sed -E 's/.*"([^"]*)"$/\1/' || echo '')
fi
if [ -z "$SID" ]; then
  SESS_FILE=$(ls evidence/plan-run-*/session.json 2>/dev/null | head -n 1 || echo '')
  if [ -n "$SESS_FILE" ]; then
    SID=$(grep -oE '"session_id"\s*:\s*"[^"]*"' "$SESS_FILE" | head -n 1 | sed -E 's/.*"([^"]*)"$/\1/' || echo '')
  fi
fi
if [ -n "$SID" ]; then
  if ! grep -qF "$SID" MEMORY.md; then
    echo "PRE-COMMIT FAIL: MEMORY.md does not contain SESSION_ID=$SID. Update Ascendance Run section."
    exit 1
  fi
fi

BANNED_HITS=0
TMP_MEM=$(mktemp)
awk '/^## Ascendance Run /,/^## /' MEMORY.md > "$TMP_MEM" || true
if [ -s "$TMP_MEM" ]; then
  H=$(grep -cEi '\b(inferred|likely|should|probably|close enough|done-ish|implied|assumed|effectively|essentially|in practice|approximately|basically|mostly|seems|appears to|close to|near enough)\b' "$TMP_MEM" || echo 0)
  BANNED_HITS=$((BANNED_HITS + H))
fi
rm -f "$TMP_MEM"
while IFS= read -r f; do
  if echo "$f" | grep -qE '^evidence/'; then
    if [ -f "$f" ]; then
      H=$(grep -cEi '\b(inferred|likely|should|probably|close enough|done-ish|implied|assumed|effectively|essentially|in practice|approximately|basically|mostly|seems|appears to|close to|near enough)\b' "$f" || echo 0)
      BANNED_HITS=$((BANNED_HITS + H))
    fi
  fi
done <<< "$STAGED"
if [ "$BANNED_HITS" -gt 0 ]; then
  echo "PRE-COMMIT FAIL: banned label hits=$BANNED_HITS in evidence/** or MEMORY.md Ascendance section."
  exit 1
fi

exit 0
