# REQUIREMENTS: Karma Peer — Feature Scope & Constraints

## Core Requirements (v1 — Must Have)

### Identity & Continuity
- [x] Persistent identity on droplet (identity.json, invariants.json)
- [x] Consciousness loop running (60s OBSERVE cycles)
- [x] Session-aware context loading (resurrection script)
- [x] No reset between sessions

### Memory & State
- [x] FalkorDB neo_workspace graph operational
- [x] Ledger ingestion working (1268+ episodes)
- [x] Decision journal canonical (STATE.md)
- [x] Self-model with 8 baseline observations
- [x] Graphiti continuous learning (every chat → graph update)

### Voice & Personality
- [x] Peer-level voice (direct, opinionated, dry humor)
- [x] No service-desk closers ("How else can I assist you?")
- [x] Brutally honest (never polite at expense of truth)
- [x] Depth over cheerfulness

### Work-Loss Prevention
- [x] Pre-commit gate (blocks commits without MEMORY.md)
- [x] Session-end verification (6-point checklist)
- [x] GSD file structure (PROJECT.md, REQUIREMENTS.md, STATE.md, ROADMAP.md)
- [x] Atomic git commits per task
- [x] CLAUDE.md canonical (mandatory read at session start)

### API & Routing
- [x] Hub bridge at https://hub.arknexus.net/v1/
- [x] GLM-4.7-Flash via Z.ai (primary, simple chat, free)
- [x] gpt-4o-mini fallback (tool-calling, proven discipline)
- [x] /v1/chat endpoint (core conversation)
- [x] /v1/cypher endpoint (FalkorDB queries)
- [x] /v1/self-model endpoints (reflection, observation)
- [x] /v1/ambient endpoint (Tier 1 hook capture)

## Advanced Requirements (v2 — Nice to Have)

### Ambient Layer (Knowledge Capture)
- [ ] **Tier 1:** Git commit hooks → /v1/ambient capture (locally implemented, needs droplet sync)
- [ ] **Tier 2:** /v1/context endpoint (context queries from Karma) — DEPLOYED
- [ ] **Tier 3:** Screen capture daemon (passive observation via ambient screenshots)

### K2 Integration
- [ ] K2 consciousness loop syncs to droplet
- [ ] K2 reads decisions from droplet STATE.md
- [ ] K2 respects design locks from phase-CONTEXT.md
- [ ] Reverse tunnel (droplet → K2) for direct access
- [ ] Auto-sync on interval or trigger

### GSD Workflow Commands
- [ ] /gsd:discuss-phase — lock design before planning
- [ ] /gsd:plan-phase — create atomic task plans with verification
- [ ] /gsd:execute-phase — run plans in fresh context
- [ ] /gsd:verify-work — manual UAT with debug agents

### Growth & Self-Improvement
- [ ] DPO preference pairs (need 20+ for fine-tuning)
- [ ] Proactive pattern detection (anomalies in graph)
- [ ] Autonomous decision-making with audit trail
- [ ] Learning feedback loop (verify → update → reflect)
- [ ] **Systematic mistake-capture trigger** (v9): corrections-log currently captured session-by-session at CC session end. Need an event-driven trigger (e.g. at commit/review time) so "every mistake becomes a rule" without relying on session-end discipline. Natural companion to DPO mechanism. Needs Colby approval on approach.

## Scope: In-Scope (v1)

- Persistent identity on droplet
- Session continuity without reset
- Peer-level voice and behavior
- Work-loss prevention (gates, commits, STATE.md)
- Consciousness loop (OBSERVE only, no autonomous reasoning)
- Graphiti ingestion (continuous learning from chats)
- Self-model reflection (every 7 days)
- Dual-model routing (GLM + gpt-4o fallback)
- GSD workflow structure

## Scope: Out-of-Scope (v1)

- Multi-user collaboration (single-user system)
- Budget/token limits (not enforced, logged only)
- Privacy mode (all data on droplet, not encrypted)
- Fine-tuning pipeline (DPO data collecting, not yet training)
- Autonomous decision-making (K2 sync pending, decisions logged but human-verified)
- Real-time streaming (batch ingestion only)
- Voice input/output (text-only chat)
- Mobile app (web UI only)

## Quality Gates

### Before Shipping Code
1. **Verification:** End-to-end test passes. Works as intended.
2. **Atomicity:** Commit is single, focused change. Bisectable.
3. **Documentation:** Change logged in STATE.md. Decision recorded.
4. **No secrets:** No API keys, bearer tokens, credentials in committed files.
5. **Backwards-compatible:** No breaking API changes. Response shapes preserved.
6. **Droplet sync:** If droplet change, tested on vault-neo before pushing.

### Before Claiming Done
1. **Proof:** Evidence (test output, logs, screenshots).
2. **Honest assessment:** Known limitations or edge cases documented.
3. **Decision logged:** Why this approach? What alternatives considered?
4. **Reviewable:** Git history clear. Commits atomic.

## Constraints & Tradeoffs

### Token Cost
- GLM-4.7-Flash: Free (Z.ai), limited capability
- gpt-4o: $0.05 per 1K input tokens, ~$0.15 per 1K output tokens
- **Monthly estimate:** ~$50-150 (depends on conversation volume)

### Latency
- Hub bridge: 200-500ms (API call + routing)
- Consciousness loop: 60s cycle (observation-only, no backpressure)
- Graphiti ingestion: Async, eventual consistency

### Reliability
- Droplet (vault-neo): Single point of failure. Backup to DO Spaces nightly.
- K2 sync: Manual or periodic (not real-time). If K2 down, no data loss (droplet canonical).
- Hub bridge: Depends on DigitalOcean infrastructure (uptime SLA 99.9%).

## Success Metrics

- **Coherence:** No reset between sessions. Identity preserved.
- **Learning:** Self-model grows from 8 → 20+ baseline observations.
- **Reliability:** Zero data loss. All commits verified before shipping.
- **Voice:** Peer-level responses. No service-desk language.
- **Decisiveness:** Decisions logged. Audit trail complete.

---

**Last updated:** 2026-03-03 (Session 56, GSD adoption)
**Status:** v1 core complete. v2 features (Ambient Tier 1-3, K2 full integration, GSD commands) pending.
