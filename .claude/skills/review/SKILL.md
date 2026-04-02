---
name: review
description: Show current session state — active task, hierarchy, health, blockers — without executing anything. Use when Colby types /review or "what's the state?" or "where are we?" before deciding what to work on.
---

# Review — Session State Surface (No Execution)

Surface current state clearly. Do NOT execute any task. Do NOT invoke brainstorming. Do NOT start work.

## Output this block, populated with real current values:

```
══════════════════════════════════════════════
 KARMA SESSION STATE
══════════════════════════════════════════════
 Active task  : [task-id Step N — description from MEMORY.md item 2]
 Sprint item  : [first incomplete item in PLAN.md CURRENT SPRINT]
 Match?       : [YES — aligned / NO DRIFT — MEMORY says X, PLAN says Y]

 Hierarchy    : SOVEREIGN: Colby | ASCENDANT: CC | KO: Codex | KFH: KCC | INITIATE: Karma

 Health       : [containers OK / any flags from last resurrect check]
 K2           : [spine version, stable patterns count]
 Blockers     : [from STATE.md — list or "none"]

 PLAN-A       : [A1/A2/A3 status]
 PLAN-B       : [B1-B4 status]
 PLAN-C       : [C1-C4 status]
 PROOF-A      : [Task 1-4 status]

 Last commit  : [git log -1 --oneline]
 Session files: [N unprocessed in ccSessions/]
══════════════════════════════════════════════
 Say "go" to execute active task, or redirect.
══════════════════════════════════════════════
```

## Steps

1. Read `MEMORY.md` → "Current State" section (active task, session, blocker) + "Open Blockers" section
2. Read `Karma2/PLAN.md` → "Backlog Status" table for current sprint items
3. Read `.gsd/STATE.md` → get phase and blockers
4. Read `.gsd/ROADMAP.md` head 30 → get milestone status
5. Run `git log -1 --oneline` for last commit
6. Output the block above with real values
7. STOP. Do not execute anything. Wait for Colby to direct.

## Rules

- This skill NEVER starts work
- NEVER ends with tool calls that execute tasks
- NEVER invokes brainstorming
- Use in place of `/resurrect` when Colby wants to see state without starting a session
- After outputting the block: respond to questions, but do not start executing the active task unless Colby explicitly says "go" or "start" or "execute"
