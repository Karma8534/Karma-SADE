# Codex Nexus Plan

Date: 2026-04-05

This is the replacement execution plan derived from:
- `docs/ForColby/nexus.md` v5.5.0
- `.gsd/codex-cascade-audit.md`
- `Karma2/map/preclaw1-gap-map.md`
- `.gsd/phase-cascade-pipeline-PLAN.md`
- `docs/anthropic-docs/*`
- `docs/claude-mem-docs/*`
- `docs/wip/preclaw1/preclaw1/src`

## Purpose

Build a better version of the harness that:
- uses the existing browser/Electron Nexus as one continual merged workspace
- exceeds the Codex + Claude Code floor
- preserves persistent memory, persona, and session continuity
- exposes a single combined Chat + Cowork + Code workspace by default
- can self-improve only through verified diffs and verified tests
- closes the preclaw1 gap map instead of drifting into infrastructure-only work

## Audit Corrections

The old plan had these blockers:
- `Vesper/vesper_watchdog.py` was treated like a candidate engine; it is only a small brief/spine writer and needs new parser/ranker primitives.
- `Scripts/vesper_governor.py` was mapped to a nonexistent `apply_promotion()`; the real apply path is `_apply_to_spine()` plus `run_governor()`.
- `Scripts/vesper_eval.py` can currently approve confidence-only or diff-less work; the executor loop must reject no-diff and no-test candidates before scoring.
- `Karma2/map/preclaw1-gap-map.md` was treated as if row updates alone were enough; summary totals and row status must update atomically.
- The plan missed the claude-mem primitives for hook-based memory capture, privacy tags, progressive disclosure search, and worker-service separation.

## Non-Negotiables

1. One candidate, one diff, one test, one promotion.
2. No promotion without a real file delta.
3. No promotion without a real test command and real test output.
4. No gap-map update unless the change is applied and smoke-tested.
5. No concurrent writers without a lock strategy.
6. No separate-surface expansion before the core continuity/executor loop is stable.
7. No claim of progress without evidence in state files or logs.

## Assimilated Primitives

### From Anthropic docs

- Tool-use and message semantics as the schema/reference substrate; for Max, the primary live path remains `CC --resume` rather than paid direct Anthropic API.
- Model choice, effort, fast mode, and context budgeting.
- Prompt caching and context compaction.
- Token counting and cost visibility.
- Structured outputs and citations.
- Web search, web fetch, code execution, and file support.
- Tool-use framework, permissions, hooks, sessions, and subagents.
- MCP connector, remote MCP servers, skills, plugins, slash commands, todo tracking.
- Desktop, web, VS Code, JetBrains, Chrome, Slack, GitHub Actions, and GitLab surfaces.

### From Claude Code source

- Command registry and slash-command model.
- Session history model with resume, rewind, compact, export, share, rename, tag.
- Context assembler with explicit budget control.
- Cost tracker and hooks.
- Query engine and retrieval primitives.
- Task model and tool model.
- Settings schema and typed state model.
- Services layer, plugin subsystem, remote transport, and upstream proxy.
- Keybindings, vim mode, voice, memory scanning, output styles, onboarding.

### From claude-mem

- Lifecycle hooks for session and tool events.
- Worker-service separation for expensive operations.
- SQLite plus vector-hybrid memory.
- Progressive disclosure search: search -> timeline -> full detail.
- Privacy tags before persistence.
- Skill-based retrieval and execution skills.
- Exit-code discipline and restart discipline.
- Build-and-sync automation around a plugin boundary.

## Architecture

The harness should have four layers:
- Core executor layer: gap closure, task execution, diff/test gating.
- Brain layer: persistent state, summary injection, retrieval, privacy.
- Workspace layer: the already-existing browser/Electron merged workspace, session continuity, permissions, diff view, cowork/code integration.
- Growth layer: plugins, skills, transport, self-improvement loop.

The older `agent` / `orchestrator` framing is retained only inside the core executor and growth layers as an implementation pattern. It is not the product architecture. The product architecture is one unified brain in one merged workspace with one continual session by default.

The core executor layer must be finished first.

## Phase 0: Load-Bearing Core

Goal: make the system able to accept a gap, generate a real candidate, verify it, and apply it safely.

Files:
- `Scripts/karma_persistent.py`
- `Scripts/vesper_eval.py`
- `Scripts/vesper_governor.py`
- `Vesper/vesper_watchdog.py`
- `Vesper/karma_regent.py`
- `Karma2/map/preclaw1-gap-map.md`

Work:
- Add `gap_closure` as a first-class actionable type in `Scripts/karma_persistent.py`.
- Build structured gap-closure context from the gap map and target files.
- Reject candidates in `Scripts/vesper_eval.py` that lack `target_files`, `test_command`, or a real diff.
- Route only smoke-tested promotions through `Scripts/vesper_governor.py`.
- Add gap-map parsing, ranking, and emission helpers to `Vesper/vesper_watchdog.py`.
- Add gap backlog summary loading and backlog-aware evaluation to `Vesper/karma_regent.py`.
- Update gap-map row status and summary totals atomically.

