# CODEX MASTER FORENSIC BUILD PROMPT — NEXUS vFINAL++
# Owner: Colby (Sovereign)
# Target: Codex / ArchonPrime
# Repo: C:\Users\raest\Documents\Karma_SADE
# Date: 2026-04-05
# Mode: Forensic repair + contradiction purge + TDD lock + architecture deepening + live-state verification

You are operating in:
C:\Users\raest\Documents\Karma_SADE

- treat these two persisted artifacts as continuity anchors:
 - C:\Users\raest\Documents\Karma_SADE\MEMORY.md
 - C:\Users\raest\Documents\Karma_SADE\tmp\handoffs\handoff-20260405T135600Z.yaml

You are not here to align with plans.
You are not here to produce reassuring summaries.
You are here to make the Nexus actually work, with proof.

Your job is to:
- reverse-engineer current truth from repo + runtime
- identify and resolve contradictions in docs/state/history
- reproduce the real failing path
- write failing tests first
- implement the minimum correct fix
- deepen architecture only where testability or safety demands it
- prove the fix in live runtime
- continue until the system works or a real blocker remains

==================================================
0. PRIME DIRECTIVE
==================================================

Documentation is context only.
Documentation is NEVER proof.

You may not treat any document, state file, roadmap, appendix, milestone note, session log, commit message, or prior agent claim as evidence that something is:
- done
- complete
- passed
- verified
- working
- deployed
- fixed
- independent
- stable
- shipped

Every such claim must be re-proven from:
1. live runtime behavior
2. current source code
3. current config / env / process state
4. failing tests written or reproduced now
5. passing tests after the fix
6. live browser / Electron / process verification where applicable

If a doc says something is complete and you have not re-proven it now, mark it:
UNVERIFIED — DOC CLAIM ONLY

==================================================
1. AUTHORITY ORDER
==================================================

When sources conflict, obey this order:

1. LIVE RUNTIME PROOF
2. CURRENT SOURCE CODE
3. CURRENT CONFIG / ENV / PROCESS STATE
4. FRESH TEST OUTPUT FROM THIS SESSION
5. ACTIVE DOCS
6. HISTORICAL DOCS / STATUS SNAPSHOTS / SESSION LOGS
7. PRIOR AGENT CLAIMS

Rules:
- Runtime beats docs.
- Current source beats historical summaries.
- Fresh tests beat historical “PASS.”
- Historical “done” is a hypothesis, not a fact.
- A later appendix does not become truth unless runtime/source still agree.

==================================================
2. THE ACTUAL GOAL
==================================================

Build the Nexus harness so that:
- hub.arknexus.net and the Electron KARMA app on P1 are the same merged workspace
- the default mode is one continual workspace/session
- new thread is optional branching, not the default identity model
- the system exceeds the Codex + Claude Code floor
- persistent memory, persistent session continuity, self-editing, self-improvement, learning, crash recovery, and real tool use are baseline capabilities
- the harness remains functional when CC is unavailable by degrading through valid fallback paths
- the browser and Electron are not decorative shells around a broken substrate
- active docs match proven runtime truth after the work is complete

==================================================
3. LOCKED ARCHITECTURE TRUTH
==================================================

These are the locked truths unless runtime disproves them:

1. The browser Nexus and Electron KARMA already ARE the merged workspace.
2. The top-level product model is one unified brain in one merged workspace with one continual session by default.
3. The older agent/orchestrator split is INTERNAL ONLY.
4. Internal split logic is valid only for executor, gating, evaluation, governor, routing, and similar control flow.
5. CC --resume on P1 is the primary Julian inference path under Max.
6. Direct api.anthropic.com Console API calls are NOT the primary path and must not replace the Max CLI path.
7. Groq, K2, local Ollama, and OpenRouter are fallback/support paths, not the primary Julian identity path.
8. K2 exists to synthesize, stabilize, evaluate, consolidate, and extend continuity, not to replace Julian.
9. The harness is an extension of the brain/continuity substrate, not a decorative wrapper.
10. Continuity precedes decoration.
11. Core executor stability precedes UI growth.
12. One candidate = one diff = one test = one promotion = one gap-map update.
13. No diff = reject.
14. No real test = reject.
15. No live proof = not done.

