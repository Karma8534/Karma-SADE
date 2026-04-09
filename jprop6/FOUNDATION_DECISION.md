# FOUNDATION_DECISION

## 1) Actual Foundation (Decision)
The true foundation is not “more features.”
The true foundation is a **runtime truth + continuity + minimal harness** contract.

Mandatory foundation components:
1. Canonical runtime truth source with evidence timestamps.
2. Shared session continuity envelope usable by browser and Electron.
3. Explicit recovery behavior for session resume failures.
4. Binary proof gates that block phase advancement.
5. Honest harness surface that does not overclaim capabilities.

## 2) Minimal Viable Electron Harness (Decision)
Minimum required behavior:
1. Launches and targets `https://hub.arknexus.net`.
2. Uses secure preload (`contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`).
3. Exposes only minimal runtime/session IPC.
4. Stores session continuity envelope locally (read/write contract seam).
5. Handles hub load failure with explicit fallback page.

Out of scope for foundation harness:
1. Arbitrary shell exec.
2. Full code editing lifecycle.
3. Multi-agent orchestration UI.
4. “already complete workspace” claims.

## 3) Browser/Electron Shared Continuity Requirement
Shared minimum contract:
1. `schema_version`.
2. `written_at`.
3. `session_id`.
4. `workspace_id`.
5. `source` (`browser`|`electron`|`system`).
6. Optional `thread_id` and `last_surface_snapshot_at`.

Failure semantics:
1. Invalid envelope -> FAIL gate.
2. Missing required keys -> FAIL gate.
3. Schema drift -> rollback to previous valid envelope.

## 4) Minimal Runtime Contract (Decision)
`jprop6` runtime contract requires:
1. `/health` reachable.
2. `/v1/surface` reachable with expected keyset.
3. `/v1/spine` state explicitly tracked (healthy/unhealthy) with no hidden assumptions.
4. Runtime checks logged into proof artifacts.

## 5) Watcher/Governor Disposition (Decision)
Decision: **Demote watchers to advisory sensors until foundation gates are proven.**

Reason:
1. Existing docs show watcher/governor claims and residual blocker churn in the same canonical state file.
2. This indicates authority drift: watchers emit status but do not enforce binary completion truth.
3. A failed watcher as control should not gate phase progression.

Operational policy in `jprop6`:
1. Watchers may provide telemetry.
2. Watchers cannot close phases.
3. Only binary gate evidence in `PROOF.md` closes phases.

## 6) Agent/Orchestrator Utility Decision
Decision: retain `agent/orchestrator` as **internal implementation pattern only**, never product truth source.

Allowed:
1. Internal execution routing.
2. Eval/governor plumbing.

Forbidden:
1. Treating pattern presence as completion proof.
2. Treating architecture prose as runtime truth.

## 7) Single Source of Runtime Truth (Decision)
For `jprop6`, single source of runtime truth is:
1. Executed command evidence in `jprop6/artifacts`.
2. Binary gate outcomes in `EXECUTION_GATES.md` + `PROOF.md`.

Not accepted as runtime truth:
1. Status tables alone.
2. “shipped/live/done” prose without fresh command evidence.
