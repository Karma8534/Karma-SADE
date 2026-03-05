# Karma SADE — Session Handoff

**Date**: 2026-03-05
**Session**: 68
**GitHub**: https://github.com/Karma8534/Karma-SADE (PUBLIC)
**Last commit**: 9d68c0d (main, synced to vault-neo)

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
│   └── /v1/feedback      ─── write_memory approval gate (Session 68)
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

## What Changed in Session 68

### Code Changes (deployed to main + vault-neo)
1. `hub-bridge/lib/feedback.js` (NEW — commit a17ce54): `processFeedback()` + `prunePendingWrites()`, 7 TDD tests
2. `hub-bridge/app/server.js` (multiple commits): `pending_writes` Map, `write_memory` tool def, `writeId` threading, `POST /v1/feedback` endpoint, bare-newline fix (b002b5b), buildVaultRecord DPO fix (69f061b), type:log fix (cf63957)
3. `hub-bridge/app/public/unified.html` (commits 0618fbb, 314d301): write_id in response, feedback buttons only when writeId truthy, thumbs-down textarea, fresh token on submit, double-submit guard
4. `karma-core/hooks.py` (commit 362de7e): `"write_memory"` added to ALLOWED_TOOLS
5. `Memory/00-karma-system-prompt-live.md` (commit 6f078e7): write_memory coaching paragraph; KARMA_IDENTITY_PROMPT 11,850 → 12,366 chars

### Deployments
- karma-server rebuilt (hooks.py change)
- hub-bridge rebuilt twice (server.js + lib/ + unified.html changes)
- Both services verified healthy (RestartCount=0)

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

## Current State (All Verified 2026-03-05 Session 68)

| Component | Status |
|-----------|--------|
| write_memory tool + pending_writes gate | ✅ LIVE — in-process Map, write_id threading (Session 68) |
| POST /v1/feedback endpoint | ✅ LIVE — auth + approve/reject + DPO (Session 68) |
| unified.html feedback UI | ✅ LIVE — 👍/👎 buttons + thumbs-down textarea (Session 68) |
| DPO pairs in vault ledger | ✅ LIVE — type:log, tags:["dpo-pair"], 0/20 accumulated (Session 68) |
| System prompt write_memory coaching | ✅ LIVE — 12,366 chars (Session 68) |
| Deep-mode tool gate | ✅ LIVE — standard chat no longer gets tools (Session 67) |
| v9 Phase 3 persona coaching | ✅ LIVE — behavioral coaching deployed (Session 67) |
| GLM tool-calling | ✅ LIVE — end-to-end verified Session 66 |
| graph_query tool | ✅ LIVE — Karma can query FalkorDB in deep mode |
| get_vault_file tool | ✅ LIVE — Karma can read MEMORY.md, system-prompt, etc. |
| System prompt | ✅ HONEST + COACHED — accurate tool list + behavioral guidance |
| GLM_RPM_LIMIT | ✅ 40 RPM |
| hooks.py whitelist | ✅ Updated: graph_query, get_vault_file, write_memory |
| TOOL_NAME_MAP | ✅ Fixed (empty dict) |
| K2_PASSWORD | ✅ Secured (env var) |
| Main branch protection | ✅ Enabled |
| Entity Relationships | ✅ LIVE in karmaCtx (Session 64) |
| Recurring Topics | ✅ LIVE in karmaCtx (Session 64) |
| FAISS semantic search | ✅ LIVE (Session 62) |
| Graphiti watermark | ✅ LIVE, new episodes get entity extraction (Session 63) |

---

## Next Session (Session 69)

**Primary task:** karma-verify skill fix + v9 Phase 5 MENTIONS verification

1. Fix karma-verify skill — update `C:\Users\raest\.claude\skills\karma-verify\SKILL.md` to check `assistant_text` instead of `reply`
2. v9 Phase 5 — Verify MENTIONS edge growth: `ssh vault-neo "docker exec anr-karma-server curl -s localhost:8000/v1/cypher -d '{\"query\":\"MATCH ()-[:MENTIONS]->() RETURN count(*) as edges\"}'"`
3. Check DPO accumulation: `ssh vault-neo "grep -c 'dpo-pair' /opt/seed-vault/memory_v1/ledger/memory.jsonl"` — should be growing with use

**Blocker if any:** None. All systems green.

---

## Known Pitfalls (Active — Must Not Forget)

1. **Hub-bridge build context ≠ git repo** — after `git pull` on vault-neo, must cp server.js + lib/ to build context (parent `/opt/.../hub_bridge/`, NOT under `app/`)
2. **hub-bridge lib/ files go at parent level** — `lib/feedback.js` must be at `/opt/.../hub_bridge/lib/` not under `app/lib/`
3. **hooks.py ALLOWED_TOOLS** — new tools silently rejected without whitelist entry
4. **TOOL_NAME_MAP must stay empty** — any entries will remap tool names to wrong values
5. **docker restart ≠ compose up -d** — hub.env changes require `compose up -d` to take effect
6. **vault-neo git pull after squash merge** — use `git reset --hard origin/main`, not `git pull`
7. **FalkorDB graph name is `neo_workspace`** — NOT `karma` (karma graph is empty)
8. **karma-verify smoke test checks wrong key** — skill checks `reply` but hub returns `assistant_text`; false FAILED on healthy service (OPEN)
9. **vault-api type enum is closed** — only ["fact","preference","project","artifact","log","contact"]; use type:"log" + tags for custom types
10. **buildVaultRecord() required for all vault writes** — bare objects fail schema validation silently (vaultPost fire-and-forget swallows 422)
