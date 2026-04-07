# memcompare.md

## Ground Truth Sources Read
- mempalace-main (local leak): README.md, miner/search code surfaces, hooks/benchmarks layout
- claude-mem-docs (canonical used today): repo structure, worker + sqlite services, hooks architecture, context/usage docs

## High-Signal Primitives in mempalace-main
- **Palace topology**: wings/rooms/halls/tunnels/closets/drawers schema for namespace + cross-linking. Built-in cross-wing tunnels aid disambiguation without vector search first.
- **AAAK dialect**: lossless shorthand (~30x compression, ~170-token wake-up). Text-only; model-agnostic; no decoder needed. Good for pre-loading continuity in small context budgets.
- **Wake-up context generator**: `mempalace wake-up` emits minimal critical facts; fits into system prompt for local models.
- **Mining modes**: projects (code/docs), convos (chat exports), general (auto classify into decisions/preferences/milestones/problems/emotion). Multiple extractors already wired.
- **MCP tool suite (19 tools)**: mempalace_search, status, etc; ready drop-in for MCP-capable UIs (Claude, Cursor). Hooks scripts (`mempal_save_hook.sh`, `mempal_precompact_hook.sh`) for autosave/pre-compaction.
- **No-cloud dependency**: Chroma + local pipeline only; designed to run offline.
- **Benchmarks + runners**: LongMemEval runners, hybrid rerank, locomo/convomem etc. Useful for regression harness against our own stack.

## High-Signal Primitives in claude-mem-docs (current stack)
- **Worker/daemon with hooks**: robust lifecycle, SSE broadcaster, session/store/search services over SQLite, hook lifecycle with PostToolUse/Context reinjection, zombie-prevention.
- **Search strategies**: hybrid Chroma/SQLite/Timeline builders, filters, rankers, transcript watcher.
- **Session & observation schema**: transcripts, prompts, summaries, timeline; includes migration framework and constraints.
- **Install/ops**: npm/bun-based worker, process manager, health monitor, version checks, Windows quirks (WMIC parsing), tests.
- **UI viewer**: React viewer for logs/observations/prompts with SSE.

## Contrast (what mempalace adds vs claude-mem)
- Topology & AAAK give structured, compressible wake-up contexts; claude-mem lacks lossless compression and wing/room/tunnel grouping.
- Mining for convos/code with automatic room typing; claude-mem assumes upstream hook/feed and lighter auto-classification.
- MCP-first tool surface; claude-mem plugin/hook surface is Claude-specific and heavier.
- Benchmarks ready to run; claude-mem has no LongMemEval harness bundled.

## Gaps/Risks in mempalace for Nexus
- Python/Chroma-only; no built-in permissions/worker orchestration or SSE; no session resume semantics; no transcript watcher.
- No Windows service packaging; minimal tests (few unit tests only).
- AAAK grammar not integrated with tool-use hooks; would need port into cc_server/Electron tool loop.
- No evidence of multi-user auth, privacy checks, or write gating; must route through permission_engine.

## Adopt (direct lift)
1) **AAAK wake-up emitter**: port the dialect generator to produce ~170-token continuity preamble; inject into CC/Electron system prompt and K2 cortex warm start.
2) **Palace topology mapping**: adopt wings/rooms/halls/tunnels as logical namespaces over claude-mem observations; store as tags/fields in sqlite and search indexes.
3) **Benchmarks**: reuse `benchmarks/*.py` runners to score Nexus memory (Claude-mem backend) after integration; keep for regression.
4) **Mining modes**: incorporate convo/project/general extractors as feeders into claude-mem ingestion hook (permission-gated) instead of separate DB.
5) **Wake-up command**: add Nexus CLI/API to emit compressed continuity block (using AAAK + palace) for fallback local models.

## Adapt (needs integration work)
- **MCP tool surface**: wrap claude-mem search/status into MCP-compatible server mirroring mempalace tool set; keep permission_engine gate.
- **Hooks**: translate `mempal_save_hook` & `precompact` into our hook lifecycle (session-end / posttooluse) to compact/prune.
- **Entity/graph utilities**: map `entity_detector` and `knowledge_graph` outputs into claude-mem observation fields for better cross-room tunneling.

## Reject / Avoid
- Duplicating storage (Chroma + sqlite) — keep single claude-mem sqlite+vector store; ingest mempalace outputs as views.
- Replacing claude-mem worker/daemon with mempalace CLI; we retain our daemon and permission engine.

## Recommended merge plan for Nexus
1) **Add AAAK module** into claude-mem ingestion pipeline: generate compressed wake-up block per session and cache for CC/Electron/K2 cortex.
2) **Extend schema**: add wing/room/hall/tunnel tags to observations; create derived palace graph materialized view.
3) **Feeders**: build permissioned ingestion hook that runs mempalace-style miners (projects/convos/general) and writes into claude-mem sqlite with palace tags; no separate DB.
4) **MCP façade**: expose claude-mem search/status via MCP tool definitions aligned to mempalace tool names for Claude/Cursor parity.
5) **Bench regressions**: wire LongMemEval runner to CI against claude-mem DB; add convomem/locomo smoke benches.
6) **Wake-up endpoint**: new /memory/wakeup returns AAAK+palace summary for local models and fallback cascades.
7) **Retention/compaction**: adapt precompact hook to our retention policy; ensure permission_engine gating before execution.

## Files to reference during implementation
- mempalace AAAK & topology: `mempalace/dialect.py`, `normalize.py`, `layers.py`, `palace_graph.py`
- Miners: `mempalace/convo_miner.py`, `miner.py`, `general_extractor.py`, `entity_detector.py`
- MCP: `mempalace/mcp_server.py`, `examples/mcp_setup.md`
- Hooks: `hooks/mempal_precompact_hook.sh`, `hooks/mempal_save_hook.sh`
- Benchmarks: `benchmarks/longmemeval_bench.py`, `benchmarks/convomem_bench.py`, `benchmarks/BENCHMARKS.md`
- Claude-mem integration points: `claude-mem-docs/src/services/sqlite/*`, `src/services/worker/*`, `docs/public/architecture/*.md`, hook lifecycle tests (`tests/integration/hook-execution-e2e.test.ts`)

## Immediate Actions (for Nexus next sprint)
- Lift AAAK generator and palace tagging into claude-mem ingestion.
- Build wake-up endpoint + palace-tagged search API.
- Add LongMemEval runner to CI against claude-mem DB.
- Keep single storage; disable any parallel Chroma instance unless under our control.
