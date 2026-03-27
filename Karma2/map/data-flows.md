# Data Flows — Ground Truth (2026-03-27, updated Session 145)

## Karma Chat Flow (3-tier routing)
User → hub.arknexus.net/v1/chat
  → hub-bridge classifyMessageTier(userMessage, deep_mode)
  → TIER 0 (recall): K2 cortex ($0) → P1 cortex fallback → cloud fallback
  → TIER 1-2: gpt-5.4-mini via OpenAI API ($0.75/$4.50 per 1M)
  → TIER 3: gpt-5.4 via OpenAI API ($2.50/$15.00 per 1M)
  → buildSystemText(karmaCtx, semanticCtx, memoryMdTail) — tiered identity injection
  → Tier 1: 00-karma-local-prompt.md (1.2K chars)
  → Tier 2: 01-karma-standard-prompt.md (2.3K chars)
  → Tier 3: 00-karma-system-prompt-live.md (39K chars)
  → response stored to ledger via /v1/ambient
  → cost logged to /run/state/request_cost.jsonl (queryable via /v1/trace)
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
  → extracts candidate patterns
  → writes to regent_candidates/

vesper_eval.py (every 5min):
  → grades recent turns using quality_metrics
  → updates session_state.json

vesper_governor.py (every 2min):
  → reads candidates from regent_candidates/
  → checks all 4 gates (identity_consistency, persona_style, session_continuity, task_completion)
  → creates spine_backup_pre_promote.json + git snapshot BEFORE write
  → applies passing candidates to vesper_identity_spine.json
  → writes to FalkorDB via hub.arknexus.net/v1/cypher
  → writes audit record to vesper_governor_audit.jsonl (3805+ entries)
  → total_promotions: 1284

## Memory Capture Flow (ambient)
Git commit → post-commit hook → /v1/ambient → vault-api → ledger.jsonl
Session end → session-end.sh → /v1/ambient → vault-api → ledger.jsonl
Karma chat turns → /v1/chat → stored automatically → ledger.jsonl
PDF files → karma-inbox-watcher.ps1 → /v1/ingest → extraction → ledger.jsonl
Bus messages → bus_to_cortex.py (2min cron) → K2 cortex ingestion

## Ledger → Graph Flow
ledger.jsonl (209K+ entries) → batch_ingest cron (every 6h, --skip-dedup)
  → direct Cypher write to FalkorDB neo_workspace
  → 4789+ nodes (Episodic + Entity + Decision)

## K2 Cache Sync
vault-neo → K2: sync-from-vault.sh pull (every 30min, tightened S145 from 6h)
K2 → vault-neo: sync-from-vault.sh push (hourly, k2_local_observations.jsonl → /v1/ambient)
K2 → P1: sync_k2_to_p1.py (every 30min, Windows scheduled task)

## Sovereign Visibility
/v1/status → models, spend, node health, governance state
/v1/trace → per-request cost log (last 50 entries)
CASCADE UI → compact node health display
AGORA → shared bus event surface at /agora
