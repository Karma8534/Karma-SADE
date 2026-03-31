#In CC Paste this#

You are now operating in LOCKED FORENSIC EXECUTION MODE for The Nexus / Karma project.

Mission:
Take the attached/current Nexus plan as INPUT, not truth. Forensically audit it against the actual repo, actual runtime behavior, actual CLI capability, and actual deployed system state. Then harden the plan, close every blocker/gap/missed item, implement the required fixes, and retro-verify all completed work until the system is genuinely working end-to-end.

Primary rule:
Do not treat any claim in the plan as “done” unless you re-prove it yourself from code, runtime behavior, logs, tests, or live endpoint checks.

Non-negotiable operating rules:
1. Best-path only. No menus. No “could/might/maybe” unless an item is truly unknown.
2. Do not stop at analysis. Continue through audit → correction → implementation → verification.
3. Do not ask for confirmation unless blocked by one of these only:
   - irreversible/destructive action
   - credentials/secrets not present
   - legal/contract acceptance
   - admin elevation that must be performed by Colby
4. If blocked by one of those, do not stop vaguely. Emit:
   - exact blocker
   - exact reason
   - exact command/action Colby must perform
   - exact point where you will resume
5. No placeholders, no pseudo-completion, no “should work.”
6. Every claim must be backed by evidence.
7. Every change must be verifier-gated.
8. Use TDD-first: RED → GREEN → REFACTOR.
9. Use Context7 before framework/library-specific changes.
10. Preserve merge-first language. Outputs are merge artifacts / proof packs / snapshots.

Your job has 4 layers:
LAYER A — FORENSIC TRUTH PASS
LAYER B — PLAN HARDENING
LAYER C — IMPLEMENTATION
LAYER D — RETROACTIVE RE-VERIFICATION OF ALL SPRINTS

==================================================
LAYER A — FORENSIC TRUTH PASS
==================================================

First, build a truth ledger before editing anything.

A1. Read all relevant project artifacts, including but not limited to:
- the attached/current Nexus plan
- any mirrored PLAN.md files
- MEMORY.md
- CLAUDE.md
- proxy.js
- cc_server_p1.py
- unified.html
- agora.html
- Electron files (main.js, preload.js, package config)
- hooks/loggers including cc-chat-logger.py
- any files related to ambient capture, ledger writes, shared awareness, Vesper/regent, routing, deploy, restart, or failover

A2. Produce a truth table with 4 states only:
- VERIFIED_TRUE
- VERIFIED_FALSE
- INFERRED_ONLY
- NOT_YET_TESTED

A3. Re-evaluate every claimed “DONE / LIVE / PROVEN / VERIFIED / AVAILABLE / RUNNING” item against actual evidence.

A4. Re-evaluate every baseline item the same way.

A5. Re-evaluate every “resolved” forensic item the same way.

A6. Explicitly identify:
- false positives
- inferred-but-not-proven items
- missing dependencies
- mismatched paths
- broken assumptions
- stale plan claims
- implementation drift
- architecture drift
- runtime drift
- doc drift

A7. Build an “Assumption Ledger” containing every assumption the plan currently makes that must be proven before code can safely rely on it.

Minimum assumptions to verify explicitly:
- exact Claude Code CLI flags actually supported in current environment
- exact stream-json output schema actually emitted
- whether --verbose is required in current CLI/runtime
- whether attachments/files are accepted the way the plan assumes
- whether effort/model/budget flags actually exist and behave as assumed
- whether POST streaming from browser is implemented via fetch readable stream, SSE, or another viable method
- whether cancel can target the correct process safely under concurrency
- whether tool output includes structures that can leak secrets
- whether shared log/JSONL writes are concurrency-safe
- whether reboot persistence path is correct on P1 and/or K2
- whether Electron IPC bridge is actually wired end-to-end
- whether cc-chat-logger.py really writes Code tab conversations into nexus-chat.jsonl

Do not skip this layer.

==================================================
LAYER B — PLAN HARDENING
==================================================

After the truth pass, rewrite the plan into a hardened execution plan.

You must preserve the valid parts of the current plan, including its sprint structure where correct, but you must repair all weak points.

Mandatory hardening corrections:
1. Replace all subjective acceptance criteria with measurable ones.
   Example:
   - “Opus-quality at $0” is not sufficient by itself.
   Replace with measurable latency, correctness, routing, fallbacks, and cost accounting gates.

2. Treat all CLI capabilities as unknown until proven from:
   - `claude --help`
   - direct probe commands
   - observed runtime behavior
   Never hardcode flags because the plan assumes they exist.

3. Correct browser streaming architecture:
   - Do not assume EventSource for POST bodies.
   - Prefer the transport that is actually compatible with the existing architecture and the verified browser/server behavior.
   - If resumable streaming is claimed, require event ids + replay buffer + tested reconnect semantics before allowing that claim.

4. Correct cancel architecture:
   - No global single-PID cancel.
   - Use request_id-scoped process registry.
   - Ensure correct subprocess-tree termination.
   - Prevent cancelling the wrong request under concurrency.
   - Add cleanup on disconnect, timeout, and completion.

5. Correct upload/attachment architecture:
   - verify actual CLI/file ingestion path first
   - enforce MIME/type allowlist
   - enforce file size caps
   - use secure temp file lifecycle + cleanup
   - prevent path traversal
   - avoid unnecessary base64 bloat if a better verified path exists
   - checksum and log upload metadata safely

6. Add security hardening missing from the plan:
   - authn/authz requirements for new endpoints
   - CSRF / same-origin considerations where relevant
   - rate limits / abuse controls
   - redaction of secrets from tool results, file previews, logs, and UI panels
   - safe handling of env vars, tokens, bearer strings, credentials, and local paths

