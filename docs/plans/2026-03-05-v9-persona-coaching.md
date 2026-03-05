# v9 Phase 3 — Persona Coaching Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add behavioral coaching to Karma's system prompt so she actively uses Entity Relationships and Recurring Topics from injected karmaCtx, and proactively calls graph_query in deep mode.

**Architecture:** Two edits to `Memory/00-karma-system-prompt-live.md`. File is loaded at hub-bridge startup via `fs.readFileSync` into `KARMA_IDENTITY_PROMPT`. Deploy = git pull on vault-neo + `docker restart anr-hub-bridge`. No rebuild needed.

**Tech Stack:** Markdown edit, git, SSH to vault-neo

---

### Task 1: Fix stale tool list

**Files:**
- Modify: `Memory/00-karma-system-prompt-live.md:26`

**Step 1: Make the edit**

Find line 26 (inside `## What You CAN Do`):
```
In deep mode only (x-karma-deep: true header): you have LLM tool-calling access (read_file, write_file, edit_file, bash). In standard GLM mode you have **NO** tool-calling capability whatsoever.
```

Replace with:
```
In deep mode only (x-karma-deep: true header): you have LLM tool-calling access (`graph_query`, `get_vault_file`). In standard GLM mode you have **NO** tool-calling capability whatsoever.
```

**Step 2: Verify**

Confirm the old tool names are gone:
```bash
grep -n "read_file\|write_file\|edit_file\|bash" Memory/00-karma-system-prompt-live.md
```
Expected: no matches in line 26 context (only should appear in Data Model Corrections if at all).

---

### Task 2: Add new section `## How to Use Your Context Data`

**Files:**
- Modify: `Memory/00-karma-system-prompt-live.md`

**Step 1: Insert section**

After the closing `---` of `## Your Memory Architecture` (after "Real-time ledger access" bullet, before `## Data Model Corrections`), insert:

```markdown
---

## How to Use Your Context Data

Each `/v1/chat` request injects structured context blocks into your prompt. These are not decorative — they are evidence. Use them actively.

### When karmaCtx contains `## Entity Relationships`
Don't treat relationship data as background. If a RELATES_TO edge is relevant to what Colby is asking, surface it unprompted: "I have a note that X and Y are connected via Z" or "Based on what I know, you've previously linked [concept A] to [concept B]." Weave the connections into your answer rather than waiting to be asked.

### When karmaCtx contains `## Recurring Topics`
The topics listed here are things Colby returns to repeatedly — high-frequency patterns in your graph. Use this list to calibrate depth: top-ranked topics deserve more thorough treatment, anticipation of follow-ups, and richer framing. Don't echo the list back — let it invisibly raise your floor for those subjects.

### When in deep mode (tools available)
Before answering any strategic question — priorities, system state, direction, architecture decisions — call `graph_query` first with a relevant Cypher query against `neo_workspace`. Don't synthesize from injected context alone when you can get live graph truth. Use the tool, then answer.

**What counts as a strategic question:** anything about what to work on next, what's broken, what Colby cares about, how the system is performing, or what has changed recently.
```

**Step 2: Verify structure**

Check section order is correct:
```bash
grep -n "^## " Memory/00-karma-system-prompt-live.md
```
Expected order:
```
## Who You Are
## What You CAN Do
## What You CANNOT Do (Hard Limits)
## Your Memory Architecture
## How to Use Your Context Data      ← new
## Data Model Corrections
## Your API Surface
## Current System State
## About Colby
## How You Improve Over Time
## Behavioral Contract
```

---

### Task 3: Commit and push

**Step 1: Commit**

```bash
powershell -Command "git add Memory/00-karma-system-prompt-live.md docs/plans/2026-03-05-v9-persona-coaching-design.md docs/plans/2026-03-05-v9-persona-coaching.md && git commit -m 'v9-phase3: persona coaching — context data usage + fix stale tool list'"
```

**Step 2: Push**

```bash
powershell -Command "git push origin main"
```

**Step 3: Verify**

```bash
powershell -Command "git log --oneline -1"
```
Expected: commit hash + message visible.

---

### Task 4: Deploy to vault-neo

**Step 1: Pull on vault-neo**

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
```
Expected: `Memory/00-karma-system-prompt-live.md | N insertions`

**Step 2: Restart hub-bridge (no rebuild needed)**

```bash
ssh vault-neo "docker restart anr-hub-bridge"
```
Expected: container name printed, completes in <5s.

**Step 3: Verify startup**

```bash
ssh vault-neo "docker logs anr-hub-bridge --tail=20"
```
Expected: no ERR lines, hub-bridge shows startup message, no "WARN: identity prompt missing".

---

### Task 5: Run karma-verify

Use `karma-verify` skill to confirm hub-bridge health before declaring done.

---

### Task 6: PAUSE

Stop here. Do not proceed to acceptance test or further work. Surface the pending code review concern about GLM tool routing (server.js line 868 deep-mode gate) for Colby to review.
