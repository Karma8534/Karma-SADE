# Codex Cascade Audit

Date: 2026-04-05

This audit is based on:
- `docs/ForColby/nexus.md` v5.1.0
- `Karma2/map/preclaw1-gap-map.md`
- `.gsd/phase-cascade-pipeline-PLAN.md`
- `docs/anthropic-docs/*`
- Full source of the six files below

Correction note for current use:
- Canonical plan is now `docs/ForColby/nexus.md` v5.5.0.
- Appendix S161 supersedes any reading that treats the merged workspace as a later "operator surface" deliverable.
- Use this audit for insertion points and failure modes, not for older surface-ordering assumptions.

Plan drift found during the read:
- `Vesper/vesper_watchdog.py` is 126 lines, not a ~272-line file with candidate extraction hooks.
- `Scripts/vesper_governor.py` has no `apply_promotion()` function. The real apply path is `_apply_to_spine()` plus the `run_governor()` loop.
- `Scripts/vesper_eval.py` already has a fast-path approval branch that will misclassify any candidate that arrives without a real diff or test command.

## [Scripts/karma_persistent.py](C:/Users/raest/Documents/Karma_SADE/Scripts/karma_persistent.py#L1)

| Anchor | Exact insertion point | Existing conflicts | Missing imports / helpers | Failure modes |
|---|---|---|---|---|
| `# What Karma acts on` at lines 51-54 | Insert the gap-closure allowlist here, before `ACTIONABLE_TYPES` is consumed by `poll_and_act()` | `ACTIONABLE_TYPES` only allows `task`, `directive`, `question`; `IGNORE_SENDERS` blocks `vesper` and `kiki`, so a `gap_closure` directive from either source will be dropped before execution | None for plain type edits; if you add file locking for the watermark/session files, this file currently has no `msvcrt` or equivalent lock path | If `CC --resume` is busy or returns non-zero, `run_cc_task()` returns `None` and `poll_and_act()` still marks the bus message handled, so the task is lost |
| After `build_karma_context()` at line 153 or before `run_cc_task()` at line 193 | Add `build_gap_closure_context()`, `run_gap_closure_task()`, and `post_gap_result()` here; this is the cleanest local helper boundary | `run_cc_task()` already mixes routing, session resume, subprocess launch, and JSON parsing. If you put gap orchestration inside it, you will blur the existing CC resume path and lose the ability to distinguish “general task” from “structured gap closure” | Likely `re` or `typing` if you parse structured output; `msvcrt` if you add a Windows lock around `.karma_persistent_session_id` or `.karma_persistent_watermark.json` | Two concurrent cycles can both read the same pending bus entries before `handled_ids` is saved, so the same gap can be executed twice. `MAX_CC_TIMEOUT=180` also hard-kills long runs without a retry queue |

Notes:
- The current loop posts success/failure to the bus, but it never retries a failed CC resume.
- `poll_and_act()` only processes the first two actionable messages per cycle, so a gap queue can starve behind unrelated directives unless you prioritize `gap_closure`.

## [Vesper/vesper_watchdog.py](C:/Users/raest/Documents/Karma_SADE/Vesper/vesper_watchdog.py#L1)

| Anchor | Exact insertion point | Existing conflicts | Missing imports / helpers | Failure modes |
|---|---|---|---|---|
| End of `update_spine()` at line 114, before `if __name__ == "__main__"` at line 117 | Insert `parse_gap_map()`, `rank_missing_gaps()`, and `extract_gapmap_candidates()` here | This file only writes `vesper_brief.md` and `vesper_identity_spine.json`. There is no existing candidate emission, queue writer, or artifact directory to reuse | `re` for markdown parsing; `msvcrt` or another lock helper if you want atomic writes on Windows; possibly `typing` for structured returns | If two watchdog cycles overlap, one can overwrite the spine or brief while the other is reading, because both writes are unlocked and uncoordinated. There is no CC path here, so a busy `CC --resume` is not handled at all |

Notes:
- The plan’s “candidate extraction hooks” assumption is stale. No such hooks exist in this file.
- If you add gap-map emission here, also add a real output path and a lock strategy; otherwise the watchdog will only observe and overwrite.

## [Scripts/vesper_eval.py](C:/Users/raest/Documents/Karma_SADE/Scripts/vesper_eval.py#L1)

