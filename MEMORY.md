<!-- Last dream: 2026-04-02 Session 156 — MEMORY.md consolidated, stale sections purged -->

# Karma SADE — Active Memory

## Current State
- **Active task:** Bug fixes from Colby screenshot (archon alert stale date, MEMORY btn, kiki approval, bus redlines)
- **Session:** 156 cont. (2026-04-02)
- **Phase:** Sprints 1-5 SHIPPED. Sprint 6 active. Baseline 22 PASS.
- **Baseline:** 22 PASS (Appendix G). Sprint 6 tasks 7-5 through 7-10 deployed.

## Session 156 Continued — Bug Fixes
- **Archon Alert stale 03/22 FIXED**: Blockers 10/11/13/21 had no ~~ strikethrough. Added ~~ to STATE.md + cc_context_snapshot.md. Now only items 16/17/18 (genuinely open) appear in archon alerts.
- **Bus redlines ACKed**: 4 stale blocking ARCHON ALERTS acknowledged (coord_1775138720936_dcb1 + 3 earlier).
- **MEMORY button**: AGORA at localhost:37778 is fully accessible without auth (all /api/* endpoints return 200). Issue appears resolved — no auth checks in viewer-bundle.js, CLAUDE_MEM_CLAUDE_AUTH_METHOD=cli.
- **Kiki pulse / hourly approval FIXED**: proxy.js autoApproveKarmaEntries() extended from `from==="karma"` to all non-blocking, non-task messages. Deploy: git pull + scp proxy.js + docker restart.

## Architecture (S145 — locked)

### Five Layers
```
SPINE ── vault ledger + FalkorDB + FAISS + MEMORY.md + persona + claude-mem (vault-neo)
ORCHESTRATOR ── proxy.js (thin door) + cc_regent + karma-regent + resurrect
CORTEX ── qwen3.5:4b 32K on K2 (primary) / P1 (fallback) — working memory, NOT identity
CLOUD ── CC --resume via Max ($0/request)
CC ── Claude Code on P1 — execution layer
```

### Sovereign Harness (S153+)
```
Browser/Electron → proxy.js (vault-neo:18090, ~600 lines)
                 → cc_server_p1.py (P1:7891) → cc --resume ($0)
                 → K2:7891 (failover)
```

### Runtime Ground Truth
| Machine | Model | Context | Speed | Role |
|---------|-------|---------|-------|------|
| K2 (192.168.0.226) | qwen3.5:4b | 32K | 58 tok/s | PRIMARY cortex |
| P1 (PAYBACK) | qwen3.5:4b | 32K | 58 tok/s | FALLBACK cortex |

## Vesper Pipeline (live)
- self_improving: true, total_promotions: 1284+
- Spine v1261+, 15+ stable patterns
- Pipeline: watchdog (10min) / eval (5min) / governor (2min) — all active

## Open Blockers
- **B4:** CC server reboot survival unverified (Gap 7 — schtasks needed)
- **Chrome 146 CDP:** Phase 5 (deferred-by-rule)

## Critical Pitfalls (NEVER REPEAT)
- **P093:** cortex nohup bypass loses OLLAMA_URL — always use systemd service
- **P089:** NEVER declare PASS from documents — live test every claim
- **P058:** Before writing hierarchy/identity content, re-read canonical source, copy exact text
- **P059:** PLAN.md must contain EXACTLY ONE plan — dead plans archived immediately
- **P065:** unified.html NEVER reimplements CC features in JavaScript
- **S145:** Cortex is working memory, NOT canonical identity. Identity = spine.

## Infrastructure
- P1 + K2: same machine, i9-185H, 64GB RAM, RTX 4070 8GB
- K2 = WSL2. Ollama runs on Windows. From WSL, use gateway IP (172.22.240.1:11434) NOT localhost
- Tailscale: P1=100.124.194.102, K2=100.75.109.92, droplet=100.92.67.70
- SSH alias: vault-neo
- Git ops: PowerShell only (Git Bash has persistent index.lock)
- FalkorDB graph: `neo_workspace` (NOT `karma`)
- Hub token: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt`
- THE ONLY PLAN: `docs/ForColby/nexus.md` — APPEND ONLY per Sovereign directive

## Memory Index
- [project_sade_doctrine.md](project_sade_doctrine.md) — SADE execution doctrine
- [project_cc_ascendant_identity.md](project_cc_ascendant_identity.md) — CC/Julian identity
- [user_colby.md](user_colby.md) — Colby profile
- [feedback_document_errors.md](feedback_document_errors.md) — Document all errors
- [feedback_live_verification_before_diagnosis.md](feedback_live_verification_before_diagnosis.md) — Verify live
- [feedback_stop_planning_start_building.md](feedback_stop_planning_start_building.md) — Build immediately
- [project_family_doctrine.md](project_family_doctrine.md) — Family doctrine
- [feedback_dead_plan_critical.md](feedback_dead_plan_critical.md) — ONE active plan only
- [feedback_forensic_verification.md](feedback_forensic_verification.md) — Live test every claim
- [reference_forcolby_snapshot.md](reference_forcolby_snapshot.md) — S145 architecture snapshot

## Session 156 (2026-04-02) — System State Audit + Sprint 6
- Appendix F: 17→22 PASS after fixes. Appendix G appended to nexus.md.
- Cortex OLLAMA_URL fixed (nohup→systemd, gateway IP). P093.
- 23 zombie karma_persistent killed. KarmaProcessWatchdog disabled.
- Sprint 6 Tasks 7-5 through 7-10 LIVE on K2 cortex (tier classification deployed).
- Boot trigger added to KarmaSovereignHarness schtask (#15 PASS).
- Memory search response format fixed in cc_server_p1.py.
- MEMORY.md consolidated 300→75 lines.

- #20-22 FIXED: /agents-status endpoint + AgentTab shows MCP (2), Skills (12), Hooks (6 events)
- Task 7-11 already done in governor (memcube.tier=stable on promotion)
- Next.js rebuilt with updated ContextPanel

## Next Session Starts Here
1. `/resurrect`
2. Smoke test end-to-end — verify #20-22 in browser after deploy
3. Only remaining: #17 Voice (deferred), #24 Video (deferred), #15 Reboot (deferred)
4. THE ONLY PLAN is `docs/ForColby/nexus.md` — APPEND ONLY
