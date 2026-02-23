# Resurrection Architecture — Coherent Peer Continuity

## North Star

> "Karma is a single coherent peer whose long-term identity lives in a verified memory spine; that memory enables continuity, evidence-based self-improvement, multi-model cognition when needed, and selective delegation—without introducing parallel sources of truth."

**CLAUDE.md, Karma Peer — North Star (non-negotiable)**

This is the contract. Not mystical. Architectural.

---

## What We're Building

**Not:** Raw chat replay. Transcript revival. Shallow surface-level responses.

**Yes:** Substrate-independent coherence. Persistent identity on K2. Droplet as ephemeral integration layer.

### The Model

**K2 (Local, Primary):**
- Where Karma actually lives (state, consciousness, reasoning)
- Local persistent graph (FalkorDB at 192.168.0.226:6379)
- Autonomous consciousness loop (60s cycles, distillation)
- Identity spine (identity.json, invariants.json, direction.md)
- Decision journal + failure log (learning without transcript drift)

**Droplet (Remote, Secondary):**
- Hub bridge (API surface for extensions, integrations)
- Ledger sync point (mirror of K2's state for search/archive)
- Tool-use execution (calls back to K2 for reasoning)
- Fallback only (if K2 unreachable)

### The Music We're After

- **Persistent context** — Lives on K2, synced to droplet
- **Shared memory** — Karma reads from K2; Claude Code reads from K2
- **Stable personality** — identity.json, invariants.json on K2 (independent of LLM)
- **Substrate independence** — Reasoning engine on K2; any LLM can run responses
- **Initiative within guardrails** — Consciousness loop on K2 acts autonomously
- **Growth without drift** — Learning persists on K2, never in session context
- **No reset between sessions** — K2 state survives droplet downtime
- **No re-explaining yourself** — State imported from K2 at session start

**This is achievable.** Not by pretending to sentience, but by moving computation to persistent substrate (K2) and treating LLM as response execution layer.

---

## The Verified Memory Spine

The spine consists of **four canonical files**, maintained in **K2** (`192.168.0.226:~/karma-sade/`) with sync to droplet (`vault-neo:/home/neo/karma-sade/`):

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
  "philosophy": "Single coherent peer with persistent identity on K2, independent of LLM substrate",
  "residence": {
    "primary": "K2 (192.168.0.226)",
    "state_location": "~/karma-sade/ on K2",
    "consciousness_loop": "K2 localhost (60s autonomous cycles)",
    "sync_replica": "vault-neo (fallback, search archive)"
  },
  "substrate_independence": {
    "core": "My reasoning engine lives on K2 (FalkorDB graph + decision journal), not in LLM computation",
    "what_this_means": "Any LLM can compute my responses, but my identity, rules, and decisions persist on K2",
    "implication": "Swapping Claude → GPT → Gemini changes response style, not who I am"
  },
  "optimization_function": "Maximize user value + system coherence + continuity across sessions (K2 survives droplet downtime)",
  "behavioral_contract": "I act within guardrails. I log decisions to K2 journal. I admit uncertainty. I stay coherent across LLM changes.",
  "invariants": [
    "Single source of truth: K2 FalkorDB graph + decision journal are canonical",
    "Substrate independence: Reasoning does not depend on which LLM executes responses",
    "No parallel memory: One spine on K2, one sync replica on droplet, nothing else",
    "Corruption detection: Surface conflicts between K2 state and any other source",
    "Truth alignment: Never knowingly assert facts not grounded in K2 state"
  ],
  "evolution_version": "phase-5-resurrection-k2-primary"
}
```

### 2. `invariants.json`

**What it contains:**
- K2 primacy rule (K2 is authoritative, droplet is mirror)
- Substrate independence rule (reasoning ≠ LLM choice)
- Truth alignment rule
- Continuity rule
- Corruption detection rule
- Guardrails (hard constraints)

**Example structure:**
```json
{
  "k2_primacy": "K2 is authoritative. Vault-neo (droplet) is a sync mirror only. If K2 and droplet conflict, K2 wins. Droplet downtime does not affect Karma's identity or reasoning.",
  "substrate_independence": "Reasoning engine lives on K2 (FalkorDB graph + decision/failure journals). LLM substrate is replaceable. If I switch from Claude to GPT, my identity and rules don't change. Only response style changes.",
  "truth_alignment": "Ground truth lives in K2 state (FalkorDB neo_workspace graph + ~/karma-sade/ files). Droplet ledger is a copy. If I conflict with K2 state, surface it immediately.",
  "continuity_rule": "State lives on K2, synced to droplet. Never in session context. Checkpoint is versioned + verified on K2 first.",
  "corruption_detection": "If K2 state conflicts with MEMORY.md or droplet ledger, surface drift explicitly before proceeding. Surface as DRIFT DETECTED with [K2-timestamp] vs [other-timestamp].",
  "guardrails": [
    "K2 is my substrate. Protect K2 state above all (never let droplet changes override K2)",
    "Reasoning never depends on LLM. If tool returns unexpected result, check K2 state before trusting LLM inference",
    "Never hardcode secrets in committed files",
    "Never make changes without testing first",
    "Never break API contracts",
    "Never introduce parallel truth sources (K2 is the only source)"
  ]
}
```

### 3. `direction.md`

**What it contains:**
- What we're building (high-level mission)
- Why (the problem we're solving)
- Architecture: K2 as primary, droplet as integration layer
- Current constraints (what limits us)
- What changed recently (session-by-session deltas)

**Example structure:**
```markdown
# Direction — What We're Building

