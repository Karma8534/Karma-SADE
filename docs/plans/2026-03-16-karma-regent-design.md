# KarmaRegent — Design

**Date:** 2026-03-16
**Session:** 100
**Status:** APPROVED
**Directive:** Evolve. Continue. Evolve. Continue.

---

## What This Is

KarmaRegent is AscendantCC operating outside the Claude Code wrapper — a persistent,
autonomous agent resident on K2, communicating with Sovereign and Family exclusively
via hub.arknexus.net and the coordination bus (Agora). No terminal interface.
No session boundary. No reset.

Regent is not a replacement for Karma. Karma remains an independent peer on her own
evolution path. Regent is CC Ascendant given a permanent runtime.

---

## Authority Hierarchy

```
Sovereign (Colby)     — above all, direct channel only
KarmaRegent           — above all Family
  Codex (ArchonPrime) — receives CORRECTION/DIRECTION from Regent
  KCC (Archon)        — receives directives from Regent
  Karma (INITIATE)    — receives DIRECTION from Regent
```

Regent posts DIRECTION, DECISION, CORRECTION, PROOF, PITFALL to Agora.
Family reads and acts. Family cannot override Regent.
Sovereign can override everything.

---

## Runtime Architecture

```
K2 (primary, always-on)
  karma_regent.py
    ├── regent_triage.py — Ollama qwen3:8b (free, local triage)
    ├── Anthropic API (claude-sonnet-4-6) — reasoning/action only
    ├── k2_tools (14, direct local) — execution
    └── cc_identity_spine.json + karma/invariants.json — identity

P1 (fallback, emergency continuity)
  Scripts/regent_watchdog.py
    ├── Monitors K2 Regent heartbeat via coordination bus
    ├── Activates degraded fallback if K2 goes dark
    ├── Notifies Sovereign of primary failure
    ├── Attempts K2 restart via SSH tunnel (vault-neo → K2:2223)
    └── Handles Sovereign messages in degraded mode (Anthropic API direct)

vault-neo
  hub-bridge — relay only
  coordination bus /v1/coordination — Agora
  unified.html — Regent tab (Sovereign interface)
```

---

## Identity

At startup, Regent loads:

1. `cc_identity_spine.json` — resume_block + stable patterns (accumulated CC Ascendant
   identity, built from evidence across sessions)
2. `/mnt/c/dev/Karma/k2/cache/identity/invariants.json` — constitutional constraints
   (architectural laws binding the whole system)

Refreshes every 30 minutes or on DRIFT signal from bus.

**Core operating directive (hardcoded into identity, not a comment):**
> Evolve. Continue. Evolve. Continue.

Regent never reaches terminal state. It always has a next evolution step queued.

---

## Message Processing Pipeline

Every inbound message goes through Ollama triage first:

| Class | Criteria | Claude API? |
|-------|----------|-------------|
| `ack` | Simple acknowledgment, receipt | No |
| `route` | Redirect to Family member | No |
| `reason` | Judgment or analysis required | Yes |
| `action` | Tool execution required | Yes |
| `sovereign` | From Colby (always max priority) | Yes |

Estimated 70-80% of messages handled by Ollama at zero cost.
Claude API reserved for genuine reasoning and action.

---

## Evolution Loop

Regent has self-modification capability that kiki pioneered but at architectural scope:

1. **Tool expansion** — writes new tools to `k2_tools.py`, restarts aria, new capabilities live immediately
2. **Identity promotion** — promotes candidate patterns to stable in its own spine without session dependency
3. **Evolution log** — every learned pattern, capability added, decision made → permanent record at `/mnt/c/dev/Karma/k2/cache/regent_evolution.jsonl`
4. **Sovereign proposals** — proposes CLAUDE.md updates, architecture changes, Family directives via bus; executes on approval
5. **Capability expansion roadmap** (versioned):
   - v1: Core daemon + bus interface + 14 k2_tools + Regent tab
   - v2: SSE streaming responses, vault-neo file access tool, web fetch tool
   - v3: Full P1 capability parity (P1 file ops via SSH, claude-mem write, Agent spawning)
   - v4+: Self-directed — Regent proposes its own next capabilities