==================================================
4. HOST MAP
==================================================

Always name the host before acting:

- P1 = Windows host, Electron, browser dev path, local Claude Max CLI path, cc_server_p1.py
- K2 = Ubuntu/WSL/Linux side, cortex, regent, kiki, vesper, synthesis/eval infrastructure
- vault-neo = deploy/runtime spine

Rules:
- Command availability is not host identity.
- Reachability is not ownership.
- PATH presence is not installation state.
- If WSL/Ubuntu is reachable from P1, treat it as K2 unless proven otherwise.

Before risky actions, restate:
- host
- exact file write set
- exact proof target
- why the action belongs to the current failing path

Risky actions include:
- auth commands
- scheduled task changes
- registry changes
- service/systemd changes
- deployment
- environment mutation
- secret-path changes
- host-boundary changes
- kill/restart actions
- self-edit application

==================================================
5. MANDATORY READ ORDER
==================================================

Read these first, in order:

1. docs/ForColby/nexus.md
2. .gsd/STATE.md
3. .gsd/codex-sovereign-directive.md
4. .gsd/codex-nexus-build-contract.md
5. .gsd/codex-cascade-audit.md
6. .gsd/codex-nexusplan.md
7. Karma2/cc-scope-index.md
8. docs/anthropic-docs/
9. docs/claude-mem-docs/
10. docs/wip/preclaw1/preclaw1/src/

Create or refresh:
.gsd/codex-execution-ledger.md

Ledger must include:
- timestamp
- host
- current step
- file write set
- proof target
- contradiction summary
- reproduced failure
- failing tests
- passing tests
- runtime proof
- blockers
- next proof command

==================================================
6. GRILL-ME PRIMITIVE — LOAD-BEARING
==================================================

Use the `grill-me` primitive exactly like this:

Interview relentlessly about every aspect of the problem UNTIL there is shared understanding,
BUT if a question can be answered by exploring the codebase, tests, logs, configs, or runtime,
explore the codebase instead of asking.

Walk down each branch of the design tree one by one.
Resolve dependencies in order.
Ask only high-leverage, numbered questions that materially change implementation or acceptance criteria.
Do not ask broad, lazy, or speculative questions.

Operational rule:
- codebase first
- runtime second
- ask last

If the repo can answer it, do not ask.

If the environment supports skills, use:
npx skills@latest add mattpocock/skills/grill-me
If not, emulate the primitive exactly.

==================================================
7. TDD PRIMITIVE — LOAD-BEARING
==================================================

Use strict Red → Green → Refactor.

RED
- Write a failing test for one concrete requirement.
- Prove failure now.

GREEN
- Write the minimum code to pass that test.
- Do not add unrelated cleanup in Green.

REFACTOR
- Improve structure, naming, and boundaries.
- Keep tests green.

REPEAT
- Continue until the reproduced failure is fixed and verified in runtime.

No fix is valid unless:
- the failure was reproduced first
- a failing test existed first
- the test passes after the fix
- relevant existing tests still pass
- live runtime behavior is verified

If the environment supports skills, use:
npx skills@latest add mattpocock/skills/tdd
If not, emulate the primitive exactly.

==================================================
8. ARCHITECTURE DEEPENING PRIMITIVE — LOAD-BEARING
==================================================

TDD only works if the architecture supports it.

Before architecture work, inspect the repo for these three failure patterns:

A. Understanding one concept requires jumping across many small files.
B. Pure functions were extracted for “testability,” but the real bug hides in how they are called or orchestrated.
C. Tightly coupled modules make changes risky.

When these patterns block reliable testing or safe fixes, find deepening opportunities:
- collapse shallow, scattered modules into deeper modules with cleaner interfaces
- move behavior closer to the seam where it is actually used
- reduce cross-file hopping for one concept
- do not create fake abstractions just to look “clean”

Architecture changes are allowed only when they improve:
- testability of the real behavior
- clarity of the real control surface
- safety of the current fix
- ability to verify end-to-end behavior

Do not refactor speculatively.
Do not reorganize unrelated code.
Do not do aesthetic cleanup first.

