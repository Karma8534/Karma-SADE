# Architecture — Karma Peer Memory System

## System Overview
A multi-source capture pipeline that records git commits, Claude Code sessions,
and direct chat interactions, routes them through the hub-bridge, and stores them
in an append-only ledger. FalkorDB graph is populated by batch_ingest running on cron.

**Chrome extension: SHELVED.** Never reliably captured conversations. Not in active use.

## Active Capture Sources (as of 2026-03-03)

| Source | Mechanism | Last seen in ledger |
|--------|-----------|---------------------|
| Git commits | post-commit hook → /v1/ambient | 2026-03-03 (current) |
| Claude Code sessions | session-end hook → /v1/ambient | 2026-03-03 (current) |
| Direct chat (/v1/chat) | hub-bridge stores to ledger | 2026-03-03 (current) |
| PDF/image ingestion | karma-inbox-watcher.ps1 → /v1/ingest | 2026-03-03 (active) |
| Karma terminal | karma-terminal client | 2026-02-27 (stale) |
| Chrome extension | **SHELVED** | 2026-02-26 (legacy data only) |

## Data Flow (Current)

```
Git commit          → post-commit hook  ↘
Claude Code session → session-end hook  → /v1/ambient → vault-api → ledger
Direct chat         → /v1/chat          ↗
PDF/images          → /v1/ingest        ↗

Ledger → batch_ingest (cron every 6h on vault-neo) → FalkorDB neo_workspace graph
```

## Layer Details

### Capture Layer (Tier 1 — Ambient)
- **post-commit hook** (`.git/hooks/post-commit`): fires on every git commit, POSTs commit metadata to `/v1/ambient`
- **session-end hook** (`.claude/hooks/session-end.sh`): fires when Claude Code session ends, POSTs session summary to `/v1/ambient`
- Auth: Bearer token read via SSH from vault-neo at hook runtime

### PDF/Image Ingestion (Tier 2 — Enrichment)
- **karma-inbox-watcher.ps1**: PowerShell FileSystemWatcher on `OneDrive\Karma\Inbox` and `OneDrive\Karma\Gated`
- POSTs base64-encoded files to `/v1/ingest` on hub-bridge
- Rate-limit aware: detects 429, backs off 60s, retries up to 3x, writes `.jammed.txt` if exhausted
- Time-window scheduling: optional params `$ProcessingWindowStart`/`$ProcessingWindowEnd` for off-peak batch
- 8s delay between batch files (prevents GLM rate-limit starvation)
- GLM-4.7-Flash processes extraction — no fallback to paid models (Decision #7)

### Hub API (Bridge)
- URL: https://hub.arknexus.net
- Endpoints in use: `/v1/ambient` (hook capture), `/v1/chat` (Karma chat), `/v1/context` (context query), `/v1/cypher` (graph query), `/v1/self-model`, `/v1/ingest` (PDF pipeline)
- Auth: Bearer token (hub.chat.token.txt for chat; hub.capture.token.txt for ambient hooks)
- Model routing: GLM-4.7-Flash primary (~80%), gpt-4o-mini fallback (~20%) — Decision #7

### Vault API
- FastAPI application running in Docker (anr-vault-api container)
- Validates incoming data, assigns IDs, timestamps
- Appends to JSONL ledger at `/opt/seed-vault/memory_v1/ledger/memory.jsonl`

### Storage
- **Ledger**: `/opt/seed-vault/memory_v1/ledger/memory.jsonl` — ~4000+ entries (2026-03-03), append-only
- **FalkorDB**: `neo_workspace` graph — 2293 nodes (batch_ingest cron running every 6h)
- **ChromaDB**: anr-vault-search container — semantic vector search (status: running but not recently updated)
- **SQLite**: `/opt/seed-vault/memory_v1/memory.db` — observations table (consciousness loop writes here)

## Ledger Entry Distribution (actual, 2026-03-03)

| Tags | Count | Source |
|------|-------|--------|
| chat, default, hub | 1538+ | /v1/chat conversations |
| capture, claude, conversation, extension | 750 | LEGACY — Chrome extension (shelved) |
| karma-sade, log, sync | 614 | karma-sade sync log |
| capture, conversation, extension, openai | 436 | LEGACY — Chrome extension (shelved) |
| capture, conversation, karma-terminal | 115 | Karma terminal client |
| capture, git, commit | ~20+ | post-commit hook (active) |
| capture, session-end, claude-code | ~20+ | session-end hook (active) |

## batch_ingest
- Runs on cron: `0 */6 * * *` on vault-neo
- Command: `docker exec karma-server sh -c 'LEDGER_PATH=/ledger/memory.jsonl python3 /app/batch_ingest.py > /tmp/batch.log 2>&1'`
- LEDGER_PATH inside container: `/ledger/memory.jsonl` (NOT `/opt/seed-vault/...`)
- Extended to handle hub/chat entries (2026-03-03): detects `hub+chat` tags, reads `assistant_text` fallback

## karma-server Build Context
- **Compose file**: `/opt/seed-vault/memory_v1/compose/compose.yml`
- **Build context**: `/opt/seed-vault/memory_v1/karma-core/` (NOT the git repo at `/home/neo/karma-sade/karma-core/`)
- **Sync pattern**: After git changes to karma-core, always `cp` updated files to build context before rebuild
- **Rebuild command**: `cd /opt/seed-vault/memory_v1/compose && docker compose build --no-cache karma-server && docker compose up -d karma-server`

## Consciousness Loop
- Runs in karma-server container, 60s cycles
- OBSERVE-only: pure rule-based delta scan, zero LLM calls
- Writes to SQLite observations table (primary) + consciousness.jsonl (legacy)
- LOG_GROWTH on startup = expected (first cycle always sees recent episodes, then goes idle)

## Security (as of 2026-03-03)
- OPENAI_API_KEY: read from mounted file `/opt/seed-vault/memory_v1/session/openai.api_key.txt` — NOT injected as env var (prevents `docker inspect` exposure)
- K2 credentials: externalized to env vars in compose file (not hardcoded)
- Hub bearer token: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt`

## What Is NOT Operational
- Chrome extension (shelved — DOM scraping was unreliable)
- Karma terminal (last capture 2026-02-27)
- DPO preference pair accumulation (needs 20+ pairs, not yet started)
- Ambient Tier 3 (screen capture daemon — not yet built)
