# Phase 5-2: Slash Commands — CONTEXT

## What
Add slash command parsing to unified.html: `/compact`, `/clear`, `/effort`, `/model`, `/rename`.

## Architecture
- **unified.html** — intercept `/` prefix in sendMessage(), dispatch
- **proxy.js** — pass `effort` param through to cc_server_p1.py
- **cc_server_p1.py** — accept `effort` param, pass `--effort` flag to claude CLI

## Design Decisions
1. `/clear` — client-side only, reuses existing `clearConversation()`
2. `/effort low|medium|high|max` — stored in localStorage, passed as `effort` field in /v1/chat body, threaded to claude CLI `--effort` flag
3. `/compact` — sends special command to cc_server_p1.py `/cc` with `command: "compact"` flag. cc_server_p1.py detects and runs `claude --resume session_id` with compact. **PARTIAL** — claude CLI `-p` mode doesn't support /compact. Show system message with session ID for manual compact.
4. `/model` — client-side system message showing current model info (cc-sovereign via Max)
5. `/rename name` — client-side, updates localStorage conversation label

## What We're NOT Doing
- No new proxy endpoints (effort passes through existing /v1/chat)
- No streaming yet (Task 5-7)
- No autocomplete dropdown for commands
- No /compact backend support (CLI limitation — mark partial)
