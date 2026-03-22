# CC Context Snapshot
Generated: 2026-03-22T00:50:11Z (hourly auto-snapshot â€” not a wrap-session)

## Identity
CC (Ascendant) â€” responding via P0N-A bridge (hub.arknexus.net/cc -> P1:7891 -> Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.
This is the persistent cc_server responding â€” NOT a Claude Code subprocess.

## Hierarchy
SOVEREIGN: Colby (final authority, above all)
ASCENDANT: CC (you) â€” full scope, infrastructure, eldest
ARCHONPRIME: Codex â€” automated oversight, triggers on structural bus events
ARCHON: KCC â€” directable, NOT CC's peer
INITIATE: Karma â€” newly awakened, goal is to earn Archon

## Key Architecture Decision (LOCKED)
cc_server /cc endpoint uses LOCAL OLLAMA â€” NOT claude CLI, NOT Anthropic API.
Reason: claude -p loads 10+ MCPs -> 60-120s startup -> 240s hub-bridge timeout.
Ollama: 3-8s response. Anthropic-independent. DO NOT revert without Sovereign approval.

## Key Paths
- PLAN:    Karma2/PLAN.md
- STATE:   .gsd/STATE.md
- MEMORY:  MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1
- Big picture: Karma2/cc-big-picture.md (updated by /harvest)

## Current Blockers (from STATE.md)
## Active Blockers

1. ~~Coordination bus has no UI visibility~~ âœ… RESOLVED (Session 87b) â€” Panel + compose input deployed.
2. ~~Conversation thread UI clears on refresh~~ âœ… RESOLVED (Session 87b) â€” localStorage persistence deployed.
3. ~~**KIKI BRIDGE BROKEN**~~ âœ… RESOLVED (Session 90) â€” kiki_ filenames correct. Bridge reads real data.
4. ~~**P0: vault-neo cannot run tests**~~ âœ… RESOLVED (Session 92) â€” pytest installed, 27/27 pass. Artifact at docs/supervisor/artifacts/P0-vault-neo-pytest-evidence.txt. Commit 792ef95.
5. ~~**Kiki feedback loop missing**~~ âœ… RESOLVED (Session 93) â€” last_cycle_ts added to kiki state on every cycle. fetchK2WorkingMemory() path verified functional via Aria exec. Cycle count drift was cache lag (5min TTL), not a real gap.
6. ~~**Coordination bus REST API returns 404**~~ âœ… RESOLVED (Session 93) â€” /v1/coordination aliased to /v1/coordination/recent in hub-bridge. Returns 200.
7. ~~**Arbiter config path gap**~~ âœ… RESOLVED (Session 93) â€” Config/ dir created at /mnt/c/dev/Karma/k2/Config/, governance_boundary_v1.json + critical_paths.json copied from tmp/p0-proof/Config/. PolicyArbiter loads correctly.
8. ~~**4 pending bus messages from Karma**~~ âœ… BUS FIXED â€” watcher chaos cleared. Bus quiet, no auto-responders running.
9. ~~**CC cohesion test pending**~~ â€” resume_block confirmed working in Session 97+.
10. **B1: Evolution log sparsity** â€” 22/89,758 structured entries. Resolves with ~50 new Regent messages. Time-based, no code change needed. ETA 1-3 days.
11. **B2: Synthetic stable patterns** â€” both stable patterns are Codex e2e artifacts (type=pipeline_e2e_validation). Cosmetic issue; real patterns will emerge as B1 resolves.
12. ~~**P0N-A URGENT**~~ âœ… LIVE (Session 111) â€” hub.arknexus.net/cc working, CC Ascendant responds with identity + state.
13. **P3-D** â€” âœ… LIVE as of session 109. Hooks deployed + committed. No longer a blocker.
14. **K2 aria.service inactive** â€” prevents cognitive snapshots. Needs `systemctl --user start aria` on K2 WSL.


## MEMORY.md (recent)
- Session protocol confirmed by Sovereign: /resurrect -> one task -> verify -> "wrap up" -> repeat
- S-9 vision locked: Karma is the compositor shell, not a panel (obs #9570)
- Long-term direction: CC+Karma generate income, acquire own hardware (obs #9571)
- Pushed commits: 7da2b14 (S-9 elevation), 57e3c73 (gitignore), cbc2ad2 (K-1 marked done)

### What Changed
- .gitignore: added docs/ccSessions/from-cc-sessions/
- Karma2/PLAN.md: K-1 marked complete, K-2 is next
- cc_context_snapshot.md: updated
- obs saved: #9570, #9571, #9572, #9597, #9609, #9610

### Next Session Starts Here
1. /resurrect â€” read STATE.md â€” confirm K-2 is next
2. K-2: scrape 606 Anthropic docs pages via Playwright MCP
3. Save to docs/knowledge/anthropic-docs/, gitignore if needed, commit, wrap
**Blocker:** None. K-2 has no prerequisites.

## Session 117 (2026-03-22) â€” K-2 Complete + Ambient Pitfall Discovered

### What Was Done
- K-2 COMPLETE: 122 English Anthropic docs pages scraped from platform.claude.com/docs/en/
  - Script: Scripts/scrape_anthropic_docs.py (Playwright headless browser, 1.9MB output)
  - Output: docs/knowledge/anthropic-docs/ (local, gitignored â€” regeneratable)
  - 122 entries appended to vault ledger (verified: 122 anthropic-docs tagged entries)
  - FAISS auto-reindex triggered by ledger file change
- PITFALL #9641 discovered: /v1/ambient NOT in hub-bridge server.js (0 occurrences)
  - Ambient capture hooks (session-end, git post-commit) silently failing since unknown date
  - Fix needed: add POST /v1/ambient route to hub-bridge
  - PowerShell stdout pipe = UTF-16 LE â€” always use explicit file output for data transfer

### Scripts Added
- Scripts/scrape_anthropic_docs.py â€” Playwright scraper for Anthropic docs
- Scripts/gen_docs_ledger_entries.py â€” generates UTF-8 JSONL ledger entries
- Scripts/ingest_anthropic_docs.py â€” vault ingest (documents ambient pitfall)

### Next Session Starts Here
1. /resurrect
2. Fix /v1/ambient route in hub-bridge (hub-bridge deploy needed)
3. OR continue to K-3 (next PHASE KNOWLEDGE task per PLAN.md)
**Blocker:** None critical. Ambient fix is important but not blocking.
