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
LARGE_FILES=$(find . -type f -size +10M ! -path "./.git/*" ! -path "./.claude/worktrees/*" 2>/dev/null | wc -l)
if [ $LARGE_FILES -eq 0 ]; then
  echo "  ✅ PASS - No large files untracked"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "  ⚠️  WARN - Found $LARGE_FILES large files (>10MB)"
  echo "     Consider .gitignore or cleanup"
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
