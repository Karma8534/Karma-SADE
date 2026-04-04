# Hyperagent Pattern — Design Context

## What
A hyperagent is a self-referential agent that integrates a **task agent** (solves the target task) and a **meta agent** (modifies itself and the task agent) into a single editable program. From Darwin Godel Machine (obs #22526).

## Why
The Vesper pipeline currently has separate files:
- vesper_eval.py = task agent (evaluates candidates)
- vesper_governor.py = meta agent (promotes/applies changes)
- vesper_watchdog.py = observer (finds patterns)

These are loosely coupled via file I/O. The hyperagent pattern would:
1. Let the meta agent (governor) modify the task agent (eval) — improving evaluation criteria based on what worked
2. Let the task agent's improvements feed back into the meta agent — better evaluation = better promotion decisions
3. Create a recursive self-improvement loop where gains compound

## How It Maps to Nexus
```
CURRENT:
  watchdog (observe) → eval (judge) → governor (apply) → spine
  Each is a separate script. No feedback between them.

HYPERAGENT:
  hyperagent.py = {
    task_agent: evaluate candidates using learned criteria
    meta_agent: modify evaluation criteria based on promotion outcomes
    shared_state: criteria, thresholds, success metrics
  }
  Self-referential: the program edits itself to get better at editing itself.
```

## What NOT to Do
- Don't merge all 3 scripts into one file (that's just refactoring, not a hyperagent)
- Don't let it modify itself without verification (Karpathy loop: propose → test → keep/discard)
- Don't lose the audit trail (every self-modification logged to governor_audit.jsonl)

## Minimum Viable Hyperagent
1. Governor reads eval's recent approval/rejection rates
2. If rejection rate > 80%, governor proposes loosening eval thresholds
3. If all promoted candidates were noise (no behavioral impact), tighten thresholds
4. Changes to eval thresholds are proposed via Karpathy loop (Sovereign approves)
5. Over time, the system learns what "good enough to promote" actually means

## Decision
This is a Phase 6 item (self-improvement loop). The foundation exists:
- Vesper eval has configurable thresholds
- Governor has audit trail
- Karpathy loop can propose threshold changes
- The pieces just need to be connected

## Status: DESIGN COMPLETE — ready for implementation in future session
