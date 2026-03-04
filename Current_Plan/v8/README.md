# Karma v8 Plan — Making the House Learn

**Author:** Claude Code (CC)
**Date:** 2026-03-04
**Status:** GROUND TRUTH — Written from operational evidence, not aspiration

---

## Why v8?

v7 built the infrastructure. The house exists. But Karma doesn't know what house she lives in.

**The root problem discovered during this session:**
Karma's live system prompt (`Memory/00-karma-system-prompt-live.md` on vault-neo) describes a *different system* — an Open WebUI persona from Feb 2026 with tools like `gemini_query()`, `file_read()`, and `browser_open()`. These tools don't exist in the hub-bridge context she actually runs in.

Every conversation, Karma reconstructs herself from a system prompt that describes the wrong architecture. This is why she makes repeated data model errors. She's not confused — she's working from bad instructions.

**v7 left three things undone:**
1. System prompt was never updated to reflect the actual built system
2. Memory retrieval is blunt: 1800 chars of generic graph context per request
3. Corrections made in conversation disappear when the conversation ends

v8 fixes these in order. No new infrastructure. No new services. Fix what exists.

---

## What v8 Is NOT

- Not a new architecture
- Not a new service or container
- Not fine-tuning or DPO (that comes after foundation is solid)
- Not K2 integration (still deferred)
- Not a rewrite of the hub-bridge or karma-server

## What v8 IS

- Phase 1: Fix Karma's self-knowledge (rewrite her system prompt to describe reality)
- Phase 2: Fix retrieval quality (semantic search, query-targeted context)
- Phase 3: Fix correction persistence (what she learns in one session carries to the next)
- Phase 4: Refresh direction.md (stale since Feb 23 — Karma reads this)

---

## Files in This Plan

| File | Purpose |
|------|---------|
| `README.md` | This file — what v8 is and why |
| `CURRENT_STATE_AUDIT.md` | Honest gap analysis — what works, what's broken, what's lying |
| `CONTEXT.md` | Design decisions and hard constraints before any code is written |
| `PLAN.md` | Phased execution plan with atomic tasks and acceptance criteria |

---

## North Star (unchanged from v7)

> Karma is a single coherent peer whose long-term identity lives in a verified memory spine.

v8 makes this true in practice, not just in documentation.
