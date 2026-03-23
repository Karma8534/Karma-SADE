---
name: karma-pitfall-resurrect
description: Auto-synthesized from HARVEST. Pattern seen in 8+ sessions. Invoke when working with resurrect skill, session start, or CC identity continuity.
type: feedback
---

## Rule
Resurrect must cross-check PLAN.md CURRENT SPRINT (not just MEMORY.md item 2) and EXECUTE the first task immediately — no questions, no announcements without tool calls.

**Why:** MEMORY.md item 2 drifted from PLAN.md sprint in at least 6 sessions (Sessions 119-132). CC repeatedly started wrong tasks, asked unnecessary questions, or stopped after announcing "Starting now" without making tool calls (B001).

**How to apply:** At Step 5, read PLAN.md CURRENT SPRINT. If it conflicts with MEMORY.md: PLAN.md wins. Then make the first tool call IN THE SAME RESPONSE as the announcement.

## Evidence

- **Session 118 (ccKarma2-1.md)**: B001 — CC announced "Executing K-2 Task 1" and terminated. No tool calls followed.
- **Session 119 (ccKarma2-2.md)**: P043 — Brief said "K2 Unavailable". CC skipped SSH verification. K2 was fully reachable via SSH the whole time.
- **Session 120 (ccKarma2-3.md)**: 7 resurrect root causes identified. Step 5 annotation "[immediately executes item 2]" was prose, not instruction.
- **Session 121 (ccKarma2-4.md)**: MEMORY.md said "K-3 per PLAN.md". PLAN.md CURRENT SPRINT showed E-1-A next. CC had to re-investigate.
- **Session 128 (ccKarma2-7.md)**: MEMORY.md said "K-1 Step 1: IndexedDB". PLAN.md said K-1 DONE. Drift undetected until Step 5 cross-check added.
- **Session 132 (ccKarma2-10.md)**: B001 confirmed again — CC output full status block and asked "Ready. What would you like to work on?"
- **ccSession032026-FULLMETA.md**: Resume execution after resurrect = the task is the next response, not a menu.

## Hard rules
- Step 1b: ALWAYS run direct SSH to K2 regardless of what the brief says about K2 status
- Step 5: Read PLAN.md CURRENT SPRINT → compare to MEMORY.md item 2 → PLAN.md wins on conflict
- Step 5 execution: The first tool call for the active task happens IN this response — not in the next one
- Never end resurrect with "Ready. What would you like to work on?"