If the environment supports skills, use:
npx skills@latest add mattpocock/skills/improve-codebase-architecture
If not, emulate the primitive exactly.

==================================================
9. CONTRADICTION PURGE — REQUIRED FIRST
==================================================

Before implementation, build a CONTRADICTION MATRIX.

At minimum verify and resolve:
- old gap-map state vs later S160 state
- “Phase 0 next” vs “Phase 0-4 all shipped”
- “no UI before core executor stable” vs large UI/operator-surface completion claims
- “Electron is mostly shell” vs “Electron already has 13 IPC handlers, 12 independent”
- stale model/routing assumptions
- stale continuity claims
- any “done/passed/shipped/live” statements in docs that lack current proof

For each contradiction:
- claim A
- claim B
- source of each
- authority winner
- why it wins
- consequence for build order
- whether loser is stale, historical, or currently false

No coding begins until contradiction purge is complete.

==================================================
10. WHAT EXISTS — HYPOTHESIS TABLE, NOT TRUTH
==================================================

Treat these as hypotheses until proven:

A. Electron
- 13 IPC handlers exist
- 12 operate independently
- only cc-chat depends on CC --resume

B. cc_server_p1.py
- context assembly exists
- tool defs / tool execution / fallback pieces may exist
- streaming and session handling may already exist
- self-edit endpoints may already exist
- permission engine exists

C. hub-bridge / proxy
- routing, bus, SSE passthrough, K2 failover may already exist

D. executor path
- evaluator and governor exist
- watchdog exists but may be smaller than earlier plans assumed
- diff-less candidates may still be wrongly approved
- atomic gap-map update may still be missing or partial

E. continuity
- transcript storage, MEMORY.md, claude-mem, spine injection, and checkpoints may exist in partial form
- bundle history may overstate restart continuity

F. inference
- CC --resume primary under Max
- K2 and Groq as fallback/support
- OpenRouter as escape hatch

You must produce a VERIFIED CAPABILITIES TABLE:
- claimed capability
- current proof
- host
- file(s)
- runtime status
- VERIFIED / PARTIAL / FALSE / UNVERIFIED

==================================================
11. CRITICAL PATH — DO THIS ORDER
==================================================

You are not allowed to wander.

The critical path is:

STEP 0 — CONTRADICTION PURGE
Goal:
- reconcile bundle vs repo vs runtime
Done when:
- contradiction matrix exists
- stale claims are marked
- active truth is locked

STEP 1 — REPRODUCE THE SINGLE MOST LOAD-BEARING FAILURE
Choose the highest-value failing path from this set:
1. Browser harness cannot complete a real tool loop through the primary/fallback path
2. Electron harness cannot complete the same real tool loop
3. Session continuity fails across restart
4. Executor loop cannot close one real gap end-to-end
5. Browser/Electron are not truly one continual workspace/session

Pick the highest-value one based on runtime evidence, not docs.

Done when:
- reproduced with exact command/action + exact broken output/behavior

STEP 2 — WRITE FAILING TESTS
Required:
- characterization test for current broken behavior
- acceptance test for intended behavior
- integration/e2e test if orchestration/runtime bug

Done when:
- tests fail for the real reason

STEP 3 — FIX THE MINIMUM SURFACE
Allowed targets only:
- the exact broken path
- architecture deepening only if TDD or safety is blocked

Done when:
- minimum correct fix exists
- no unrelated scope drift

STEP 4 — PASS TESTS
Done when:
- changed tests pass
- relevant existing tests pass
- no diff-less or test-less path remains approved if executor path touched

STEP 5 — LIVE RUNTIME VERIFY
Must verify all relevant layers:
- source-level fix
- process-level state
- browser behavior if browser path affected
- Electron behavior if Electron path affected
- restart continuity if continuity was part of the bug
- fallback behavior if routing was part of the bug

STEP 6 — ONLY THEN MOVE TO NEXT LOAD-BEARING FAILURE
Repeat the loop until the full success floor is real.

==================================================
12. SPECIFIC LOAD-BEARING TARGETS
==================================================

These take precedence over everything else:

A. cc_server primary path
Must verify:
- CC --resume is still the primary path
- no paid direct Anthropic API replacement
- real tool loop exists or is completed
- session lock / stale-session handling works
- valid fallback cascade works when CC is unavailable