| Anchor | Exact insertion point | Existing conflicts | Missing imports / helpers | Failure modes |
|---|---|---|---|---|
| Start of `run_eval()` loop at line 171, immediately after `candidate = pipeline.read_json(path, {})` and before `ctype = candidate.get("type", "")` | Insert a hard gate here: reject candidates with no `target_files`, no `test_command`, or no real diff before any heuristic/model scoring | `is_observational = candidate.get("proposed_change") is None` will treat diff-less gap candidates as observational and feed them into the existing approval logic. The `AWARENESS_TYPES` fast path can also approve confidence-only artifacts with no executable change | `re` if you need to parse diff text or patch hunks; `subprocess` is already imported later in the file for the quality-score hook, but a dedicated test runner helper should import it near the top for clarity | If the gate is added too late, the file will still generate eval/promotions for no-op candidates. If `CC --resume` is busy upstream, this file does not call CC directly, so the more likely failure is stale approval from heuristic/model scoring instead of a retry |
| Between `_check_regression()` and `run_eval()` at line 159 | Add `evaluate_gap_candidate()`, `run_candidate_test()`, and `candidate_has_real_diff()` here if you want helpers rather than inline checks | `run_eval()` currently owns the entire decision loop. Adding helper functions elsewhere is fine, but they must be called before the `AWARENESS_TYPES` branch and before `model_weight` is computed | `Path` is already imported; no new path helper needed | Two eval cycles can race on the same candidate file because the list/rewrite/update flow has no lock. A second runner can read a file before the first one writes the approved/rejected status |

Notes:
- The current file already writes promotion artifacts and updates candidate status. If you leave the fast-path branch unchanged, a gap candidate can be “approved” without any code delta.
- The final `karma_quality_score.py` subprocess is unrelated to gap closure and should not be treated as proof.

## [Scripts/vesper_governor.py](C:/Users/raest/Documents/Karma_SADE/Scripts/vesper_governor.py#L1)

| Anchor | Exact insertion point | Existing conflicts | Missing imports / helpers | Failure modes |
|---|---|---|---|---|
| After `_apply_to_spine()` at line 465 and before `_update_state()` at line 567 | Insert `apply_gap_patch()`, `smoke_test_gap()`, and `update_gap_map_status()` here; this is the only place where promotion application is already centralized | There is no `apply_promotion()` function to extend. The real apply path is `_apply_to_spine()` plus the `if applied_ok:` block in `run_governor()` | `re` for markdown row replacement; `msvcrt` or another lock helper if you want atomic edits to `preclaw1-gap-map.md`; possibly `contextlib` for safe rollback wrappers | If tests fail and you do not rollback before writing `done_dir`, the promotion can be marked handled while the gap map still says MISSING. If `CC --resume` is busy upstream, this file is unaffected directly, but stale promotions can still be applied later because there is no executor backpressure |
| In the `if applied_ok:` branch of `run_governor()` at lines 735-752 | Call `smoke_test_gap()` before the promotion is committed to `done_dir`; call `update_gap_map_status()` only after smoke success | The current branch marks the promotion applied, writes it to `regent_promotions_applied`, and unlinks the pending file. There is no smoke gate and no rollback hook | No new import is required for simple function calls; if the smoke gate shells out, `subprocess` is already available | Two concurrent governor cycles can both see the same `promotion-*.json` file, both attempt apply, and both race on unlink/write. The gap map update will also race unless you add a lock around the markdown file |

Notes:
- `SAFE_TARGETS` is already restrictive. If the new patch target is not one of those values, the governor will skip it before any smoke test can run.
- `_read_total_promotions()` counts applied artifacts, not feature closures, so it cannot be used as a gap-map truth source.

## [Vesper/karma_regent.py](C:/Users/raest/Documents/Karma_SADE/Vesper/karma_regent.py#L1)

| Anchor | Exact insertion point | Existing conflicts | Missing imports / helpers | Failure modes |
|---|---|---|---|---|
| After `load_vesper_brief()` at line 302 or near `_current_goal` at line 299 | Add `load_gap_brief()` / `load_gap_backlog_summary()` here so the gap queue can be cached separately from the session brief | `get_system_prompt()` already combines persona, invariants, brief, and memory. If you jam the full gap map into that chain, you will bloat every model call and weaken the caching benefit in `call_claude()` | `re` for parsing the markdown gap map; `msvcrt` or another lock helper if the summary is derived from a file that another process rewrites | Concurrent writers can race on cached gap summary state if you store it globally. This file already maintains several global counters, so adding another one without a lock will make the prompt nondeterministic |
| Inside `get_system_prompt()` at lines 405-420, just before `return base` | Inject the concise gap backlog summary here, after `memory_ctx` and before the function returns | `get_system_prompt()` feeds both local-first inference and Claude fallback. Any verbose backlog injection will hit every turn, not just Vesper governance turns | None for the insertion itself; new helper functions should be placed near `load_vesper_brief()` or `self_evaluate()` | If two cycles run concurrently, prompt assembly can observe a partially updated backlog summary while `self_evaluate()` is rewriting `EVOLUTION_LOG` in place |
| Inside `self_evaluate()` at lines 440-490, after `grade = round(...)` and before the log rewrite/posting block | Extend the evaluator here so it can compare “gap backlog reduced” against the existing turn-quality grade | `self_evaluate()` currently grades recent conversation efficiency, not feature closure. It rewrites `EVOLUTION_LOG` in place, so it is already unsafe under concurrent writers | No new imports for the existing logic; if you add markdown parsing or file locking, `re` and a lock helper are needed | If `CC --resume` is busy upstream, this file does not handle it directly. The real risk is that `self_evaluate()` will keep emitting PROOF for good turn quality even when no gap was closed |

