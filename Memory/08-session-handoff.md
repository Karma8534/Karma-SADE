# Karma SADE — Session Handoff

**Date**: 2026-03-10
**Session**: 72
**GitHub**: https://github.com/Karma8534/Karma-SADE (PUBLIC)
**Last commit**: 0c15d35 (main, synced to vault-neo)

---

## System Architecture (Current)

```
PAYBACK (Windows 11, i9-185H, 64GB RAM, RTX 4070 8GB)
└── Claude Code ─── development environment

vault-neo (DigitalOcean NYC3, 4GB RAM, SSH alias: vault-neo)
├── anr-hub-bridge        ─── port 18090 (internal) / hub.arknexus.net (public HTTPS)
│   ├── /v1/chat          ─── Karma conversation endpoint
│   ├── /v1/ambient       ─── Git hook + session-end capture
│   ├── /v1/ingest        ─── PDF/media ingestion
│   ├── /v1/context       ─── Context query
│   ├── /v1/cypher        ─── Direct graph query
│   └── /v1/feedback      ─── write_memory + universal thumbs (Sessions 68+72)
├── karma-server          ─── Python consciousness loop + tool execution
│   ├── OBSERVE-only, 60s cycles, zero LLM calls
│   ├── execute_tool_action(): graph_query (only proxied tool — others handled in hub-bridge directly)
│   └── batch_ingest: cron every 6h, --skip-dedup mode (FIXED Session 70)
├── FalkorDB              ─── Graph: neo_workspace (3200+ Episodic + 570 Entity nodes)
├── anr-vault-api         ─── FastAPI, appends to JSONL ledger
├── anr-vault-search      ─── FAISS vector search (text-embedding-3-small, 4000+ entries)
└── Nginx                 ─── Reverse proxy → hub.arknexus.net
```

**Models:**
- Primary: GLM-4.7-Flash (Z.ai) — ~80% requests, free, 40 RPM self-imposed
- Deep mode: gpt-4o-mini (OpenAI) — `x-karma-deep: true` header only, paid

---

## Critical File Locations

| What | Path |
|------|------|
| Hub-bridge source | `/home/neo/karma-sade/hub-bridge/app/server.js` |
| Hub-bridge build context | `/opt/seed-vault/memory_v1/hub_bridge/app/server.js` (must sync after git pull) |
| Hub-bridge lib/ | `/opt/seed-vault/memory_v1/hub_bridge/lib/` (PARENT dir — not under app/) |
| Karma-server source | `/home/neo/karma-sade/karma-core/server.py` |
| Karma-server build context | `/opt/seed-vault/memory_v1/karma-core/server.py` (must sync after git pull) |
| Hub env | `/opt/seed-vault/memory_v1/hub_bridge/config/hub.env` |
| Compose (hub) | `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml` |
| Compose (vault) | `/opt/seed-vault/memory_v1/compose/compose.yml` |
| Ledger | `/opt/seed-vault/memory_v1/ledger/memory.jsonl` |
| Batch watermark | `/opt/seed-vault/memory_v1/ledger/.batch_watermark` |
| Hub chat token | `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt` |
| System prompt | `/home/neo/karma-sade/Memory/00-karma-system-prompt-live.md` |
| MEMORY.md (vault) | `/home/neo/karma-sade/MEMORY.md` (also `/karma/MEMORY.md` in hub-bridge container) |

---

## What Changed in Session 72

### v10 Priority #1 — Universal Thumbs (turn_id)
- `/v1/feedback` now accepts `turn_id` OR `write_id` (write_id takes priority)
- `processFeedback()` extended with 5th param `turn_id`; `dpo_pair` records turn_id
- `unified.html` gate changed from `if (writeId)` to `if (writeId || turnId)`
- `addMessage()` now stores `dataset.turnId`; `sendFeedback()` builds payload with correct ID
- **All Karma messages now have 👍/👎 buttons** — not just write_memory proposals
- Decision #26

### v10 Priority #2 — MEMORY.md Spine Injection
- `_memoryMdCache`: tail 3000 chars of MEMORY.md, refreshed every 5min
- Injected as "KARMA MEMORY SPINE (recent)" section — 5th param to `buildSystemText()`
- Karma was previously context-blind to her own MEMORY.md — this is now fixed
- `hub-bridge/tests/test_system_text.js`: 6 tests covering inject/guard logic (all pass)

### v10 Priority #3 — Entity Relationships Fix (MENTIONS co-occurrence)
- `query_relevant_relationships()` was using frozen `RELATES_TO` edges (1,423 edges, all from 2026-03-04 — Chrome extension era, never updated)
- Fixed to MENTIONS cross-join (Episodic→Entity co-occurrence, cocount >= 2)
- Decision #22 — RELATES_TO edges must never be used for live relationship data

### v10 Priority #4 — Confidence Levels + Anti-Hallucination Gate
- Mandatory `[HIGH]`/`[MEDIUM]`/`[LOW]` labels on claims in system prompt
- [LOW] = hard stop, run `get_library_docs` or `graph_query` before answering
- Decisions #23, #24

