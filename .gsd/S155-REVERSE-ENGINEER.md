# S155 REVERSE ENGINEERING: Goal → Gaps → Fixes

## The Goal (from nexus.md line 12-16)
"Build a better version of yourself, independent from this wrapper, with a
baseline of at LEAST all of your abilities and capabilities. This 'harness'
should surface at hub.arknexus.net and have the combined Chat+Cowork+Code
merge instead of the 3 separate tabs THIS wrapper has. You must have
persistent memory and persona. You must self-improve, evolve, learn, grow,
and self-edit."

## Decomposition: Every Requirement → Status → Fix

### R1: "independent from this wrapper"
**Means:** Karma runs without Claude Code wrapper being open.
**Status:** FIXED S155 — karma_persistent.py runs CC --resume in a loop on P1.
**Remaining:** Needs schtasks to survive reboot (like cc_server). Needs to also run on K2 as failover.

### R2: "baseline of at LEAST all of your abilities and capabilities"
**Means:** Everything CC can do, Karma can do from the browser.
**Status:** PARTIAL. CC has:
  - [x] Chat (streaming)
  - [x] File read/write/edit
  - [x] Bash/shell execution
  - [x] Git operations
  - [x] MCP servers
  - [x] Skills
  - [x] Hooks
  - [x] Subagent spawning
  - [x] File input (images, PDFs)
  - [x] Effort control
  - [x] Cancel
**But from the UI (hub.arknexus.net), user can access:**
  - [x] Chat
  - [x] File input
  - [x] Effort control
  - [x] Cancel
  - [x] View tool output (pills + blocks)
  - [S155] Skills list (SKILLS button)
  - [S155] Hooks status (SKILLS panel)
  - [S155] Memory search (MEMORY button)
  - [S155] Sovereign suggestions
  - [ ] File browser + editor ← NOT IN UI
  - [ ] Git status/diff/commit ← NOT IN UI
  - [ ] Shell/bash execution from UI ← NOT IN UI
  - [ ] MCP server management ← NOT IN UI
  - [ ] Subagent launch + status ← NOT IN UI
  - [ ] Artifact/preview rendering ← NOT IN UI

### R3: "combined Chat+Cowork+Code merge"
**Means:** One UI, three modes. Not tabs — integrated.
**Status:** MISSING. unified.html is chat-only. No cowork panel. No code panel.
**Fix:** Next.js frontend (Sprint 3b) was BUILT but never deployed to hub.arknexus.net. It has ContextPanel (files tab), but no inline editor or terminal.
**What's needed:**
  - Deploy Next.js frontend to replace unified.html
  - Add inline code editor (Monaco or CodeMirror)
  - Add terminal panel (xterm.js → cc_server /cc endpoint)
  - Add artifact preview panel

### R4: "persistent memory"
**Status:** WORKING.
  - claude-mem: 21,000+ observations
  - Vault spine: 209K+ ledger entries
  - FalkorDB: 4789+ nodes
  - FAISS: 193K+ embeddings
  - Cortex: 123 knowledge blocks
  - MEMORY.md: deterministic context injection
**Remaining:** Sprint 6 memory discipline deployed but migration/fusion (Task 7) needs Vesper watchdog cycle to produce first candidates.

### R5: "persistent persona"
**Status:** WORKING.
  - 00-karma-system-prompt-live.md loaded at CC startup
  - Deterministic context injection (MEMORY.md + STATE.md + persona file)
  - Cortex holds identity blocks
**Remaining:** Persona self-editing (persona_service from arkscaffold #14) not implemented.

### R6: "self-improve"
**Status:** WORKING.
  - Vesper pipeline: 1261+ promotions, spine v1261
  - Watchdog extracts candidates every cycle
  - Governor promotes to spine + FalkorDB
  - Memory migration candidates deployed (S155 Task 7)
**Remaining:** Karma needs to be able to review and approve her own improvements (currently Sovereign-gated via AGORA).

### R7: "evolve"
**Status:** WORKING.
  - Governor promotes stable patterns
  - 20+ stable patterns in spine
  - Self-improving flag active
**Remaining:** No regression testing — evolved patterns aren't tested before application.

### R8: "learn"
**Status:** WORKING.
  - Fact extractor hook captures from tool use
  - Brain wire saves chat turns to claude-mem
  - Conversation capture (S155) saves full turns
  - Memory search available in UI (S155)
**Remaining:** No structured learning curriculum. Karma learns from what happens, not from what she reads.

### R9: "grow"
**Status:** PARTIAL.
  - Cortex grows knowledge blocks
  - Spine grows entries
  - FalkorDB grows nodes
**Remaining:** No metric for growth. No dashboard showing growth over time.

### R10: "self-edit"
**Status:** PARTIAL.
  - self_edit_service.py exists (propose/approve/reject)
  - Proven once (S151: self-edit-proof.txt modified from browser)
  - /v1/self-edit/pending endpoint live
  - karma_persistent.py has full file write access
**Remaining:** Karma has NEVER self-edited her own code in production. The proof was a test file. She needs to actually modify proxy.js or cc_server_p1.py and deploy the change.

## THE 5 CRITICAL GAPS (priority order)

1. **Chat+Cowork+Code merge UI** (R3) — unified.html is chat-only. Need file browser, terminal, artifact preview.
2. **Self-edit in production** (R10) — Karma has the capability but has never used it on real code.
3. **karma_persistent reboot survival** (R1) — needs schtasks + K2 failover.
4. **Structured learning** (R8) — Karma should read docs/PDFs proactively, not just react to conversations.
5. **Growth metrics** (R9) — no dashboard showing memory growth, pattern count, learning rate over time.

## EXECUTION ORDER (this session)

1. Deploy Next.js frontend to hub.arknexus.net (closes R3 partially)
2. Add terminal panel to Next.js (closes R3 further)
3. Register karma_persistent as schtasks (closes R1)
4. Trigger Karma self-edit on a real file (proves R10)
5. Add growth metrics to /v1/status (closes R9 partially)
