# Karma SADE Session Summary (Latest)

**Date**: 2026-03-05
**Session**: 66
**Focus**: Promise loop fix + GLM tool-calling + system prompt honesty + session wrap-up

---

## What Was Done

### Promise Loop Fix (all 4 root causes resolved)
- **RC1** (line 413): False tool declaration in system prompt replaced with accurate deep-mode-gated list
- **RC2** (line 868): `callLLMWithTools()` now routes all non-Anthropic models to `callGPTWithTools()` — GLM gets real tool definitions
- **RC3**: System prompt context size corrected to "~12,000 chars (KARMA_CTX_MAX_CHARS)" — was falsely claiming ~1800
- **RC4**: `GLM_RPM_LIMIT=40` added to hub.env (was defaulting to 20); honest 429 behavior documented in system prompt

### New Tools Live
- **graph_query(cypher)**: Karma can run raw Cypher against FalkorDB neo_workspace in standard GLM mode. Handler in karma-core/server.py, proxied via karma-server.
- **get_vault_file(alias)**: Karma can read canonical files (MEMORY.md, system-prompt, etc.) by alias. Handled directly in hub-bridge using /karma/ volume mount.
- **hooks.py whitelist**: Added both tools to `ALLOWED_TOOLS`. This is a hidden requirement — new tools silently rejected without it.
- **TOOL_NAME_MAP bug fixed**: Was mapping `read_file → file_read` (wrong names). Now `{}` = identity passthrough.

### Security
- K2_PASSWORD moved from plaintext `docker-compose.karma.yml` → `${K2_PASSWORD}` env var; value stored in hub.env

### Repository Hygiene
- PR #14 squash-merged to main (squash commit: 357bcb9)
- 25 stale remote branches deleted
- Main branch protection enabled (no force push, no deletion)

### Session Wrap-Up
- STATE.md, ROADMAP.md, CLAUDE.md, architecture.md, direction.md all updated
- Memory/problems-log.md created with 4 problem entries
- Memory/11-session-summary-latest.md (this file) updated
- Memory/08-session-handoff.md updated
- vault MEMORY.md (droplet) appended with Session 66 summary
- cc-session-brief.md regenerated (timestamp 2026-03-05T18:07:43Z)

---

## What Is Live (Verified)

| Component | Status |
|-----------|--------|
| GLM tool-calling (graph_query, get_vault_file) | ✅ LIVE — end-to-end verified |
| System prompt honesty (tool list, context size, rate-limit) | ✅ DEPLOYED |
| GLM_RPM_LIMIT=40 | ✅ ACTIVE via hub.env |
| Hub-bridge v2.11.0 | ✅ Running (port 18090) |
| Karma-server | ✅ Running, graph_query handler active |
| FalkorDB neo_workspace | ✅ LIVE, 3621 nodes |
| FAISS semantic search | ✅ LIVE, 4073+ entries |
| Graphiti watermark cron | ✅ Every 6h, entity extraction for new episodes |

---

## What's Next

**Immediate (Session 67):**
v9 Phase 3 — Persona coaching: teach Karma WHAT TO DO when she sees `## Entity Relationships` and `## Recurring Topics` sections in karmaCtx. This is a system prompt edit only — git pull + docker restart, no rebuild needed.

**Exact first command for Session 67:**
```
/resurrect
```
Then: edit `Memory/00-karma-system-prompt-live.md` — add behavioral instructions for how Karma should USE Entity Relationships + Recurring Topics sections. Deploy: git push → vault-neo git pull → docker restart anr-hub-bridge → verify response quality.

---

## Decisions Locked This Session

- Decision #13: callGPTWithTools routes ALL non-Anthropic models (GLM supports native function calling)
- Decision #14: TOOL_NAME_MAP is identity passthrough — empty dict `{}` is correct
- Decision #15: get_vault_file in hub-bridge (not karma-server) — hub has /karma/ volume access
