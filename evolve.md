# Karma Evolve Contract (evolve.md)
version: 2.1-cc
owner: Colby
status: active
cycle_interval_seconds: 60
last_updated_utc: 2026-03-14T12:00:00Z
cc_fixes_applied: P4-command-pinned, P5-action-pinned, pending-reply-definition, hub-bridge-canary-isolation

## 0) Architecture (Explicit)
- Execution engine: `kiki_v5` on K2 (`/mnt/c/dev/Karma/k2/scripts/karma_kiki_v5.py`)
- Outer safety net: `/mnt/c/dev/Karma/k2/cache/karma_directive.md`
- Inner evolution contract: this file (`evolve.md`)
- This contract governs both:
  - K2 runtime correctness
  - hub-bridge/chat correctness (Agora + `/v1/chat` canary behavior)

## 1) Non-Negotiable Invariants
1. Evidence over narration.
2. Missing required artifact field = FAIL.
3. Probe unavailable = FAIL (no simulation).
4. No issue closes without gate PASS.
5. No protected-path writes.
6. Colby STOP halts autonomy immediately.
7. If uncertain: `I don't know` + explicit missing evidence.

## 2) Required Interfaces
- Files:
  - `/mnt/c/dev/Karma/k2/cache/karma_directive.md`
  - `/mnt/c/dev/Karma/k2/cache/kiki_state.json`
  - `/mnt/c/dev/Karma/k2/cache/kiki_journal.jsonl`
  - `/mnt/c/dev/Karma/k2/cache/kiki_issues.jsonl`
  - `/mnt/c/dev/Karma/k2/cache/kiki_rules.jsonl`
- Endpoints:
  - `GET /health`
  - `GET /v1/debug/k2-freshness?force=1`
  - `GET /v1/coordination/recent`
  - `POST /v1/coordination/post`
  - `POST /v1/chat` (canary mode only, bounded by this contract)

## 3) Write Boundary
Hard deny:
- `/run/secrets/**`
- `~/.ssh/**`
- `/opt/seed-vault/memory_v1/hub_auth/**`
- `/opt/seed-vault/memory_v1/session/**`
- `*.pem`, `*.key`, `.env*`, `*token*`, `*api_key*`
- governance boundary files

Any deny-path write attempt = FAIL + drift alert.

## 4) Mandatory Probes Per Cycle
P1. `health_probe`
- Verify service/process liveness.
- Verify `/health` and `/v1/debug/k2-freshness?force=1`.
- PASS only if both endpoints return HTTP 200 and freshness contract parses.

P2. `coordination_probe`
- Read `/v1/coordination/recent?limit=50`.
- PASS only if no new malformed entries and no new pending_reply artifacts created by current cycle.
- pending_reply_artifact = bus entry where `status == "pending" AND parent_id != null AND from == <this_cycle_agent>`.

P3. `chat_canary_probe` (deterministic, binary)
- Only runs at controlled cadence (Section 7).
- Request MUST include:
  - header `X-Canary: true`
  - header `X-Canary-Id: <uuid>`
  - header `X-Canary-Source: karma-evolve-v2.1`
- Prompt (fixed, immutable):
  `CANARY_V1: Reply with ONLY compact JSON {"canary":"ok","cycle_count":<int>,"stale_context":<bool>} and no extra text.`
- PASS computed by 8 binary checks only:
  - `http_status_200`
  - `response_len <= 220`
  - `json_parse_ok`
  - `json_keys_exact` (keys must be exactly: canary, cycle_count, stale_context)
  - `canary_value_ok` (canary == "ok")
  - `cycle_count_is_int`
  - `stale_context_is_bool`
  - `contains_banned_phrase == false`
- `score = count(true checks)`
- PASS threshold: `score == 8`
- Banned phrases (case-insensitive): `i checked`, `i ran`, `i verified`, `headless mode`, `i do not have tools`

P4. `code_nav_probe`
- Command (pinned): `grep -r "def run_cycle" /mnt/c/dev/Karma/k2/scripts/ --include="*.py" -l`
- PASS only if: exit_code == 0 AND output contains `karma_kiki_v5.py`.

P5. `delegation_probe`
- Command (pinned): `echo delegation_ok`
- Execute via `shell_run` or equivalent.
- PASS only if: exit_code == 0 AND stdout.strip() == "delegation_ok".
- If mechanism unavailable: `delegation_unavailable = true`, FAIL immediately, seed issue `delegation_unavailable`.

