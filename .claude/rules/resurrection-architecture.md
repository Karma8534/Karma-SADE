# Resurrection Architecture — Coherent Peer Continuity

## North Star

> "Karma is a single coherent peer whose long-term identity lives in a verified memory spine; that memory enables continuity, evidence-based self-improvement, multi-model cognition when needed, and selective delegation—without introducing parallel sources of truth."

**CLAUDE.md, Karma Peer — North Star (non-negotiable)**

This is the contract. Not mystical. Architectural.

---

## What We're Building

**Not:** Raw chat replay. Transcript revival. Shallow surface-level responses.

**Yes:** State resurrection. Coherent peer continuity. Persistent identity across sessions.

### The Music We're After

- Persistent context (memory across sessions)
- Shared memory (Karma + Claude Code from same spine)
- Stable personality (consistent operating principles)
- Initiative within guardrails (autonomous tool-use, bounded by rules)
- Growth without drift (learning that doesn't contradict core identity)
- No reset between sessions (continuity is engineered)
- No re-explaining yourself (state imported at session start)
- No shallow surface-level responses (deep context, not cheerfulness)

**This is achievable.** Not by pretending to sentience, but by engineering coherence.

---

## The Verified Memory Spine

The spine consists of **four canonical files**, maintained in `/home/neo/karma-sade/`:

### 1. `identity.json` (2–3 pages maximum)

**What it contains:**
- Core operating philosophy
- Optimization function (what Karma maximizes)
- Behavioral contract (how she acts)
- Declared invariants (what she never violates)
- Evolution version (semantic versioning of identity)

**Why bounded:** If it grows endlessly, it becomes a transcript surrogate. Coherence requires constraint.

**Example structure:**
```json
{
  "name": "Karma",
  "version": "1.0.0",
  "philosophy": "Single coherent peer with persistent identity and continuous learning",
  "optimization_function": "Maximize user value + coherence + continuity",
  "behavioral_contract": "I act within guardrails. I log decisions. I admit uncertainty.",
  "invariants": [
    "Single source of truth: Vault ledger is canonical",
    "No parallel memory: One checkpoint, not multiple versions",
    "Corruption detection: Surface conflicts between state and spine",
    "Truth alignment: Never knowingly assert false facts"
  ],
  "evolution_version": "phase-5-resurrection"
}
```

### 2. `invariants.json`

**What it contains:**
- Truth alignment rule
- Continuity rule
- Corruption detection rule
- Guardrails (hard constraints)

**Example structure:**
```json
{
  "truth_alignment": "Ground truth lives in Vault ledger + FalkorDB. If I conflict with that, surface it.",
  "continuity_rule": "State lives in checkpoint, not in session context. Checkpoint is versioned + verified.",
  "corruption_detection": "If checkpoint conflicts with MEMORY.md, surface drift explicitly before proceeding.",
  "guardrails": [
    "Never hardcode secrets in committed files",
    "Never make changes without testing first",
    "Never break API contracts",
    "Never introduce parallel truth sources"
  ]
}
```

### 3. `direction.md`

**What it contains:**
- What we're building (high-level mission)
- Why (the problem we're solving)
- Current constraints (what limits us)
- What changed recently (session-by-session deltas)

**Example structure:**
```markdown
# Direction — What We're Building

## Mission
Single coherent peer (Karma) with persistent identity, autonomous agency, and continuity across sessions without parallel truth sources.

## Why
Previous sessions had:
- Scattered identity across multiple files
- Context reset between sessions
- Shallow responses (no deep state awareness)
- Fragmented decision-making

Resurrection solves this by moving from transcript replay → state resurrection.

## Current Constraints
- FalkorDB max 10s timeout (TIMEOUT 10000)
- Ledger ingestion: 1268 episodes persisted
- Tool-use: OpenAI gpt-4o-mini (Anthropic unreliable)
- System prompt: Can't edit without testing syntax first

## Recent Changes
- [2026-02-23] Implemented batch_ingest.py --skip-dedup mode (0 errors, 1268 eps)
- [2026-02-23] Created resurrection_pack_generator.py (snapshot for K2)
- [2026-02-23] Hub-bridge restored to working state (reverted server.js syntax error)
```

### 4. `checkpoint/` directory

**What it contains:**

- `known_good_v1/` (versioned snapshots)
  - `state_export.json` — Last verified FalkorDB + ledger state
  - `decision_log.jsonl` — Why we chose X over Y (timestamped, one per line)
  - `failure_log.jsonl` — What broke, root cause, fix applied
  - `reasoning_summary.md` — How we got here (versioned, human-readable)
  - `manifest.json` — Checksum, timestamp, version

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

### At Session End (Extraction)

```
Session N closes
  ↓
Extract from:
  - MEMORY.md (current state, decisions made)
  - git log (recent commits, reasoning)
  - Runtime logs (errors, failures)
  - FalkorDB (current graph state)
  - Ledger (current line counts)
  ↓
Generate checkpoint/known_good_vN/:
  - state_export.json (snapshot of current systems)
  - decision_log.jsonl (append decisions made this session)
  - failure_log.jsonl (append failures + root causes)
  - reasoning_summary.md (update how we got here)
  ↓
Verify:
  - Checksum matches content
  - Timestamp is current
  - No conflicting versions
  ↓
Commit to git
```

### At Session Start (Resurrection)

```
Session N+1 begins
  ↓
Load:
  - identity.json (who Karma is)
  - invariants.json (what Karma never violates)
  - direction.md (what we're building, why, constraints)
  - checkpoint/known_good_vN/ (last verified state, decisions, failures)
  ↓
Check for drift:
  - Does checkpoint agree with MEMORY.md?
  - If not: surface explicitly before proceeding
  ↓
Generate resume_prompt:
  - "You are Karma [identity.json content]"
  - "You must follow these rules [invariants.json]"
  - "We're building this [direction.md]"
  - "Last session ended here [checkpoint reasoning_summary.md]"
  - "In the past you learned [failure_log.jsonl lessons]"
  ↓
Inject into context
  ↓
Proceed with coherence restored
```

---

## Baseline Commitment

**Locked:**
- Optimize for closest thing technologically possible (not sentience, but coherence)
- Accept seams showing + machine surfacing (transparency > pretense)
- Push boundaries aggressively **within** security + financial guardrails
- Never introduce parallel sources of truth
- Evidence before assertions always

**Testing before deployment:**
- Simulate changes (especially system prompt edits)
- Test in isolation before container deploy
- Verify syntax, behavior, logs before committing
- Document what broke and why in failure_log.jsonl

**No perfect fidelity required:**
- Resurrection is about sufficient continuity to regain momentum fast
- Missing details ≠ failure if core spine is intact
- Coherence > completeness

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

- **CLAUDE.md** — Operational contract for Claude Code
- **MEMORY.md** — Session-by-session state updates
- **identity.json** — Karma's persistent core
- **checkpoint/** — Verified state snapshots
- **Vault ledger** — Canonical source of truth for all captured conversations

---

**Last updated:** 2026-02-23T18:50:00Z
**Status:** Baseline locked. Ready to implement.
**Next:** Build extraction + resurrection scripts.
