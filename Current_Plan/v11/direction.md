# Direction — What We're Building

**Last updated:** 2026-03-11
**Status:** v11 — Aria/K2 integration complete (Session 81). MODEL_DEEP=claude-sonnet-4-6. System fully operational.

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
| **K2 / Aria** | Karma's local compute half (100.75.109.92). Ollama :11434 (qwen3-coder:30b MoE), Aria service :7890 | ✅ Operational |
| **aria_local_call** | hub-bridge tool → K2:7890/api/chat. Service key auth. Observations sync to /v1/ambient. session_id threaded. | ✅ Live (Session 81) |
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

## What Changed: Sessions 73–81

| Session | Key Change |
|---------|-----------|
| 74 | get_vault_file extended (repo/+vault/ prefixes); get_local_file tool; karma-file-server.ps1 |
| 75 | Model switch to Haiku 3.5; lib/*.js committed to git; backend-only verification ≠ green |
| 77 | Cognitive architecture layer design (Self-Model Kernel, Metacognitive Trace, Deferred Intent Engine) |
| 78-80 | Deferred Intent Engine live; session amnesia fix (MAX_SESSION_TURNS 8→20); file upload |
| 81 | MODEL_DEEP=claude-sonnet-4-6; K2/Aria integration (delegated fix, vault sync, session_id); $60 cap; subscription cleanup |

---

## Current Constraints

- FalkorDB: 10s timeout, vault-neo:6379
- Ledger: 4000+ episodes
- System prompt: ~18,200 chars (Session 81 load confirmed) — monitor for token pressure
- MODEL_DEFAULT: claude-haiku-4-5-20251001 (standard, fast/cheap, no tools)
- MODEL_DEEP: claude-sonnet-4-6 (deep, tools, peer-quality — $0.0252/req)
- Monthly cap: $60 (MONTHLY_USD_CAP in hub.env)
- PRICE_CLAUDE: ❌ needs update to Sonnet rates ($3/$15 per 1M)
- DPO pairs: accumulation in progress — needs regular Karma usage with 👍/👎

---

## What Is NOT Operational

- Chrome extension (shelved — DOM scraping unreliable)
- Karma terminal (last capture 2026-02-27, stale)
- Ambient Tier 3 (screen capture daemon — not yet built)
- JPG/PNG vision: code deployed but falls through to extractPdfText() — needs Anthropic multimodal fix
- Paste in Karma UI: works everywhere except hub.arknexus.net — suspected Cloudflare CSP