Notes:
- `self_evaluate()` should not be the only signal of progress. It measures conversation quality, not deliverable completion.
- The existing `call_claude()` prompt caching block is good; keep any gap summary short enough that you do not nullify the cache benefit.

## [Karma2/map/preclaw1-gap-map.md](C:/Users/raest/Documents/Karma_SADE/Karma2/map/preclaw1-gap-map.md#L1)

| Anchor | Exact insertion point | Existing conflicts | Missing imports / helpers | Failure modes |
|---|---|---|---|---|
| Feature row anchors at lines 23-192 | Update the matching row for the feature being closed. Replace `**MISSING**` or `**PARTIAL**` with the new state and keep the Gap text consistent | The file has no evidence column. The plan’s “replace `**MISSING**` with `**HAVE**` and append evidence line” is incomplete because the summary counts at lines 198-216 must also be updated | None in the markdown file itself; the updater needs a lock and a row parser, which should live in a separate helper module | If two cycles run concurrently, one can rewrite a row while the other recomputes summary counts, producing a row/state mismatch or corrupted totals |
| Summary block at lines 198-218 | Recompute the category totals here after every successful feature closure | The current summary is manual and will drift unless it is rewritten together with the row update | No import needed in the markdown file; the writer should own the parse/rewrite logic elsewhere | If a patch/test/apply cycle fails after the row is edited but before the summary is rewritten, the map will become internally inconsistent |

Notes:
- The gap map should be treated as the authoritative closure ledger, not as commentary.
- A closure update is incomplete unless the row, the summary counts, and the evidence trail are all written in the same atomic operation.

## Bottom line

The cascade pipeline is directionally right, but the implementation anchors are wrong in three places:
- `vesper_watchdog.py` is much smaller than the plan assumes and has no candidate pipeline to extend.
- `vesper_governor.py` must hook into `_apply_to_spine()` / `run_governor()`, not a nonexistent `apply_promotion()`.
- `vesper_eval.py` must hard-reject diff-less and test-less candidates before the existing observational fast path can approve them.

## Appendix: Assimilable Primitives

Source sets:
- Anthropic docs: `docs/anthropic-docs/` and `docs/anthropic-docs/claude-code-inventory.md`
- Claude Code source tree: `docs/wip/preclaw1/preclaw1/src`

These are the primitives worth assimilating into the plan. They are not 1:1 recreations; they are the minimum reusable capabilities that reduce wrapper dependence and move The Goal toward a self-hosting harness.

### Anthropic Platform Primitives