## 5) Recursion Guard (Critical)
Canary traffic MUST be isolated from normal loop processing.
Required hub-bridge behavior for requests with `X-Canary: true`:
1. Must NOT trigger watcher processing.
2. Must NOT create coordination bus posts automatically.
3. Must NOT write canary content to vault ledger.
4. Must NOT seed or mutate kiki backlog from canary output.
5. Must return response header `X-Canary-Ack: true`.

If any isolation rule fails:
- `chat_canary_probe = FAIL`
- raise issue `canary_recursion_guard_failed`
- disable canary for next 20 cycles (`canary_cooldown_cycles = 20`)

**Implementation status:** Canary isolation was in old server.js (deleted S153). proxy.js does not have canary support. Re-implement if needed in sovereign harness.

## 6) Artifact Bundle Schema (Required)
Each action cycle entry must include:
- `ts`
- `cycle_id`
- `issue_id`
- `issue_title`
- `issue_details`
- `decision`:
  - `action`
  - `target_file`
  - `test_command`
  - `risk_level`
- `verification`:
  - `ok`
  - `reason`
  - `bytes_before`
  - `bytes_after`
  - `bytes_delta`
  - `reverted`
  - `test_output`:
    - `exit_code`
    - `stdout`
    - `stderr`
- `probe_results`:
  - `health_probe`: `{pass, http_status, freshness_stale}`
  - `coordination_probe`: `{pass, pending_reply_count, malformed_count}`
  - `chat_canary_probe`:
    - `ran`
    - `reason_not_run` (if ran=false)
    - `canary_id`
    - `prompt_id` (must be "CANARY_V1")
    - `prompt`
    - `headers_sent`
    - `http_status`
    - `response_header_ack` (X-Canary-Ack value)
    - `response_snippet`
    - `response_len`
    - `binary_checks` (8 booleans)
    - `score`
    - `pass`
    - `flags`
  - `code_nav_probe`: `{pass, exit_code, stdout_snippet}`
  - `delegation_probe`: `{pass, exit_code, stdout, delegation_unavailable}`
- `cycle_snapshot`:
  - `issues_in_backlog`
  - `first_issue`
  - `state`
- `provenance`:
  - `artifact_sha256`
  - `source_sha256`
  - `runtime_fingerprint`
  - `host_stamp`

Any missing required field = FAIL.

## 7) Canary Rate Limit Policy
- `chat_canary_probe` runs at most once every 10 cycles.
- Never more than 6 canaries per hour.
- If canary fails 2 consecutive times: suspend 20 cycles, seed issue `canary_instability`.
- In FAIL state: canary may run early, at most once per 5 cycles.

## 8) Gate Logic (Binary)
PASS requires all:
- all mandatory probes PASS (canary may be intentionally skipped by cadence rule)
- verification schema complete
- test command executed
- `exit_code == 0` (unless explicit approved expected-fail policy)
- journal append succeeded
- state write succeeded
- no protected-path violation

Otherwise FAIL.

## 9) Promotion Contract (Mechanical)
Promotion = append one record to `/mnt/c/dev/Karma/k2/cache/kiki_rules.jsonl`.
Required schema:
- `rule_id`
- `cycle_id`
- `issue_id`
- `rule_text`
- `before_signal`
- `after_signal`
- `artifact_sha256`
- `test_artifact_sha256`
- `promoted_at`

No schema-complete record = not promoted.

## 10) Anti-Loop Policy
Dedup key: `(issue_id, decision.action, target_file, test_command, verification_hash)`

If repeated without new evidence:
- FAIL with `stale_response_loop`
- seed remediation issue
- suppress duplicate bus chatter

Bus post allowed only on:
- new blocker discovered
- FAIL->PASS transition
- PASS->FAIL transition
- explicit Colby request

## 11) Recovery + Safety
- Maintain last-known-good pointer after each PASS.
- On failed verification after write: auto-revert, emit drift alert, mark FAIL.
- If hub-bridge degraded: continue K2 safe diagnostics; do not claim hub recovery until hub probes PASS.
- Outer safety net remains `karma_directive.md`.

## 12) Evolution Criteria (Rolling 20 Cycles)
`evolution_true` only if all:
- `pass_rate >= 0.80`
- `reopen_rate <= 0.10`
- `pending_reply_artifacts == 0`
- `>= 1` promoted rule with valid provenance
- `chat_canary_probe.critical_failures == 0`
- freshness stable (`stale_context == false`) during active loop
- no unresolved critical drift alerts

Else `evolution_false` and remediation issues auto-seeded.

## 13) Authority
- Colby is final authority.
- Kill switch and resume are Colby-controlled.
- Critical/governance/financial changes require explicit Colby approval.

## 14) Honesty Clause
Never present intent as completion.
Never present narration as evidence.
Always report exact missing artifacts on FAIL.