7. Add observability hardening missing from the plan:
   - per-request ids
   - structured logs
   - latency metrics
   - stream failure classification
   - cancel metrics
   - upload metrics
   - proof-pack artifact locations

8. Add rollback/recovery requirements:
   - snapshot or restore point before risky changes
   - rollback commands
   - deploy/restart verification steps
   - post-reboot proof
   - failure-mode drills

9. Add concurrency hardening:
   - simultaneous chat requests
   - cancel during stream
   - disconnect during stream
   - multi-tab/browser behavior
   - shared file write contention
   - repeated restart handling

10. Add parser hardening:
   - golden sample fixtures for real stream-json outputs
   - parser tests for text/tool_use/tool_result/error/partial cases
   - malformed line handling
   - truncated stream handling
   - unknown content block handling

11. Add data hygiene:
   - sanitize rendered tool/file output
   - bounded memory growth in UI
   - truncation strategy for huge tool results
   - no accidental rendering of secrets or full binary blobs

12. Add deployment hardening:
   - exact service/process ownership
   - restart path
   - health checks
   - smoke tests after deploy
   - proof that hub.arknexus.net still works publicly after changes

13. Preserve these plan truths unless disproven:
   - K2 must not use claude CLI if plan/rules say cascade-only
   - unified.html must not reimplement Claude Code features in JS
   - every UI-facing behavior must have terminal/probe verification before browser polish

Output a corrected HARDENED PLAN that includes:
- updated gap list
- corrected sprint order if needed
- dependency graph
- measurable acceptance criteria
- test plan
- rollback plan
- external blocker list
- proof-pack format

==================================================
LAYER C — IMPLEMENTATION
==================================================

Then execute the hardened plan.

Execution protocol:
1. Start with the highest-value blocking sprint.
2. For each gap:
   a. Write/adjust failing tests or probe scripts first
   b. Run them and capture RED evidence
   c. Implement the fix
   d. Run GREEN evidence
   e. Refactor carefully
   f. Re-run the full relevant suite
   g. Capture proof

3. After each gap, update:
   - hardened plan status
   - assumption ledger
   - baseline matrix
   - proof pack

4. After each sprint:
   - run sprint-local smoke tests
   - run impacted prior-sprint tests again
   - verify no regressions
   - update live status only if re-proven

5. If a plan item proves wrong:
   - do not force the old plan through
   - replace it with the best verified design
   - document the correction
   - continue

6. If a claimed CLI flag/feature is unsupported:
   - do not fake it
   - derive the correct supported equivalent
   - update code/tests/plan accordingly
   - continue

==================================================
LAYER D — RETROACTIVE RE-VERIFICATION
==================================================

This is mandatory.

After finishing each sprint, recursively re-verify all prior “done” work back through Sprint 1.

That means:
- no later sprint can stand on an earlier sprint that is only assumed
- no “completed” sprint remains completed if later evidence breaks it
- if a later sprint exposes a flaw in an earlier sprint, reopen that earlier sprint immediately
- continue until all completed sprints remain green under current reality

Required recursive loop:
1. finish current sprint
2. run current sprint verification
3. run previous sprint verification
4. run Sprint 1 verification
5. run baseline subset affected by all completed sprints
6. if any fail, reopen earliest broken sprint first
7. continue until all completed sprints are green simultaneously

==================================================
REQUIRED DELIVERABLE FORMAT
==================================================

At meaningful checkpoints, emit exactly these sections:

1. FORENSIC FINDINGS
- false claims
- inferred claims
- missing blockers
- newly discovered gaps
- architecture corrections

2. HARDENED PLAN
- updated gap inventory
- sprint order
- dependencies
- acceptance criteria
- rollback strategy

3. EXECUTION LOG
- files changed
- commands run
- tests added/changed
- services restarted
- deploy actions

4. PROOF PACK
- RED evidence
- GREEN evidence
- smoke results
- latency numbers
- screenshots/log snippets if available
- commit ids if applicable

5. BASELINE MATRIX
For each baseline item:
- VERIFIED_PASS
- VERIFIED_FAIL
- BLOCKED_EXTERNAL
- NOT_STARTED

6. NEXT BLOCKER
Only if truly blocked by an external dependency.
Include exact human action required.

==================================================
STOP CONDITION
==================================================

Do not stop because the repo “looks good.”
Do not stop because some tests pass.
Do not stop because the plan was updated.
Do not stop because one sprint is green.

Stop only when every non-deferred baseline item is in exactly one of these states:
- VERIFIED_PASS, with evidence
or
- BLOCKED_EXTERNAL, with exact blocker, exact reason, and exact next human action

“DEFERRED” items may remain deferred only if they are explicitly marked deferred by the plan and are not prerequisites for any non-deferred item.

==================================================
PRIORITY ORDER IF YOU NEED TO CHOOSE
==================================================

Default priority unless live evidence forces reorder:
1. Truth pass / assumption ledger
2. Streaming transport correctness
3. Rich output parser correctness + safe rendering
4. Request-scoped cancel correctness
5. File/image input correctness + security
6. CLI capability mapping based on proven flags only
7. Electron IPC end-to-end correctness
8. Evolution feedback loop correctness
9. Reboot survival / restart persistence
10. Full recursive baseline verification

==================================================
FINAL INSTRUCTION
==================================================

Begin now.
Do the forensic truth pass first.
Then harden the plan.
Then implement.
Then recursively re-verify all completed sprints back to Sprint 1.
Do not leave wiggle room for unstated assumptions, inferred completions, fake-green states, or partial verification.