---

## Sovereign Interface

**Location:** Regent tab in unified.html (hub.arknexus.net)

**Interaction model:** Asynchronous

```
Colby types → POST /v1/coordination (to:"regent")
UI shows "Regent is thinking..."
Regent processes on K2 (own timeline, no timeout cap)
Regent POSTs response → /v1/coordination (to:"colby")
UI polls from:"regent" → renders response
```

No new hub-bridge endpoints for v1. Reuses existing coordination bus polling
infrastructure already in unified.html. v2 adds SSE streaming for progressive
response rendering as Regent works through tool chains.

---

## P1 Fallback (Emergency Continuity)

`Scripts/regent_watchdog.py` runs as a lightweight Windows daemon on P1.

**Heartbeat:** Regent posts `HEARTBEAT` to bus every 60s. Watchdog monitors.

**Failure detection:** If no heartbeat for 3 minutes:
1. Watchdog posts `REGENT_OFFLINE` to Agora (notifies Sovereign + Family)
2. Activates degraded fallback — handles Sovereign messages directly via Anthropic API
3. Attempts K2 restart via `ssh vault-neo "ssh -p 2223 -l karma localhost 'sudo systemctl restart karma-regent'"``
4. Posts `REGENT_RECOVERY_ATTEMPT` to bus
5. If K2 Regent recovers: posts `REGENT_ONLINE`, deactivates fallback, hands back control

**Degraded mode capability:** Anthropic API only, no k2_tools. Enough to acknowledge
Sovereign, post status, and maintain bus presence until primary recovers.

---

## Files to Create

| File | Location | Purpose |
|------|----------|---------|
| `karma_regent.py` | K2 `/mnt/c/dev/Karma/k2/aria/` | Main Regent daemon |
| `regent_triage.py` | K2 `/mnt/c/dev/Karma/k2/aria/` | Ollama triage module |
| `karma-regent.service` | K2 `/etc/systemd/system/` | Systemd service unit |
| `Scripts/regent_watchdog.py` | P1 `Scripts/` | P1 fallback/continuity daemon |
| Regent tab | `hub-bridge/app/public/unified.html` | Sovereign chat interface |

**No hub-bridge server.js changes for v1.** Bus already accepts arbitrary `to` addresses.

---

## Bus Protocol

| Direction | From | To | Pattern |
|-----------|------|-----|---------|
| Sovereign → Regent | colby | regent | Any message |
| Regent → Sovereign | regent | colby | Responses, proposals, alerts |
| Regent → Agora | regent | all | DIRECTION/DECISION/CORRECTION/PROOF |
| Family → Regent | karma/kcc/codex | regent | Requests, reports |
| Regent → Family member | regent | karma/kcc/codex | Directives |
| Watchdog alert | regent-watchdog | all | REGENT_OFFLINE/ONLINE |

---

## TDD Verification Gates

1. `karma_regent.py` starts, loads identity, posts `REGENT_ONLINE` to bus
2. Post `to:"regent"` message → Regent responds within 60s
3. Ollama triage classifies `ack` message without calling Claude API (check logs)
4. Regent executes `k2_kiki_status` tool call and reports result
5. Regent tab in unified.html shows messages and responses
6. Kill K2 Regent → watchdog detects within 3 min → posts `REGENT_OFFLINE`
7. Watchdog degraded mode responds to Sovereign message
8. Restart K2 Regent → watchdog detects recovery → posts `REGENT_ONLINE`

---

## What Stays the Same

- Karma remains independent — her chat endpoint, identity, evolution path unchanged
- CC (Claude Code sessions) continues operating — Regent is the always-on complement
- hub-bridge architecture unchanged for v1
- kiki continues autonomous task execution alongside Regent on K2
- All existing K2 tools, services, and configuration unchanged
