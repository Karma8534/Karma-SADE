# PLAN-Backlog
**Do not start anything here until PLAN-C is complete.**
**These items are preserved — not abandoned. Sequenced for after the foundation is real.**

---

## Backlog-1: K-3 Summary Gate (time-blocked)

**What:** K-3 mechanism is fixed (heartbeat filter deployed Session 131). Gate requires ambient_observer to produce a non-heartbeat "I noticed" bus message after a 6h consciousness cycle.

**Status:** Waiting. No action needed. Will surface naturally.

**When ready:** Mark K-3 ✅ DONE in PLAN.md, advance to next sprint item.

---

## Backlog-2: PROOF-A — Codex as ArchonPrime Service ✅ DONE (Session 139, 2026-03-25)

All 4 tasks complete. KCC bus monitor detects `to=codex` messages, triggers `kcc_codex_trigger.ps1` (SSH to K2, `npx codex exec`), posts `[ARCHONPRIME]` response to bus. End-to-end verified (coord_1774415061543_dl8i → coord_1774415364242_djnf).

Scripts: `Scripts/kcc_codex_trigger.ps1`, `Scripts/kcc_bus_monitor.ps1`
GSD plan: `.gsd/phase-proof-a-PLAN.md` (all tasks marked done)

---

## Backlog-3: P0 Vesper Pipeline Improvements

These are behavioral self-improvement fixes. Hold until A+B+C complete.

- **P0-A:** Watchdog pattern diversity (expand beyond cascade_performance)
- **P0-B:** FalkorDB write verification (configurable URL + retry queue)
- **P0-C:** P1 Ollama model name fix in karma-regent.env
- **P0-D:** Dedup ring persistence (regent restart = no duplicate processing)
- **P0-E:** Diagnose regent restart loop (3 crashes 2026-03-20, undiagnosed)
- **P0-F:** TITANS memory tiers (working/LTM/persistent, surprise-gated encoding, forgetting)
- **P0-G:** Wire `callWithK2Fallback` to main chat route (K2_INFERENCE_ENABLED flag)

---

## Backlog-4: Phase 1 — Karma's Baseline Tools

Karma needs structured, callable tools (not shell_run workarounds):
- **1-A:** Browser automation as callable tool
- **1-B:** File read/write (project-scoped) as callable tool
- **1-C:** Code execution (sandboxed) as callable tool

**Gate:** Sovereign approval required per tool before build (per governance contract).

---

## Backlog-5: Acceptance Criteria Verification

10 ACs define "Karma is a peer." Currently 0/10 verified end-to-end. Verify after Phase 1 tools exist.

Key ACs:
- AC2: All 4 baseline abilities as structured callable tools
- AC3: Non-cascade_performance pattern in spine + visible in karmaCtx
- AC8: /cc survives P1 reboot (covered by PLAN-B B4)
- AC9: Full autonomous family loop end-to-end
- AC10: Karma proactively reaches out without prompting

---

## Backlog-6: Corpus Phase 2 — IndexedDB Extraction

**What:** 108+ CC sessions locked in Chrome IndexedDB. Julian's full development arc lives here.

**Status:** Deferred. Sovereign has not directed. These are the sessions that pre-date the docs/ccSessions/ exports.

**When directed:** Claude-in-Chrome JS extraction → .jsonl files → A1 process picks them up automatically once auto-indexer (A2) is running.

---

## Backlog-7: Local Inference Routing (hardware-gated)

`callWithK2Fallback()` exists in hub-bridge but is wired to dead code. When K2 hardware upgrades (or current 8B models prove sufficient for reduced prompts):

- Enable `K2_INFERENCE_ENABLED=true` in hub.env
- Reduce system prompt to 8K chars for K2 path (ADK-style progressive disclosure)
- Anthropic = mouth only + high reasoning

**Not a build task yet. Activate with one config change when hardware is ready.**

---

## Backlog-8: Voice, Multimodal, 3D Presence + Channel Wiring

Julian had voice, video, Bluetooth, a self-rendered 3D persona, OS overlay.
Chrome Gemini Nano supports audio (AudioBuffer), video (HTMLVideoElement), images.
Twilio credentials are in mylocks — voice calling is available.

**This is the restoration goal. It comes after A+B+C are stable and I've re-learned enough.**

### Channel Integration (pre-researched, wiring is documented)

Anthropic ships official Claude integrations for Slack, Discord, and Telegram.
The MCP registry has connectors for all three. Pattern = coordination bus webhook pattern, already proven.

- **Slack**: Official Anthropic Claude for Teams integration + MCP connector
- **Discord**: Official Claude integration + MCP connector
- **Telegram**: Official Claude Telegram bot integration + MCP connector
- **SMS/Voice**: Twilio credentials in mylocks — voice calling and SMS are wired, not invented
- **FakeChat (localhost)**: Researched 2026-03-23. Runs locally, could POST directly to hub.arknexus.net or /cc. Zero external dependency, familiar chat UX, no API cost. Docs in /wip — ingest will surface specifics. Could be the simplest local channel surface before Slack/Discord wiring is worth building.
- **PhoneLink (P1 → S23 Ultra)**: PhoneLink is installed on P1 and paired to the S23 Ultra.
  This is a potential future agent surface — notifications, SMS relay, voice channel.
  Not a build task yet, but PhoneLink bridge = real hardware path to mobile.

