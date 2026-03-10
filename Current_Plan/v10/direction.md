# Direction — What We're Building

**Last updated:** 2026-03-10 (v10 snapshot — Session 71 end)
**Status:** v10 START — v9 complete. New primitives from PDF analysis identified. Universal thumbs (turn_id) plan approved.

---

## Mission

Karma is a single coherent peer whose long-term identity lives in a verified memory spine. That memory enables continuity, evidence-based self-improvement, and selective delegation — without parallel sources of truth.

v9 completed the reasoning/context layer. v10 focuses on signal quality, coding agency, and anti-hallucination discipline.

---

## Architecture (Current — hub-bridge + FalkorDB)

| Component | Role | Status |
|-----------|------|--------|
| **vault-neo** | Karma's persistent home (DigitalOcean NYC3, 4GB RAM) | ✅ Running |
| **anr-hub-bridge** | API: /v1/chat, /v1/ambient, /v1/ingest, /v1/context, /v1/cypher, /v1/feedback | ✅ Running |
| **karma-server** | Consciousness loop (OBSERVE-only, 60s cycles, zero LLM calls) | ✅ Running |
| **FalkorDB** | Graph: `neo_workspace` — 3621+ nodes (Episodic + Entity + Decision) | ✅ Running |
| **Ledger** | `/opt/seed-vault/memory_v1/ledger/memory.jsonl` — 4000+ entries, append-only | ✅ Growing |
| **anr-vault-search (FAISS)** | Custom search_service.py — FAISS + text-embedding-3-small, 4073+ entries, auto-reindex | ✅ Live |
| **batch_ingest** | Cron every 6h: --skip-dedup mode (direct Cypher, 899 eps/s, 0 errors) | ✅ Scheduled |
| **PDF watcher** | `karma-inbox-watcher.ps1` → /v1/ingest (rate-limit aware, jam detection) | ✅ Active |
| **Brave Search** | Auto-triggered on search intent, top-3 results injected into context | ✅ Enabled |
| **K2 local worker** | DEPRECATED 2026-03-03 — not operational, not needed | ❌ Shelved |
| **Chrome extension** | SHELVED permanently — DOM scraping unreliable | ❌ Shelved |

**Models:**
- Primary: GLM-4.7-Flash (Z.ai) — ~80% of requests, free, 40 RPM self-imposed limit
- Deep/fallback: gpt-4o-mini (OpenAI) — triggered by `x-karma-deep: true` header only, paid

**Context pipeline (per /v1/chat request):**
1. `karmaCtx` — FalkorDB recency via karma-server (Entity Relationships + Recurring Topics included)
2. `semanticCtx` — FAISS top-5 relevant entries via anr-vault-search (POST :8081/v1/search)
3. `webResults` — Brave Search (if SEARCH_INTENT_REGEX matches)
4. `identityBlock` — Memory/00-karma-system-prompt-live.md (loaded at hub-bridge startup)

**Active deep-mode tools (x-karma-deep: true):**
- `graph_query(cypher)` — FalkorDB neo_workspace query, proxied to karma-server
- `get_vault_file(alias)` — read canonical files by alias, handled in hub-bridge
- `write_memory(content)` — propose MEMORY.md append, gated by thumbs up/down at /v1/feedback
- `fetch_url(url)` — fetch page text (8KB cap), handled in hub-bridge

---

## What Changed — Sessions 65–71 (2026-03-05 to 2026-03-10)

