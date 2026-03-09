# Karma SADE — Session Handoff

**Date**: 2026-03-09
**Session**: 70
**GitHub**: https://github.com/Karma8534/Karma-SADE (PUBLIC)
**Last commit**: 59408af (main, synced to vault-neo)

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

## What Changed in Session 70

### System Prompt Changes
1. `Memory/00-karma-system-prompt-live.md` (commits 8b989dc, 59408af):
   - Trimmed: 16,519 → 11,674 chars (-29%)
   - Removed: API Surface table, corrections #1/#2/#5 (verdict.txt, batch_ingest direction, consciousness loop), infrastructure container list, machine specs
   - Added: explicit "resurrection spine" ban paragraph
   - Added: context lag explanation ("0-6h lag is normal")
   - Per-request input chars: 67,388 → 56,843

### Infrastructure Fix (vault-neo only, not in git)
- vault-neo crontab: added `--skip-dedup` to batch_ingest command
- Manual catchup: watermark reset to 4100, 118 entries ingested at 879 eps/s, 0 errors
- FalkorDB: 76 March-5 nodes + March-9 nodes now present

---

## Current State (All Verified 2026-03-09 Session 70)

| Component | Status |
|-----------|--------|
| /v1/chat | ✅ ok, 56,843 input chars (was 67,388) |
| System prompt | ✅ 11,674 chars, no resurrection spine, context lag noted |
| batch_ingest cron | ✅ --skip-dedup PERMANENT — Graphiti mode was silently failing |
| FalkorDB catchup | ✅ March 5+9 entries ingested — Karma context current |
| hub-bridge | ✅ RestartCount=0, v2.11.0 |
| fetch_url tool | ✅ LIVE — deep mode, user-provided URLs (Session 69) |
| write_memory + /v1/feedback | ✅ LIVE — pending_writes gate + DPO pairs (Session 68) |
| unified.html | ✅ LIVE — write_memory 👍/👎 buttons (Session 68) |
| Deep-mode tool gate | ✅ standard chat no longer gets tools (Session 67) |
| graph_query / get_vault_file | ✅ LIVE (Session 66) |
| FAISS semantic search | ✅ LIVE (Session 62) |

---

## Next Session (Session 71)

**Primary task:** Thumbs up/down general feedback UI for Karma chat

1. **Explore hub-bridge UI source**: Read `hub-bridge/app/public/unified.html` + `hub-bridge/app/server.js` /v1/feedback endpoint to understand what's already there from Session 68
2. **Complete brainstorming**: The write_memory feedback (Session 68) is thumbs on memory writes only. The user wants general per-message thumbs on ALL responses. Brainstorming was started last session — pick up at "explore project context" step.
3. **writing-plans → implement**

**Blocker if any:** None. All systems green.

---

## Known Pitfalls (Active — Must Not Forget)

1. **Hub-bridge build context ≠ git repo** — after `git pull` on vault-neo, must cp server.js + lib/ to build context (parent `/opt/.../hub_bridge/`, NOT under `app/`)
2. **hub-bridge lib/ files go at parent level** — `lib/feedback.js` must be at `/opt/.../hub_bridge/lib/` not under `app/lib/`
3. **hooks.py ALLOWED_TOOLS** — new tools silently rejected without whitelist entry
4. **TOOL_NAME_MAP must stay empty** — any entries will remap tool names to wrong values
5. **docker restart ≠ compose up -d** — hub.env changes require `compose up -d` to take effect
6. **FalkorDB graph name is `neo_workspace`** — NOT `karma` (karma graph is empty)
7. **vault-api type enum is closed** — only ["fact","preference","project","artifact","log","contact"]; use type:"log" + tags for custom types
8. **buildVaultRecord() required for all vault writes** — bare objects fail schema validation silently
9. **batch_ingest cron MUST use --skip-dedup** — Graphiti mode silently fails at scale (watermark advances, 0 nodes created, no error logged). Verify: `crontab -l | grep batch` must show `--skip-dedup`
10. **Watermark file is root-owned** — can't write directly; use `docker exec karma-server sh -c 'echo N > /ledger/.batch_watermark'`
