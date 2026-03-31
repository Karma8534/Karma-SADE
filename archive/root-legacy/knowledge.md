# Project knowledge

This file gives Codebuff context about your project: goals, commands, conventions, and gotchas.

## What this is

Karma SADE is a personal agentic AI system with multi-model smart routing, a temporal knowledge graph (FalkorDB + Graphiti), persistent memory (ArkNexus Vault), a consciousness loop, and a Chrome extension for chat capture. It runs across a local Windows 11 machine and a DigitalOcean droplet (vault-neo / arknexus.net).

## Key directories

- `karma-core/` — Python FastAPI server (the "brain"): chat via WebSocket, knowledge graph queries, consciousness loop, model routing, SMS. Runs on port 8340 inside Docker.
- `hub-bridge/` — Node.js (ESM) HTTP server: OpenAI/Anthropic proxy with tool-use, Brave web search, session memory, ingest pipeline, vault file access. Runs on port 18090 inside Docker.
- `vault-api/` — Node.js (CJS, Express) server: append-only JSONL ledger, facts endpoint, checkpoint/promote/resurrection system. Runs on port 8080 inside Docker on the droplet.
- `Scripts/` — PowerShell (.ps1) and Python (.py) automation: health checks, memory sync, sentinel, backend, quota management, resurrection, watchers.
- `Memory/` — Local mirror of canonical knowledge: system prompts, architecture docs, user facts, session summaries. Synced bidirectionally with Vault every 5 min.
- `Dashboard/` — Static HTML dashboards (unified 3-panel layout).
- `chrome-extension/` — Browser extension capturing chats from Claude/OpenAI/Gemini.
- `docs/` — Design docs, plans, and contracts.
- `Scripts/resurrection/` — PowerShell scripts for session resurrection system.

## Commands

- **Start locally:** `START_KARMA.bat` or double-click desktop shortcut
- **Dashboard:** `http://localhost:9401/unified`
- **karma-core (Docker):** Built from `karma-core/Dockerfile`, deployed via `docker-compose.karma.yml`
- **hub-bridge (Docker):** Deployed via `hub-bridge/compose.hub.yml`
- **hub-bridge deps:** `cd hub-bridge && npm install`
- **karma-core deps:** `pip install -r karma-core/requirements.txt`
- **Health check:** `curl http://localhost:9401/health` (local backend) or `curl http://localhost:8340/health` (karma-core)
- **Run local backend:** `python Scripts/karma_backend.py` (port 9401)
- **Test backend:** `python Scripts/test_backend.py`

## Architecture / Data flow

1. User sends message via Dashboard WebSocket, Chrome extension, CLI, or SMS
2. `hub-bridge` receives it, fetches FalkorDB context from `karma-core` (`/raw-context`), builds system prompt, routes to LLM (Claude/GPT with tool-use)
3. `karma-core` queries FalkorDB (knowledge graph) + PostgreSQL (preferences) to build context
4. Responses are logged to Vault JSONL ledger; facts auto-extracted and written back
5. Consciousness loop (`karma-core/consciousness.py`) runs every 60s: observe → think → act → reflect
6. Knowledge graph updated via Graphiti episodes after each conversation turn
7. Ingest pipeline: ASSIMILATE/DEFER/DISCARD signals in LLM responses trigger FalkorDB writes via `/write-primitive`
8. Memory Integrity Gate: episodes land as `candidate` lane, promoted to `canonical` only with explicit user approval via `/promote-candidates`

## Conventions

- **karma-core:** Python 3, FastAPI, async, type hints. Config via env vars in `karma-core/config.py`.
- **hub-bridge:** Node.js ESM (`"type": "module"`), raw `http.createServer` (no Express), secrets loaded from files at startup.
- **vault-api:** Node.js CJS (`require`), Express, AJV schema validation for ledger writes.
- **Naming:** User's real name is Colby (alias: Neo). Karma should always use "Colby".
- **Docker networking:** `network_mode: host` for karma-server (direct Tailscale access). Vault services on `anr-vault-net` Docker network.
- **Secrets:** API keys in Windows registry (local) or `/run/secrets/` files (Docker).
- **Ledger:** Append-only JSONL at `/opt/seed-vault/memory_v1/ledger/memory.jsonl`. Never delete entries; deprecate via verification status.
- **FalkorDB:** Uses Redis protocol on port 6379. Graph ID: `neo_workspace`. Cypher queries via `GRAPH.QUERY` command.

## Gotchas

- hub-bridge is ESM (`import`), vault-api is CJS (`require`) — don't mix module styles.
- FalkorDB port is 6379 (Redis protocol) internally, 7687 externally via Docker.
- Claude API key is currently disabled (no credits). Primary LLM routing goes through GPT-4o-mini / Claude Sonnet via hub-bridge.
- Consciousness loop ingestion to Graphiti is disabled due to prior entity corruption from `batch_ingest --skip-dedup`; writes go to ledger only.
- The local `Scripts/karma_backend.py` (port 9401) is a separate backend from `karma-core/server.py` (port 8340) — they serve different roles.
- `karma-core/router.py` handles multi-model routing (Groq, MiniMax, GLM-5, OpenAI) for the Docker-based server.
- Session memory in hub-bridge is in-process only (30 min TTL, 8 turn pairs). Not persisted across restarts.