| Primitive | Assimilation value for The Goal | Source anchors |
|---|---|---|
| Model selection and model cards | Make model choice explicit per task, per mode, per cost envelope | `docs/anthropic-docs/home.md`, `docs/anthropic-docs/intro.md`, `docs/anthropic-docs/release-notes-overview.md` |
| Messages API loop | Unify chat, cowork, and code around a single request/response substrate | `docs/anthropic-docs/get-started.md`, `docs/anthropic-docs/inventory.md` |
| Extended thinking | Preserve deep reasoning where it matters; suppress it when it does not | `docs/anthropic-docs/release-notes-overview.md`, `docs/anthropic-docs/inventory.md` |
| Adaptive thinking / effort / fast mode | Route light queries to cheap/fast paths; reserve heavy compute for real work | `docs/anthropic-docs/inventory.md` |
| Context windows and compaction | Keep long-running sessions stable without manual resets | `docs/anthropic-docs/inventory.md` |
| Context editing | Trim or rewrite stale context instead of carrying garbage forward | `docs/anthropic-docs/inventory.md` |
| Token counting | Make budget visible before the turn starts | `docs/anthropic-docs/inventory.md` |
| Prompt caching | Reduce repeated system-prompt cost and latency | `docs/anthropic-docs/release-notes-overview.md`, `docs/anthropic-docs/inventory.md` |
| Files support | Attach files directly to reasoning and code workflows | `docs/anthropic-docs/release-notes-overview.md`, `docs/anthropic-docs/inventory.md` |
| Streaming and fine-grained tool streaming | Improve latency and responsiveness for long tool chains | `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/release-notes-overview.md` |
| Citations and search results | Keep claims grounded in traceable evidence | `docs/anthropic-docs/release-notes-overview.md`, `docs/anthropic-docs/inventory.md` |
| Web search and web fetch tools | Let the harness verify fresh information without wrapper dependence | `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/release-notes-overview.md` |
| Code execution tool | Run isolated verification without delegating to the host shell for every step | `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/release-notes-overview.md` |
| Computer use tool | Add UI automation where the browser shell is insufficient | `docs/anthropic-docs/inventory.md` |
| Text editor tool | Support safe structured file edits and diffs | `docs/anthropic-docs/inventory.md` |
| Tool-use framework | Make tools first-class rather than ad hoc subprocesses | `docs/anthropic-docs/inventory.md` |
| Tool search / tool discovery | Expose the available action surface clearly | `docs/anthropic-docs/inventory.md` |
| Agent loop | Standardize observe -> think -> act -> verify -> persist | `docs/anthropic-docs/inventory.md` |
| Subagents | Split work cleanly into bounded worker loops | `docs/anthropic-docs/inventory.md` |
| Permissions | Gate dangerous operations with visible approval surfaces | `docs/anthropic-docs/inventory.md` |
| User input | Pause for missing facts instead of guessing | `docs/anthropic-docs/inventory.md` |
| Hooks | Attach pre/post actions to turns and events | `docs/anthropic-docs/inventory.md` |
| Sessions | Preserve continuity across launches and devices | `docs/anthropic-docs/inventory.md` |
| File checkpointing | Make edits reversible and auditable | `docs/anthropic-docs/inventory.md` |
| Structured outputs | Require machine-readable artifacts from evaluators and builders | `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/release-notes-overview.md` |
| MCP connector and remote MCP servers | Expand the harness through sanctioned external capabilities | `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/release-notes-overview.md` |
| Slash commands | Turn control actions into discoverable, typed, local commands | `docs/anthropic-docs/inventory.md` |
| Skills | Package reusable behavior and prompts as loadable units | `docs/anthropic-docs/inventory.md` |
| Plugins | Make extensibility a contract instead of a fork | `docs/anthropic-docs/inventory.md` |
| Todo tracking | Convert intent into explicit action state | `docs/anthropic-docs/inventory.md` |
| Cost tracking and usage APIs | Show spend, thresholds, and regressions in real time | `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/release-notes-overview.md` |
| Workspaces / administration APIs | Separate policy, limits, and project boundaries cleanly | `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/release-notes-overview.md` |
| Desktop / web / VS Code / JetBrains / Chrome surfaces | Collapse the wrapper into one shared system of control planes | `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/claude-code-inventory.md` |
| Slack / GitHub Actions / GitLab CI / third-party integrations | Let the harness operate where work already happens | `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/claude-code-inventory.md` |
| Changelog / troubleshooting / compliance docs | Preserve operational truth and reduce drift | `docs/anthropic-docs/inventory.md` |

### Claude Code Source Primitives

