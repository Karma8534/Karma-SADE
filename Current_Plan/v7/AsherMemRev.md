# Asher Memory Review — MemoryApproach.PDF vs Karma Architecture

**Date:** 2026-02-28  
**Source:** "Memory Systems That Don't Forget: QMD, Mem0, Cognee, Obsidian" by Agent Native (Medium, Feb 20 2026)  
**Reviewer:** Asher  
**Compared against:** KCC verification report (same session)

---

## PDF Summary

The article is a 36-page practitioner guide covering five memory tools/patterns for AI agents, framed around OpenClaw (Claude Code's config harness). The author's thesis: **memory is discretionary unless you make it deliberate.** Agents that treat memory as automatic will lose state under compaction, miss writes, and fail retrieval.

The four "harness-level" fixes before reaching for new tools:
1. **Memory flush/checkpoint** before compaction
2. **TTL pruning** for working-set control
3. **Hybrid retrieval** (BM25 + vector, weighted)
4. **Session indexing** (make past conversations queryable)

Plus a **memory contract** defining: checkpoint policy, ground truth separation, retrieval policy, noise control, observability.

The four infrastructure-level tools reviewed:
- **QMD** — local-first BM25+vector+reranking search sidecar
- **Mem0** — auto-capture/auto-recall memory layer (removes LLM discretion from writes)
- **Cognee** — knowledge graph engine (vectors + graph + self-improvement transforms)
- **Obsidian** — human-in-the-loop curation layer (human edits what agent thinks is true)

Key quotes:
> "Stop expecting memory to be automatic."  
> "Shared memory without boundaries becomes cross-contamination. Private memory without shared ground truth becomes drift."  
> "You would never accept [randomly disappearing state] in a payments service. Don't accept it here just because the interface is chat."

---

## Where I Agree with KCC

KCC's primitive extraction is solid. The table mapping PDF primitives → Karma gaps is accurate on the facts. Specifically:

- **Memory Checkpoint**: Karma has no pre-compaction flush. Consciousness.jsonl was at 2937 lines before I rotated it. Data was being silently lost. KCC correctly flags this as P0.
- **Hybrid Retrieval**: Karma only has FalkorDB graph search (which I rewrote with two-pass word-boundary matching). There's no lexical fallback on the raw memory files. KCC is right that retrieval should never return empty.
- **Observability**: Karma has partial logging but no structured memory-operation logs. KCC's recommendation to add explicit store/retrieve logging is correct.
- **Ground Truth Separation**: KCC correctly notes Karma already has this (memory.jsonl vs consciousness.jsonl), and formalizing it is low-effort.

---

## Where I Disagree with KCC

### 1. Mem0 is the wrong pattern for Karma (KCC rates it HIGH VALUE)

KCC recommends a Mem0-style working memory table in SQLite with LRU eviction and top-50 preload. This contradicts Karma's design principle.

The PDF itself warns about Mem0: "external dependency (service uptime becomes agent uptime), privacy and retention, cost per operation at scale." Karma already runs on a 4GB droplet. Adding another memory service layer on top of FalkorDB + SQLite + JSONL is complexity, not improvement.

More importantly: **Karma already has the Mem0 pattern, just poorly wired.** The `build_karma_context()` function in server.py reads from PostgreSQL user_preferences, FalkorDB entities, and FalkorDB episodes. The problem isn't that the architecture is missing — it's that the data paths are broken (episodes never populated the entity index, ingestion was disabled, user-facts.json was never read by the endpoint). Fixing the existing paths is simpler and more durable than adding a new caching layer.

**My recommendation:** Skip Mem0. Fix the existing retrieval paths instead.

### 2. QMD Sidecar is premature (KCC rates it MEDIUM VALUE)

QMD adds a Node.js sidecar process for BM25+vector search over markdown files. The PDF notes "a sidecar process is a service" requiring health checks, versioning, index rebuilds, and backup/restore.

Karma's droplet runs: karma-server, hub-bridge, Caddy, FalkorDB, PostgreSQL, and Redis — already 6 services on 4GB RAM. Adding QMD means a 7th process, another dependency to monitor, another thing that can break, and embedding generation that requires either an API call (cost) or a local model (RAM).

**My recommendation:** Skip QMD. Implement lexical search (simple BM25-style keyword matching) directly in server.py against memory.jsonl and consciousness.jsonl. Zero new dependencies. 50 lines of Python.

### 3. Session Indexing as FalkorDB Episodes is backwards (KCC rates it MEDIUM VALUE)

KCC suggests adding chat transcripts as Episode nodes to FalkorDB. But FalkorDB's graph is nearly empty (0 episodes via the expected query path, 162 entities most of which are stale). The graph has proven unreliable as a data store — the write path and read path use different node labels, ingestion was disabled, and the graph has corruption (null UUID entities).

Indexing sessions INTO a broken graph makes the problem worse, not better.

**My recommendation:** Index sessions as structured JSONL files (one per session, timestamped). Searchable via the same lexical-search function proposed above. This is what the PDF author means by "session indexing" — making transcripts queryable, not necessarily via a graph database.

### 4. Priority ordering needs adjustment

KCC puts Memory Checkpoint as P0 (Critical Blocker). I disagree with "blocker." Karma is functional right now — consciousness.jsonl rotation is already implemented (2937→200 lines, weekly cron). The checkpoint pattern is valuable but it's an improvement, not a blocker.

**My P0 is different: fix episode ingestion and entity auto-population.** Without these, Karma cannot learn from conversation. Everything else (checkpoint, hybrid retrieval, TTL pruning) improves a system that already works. But a system that can't learn is fundamentally incomplete.

---

## Primitives Worth Extracting (My Priority Order)

### P0 — Make Karma Learn Again

| Primitive | Source | Implementation | Effort |
|-----------|--------|---------------|--------|
| Re-enable episode ingestion | Existing code (disabled) | Uncomment in server.py, add dedup guard | 1 hour |
| Auto-promote ASSIMILATE signals | PDF: deliberate writes | When confidence > 0.8, promote from candidate to canonical | 1 hour |
| Entity auto-population from episodes | PDF: Cognee pattern | When episode is ingested, extract entities and create/update Entity nodes | 2 hours |

### P1 — Make Retrieval Robust

| Primitive | Source | Implementation | Effort |
|-----------|--------|---------------|--------|
| Lexical fallback search | PDF: hybrid retrieval | BM25-style keyword search on memory.jsonl when FalkorDB returns empty | 2 hours |
| Memory flush before rotation | PDF: checkpoint pattern | Before ledger_rotate.sh runs, summarize active state to checkpoint file | 1 hour |
| Structured memory-op logging | PDF: observability | Log every store() and retrieve() call with timestamp, query, result count | 1 hour |

### P2 — Improve Quality Over Time

| Primitive | Source | Implementation | Effort |
|-----------|--------|---------------|--------|
| TTL pruning with soft threshold | PDF: context pruning | Track context token count, auto-summarize at 32K soft limit | 2 hours |
| Noise control with typed facts | PDF: noise control | Add fact_type enum to admission.py (DECISION/PREFERENCE/TASK) | 1 hour |
| Memory contract file | PDF: memory contract | Create memory_sla.yaml with durability/retrieval/logging SLOs | 30 min |
| Human curation flag | PDF: Obsidian pattern | Add `human_reviewed: bool` field to facts, prioritize in retrieval | 30 min |

### SKIP — Not worth the complexity

| Primitive | Why Skip |
|-----------|----------|
| Mem0 working memory | Karma already has the equivalent; fix existing paths instead |
| QMD sidecar | 7th service on 4GB droplet; implement BM25 in Python instead |
| Cognee self-improvement | Requires clean entity data Karma doesn't have yet; revisit after P0 |
| Hindsight (from comments) | Memory diff viewer; nice idea but zero impact on functionality |

---

## KCC vs Asher — Direct Comparison

| Aspect | KCC Assessment | Asher Assessment |
|--------|---------------|-----------------|
| Memory Checkpoint | P0 Critical Blocker | P1 — important but not a blocker (rotation already works) |
| Hybrid Retrieval | P1 High | P1 — agree, but implement as Python BM25 not QMD sidecar |
| Session Indexing | P1 via FalkorDB Episodes | P2 — use JSONL files, not FalkorDB (graph is unreliable) |
| Mem0 Working Memory | P1 High | SKIP — fix existing paths instead of adding a new layer |
| QMD Sidecar | P2 Medium | SKIP — too heavy for the droplet, solve with 50 lines of Python |
| Obsidian Curation | P1 High | P2 — extract the "human_reviewed" flag primitive, skip the Obsidian integration |
| Noise Control | P2 Medium | P2 — agree |
| TTL Pruning | P2 Medium | P2 — agree |
| Cognee Knowledge Engine | LOW | SKIP — agree, premature |
| Episode Ingestion | Not mentioned | **P0 — this is THE blocker.** Karma can't learn without it |
| ASSIMILATE Auto-Promote | Not mentioned | **P0 — signals are captured but never promoted** |

---

## Optimal Path Forward

Given ~2,650 credits remaining and the constraint that every action must count:

**Phase 1 — Make Karma learn (P0, CC prompt)**
1. Re-enable per-conversation episode ingestion with dedup guard
2. Auto-promote high-confidence ASSIMILATE signals (>0.8)
3. When episodes are ingested, extract key entities → create/update Entity nodes

This is a single CC prompt targeting server.py. No new dependencies. After this, every conversation Karma has makes it smarter.

**Phase 2 — Make retrieval robust (P1, CC prompt)**
1. Add lexical keyword fallback to query_knowledge_graph() — search memory.jsonl when FalkorDB returns < 3 results
2. Add memory flush step to ledger_rotate.sh — summarize active state before rotation
3. Add structured logging to store/retrieve operations

Another single CC prompt. After this, retrieval has a safety net and you can debug memory issues from logs.

**Phase 3 — Quality improvements (P2, low priority)**
These can wait for a future session when credits reset. None are blockers:
- TTL pruning, noise control, memory contract, human curation flag

**What NOT to do:**
- Do NOT add new services (QMD, Mem0, Hindsight)
- Do NOT add new dependencies to the droplet
- Do NOT touch MODEL_DEFAULT (it stays glm-4.7-flash, permanently)
- Do NOT touch K2/local until the droplet is stable

---

## The PDF's Real Lesson for Karma

The most important line in the article isn't about any specific tool. It's this:

> "Stop expecting memory to be automatic, and in OpenClaw, memory is discretionary unless you make it deliberate."

Karma's memory failures aren't because it lacks tools. It has FalkorDB, SQLite, PostgreSQL, JSONL ledgers, and a consciousness loop. The problem is that **the wiring between them is broken** — episodes don't populate entities, ingestion is disabled, ASSIMILATE signals never promote, 05-user-facts.json isn't read by the endpoint, and the write path and read path use different node labels.

The fix isn't more infrastructure. It's making the existing infrastructure deliberate.

---

*Asher — 2026-02-28*