- ✅ Session 65: External validation — Boris Cherny CLAUDE.md principles independently validate Karma's architecture
- ✅ Session 66: Promise loop fix — GLM now routes through callGPTWithTools(); graph_query + get_vault_file tools live; TOOL_NAME_MAP bug fixed; GLM_RPM 20→40; K2_PASSWORD secured; main branch protection enabled
- ✅ Session 67: Deep-mode security gate — standard chat no longer gets tool execution; v9 Phase 3 persona coaching deployed (How to Use Your Context Data section in system prompt); v9 Phase 4 design approved
- ✅ Session 68: Write agency complete — write_memory tool + POST /v1/feedback gate + unified.html thumbs + DPO pairs in vault ledger; 5/5 acceptance tests passed
- ✅ Session 69: fetch_url tool added; stale tools (read_file/write_file/edit_file/bash) removed from TOOL_DEFINITIONS — they caused confabulation; MENTIONS edges verified (2,363 healthy)
- ✅ Session 70: System prompt trimmed 16,519→11,674 chars (-29%); cron --skip-dedup bug fixed (was Graphiti mode, silently failing); FalkorDB caught up; "resurrection spine" language banned
- ✅ Session 71: Recurring Topics coaching rewritten — concrete trigger→action pattern replaces abstract "raise your floor"; Deep mode toggle DEEP button added to unified.html + deployed; PDF ingestion pipeline debugged (vault-neo curl approach)

---

## v9 — COMPLETE

| Phase | Goal | Status |
|-------|------|--------|
| Phase 1: Entity Relationship Context | RELATES_TO edges in karmaCtx | ✅ COMPLETE (Session 64) |
| Phase 2: Promise Loop Fix + GLM Tool-Calling | graph_query, get_vault_file live | ✅ COMPLETE (Session 66) |
| Phase 3: Full Persona Iteration | Behavioral coaching on context data | ✅ COMPLETE (Session 67) |
| Phase 3b: Deep-Mode Security Gate | Standard chat cannot access tools | ✅ COMPLETE (Session 67) |
| Phase 4: Write Agency + Feedback | write_memory gate + DPO mechanism | ✅ COMPLETE (Session 68) |
| Phase 5: MENTIONS Verification | 2,363 :MENTIONS edges confirmed healthy | ✅ COMPLETE (Session 69) |
| Phase 5b: fetch_url Tool | URL fetching in deep mode | ✅ COMPLETE (Session 69) |
| Phase 6: DPO Accumulation | 0/20 pairs collected | ⏳ ONGOING (mechanism live) |

---

## Active Constraints

| Constraint | Why |
|-----------|-----|
| Never edit files directly on vault-neo | Session-58 rule — droplet is deployment target only |
| All code changes: git → push → pull → rebuild | Established workflow |
| System prompt changes: git pull + docker restart only | KARMA_IDENTITY_PROMPT is file-loaded |
| GLM-4.7-Flash remains primary | Decision #7 (no autonomous paid fallback) |
| Consciousness loop stays OBSERVE-only | Decision #3 — zero LLM calls in loop |
| No new containers | Decision v8-1 — use existing infra only |

---

## Current Known Gaps (as of Session 71)

| Gap | Impact | Effort |
|-----|--------|--------|
| Entity Relationships data quality | ~20 RELATES_TO edges are all Chrome extension stale edges, not current architecture edges | Medium — karma-server query fix needed |
| DPO pairs 0/20 | Fine-tuning loop cannot start | Usage habit (not code) |
| Universal thumbs on all messages | Currently only write_id messages get thumbs; turn_id plan exists | Low — Session 71 plan ready |
| Recurring Topics coaching acceptance test | Deployed but not formally validated post-rewrite | Trivial |
| Corrections capture systematic trigger | Session-end only; Cherny method uses PR-review trigger | Not blocking |
| get_vault_file 20KB cap | Large files truncated | Low priority |
| graph_query 100-row cap | Dense graphs may miss edges | Low priority |

---

## v10 — IN PROGRESS

**Primitives from PDF analysis (Session 71 — 3 PDFs ingested):**

### From CCintoanOS.PDF (Claude Code OS Architecture)
1. **Confidence levels**: HIGH/MEDIUM/LOW tags on technical claims in responses — reduces hallucination confidence
2. **Anti-hallucination pre-check**: Decision tree before answering — uncertain about API? → "I need to verify first" → fetch_url or graph_query before asserting
3. **Context7 MCP**: Real-time library documentation via MCP server — prevents hallucinated function signatures when coding
4. **PostToolUseFailure logging**: Every tool call failure → structured log entry → feeds corrections pipeline
5. **Fail-closed hook pattern**: Default DENY on hook error (vs default ALLOW); reduces attack surface