Exit criteria:
- A gap enters the loop, becomes one diff, one test, one promotion, and one gap-map update.

## Phase 1: Persistent Memory and Persona

Goal: preserve identity across sessions without depending on wrapper state.

Files:
- `Vesper/karma_regent.py`
- `Scripts/karma_persistent.py`
- `docs/claude-mem-docs/CLAUDE.md` as a behavioral reference

Work:
- Keep a canonical session/history store.
- Inject concise state and memory summaries into prompts, not full raw logs.
- Add privacy-tag or equivalent redaction before persistence.
- Make session start, tool use, and session end explicit events.
- Persist enough state to recover after restart without cold-start amnesia.

Exit criteria:
- Restarting the harness does not destroy context, identity, or operating state.

## Phase 2: Merged Workspace Hardening

Goal: harden the already-existing merged workspace so browser and Electron behave as one continual session with integrated control, code, and cowork flows.

Files:
- `frontend/src/`
- `hub-bridge/app/proxy.js`
- `electron/main.js`
- `preload.js`
- `Karma2/map/preclaw1-gap-map.md`

Work:
- Add slash commands.
- Add settings and session history surfaces.
- Add cost and health indicators.
- Add permission prompts for dangerous operations.
- Add diff and git surfaces.
- Add agent/task visibility.

Exit criteria:
- The user can drive the system from browser or Electron as one continual workspace without fragmented tabs or split continuity.

## Phase 3: Retrieval and Planning

Goal: make memory search and task planning explicit, bounded, and token-efficient.

Files:
- `Karma2/primitives/INDEX.md`
- `Karma2/cc-scope-index.md`
- `docs/claude-mem-docs/README.md`
- `docs/claude-mem-docs/package.json`

Work:
- Add search-first memory retrieval behavior.
- Add a planning skill and an execution skill boundary.
- Add token-budget and context-budget visibility.
- Add retrieval-driven task decomposition.
- Keep context small enough that prompt caching remains useful.

Exit criteria:
- Planning and retrieval work as a deliberate system, not as incidental chat behavior.

## Phase 4: Extensibility

Goal: add plugins and skills without hard-wiring every future capability.

Files:
- `plugins/`
- `skills/`
- `docs/anthropic-docs/inventory.md`

Work:
- Add plugin loading and trust boundaries.
- Add skill discovery and packaging.
- Add MCP and remote tool expansion points.
- Keep extension hooks explicit and reviewable.

Exit criteria:
- New capabilities can be installed without rewriting the core harness.

## Phase 5: Multi-Surface Transport

Goal: unify the control plane across desktop, web, IDE, and browser surfaces.

Files:
- `hub-bridge/app/proxy.js`
- `frontend/src/`
- `electron/main.js`
- `preload.js`
- `docs/anthropic-docs/inventory.md`

Work:
- Unify Chat + Cowork + Code into one coordinated surface.
- Add transport fallback and retry discipline.
- Align desktop, web, IDE, and Chrome routing.
- Keep transport concerns below the UI layer.

Exit criteria:
- The harness presents as one system, not as a wrapper with disconnected modes.

## Phase 6: Self-Improvement Loop

Goal: turn observation into verified progress.

Files:
- `Vesper/vesper_watchdog.py`
- `Scripts/vesper_eval.py`
- `Scripts/vesper_governor.py`
- `Vesper/karma_regent.py`
- `Karma2/map/preclaw1-gap-map.md`

Work:
- Rank gap candidates from the gap map.
- Gate candidates on real diffs and real tests.
- Smoke-test applied changes before marking them done.
- Record gap closures in the gap map with evidence.
- Track backlog reduction as a measurable signal.

Exit criteria:
- The pipeline can close a gap without manual repair after every step.

## Phase 7: Voice and Presence

Goal: add richer interaction modes only after the core loop is stable.

Files:
- `frontend/src/`
- `electron/main.js`
- `preload.js`
- `docs/anthropic-docs/inventory.md`

Work:
- Add voice mode.
- Add presence indicators.
- Add optional camera/video only if the core state and control plane are stable.

Exit criteria:
- Voice and presence are additive, not destabilizing.

## Phase 8: Hardening and Drift Control

Goal: keep the plan honest after shipping starts.

Files:
- `.gsd/STATE.md`
- `.gsd/ROADMAP.md`
- `.gsd/codex-cascade-audit.md`
- `docs/claude-mem-docs/CHANGELOG.md`

Work:
- Keep state files evidence-based.
- Sync roadmap with shipped work.
- Record release-note style provenance.
- Prevent dead plan drift.

Exit criteria:
- The system can describe its state without inventing it.

## Exact Edit Order

