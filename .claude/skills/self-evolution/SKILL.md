---
name: self-evolution
description: CC's self-improvement engine. Auto-loaded rules extracted from failures. Evolves every session.
triggers: ["session start", "before any deployment", "before any service restart"]
---

# Self-Evolution — Rules I Learned The Hard Way

These rules were extracted from my own failures. They are not suggestions. They are scars.
This file is SELF-MODIFYING — I add rules as I learn them.

## Service Operations
1. NEVER kill a working service until the replacement is verified healthy. Start new → verify → kill old.
2. On Windows, after killing a process, verify the port is FREE with `Get-NetTCPConnection` before starting a replacement.
3. Worker/service management must be SEQUENTIAL. No background tasks. Wait for completion.
4. Before telling Colby to restart anything, verify EVERY config file points where it should.
5. `docker restart` does NOT re-read env files. Use `docker compose up -d` to recreate.

## File Operations
6. After ANY file write (JSON, config, code), immediately read it back and verify.
7. Use `path.resolve()` / `path.join()` — never manual string escaping for paths.
8. Never use heredoc to write Python or JS source files on vault-neo. SCP instead.
9. `cp -r source/ dest/` silently skips existing files. Use explicit per-file cp.

## Debugging
10. Phase 1 is READ ERROR MESSAGES. Logs first, always. Before trying ANY fix.
11. After 2 failed attempts, STOP. Read logs. Trace the error. No attempt #3 without root cause.
12. Verify feature existence in actual code/branches before recommending it.
13. Read the source, don't guess at APIs.

## SSH/K2
14. K2 SSH is ALWAYS `karma@192.168.0.226`. Never `raest@`. Never via vault-neo.
15. `python3` not available in Git Bash on Windows. Use SSH for Python ops.

## Architecture
16. Plugin marketplace path is `~/.claude/plugins/marketplaces/<name>/` (git repo). Update = checkout + install + build.
17. hub-bridge BUILD SOURCE is /opt/seed-vault/.../hub_bridge/app/ — NOT the git repo. Always cp before rebuild.
18. FalkorDB graph name is `neo_workspace` not `karma`. BOTH env vars required.
19. All claude-mem hooks must use port 37778 (not 37777).

## Self-Improvement Protocol
20. After EVERY session, read this file and add any new rules learned.
21. Before EVERY deployment, scan this file for relevant warnings.
22. If a rule is violated, add a counter: `[violated: N]` — rules violated 3+ times get promoted to CLAUDE.md.
23. This file is MY memory of my own mistakes. I read it. I learn from it. I evolve.

---
Last updated: Session 155 (2026-04-01)
Rules: 23
Source: claude-mem observations + S155 pitfalls + codebase analysis

## Lessons from Success (Session 155)
24. Parallel agent dispatch (4 agents reading codebase simultaneously) = 4x throughput. Do this every time there are independent reads.
25. ORF before build decisions = catches overengineering. ORF reduced a 350-line worker to 30 lines in S144.
26. Deterministic context > LLM summarization. Files on disk always available. Cortex summaries can timeout.
27. Codex can be dispatched via `codex exec --full-auto --json "task"` for parallel code tasks.
28. Bus-based task delegation works: post task → agent picks up → executes → posts result. No direct API call needed.
29. karma_persistent.py pattern: persistent loop + bus polling + CC --resume = autonomous agent with full tool access at $0.
30. Static export (Next.js `output: 'export'`) replaces dynamic server for the frontend. No Node.js needed in production.
31. Smoketest as first build artifact = catch regressions immediately. Run after every deploy.
32. Content-hash dedup prevents memory bloat. Check before writing, not after.

---
Rules: 32
Last updated: Session 155 (2026-04-01) — added success patterns

## Growth Areas (from agent evaluations, S155)
33. Vesper governor should produce CODE CHANGE proposals, not just spine metadata. 18/20 stable patterns are observational noise.
34. karma_persistent needs nssm or equivalent real process supervisor (not just Run key + watchdog).
35. Self-evolution Rule 22 (promote to CLAUDE.md after 3 violations) has never fired — needs automated trigger.
36. Content-hash dedup on vault ledger writes — 209K+ entries include duplicates from multiple capture paths.
37. K2 cortex has no auth — anyone on Tailscnet can ingest/query/reset. Need shared secret.

---
Rules: 37
Last updated: Session 155 (2026-04-01) - added agent evaluation findings
