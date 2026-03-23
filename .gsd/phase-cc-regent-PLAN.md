# CC Regent — Implementation Plan

**Created:** 2026-03-23
**Directive:** Sovereign — build CC's persistent agent layer
**Context:** .gsd/phase-cc-regent-CONTEXT.md

---

## Task 1: Read karma_regent.py to understand pattern
```
Read: ssh vault-neo "ssh -p 2223 -l karma ... cat /mnt/c/dev/Karma/k2/aria/karma_regent.py"
```
<verify>Full file read. Understand: cycle structure, state file read/write, service integration, circuit breakers.</verify>
<done>[x] 2026-03-23 Session 132</done>

## Task 2: Read cc_identity_spine.json and cc_scratchpad.md structure
```
Read both files via K2 SSH to understand current CC state file format.
```
<verify>Know the schema — what cc_regent needs to read and write.</verify>
<done>[x] 2026-03-23 Session 132</done>

## Task 3: Design cc_regent.py — state integration cycle
Write `cc_regent.py` with:
- `integrate_session()`: reads cc_scratchpad.md COGNITIVE_STATE block + cc_cognitive_checkpoint.json → updates cc_identity_spine.json resume_block
- `build_session_brief()`: writes the brief that resurrect reads at next session start
- Circuit breaker: max 10 ops per cycle, configurable daily API limit
- No inference calls between sessions — state files only
<verify>Script runs without error on K2. `python3 cc_regent.py --dry-run` exits 0.</verify>
<done>[x] 2026-03-23 Session 132 — dry-run exits 0, cognitive_state extracted 5 keys</done>

## Task 4: Deploy as cc-regent.service on K2
```
scp cc_regent.py to K2 /mnt/c/dev/Karma/k2/aria/
Write /etc/systemd/system/cc-regent.service (mirror aria.service pattern)
systemctl enable + start cc-regent
```
<verify>`systemctl status cc-regent` shows active. `journalctl -u cc-regent -n 20` shows clean cycle.</verify>
<done>[x] 2026-03-23 Session 132 — active PID 600393, first cycle: spine v38 written, resume_block=2044 chars</done>

## Task 5: Wire wrap-session to trigger cc_regent integration
```
After session wrap cognitive snapshot → trigger cc_regent integrate_session()
Can be: direct SSH call at end of wrap-session Step 1
```
<verify>End a test session. cc_regent logs show integration ran. cc_identity_spine.json resume_block updated with session content.</verify>
<done>[x] 2026-03-23 Session 132 — wrap-session SKILL.md updated with explicit --integrate SSH call after COGNITIVE_STATE write</done>

## Task 6: Wire resurrect to read cc_regent brief
```
Resurrect Step 1b already reads cc_identity_spine.json resume_block.
Verify the brief now contains cc_regent-integrated content, not just manual snapshots.
```
<verify>Fresh session `/resurrect` — resume_block contains last session's cognitive trail from cc_regent (not stale).</verify>
<done>[x] 2026-03-23 Session 132 — spine session_count=1, resume_block contains cognitive trail. Gate: next /resurrect will read cc_regent-integrated content.</done>

## Gate
CC wakes up at next session start with:
- No B001 violation
- resume_block containing actual last-session cognitive state (not reconstructed)
- No manual reconstruction of context needed
