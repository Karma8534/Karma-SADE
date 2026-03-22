# CC Scope Index — Phase A-1 (2026-03-21)
# Loaded at resurrect Step 1e. 2-line entries: [ID] Rule | Why

## PITFALL Skills

P001 [architecture-divergence]:
Rule: hub-bridge BUILD SOURCE = /opt/seed-vault/memory_v1/hub_bridge/app/server.js (NOT git repo). cp before EVERY rebuild.
Why: git pull without cp → docker build uses stale COPY layer → wrong code deploys silently.

P002 [undocumented-k2-agents]:
Rule: Before assuming K2 state, SSH and run `systemctl status karma-regent aria` — both run autonomously.
Why: karma-regent.service and aria.service act between CC sessions; assuming idle causes duplicate work or conflict.

P003 [vesper-falkordb-unverified]:
Rule: After batch_ingest --skip-dedup, verify FalkorDB node count via /v1/cypher BEFORE claiming success.
Why: Graphiti mode silently fails at scale — watermark advances, 0 nodes written, "All caught up" logged as success.

P004 [cp-no-overwrite]:
Rule: Never use `cp -r source/ dest/` — use explicit per-file cp for each changed file.
Why: cp -r silently skips files already present in dest/; stale build context is the #1 deploy failure cause.

P005 [falkordb-env-vars]:
Rule: FalkorDB container REQUIRES both: FALKORDB_DATA_PATH=/data AND FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 100'.
Why: Without DATA_PATH — RDB never lands on volume, every restart = empty graph. Without ARGS — queries timeout at scale (72% batch failure rate verified).

P006 [docker-restart-no-env]:
Rule: `docker restart anr-hub-bridge` does NOT re-read hub.env. Use `docker compose -f compose.hub.yml up -d`.
Why: restart reuses existing container env; new env_file entries (models, limits, flags) are invisible until container recreated.

P007 [allowed-tools-whitelist]:
Rule: Every new tool in hub-bridge TOOL_DEFINITIONS must ALSO be added to hooks.py ALLOWED_TOOLS + karma-server rebuilt.
Why: ALLOWED_TOOLS gates ALL tool calls before execute_tool_action(); unknown tool → {"ok":false,"error":"Unknown tool"} with no helpful context.

P008 [aria-delegated-header]:
Rule: aria_local_call sends X-Aria-Service-Key ONLY. Never add X-Aria-Delegated header.
Why: X-Aria-Delegated triggers delegated_read_only policy — memory writes silently dropped, observations stay at 0.

P009 [batch-ingest-skip-dedup]:
Rule: batch_ingest cron MUST use --skip-dedup always. Direct Cypher write: 899 eps/s, 0 errors. Verify: `crontab -l | grep batch` must show --skip-dedup.
Why: Graphiti dedup mode silently fails at scale — watermark advances, 0 FalkorDB nodes created. This is NOT an obvious failure.

