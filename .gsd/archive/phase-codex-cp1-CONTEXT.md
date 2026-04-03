# Codex Critical Path Item 1 — CONTEXT

## What We're Doing
Enforce PreToolUse denials + wire load_transcript into resume flow in cc_server_p1.py.

## Design Decisions

### PreToolUse Enforcement Reality
The CC subprocess (`claude` CLI) runs autonomously. By the time we see a `tool_use` event in stream-json output, CC has ALREADY decided to use the tool and executes it internally. Our hooks fire on observation, not prevention.

**Real enforcement options:**
1. Pass denied tools list to CC subprocess via `--disallowedTools` flag (if available)
2. Kill subprocess on denied tool detection + return error to browser
3. For nexus_agent path: check_permission() already gates BEFORE execution — this works

**Decision:** Option 2 — detect denied tool in stream, kill subprocess, return denial error. This is the only enforcement we can do without CC CLI changes. Also pass permission stack to _build_cc_cmd as system prompt context (CC will self-restrict if told not to use certain tools).

### load_transcript Wiring
- CC subprocess path: `--resume` with session_id handles CC's own recovery
- cc_server transcript (append_transcript): writes user messages for crash-safe record
- **Gap:** After cc_server restart, transcript exists on disk but is never loaded
- **Fix:** On request with x-conversation-id, load transcript as conversation context for build_context_prefix

## What We're NOT Doing
- Modifying CC CLI itself
- Changing nexus_agent.py (check_permission already works there)
- Adding new tools or endpoints
