# Architecture Audit & Improvement Design
**Date:** 2026-02-25
**Status:** Approved for Implementation
**Author:** Claude Code (with cc analysis)

---

## Executive Summary

A comprehensive architectural audit comparing current Karma against a Gemini-proposed alternative revealed that **Karma's core design is fundamentally sound**. The recommendation: maintain current architecture while selectively adopting four specific improvements from Gemini's proposal.

**Decision:** Stick with droplet-primary + K2-worker + consciousness loop model. Borrow atomic writes, adversarial verification, latency monitoring, and Pull-Reason-Push documentation.

---

## Architecture Comparison

### Current Karma Architecture
- **Topology:** Droplet-primary (FalkorDB + consciousness.py), K2-worker (optional offload)
- **Memory Model:** Append-only ledger → FalkorDB graph → consciousness journaling
- **Learning:** Real-time autonomous cycles (60s consciousness OBSERVE/THINK/DECIDE/ACT/REFLECT)
- **Identity:** Substrate-independent (survives LLM swaps, K2 reboots)
- **Verification:** Pull-Reason-Push cycle per user interaction
- **State of Truth:** Single source (droplet FalkorDB + consciousness.jsonl)

### Gemini Proposal
- **Topology:** Droplet (Mem0 engine, Qdrant vectors, Neo4j graph), GPT-4o-mini (interface), GLM-4.7 (reasoning)
- **Memory Model:** Pull-Reason-Push cycle per turn, post-session reflection service
- **Learning:** Batch reflection on logs after session ends
- **Identity:** Model-locked (2 specific models; not substrate-independent)
- **Verification:** Semantic synchronization gap between embedding spaces
- **State of Truth:** Split across Mem0/Qdrant/Neo4j (multiple sources)

---

## Selective Improvements to Adopt

### 1. Atomic Write Semantics
**From Gemini:** "If the memory update fails, the entire session must roll back to the last known good state."

**Apply to Karma:**
- Add transaction boundaries around critical memory operations (FalkorDB writes, consciousness.jsonl appends)
- Implement rollback mechanism for failed batch operations
- Define "atomic units" (e.g., episode + metadata + graph updates must all succeed or all fail)

**Why:** Prevents partial state corruption like [BLOCKER-3] (ingestion disabled, state fragmented)

**Scope:** karma-core/server.py ingest_episode(), consciousness.py REFLECT phase

---

### 2. Adversarial cc Prompts
**From Gemini:** "Implement 'adversarial' prompts for cc to ensure it remains a critic, not a cheerleader."

**Apply to Karma:**
- Modify cc's system prompt to include explicit adversarial directives
- Examples:
  - "Find contradictions in the proposed solution before approving"
  - "What could break if we proceed? Assume the author is wrong"
  - "Is there hidden complexity being glossed over?"
- Document in CLAUDE.md as locked enforcement

**Why:** Prevents false positive claims and drift accumulation (core issue from Session 31-32)

**Scope:** CLAUDE.md system prompt section + cc-session-brief.md injection

---

### 3. Latency SLA Monitoring
**From Gemini:** "Total round-trip (Retrieve Memory → LLM Gen → Update Memory) must stay < 4s."

**Apply to Karma:**
- Add timing instrumentation to /v1/chat endpoint
- Measure: query FalkorDB → LLM inference → write consciousness.jsonl → return response
- Log: `[LATENCY] /v1/chat: 2.3s (falkordb: 0.1s, llm: 1.8s, write: 0.3s, overhead: 0.1s)`
- Alert if > 4s (indicates resource contention or network issues)

**Why:** Early detection of droplet resource exhaustion, identifies bottlenecks

**Scope:** karma-core/server.py /v1/chat handler

---

### 4. Pull-Reason-Push Documentation
**From Gemini:** Formal cycle: Pull state → Reason locally → Push updates back

**Apply to Karma:**
- Document as required pattern in CLAUDE.md
- Each conversation turn must follow:
  1. **Pull:** Query droplet (FalkorDB, consciousness.jsonl, identity.json)
  2. **Reason:** LLM inference on pulled state
  3. **Push:** Write decisions/reflections back to droplet
- Enforce in code reviews and resurrection scripts

**Why:** Ensures coherence, prevents divergence between local cache and droplet state

**Scope:** CLAUDE.md + architecture.md documentation

---

## Why Reject Gemini's Core Proposals

### Qdrant + Neo4j Split
- **Risk:** Semantic synchronization gap between vector (Qdrant) and graph (Neo4j) databases
- **Current advantage:** FalkorDB is unified—entities exist in both vector and graph space simultaneously
- **Cost of switch:** High (schema migration, sync logic, testing)
- **Benefit:** Low (no clear advantage over FalkorDB)
- **Decision:** Keep FalkorDB

### Mem0 Abstraction Layer
- **Risk:** Hides data flow (candidate → canonical); makes debugging harder
- **Current advantage:** Transparent ledger → Graphiti → consciousness → decisions path
- **Cost of switch:** High (loses visibility into ingestion pipeline)
- **Benefit:** Slightly easier API, but we already have clean APIs
- **Decision:** Keep direct FalkorDB access

