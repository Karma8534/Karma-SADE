# Karma SADE — Session Handoff

**Date**: 2026-03-05
**Session**: 67
**GitHub**: https://github.com/Karma8534/Karma-SADE (PUBLIC)
**Last commit**: ed9adfe (main, synced to vault-neo)

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
│   └── /v1/cypher        ─── Direct graph query
├── karma-server          ─── Python consciousness loop + tool execution
│   ├── OBSERVE-only, 60s cycles, zero LLM calls
│   ├── execute_tool_action(): graph_query, get_vault_file, read_file, write_file, edit_file, bash
│   └── batch_ingest: cron every 6h, Graphiti watermark mode
├── FalkorDB              ─── Graph: neo_workspace (3621+ nodes)
├── anr-vault-api         ─── FastAPI, appends to JSONL ledger
├── anr-vault-search      ─── FAISS vector search (text-embedding-3-small, 4073+ entries)
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
| Karma-server source | `/home/neo/karma-sade/karma-core/server.py` |
| Karma-server build context | `/opt/seed-vault/memory_v1/karma-core/server.py` (must sync after git pull) |
| Hub env | `/opt/seed-vault/memory_v1/hub_bridge/config/hub.env` |
| Compose (hub) | `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml` |
| Compose (vault) | `/opt/seed-vault/memory_v1/compose/compose.yml` |
| Ledger | `/opt/seed-vault/memory_v1/ledger/memory.jsonl` |
| Hub chat token | `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt` |
| System prompt | `/home/neo/karma-sade/Memory/00-karma-system-prompt-live.md` |
| MEMORY.md (vault) | `/home/neo/karma-sade/MEMORY.md` (also accessible at `/karma/MEMORY.md` in hub-bridge container) |

---

## What Changed in Session 67

### Code Changes (deployed)
1. `hub-bridge/app/server.js` (commit 41b2c06):
   - Lines 1269-1272: `deep_mode ? callLLMWithTools() : callLLM()` — standard chat no longer gets tools
   - Removed stale DIAGNOSTIC log left from Session 66 debugging
2. `Memory/00-karma-system-prompt-live.md` (commit f90cea7):
   - Line 26: fixed stale tool list (read_file/write_file → graph_query/get_vault_file)
   - New section "How to Use Your Context Data": behavioral coaching for Entity Relationships, Recurring Topics, deep-mode graph_query proactivity
   - KARMA_IDENTITY_PROMPT: 10,415 → 11,850 chars

---

## What Changed in Session 66

### Code Changes (merged to main, deployed)
1. `hub-bridge/app/server.js`:
   - Line 868: `callLLM()` → `callGPTWithTools(messages, maxTokens, model)` — GLM gets tool definitions
   - Line 413: False tool declaration replaced with accurate deep-mode-gated tool list
   - `TOOL_DEFINITIONS`: added `graph_query` + `get_vault_file`
   - `TOOL_NAME_MAP`: was `{read_file: "file_read", ...}` (wrong) → `{}` (identity passthrough)
   - `executeToolCall()`: direct handler for `get_vault_file` using VAULT_FILE_ALIASES + /karma/ volume
2. `karma-core/server.py`: `graph_query` handler in `execute_tool_action()` — runs Cypher via get_falkor()
3. `karma-core/hooks.py`: `graph_query` + `get_vault_file` added to `ALLOWED_TOOLS` whitelist
4. `docker-compose.karma.yml`: K2_PASSWORD plaintext → `${K2_PASSWORD}` env var
5. `Memory/00-karma-system-prompt-live.md`: tool list, context size, rate-limit honesty fixes

### Config Changes (on vault-neo hub.env, not in git)
- `GLM_RPM_LIMIT=40` (was defaulting to 20)
- `K2_PASSWORD=just4us2use` (moved from plaintext compose)

---

## Current State (All Verified 2026-03-05 Session 67)

| Component | Status |
|-----------|--------|
| Deep-mode tool gate | ✅ LIVE — standard chat no longer gets tools (Session 67) |
| v9 Phase 3 persona coaching | ✅ LIVE — behavioral coaching deployed (Session 67) |
| GLM tool-calling | ✅ LIVE — end-to-end verified Session 66 |
| graph_query tool | ✅ LIVE — Karma can query FalkorDB in standard GLM mode |
| get_vault_file tool | ✅ LIVE — Karma can read MEMORY.md, system-prompt, etc. |
| System prompt | ✅ HONEST + COACHED — accurate tool list + behavioral guidance |
| GLM_RPM_LIMIT | ✅ 40 RPM |
| hooks.py whitelist | ✅ Updated with new tools |
| TOOL_NAME_MAP | ✅ Fixed (empty dict) |
| K2_PASSWORD | ✅ Secured (env var) |
| Main branch protection | ✅ Enabled |
| Entity Relationships | ✅ LIVE in karmaCtx (Session 64) |
| Recurring Topics | ✅ LIVE in karmaCtx (Session 64) |
| FAISS semantic search | ✅ LIVE (Session 62) |
| Graphiti watermark | ✅ LIVE, new episodes get entity extraction (Session 63) |

---

## Next Session (Session 68)

**Primary task:** v9 Phase 4 — Karma write agency + feedback mechanism

1. Run acceptance test for v9 Phase 3: Ask Karma about a Recurring Topic → verify she references entity relationships unprompted (no code needed, just conversation test)
2. Start Phase 4 with `/brainstorm` skill → design doc → implementation plan
3. Phase 4 scope:
   - `POST /v1/feedback {turn_id, rating: +1/-1, note?: string}` endpoint in hub-bridge
   - New tools for Karma: `write_memory(content)`, `annotate_entity(name, note)`, `flag_pattern(description)`
   - Write routing: 👍 → PATCH /v1/vault-file/MEMORY.md; 👎 + text → corrections-log.md
   - DPO: every rated response = preference pair
4. Fix karma-verify skill: update smoke test to check `assistant_text` instead of `reply`

**Blocker if any:** None. Design approved. Brainstorming can start immediately.

---

## Known Pitfalls (Active — Must Not Forget)

1. **Hub-bridge build context ≠ git repo** — after `git pull` on vault-neo, must `cp server.js` to build context before rebuild
2. **hooks.py ALLOWED_TOOLS** — new tools silently rejected without whitelist entry
3. **TOOL_NAME_MAP must stay empty** — any entries will remap tool names to wrong values
4. **docker restart ≠ compose up -d** — hub.env changes require `compose up -d` to take effect
5. **vault-neo git pull after squash merge** — use `git reset --hard origin/main`, not `git pull`
6. **FalkorDB graph name is `neo_workspace`** — NOT `karma` (karma graph is empty)
7. **karma-verify smoke test checks wrong key** — skill checks `reply` but hub returns `assistant_text`; false FAILED on healthy service
