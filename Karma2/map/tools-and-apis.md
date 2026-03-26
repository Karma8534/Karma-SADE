# Tools and APIs — Ground Truth (2026-03-20)

## Hub-Bridge Tools (Karma can call these)
TOOL_DEFINITIONS defined at server.js line 1342.
Active tools (from architecture.md + verified in code):
- graph_query(cypher) — FalkorDB neo_workspace via karma-server (proxied)
- get_vault_file(alias) — read canonical files by alias
- write_memory(content) — append to MEMORY.md (approval-gated)
- fetch_url(url) — HTTP fetch + HTML strip (8KB cap)
- get_library_docs(library) — known library docs
- get_local_file(path) — read files on K2
- shell_run(command) — execute on K2 via aria /api/exec
- aria_local_call — K2:7890/api/chat (Aria service)
- browser_* — NOT YET WIRED (chromium exists on K2, not a hub-bridge tool)

## Hub-Bridge API Endpoints (hub.arknexus.net)
- POST /v1/chat — main Karma chat
- POST /v1/ambient — capture hook ingestion
- GET/POST /v1/context — context query
- POST /v1/cypher — FalkorDB graph query
- POST /v1/ingest — PDF/image ingestion
- POST /v1/feedback — thumbs approval gate
- GET /v1/coordination/recent — bus read
- POST /v1/coordination/post — bus write
- GET /v1/vault-file/{alias} — read canonical files
- PATCH /v1/vault-file/MEMORY.md — write spine
- GET /health — no-auth health check

## Canonical File Aliases
- MEMORY.md
- system-prompt (Memory/00-karma-system-prompt-live.md)
- session-handoff (Memory/08-session-handoff.md)
- session-summary (Memory/11-session-summary-latest.md)
- core-architecture (Memory/01-core-architecture.md)
- consciousness (ledger/consciousness.jsonl)
- collab / candidates (ledger files)

## Karma-Server Tools (karma-server container)
- graph_query → hooks.py ALLOWED_TOOLS whitelist gates entry
- batch_ingest → cron every 6h, --skip-dedup mode
- consciousness loop → 60s OBSERVE-only cycles

## Aria Service (K2:7890)
- POST /api/chat — Aria chat (used by aria_local_call tool)
- POST /api/exec — shell command execution (used by shell_run tool)
- Auth: X-Aria-Service-Key header

## Model Routing (karma-regent.service, /etc/karma-regent.env)
Cascade order (Session 107 fix): K2 Ollama → P1 Ollama → z.ai → Groq → OpenRouter → Claude
- K2_OLLAMA_URL: http://host.docker.internal:11434
- K2_OLLAMA_PRIMARY_MODEL: nemotron-mini:optimized (VERIFIED LIVE S143 — 3.1GB, 100% GPU, 4096 ctx)
- P1_OLLAMA_URL: http://100.124.194.102:11434
- P1_OLLAMA_MODEL: nemotron-mini:latest — RESOLVED (model exists on P1, verified Session 110/125)
- REGENT_TRIAGE_MODEL: nemotron-mini:optimized (was qwen3:8b — stale, corrected S143)
- Cloud keys: ANTHROPIC, GROQ, OPENROUTER, ZAI all present in env

## Hub-Bridge Model Routing (hub.env on vault-neo)
- MODEL_DEFAULT: claude-haiku-4-5-20251001
- MODEL_DEEP: claude-haiku-4-5-20251001 (both slots same)
- Tools: available in ALL modes (deep gate removed Session 85)
