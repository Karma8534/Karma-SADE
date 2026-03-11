# Karma SADE Session Summary (Latest)

**Date**: 2026-03-11
**Session**: 84 (84b/84c/84d)
**Focus**: K2 agency — MANDATORY state-write, redundancy cache, shell_run tool (Karma direct shell access)

---

## What Was Built

### 1. MANDATORY K2 State-Write Protocol (84b)
Prominent MANDATORY section added to system prompt. Karma calls `aria_local_call` after any DECISION/PROOF/PITFALL/DIRECTION/INSIGHT. System prompt: 20,780 → 23,085 chars. Deployed via git pull + docker restart.

### 2. K2 Redundancy Cache (84c)
`k2/sync-from-vault.sh` pull/push/status. Pull cron 6h: rsync identity/invariants/direction + ledger tail-500. Push cron 1h: POST observations to /v1/ambient (token fetched live). aria.service starts with identity loaded from `/mnt/c/dev/Karma/k2/cache/`. `/health` endpoint returns cache_age_hours + vault_reachable. Drop-in `Environment=HOME=/home/karma` required in aria.service systemd config.

### 3. shell_run Tool (84d)
`/api/exec` endpoint in aria.py (K2:7890): `subprocess.run(command, shell=True, timeout=30)`, gated by X-Aria-Service-Key. `shell_run(command)` added to hub-bridge TOOL_DEFINITIONS + handler (calls aria /api/exec). vault-neo public key added to K2 authorized_keys. hub-bridge v2.11.0. Reverse tunnel user is `karma@localhost:2223` (NOT neo).

## What's Live
- Karma can: `shell_run("systemctl status aria")`, `shell_run("cat /mnt/c/dev/Karma/k2/cache/.last_sync")`
- K2 cache syncing every 6h (pull) and 1h (push)
- MANDATORY state-write coaching in every Karma response context

## What's Open
- PRICE_CLAUDE in hub.env: still Haiku rates (needs Sonnet $3.00/$15.00)
- K2 ownership/agency breakthrough not yet checkpointed to ledger
- Prompt caching not yet implemented

## Next Session Step 1
Test shell_run end-to-end: open hub.arknexus.net deep mode → ask Karma to shell_run systemctl status aria → verify K2 output returned.
