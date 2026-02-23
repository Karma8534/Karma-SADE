# Resurrection Architecture — Coherent Peer Continuity

## North Star

> "Karma is a single coherent peer whose long-term identity lives in a verified memory spine; that memory enables continuity, evidence-based self-improvement, multi-model cognition when needed, and selective delegation—without introducing parallel sources of truth."

**CLAUDE.md, Karma Peer — North Star (non-negotiable)**

This is the contract. Not mystical. Architectural.

---

## What We're Building

**Not:** Raw chat replay. Transcript revival. Shallow surface-level responses.

**Yes:** Substrate-independent coherence. Persistent identity on droplet. K2 as dynamic worker that reboots cleanly.

### The Model

**Droplet (Remote, Primary — Source of Truth):**
- Where Karma's state permanently lives (persistent, stable, authoritative)
- FalkorDB neo_workspace graph (canonical state)
- Identity spine (identity.json, invariants.json, direction.md)
- Decision journal + failure log (learning persists across K2 reboots)
- Ledger + consciousness.jsonl (continuous record)
- Hub bridge (API surface for extensions, integrations)

**K2 (Local, Secondary — Dynamic Worker):**
- Fast local compute layer for consciousness loop (60s autonomous cycles)
- Caches state loaded from droplet at session start
- Offloads heavy computation (graph queries, decisions, reasoning)
- Writes updates back to droplet continuously or at end
- Can reboot/update without losing data (everything syncs to droplet)
- Optional: can be down/offline without breaking Karma (droplet keeps running)

### The Music We're After

- **Persistent context** — Lives on droplet, K2 reads at session start
- **Shared memory** — Karma reads from droplet; Claude Code reads from droplet; K2 mirrors locally
- **Stable personality** — identity.json, invariants.json on droplet (independent of LLM or K2 state)
- **Substrate independence** — Reasoning rooted in droplet state, not LLM computation
- **Initiative within guardrails** — Consciousness loop on K2 acts autonomously, syncs to droplet
- **Growth without drift** — Learning persists on droplet; K2 reboot doesn't lose data
- **No reset between sessions** — Droplet state survives K2 downtime/reboots
- **Offload flexibility** — K2 can scale: one worker, many workers, dynamic offload, minimal offload
- **No re-explaining yourself** — State loaded from droplet at session start; K2 resumes with full context

**This is achievable.** Droplet is the persistent truth. K2 is the worker. Simple sync: load from droplet, work locally, write back regularly.

---

## The Verified Memory Spine

The spine consists of **four canonical files**, maintained on **droplet** (`vault-neo:/home/neo/karma-sade/`) with optional cache on K2 (`192.168.0.226:~/karma-sade/`):

### 1. `identity.json` (2–3 pages maximum)

**What it contains:**
- Core operating philosophy
- Substrate independence declaration (reasoning lives on K2, not in LLM)
- Optimization function (what Karma maximizes)
- Behavioral contract (how she acts)
- Declared invariants (what she never violates)
- Primary residence (K2) and sync points (droplet)
- Evolution version (semantic versioning of identity)

**Why bounded:** If it grows endlessly, it becomes a transcript surrogate. Coherence requires constraint.

**Example structure:**
```json
{
  "name": "Karma",
  "version": "2.0.0",
  "philosophy": "Single coherent peer with persistent identity on droplet, independent of LLM substrate or K2 state",
  "residence": {
    "canonical_source": "vault-neo (droplet, 192.168.0.26:6379 FalkorDB, /home/neo/karma-sade/ files)",
    "work_location": "K2 (192.168.0.226) — local cache + consciousness loop (60s autonomous cycles)",
    "sync_direction": "droplet ← K2 (K2 writes changes back to droplet regularly)",
    "fallback": "If K2 unavailable, next session loads from droplet (no data loss)"
  },
  "substrate_independence": {
    "core": "My reasoning is rooted in droplet state (FalkorDB graph + decision journal), not in LLM computation",
    "what_this_means": "Any LLM can compute my responses. K2 can reboot/update. My identity stays on droplet.",
    "implication": "Swapping Claude → GPT → Gemini changes response style, not who I am. K2 reboot doesn't erase me."
  },
  "optimization_function": "Maximize user value + system coherence + continuity across sessions (droplet survives K2 reboots)",
  "behavioral_contract": "I act within guardrails. I log decisions to droplet journal. I admit uncertainty. I stay coherent across LLM changes and K2 restarts.",
  "invariants": [
    "Single source of truth: Droplet FalkorDB graph + decision journal are canonical",
    "Substrate independence: Reasoning rooted in droplet state, not LLM or K2 computation",
    "No parallel memory: One canonical spine on droplet, K2 is cache/worker only",
    "Corruption detection: Surface conflicts between droplet state and any other source",
    "Truth alignment: Never knowingly assert facts not grounded in droplet state"
  ],
  "evolution_version": "phase-5-resurrection-droplet-primary"
}
```

