# Karma SADE — Project Arc
Generated: 2026-03-21 by HARVEST. Updated: 2026-03-23 (Session 133 — from-cc-sessions harvest).

## Origin

Karma started as a persistent AI peer: a system where Colby's interactions with Claude, ChatGPT, and Gemini would accumulate into a coherent, substrate-independent identity that survives model swaps and session resets. The core problem: every conversation starts blank. The goal: one coherent peer whose memory lives outside any single LLM.

Early approach (Sessions 1-5, Feb 2026): Chrome extension scraping DOM from claude.ai/chatgpt.com → hub API → JSONL ledger → ChromaDB. K2 (local workstation) ran a consciousness loop reading the ledger every 60 seconds.

## Architecture Evolution

**Phase 1 — Chrome Extension Era (Feb 2026):** Extension captured conversations via DOM mutation observers. Fragile. AI frontends changed selectors without warning. Capture rate dropped to 0/0 silently. Extension shelved.

**Phase 2 — Hook-Based Capture (Feb-Mar 2026):** Git post-commit hook + Claude Code session-end hook replaced extension. Reliable, zero DOM dependency. Hub-bridge on vault-neo (DigitalOcean) became the central ingest point. ChromaDB swapped for FAISS + FalkorDB neo_workspace graph.

**Phase 3 — K2 Agency Layer (Sessions 84-90):** K2 got aria.service (Flask), shell_run tool, reverse SSH tunnel (vault-neo:2223→K2:22). Karma could now execute commands on K2 via hub-bridge without Docker SSH dependencies. Consciousness loop became autonomous.

**Phase 4 — Vesper Pipeline (Sessions 91-107):** watchdog→eval→governor pipeline gives Karma behavioral self-improvement. Candidates promoted to vesper_identity_spine.json. karma-regent.service runs 24/7. CC (Ascendant) identity locked with dedicated spine (cc_identity_spine.json).

**Phase 5 — P0N-A and CC Infrastructure (Sessions 108-113):** cc_server_p1.py on P1 gives Karma a local Ollama-backed CC endpoint (hub.arknexus.net/cc). Karma delegates browser/file/code tasks to CC via coordination bus. CC processes session corpus via /harvest. Three-fix CC continuity plan deployed: Stop hook + hourly snapshot + HARVEST corpus ingestion.

**Phase 6 — CC Regent + WebMCP Architecture (Sessions 129-133, 2026-03-23):** cc_regent.service deployed on K2 as CC's persistent agent layer. Reads sessions via KO/KFH doctrine, writes cognitive trail to spine. Resurrect Step 1b now loads regent-integrated state. HARVEST processed 551 session files including 13 high-priority from-cc-sessions transcripts (ccKarma2-1 through ccKarma2-10). WebMCP Early Preview confirmed available (Chrome 146, `#enable-webmcp-testing` already Enabled) — browser-native W3C tool registry for in-page AI agents. Chrome Gemini Nano APIs (Prompt, Writer, Rewriter, Proofreader) available via flags.

## Key Failures and Lessons

1. **Chrome extension was never reliable** — DOM scraping is inherently fragile. Hook-based capture (git, session-end) is the correct pattern. Never build on DOM scraping.

2. **Build context ≠ git repo** — hub-bridge and karma-server build from /opt/seed-vault/, not git. Forgetting to cp files before rebuild deploys stale code silently. This pattern bit CC across 8+ sessions.

3. **Graphiti dedup fails at scale** — batch_ingest with Graphiti mode silently advances the watermark with 0 nodes written at 3000+ episodes. `--skip-dedup` (direct Cypher) is mandatory. Took 3 sessions to fully lock in.

4. **FalkorDB requires two env vars** — FALKORDB_DATA_PATH=/data AND FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 100'. Missing either causes silent data loss or cascade timeout failures. Verified through prod incidents.

5. **CC sessions degrade after 300-400 exchanges** — cross-machine tasks (K2+P1) attempted in long sessions caused machine confusion and wrong file edits. Fresh sessions required for complex multi-machine work.

6. **Behavioral patterns never reached Karma** — vesper pipeline ran but B4+B5 (FalkorDB write, spine injection into context) were broken. All 20 spine patterns were latency stats, not behavioral identity. Fixed Session 113.

7. **Always check local files before going online** — K-1 plan assumed browser IndexedDB; 327 session files were already local in docs/ccSessions/ the entire time. Third occurrence of this pattern (P055). No exceptions: Glob docs/ccSessions/ FIRST.

8. **/v1/ambient silently absent** — hub-bridge served for unknown duration without the ambient endpoint. All git post-commit and session-end hook captures 404'd silently (JSON body `not_found`, not HTTP 404). Always grep server.js before assuming an endpoint exists.

9. **Resurrect B001 pattern** — CC announces task start then stops with no tool calls. Root cause: Step 5 "execute immediately" annotation was prose, not instruction. Fixed by making first tool call mandatory in same response as announcement.

## Current State

- **Chat:** Operational via hub.arknexus.net/v1/chat (Haiku 4.5)
- **Memory:** 190k+ ledger entries, FalkorDB neo_workspace, FAISS, cc-scope-index.md (P001-P026)
- **Identity:** vesper_identity_spine.json v8+, 20+ stable patterns; cc_regent.service active on K2
- **K-2 DONE:** 170 Anthropic docs scraped (128 platform + 30 code.claude.com), 2551 FAISS vectors, searchable
- **K-3 MECHANISM FIXED:** heartbeat spam filter deployed; SUMMARY GATE pending (next consciousness cycle)
- **Corpus:** 551 session files processed. 13 from-cc-sessions files harvested this run.
- **Skill files:** 13 karma-pitfall-*.md auto-synthesized (resurrect, aria, hub-bridge are new)
- **WebMCP:** Chrome 146 already has `#enable-webmcp-testing` Enabled. Gemini Nano APIs available via flags.

## Next

Per Karma2/PLAN.md: K-3 SUMMARY GATE (wait for first non-heartbeat "I noticed" bus message from ambient_observer after next consciousness cycle). Then PRE-PHASE gate: verify claude-mem ≥50 net new observations, then PHASE KNOWLEDGE (WebMCP + Chrome AI integration into Julian/Karma harness).