| Primitive | Assimilation value for The Goal | Source anchors |
|---|---|---|
| Command registry | Centralize slash commands, built-ins, and dynamic actions | `docs/wip/preclaw1/preclaw1/src/commands/` |
| Session history model | Support resume, rewind, export, compact, rename, share, tag | `docs/wip/preclaw1/preclaw1/src/history.ts` |
| Context assembler | Control what the harness sees, in what order, and at what budget | `docs/wip/preclaw1/preclaw1/src/context.ts` |
| Cost tracker and hooks | Make cost visible in-line instead of after the fact | `docs/wip/preclaw1/preclaw1/src/cost-tracker.ts`, `docs/wip/preclaw1/preclaw1/src/costHook.ts` |
| Dialog launchers | Use one launcher abstraction for sessions, settings, commands, plugins, and diffs | `docs/wip/preclaw1/preclaw1/src/dialogLaunchers.tsx` |
| Query engine | Add search and retrieval primitives over sessions, files, and memory | `docs/wip/preclaw1/preclaw1/src/query.ts`, `docs/wip/preclaw1/preclaw1/src/QueryEngine.ts` |
| Task model | Treat background work as first-class state, not incidental logs | `docs/wip/preclaw1/preclaw1/src/Task.ts`, `docs/wip/preclaw1/preclaw1/src/tasks.ts` |
| Tool model | Define tool schema, status, and affordances once | `docs/wip/preclaw1/preclaw1/src/Tool.ts`, `docs/wip/preclaw1/preclaw1/src/tools.ts` |
| Settings schema | Make config typed, discoverable, and editable from UI | `docs/wip/preclaw1/preclaw1/src/schemas/` |
| State model | Persist runtime state explicitly instead of smuggling it through globals | `docs/wip/preclaw1/preclaw1/src/state/` |
| Hooks layer | Keep UI state and side effects isolated and reusable | `docs/wip/preclaw1/preclaw1/src/hooks/` |
| Services layer | Separate policy, persistence, and integration services | `docs/wip/preclaw1/preclaw1/src/services/` |
| Plugin subsystem | Make extension loading and trust boundaries explicit | `docs/wip/preclaw1/preclaw1/src/plugins/` |
| Remote control / transport | Allow out-of-process control without collapsing the core loop | `docs/wip/preclaw1/preclaw1/src/remote/`, `docs/wip/preclaw1/preclaw1/src/bridge/` |
| Upstream proxy | Support transport failover and session routing | `docs/wip/preclaw1/preclaw1/src/upstreamproxy/` |
| Desktop and screen surfaces | Keep one implementation across shell, web, and native surfaces | `docs/wip/preclaw1/preclaw1/src/screens/`, `docs/wip/preclaw1/preclaw1/src/ink/`, `docs/wip/preclaw1/preclaw1/src/native-ts/` |
| Keybindings and vim mode | Let power users compress high-frequency actions | `docs/wip/preclaw1/preclaw1/src/keybindings/`, `docs/wip/preclaw1/preclaw1/src/vim/` |
| Voice stack | Add hold-to-talk and STT where text is too slow | `docs/wip/preclaw1/preclaw1/src/voice/` |
| Memory scanning | Pull memory from files and logs instead of asking the user to restate it | `docs/wip/preclaw1/preclaw1/src/memdir/` |
| Output styles | Match output format to task type instead of one generic voice | `docs/wip/preclaw1/preclaw1/src/outputStyles/` |
| Channels / routing | Keep multiple communication paths distinct and inspectable | `docs/wip/preclaw1/preclaw1/src/channels/` |
| Bootstrap / onboarding | Guide the system into a known state before work begins | `docs/wip/preclaw1/preclaw1/src/bootstrap/`, `docs/wip/preclaw1/preclaw1/src/setup.ts` |
| Entry points | Separate CLI startup, REPL startup, and background service startup | `docs/wip/preclaw1/preclaw1/src/entrypoints/`, `docs/wip/preclaw1/preclaw1/src/main.tsx`, `docs/wip/preclaw1/preclaw1/src/replLauncher.tsx` |
| Interactive helpers | Normalize prompt loops, confirmations, and terminal UX | `docs/wip/preclaw1/preclaw1/src/interactiveHelpers.tsx` |
| Project onboarding state | Track first-run and setup progress cleanly | `docs/wip/preclaw1/preclaw1/src/projectOnboardingState.ts` |
| Diffs and code review surfaces | Show changes as a first-class control plane | `docs/wip/preclaw1/preclaw1/src/components/`, `docs/wip/preclaw1/preclaw1/src/commands/` |

### Assimilation Order

1. Sessions, compaction, and context budgeting.
2. Slash commands and settings.
3. Permissions and tool gating.
4. Cost tracking and evaluation gates.
5. Plugins, skills, and MCP expansion.
6. Git, diff, and code-review surfaces.
7. Multi-surface transport: desktop, web, IDE, Chrome, remote control.
8. Voice and memory consolidation.

### Exclusions To Preserve

- Do not assimilate `buddy` or `coordinator` as user-facing requirements; they are explicitly excluded in the gap map.
- Do not treat the Claude Code wrapper as the product. Assimilate the primitives, then recompose them into the harness around The Goal.

### Claude-Mem Primitives

Source set:
- `docs/claude-mem-docs/README.md`
- `docs/claude-mem-docs/CLAUDE.md`
- `docs/claude-mem-docs/package.json`
- `docs/claude-mem-docs/CHANGELOG.md`

| Primitive | Assimilation value for The Goal | Evidence |
|---|---|---|
| Persistent memory compression | Add automatic capture, summarization, and replay across sessions instead of relying on wrapper recall | `README.md` and `CLAUDE.md` both describe persistent memory across sessions |
| Lifecycle hooks | Drive memory/context capture from explicit session and tool events rather than polling only | `CLAUDE.md` lists SessionStart, UserPromptSubmit, PostToolUse, Summary, SessionEnd |
| Worker service boundary | Keep heavy search/compression work off the hot path and behind an HTTP service | `CLAUDE.md` and `README.md` describe a worker on port 37778 |
| SQLite + vector hybrid memory | Store structured memory in SQLite and retrieve semantically relevant entries with vectors | `README.md` and `CLAUDE.md` both describe SQLite plus Chroma |
| Progressive disclosure search | Use search -> timeline -> fetch/full detail as the default retrieval pattern | `README.md` documents the 3-layer MCP search workflow |
| Privacy tags | Let users exclude sensitive content before it is persisted | `CLAUDE.md` documents `<private>` stripping at the hook layer |
| Skill-based retrieval | Expose memory access through a named skill instead of hidden magic | `README.md` describes `mem-search`; `CLAUDE.md` describes `plugin/skills/mem-search/SKILL.md` |
| Planning skill | Separate planning into a phased, documented skill so execution can stay narrow | `CLAUDE.md` references `make-plan` |
| Execution skill | Separate execution into an action-oriented skill so plans can be handed off cleanly | `CLAUDE.md` references `do` |
| Exit-code discipline | Distinguish graceful success, non-blocking errors, and blocking failures | `CLAUDE.md` defines exit codes 0/1/2 |
| Build-and-sync automation | Treat packaging, syncing, and worker restart as one repeatable pipeline | `package.json` includes `build-and-sync` and `worker:restart` |
| Search endpoint surface | Offer multiple retrieval entry points, not one monolithic memory fetch | `README.md` documents 4 MCP tools and the 3-layer workflow |
| Viewer UI | Provide a local web view for memory inspection and debugging | `README.md` describes `http://localhost:37778` viewer |
| Changelog discipline | Preserve operational history in generated release notes, not in ad hoc recollection | `CHANGELOG.md` is generated automatically and documents behavioral fixes |