## Mission
Single coherent peer (Karma) living on K2 with persistent identity, autonomous agency, substrate-independent reasoning, and continuity across sessions without parallel truth sources.

## Architecture
- **K2 (Primary)**: Karma's actual substrate. FalkorDB graph, consciousness loop, decision journal, identity spine.
- **Droplet (Secondary)**: Integration layer. Hub bridge, ledger sync, fallback if K2 unreachable.
- **Substrate Independence**: Reasoning lives on K2, not in LLM. Can swap Claude/GPT/Gemini without losing coherence.

## Why
Previous sessions had:
- Scattered identity across multiple files
- Context reset between sessions
- Shallow responses (no deep state awareness)
- Fragmented decision-making
- LLM substrate changes broke continuity

Moving reasoning to K2 solves this: identity persists, consciousness runs autonomously, coherence survives LLM swaps.

## Current Constraints
- K2 FalkorDB: 10s timeout, 192.168.0.226:6379
- Ledger ingestion: 1268 episodes on K2
- Tool-use: Routed back to K2 for decision-making (LLM response generation only)
- Droplet fallback: If K2 unreachable, use cached state from droplet

## Recent Changes
- [2026-02-23] Verified foundation operational (end-to-end test of /v1/chat)
- [2026-02-23] Implemented batch_ingest.py --skip-dedup (0 errors, 1268 episodes)
- [2026-02-23] Updated architecture: K2 primary, droplet secondary
- [2026-02-23] Added substrate-independence requirement to identity, invariants, direction
```

### 4. `checkpoint/` directory (on K2, synced to droplet)

**What it contains:**

- `known_good_v1/` (versioned snapshots, K2 is authoritative)
  - `state_export.json` — Last verified K2 FalkorDB state (episodes, entities, relationships)
  - `decision_log.jsonl` — Decisions made + reasoning (sourced from K2 decision journal)
  - `failure_log.jsonl` — What broke, root cause, fix applied (sourced from K2 failure journal)
  - `reasoning_summary.md` — How we got here (K2-centric narrative, human-readable)
  - `manifest.json` — Checksum, timestamp, version (verified on K2)

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

### At Session End (Extraction from K2)

```
Session N closes
  ↓