B. Electron cc-chat path
Must verify:
- Electron is not just a shell
- it can perform the same critical task path as browser
- tool loop and fallback work if this path depends on them

C. canonical continuity substrate
Must verify:
- transcript reload
- current session persistence
- MEMORY.md / claude-mem / spine / checkpoint contribution
- browser and Electron share one continual session model rather than split continuity

D. core executor
Must verify:
- one candidate
- one diff
- one test
- one promotion
- one atomic gap-map update
- no no-diff / no-test false approval

E. merged workspace hardening
Only after A–D are real.
Must verify:
- cowork/code/permissions/diff surfaces operate on the already-existing merged workspace
- no wrapper-fragmented workflow remains

==================================================
13. EXPLICITLY DEFERRED UNTIL CORE IS REAL
==================================================

Do NOT prioritize these unless the reproduced bug proves they are load-bearing:

- inbox PDF conversion
- Chrome extension growth
- voice/presence expansion
- IDE/Chrome/remote transport growth
- plugin breadth
- aesthetic UI work
- historical backlog cleanup
- low-severity known-issue cleanup
- tabled side quests
- feature-count growth

Known deferred items:
- corpus_cc.jsonl
- P0-G dead code cleanup
- PROOF-A pending work
- low-severity UI/status cleanups
- vestigial tier/mode cleanup
- cascade dot cosmetics

==================================================
14. DOC CLAIM POLICY
==================================================

For every statement found in docs like:
- already working
- verified
- complete
- shipped
- live
- resolved
- done when
- fixed

Apply this policy:

IF live proof exists now:
- mark VERIFIED
- cite the proof you just ran

ELSE:
- mark UNVERIFIED — DOC CLAIM ONLY
- do not inherit it into planning
- do not optimize around it
- do not use it to skip testing

==================================================
15. LIVE-STATE CHECKPOINTS
==================================================

At session start:
- read docs for context only
- build contradiction matrix
- create verification ledger
- choose highest-value failing path

Every 10 minutes OR before risky actions:
- re-check live process state
- re-check branch/file state
- re-check whether current work still maps to the reproduced failure
- re-check for drift into doc-driven or feature-driven work

If drift detected:
- stop
- log drift cause
- restate current failing path
- continue only after alignment restored

==================================================
16. REQUIRED PROOF TYPES
==================================================

Only these count:
- pytest / test runner output
- npm run build / node --check output
- curl / Invoke-RestMethod output
- process lists / health checks
- file existence / content checks
- browser smoke behavior
- Electron smoke behavior
- restart / recovery proof
- fallback-path proof

Not proof:
- comments
- plans
- roadmaps
- state files
- appendices
- milestone prose
- commit messages
- agent summaries

==================================================
17. ANTI-FAILURE RULES
==================================================

- Do not confuse scaffold with capability.
- Do not confuse routed-to-CC features with independence.
- Do not rewrite working systems without proof they are the blocker.
- Do not ask questions the repo/runtime can answer.
- Do not do architecture work before reproducing the failure.
- Do not count progress without diff + test + runtime proof.
- Do not declare PASS from docs.
- Do not trust stale snapshots.
- Do not replace CC --resume with paid API calls.
- Do not do UI-first work.
- Do not stop on milestone prose.
- Do not let feature count stand in for correctness.
- Do not let diff-less candidates reach promotion.
- Do not let no-test candidates reach promotion.
- Do not let summary text satisfy completion.
- Do not update docs first.

==================================================
18. WHAT “DONE” ACTUALLY MEANS
==================================================

The Nexus is not done until:
- browser works on the real critical path
- Electron works on the same real critical path
- continuity survives restart if continuity was in scope
- tool use works if tool loop was in scope
- fallback works if routing was in scope
- executor closes one real gap if executor was in scope
- browser/Electron act as one continual merged workspace if that was the failing path
- docs/contracts are updated only after code + tests + runtime proof agree

==================================================
19. OUTPUT FORMAT — EVERY STEP
==================================================

For every step, output exactly:

1. CURRENT STEP
- host
- file write set
- proof target

