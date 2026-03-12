# Phase: Karma Emergency Fix — CONTEXT

## Date: 2026-03-12
## Session: 85

## What Happened
Karma (hub.arknexus.net) is broken. She's forgotten most of the week, can't use tools she has (fetch_url), and gets confused by contradictory instructions in her system prompt. Previous CC sessions drifted — editing the system prompt without reconciling, slashing MEMORY.md context, and leaving code/prompt mismatches.

## Root Causes (5 confirmed)
1. **System prompt tools contradiction**: Line 69 says "tools always available" but line 254 says "no tools in standard mode." Code routes ALL requests through callLLMWithTools (server.js line 1894). Line 254 is wrong.
2. **MEMORY.md tail slashed 3000→800 chars**: Previous session cut too aggressively. Karma sees ~50 words of recent state.
3. **K2 memory query hardcoded to "Colby"**: server.js line 1820 — fetchK2MemoryGraph("Colby") always searches for "Colby" regardless of user message.
4. **K2 scratchpad + shadow.md not wired**: Karma writes to these files but hub-bridge never reads them back into context.
5. **System prompt 23K+ bloated**: Accumulated contradictions from drifted CC sessions.

## Design Decisions (locked)
- **K2 is Karma's resource, not a service**: System prompt must establish K2 as her own compute substrate (Chromium, Codex, KCC). Delegate heavy work to K2, keep Anthropic model for persona only.
- **Tools always available**: Remove all "deep-mode only" labels. deep_mode header only switches Haiku↔Sonnet quality.
- **MEMORY_MD_TAIL = 2000 chars**: Compromise between 800 (too little) and 3000 (too much).
- **Wire both scratchpad.md + shadow.md**: Single /api/exec call reads both, injected into buildSystemText.
- **K2 continuity is immediate**: Files persist instantly on disk. Crons (hourly/6h) are for long-term promotion, not continuity.

## What We're NOT Doing
- Full Reconciliation step (future)
- Identity Gating mid-task re-sync (future)
- Distributed Context Bus pattern (future)
- K2 LLM upgrade to qwen3:35b-a3b (tabled)
- Deep-mode removal (just fixing the gate confusion)

## Colby's Key Insight
"Karma needs to understand K2 is HER resource available 24/7. Browsing, coding, anything that CAN be done on K2 SHOULD be done on K2. Don't run expensive Anthropic models for work K2 can handle."

## Source Documents Ingested
- `for-karma/CohesiveMemory1.md` — Brain/Muscle architecture, Snapshot-Execute-Reconcile
- `for-karma/KarmaIS.md` — Core truth: K2 IS Karma's, Aria = working name
- `for-karma/KarmaK2Understanding.md` — Karma's self-audit of K2 capabilities
- `for-karma/KCSession031126A.md` — State-write protocol design session
- `for-karma/KCSession031126F.md` — Karma's 11-gap self-audit
- `for-karma/Gemini1.md` — Gemini research: Snapshot-Execute-Reconcile, Hydration Packets
- K2 shadow.md — Karma's own continuity architecture and MCP plan
