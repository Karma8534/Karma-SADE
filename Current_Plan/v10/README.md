# Current_Plan/v10 — Snapshot (2026-03-10)

Captured at: Session 71 end. v9 complete. v10 starting.

## What This Is

Version snapshot of Karma's architectural documentation at the start of v10. Per CLAUDE.md rule: exact copies of canonical files plus updated direction.md/PROJECT.md with v10 additions merged in.

**Originals remain canonical:** `.gsd/STATE.md`, `.gsd/ROADMAP.md`, `direction.md`, etc. These are redundancy copies.

## Files in This Snapshot

| File | Source | Notes |
|------|--------|-------|
| STATE.md | `.gsd/STATE.md` | Exact copy — Session 70 last update |
| ROADMAP.md | `.gsd/ROADMAP.md` | Exact copy — Session 69 last update |
| REQUIREMENTS.md | `.gsd/REQUIREMENTS.md` | Exact copy — Session 56 last update |
| MEMORY.md | `MEMORY.md` | Exact copy — Session 71 current |
| CLAUDE.md | `CLAUDE.md` | Exact copy — current operator contract |
| architecture.md | `.claude/rules/architecture.md` | Exact copy — current arch rules |
| 00-karma-system-prompt-live.md | `Memory/00-karma-system-prompt-live.md` | Exact copy — Session 71 deployed |
| direction.md | **UPDATED** | Incorporates v10 primitives from PDFs |
| PROJECT.md | **UPDATED** | Reflects v10 capabilities + planned enhancements |
| README.md | **NEW** | This file |

## What v9 Delivered (Sessions 65–71)

| Session | Key Deliverable |
|---------|----------------|
| 65 | External validation: Boris Cherny CLAUDE.md principles confirm Karma's architecture |
| 66 | Promise loop fix: GLM now routes through callGPTWithTools(); graph_query + get_vault_file live; TOOL_NAME_MAP bug fixed |
| 67 | Deep-mode security gate; v9 Phase 3 persona coaching (How to Use Your Context Data) |
| 68 | Write agency: write_memory + POST /v1/feedback + unified.html thumbs + DPO pairs in vault; 5/5 acceptance tests |
| 69 | fetch_url tool; stale tools removed (prevented confabulation); MENTIONS edges verified (2,363) |
| 70 | System prompt trimmed 29%; cron --skip-dedup bug fixed; FalkorDB caught up |
| 71 | Recurring Topics coaching rewritten (concrete behavior); DEEP button in UI; PDF ingest pipeline debugged |

## What v10 Adds

### Primitives from PDF Analysis (Session 71)

**From CCintoanOS.PDF (Claude Code OS Architecture):**
- Confidence levels: HIGH/MEDIUM/LOW tags on technical claims
- Anti-hallucination pre-check: verify with fetch_url/graph_query before asserting uncertain facts
- Context7 MCP: real-time library docs, prevents hallucinated function signatures
- PostToolUseFailure logging: tool error → structured log → corrections pipeline
- Fail-closed hook pattern: default DENY on hook error

**From PiMonoCoder.PDF (Pi Coder Architecture):**
- Pi-mono 4-tool philosophy: read/write/edit/bash only — minimal footprint, maximum coding agency
- Self-as-subagent via bash: orchestrator spawns itself as worker
- Minimal system prompt discipline: context from files, not hardcoded knowledge

**From LocalAIFortress.PDF:**
- Local model routing patterns
- Security boundary enforcement (local-first for sensitive data)

### v10 Priority Order

1. **Universal thumbs (turn_id fallback)** — Session 71 plan already written; 4-task implementation
2. **Entity Relationships data quality** — karma-server query fix; replace Chrome extension stale edges
3. **Confidence levels + anti-hallucination coaching** — system prompt additions
4. **Context7 MCP** — new deep-mode tool for live library docs

## Known Gaps at v10 Start

- Entity Relationships: ~20 RELATES_TO edges are all stale Chrome extension edges (not current arch)
- DPO pairs: 0/20 collected — fine-tuning loop cannot start yet
- Recurring Topics coaching acceptance test: deployed but not formally re-validated post-Session 71 rewrite
- Corrections capture: session-end only (not event-driven like Cherny's PR-review trigger)

## How to Use This Snapshot

Read `direction.md` for full v10 direction including all PDF primitives.
Read `STATE.md` for current system status and decisions.
Read `ROADMAP.md` for phase history and upcoming work.
