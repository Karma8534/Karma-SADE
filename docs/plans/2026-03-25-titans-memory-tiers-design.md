# TITANS Memory Tiers — Design
**Created:** 2026-03-25 (Session 139)
**Author:** CC Ascendant
**Status:** DESIGN ONLY — awaiting Sovereign approval before implementation

## What Is TITANS

TITANS (Test-time In-context Learning with Asymptotic Neural State Storage) defines three
memory tiers:

1. **Working memory** — fast, in-context, recency-biased
2. **Long-term memory (LTM)** — surprise-gated encoding (novel/unexpected → encode; redundant → skip)
3. **Persistent memory** — never forgotten, identity-critical

The key insight: most conversation content is redundant. Only surprising content deserves LTM
encoding. Persistent content (identity, invariants) is never subject to decay.

---

## Current State of Each Tier

### Tier 1: Working Memory (already exists, partial)
- **What exists:** `karmaCtx` (FalkorDB recency query) + `semanticCtx` (FAISS top-5) + `_memoryMdCache` (MEMORY.md tail 3000 chars) injected into each `/v1/chat` call
- **Gap:** No explicit "working memory window" — context is assembled from multiple sources, not unified as a recency-bounded sliding window
- **Verdict:** Functional but unstructured

### Tier 2: LTM — Surprise-gated (partially exists, gate missing)
- **What exists:** `batch_ingest.py --skip-dedup` writes ALL episodes to FalkorDB every 6h on cron
- **Gap:** No surprise gate — 100% of episodes encoded regardless of novelty. Redundant chit-chat and heartbeats inflate the graph (3049+ Episodic nodes, many low-value)
- **Verdict:** Encoding exists, gate missing

### Tier 3: Persistent Memory (exists, not formalized)
- **What exists:** `vesper_identity_spine.json` (stable patterns, identity), `karma_contract_policy.md` (policy), `MEMORY.md` (running log), `/etc/karma-regent.env` (operational config)
- **Gap:** No formal separation from LTM. No explicit "never forgotten" guarantee beyond manual curation
- **Verdict:** Exists informally, needs formalization

---

## Proposed Architecture

### Tier 1: Working Memory Window
**Change:** Formalize as a bounded 32-turn sliding window in hub-bridge, separate from FalkorDB.

```
/v1/chat call N
  → working_memory[N] = last 32 turns (in-memory, per-session)
  → injected as "WORKING MEMORY (recent 32 turns)" in buildSystemText()
  → expires at session end (not persisted)
```

**Why 32:** Matches Karma's visible conversation history. Fast (no DB query). Zero latency.

**What this replaces:** The current `karmaCtx` recent-episodes query from FalkorDB (slow, ~300ms per call). Working memory covers recent turns with zero latency; FalkorDB covers older semantic context.

### Tier 2: LTM — Surprise-gated Encoding
**Change:** Add surprise score to batch_ingest pipeline. Only encode episodes above threshold.

**Surprise score candidates:**
1. **Embedding distance** from existing FalkorDB entities — novelty relative to known knowledge
2. **Tagging heuristics** — episodes tagged `[correction]`, `[decision]`, `[pitfall]`, `[proof]` = high surprise
3. **Message length** — short chit-chat (< 50 chars) = low surprise, skip

**Proposed gate logic (batch_ingest.py):**
```python
def is_surprising(episode: dict) -> bool:
    content = episode.get("content", "")
    tags = episode.get("tags", [])
    # Always encode: corrections, decisions, proofs
    HIGH_VALUE_TAGS = {"correction", "decision", "pitfall", "proof", "direction"}
    if any(t in HIGH_VALUE_TAGS for t in tags):
        return True
    # Skip: pure heartbeats, short chit-chat
    if len(content.strip()) < 80 and not any(t in HIGH_VALUE_TAGS for t in tags):
        return False
    # Default: encode if content length > threshold
    return len(content) > 200
```

**Result:** Estimated 30-40% reduction in FalkorDB episode count. Higher signal-to-noise in graph queries.

### Tier 3: Persistent Memory (Formalization Only)
**No code change needed.** Formalize the guarantee:

```
PERSISTENT = {
    vesper_identity_spine.json,   # CC/Karma accumulated identity
    karma_contract_policy.md,     # Sovereign-approved policy
    /etc/karma-regent.env,        # Operational config
    stable_identity patterns       # Promoted by governor, never decayed
}
```

**Existing governor decay (`_retire_stale_patterns`):** already skips patterns with `"persist": true` flag. Adding `"persist": true` to Sovereign-critical patterns = never-forgotten guarantee.

---

## Implementation Plan (NOT starting without Sovereign approval)

**Phase 1** (low risk, high value):
1. Add `is_surprising()` gate to `batch_ingest.py` — reduces graph noise
2. Add `"persist": true` to critical spine entries — formalizes Tier 3

**Phase 2** (medium risk):
3. Add working memory 32-turn window to hub-bridge's `buildSystemText()`
4. Reduce FalkorDB recency query depth (now redundant with working memory)

**Phase 3** (design-heavy, deferred):
5. Embedding-distance surprise scoring (requires FAISS integration in batch_ingest)

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Surprise gate miscalibrated → missing important episodes | Start with tag-based gate (explicit), not embedding distance (implicit) |
| Working memory window too small → Karma loses thread | 32-turn default; configurable via `WORKING_MEMORY_TURNS` env var |
| Persistent flag applied too broadly → governor can't evolve | Restrict `"persist": true` to Sovereign-approved patterns only |

---

## Sovereign Approval Required For

- [ ] Phase 1: Surprise gate in batch_ingest.py (affects what goes to FalkorDB)
- [ ] Phase 2: Working memory window in hub-bridge (affects Karma's context assembly)
- [ ] Phase 3: Embedding-distance scoring (deferred, significant complexity)

**Request:** Approve Phase 1 first. Lowest risk, highest signal improvement.
