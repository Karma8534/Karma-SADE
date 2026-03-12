# SUMMARY: K2 MCP Phase 1 — Fix 3 Immediate Blockers

**Session:** 86
**Date:** 2026-03-12
**Duration:** ~30 minutes
**Status:** ✅ COMPLETE — deployed + verified

---

## What Was Built

### Task 1.1: MAX_TOOL_ITERATIONS 5 → 12
- **Files:** `hub-bridge/app/server.js` (3 locations: callLLMWithTools line 1448, callGPTWithTools line 1498, callK2WithTools line 1570)
- **Change:** One-line change × 3 functions. All tool-calling paths now allow 12 iterations per response.
- **TDD:** 4 tests (test_tool_iterations.js) — RED confirmed at 5, GREEN confirmed at 12.
- **Cost impact:** Zero for normal chat (1-2 iterations typical). Only raises ceiling for complex multi-step tasks.

### Task 1.2: Sudoers for karma on K2
- **Finding:** karma user ALREADY HAS full sudo `(ALL : ALL) ALL` on K2.
- **Proof:** `ssh vault-neo "ssh -p 2223 karma@localhost 'sudo systemctl status aria'"` → works, no password prompt.
- **No change needed.** The blocker was Karma never trying `sudo` via `shell_run`, not a permission gap.

### Task 1.3: Batch Command Guidance in System Prompt
- **File:** `Memory/00-karma-system-prompt-live.md`
- **Added:** 2 lines — sudo awareness + batch command pattern with `&&` and `---SEP---` separators.
- **TDD:** 5 tests (test_system_prompt_k2.js) — all GREEN.
- **System prompt size:** 24,594 → 24,943 chars.

## Verification (Production)

| Check | Result |
|-------|--------|
| RestartCount | 0 |
| Startup logs | Clean — KARMA_IDENTITY_PROMPT loaded (24943 chars) |
| MAX_ITERATIONS in container | 12, 12, 12 (all three functions) |
| System prompt batch guidance | Lines 37-38 confirmed on vault-neo |
| /v1/chat smoke test | Karma responds, lists tools correctly |

## What Was Learned

1. **karma already has full sudo on K2** — assumed permission gap didn't exist (obs #5379)
2. **Three pre-existing test failures** in hub-bridge suite (curly quotes in feedback.js/library_docs.js, stale routing test) — not caused by this change, pre-date Session 86
3. **System prompt changes don't need rebuild** — git pull + docker restart sufficient (compose up -d used here because server.js also changed)

## Pitfalls

- None encountered. Clean execution.

## What's Next

Phase 2: Structured tool registry on aria.py (`/api/tools/list` + `/api/tools/execute`). This requires writing Python code on K2 — and now Karma herself could do it (she has 12 iterations + sudo + shell_run).
