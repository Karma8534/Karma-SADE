# Architecture — Karma Peer Memory System

## System Overview
A multi-source capture pipeline that records git commits, Claude Code sessions,
and direct chat interactions, routes them through the hub-bridge, and stores them
in an append-only ledger. FalkorDB graph is populated by batch_ingest from the ledger.

**Chrome extension: SHELVED.** Never reliably captured conversations. Not in active use.

## Active Capture Sources (as of 2026-03-03)

| Source | Mechanism | Last seen in ledger |
|--------|-----------|---------------------|
| Git commits | post-commit hook → /v1/ambient | 2026-03-03 (current) |
| Claude Code sessions | session-end hook → /v1/ambient | 2026-03-03 (current) |
| Direct chat (/v1/chat) | hub-bridge stores to ledger | 2026-03-03 18:22 |
| Karma terminal | karma-terminal client | 2026-02-27 (stale) |
| Chrome extension | **SHELVED** | 2026-02-26 (legacy data only) |

## Data Flow (Current)

```
Git commit          → post-commit hook  ↘
Claude Code session → session-end hook  → /v1/ambient → vault-api → ledger
Direct chat         → /v1/chat          ↗

Ledger → batch_ingest (manual) → FalkorDB neo_workspace graph
```

## Layer Details

### Capture Layer (Tier 1 — Ambient)
- **post-commit hook** (`.git/hooks/post-commit`): fires on every git commit, POSTs commit metadata to `/v1/ambient`
- **session-end hook** (`.claude/hooks/session-end.sh`): fires when Claude Code session ends, POSTs session summary to `/v1/ambient`
- Auth: Bearer token read via SSH from vault-neo at hook runtime

### Hub API (Bridge)
- URL: https://hub.arknexus.net
- Endpoints in use: `/v1/ambient` (hook capture), `/v1/chat` (Karma chat), `/v1/context` (context query), `/v1/cypher` (graph query), `/v1/self-model`
- Auth: Bearer token (hub.chat.token.txt for chat; hub.capture.token.txt for ambient hooks)

### Vault API
- FastAPI application running in Docker (anr-vault-api container)
- Validates incoming data, assigns IDs, timestamps
- Appends to JSONL ledger at `/opt/seed-vault/memory_v1/ledger/memory.jsonl`

### Storage
- **Ledger**: `/opt/seed-vault/memory_v1/ledger/memory.jsonl` — 3980 entries (2026-03-03), append-only
- **FalkorDB**: `neo_workspace` graph — 1570 nodes (frozen; batch_ingest not running)
- **ChromaDB**: anr-vault-search container — semantic vector search (status: running but not recently updated)
- **SQLite**: `/opt/seed-vault/memory_v1/memory.db` — observations table (consciousness loop writes here)

## Ledger Entry Distribution (actual, 2026-03-03)

| Tags | Count | Source |
|------|-------|--------|
| chat, default, hub | 1521 | /v1/chat conversations |
| capture, claude, conversation, extension | 750 | LEGACY — Chrome extension (shelved) |
| karma-sade, log, sync | 614 | karma-sade sync log |
| capture, conversation, extension, openai | 436 | LEGACY — Chrome extension (shelved) |
| capture, conversation, karma-terminal | 115 | Karma terminal client |
| capture, git, commit | ~10 | post-commit hook (active) |
| capture, session-end, claude-code | ~10 | session-end hook (active) |

## FalkorDB Growth Problem
- batch_ingest is NOT running automatically
- Graph has been frozen at 1570 nodes since last manual batch run
- Consciousness loop observes FalkorDB but cannot grow it (OBSERVE-only by design)
- **To grow the graph:** `docker exec -d karma-server sh -c 'LEDGER_PATH=/opt/seed-vault/memory_v1/ledger/memory.jsonl python3 /app/batch_ingest.py > /tmp/batch.log 2>&1'`

## Consciousness Loop
- Runs in karma-server container, 60s cycles
- OBSERVE-only: pure rule-based delta scan, zero LLM calls
- Writes to SQLite observations table (primary) + consciousness.jsonl (legacy)
- LOG_GROWTH on startup = expected (first cycle always sees ~20 recent episodes, then goes idle)
- `cycle: 1` on every active event = karma-server has been restarting; counter resets

## What Is NOT Operational
- Chrome extension (shelved — DOM scraping was unreliable)
- Automatic batch_ingest (no scheduler configured)
- Karma terminal (last capture 2026-02-27)
- DPO preference pair accumulation (needs 20+ pairs, not yet started)
- Ambient Tier 3 (screen capture daemon — not yet built)