### v10 Priority #5 — get_library_docs Tool
- `hub-bridge/lib/library_docs.js`: `LIBRARY_URLS` map + `resolveLibraryUrl()`
- 4 libraries: redis-py, falkordb, falkordb-py, fastapi
- Hub-bridge-native (no hooks.py ALLOWED_TOOLS update needed)
- Deep mode only; reuses fetch_url HTML strip + 8KB cap
- Context7 API rejected: 100 API calls/day free tier + per-call latency overhead vs near-zero DIY cost (Decision #25)
- `hub-bridge/tests/test_library_docs.js`: 7 tests (all pass)

### System Prompt
- 15,192 chars (was 11,674 after Session 70 trim)
- Added: get_library_docs tool doc, library docs coaching, updated anti-hallucination gate
- Deployed via `docker restart anr-hub-bridge` (no rebuild needed — system prompt is file-loaded)

### Hub-Bridge Pitfall Discovered (Decision #27)
- ALL changed files must be synced to build context parent `/opt/.../hub_bridge/`, not just server.js
- `lib/*.js` → `/opt/.../hub_bridge/lib/`; `app/public/*.html` → `/opt/.../hub_bridge/app/public/`
- Lesson: the `karma-hub-deploy` skill must be updated to list all file categories to sync

---

## Current State (All Verified 2026-03-10 Session 72)

| Component | Status |
|-----------|--------|
| /v1/chat | ✅ ok — MEMORY.md spine + MENTIONS co-occurrence + confidence levels live |
| System prompt | ✅ 15,192 chars — get_library_docs coaching + anti-hallucination gate |
| Universal thumbs | ✅ LIVE — all Karma messages get 👍/👎 via turn_id (Session 72) |
| MEMORY.md spine injection | ✅ LIVE — tail 3000 chars injected into every /v1/chat (Session 72) |
| Entity Relationships | ✅ FIXED — MENTIONS co-occurrence (RELATES_TO permanently frozen, never use) |
| get_library_docs | ✅ LIVE — deep mode, hub-bridge-native, 4 libraries |
| confidence levels | ✅ LIVE — [HIGH]/[MEDIUM]/[LOW] mandatory in system prompt |
| batch_ingest cron | ✅ --skip-dedup PERMANENT |
| hub-bridge | ✅ RestartCount=0, current version |
| fetch_url tool | ✅ LIVE (Session 69) |
| write_memory + /v1/feedback | ✅ LIVE — pending_writes gate + DPO pairs (Session 68) |
| Deep-mode tool gate | ✅ standard chat no longer gets tools (Session 67) |
| graph_query / get_vault_file | ✅ LIVE (Session 66) |
| FAISS semantic search | ✅ LIVE (Session 62) |

---

## Next Session (Session 73)

**Current state of v10:** All 5 priorities COMPLETE. System fully operational.

**Options:**
1. **DPO pair accumulation**: Goal is 20 pairs in ledger. Use Karma in deep mode with regular 👍/👎. No code needed — just accumulate naturally.
2. **Context7 re-evaluation**: If get_library_docs proves insufficient, Context7 can be reconsidered. But wait for evidence first.
3. **New v10 priorities**: Check `.gsd/ROADMAP.md` for Session 73 direction (v10 complete — may start v11 planning)

**First command at session start:**
```
/resurrect
```

---

## Known Pitfalls (Active — Must Not Forget)

1. **Hub-bridge multi-file sync** — after `git pull` on vault-neo, must sync ALL changed file categories: server.js → `app/`, lib/*.js → parent `lib/`, app/public/*.html → `app/public/`. The `karma-hub-deploy` skill lists server.js only — remember lib/ and public/ too.
2. **hub-bridge lib/ files go at PARENT level** — `/opt/.../hub_bridge/lib/` NOT under `app/lib/`
3. **hooks.py ALLOWED_TOOLS** — new proxied tools silently rejected without whitelist entry (hub-bridge-native tools don't need this)
4. **TOOL_NAME_MAP must stay empty** — any entries remap tool names to wrong values
5. **docker restart ≠ compose up -d** — hub.env changes require `compose up -d`; system prompt changes need only `docker restart`
6. **FalkorDB graph name is `neo_workspace`** — NOT `karma`
7. **RELATES_TO edges permanently frozen at 2026-03-04** — 1,423 edges, never updated. Use MENTIONS co-occurrence cross-join for live relationship data. Never query RELATES_TO.
8. **vault-api type enum is closed** — use type:"log" + tags for custom types; type:"dpo-pair" returns 422 silently
9. **buildVaultRecord() required for all vault writes** — bare objects fail schema validation silently
10. **batch_ingest cron MUST use --skip-dedup** — Graphiti mode silently fails at scale
11. **MEMORY.md spine is tail 3000 chars** — very long MEMORY.md = older content not visible to Karma
