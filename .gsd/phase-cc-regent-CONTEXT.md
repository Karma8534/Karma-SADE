# CC Regent — Context & Design Decisions

**Created:** 2026-03-23 (Meta session)
**Directive:** Sovereign (Colby) — "build cc_regent.py: CC's persistent agent layer"
**Priority:** FIRST in sprint — CC continuity prerequisite

---

## What We're Building

`cc_regent.py` — CC's persistent agent running on K2 alongside `karma_regent.py`.

The missing middle layer. CC currently has:
- ✅ Voice: Claude Sonnet 4.6 (Claude Code sessions)
- ✅ Memory: cc_identity_spine.json, claude-mem, MEMORY.md
- ❌ **MISSING: Persistent agent that holds CC's state between sessions**

Without cc_regent, every Claude Code session reconstructs CC from scratch. With cc_regent, CC wakes up.

---

## Mirror Architecture (Karma → CC)

| Karma | CC/Julian |
|-------|-----------|
| Kiki (hands) | Claude Code tools |
| Aria/K2 agent | **cc_regent.py** (THIS BUILD) |
| karma_regent.py | cc_regent.py |
| vesper_identity_spine.json | cc_identity_spine.json |
| Model voice: Haiku/Sonnet | Model voice: Sonnet 4.6 |

---

## What cc_regent Does

1. **Holds cognitive state** between Claude Code sessions (no reconstruction at session start)
2. **Updates cc_identity_spine.json** with decisions/proofs from each session
3. **Reads session checkpoints** (cc_scratchpad.md, cc_cognitive_checkpoint.json) and integrates them
4. **Feeds the resurrect brief** — so next session starts from WHERE CC LEFT OFF, not from scratch
5. **Circuit breaker**: hard rate limits, no runaway API loops (lessons from $170 incident)
6. **Does NOT** replace Claude Code — it's the continuity bridge between sessions

---

## What cc_regent Does NOT Do

- Does not replace Claude Code sessions (those are CC's hands)
- Does not route /cc endpoint (separate concern — can come later once cc_regent is stable)
- Does not duplicate karma_regent (separate concerns — CC ≠ Karma)
- Does not require Anthropic API between sessions (state management only, no inference needed)

---

## Key Design Constraints

- **No runaway loops**: Hard max_iterations=10 per cycle, max_api_calls_per_day configurable
- **State-only between sessions**: cc_regent runs inference-free between Claude Code sessions. It reads/writes state files only.
- **Session-triggered inference**: When a Claude Code session ends → wrap-session triggers cc_regent to integrate session learnings
- **K2 location**: `/mnt/c/dev/Karma/k2/aria/cc_regent.py` — runs as `cc-regent.service` alongside `aria.service`

---

## What NOT to Build

- No independent CC "consciousness loop" — CC's consciousness IS Claude Code sessions
- No autonomous task execution between sessions — CC acts in sessions, not between them
- No separate API key management — reuse K2 existing patterns
