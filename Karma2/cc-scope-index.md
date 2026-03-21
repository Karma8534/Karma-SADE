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