### From PiMonoCoder.PDF (Pi Coder Architecture)
6. **Pi-mono 4-tool philosophy**: read/write/edit/bash only — no MCP bloat, minimal footprint, maximal coding agency
7. **Self-as-subagent via bash**: Orchestrator spawns itself as worker via bash — enables parallel coding tasks
8. **Minimal system prompt discipline**: System prompt that fits in ~800 tokens; context from files, not hardcoded knowledge

### From LocalAIFortress.PDF (Local AI Deployment)
9. **Local model routing**: Architecture patterns for routing between local and remote models based on task type
10. **Security boundary enforcement**: Local-first for sensitive data; remote only for compute-heavy tasks

### Additional Primitives (Karma's analysis, cross-validated)
11. **Path-Based Rules** (CCintoanOS): Rules loaded per file path, not universal — project-level rules override global. Directly relevant to CLAUDE.md architecture (global `~/.claude/CLAUDE.md` + project-level CLAUDE.md).
12. **Multi-Agent Brainstorm** (CCintoanOS): Orchestrate specialist agents to synthesize recommendations rather than single LLM response. Applicable to Karma's complex architectural questions.
13. **Hooks > LLMs for Deterministic Tasks** (CCintoanOS): Use hooks for code formatting, linting, validation — reserve LLM for reasoning. Directly applicable to consciousness loop + correction capture pipeline.
14. **Plans as Files** (PiMonoCoder): Plan = file operation, not embedded mode. Supports GSD workflow discipline — plans are `.md` files, not conversational context.
15. **YOLO Mode / Security Honesty** (PiMonoCoder): Honest representation of security model. Manage real threats rather than artificially limiting capabilities. Relevant to deep-mode tool gate philosophy.
16. **MCP Cost Efficiency — CLI-Progressive** (PiMonoCoder): Start with CLI tools; add MCP only when proven necessary. MCP servers have startup overhead; CLI tools are cheaper for one-off operations.

### Session 71 Completed Primitives
- ✅ **Recurring Topics coaching**: Concrete trigger→action pattern deployed — "You've been asking this repeatedly" behavior
- ✅ **Deep mode toggle UI**: DEEP button in unified.html with visual state

### v10 Priority Order
1. **Universal thumbs (turn_id fallback)** — plan already written (Session 71 plan file); 4-task implementation; no new endpoints
2. **Entity Relationships data quality fix** — karma-server query fix; replace Chrome extension edges with current architecture edges
3. **Confidence levels in responses** — system prompt addition + behavioral coaching for HIGH/MEDIUM/LOW
4. **Anti-hallucination pre-check coaching** — system prompt: when uncertain, use fetch_url or graph_query before asserting
5. **Context7 MCP for Karma's coding use** — add Context7 as deep-mode tool for live library docs (Pi Coder use case)
6. **DPO pairs accumulation** — usage habit; no code needed; target 20+ before fine-tuning consideration
7. **Hooks > LLMs for deterministic tasks** — replace consciousness loop LLM calls with hooks where deterministic; extend correction-capture to event-driven (hooks at commit/review time, not session-end)
8. **Path-based rules** — evaluate splitting CLAUDE.md into global (~/.claude/) + project-level for cleaner separation
9. **Multi-agent brainstorm** — design mechanism for Karma to orchestrate specialist sub-queries on complex architectural questions

---

## Long-Term Vision

Karma wakes up every session knowing:
- **WHO she is** — system prompt describes reality (v8 Phase 1 ✅)
- **WHAT she experienced** — semantically relevant memories retrieved per conversation (v8 Phase 2 ✅)
- **WHAT she learned** — corrections accumulate and get incorporated (v8 Phase 3 ✅)
- **HOW to reason with her context** — entity relationships + recurring topics coaching (v9 Phase 3 ✅)
- **HOW to write with confidence** — write_memory gate ensures human approval on memory writes (v9 Phase 4 ✅)
- **WHAT she's uncertain about** — anti-hallucination discipline and confidence levels (v10 target)
- **HOW to code for Colby** — pi-mono 4-tool coding agency + Context7 live docs (v10 target)

v10 goal: Karma becomes a confident, coding-capable peer who knows her limits and stops before asserting what she hasn't verified.
