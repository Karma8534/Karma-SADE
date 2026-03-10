# Direction — What We're Building

**Last updated:** 2026-03-10
**Status:** v10 COMPLETE — All 5 priorities shipped (Session 72). System fully operational.

---

## Mission

Karma is a single coherent peer whose long-term identity lives in a verified memory spine. That memory enables continuity, evidence-based self-improvement, and selective delegation — without parallel sources of truth.

---

## Architecture (Current — hub-bridge + FalkorDB)

| Component | Role | Status |
|-----------|------|--------|
| **vault-neo** | Karma's persistent home (DigitalOcean NYC3, 4GB RAM) | ✅ Running |
| **anr-hub-bridge** | API surface: /v1/chat, /v1/ambient, /v1/ingest, /v1/feedback | ✅ Running |
| **karma-server** | Consciousness loop (OBSERVE-only, 60s cycles, zero LLM calls) | ✅ Running |
| **FalkorDB** | Graph: `neo_workspace` — 3200+ Episodic + 570 Entity nodes | ✅ Running |
| **Ledger** | `/opt/seed-vault/memory_v1/ledger/memory.jsonl` — 4000+ entries, append-only | ✅ Growing |
| **anr-vault-search (FAISS)** | Custom search_service.py — FAISS + text-embedding-3-small, 4000+ entries | ✅ Live |
| **batch_ingest** | Cron every 6h, --skip-dedup mode (FIXED Session 70) | ✅ Scheduled |
| **PDF watcher** | `karma-inbox-watcher.ps1` → /v1/ingest (rate-limit aware, jam detection) | ✅ Active |
| **Brave Search** | Auto-triggered on search intent, top-3 results injected into context | ✅ Enabled |
| **K2 local worker** | DEPRECATED 2026-03-03 — not operational, not needed | ❌ Shelved |
| **Chrome extension** | SHELVED permanently — DOM scraping unreliable | ❌ Shelved |

---

## Active Tool Suite (Deep Mode)

| Tool | Handler | Purpose |
|------|---------|---------|
| `graph_query(cypher)` | karma-server proxy | Query FalkorDB neo_workspace |
| `get_vault_file(alias)` | hub-bridge native | Read canonical files (MEMORY.md, system-prompt, etc.) |
| `write_memory(content)` | hub-bridge native | Propose MEMORY.md append (requires 👍 approval) |
| `fetch_url(url)` | hub-bridge native | Fetch live web content (8KB cap, HTML stripped) |
| `get_library_docs(library)` | hub-bridge native | Fetch library documentation (redis-py, falkordb, falkordb-py, fastapi) |

---

## v10 Milestones — COMPLETE

All 5 priorities shipped in Session 72:

1. ✅ **Universal thumbs** — 👍/👎 on ALL Karma messages via turn_id fallback (Decision #26)
2. ✅ **MEMORY.md spine injection** — tail 3000 chars in every /v1/chat (Decision #21)
3. ✅ **MENTIONS co-occurrence** — live Entity Relationships replacing frozen RELATES_TO (Decision #22)
4. ✅ **Confidence levels** — [HIGH]/[MEDIUM]/[LOW] mandatory; [LOW] = hard stop (Decisions #23, #24)
5. ✅ **get_library_docs** — DIY library doc tool, Context7 rejected (Decision #25)

---

## What Changed: Sessions 66–72

| Session | Key Change |
|---------|-----------|
| 66 | GLM tool-calling live; graph_query + get_vault_file; TOOL_NAME_MAP bug fixed |
| 67 | Deep-mode tool gate; standard chat no longer gets tools |
| 68 | write_memory gate; /v1/feedback; 👍/👎 on memory writes; DPO pairs |
| 69 | fetch_url tool; stale tools removed (read_file, write_file, edit_file, bash) |
| 70 | System prompt trim (16K→11K chars); batch_ingest --skip-dedup permanent; context lag note |
| 71 | (Not recorded — likely minor fixes) |
| 72 | v10 all 5 priorities complete (see above) |

---

## Current Constraints

- FalkorDB: 10s timeout, vault-neo:6379
- Ledger: 4000+ episodes
- System prompt: 15,192 chars — monitor for token pressure (429s above ~13K chars were the signal)
- GLM_RPM_LIMIT: 40 RPM (Z.ai free tier)
- DPO pairs: 0/20 goal — needs regular use with 👍/👎 feedback

---

## What Is NOT Operational

- Chrome extension (shelved — DOM scraping unreliable)
- Karma terminal (last capture 2026-02-27, stale)
- Ambient Tier 3 (screen capture daemon — not yet built)
- DPO pair accumulation: mechanism LIVE but 0 pairs collected — needs actual Karma usage