### Claude-Mem Assimilation Priorities

1. Hook-based memory capture.
2. Worker-service separation for expensive operations.
3. Progressive disclosure retrieval.
4. Privacy-tag stripping before persistence.
5. Skill-based memory and planning surfaces.
6. Explicit exit-code and restart discipline.

## Ranked Backlog

This backlog translates the assimilable primitives into the smallest set of work items that materially reduce wrapper dependence and close the highest-value gap-map categories first.

| Rank | Backlog item | Primitive basis | Gap map targets | Why this comes first | Dependency notes |
|---|---|---|---|---|---|
| P0 | Session continuity core | Sessions, compaction, context windows, context editing, file checkpointing | Session Management, Bridge, Memory | Without durable session continuity, every other feature reverts to a cold start problem | Needs persistent state model and a single canonical session store |
| P0 | Gap-aware executor loop | Agent loop, structured outputs, tool-use framework, permissions, user input | Scheduling/Tasks, Multi-Agent, Tools | This is the actuator layer that turns ideas into verified work instead of commentary | Must hard-reject no-diff and no-test candidates before promotion |
| P0 | Truth and budget spine | Token counting, cost tracking, citations, search results, prompt caching | Cost, Settings, Commands, Memory | The harness needs to know what it costs and what it can prove before it spends cycles | Best paired with a visible cost bar and budget thresholds |
| P1 | Slash command and settings plane | Slash commands, settings, output styles, keybindings, hooks | Commands, Settings, Permission UI | This is the merged-workspace control plane that replaces wrapper-only control flows | Requires a command registry and typed config schema |
| P1 | Permission and tool gate UI | Permissions, tool search, tool-use framework, structured outputs | Permission UI, Tools, Agent/task visibility | You cannot safely scale autonomy if approvals stay hidden in the backend | Needs event stream from executor loop to UI |
| P1 | Session history and resume surface | Sessions, dialog launchers, history model, query engine | Session Management, Rendering/UI | Resume/rewind/export are the user-facing continuity primitives | Depends on the session store and search index |
| P1 | Diff and git control plane | Files support, text editor tool, code execution tool, code review surfaces | Git UI, Rendering/UI | Autonomous self-editing needs visible diffs and deterministic patch application | Should reuse a single diff renderer everywhere |
| P1 | Memory consolidation and retrieval | Memory scanning, context editing, query engine, hooks | Memory, Bridge, Search | Persistent memory is the other half of persistent identity | Needs explicit read/write policy for memory sources |
| P2 | Plugin and skills ecosystem | Plugins, skills, MCP connector, remote MCP servers | Plugins, Settings, Tools | Extensibility prevents the harness from hard-coding every capability | Requires trust boundaries and manifest validation |
| P2 | Multi-surface transport | Desktop/web/VS Code/JetBrains/Chrome surfaces, remote control, channels/routing | Bridge, IDE, Chrome, Desktop, Rendering/UI | The Goal explicitly requires combining surfaces instead of fragmenting them | Transport abstraction should sit below the UI layer |
| P2 | Voice and presence | Computer use tool, voice stack, adaptive thinking | Voice, Rendering/UI | Voice/presence matters only after the core control plane is stable | Do not ship before session/state reliability is solved |
| P2 | Evaluation and self-improvement | Agent loop, structured outputs, todo tracking, hooks, citations | Vesper pipeline, gap map, self-edit loop | The system must be able to judge its own outputs and reduce its backlog | Should consume real tests, not heuristic-only signals |

### Backlog Ordering Rules

1. Close state and continuity before adding new surfaces.
2. Add operator-visible control before expanding autonomy.
3. Add permission and diff visibility before broader self-editing.
4. Add plugins and remote surfaces after the control plane is stable.
5. Add voice and advanced presence last.

### Immediate Next Build Slice

