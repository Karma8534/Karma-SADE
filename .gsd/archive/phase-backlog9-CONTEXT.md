# Backlog-9: karma-observer.py — CONTEXT
**Date:** 2026-03-25 | **Session:** 143

## What We're Building
A daemon on K2 that extracts behavioral rules from Karma's conversation history and writes them to karma-directives.md. Hub-bridge reads this file and injects it into Karma's system prompt on every /v1/chat call.

## Design Decisions (locked)

### Where it runs: K2
- Follows existing pattern: vesper_watchdog, vesper_eval, vesper_governor all run on K2
- Access to K2 cache files and local Ollama for rule extraction
- systemd timer (like karma-regent.service pattern)

### What it reads: vault ledger via hub-bridge API
- Reads recent ledger entries via POST /v1/search (FAISS semantic search on vault-neo)
- Filters for entries containing `[karma-correction]` or `[PITFALL]` or explicit behavioral feedback
- Also reads DPO pairs from ledger (tags: dpo-pair) for thumbs-down corrections

### What it writes: karma_behavioral_rules.jsonl on K2 + PATCH to vault-neo
- Primary output: `/mnt/c/dev/Karma/k2/cache/karma_behavioral_rules.jsonl`
- Each rule: `{"rule": "...", "confidence": 0.XX, "source_episode": "...", "extracted_at": "ISO", "applied": false}`
- Secondary: PATCH /v1/vault-file/MEMORY.md with `[KARMA-RULE] rule text` for persistence

### How hub-bridge reads it: new cache in buildSystemText()
- Pattern: identical to _memoryMdCache (tail N chars, refresh every 5min)
- New cache: _karmaRulesCache reads from K2 via Tailscale HTTP or from a vault-neo synced copy
- Simplest path: karma-observer.py POSTs rules to /v1/ambient with tag `karma-behavioral-rule` → FAISS indexes them → buildSystemText() fetches via existing semanticCtx path
- This means: NO new hub-bridge code needed for MVP. Rules surface through existing FAISS retrieval.

### What we're NOT doing
- No LLM-based rule extraction (too expensive, too slow) — keyword + pattern matching only
- No real-time injection (polling is fine at 10-15min cadence)
- No separate buildSystemText() section for MVP — rules surface via FAISS semanticCtx
- No karma-directives.md sync from K2 to P1 for MVP — that's a future step

## Convergence with Backlog-11 (karma-directives.md)
- karma-directives.md on P1 is the SEED file (human-written initial directives)
- karma-observer.py on K2 is the WRITER (machine-extracted rules)
- For MVP: observer writes to jsonl + /v1/ambient. karma-directives.md updated manually.
- Future: observer reads karma-directives.md, appends to "Learned Rules" section, pushes to vault-neo

## Existing Patterns to Follow
- vesper_watchdog.py: 10min cadence, scans structured log, extracts candidates
- ambient_observer.py: signal extraction from bus messages, noise filtering
- Both use polling loops with sleep intervals