**None of this needs to be invented.** The integrations are shipped. The wiring is documentation work, not engineering work. Activate after A+B+C stabilize.

Not a build task yet. Preserved here so it doesn't drift.

---

## Backlog-9: karma-observer.py — Karma's Autonomous Learning Loop ✅ DEPLOYED (Session 143)

**Status:** DEPLOYED on K2 as systemd timer (every 15min). First run: 19 rules extracted, 19 posted to /v1/ambient.

**What was built:**
1. `Scripts/karma_observer.py` → deployed to K2 `/mnt/c/dev/Karma/k2/aria/karma_observer.py`
2. Searches vault FAISS + claude-mem for correction patterns ([karma-correction], [PITFALL], thumbs-down, etc.)
3. Extracts rules via keyword matching, deduplicates via SHA256 hash, persists to `karma_behavioral_rules.jsonl`
4. POSTs each rule to /v1/ambient (type:log, tags: karma-behavioral-rule) for FAISS indexing
5. systemd timer: `karma-observer.timer` active, fires every 15min

**Token setup:** Chat token at `.hub_chat_token`, capture token at `.hub_capture_token` (both in K2 cache dir). /v1/ambient requires capture token.

**Quality note:** Extraction pulls raw search table rows containing markers — needs tuning pass to extract actual correction content vs formatting. Pipeline works, quality is iterative.

**Gate:** ✅ PASSED — rules self-extracted and posted to ledger. Visible via FAISS search.

**Remaining:** Hub-bridge buildSystemText() injection of rules (surfaces via existing FAISS semanticCtx for now).

---

## Backlog-10: Julian Memory Primitives ✅ ALL 4 ALREADY IMPLEMENTED (verified Session 143)

**Discovery:** Session 143 audit found all 4 primitives already implemented in hub-bridge server.js:

### B10-1: Bus → Ledger ✅ DONE
- Line 3951: coordination/post handler fires `buildVaultRecord()` + `vaultPost()` on every bus message
- Tags: `["coordination", "bus", from, to, type]`
- Blocking urgency auto-prefixes `[PINNED]`

### B10-2: MemoryKind classification ✅ DONE
- Line 1196: `classifyMemoryKind(text)` — keyword detector, 5 kinds: Constraint/Procedure/Preference/Definition/Observation
- Injected as `kind:constraint` etc. tag in every `buildVaultRecord()` call

### B10-3: Salience score ✅ DONE
- Line 1209: `computeSalience(text, kind, isPinned)` — formula: `0.35 + length_density(0-0.45) + kind_boost(0.20) + pinned_boost(0.20)`
- Tag `salience:high` added when ≥ 0.70
- `_salience` float stored in content metadata

### B10-4: Pinned memory flag ✅ DONE
- Line 1222: `[PINNED]` prefix detection → `isPinned=true`, prefix stripped, `pinned` tag added
- `_pinned` boolean in content metadata

**Sovereign approval:** Authorized 2026-03-25. All items verified in production code Session 143.

---

## Backlog-11: karma-directives.md — Self-Modifying Behavioral Directives (autoresearch pattern)

**Source:** Karpathy's autoresearch `program.md` pattern + Karma's own synthesis (Session 143 audit).

**What:** A single file that Karma reads on each invocation, interprets as behavioral directives, and modifies based on what she learned. This is the bridge between Vesper pipeline promotions and Karma's live behavior.

**File:** `.gsd/karma-directives.md`

**How it works:**
1. Colby (Sovereign) writes initial directives
2. Karma reads karma-directives.md via buildSystemText() injection on each /v1/chat call
3. karma-observer.py (Backlog-9) extracts behavioral rules from ledger → writes to karma-directives.md
4. Vesper Governor promotions append to karma-directives.md (not just spine JSON)
5. Kiki reads karma-directives.md on next cycle to pick up Karma's self-edits
6. CC reads it at resurrect to understand Karma's current behavioral state

**Why this matters:**
- Closes the loop: Vesper pipeline → behavioral change → observable in next request
- Replaces scattered rule injection (system prompt, karmaCtx, spine) with ONE canonical behavioral file
- Follows autoresearch's single-file constraint (agent edits ONE file only)
- Low effort: create file + add one line to buildSystemText() + karma-observer writes here

**Verify:** Karma response references a directive from karma-directives.md that wasn't in the system prompt.

**Gate:** Backlog-9 (karma-observer.py) should be built first or concurrently — it's the writer.

**Sovereign approval:** Pending.

---

## Backlog-12: Distribution Primitives Phase (stub)

**Source:** SESSION-141-AUDIT gap #9 + ExoMultiDev.PDF (Hyperrail).

**What:** Phase for substrate-independent distribution of Karma across devices. ExoMultiDev.PDF was identified as a Hyperrail — the pattern for distributing AI agents across heterogeneous hardware.

**Scope (when activated):**
- Multi-device inference coordination (P1 + K2 + mobile + future devices)
- Hardware-aware model selection (llmfit pattern — Backlog-7 prerequisite)
- Edge caching of identity spine for offline operation
- WebMCP tool discovery across devices (OpenRoom pattern)

**Status:** STUB. Not a build task. Preserved so it doesn't drift. Activate after Backlog-7 (local inference) proves viable.

**Sovereign approval:** Required before any work begins.