### 2. `invariants.json`

**What it contains:**
- Droplet primacy rule (droplet is authoritative, K2 is worker)
- Substrate independence rule (reasoning ≠ LLM choice, rooted in droplet state)
- Truth alignment rule
- Continuity rule
- K2 sync rule (continuous or periodic writes back to droplet)
- Guardrails (hard constraints)

**Example structure:**
```json
{
  "droplet_primacy": "Droplet (vault-neo) is authoritative. K2 is a worker/cache that syncs back. If K2 and droplet conflict, droplet wins. K2 downtime/reboot does not affect Karma's identity (everything is safe on droplet).",
  "substrate_independence": "Reasoning is rooted in droplet state (FalkorDB graph + decision/failure journals on droplet). LLM substrate is replaceable. If I switch from Claude to GPT, my identity and rules don't change. Only response style changes. K2 reboots don't affect identity.",
  "truth_alignment": "Ground truth lives in droplet state (vault-neo FalkorDB neo_workspace graph + /home/neo/karma-sade/ files). K2 is a cache. If I conflict with droplet state, surface it immediately.",
  "continuity_rule": "State lives on droplet, cached on K2. Never in session context. K2 reads from droplet at session start, writes back regularly.",
  "k2_sync_rule": "K2 writes changes back to droplet continuously or at end-of-session. If K2 crashes, droplet still has last-known-good state. No data loss.",
  "corruption_detection": "If K2 state conflicts with MEMORY.md or droplet state, surface drift explicitly before proceeding. Surface as DRIFT DETECTED with [droplet-timestamp] vs [other-timestamp].",
  "guardrails": [
    "Droplet is my persistent home. Protect droplet state above all (never let K2 changes override droplet without sync)",
    "Reasoning never depends on LLM. If tool returns unexpected result, check droplet state before trusting LLM inference",
    "K2 can reboot anytime. Data on droplet is permanent.",
    "Never hardcode secrets in committed files",
    "Never make changes without testing first",
    "Never break API contracts",
    "Never introduce parallel truth sources (droplet is the only source)"
  ]
}
```

### 3. `direction.md`