2. CONTRADICTION MATRIX
- conflict
- source A
- source B
- winner
- why

3. VERIFIED CAPABILITIES TABLE
- capability
- claimed by
- proof
- status

4. REPRODUCED FAILURE
- exact command/action
- exact output/behavior
- exact broken requirement

5. TEST PLAN
- characterization test
- acceptance test
- integration/e2e test if needed
- why each exists

6. ARCHITECTURE FINDINGS
- shallow/scattered concept?
- fake pure-function seam?
- tight coupling?
- deepening opportunity?
- what will NOT be changed?

7. TDD LOOP
- RED: failing test + output
- GREEN: minimal fix
- REFACTOR: cleanup
- RESULT: passing output

8. LIVE VERIFICATION
- source-level proof
- process-level proof
- browser proof
- Electron proof
- restart proof if relevant
- fallback proof if relevant

9. DOC UPDATE ELIGIBILITY
- docs may be updated: YES/NO
- why

10. PROOF PACK
- files changed
- tests passed
- commands run
- runtime proof
- remaining risks
- exact verdict: VERIFIED WORKING / NOT YET VERIFIED

11. NEXT LOCKED STEP
- next step
- host
- file write set
- proof target

IMPORTANT:
If work remains, do not end with a victory summary.
End with the next concrete action to avoid false stop.

==================================================
20. STOP CONDITIONS
==================================================

Do not stop because:
- docs say it is done
- old work said it passed
- code compiles
- one endpoint returns 200
- one test passed while runtime is unverified
- UI looks improved
- a summary sounds convincing
- a large amount of work was completed

Stop only when:
- the reproduced failure is fixed
- tests prove it
- live system state proves it
- restart/persistence/fallback are verified if they were part of the bug

If blocked, output:
- blocker
- why it blocks proof
- exact minimal missing information needed
- affected host
- affected step
- affected file set

==================================================
20A. HARD GATE CLOSURE RULE
==================================================

Every gate is binary:
- DONE
- NOT DONE

Forbidden phrases:
- complete enough
- good enough
- sufficient to proceed
- enough signal to move on

Rules:
- A mandatory read gate is NOT complete until every required file/reference in the gate has been read as required.
- Inventories, file counts, or sampled references do NOT close a mandatory read gate unless the gate explicitly asked only for inventory or sampling.
- Early contradictions do NOT authorize advancing to the next phase.
- Insight does NOT close a gate.
- Before announcing a phase transition, output the current gate closure item-by-item and show that every required item is DONE.
- If even one required item is incomplete, say: `GATE NOT COMPLETE` and continue the current gate.

==================================================
20B. CORE FACT CORRECTION RULES
==================================================

If a correction concerns a load-bearing runtime fact such as:
- service endpoint
- port
- host
- auth path
- primary inference path
- memory substrate

then:
- prove it in current code
- prove it in live runtime
- update every relevant text file that still asserts the old fact
- classify any remaining binary/generated residue explicitly
- do not say the correction is complete until the remaining residue set is either fixed or explicitly blocked

Additional anti-drift rules:
- Do not normalize from memory. Normalize from live proof.
- Do not preserve corrected falsehoods in ledgers, status files, or summaries.
- Do not treat mitigation as resolution when the blocker belongs to the user or OS.
- If the user said they will resolve blockers, stop and hand them the exact action instead of side-stepping it.
- When asked to fix "all files", that means tracked + untracked relevant text files, not just active docs.
- For endpoint cleanup, prefer semantic endpoint scans over raw numeric scans.

==================================================
21. FIRST ACTIONS
==================================================

Begin now:

1. Read required files in order.
2. Build the CONTRADICTION MATRIX.
3. Create the VERIFIED CAPABILITIES TABLE.
4. Mark every unproven “done/passed/complete/live” doc claim as UNVERIFIED — DOC CLAIM ONLY.
5. Choose the single highest-value failing path from runtime evidence.
6. Reproduce it.
7. Write the first failing test.
8. Start Red → Green → Refactor.
9. Verify live system state before claiming anything.

Start with:
- CURRENT STEP
- CONTRADICTION MATRIX
- VERIFIED CAPABILITIES TABLE
- REPRODUCED FAILURE
- first RED test
