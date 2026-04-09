#!/bin/bash
# PRE-COMPACT FLUSH HOOK — Emergency save before context compaction
# Ported from MemPalace mempal_precompact_hook.sh (nexus 5.6.0, obs #25022)
#
# Claude Code "PreCompact" hook. ALWAYS blocks.
# Forces emergency state dump before context window shrinks.
#
# Install: registered in .claude/settings.local.json hooks.PreCompact

STATE_DIR="$HOME/.mempalace/hook_state"
mkdir -p "$STATE_DIR"

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null || echo "unknown")

echo "[$(date '+%H:%M:%S')] PRE-COMPACT triggered for session $SESSION_ID" >> "$STATE_DIR/hook.log"

# Always block — compaction = save everything
cat << 'HOOKJSON'
{
  "decision": "block",
  "reason": "COMPACTION IMMINENT. Save ALL DECISION/PROOF/PITFALL/DIRECTION/INSIGHT events to MEMORY.md and claude-mem NOW. Update .gsd/STATE.md with current progress. Be thorough — after compaction, detailed context will be lost. Save everything, then allow compaction to proceed."
}
HOOKJSON
