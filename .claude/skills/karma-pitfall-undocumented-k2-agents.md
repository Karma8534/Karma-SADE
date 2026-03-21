---
name: karma-pitfall-undocumented-k2-agents
description: Use when working with K2 agents, cron jobs, or system state. Every K2 cron agent must be in Karma2/map/services.md or it is invisible to next session.
type: feedback
---

## Rule

After creating ANY new K2 cron agent or scheduled script, immediately add it to `Karma2/map/services.md`. Do not wait until session end — add it the moment the agent is verified running.

**Why:** cc_anchor_agent.py (every 3h drift check) and cc_hourly_report.py (every 1h status post) existed in K2's crontab for multiple sessions but were never in any resurrect-loaded file. CC consistently arrived not knowing these agents existed, leading to duplicate work and incorrect system state claims. K2 crontab is not surfaced by resurrect unless gen-cc-brief.py runs. Documented in CCSession032026A (2026-03-20, obs #8652).

**How to apply:** When in doubt about what K2 agents are running: `ssh vault-neo "ssh -p 2223 -l karma localhost 'crontab -l'"`. Before adding a new agent, check if one already exists for that purpose. After adding: update services.md immediately, commit, push.

## Evidence

- CCSession032026A (2026-03-20): CC discovered cc_anchor_agent and cc_hourly_report existed only in K2 crontab, invisible to every prior session.
- Obs #8652 in claude-mem