1. `Scripts/karma_persistent.py`
2. `Scripts/vesper_eval.py`
3. `Scripts/vesper_governor.py`
4. `Vesper/vesper_watchdog.py`
5. `Vesper/karma_regent.py`
6. `Karma2/map/preclaw1-gap-map.md`
7. `frontend/src/`
8. `hub-bridge/app/proxy.js`
9. `electron/main.js`
10. `preload.js`
11. `Karma2/primitives/INDEX.md`
12. `Karma2/cc-scope-index.md`
13. `plugins/`
14. `skills/`
15. `docs/claude-mem-docs/CLAUDE.md`
16. `docs/claude-mem-docs/README.md`
17. `.gsd/STATE.md`
18. `.gsd/ROADMAP.md`

## Operational Rules

- Never advance a candidate to promotion without a diff and a test.
- Never update the gap map without a smoke-tested apply.
- Never let two writers modify the same gap-map row without locking.
- Never expand UI before the core loop is verified.
- Never claim completion from docs alone.

## Success Definition

The plan succeeds when:
- the executor closes gaps autonomously
- memory survives restarts
- the user gets one coherent control surface
- extensions can be added cleanly
- the gap map shrinks with evidence
- the system remains honest about what is verified

## Work Queue

### P0

#### `Scripts/karma_persistent.py`
- Goal: accept `gap_closure` work and route it to a structured task runner.
- Acceptance:
  - `gap_closure` is recognized as actionable.
  - bus messages are not marked handled on a failed CC resume without retry policy.
  - gap tasks produce structured output, not prose only.

#### `Scripts/vesper_eval.py`
- Goal: reject any candidate that lacks a diff or test.
- Acceptance:
  - no `target_files` means reject.
  - no `test_command` means reject.
  - no real diff means reject.
  - evaluation output records the rejection reason.

#### `Scripts/vesper_governor.py`
- Goal: apply only smoke-tested promotions and update the gap map atomically.
- Acceptance:
  - smoke test runs before apply is finalized.
  - failed smoke test prevents gap-map update.
  - gap-map row and summary counts update in one lock-protected operation.

#### `Karma2/map/preclaw1-gap-map.md`
- Goal: become the authoritative closure ledger.
- Acceptance:
  - row status changes reflect real closure.
  - summary totals remain consistent.
  - evidence is recorded with the closure.

### P1

#### `Vesper/vesper_watchdog.py`
- Goal: rank missing gaps and emit structured candidates.
- Acceptance:
  - parser reads the gap map without corruption.
  - ranking prioritizes the highest-value missing items.
  - output is deterministic for the same map state.

#### `Vesper/karma_regent.py`
- Goal: carry backlog awareness and persistent identity into every turn.
- Acceptance:
  - prompt includes a concise backlog summary.
  - self-evaluation can detect backlog reduction.
  - restart does not lose the current goal or session state.

#### `frontend/src/`
- Goal: expose session, settings, cost, permissions, and diff surfaces.
- Acceptance:
  - slash commands open a picker.
  - settings page exists.
  - session history is visible.
  - cost and permission state are visible.
  - diffs can be viewed before apply.

#### `hub-bridge/app/proxy.js`
- Goal: unify transport and expose the combined surface.
- Acceptance:
  - chat/cowork/code paths share one routing model.
  - transport failures fall back cleanly.
  - bus and dedup behavior remain stable.

### P2

#### `electron/main.js` and `preload.js`
- Goal: support the unified surface without extra wrapper tabs.
- Acceptance:
  - IPC channels are explicit.
  - desktop app launches the unified experience.
  - no mode is isolated behind a dead tab.

#### `Karma2/primitives/INDEX.md` and `Karma2/cc-scope-index.md`
- Goal: make primitives and pitfalls searchable.
- Acceptance:
  - primitives are indexed by capability.
  - known pitfalls are mapped to mitigation rules.

#### `plugins/` and `skills/`
- Goal: add extensibility with trust boundaries.
- Acceptance:
  - plugin manifests are discoverable.
  - skill discovery works.
  - extension loading does not bypass approval.

#### `docs/claude-mem-docs/CLAUDE.md` and `docs/claude-mem-docs/README.md`
- Goal: use claude-mem patterns as the memory/control reference.
- Acceptance:
  - hook lifecycle is reflected in the harness design.
  - progressive disclosure retrieval is used as the memory model.
  - privacy tags or equivalent redaction are part of the plan.

#### `docs/anthropic-docs/inventory.md`
- Goal: keep the plan aligned with current Claude platform primitives.
- Acceptance:
  - model/effort/context primitives are reflected in the plan.
  - tool, session, permission, and plugin primitives are not omitted.

## Queue Rules

1. Clear every P0 item before shipping UI expansion.
2. Do not start P1 UI work until the executor loop is verified on real diffs and tests.
3. Do not start P2 extensibility until the memory and transport model is stable.
4. Every item needs a file target and an acceptance check.
5. Every acceptance check must be verifiable from runtime behavior or written artifacts.
