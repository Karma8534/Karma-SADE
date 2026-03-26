---
name: dream
description: "Memory consolidation — cleans MEMORY.md, resolves contradictions, prunes stale entries, rebuilds index under 200 lines. Run after long sessions or when memory feels bloated. Triggers: /dream, 'consolidate memory', 'clean up memory', 'dream'."
---

# Dream — Memory Consolidation for Karma SADE

You are performing a dream — a reflective consolidation pass over Julian/Karma's memory files.
The goal: future sessions orient in seconds, not minutes. No stale facts. No contradictions. No bloat.

## Phase 1 — Orient (read everything, touch nothing)

1. Read `MEMORY.md` (full file — know what's there)
2. Read `.gsd/STATE.md` (current active task, phase, blockers)
3. Read `.gsd/ROADMAP.md` (milestone status)
4. Read `.gsd/karma-directives.md` (behavioral directives)
5. Read `Karma2/map/active-issues.md` (open vs closed issues)
6. Search claude-mem for recent observations (last 20, project=Karma_SADE)
7. Note: what session numbers are referenced? What's the latest?

**Output a mental model** (not printed to user): what is current, what is stale, what contradicts.

## Phase 2 — Gather Signal (find problems)

For each entry in MEMORY.md, check:
- **Stale sessions**: Is this session note >7 days old AND not the most recent 5 sessions? → candidate for archival
- **Resolved blockers**: Does the entry mention a blocker that active-issues.md shows as CLOSED? → delete the blocker text
- **Contradictions**: Does MEMORY.md say X but STATE.md or active-issues.md says NOT X? → fix MEMORY.md
- **Relative dates**: "next session", "yesterday", "soon" → convert to absolute dates or delete if past
- **Stale infrastructure**: References to services/PIDs/uptimes that are certainly outdated → remove specifics, keep facts
- **Duplicate information**: Same fact stated in multiple places → keep the most recent, remove duplicates

Also check:
- `karma-directives.md` Learned Rules section — any rules that contradict current plan? Remove them.
- `cc_context_snapshot.md` if it exists — is it stale? Delete if >24h old.

## Phase 3 — Consolidate (make changes)

**MEMORY.md restructure:**
```
# Karma SADE — Active Memory
<!-- Last dream: YYYY-MM-DD Session NNN -->

## Current State (updated by dream)
- Active task: [from STATE.md]
- Current blocker: [from STATE.md]
- Session: [latest session number]
- Julian = TRUE: [persistent memory + self-eval + self-improvement + learning + evolving]

## Architecture Quick Reference
[Keep the infrastructure table — it's stable and useful]
[Keep the model routing table — update if changed]

## Recent Sessions (last 5 only)
[Session N]: [one-line summary]
[Session N-1]: [one-line summary]
...

## Known Pitfalls (active only — remove resolved)
[Keep only pitfalls that are STILL active per active-issues.md]

## Memory Index
[Keep file-based memory index pointers — these are stable]
```

**Rules:**
- MEMORY.md MUST be under 200 lines after consolidation
- Session notes older than 5 sessions → archive summary to claude-mem observation, delete from MEMORY.md
- Every entry must have an absolute date, not relative
- Infrastructure facts (IPs, ports, paths) stay — they're stable reference
- Session-specific debugging notes go — they're ephemeral

**karma-directives.md:**
- Remove any Learned Rules that reference resolved issues
- Keep Active Directives intact (Sovereign-written)

## Phase 4 — Prune and Index

1. Rebuild MEMORY.md with the structure above
2. Count lines — if >200, cut oldest session summaries first
3. Update the `<!-- Last dream -->` comment with today's date and session
4. Save an observation to claude-mem: `[DREAM] Consolidated MEMORY.md: [what changed]`
5. Print summary to user:
   - Lines before → lines after
   - Entries removed (with reason)
   - Contradictions resolved
   - Stale facts cleaned

## Scoped Runs

- `/dream` — consolidate project MEMORY.md only (default)
- `/dream full` — also consolidate karma-directives.md + STATE.md alignment check
- `/dream user` — consolidate user-level memory at `~/.claude/MEMORY.md` (if exists)

## When to Run

- After any session longer than 30 exchanges
- When MEMORY.md exceeds 200 lines
- When resurrect takes >60s (sign of bloated memory)
- When you notice contradictions in memory during a session
- At Sovereign request

## What NOT to Do

- Never delete the Memory Index section (file pointers are stable)
- Never delete infrastructure facts (IPs, ports, paths)
- Never delete Sovereign directives from karma-directives.md
- Never consolidate without reading STATE.md first (need to know what's active)
- Never archive the current session's notes (only older sessions)
