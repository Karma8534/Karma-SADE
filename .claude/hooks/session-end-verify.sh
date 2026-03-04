#!/bin/bash
# SESSION-END VERIFICATION GATE: Ensure all work is documented, deployed, and saved
# Purpose: Verify before session ends that no work is lost
# Failure: Exits 1 with checklist of what's missing. User must fix before ending session.

set -e

FAIL=0
CHECKS_PASSED=0
CHECKS_TOTAL=0

echo ""
echo "🔍 SESSION-END VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# CHECK 1: Git status clean (no uncommitted changes)
echo ""
echo "CHECK 1: Git status clean?"
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if git diff --quiet && git diff --cached --quiet; then
  echo "  ✅ PASS - No uncommitted changes"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "  ❌ FAIL - Uncommitted changes exist"
  echo "     Run: git add [files] && git commit"
  FAIL=1
fi

# CHECK 2: MEMORY.md recently updated
echo ""
echo "CHECK 2: MEMORY.md recently updated?"
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if [ -f "MEMORY.md" ]; then
  MEMORY_MTIME=$(stat -f%m "MEMORY.md" 2>/dev/null || stat -c%Y "MEMORY.md" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  AGE=$((NOW - MEMORY_MTIME))
  if [ $AGE -lt 3600 ]; then
    echo "  ✅ PASS - MEMORY.md updated ${AGE}s ago"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
  else
    echo "  ⚠️  WARN - MEMORY.md not updated recently (${AGE}s ago)"
    echo "     Consider updating MEMORY.md with session summary"
  fi
else
  echo "  ❌ FAIL - MEMORY.md not found"
  FAIL=1
fi

# CHECK 3: Git log has recent commit
echo ""
echo "CHECK 3: Recent git commits exist?"
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
LAST_COMMIT=$(git log --oneline -1 2>/dev/null | head -1 || echo "")
if [ ! -z "$LAST_COMMIT" ]; then
  echo "  ✅ PASS - Last commit: $LAST_COMMIT"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "  ⚠️  WARN - No git history found (fresh repo?)"
fi

# CHECK 4: Branch is correct
echo ""
echo "CHECK 4: On correct branch?"
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
if [[ "$BRANCH" == "main" || "$BRANCH" == "feature/"* || "$BRANCH" == "develop" ]]; then
  echo "  ✅ PASS - Branch: $BRANCH"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "  ⚠️  WARN - Branch: $BRANCH (verify correct)"
fi

# CHECK 5: No large uncommitted files
echo ""
echo "CHECK 5: No large untracked files?"
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
LARGE_FILES=$(find . -type f -size +10M ! -path "./.git/*" ! -path "./.claude/worktrees/*" 2>/dev/null \
  | while read -r f; do git check-ignore -q "$f" 2>/dev/null || echo "$f"; done \
  | wc -l)
if [ $LARGE_FILES -eq 0 ]; then
  echo "  ✅ PASS - No large files untracked"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "  ⚠️  WARN - Found $LARGE_FILES large files (>10MB)"
  echo "     Consider .gitignore or cleanup"
fi

# CHECK 6: Droplet git state clean (CRITICAL — prevents droplet drift)
echo ""
echo "CHECK 6: Droplet (vault-neo) git state clean?"
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
DROPLET_STATUS=$(ssh vault-neo "cd /home/neo/karma-sade && git status --short" 2>/dev/null)
DROPLET_BRANCH=$(ssh vault-neo "cd /home/neo/karma-sade && git rev-parse --abbrev-ref HEAD" 2>/dev/null)
DROPLET_HEAD=$(ssh vault-neo "cd /home/neo/karma-sade && git rev-parse --short HEAD" 2>/dev/null)
LOCAL_HEAD=$(git rev-parse --short HEAD 2>/dev/null)
if [ -z "$DROPLET_STATUS" ] && [ "$DROPLET_HEAD" = "$LOCAL_HEAD" ]; then
  echo "  ✅ PASS - Droplet clean, HEAD matches ($DROPLET_HEAD)"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
elif [ -z "$DROPLET_STATUS" ] && [ "$DROPLET_HEAD" != "$LOCAL_HEAD" ]; then
  echo "  ❌ FAIL - Droplet clean but HEAD diverged"
  echo "     Droplet: $DROPLET_HEAD  Local: $LOCAL_HEAD"
  echo "     Run: ssh vault-neo 'cd /home/neo/karma-sade && git pull origin main'"
  FAIL=1
else
  echo "  ❌ FAIL - Droplet has uncommitted changes:"
  echo "$DROPLET_STATUS" | sed 's/^/     /'
  echo "     Fix: ssh vault-neo 'cd /home/neo/karma-sade && git stash'"
  echo "     OR commit them on droplet then push — but NEVER edit on droplet directly again"
  FAIL=1
fi

# CHECK 7: No abandoned worktrees
echo ""
echo "CHECK 7: No abandoned worktrees?"
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
WT_COUNT=$(git worktree list 2>/dev/null | tail -n +2 | wc -l)
if [ "$WT_COUNT" -eq 0 ]; then
  echo "  ✅ PASS - No open worktrees"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "  ⚠️  WARN - $WT_COUNT open worktrees (prune before next session)"
  echo "     Run: git worktree list && git worktree remove --force <path>"
fi

# SUMMARY
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY: $CHECKS_PASSED/$CHECKS_TOTAL checks passed"

if [ $FAIL -eq 0 ]; then
  echo "✅ SESSION READY TO END"
  echo ""
  echo "Next session will:"
  echo "  1. Run Get-KarmaContext.ps1 to load session context"
  echo "  2. Read MEMORY.md for current state"
  echo "  3. Resume from last task"
  echo ""
  exit 0
else
  echo "❌ CANNOT END SESSION - FIX ABOVE ISSUES"
  echo ""
  echo "Action required:"
  echo "  • Commit all changes: git add . && git commit"
  echo "  • Update MEMORY.md with session progress"
  echo "  • Then run session-end again"
  echo ""
  exit 1
fi