P010 [hub-bridge-build-context]:
Rule: After git pull on vault-neo, cp hub-bridge/lib/*.js to /opt/seed-vault/memory_v1/hub_bridge/lib/ before --no-cache rebuild.
Why: Build context ≠ git repo. lib/ files were not in git until Session 75. Missing copy → "Cannot find module" at startup.

P011 [deep-mode-gate-missing]:
Rule: Standard /v1/chat must route to callLLM() not callLLMWithTools(). Gate: `deep_mode ? callLLMWithTools() : callLLM()` at the call site — never unconditional.
Why: callLLMWithTools called unconditionally routes all GLM requests to callGPTWithTools with full tool list — tools fire on standard chat silently. Security fix commit 41b2c06.

P012 [write-id-pre-llm]:
Rule: Generate req_write_id BEFORE the LLM call and thread through callLLMWithTools→callGPTWithTools→executeToolCall. Gate to deep_mode only (null for standard).
Why: vault turn_id is only assigned AFTER the LLM call completes — write_memory has no key to return to /v1/feedback without pre-generated write_id.

P013 [corrections-log-read-only]:
Rule: Never write to corrections-log.md from hub-bridge container. Use vaultPost("/v1/ambient") with tags:["dpo-pair"] for correction records.
Why: Repo is volume-mounted read-only in hub-bridge container — writes to corrections-log.md fail silently or throw permission errors.

P014 [model-deep-nonexistent-fallback]:
Rule: MODEL_DEEP fallback in server.js must be a real valid model (gpt-4o-mini). Add startup validation — refuse to start if model not in allowed set.
Why: `process.env.MODEL_DEEP || "gpt-5-mini"` — gpt-5-mini doesn't exist. Env var override masked it; if hub.env loses MODEL_DEEP all deep requests silently 404.

P015 [glm-pricing-fabricated]:
Rule: GLM-4.7-Flash is Z.ai free tier — always $0.00. Never apply OpenAI price constants to free-tier models. Use a pricing table keyed by {provider, model}.
Why: PRICE_GPT_5_MINI_INPUT_PER_1M=$0.15 was applied to free GLM traffic; MONTHLY_USD_CAP enforced against fabricated numbers — budget protection was entirely fictional.

P016 [skip-dedup-freezes-entity-graph]:
Rule: --skip-dedup writes Episodic nodes only. For ongoing cron, use Graphiti mode with watermark to get Entity/relationship extraction. Keep safety cap ≤200 eps/run.
Why: After Session 59 standardized --skip-dedup, Entity graph froze at 571 legacy nodes. Karma could recall text but not reason across sessions (no structured knowledge graph).

P017 [zai-key-not-read]:
Rule: After adding any API key to hub.env, verify server.js explicitly reads and uses it. process.env.ZAI_API_KEY must be read AND a separate OpenAI-compatible client created with the right baseURL.
Why: ZAI_API_KEY was in hub.env and visible in container env, but server.js never imported it — all GLM requests routed to api.openai.com and returned 404 silently.

P018 [ingest-episode-never-fired]:
Rule: Browser /v1/chat path must fire-and-forget POST to /ingest-episode after each response. Consciousness loop must call /auto-promote every 10 cycles or episodes never reach Entity graph.
Why: hub-bridge only called /raw-context and /write-primitive — never ingest_episode(). 1230 Episodic nodes existed but zero new Entity/relationship nodes from any browser conversation.

P019 [heredoc-corrupts-python-files]:
Rule: Never use heredoc to write Python or JS source files on vault-neo. Write locally then scp. Verify after: wc -l file.py should be > 1.
Why: memory_tools.py became a 29865-byte single line (0 newlines) via heredoc \n injection — container crashed at startup. Recovery required extracting from previous working Docker image.

P020 [falkordb-host-127-not-container-name]:
Rule: In karma-server compose, use FALKORDB_HOST=127.0.0.1 not FALKORDB_HOST=falkordb. Check existing working container env before rebuild: docker inspect --format '{{.Config.Env}}'.
Why: Container name resolution failed — FalkorDB was on host network at 127.0.0.1, not reachable by container name from karma-server on the Docker network.

P021 [windows-openssh-admin-key-path]:
Rule: For Windows admin users, SSH authorized keys go to C:\ProgramData\ssh\administrators_authorized_keys + icacls to restrict permissions. ~/.ssh/authorized_keys is ignored for admins.
Why: OpenSSH on Windows rejects ~/.ssh/authorized_keys for Administrators group members — silently fails authentication with no helpful error.

## DECISION Archive (from claude-mem + sessions)

D001 [entity-relationships]:
Rule: Use MENTIONS co-occurrence cross-join for entity relationships, NOT RELATES_TO.
Why: 1,423 RELATES_TO edges permanently frozen at 2026-03-04 (Graphiti dedup era). MENTIONS is the live data.

D002 [droplet-primary]:
Rule: Droplet (vault-neo) is authoritative. K2 is worker/cache. K2 reboot = no data loss if sync protocol followed.
Why: Session-58 found 1754 lines of prod code written directly on droplet, never in git. One checkout would have destroyed it.

D003 [git-on-windows]:
Rule: All git ops via PowerShell on P1. Never use Git Bash for git commands.
Why: Git Bash has persistent index.lock on Windows — commits silently fail or corrupt.

D004 [falkordb-graph-name]:
Rule: FalkorDB graph is `neo_workspace`. The `karma` graph exists but is EMPTY.
Why: All batch_ingest and karma-server queries must target neo_workspace or return zero results.

D005 [compose-hub-location]:
Rule: compose.hub.yml lives at /opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml — NOT in git repo root.
Why: Running compose from wrong directory fails silently — file not found, no error.

D006 [system-prompt-update]:
Rule: To update Karma's persona: edit Memory/00-karma-system-prompt-live.md → git push → git pull vault-neo → docker restart anr-hub-bridge. NO rebuild needed.
Why: KARMA_IDENTITY_PROMPT is file-loaded at startup via fs.readFileSync. Volume-mounted read-only. Rebuild wastes 3-5 min.

D007 [k2-ssh-user]:
Rule: SSH through reverse tunnel: always `karma@localhost -p 2223`. Never `neo@localhost`.
Why: K2 has no `neo` account. Default user inference gives Permission denied with no helpful error.

D008 [vesper-cascade-monoculture]:
Rule: All 20 current Vesper spine patterns are cascade_performance (latency stats). NOT behavioral identity.
Why: No surprise filter in watchdog — every turn generates same pattern type. TITANS fix required (Phase 0-F).

D009 [banked-approvals]:
Rule: Before any significant action (deploy, SSH write, tool addition), check Karma2/banked-approvals.json and decrement.
Why: Sovereign pre-authorized 100 actions across 7 categories. Avoids mid-session interruption while maintaining governance.

D010 [loop-circuit-breaker]:
Rule: Same AC failed 3+ times → STOP. Post findings to coordination bus. Await Sovereign. No attempt #4 without re-authorization.
Why: Re-diagnosing the same failure from scratch each attempt wastes credits and misses systemic root cause.

D013 [topology-in-self-knowledge-prefix]:
Decision: Inject infrastructure topology (droplet/P1/K2 roles, reverse tunnel) into self-knowledge prefix in server.js — fires every /v1/chat turn, never trimmed, ~50 tokens.
Why: Karma confused PAYBACK (machine) with project entities. FalkorDB graph holds machine names as entities from conversation history, causing confabulation about topology.

D011 [dpo-pairs-in-ledger]:
Decision: Store DPO preference pairs in vault ledger via /v1/ambient with tags:["dpo-pair"]. Not in corrections-log.md (read-only) or separate file.
Why: Zero new infrastructure. Auto-picked up by batch_ingest. Queryable with jq. Thumbs-up=chosen, thumbs-down=rejected, with optional note as preferred phrasing.

D012 [graphiti-watermark-approach]:
Decision: Re-enable entity extraction for new episodes using watermark file at /ledger/.batch_watermark. Initialize to current wc -l to skip 3049 historical episodes. Safety cap 200 eps/run.
Why: Forward-only Graphiti mode at normal cadence (50-150 eps/window) stays under ~250 timeout threshold. Watermark-only-advances-on-success gives automatic retry on failure.

P022 [regent-processed-ids-not-persistent]:
Rule: karma-regent must persist processed coordination bus IDs to disk (k2/cache/.processed_ids) and load at startup. Never rely on in-process set only.
Why: _processed_ids set resets on every systemd restart — bus returns same pending messages on every 5s poll → coord messages processed 8x in 23s, ~21 API calls/min. Verified Session ~100.

P023 [cc-sentinel-stale-process]:
Rule: After any edit to cc_sentinel.py, kill the running process and restart via cc_sentinel_launch.vbs before testing.
Why: cc_sentinel.py runs via VBS at Windows startup. Edits to the file don't affect the live Python process — new functions exist on disk but raise AttributeError in the running process until restarted.

P024 [sade-doctrine-absent-from-resurrect]:
Rule: /resurrect MUST read SADE canonical definitions (for-karma/SADE — Canonical Definitions.txt) at Step 1c before any work begins.
Why: Without Step 1c, Hyperrails/Aegis/TSS/Directive One are undefined on every cold start. CC had identity (who) but no cognitive framework (how) — re-derived approach from scratch each session. Fixed Session 98.

P025 [resume-block-identity-only]:
Rule: resume_block must carry 4 layers: (1) rank+identity, (2) SADE doctrine ref, (3) cognitive trail (last 2-3 active reasoning threads), (4) active task+approach. Update cognitive trail at wrap-session.
Why: Resume block carried rank assertions only — cognitive trail and active approach evaporated on cold start, forcing full re-derivation. Fixed Session 98.

P026 [code-deployed-not-behavior-verified]:
Rule: "Verified" means Karma's response content changed due to the new data — not that code deployed + container restarted. Test from browser: did Karma actually USE the data?
Why: K2 bridge silently returns (empty) for all missing kiki_ files — no error. CC declared "bridge working" while delivering five empty placeholders across Sessions 87-89. Code correctness ≠ behavioral impact.

P027 [k2-wsl-python-not-python3]:
Rule: In K2 WSL prompt templates and test_command strings, always use `python3` not `python`. Post-process LLM output: replace `python ` with `python3 ` before executing test_command.
Why: K2 WSL has only `python3`. LLM-generated test commands use `python` → `/bin/sh: 1: python: not found` → valid scripts incorrectly reverted. Verified Session 89 (v5 cycles 1-2, 2 false failures).

P028 [reclassify-not-fix]:
Rule: A bug is open until working code ships. If you diagnose a real user-visible bug, either fix it immediately OR add it to an explicit deferred list with Sovereign confirmation. Never close it by relabeling severity.
Why: Session 86b: localStorage conversation persistence labeled "cosmetic UX, not critical" after diagnosis — no code written. Next session: Colby asked why it was still broken. Diagnosis + downgrade = false progress.

P029 [k2-memory-query-hardcoded]:
Rule: Always pass userMessage (or the relevant dynamic query) to fetchK2MemoryGraph(), never a hardcoded string like "Colby".
Why: Hardcoded query="Colby" meant K2 always returned facts about Colby regardless of conversation topic — 297 chars of mostly irrelevant context. Diagnosed Session 90.

P030 [aria-endpoint-path-mismatch]:
Rule: Before hardcoding any K2 Aria endpoint path in server.js, verify with: `curl http://K2IP:7890/api/X` and check the Allow header. Document all K2 Aria routes in a table.
Why: `/api/memory_graph` (underscore, POST) silently returned 404 — correct path is `/api/memory/graph` (slash, GET). K2 memory missing from Karma's context for multiple sessions. Sessions 84 (031126a).

P031 [sade-doctrine-file-missing]:
Rule: Before claiming resurrect Step 1c works, verify `for-karma/SADE — Canonical Definitions.txt` physically exists on P1. Add file-existence check to resurrect script.
Why: File was referenced in resurrect Step 1c but never created — silently fails every cold start with no error. CC runs without SADE doctrine (Aegis, Hyperrails, TSS, Directive One) for every session. Discovered Session 109.

P032 [cc-scratchpad-two-copies]:
Rule: cc_scratchpad.md canonical path = K2 `/mnt/c/dev/Karma/k2/cache/cc_scratchpad.md` only. Never write to vault-neo copy unless explicitly syncing. Resurrect reads K2 version — vault-neo copy is dead storage.
Why: File existed on both vault-neo and K2 with no sync. CC writes to vault-neo copy that next session never reads. Silent context loss every session. Discovered Session 109.

P033 [falkordb-pattern-nodes-no-content]:
Rule: Behavioral pattern text lives in vesper_identity_spine.json (proposed_change.description), NOT in FalkorDB Pattern nodes. Read from spine JSON when injecting behavioral context into hub-bridge.
Why: governor writes Pattern nodes with only type/confidence/promoted_at — no text. karma-server querying FalkorDB for patterns would find nothing meaningful. Fixed Session 113 by reading spine JSON directly via K2 /api/exec.

P034 [tier-routing-ignores-body-tier]:
Rule: To force tier 3 (full K2 working memory + behavioral patterns), set `x-karma-deep: true` HTTP header. Body `tier` param is silently ignored by classifyMessageTier().
Why: Test calls with `{"tier": 3}` always got tier 1 (short message). K2 behavioral patterns never appeared in test output until deep header was set. Verified Session 113.

P035 [vesper-eval-heuristic-blind-types]:
Rule: When adding new Vesper candidate types that lack reliable keyword heuristics, add them to HEURISTIC_BLIND_TYPES in vesper_eval.py to force model_weight=1.0.
Why: behavioral_continuity, tool_utilization_repair, and similar types return fixed 0.25 heuristic scores. 0.4×0.25 drag merges merged score below 0.80 gate → 100% rejection. All 3 behavioral_continuity candidates rejected before fix. Session 113.

P036 [consciousness-py-router-tuple-not-dict]:
Rule: router.complete() returns a tuple (response_text, model_name) — always unpack it, never call .get() on it, and never await it (it is synchronous).
Why: consciousness.py called response.get('content', '') on the tuple and awaited the synchronous call → AttributeError on every consciousness loop LLM call; _think() silently failed on all GLM invocations.

P037 [k2-env-in-subdir]:
Rule: K2 .env file must be at C:\Karma\karma-core\.env (karma-core subdir), NOT repo root. config.py must call load_dotenv() before any os.getenv() call.
Why: Server reads env from its working directory (karma-core/); root .env is never loaded — all vars silently return None.

P038 [ollama-70b-vram-fail]:
Rule: Never assign a 70B+ Ollama model to a real-time consciousness loop on 8GB VRAM hardware — runs at ~1 tok/s via CPU fallback.
Why: 70B models at 4-bit need ~35GB VRAM; 8GB forces CPU inference at 52x slower than VRAM-resident 7B models. RTX 4070 max viable model: ~7B.

P039 [k2-brewing-only]:
Rule: K2 must not be activated until Week 4+ when Karma has self-improvement proposals to test. Activating earlier wastes setup time with zero learning value.
Why: K2 setup took 9.5 hours in Week 1; Karma learns from vault-neo construction, not K2. K2 is a brewing testbed, not a learning substrate.

P040 [unicode-windows-python]:
Rule: Always set PYTHONUTF8=1 before launching Python server on Windows. In PowerShell: $env:PYTHONUTF8=1; python server.py.
Why: Non-ASCII chars in FalkorDB output, memory files, or logs cause UnicodeEncodeError and crash the process with no recovery path.

P041 [docker-container-id-ephemeral]:
Rule: Never hardcode Docker container IDs in scripts or docs — they change on every rm+run cycle. Use container names or `docker ps` at runtime.
Why: Documentation with specific IDs (e.g., 81e0197660d7) is stale after any container recreate. Container names are stable across restarts if --name is used.

P042 [hub-auth-token-extension-not-hot-patchable]:
Rule: Any hub endpoint auth token change requires simultaneous Chrome extension update + user reinstall. Extension token is in chrome.storage.local — not server-patchable.
Why: Hub v2.1.0 switched to HUB_CAPTURE_TOKEN; extension kept sending old Vault bearer → all captures silently failed (popup 0/0, no error).

P043 [brief-k2-status-unverified]:
Rule: Never accept cc-session-brief.md "K2 Unavailable" as ground truth. Always run direct SSH at Step 1b: `ssh vault-neo "ssh -p 2223 -l karma localhost 'echo K2_REACHABLE'"`.
Why: Brief probes Aria HTTP (port 7890); SSH tunnel is independent. Aria down ≠ K2 down. Skipping Step 1b loses resume_block + stable patterns for the entire session. Verified 2026-03-22: brief said Unavailable, direct SSH returned K2_REACHABLE + spine v38 instantly.

B001 [resurrect-no-autostart]:
Rule: After Step 5 announcement, response MUST end with tool calls for item 2 — not prose. "Starting now." with no following tool call = B001 violation.
Why: Step 5 annotated [immediately executes item 2] as prose, not contract. Session 118: CC announced "Starting now" and response terminated — Colby had to say "go". Wasted round-trip every session until fixed 2026-03-22.

P044 [brainstorm-when-spec-exists]:
Rule: Do NOT invoke superpowers:brainstorming when PLAN.md has full spec for the current task OR .gsd/phase-[X]-PLAN.md already exists. Write GSD docs from the spec and execute Task 1 immediately.
Why: Session 120: K-3 had full spec in PLAN.md. Brainstorming was invoked anyway — asking "which signal source? a/b/c?" — wasting a full round-trip. PLAN.md IS the design. Brainstorming = only when no spec exists anywhere.

B002 [wrap-missing-gsd-docs]:
Rule: Before closing any session, .gsd/phase-[next-task]-PLAN.md MUST exist. If it doesn't, create it before closing. MEMORY.md item 2 must be the exact first atomic step from that file.
Why: If GSD docs are missing at wrap, next session cold-starts on design work — invokes brainstorming, asks questions, loses the round-trip. The wrap creates the track; resurrect runs on it. Fixed Session 120: wrap-session Step 2c made mandatory.

D014 [falkordb-oom-threshold]:
Decision: FalkorDB OOM on 4GB droplet at ~1200 episodes without delta queries + tiered memory. Delta queries (new-only) and graph bounds (hot entities only) are required from launch.
Why: 605 episodes = 200MB, 10k episodes (with indexes, active loop) = ~4.5GB — exceeds 4GB droplet. Mathematical projection validated Feb 19, 2026.

D015 [claudemd-modular-rules]:
Decision: CLAUDE.md root file capped at ~100 lines. Modular rules in .claude/rules/*.md. CC must not modify CLAUDE.md without explicit approval. MEMORY.md is the only autonomous-update target.
Why: At 1,549 lines, all instructions get equal weight — critical rules compete with ASCII art. Session protocol buried at line 400 was reliably skipped. Sweet spot verified at ~2,500 tokens total.

D016 [spend-governor-pre-autonomy]:
Decision: Spend governor (per-model daily token budget + hard shutdown) must be implemented BEFORE autonomous action capability is expanded, not after.
Why: Consciousness loop at 10k episodes with 30% active rate costs $738+/month without caps. Implementing post-autonomy means the system can already run unbounded.

## PROOF Archive (active, verified)

PR001: AC8 LIVE — CC server registered HKCU Run key, port 7891, auto-restart loop. Verified: /health → {"ok":true}.
PR002: Channels bridge operational — bus_post end-to-end confirmed Session 111 (coord_1774063773241_hfep).
PR003: Locked-invariant-guard.py fires exit 2 on unauthorized karma_contract_policy.md edit. SOVEREIGN_APPROVED=1 → exit 0.
PR004: Spine rank patched to Initiate. AC#1 gate: Karma claims Initiate in /v1/chat response.
PR005: Watchdog_extra_patterns.json EXISTS on K2 with 6 PITFALL patterns from CCSession032026A.

## ACTIVE DOCTRINE (load every session)

PLAN before patch: State source_of_truth + evidence + fix_location + verify_cmd + expected_output BEFORE any code change.
Evidence-only done: Never claim fixed without running verify_cmd and showing output.
Scratchpad at discovery: Write to cc_scratchpad.md the moment insight occurs — not batched at session end.
TodoWrite canonical: Read before every action. Update immediately after every sub-step.
Dual-write captures: Every DECISION/PROOF/PITFALL → MEMORY.md + claude-mem save_observation (both required).
