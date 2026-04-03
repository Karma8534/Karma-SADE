# Codex Critical Path Item 1 — PLAN

## Task 1: Enforce PreToolUse denials in run_cc_stream
- In run_cc_stream(), when PreToolUse hook returns permissionDecision=deny:
  - Kill the CC subprocess immediately
  - Yield a synthetic denial event (type=error with tool name + reason)
  - Break the stream loop
- Add denied tools list to system prompt context in _build_cc_cmd (CC self-restricts)

**Verify:** Add a test tool name to deny list, send a message that would trigger it, confirm stream terminates with denial event instead of tool execution.
**Done when:** Denied tools produce a visible error in the browser stream, not silent log-only.

## Task 2: Wire load_transcript into resume flow
- In the /cc/stream handler (line ~1092), before calling run_cc_stream:
  - If x-conversation-id provided AND transcript exists on disk
  - Load transcript via load_transcript()
  - Include last N messages as conversation context in the system prompt prefix
- This enables cc_server to recover conversation state after restart

**Verify:** Restart cc_server process, send a follow-up message with same conversation-id, confirm prior context is injected.
**Done when:** load_transcript() is called in the request path and prior messages appear in CC's context.

## Task 3: End-to-end verification
- Start cc_server
- Send a message, confirm transcript written
- Check that denied tool scenario produces visible error
- Restart server, send follow-up, confirm transcript loaded

**Verify:** All 3 scenarios produce correct behavior.
**Done when:** Both gaps from Codex audit are closed with working code.