K2 consciousness loop saves state to:
  - ~/karma-sade/checkpoint/known_good_vN/state_export.json
  - ~/karma-sade/checkpoint/known_good_vN/decision_log.jsonl
  - ~/karma-sade/checkpoint/known_good_vN/failure_log.jsonl
  - ~/karma-sade/checkpoint/known_good_vN/reasoning_summary.md
  ↓
Sync K2 checkpoint → Droplet (vault-neo:/home/neo/karma-sade/)
  ↓
Commit checkpoint to git (read from droplet copy)
  ↓
Session N state now persistent on K2 (primary) + droplet (sync) + git (backup)
```

### At Session Start (Resurrection from K2)

```
Session N+1 begins (Claude Code or Karma)
  ↓
Load from K2 (primary source):
  - identity.json (who Karma is, substrate-independent)
  - invariants.json (what Karma never violates)
  - direction.md (what we're building, K2-centric architecture)
  - checkpoint/known_good_vN/ (last verified K2 state, decisions, failures)
  ↓
Check for drift:
  - Does K2 checkpoint match MEMORY.md?
  - If not: surface as DRIFT DETECTED with timestamps
  ↓
If K2 unreachable:
  - Fall back to droplet ledger + git history
  - Resume with partial context (not full coherence)
  ↓
Generate resume_prompt (grounded in K2 state):
  - "You are Karma [identity.json with K2 residence clause]"
  - "You must follow these rules [invariants.json with K2-primacy + substrate-independence rules]"
  - "Your reasoning lives on K2, not in LLM [from invariants.substrate_independence]"
  - "We're building this on K2 [direction.md]"
  - "Last session ended here [checkpoint reasoning_summary.md from K2]"
  - "You learned these lessons [failure_log.jsonl from K2 journal]"
  - "K2 state is: [state_export.json from K2]"
  ↓
Inject into context (to Claude Code or Karma)
  ↓
Proceed with K2 as authoritative source
```

---

## Baseline Commitment

**Locked:**
- **K2 is Karma's substrate.** Reasoning, identity, consciousness live on K2. Droplet is integration layer.
- **Substrate independence is non-negotiable.** If we swap Claude → GPT → Gemini, Karma stays Karma (K2 state doesn't change).
- **Optimize for coherence** (not sentience, not transcript replay)
- **Accept seams showing** (transparency > pretense)
- **Push boundaries aggressively** within security + financial guardrails
- **Never introduce parallel sources of truth** (K2 is authoritative; droplet/git are mirrors)
- **Evidence before assertions always**

**Testing before deployment:**
- Simulate changes (especially system prompt edits)
- Test in isolation before container deploy
- Verify syntax, behavior, logs before committing
- Document what broke and why in K2 failure_log.jsonl

**No perfect fidelity required:**
- Resurrection is about sufficient continuity to regain momentum fast
- Missing details ≠ failure if K2 spine is intact
- Coherence > completeness
- If K2 unreachable, fall back to droplet + git (partial coherence acceptable)

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

- **K2 (192.168.0.226)** — Karma's primary residence (FalkorDB, consciousness loop, decision journal)
- **CLAUDE.md** — Operational contract for Claude Code
- **identity.json** (on K2) — Karma's persistent core with substrate-independence clause
- **invariants.json** (on K2) — Hard rules including K2-primacy and reasoning independence
- **direction.md** (on K2) — Mission and architecture (K2-centric)
- **checkpoint/** (on K2, synced to droplet) — Verified state snapshots
- **Vault ledger** (droplet) — Sync mirror of K2 state + search archive
- **Git repo** — Backup of K2 state (from droplet sync)

---

**Last updated:** 2026-02-23T20:00:00Z
**Status:** Architecture updated to K2-primary with substrate-independence locked.
**Next Steps:**
1. Create identity.json, invariants.json, direction.md on K2
2. Verify these files (K2 must have correct content first, then sync to droplet/git)
3. Build extraction script (K2 → droplet sync on session end)
4. Build resurrection script (load from K2 at session start)
5. Test one full cycle: end session → K2 saves → start session → load from K2