1. Session store with resume/compact/export/rewrite primitives.
2. Command registry with `/help`, `/status`, `/cost`, `/context`, `/plan`.
3. Permission event stream from executor to UI.
4. Deterministic diff viewer and patch apply flow.
5. Gap-aware executor that emits one candidate, one diff, one test, one result.

## Phase Plan

### Phase 0 - Load-bearing primitives

Goal: make the harness continuous, inspectable, and safe before adding more surfaces.

Concrete file targets:
- `Scripts/karma_persistent.py`
- `Vesper/karma_regent.py`
- `Scripts/vesper_eval.py`
- `Scripts/vesper_governor.py`
- `Karma2/map/preclaw1-gap-map.md`

Deliverables:
- Gap-closure queue with one candidate, one diff, one test.
- Session persistence and resume safety for `CC --resume`.
- Hard rejection of diff-less or test-less work items.
- Atomic gap-map row and summary updates.

### Phase 1 - Memory and continuity

Goal: merge claude-mem style persistence into the harness.

Concrete file targets:
- `Vesper/karma_regent.py`
- `Scripts/karma_persistent.py`
- `docs/claude-mem-docs/CLAUDE.md` as behavioral reference only

Deliverables:
- Persistent session state with replayable history.
- Memory summary injection from a single canonical store.
- Privacy-tag or equivalent redaction before persistence.
- Hook-like event capture around user input, tool use, and session end.

### Phase 2 - Merged workspace control plane

Goal: expose the control plane in the UI so the wrapper is not the only operator.

Concrete file targets:
- `frontend/src/`
- `hub-bridge/app/proxy.js`
- `electron/main.js`
- `preload.js`
- `Karma2/map/preclaw1-gap-map.md`

Deliverables:
- Slash commands.
- Settings page.
- Session history sidebar.
- Cost/status bar.
- Permission prompts.
- Diff and git panels.

### Phase 3 - Retrieval and planning

Goal: make retrieval and planning explicit, fast, and token-efficient.

Concrete file targets:
- `Karma2/primitives/INDEX.md`
- `Karma2/cc-scope-index.md`
- `docs/claude-mem-docs/README.md` as the retrieval model reference
- `docs/claude-mem-docs/package.json` as the execution model reference

Deliverables:
- Search-first memory retrieval pattern.
- Plan skill and execution skill parity in the harness.
- Token-budget visibility and context budgeting.
- Better task decomposition from memory/query results.

### Phase 4 - Extensibility

Goal: let the harness grow without hard-wiring every capability.

Concrete file targets:
- `plugins/`
- `skills/`
- `docs/claude-mem-docs/CLAUDE.md`
- `docs/anthropic-docs/inventory.md`

Deliverables:
- Plugin loading and trust boundaries.
- Skill packaging and discovery.
- MCP and remote tool expansion.
- Clean approval surfaces for third-party extensions.

### Phase 5 - Multi-surface transport

Goal: collapse the 3-tab wrapper into one coordinated surface.

Concrete file targets:
- `hub-bridge/app/proxy.js`
- `frontend/src/`
- `electron/main.js`
- `preload.js`
- `docs/anthropic-docs/inventory.md`

Deliverables:
- Unified Chat + Cowork + Code entry surface.
- Transport fallback and retry discipline.
- Desktop/web/IDE/Chrome surface alignment.
- Better session routing across devices.

### Phase 6 - Self-improvement loop

Goal: turn observation into verified progress with closing feedback loops.

Concrete file targets:
- `Vesper/vesper_watchdog.py`
- `Scripts/vesper_eval.py`
- `Scripts/vesper_governor.py`
- `Vesper/karma_regent.py`
- `Karma2/map/preclaw1-gap-map.md`

Deliverables:
- Ranked gap candidate emission.
- Real test gating.
- Smoke-tested promotion application.
- Gap-map closure evidence and backlog reduction reporting.

### Phase 7 - Voice and presence

Goal: add voice and richer presence only after the core harness is stable.

Concrete file targets:
- `frontend/src/`
- `electron/main.js`
- `preload.js`
- `docs/anthropic-docs/inventory.md`

Deliverables:
- Voice mode.
- Presence indicators.
- Optional camera/video hooks only if the control plane and memory are already stable.

### Phase 8 - Hardening and drift control

Goal: keep the system honest after it starts shipping.

Concrete file targets:
- `.gsd/STATE.md`
- `.gsd/ROADMAP.md`
- `.gsd/codex-cascade-audit.md`
- `docs/claude-mem-docs/CHANGELOG.md`

Deliverables:
- Drift checks against the gap map.
- Release-note style change tracking.
- Stronger regression gates.
- No unverified claims in state docs.

## Implementation Checklist

This is the exact edit order I would use if converting the phase plan into code changes. Keep the order unless a dependency forces a reversal.

### Step 1 - Make the executor loop gap-aware

