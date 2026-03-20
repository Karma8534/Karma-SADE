# Data Flows — Ground Truth (2026-03-20)

## Karma Chat Flow
User → hub.arknexus.net/v1/chat
  → hub-bridge fetches karmaCtx (FalkorDB via karma-server) + semanticCtx (FAISS) in parallel
  → buildSystemText(karmaCtx, semanticCtx, memoryMdTail)
  → claude-haiku-4-5-20251001 with TOOL_DEFINITIONS
  → tool calls resolved (graph_query, get_vault_file, shell_run, etc.)
  → response stored to ledger via /v1/ambient
  → user sees response

## Regent Chat Flow (hub.arknexus.net/regent)
User → Regent chat UI → coordination bus POST
  → karma-regent.service polls bus → triage → inference cascade
  → K2 Ollama → P1 Ollama → z.ai → Groq → OpenRouter → Claude
  → response posted to coordination bus
  → UI polls and displays

## Self-Improvement Pipeline (on K2)
vesper_watchdog.py (every 10min):
  → scans regent_evolution.jsonl for structured entries
  → extracts candidate patterns (currently: cascade_performance only)
  → writes to regent_candidates/

vesper_eval.py (every 5min):
  → grades recent turns using quality_metrics
  → updates session_state.json
  → advances Option-C cycle count

vesper_governor.py (every 2min):
  → reads candidates from regent_candidates/
  → checks all 4 gates (identity_consistency, persona_style, session_continuity, task_completion)
  → applies passing candidates to vesper_identity_spine.json
  → writes to FalkorDB via hub.arknexus.net/v1/cypher (POTENTIAL 404 — see issues)
  → writes audit record to vesper_governor_audit.jsonl
  → total_promotions: 79

vesper_researcher.py (every 90min):
  → generates self-improvement proposals
  → posts to Governor queue

## Memory Capture Flow (ambient)
Git commit → post-commit hook → /v1/ambient → vault-api → ledger.jsonl
Session end → session-end.sh → /v1/ambient → vault-api → ledger.jsonl
Karma chat turns → /v1/chat → stored automatically → ledger.jsonl
PDF files → karma-inbox-watcher.ps1 → /v1/ingest → GLM extraction → ledger.jsonl

## Ledger → Graph Flow
ledger.jsonl (193,455 entries) → batch_ingest cron (every 6h, --skip-dedup)
  → direct Cypher write to FalkorDB neo_workspace
  → 4,789 Episodic + 571 Entity + 1 Decision nodes

## K2 Cache Sync
vault-neo → K2: sync-from-vault.sh (pulls identity/invariants/direction)
K2 → vault-neo: k2_local_observations.jsonl pushed to /v1/ambient (hourly cron)

## Coordination Bus Flow
Any agent → POST /v1/coordination/post → bus persistence
Any agent → GET /v1/coordination/recent → reads pending messages
karma-regent.service → polls bus → processes messages addressed to regent
CC hourly cron on K2 → reads bus → posts status to Agora (hub.arknexus.net/agora)
