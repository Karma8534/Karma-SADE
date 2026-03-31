# Tools and APIs — Ground Truth (2026-03-27, updated Session 145)

## Hub-Bridge Tools (Karma can call these)
TOOL_DEFINITIONS defined in server.js.
Active tools (verified in code):
- graph_query(cypher) — FalkorDB neo_workspace via karma-server (proxied)
- get_vault_file(alias) — read canonical files by alias
- get_local_file(path) — read files on K2 Karma_SADE folder
- list_local_dir(path) — list directory on K2
- write_memory(content) — append to MEMORY.md (approval-gated, ambient path only)
- fetch_url(url) — HTTP fetch + HTML strip (8KB cap)
- get_library_docs(library) — known library docs
- shell_run(command) — execute on K2 via aria /api/exec
- aria_local_call — K2:7890/api/chat (Aria service)
- defer_intent — deferred intent engine
- get_active_intents — surface active intents
- read_project_file / write_project_file / code_exec / browse — extended tools

## Hub-Bridge API Endpoints (hub.arknexus.net)
- POST /v1/chat — main Karma chat (3-tier routing: cortex→mini→5.4)
- POST /v1/ambient — capture hook ingestion
- GET/POST /v1/context — context query
- POST /v1/cypher — FalkorDB graph query
- POST /v1/ingest — PDF/image ingestion
- POST /v1/feedback — thumbs approval gate (write_memory + DPO pairs)
- GET /v1/coordination/recent — bus read
- POST /v1/coordination/post — bus write
- GET /v1/vault-file/{alias} — read canonical files
- PATCH /v1/vault-file/MEMORY.md — write spine (ambient)
- GET /v1/status — Sovereign visibility: models, spend, nodes, governance
- GET /v1/trace — per-request routing log (in-memory, last 50 entries) — deployed S153
- GET /v1/checkpoint/latest — vault checkpoint proxy
- GET /health — no-auth health check
- GET /healthz — detailed health with config

## Model Routing (hub.env on vault-neo, Decision #35 S145)
- MODEL_DEFAULT: gpt-5.4-mini ($0.75/$4.50 per 1M)
- MODEL_ESCALATION: gpt-5.4 ($2.50/$15.00 per 1M)
- MODEL_VERIFIER: claude-sonnet-4-6 ($3.00/$15.00 per 1M) — gated by VERIFIER_ENABLED
- Tools: available in ALL modes
- Cognitive split: recall→cortex ($0), standard→gpt-5.4-mini, deep→gpt-5.4

## Canonical File Aliases
- MEMORY.md, system-prompt, session-handoff, session-summary, core-architecture
- consciousness, collab, candidates (ledger files)
- cc-brief

## Karma-Server Tools (karma-server container)
- graph_query → hooks.py ALLOWED_TOOLS whitelist gates entry
- batch_ingest → cron every 6h, --skip-dedup mode
- consciousness loop → 60s OBSERVE-only cycles

## Aria Service (K2:7890)
- POST /api/chat — Aria chat
- POST /api/exec — shell command execution (used by shell_run tool)
- GET /api/tools/list — K2 tool registry
- POST /api/tools/execute — K2 tool execution
- Auth: X-Aria-Service-Key header

## Julian Cortex (K2:7892 primary, P1:7893 fallback)
- GET /health — status, block count, model, uptime
- POST /query — ask a question (qwen3.5:4b inference, ~5s)
- POST /ingest — add knowledge block
- GET /context — current state summary
- POST /reset — clear all blocks