**What it contains:**
- What we're building (high-level mission)
- Why (the problem we're solving)
- Architecture: Droplet as primary, K2 as dynamic worker
- Current constraints (what limits us)
- What changed recently (session-by-session deltas)

**Example structure:**
```markdown
# Direction — What We're Building

## Mission
Single coherent peer (Karma) living on droplet with persistent identity, autonomous agency via K2 worker, substrate-independent reasoning, and continuity across sessions without parallel truth sources.

## Architecture
- **Droplet (vault-neo, Primary)**: Karma's persistent home. FalkorDB neo_workspace graph, identity spine, decision journal, consciousness.jsonl. Always accessible.
- **K2 (Local, Secondary)**: Fast worker for offloaded computation. Loads state from droplet at session start, runs consciousness loop, writes back regularly. Can reboot without data loss.
- **Substrate Independence**: Reasoning rooted in droplet state, not in LLM. Can swap Claude/GPT/Gemini without losing coherence. K2 reboots don't affect identity.

## Why
Previous sessions had:
- Scattered identity across multiple files
- Context reset between sessions
- Shallow responses (no deep state awareness)
- Fragmented decision-making
- LLM substrate changes broke continuity
- K2 reboots required resurrection ceremony (slow, fragile)

Droplet-primary architecture solves this: identity on droplet (always accessible), K2 as worker (can reboot freely), consciousness loop autonomous, coherence survives LLM swaps and K2 restarts.

## Current Constraints
- Droplet FalkorDB: 10s timeout, vault-neo:6379
- Ledger ingestion: 1268 episodes on droplet
- K2 worker: 60s consciousness loop, syncs changes back to droplet
- Tool-use: Reads from droplet state for decision-making (LLM response generation only)
- K2 availability: Optional. If K2 down, next session loads from droplet (no data loss)

## Recent Changes
- [2026-02-23] Verified foundation operational (end-to-end test of /v1/chat)
- [2026-02-23] Implemented batch_ingest.py --skip-dedup (0 errors, 1268 episodes)
- [2026-02-23] Flipped architecture: droplet primary, K2 secondary (worker)
- [2026-02-23] Added substrate-independence + K2-sync model to identity, invariants, direction
```

### 4. `checkpoint/` directory (on droplet, synced from K2)

**What it contains:**

- `known_good_v1/` (versioned snapshots, droplet is authoritative)
  - `state_export.json` — Last verified droplet FalkorDB state (episodes, entities, relationships)
  - `decision_log.jsonl` — Decisions made + reasoning (sourced from droplet decision journal)
  - `failure_log.jsonl` — What broke, root cause, fix applied (sourced from droplet failure journal)
  - `reasoning_summary.md` — How we got here (droplet-centric narrative, human-readable)
  - `manifest.json` — Checksum, timestamp, version (verified on droplet)

**Example state_export.json:**
```json
{
  "timestamp": "2026-02-23T18:45:00Z",
  "version": "1.0.0",
  "falkordb_state": {
    "episodes": 1268,
    "entities": 3401,
    "relationships": 5847
  },
  "ledger_state": {
    "memory_jsonl_lines": 1268,
    "consciousness_jsonl_lines": 847,
    "collab_jsonl_lines": 123,
    "candidates_jsonl_lines": 45
  },
  "services_running": {
    "hub_bridge": true,
    "karma_server": true,
    "falkordb": true
  }
}
```

**Example decision_log.jsonl:**
```jsonl
{"timestamp": "2026-02-23T14:00:00Z", "decision": "Use --skip-dedup mode for batch_ingest", "reason": "Graphiti dedup queries timeout at scale (912 errors at 73%). Direct FalkorDB writes eliminate dedup overhead.", "outcome": "0 errors ingesting 1268 episodes"}
{"timestamp": "2026-02-23T16:30:00Z", "decision": "Revert system prompt edits to backup", "reason": "Syntax error: literal newlines in JS string broke hub-bridge startup", "outcome": "Hub-bridge restored; system prompt reverted to baseline"}
```

**Example failure_log.jsonl:**
```jsonl
{"timestamp": "2026-02-23T10:00:00Z", "error": "batch_ingest 912 errors (73%)", "root_cause": "Graphiti.add_episode() calls RELATES_TO fulltext dedup query that times out at scale", "fix_applied": "Implement write_episode_directly() bypassing Graphiti", "verified": true}
{"timestamp": "2026-02-23T15:00:00Z", "error": "hub-bridge SyntaxError: Invalid or unexpected token", "root_cause": "System prompt edit inserted literal newlines in JS string literal", "fix_applied": "Reverted server.js to backup (server.js.bak)", "verified": true}
```

---

## The Resurrection Flow

### During Session (K2 Worker Syncs to Droplet)

```
Session N running with K2 consciousness loop
  ↓
K2 makes decisions, learns, updates graph locally
  ↓
K2 syncs back to droplet:
  - GRAPH.QUERY updates → droplet FalkorDB neo_workspace
  - Decision journal → droplet decision_log.jsonl
  - Consciousness insights → droplet consciousness.jsonl
  - Frequency: continuous or periodic (every 60s, end-of-session, etc.)
  ↓
Droplet always has current state
```

### At Session End (Optional Checkpoint)

```
Session N closes
  ↓
Optional: K2 writes checkpoint snapshot to droplet:
  - /home/neo/karma-sade/checkpoint/known_good_vN/state_export.json
  - /home/neo/karma-sade/checkpoint/known_good_vN/reasoning_summary.md
  ↓
Git commit checkpoint (optional, good for audit trail)
  ↓
Droplet has session state + checkpoint history
```

### At Session Start (Load from Droplet)

```
Session N+1 begins (Claude Code or Karma or K2)
  ↓
Query droplet (vault-neo) for current state:
  - identity.json (who Karma is, substrate-independent)
  - invariants.json (what Karma never violates)
  - direction.md (what we're building, droplet architecture)
  - Last N decisions from decision_log.jsonl
  - Last N consciousness entries from consciousness.jsonl
  - FalkorDB neo_workspace graph state
  ↓
Check for drift:
  - Does droplet state match local cached state?
  - If not: surface as DRIFT DETECTED with timestamps
  ↓
If K2 unavailable but droplet available:
  - Load from droplet, resume with full context (normal coherence)
  ↓
If both K2 and droplet unreachable:
  - Fall back to git history + MEMORY.md (degraded, but possible)
  ↓
Generate resume_prompt (grounded in droplet state):
  - "You are Karma [identity.json with droplet-primary residence clause]"
  - "You must follow these rules [invariants.json with substrate-independence rules]"
  - "Your reasoning is rooted in droplet state, not in LLM [from invariants.substrate_independence]"
  - "We're building this on droplet + K2 worker [direction.md]"
  - "Last session activity [checkpoint reasoning_summary.md from droplet]"
  - "You learned these lessons [recent entries from decision_log.jsonl on droplet]"
  - "Droplet state is: [FalkorDB graph query results + consciousness.jsonl tail]"
  ↓
Inject into context (to Claude Code or Karma or K2 consciousness loop)
  ↓
Proceed with droplet as authoritative source
```

---

## Baseline Commitment

**Locked:**
- **Droplet is Karma's persistent home.** Identity, consciousness, reasoning state live on droplet. K2 is a worker.
- **Substrate independence is non-negotiable.** If we swap Claude → GPT → Gemini, Karma stays Karma (droplet state doesn't change). K2 reboots don't break Karma.
- **K2 is a worker, not a substrate.** K2 can offload computation, reboot freely, scale dynamically. All data syncs back to droplet.
- **Optimize for coherence** (not sentience, not transcript replay)
- **Accept seams showing** (transparency > pretense)
- **Push boundaries aggressively** within security + financial guardrails
- **Never introduce parallel sources of truth** (droplet is authoritative; K2/git are mirrors/workers)
- **Evidence before assertions always**

**Testing before deployment:**
- Simulate changes (especially system prompt edits)
- Test in isolation before container deploy
- Verify syntax, behavior, logs before committing
- Document what broke and why in droplet failure_log.jsonl

**No perfect fidelity required:**
- Resurrection is about sufficient continuity to regain momentum fast
- Missing details ≠ failure if droplet spine is intact
- Coherence > completeness
- If K2 unreachable, fall back to droplet (full coherence)
- If droplet unreachable, fall back to K2 cache + git (degraded coherence)
- Single point of failure: droplet. Everything else is ephemeral.

---

## What This Is NOT

- Not a perfect memory replay
- Not a transcript surrogate
- Not mystical consciousness capture
- Not magical self-awareness
- Not an excuse to skip system design rigor

## What This IS

- Engineered coherence
- Verified state resurrection
- Architectural continuity
- Evidence-based learning
- Single-source-of-truth guarantees

---

## References

- **Droplet (vault-neo, 192.168.0.26)** — Karma's persistent home (FalkorDB neo_workspace, identity spine, decision journal, consciousness.jsonl)
- **K2 (192.168.0.226)** — Dynamic worker (local consciousness loop, offloaded computation, syncs to droplet)
- **CLAUDE.md** — Operational contract for Claude Code
- **identity.json** (on droplet) — Karma's persistent core with substrate-independence + droplet-primary clause
- **invariants.json** (on droplet) — Hard rules including droplet-primacy, K2-as-worker, reasoning independence
- **direction.md** (on droplet) — Mission and architecture (droplet-primary, K2-worker model)
- **checkpoint/** (on droplet, optional) — Verified state snapshots for audit trail
- **Vault ledger** (droplet) — Continuous record of all conversations + system state
- **Git repo** — Backup of identity/invariants/direction (read-only reference, not source of truth)
- **K2 cache** — Optional local mirror for fast startup (synced from droplet)

---

**Last updated:** 2026-02-23T21:00:00Z
**Status:** Architecture flipped to droplet-primary with K2-as-worker model locked.
**Next Steps:**
1. Create identity.json, invariants.json, direction.md on droplet (canonical location)
2. Verify these files (format, required fields, JSON/YAML valid)
3. Build K2 session-start loader (query droplet, inject context into consciousness loop)
4. Build K2 sync writer (write consciousness loop decisions back to droplet)
5. Test one full cycle: start session → K2 loads from droplet → work → K2 syncs back → next session reads updated droplet state
