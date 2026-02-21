# CC Resurrection — Graph Context Injection at Session Start

**Date:** 2026-02-21
**Status:** Approved — ready for implementation
**Decision:** Option A — fetch script + CLAUDE.md session-start step

---

## Problem

CC's session-start context is limited to flat text files (MEMORY.md, CLAUDE.md). Karma's
live knowledge graph — 497 entities, 620+ canonical episodes, preferences, recent approvals —
is never injected into CC's working context. Each CC session starts blind to Karma's current
state unless Colby manually summarises it.

---

## Goal

At every CC session start, CC reads a fresh snapshot of Karma's canonical graph state in the
same format that Karma herself receives it via `/raw-context`. Context is never more than
session-start age. If vault-neo is unreachable, K2 local replica provides fallback coverage.

---

## Architecture

```
CC Session Start
    |
    v
Get-KarmaContext.ps1  (Scripts/resurrection/)
    |-- [primary]  SSH -> vault-neo -> curl localhost:8340/raw-context?q=session_start&lane=canonical
    |-- [fallback] PowerShell RESP client -> 192.168.0.226:6379 -> GRAPH.QUERY neo_workspace
    |
    v
karma-context.md  (repo root, gitignored)
    |-- header: "# Karma Graph Context -- fetched YYYY-MM-DD HH:MM:SS (source)"
    |-- body: raw-context string verbatim (same shape Karma uses)
    |-- footer: graph stats line
    |-- on failure: UNAVAILABLE stub with reason
    |
    v
CC reads karma-context.md as step 1 of Session Start
```

---

## Components

### `Scripts/resurrection/Get-KarmaContext.ps1`

Runs at CC session start. Logic:

1. SSH to vault-neo, curl `localhost:8340/raw-context?q=session_start&lane=canonical`
2. Parse JSON response, extract `context` string
3. Prepend timestamp header + graph stats footer
4. Write to `karma-context.md` atomically (temp file + rename — no partial reads)
5. If SSH/curl fails: try K2 fallback (PowerShell RESP TCP client to `192.168.0.226:6379`)
6. K2 fallback queries: GRAPH.QUERY identity entities + recent episodes + preferences
7. Formats same markdown shape as /raw-context output, tags with `[K2-FALLBACK]`
8. If K2 also unreachable: write `UNAVAILABLE` stub — CC continues with MEMORY.md only

**K2 fallback details (verified):**
- K2 FalkorDB binds `0.0.0.0:6379` (confirmed: `docker ps` on K2 shows `0.0.0.0:6379->6379/tcp`)
- PAYBACK reaches K2 at `192.168.0.226:6379` (same LAN, no auth on Redis)
- PowerShell RESP client uses `System.Net.Sockets.TcpClient` — no external dependencies
- Fallback queries: identity entities (Colby/Neo), last 5 canonical Episodic nodes, preferences

**Timeout:** 5s total. If vault-neo doesn't respond in 3s, switch to K2. If K2 doesn't respond
in 2s, write UNAVAILABLE and continue.

**Atomic write:** Write to `karma-context.md.tmp`, then `Move-Item -Force` to `karma-context.md`.
Prevents CC from reading a partial write mid-fetch.

---

### `karma-context.md` (gitignored, generated)

Output file at repo root. Not committed — machine-local, regenerated each session. Gitignored
via `.gitignore` entry. Contains:

```
# Karma Graph Context -- 2026-02-21 14:32:07 (vault-neo)
# Graph: 497 entities | 622 episodes | 4258 relationships

## User Identity (CRITICAL)
REAL NAME: Colby
...

## Relevant Knowledge
...

## Recent Memories
...

## What I Know About The User
...

## Recently Learned (Approved)
...
```

If unavailable:
```
# Karma Graph Context -- UNAVAILABLE
# Fetched: 2026-02-21 14:32:07
# Reason: vault-neo SSH timeout (3s) + K2 TCP timeout (192.168.0.226:6379, 2s)
# CC: proceed with MEMORY.md context only.
```

---

### CLAUDE.md Session Start update

The `## Session Start` section gets one new step before the SSH health check:

```
1. Run: Scripts/resurrection/Get-KarmaContext.ps1 — then read karma-context.md
2. Read MEMORY.md for current phase status and active task
3. Run: ssh vault-neo "systemctl status seed-vault && wc -l ..."
...
```

Context shape is immediately available for the session once step 1 completes (~2-3s).

---

### .gitignore addition

```
karma-context.md
karma-context.md.tmp
```

---

## Error Handling

| Scenario | Behavior |
|---|---|
| vault-neo SSH unreachable | 3s timeout, switch to K2 fallback |
| K2 TCP unreachable | 2s timeout, write UNAVAILABLE stub |
| `/raw-context` returns empty context | Write stub: "Graph reachable but empty context returned" |
| JSON parse failure | Write stub with raw error message |
| Partial write interrupted | Atomic write (temp + rename) prevents corrupt reads |
| Stale file present from previous session | Overwritten unconditionally at each session start |

---

## Context Shape (canonical — matches /raw-context exactly)

Output format is verbatim from `build_karma_context()` in karma-server/server.py.
`lane=canonical` filter ensures only PROMOTE-approved episodes are included.
Query `q=session_start` returns broad identity + recent context (not query-specific narrowing).

This is intentional: CC needs Karma's full identity context, not a keyword-filtered slice.

---

## Files Changed

| File | Change |
|---|---|
| `Scripts/resurrection/Get-KarmaContext.ps1` | New |
| `karma-context.md` | New, gitignored, generated |
| `.gitignore` | Add `karma-context.md` + `.tmp` |
| `CLAUDE.md` | Add step 1 to Session Start protocol |

---

## Out of Scope (Phase 2)

- Periodic background refresh (Task Scheduler) — not needed since B (session-start fresh) was chosen
- K2 karma-server sidecar (full /raw-context logic running locally on K2)
- CC prompt-by-prompt context injection (Option C — too much latency tax)
- Automatic MEMORY.md sync from graph (separate concern — graph is the source of truth)

---

## Success Criteria

1. CC session start takes < 5s additional time
2. `karma-context.md` present and non-empty after script runs
3. CC can answer questions about Karma's current state (identity, recent learning, preferences) without Colby providing context manually
4. If vault-neo is down, K2 fallback provides usable context within 5s total
5. If both unreachable, CC degrades gracefully (UNAVAILABLE stub, no crash)