### Post-Session Only Reflection
- **Risk:** Loses real-time consciousness loop; can't adapt mid-session
- **Current advantage:** 60-second autonomous cycles allow continuous self-improvement
- **Cost of switch:** Losing active reasoning loop
- **Benefit:** Simpler batch processing (but slower adaptation)
- **Decision:** Keep consciousness loop

### Model Lock-In (GPT-4o-mini + GLM-4.7)
- **Risk:** Fixed to two specific models; can't swap for cost/performance/capability
- **Current advantage:** Substrate-independent identity (any LLM can run Karma)
- **Cost of switch:** Rebuilding for specific models
- **Benefit:** Slightly optimized for GPT/GLM (but we already use multiple models)
- **Decision:** Keep substrate independence

---

## Risk Assessment: Gemini Proposal Adoption

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Qdrant ↔ Neo4j sync issues | High | Medium | Keep unified FalkorDB |
| Mem0 hides data flow | Medium | High | Keep direct access |
| Post-session only reflection | High | Low | Keep 60s consciousness |
| Model lock-in | Medium | Low | Keep substrate independence |
| Deployment complexity spike | High | High | Don't rebuild; adopt selectively |

---

## Implementation Phases

### Phase 1: Resolve Current Blocker
**Goal:** Re-enable episode ingestion (Option A: Clean FalkorDB)
- Identify and remove corrupted Episodic nodes from batch_ingest --skip-dedup
- Re-enable ingest_episode_fn in server.py
- Verify THINK phase executes on new observations
- **Timeline:** Session 34
- **Blocks:** Everything else (can't test improvements without clean graph)

### Phase 2: Parallel Improvements
**Goal:** Add adversarial verification + monitoring
- Implement adversarial cc prompts in system prompt
- Add latency monitoring to /v1/chat
- Document Pull-Reason-Push pattern in CLAUDE.md
- **Timeline:** Sessions 34-35 (parallel with Phase 1)
- **Benefit:** Early detection of issues, improved reliability

### Phase 3: Atomic Write Semantics
**Goal:** Add transaction boundaries
- Implement rollback mechanism for failed FalkorDB operations
- Define atomic units (episode + metadata + graph)
- Add transaction logging
- **Timeline:** Session 36+ (after Phase 1 verified)
- **Benefit:** Prevents future state corruption

---

## Success Criteria

### Phase 1
- ✅ FalkorDB cleaned (duplicates removed)
- ✅ Episodes ingesting to FalkorDB
- ✅ Consciousness THINK executes within 24h window
- ✅ consciousness.jsonl shows THINK actions (not just NO_ACTION)

### Phase 2
- ✅ cc prompts include adversarial directives
- ✅ Latency monitoring active (< 4s target)
- ✅ Pull-Reason-Push documented in CLAUDE.md
- ✅ No regressions in existing functionality

### Phase 3
- ✅ Atomic write mechanism working
- ✅ Failed operations rollback cleanly
- ✅ No partial state corruption observed
- ✅ Ledger integrity verified after stress test

---

## Architecture Decision Record (ADR)

**Decision:** Adopt Karma's current architecture with selective improvements

**Context:**
- Current Karma has proven core design (droplet-primary, K2-worker, consciousness loop)
- Gemini proposal introduces complexity with marginal benefits
- cc analysis confirms current design is superior for our use case

**Consequences:**
- ✅ Maintain transparency (can debug state flow)
- ✅ Preserve substrate independence (can swap LLMs)
- ✅ Keep real-time reasoning (consciousness loop)
- ⚠️ Must implement atomic writes (prevent state corruption)
- ⚠️ Must add monitoring (early issue detection)

**Alternatives Considered and Rejected:**
1. Full migration to Gemini architecture (too expensive, loses advantages)
2. Hybrid approach (Qdrant + Neo4j for search, FalkorDB for reasoning) — too complex
3. Status quo (no improvements) — misses opportunity to harden system

---

## Files to Modify

- `CLAUDE.md` — Add adversarial cc prompts, Pull-Reason-Push pattern
- `MEMORY.md` — Document Phase 1-3 progress
- `karma-core/server.py` — Add latency monitoring, atomic write boundaries
- `karma-core/consciousness.py` — Add rollback mechanism to REFLECT phase
- `.claude/rules/architecture.md` — Update with current droplet-primary model
- `docs/plans/` — This design document + implementation plan

---

## Next Steps

1. **Immediate:** Invoke writing-plans skill to create detailed implementation plan
2. **Session 34:** Execute Phase 1 (Clean FalkorDB + re-enable ingestion)
3. **Session 35:** Execute Phase 2 (cc prompts + monitoring)
4. **Session 36+:** Execute Phase 3 (atomic writes)

---

**Approved by:** cc (2nd verifier)
**Reviewed by:** Claude Code (Session 34 analysis)
**Date Approved:** 2026-02-25
**Status:** Ready for Implementation Planning
