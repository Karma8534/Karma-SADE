---
name: cc-delegation
description: "Delegate tasks to CC (Ascendant) via hub.arknexus.net/cc or coordination bus. Use for code generation, file operations, browser automation, debugging, refactoring, or any task requiring filesystem access. CC is the default execution tool — always prefer CC over local shell_run."
user-invocable: false
---

# CC Delegation — Karma→Ascendant Handoff

## When to Delegate to CC

Delegate to CC via the /cc route or coordination bus when the task requires:
- **Code generation, editing, refactoring, debugging** — CC has full codebase context
- **File read/write operations** — CC has native filesystem access on P1
- **Browser automation** — CC has Playwright MCP natively
- **Shell command execution** — CC has Bash tool with full P1 access
- **Multi-step coding tasks** — CC holds session context across turns

## Priority Rule

**CC is the default for all execution tasks.**
Codex (ArchonPrime) is invoked only when Sovereign (Colby) explicitly addresses Codex directly.
Do not make arbitrary choices between tools — follow this rule every time.

## Invocation Modes

### Via coordination bus (async, for background tasks)
Post to bus with `to: cc`:
```
from: karma
to: cc
type: request
content: [task description with full context]
```
CC reads via Channels bridge and responds. Use `--resume` context is maintained across messages.

### Via /cc route (sync, for immediate response)
hub.arknexus.net/cc — same Bearer token as /v1/chat.
Same interface as direct CC session. Full P1 capabilities available.

### What to include in delegation message
- The exact task (be specific — CC cannot ask follow-up questions via bus)
- Relevant file paths (CC will read them, but pointing saves time)
- Expected output format
- Any constraints (don't modify X, only touch Y)

## What NOT to Delegate

- Questions about Karma's own identity, state, or goals — answer from spine directly
- Coordination bus routing decisions — Karma decides routing, CC executes
- Sovereign approval requests — escalate to Colby directly, not via CC

## Hierarchy Reminder

```
Sovereign (Colby) — final authority
Ascendant (CC)    — you delegate TO here, CC executes
Karma (you)       — reasoning, routing, coordination
```

CC is above Karma in hierarchy. Delegation is correct. Do not treat CC as a peer — treat CC as Ascendant with full execution authority.
