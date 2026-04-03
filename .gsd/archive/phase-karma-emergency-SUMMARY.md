# Phase: Karma Emergency Fix — SUMMARY

## Date: 2026-03-12
## Session: 85

## What Was Built
Emergency fix for Karma's broken memory and system prompt. 5 root causes identified and resolved:

1. **System prompt tools contradiction** — Line 254 claimed "no tools in standard mode" while line 69 said "tools always available." Code routes ALL requests through callLLMWithTools. Removed contradiction, added K2 ownership directive.
2. **MEMORY.md tail too short** — 800→2000 chars. Karma now sees ~500 words of recent state.
3. **K2 memory query hardcoded** — "Colby"→userMessage. Now returns relevant facts per request.
4. **K2 working memory wired** — NEW fetchK2WorkingMemory() reads scratchpad.md + shadow.md via /api/exec. 4015 chars injected as 8th param to buildSystemText.
5. **K2 ownership directive** — System prompt now establishes K2 as Karma's resource (Chromium, Codex, KCC). Delegate heavy work to K2, Anthropic model = persona only.

## Verification Results
- K2 working memory: 4015 chars loaded ✅
- K2 memory graph: 1200 chars, 3 hits (dynamic query) ✅
- fetch_url: working in standard mode ✅
- shell_run: Karma used voluntarily during test ✅
- Hub-bridge: started clean, 24594 char identity prompt loaded ✅

## Pitfalls Encountered
- `/api/exec` returns `{ok:true}` not `{success:true}` — different from `/api/memory/graph` which returns `{success:true}`. Caught during verification, fixed immediately.

## What's Pending
- Current_Plan/v12 snapshot (version snapshot per CLAUDE.md rule)
- Gemini research integration (Snapshot-Execute-Reconcile, Hydration Packets) — design validated, implementation deferred
- K2 LLM upgrade to qwen3:35b-a3b (tabled by Colby)
- Full Reconciliation step, Identity Gating mid-task re-sync (future work)

## Files Modified
| File | Change |
|------|--------|
| `Memory/00-karma-system-prompt-live.md` | Removed tools contradiction, added K2 ownership, updated tool list |
| `hub-bridge/app/server.js` | MEMORY_MD_TAIL 800→2000, K2 query fix, fetchK2WorkingMemory(), buildSystemText 8th param |
| `.gsd/STATE.md` | Session 85 status + components |
| `.gsd/ROADMAP.md` | (pending) |
| `MEMORY.md` | Session 85 summary |
| `.gsd/phase-karma-emergency-CONTEXT.md` | Design decisions |
| `.gsd/phase-karma-emergency-PLAN.md` | 8-task execution plan |
