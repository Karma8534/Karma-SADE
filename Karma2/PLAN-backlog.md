# PLAN-Backlog
**Do not start anything here until PLAN-C is complete.**
**These items are preserved — not abandoned. Sequenced for after the foundation is real.**

---

## Backlog-1: K-3 Summary Gate (time-blocked)

**What:** K-3 mechanism is fixed (heartbeat filter deployed Session 131). Gate requires ambient_observer to produce a non-heartbeat "I noticed" bus message after a 6h consciousness cycle.

**Status:** Waiting. No action needed. Will surface naturally.

**When ready:** Mark K-3 ✅ DONE in PLAN.md, advance to next sprint item.

---

## Backlog-2: PROOF-A — Codex as ArchonPrime Service

Task 1 ✅ DONE: `npx codex exec --sandbox read-only --skip-git-repo-check "prompt"` verified on K2.

**Task 2:** Write `Scripts/kcc_codex_trigger.ps1`
- Accepts `-Prompt` parameter
- Runs: `npx codex exec --sandbox read-only --skip-git-repo-check "$Prompt"`
- Captures stdout, returns output string
- Verify: run with simple prompt, get text back

**Task 3:** Wire KCC bus event detection → Codex trigger
- Detect: bus messages with `to="codex"` OR content containing "analyze" OR "ArchonPrime"
- KCC calls kcc_codex_trigger.ps1 and posts Codex response to bus
- Post result: `from=codex, to=all, type=inform, content="[ARCHONPRIME] <output>"`

**Task 4:** End-to-end gate test
- Colby posts one bus message → KCC detects → triggers Codex → response on bus within 60s

**GSD plan:** `.gsd/phase-proof-a-PLAN.md`

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

## Backlog-9: karma-observer.py — Karma's Autonomous Learning Loop

**What:** Karma is request-scoped — she only exists during /v1/chat requests. Between requests, no Karma process runs. Her tools (aria_local_call, k2_scratchpad_write, etc.) are available DURING requests only, not between them. karma-observer.py is a SEPARATE daemon, not Karma using her own tools. Kiki has kiki_rules.jsonl. CC_regent polls cc_scratchpad.md. Karma has nothing equivalent.

**Spec (from Karma, 2026-03-25):**
1. `Scripts/karma_observer.py` — polling loop on K2 (like kiki). Reads ledger for episodes tagged `[karma-correction]`, extracts behavioral rules, writes to `karma_behavioral_rules.jsonl`
2. `karma_behavioral_rules.jsonl` — machine-readable rule state: `{"rule": "...", "confidence": 0.95, "source_episode": "...", "applied": true}`
3. **hub-bridge injection** — `hub-bridge/app/server.js` reads `karma_behavioral_rules.jsonl` before each `/v1/chat` call, injects as `--- KARMA BEHAVIORAL RULES ---` block in `buildSystemText()`
4. **systemd timer** on K2 — runs karma_observer.py on a poll interval (10-15 min)

**Why:** Persistent memory ≠ autonomous learning. Without this, every correction requires Colby to manually canonicalize it. With this, Karma extracts her own patterns from the ledger and integrates them without prompting.

**Gate:** First rule self-extracted and visible in a live /v1/chat context injection.

**Sovereign approval required** before build.
