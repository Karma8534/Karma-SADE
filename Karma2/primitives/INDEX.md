# Primitives Goldmine — Extracted Patterns for Assimilation

Everything ingested from research, PDFs, sessions, and external sources lands here.
Sorted by date, scored by relevance, tagged by status.

## Status Tags
- **ASSIMILATED** — integrated into Karma's codebase
- **QUEUED** — high-relevance, ready to implement
- **DEFERRED** — useful but not urgent
- **SUPERSEDED** — replaced by something better

## Structure
```
Karma2/primitives/
  INDEX.md          ← this file (running list)
  Memory/02-extracted-primitives.md  ← S157 extraction (15 USE NOW + 5 DEFER)
  /by-date/         ← raw extractions organized by ingestion date
  /by-topic/        ← curated by domain (agentic, memory, security, UI, etc.)
```

## Running List (newest first)

### 2026-04-02 (S157 — 17 files from phone research)
- *Pending ingestion via KarmaInboxWatcher*
- Source: Karma_PDFs/Inbox (hundreds of files dropped by Sovereign)
- Priority: newest date files first

### 2026-04-02 (S157 — CC Wrapper Analysis)
- 10 USE NOW primitives extracted by Codex from 1902 CC wrapper source files
- Agentic loop, crash-safe persistence, auto-compaction, subagent isolation, permission stack
- All 5 critical primitives BUILT in nexus_agent.py
- Status: **ASSIMILATED**

### 2026-04-02 (S157 — Vesper Gap Analysis)
- Codex compared yoyo-evolve vs Vesper pipeline
- Gap: promotions never reached response path
- Fix: _fetch_vesper_stable_patterns() wired into build_context_prefix()
- Status: **ASSIMILATED**

### 2026-04-02 (S157 — ngrok AI Gateway)
- Multi-provider failover, BYOK, CEL routing, Ollama custom provider
- Assessment: overengineered for our scale. OpenRouter simpler.
- Status: **DEFERRED** (Golden Ticket saved)
