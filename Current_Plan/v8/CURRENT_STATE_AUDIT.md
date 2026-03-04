# Current State Audit — What's True vs. What the Docs Say

**Date:** 2026-03-04
**Method:** Direct inspection of running system + file reads + session evidence

---

## Infrastructure (Operational — verified sessions 57-61)

| Component | Status | Evidence |
|-----------|--------|----------|
| hub-bridge API | ✅ Running | `/v1/chat`, `/v1/ambient`, `/v1/ingest`, `/v1/context`, `/v1/cypher` all responding |
| karma-server | ✅ Running | RestartCount=0. Rebuilt session 60. |
| FalkorDB `neo_workspace` | ✅ Running | 3621 nodes (3049 Episodic + 571 Entity + 1 Decision) |
| Ledger `memory.jsonl` | ✅ Growing | 4000+ entries. Active cron every 6h. |
| Consciousness loop | ✅ Running | OBSERVE-only, 60s cycles, zero LLM calls |
| GLM Rate Limiter | ✅ Live | 20 RPM, 429 on burst, waitForSlot on ingest |
| Config Validation Gate | ✅ Live | Bad MODEL_DEFAULT/DEEP = exit(1) on startup |
| PDF Ingestion pipeline | ✅ Working | karma-inbox-watcher.ps1 → /v1/ingest → ledger |
| batch_ingest cron | ✅ Scheduled | Every 6h, --skip-dedup, 899 eps/s |
| ChromaDB | ⚠️ Running but stale | Vector index not recently updated |
| Chrome Extension | ❌ Shelved | Never worked reliably. Permanent. |

---

## What Karma's System Prompt Actually Says (vault-neo, right now)

File: `/home/neo/karma-sade/Memory/00-karma-system-prompt-live.md`

**It describes:**
- "You are Karma, Neo's autonomous AI architect on PAYBACK (Windows 11)"
- Tools: `gemini_query()`, `browser_open()`, `file_read()`, `shell_run()`, `system_info()`
- References: Open WebUI at localhost:8080, Ollama, Cockpit at localhost:9400
- Memory entries as key-value pairs from Feb 2026

**Reality:** None of these tools exist in the hub-bridge context. When Karma talks via `/v1/chat`, she has NO access to local machine tools, no browser, no shell. She gets GLM-4.7-Flash + up to 1800 chars of FalkorDB context. That's it.

**Impact:** Every conversation, Karma starts with wrong self-knowledge. She thinks she has tools she doesn't have. She doesn't know she's on vault-neo. She doesn't know what FalkorDB is or how it works. She doesn't know the PDF watcher architecture.

---

## Memory/ Docs on the Droplet — Age and Accuracy

| File | Last updated | Describes | Accurate? |
|------|-------------|-----------|-----------|
| `00-karma-system-prompt-live.md` | ~2026-02-12 | Open WebUI persona + local tools | ❌ Wrong system |
| `01-core-architecture.md` | ~2026-02-12 | Open WebUI, Ollama, Sentinel | ❌ Predates current arch |
| `02-stable-decisions.md` | ~2026-02-12 | Folder conventions, Open WebUI workflow | ❌ Stale |
| `04-session-learnings.md` | ~2026-02-12 | Early Open WebUI session facts | ❌ Stale |
| `11-session-summary-latest.md` | Unknown | Unknown | Likely stale |
| `direction.md` (repo root) | 2026-02-23 | Feb 23 architectural intent | ⚠️ Stale (10+ days) |
| `MEMORY.md` (repo root) | 2026-03-04 | Current session work | ✅ Current |

**Conclusion:** The Memory/ directory is an archaeological record, not a current knowledge base. The most current source of truth is MEMORY.md (CC's mutable state) and STATE.md (.gsd/).

---

## What "Context Injection" Actually Does Today

When Colby sends a message to `/v1/chat`:

1. hub-bridge queries FalkorDB for recent episodes (limited by `KARMA_CTX_MAX_CHARS=1800`)
2. Appends that context to Karma's system prompt
3. Sends the full prompt to GLM-4.7-Flash
4. Returns the response

**What 1800 chars of FalkorDB context looks like in practice:**
- Maybe 3-5 recent episode summaries
- Generic — not targeted to the question being asked
- No semantic relevance — just recency

**What's missing:**
- Query-aware retrieval: "what do I know that's relevant to THIS question?"
- Semantic similarity search against the full 4000+ ledger entries
- ChromaDB vector search is deployed but not being used here

---

## The Three Core Gaps

### Gap 1: Karma's Self-Knowledge Is Wrong
**Symptom:** Karma searches ledger for `.verdict.txt` files. Asks to check local Windows filesystem. Doesn't know her own architecture.
**Root cause:** System prompt describes a different, old system.
**Fix:** Rewrite `00-karma-system-prompt-live.md` to describe the actual hub-bridge + FalkorDB system.

### Gap 2: Retrieval Is Blunt
**Symptom:** 1800 chars of generic recent-episode context. Karma doesn't "remember" relevant things — she remembers recent things.
**Root cause:** Context injection uses recency, not relevance.
**Fix:** Add semantic search layer. When a question arrives, retrieve the K most semantically relevant ledger entries, not just the most recent.

### Gap 3: Corrections Don't Persist
**Symptom:** Karma makes the same data model errors session after session. Corrections made in conversation are lost when the conversation ends.
**Root cause:** No mechanism to capture corrections → update system prompt.
**Fix:** Session-end protocol: CC identifies corrections → appends to system prompt → deploys.

---

## What's Working Well (Don't Touch)

- The ledger pipeline (git hooks → /v1/ambient → ledger) is solid
- GLM routing, rate limiting, config validation — all working
- batch_ingest cron — working, --skip-dedup is correct
- PDF ingestion (watcher → /v1/ingest → ledger) — working
- FalkorDB growth — working

These are not the problem. Don't rebuild them.

---

## Summary

Karma has a house she can't navigate. She has 4000+ memories she mostly can't access. She starts each conversation thinking she's someone else. v8 fixes this — not by building more rooms, but by giving her a correct map, a better way to find what she knows, and a way to remember what she learns.
