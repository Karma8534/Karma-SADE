# PLAN: Ambient Layer Tier 1 — Atomic Task Breakdown

**Phase:** Tier 1 (Git Hooks → /v1/ambient Capture)
**Status:** Ready to Execute
**Created:** 2026-03-03 (Session 56)
**Plan owner:** Claude Code + Karma

---

## Task 1: Verify Hub-Bridge Reachability

```xml
<task type="verify">
<name>Verify hub-bridge is reachable from P1</name>
<action>
Ping hub-bridge API from local machine.
Test endpoint: https://hub.arknexus.net/health (if exists) or /v1/chat
Expected: 200 OK response (proves droplet is up)
</action>
<verify>
curl -s https://hub.arknexus.net/v1/chat -X OPTIONS
Returns: 200 OK (or similar valid response, not 502/503)
</verify>
<done>
Hub-bridge responds to requests from P1 network.
No connectivity issues between local machine and vault-neo.
</done>
</task>
```

---

## Task 2: Sync Local Hooks to Droplet

```xml
<task type="deploy">
<name>Copy .git/hooks/post-commit to vault-neo</name>
<action>
Use scp to copy hook from local repo to droplet canonical location.
Source: .git/hooks/post-commit (local)
Dest: /opt/seed-vault/memory_v1/hub_bridge/.git/hooks/post-commit (droplet)
Ensure executable permissions: chmod +x post-commit
</action>
<verify>
ssh vault-neo "ls -la /opt/seed-vault/memory_v1/hub_bridge/.git/hooks/post-commit"
Returns: file exists and is executable (-rwxr-xr-x)
</verify>
<done>
Hook exists on droplet with correct permissions.
</done>
</task>
```

---

## Task 3: Sync Session-End Hook to Droplet

```xml
<task type="deploy">
<name>Copy .claude/hooks/session-end-verify.sh to vault-neo</name>
<action>
Use scp to copy session verification hook to droplet.
Source: .claude/hooks/session-end-verify.sh (local)
Dest: /opt/seed-vault/memory_v1/hub_bridge/.claude/hooks/session-end-verify.sh (droplet)
Ensure executable permissions: chmod +x session-end-verify.sh
</action>
<verify>
ssh vault-neo "ls -la /opt/seed-vault/memory_v1/hub_bridge/.claude/hooks/session-end-verify.sh"
Returns: file exists and is executable (-rwxr-xr-x)
</verify>
<done>
Session verification hook deployed to droplet.
</done>
</task>
```

---

## Task 4: Local Test — Trigger Hook Manually

```xml
<task type="test">
<name>Make a test commit to trigger post-commit hook</name>
<action>
Create a small test file in local repo.
Commit with message: "test: GSD workflow + Tier 1 hook verification"
Expected: Hook fires → sends POST to https://hub.arknexus.net/v1/ambient
Monitor: Check hub-bridge logs for /v1/ambient POST receipt
</action>
<verify>
1. Commit succeeds locally (git status shows clean)
2. Hook fires (check local .git/hook-failures.log for errors OR check hub logs for receipt)
3. Hub-bridge receives POST (grep /v1/ambient in hub-bridge logs)
</verify>
<done>
Local commit successfully triggered hook.
Hub-bridge received POST to /v1/ambient.
Data flowed from P1 → hub-bridge confirmed.
</done>
</task>
```

---

## Task 5: Verify Ledger Entry Created

```xml
<task type="verify">
<name>Check vault ledger for new ambient entry</name>
<action>
SSH to vault-neo.
Query ledger: tail -5 /opt/seed-vault/memory_v1/ledger/memory.jsonl | grep "git-commit"
Expected: Latest entry has type: "ambient", source: "git-commit", commit metadata
</action>
<verify>
ssh vault-neo "tail -5 /opt/seed-vault/memory_v1/ledger/memory.jsonl | jq 'select(.type==\"ambient\")'"
Returns: Valid JSON with ambient type, commit hash, message, files_changed
</verify>
<done>
Ledger contains new ambient capture entry.
Entry has correct schema and content.
Data persisted from hub-bridge → vault-api → ledger confirmed.
</done>
</task>
```

---

## Task 6: Test /v1/context Query

```xml
<task type="test">
<name>Query /v1/context to retrieve ambient captures</name>
<action>
Call /v1/context endpoint (if implemented).
If not implemented, query ledger manually: grep "ambient" /opt/seed-vault/memory_v1/ledger/memory.jsonl
Expected: Retrieve git commit captures from recent ambient entries
</action>
<verify>
Either:
- curl https://hub.arknexus.net/v1/context → Returns recent ambient entries (if endpoint exists)
- OR ssh vault-neo "grep 'ambient' /opt/seed-vault/memory_v1/ledger/memory.jsonl | tail -3"
Returns: Ambient captures visible and retrievable
</verify>
<done>
Ambient captures are queryable from ledger.
Next session can call /v1/context and see "last commits were: ..."
</done>
</task>
```

---

## Task 7: Document Results + Update State

```xml
<task type="admin">
<name>Create phase-tier1-SUMMARY.md and update STATE.md</name>
<action>
Document all test results in .gsd/phase-tier1-SUMMARY.md:
- What worked
- What failed (if any)
- Token usage (how many tokens this phase cost)
- Blockers discovered
- Lessons learned

Update .gsd/STATE.md:
- Mark Tier 1 as COMPLETE or BLOCKED
- Update "Current blockers" section
- Add decision log entry
</action>
<verify>
- phase-tier1-SUMMARY.md exists and is complete
- STATE.md updated with Tier 1 status
- Both files staged for commit
</verify>
<done>
Phase documentation complete.
Session 56 work fully documented.
Ready for next session to resume from Tier 1 results.
</done>
</task>
```

---

## Execution Order

**Wave 1 (Sequential):**
1. Task 1: Verify reachability
2. Task 2: Sync post-commit hook
3. Task 3: Sync session-end hook

**Wave 2 (Sequential):**
4. Task 4: Local commit test
5. Task 5: Verify ledger entry

**Wave 3 (Final):**
6. Task 6: Test /v1/context
7. Task 7: Document results

**Dependency:** Each task must pass before next starts. If any task fails, STOP and document failure in summary.

---

## Success Criteria (Full Phase)

✅ **COMPLETE** when:
- All 7 tasks pass
- No blocking errors
- Ledger has ambient entries
- /v1/context retrieves captures successfully
- Documentation updated

🛑 **BLOCKED** if:
- Hub-bridge unreachable (Task 1 fails)
- SSH to vault-neo fails
- Ledger schema mismatch
- /v1/ambient endpoint returns errors (log and continue)

---

**Created:** 2026-03-03T01:50:00Z
**Owner:** Claude Code + Karma
**Ready to execute:** YES