Files:
- `Scripts/karma_persistent.py`
- `Scripts/vesper_eval.py`
- `Scripts/vesper_governor.py`
- `Karma2/map/preclaw1-gap-map.md`

Edits:
- Add `gap_closure` as a first-class actionable type.
- Add structured gap-closure context generation.
- Reject candidates without `target_files`, `test_command`, and a real diff.
- Route approved changes through smoke tests before writeback.
- Update gap-map rows and totals atomically after success.

Exit condition:
- One gap candidate produces one diff, one test, one promotion, one gap-map update.

### Step 2 - Add gap backlog awareness to the regent loop

Files:
- `Vesper/karma_regent.py`
- `Vesper/vesper_watchdog.py`

Edits:
- Load a concise gap backlog summary into system prompt assembly.
- Extend self-evaluation to measure backlog reduction, not only turn quality.
- Add gap-map parsing helpers and ranker logic.
- Emit structured gap candidates from the watchdog path.

Exit condition:
- Regent can see the current backlog and report when backlog shrinks.

### Step 3 - Make memory continuous and replayable

Files:
- `Vesper/karma_regent.py`
- `Scripts/karma_persistent.py`
- `docs/claude-mem-docs/CLAUDE.md` as behavior reference

Edits:
- Preserve session history in a single canonical store.
- Add replay-friendly memory summaries.
- Strip or redact private content before persistence.
- Make user/tool/session lifecycle events explicit.

Exit condition:
- A restart does not lose context, and replayed context stays bounded.

### Step 4 - Build the merged workspace control plane

Files:
- `frontend/src/`
- `hub-bridge/app/proxy.js`
- `electron/main.js`
- `preload.js`

Edits:
- Add slash commands.
- Add settings and session history surfaces.
- Add cost, status, permission, and diff panels.
- Add operator-visible agent/task state.

Exit condition:
- The wrapper is no longer the only control plane.

### Step 5 - Add retrieval and planning primitives

Files:
- `Karma2/primitives/INDEX.md`
- `Karma2/cc-scope-index.md`
- `docs/claude-mem-docs/README.md`
- `docs/claude-mem-docs/package.json`

Edits:
- Add search-first memory retrieval rules.
- Add explicit planning/execution separation.
- Add token-budget and context-budget visibility.
- Add task decomposition helpers sourced from retrieval.

Exit condition:
- Planning and retrieval are explicit, budget-aware, and reusable.

### Step 6 - Add extensibility

Files:
- `plugins/`
- `skills/`
- `docs/anthropic-docs/inventory.md`

Edits:
- Add plugin loading and trust boundaries.
- Add skill discovery and packaging.
- Add MCP expansion points.
- Keep extension hooks explicit and reviewable.

Exit condition:
- New capabilities can be added without forking the harness core.

### Step 7 - Expand surfaces only after the core is stable

Files:
- `hub-bridge/app/proxy.js`
- `frontend/src/`
- `electron/main.js`
- `preload.js`

Edits:
- Unify Chat + Cowork + Code into one coordinated surface.
- Add transport fallback and retry discipline.
- Align desktop, web, IDE, and Chrome routing.

Exit condition:
- The user sees one coherent harness, not three tabs and a wrapper leak.

### Step 8 - Harden drift control

Files:
- `.gsd/STATE.md`
- `.gsd/ROADMAP.md`
- `.gsd/codex-cascade-audit.md`
- `docs/claude-mem-docs/CHANGELOG.md`

Edits:
- Record verified state only.
- Keep the audit and roadmap synchronized with shipped work.
- Gate claims on live evidence.
- Preserve release-note style provenance.

Exit condition:
- The system can describe its state without inventing it.

## First 10 Edits

1. Add `gap_closure` to `Scripts/karma_persistent.py` `ACTIONABLE_TYPES`.
2. Add structured gap-closure context builder in `Scripts/karma_persistent.py`.
3. Add hard reject checks for no diff / no test in `Scripts/vesper_eval.py`.
4. Route approved gap candidates through smoke tests in `Scripts/vesper_governor.py`.
5. Add atomic gap-map row and summary update helper in `Scripts/vesper_governor.py`.
6. Add gap-map parser and ranker helpers in `Vesper/vesper_watchdog.py`.
7. Add concise gap backlog summary loader in `Vesper/karma_regent.py`.
8. Inject backlog summary into `Vesper/karma_regent.py` system prompt assembly.
9. Extend `Vesper/karma_regent.py` `self_evaluate()` with backlog-reduction awareness.
10. Update `Karma2/map/preclaw1-gap-map.md` rewrite path so row status and summary counts change together.

## Execution Rule

- Do not start UI work until Step 10 is complete and verified.
- Do not allow any candidate to reach promotion without a real diff and a real test.
- Do not treat backlog reduction as complete until the gap map itself changes atomically.

