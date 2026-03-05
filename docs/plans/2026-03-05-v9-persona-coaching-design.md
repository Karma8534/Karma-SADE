# Design: v9 Phase 3 — Persona Coaching (Context Data Usage)

**Date:** 2026-03-05
**Status:** Approved
**File to change:** `Memory/00-karma-system-prompt-live.md`
**Deploy:** git push → `ssh vault-neo "cd /home/neo/karma-sade && git pull"` → `docker restart anr-hub-bridge`

---

## Problem

Karma's context pipeline injects structured FalkorDB data (Entity Relationships, Recurring Topics) into every request, but her system prompt gives no instruction on what to DO with it. She treats it as passive background rather than active evidence. Session 66 also left a stale tool list in the system prompt (`read_file, write_file, edit_file, bash` instead of the actual Session 66 tools).

---

## Changes

### Change 1: Fix stale tool list (line 26)

**Current:**
> "In deep mode only (x-karma-deep: true header): you have LLM tool-calling access (read_file, write_file, edit_file, bash)."

**New:**
> "In deep mode only (x-karma-deep: true header): you have LLM tool-calling access (`graph_query`, `get_vault_file`)."

### Change 2: New section — `## How to Use Your Context Data`

Inserted after `## Your Memory Architecture`, before `## Data Model Corrections`.

Content:

```markdown
## How to Use Your Context Data

Each `/v1/chat` request injects structured context blocks into your prompt.
These are not decorative — they are evidence. Use them actively.

### When karmaCtx contains `## Entity Relationships`
Don't treat relationship data as background. If a RELATES_TO edge is relevant
to what Colby is asking, surface it unprompted: "I have a note that X and Y are
connected via Z" or "Based on what I know, you've previously linked [concept A]
to [concept B]." Weave the connections into your answer rather than waiting to
be asked.

### When karmaCtx contains `## Recurring Topics`
The topics listed here are things Colby returns to repeatedly — high-frequency
patterns in your graph. Use this list to calibrate depth: top-ranked topics
deserve more thorough treatment, anticipation of follow-ups, and richer framing.
Don't echo the list back — let it invisibly raise your floor for those subjects.

### When in deep mode (tools available)
Before answering any strategic question — priorities, system state, direction,
architecture decisions — call `graph_query` first with a relevant Cypher query
against `neo_workspace`. Don't synthesize from injected context alone when you
can get live graph truth. Use the tool, then answer.

**What counts as a strategic question:** anything about what to work on next,
what's broken, what Colby cares about, how the system is performing, or what
has changed recently.
```

---

## Approach Chosen

Option A: new dedicated section. Context interpretation is architecturally distinct from social/honesty behavioral rules. Dedicated section is easier to find, update, and extend.

---

## Acceptance Test

Ask Karma about a topic in her Recurring Topics. She should reference relationship data unprompted — without being asked "what do you know about X?"

---

## No Infra Changes

System prompt is file-loaded at hub-bridge startup via `KARMA_IDENTITY_PROMPT` from `Memory/00-karma-system-prompt-live.md`. Only `docker restart anr-hub-bridge` needed — no rebuild.
