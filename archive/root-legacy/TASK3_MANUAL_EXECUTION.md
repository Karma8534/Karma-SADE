# Task 3: Re-Enable Episode Ingestion — Manual Execution Guide

## Current Status
SSH connection to vault-neo (arknexus.net) is timing out. The task cannot be completed through automated SSH from this location.

## What This Task Does
1. Cleans up duplicate Entity nodes created by Session 32's `batch_ingest --skip-dedup`
2. Re-enables episode ingestion in karma-server
3. Allows consciousness loop to observe and THINK on new episodes

## Solution: Execute on Vault-Neo Directly

You must SSH to vault-neo and run the commands manually. Use an SSH session that can sustain long-running operations.

### Option A: One-Step Automated Script (Recommended)

1. **Copy the execution script to vault-neo**:
```bash
scp C:\dev\Karma\task3_execute.sh root@arknexus.net:/tmp/
```

2. **SSH to vault-neo and run the script**:
```bash
ssh vault-neo
cd /tmp
bash task3_execute.sh
```

This script will:
- Create remove_duplicates.py if needed
- Run dry-run to see duplicates
- Delete duplicates with --confirm
- Verify duplicates are gone
- Update server.py to re-enable ingestion
- Rebuild Docker image
- Restart karma-server
- Wait for consciousness cycle
- Verify THINK execution
- Report results

**Expected duration**: 90-120 seconds total (mostly waiting for Docker operations and consciousness cycle)

**Expected final output**:
```
===== TASK 3 EXECUTION COMPLETE =====

Next steps:
1. Commit changes to git: git add karma-core/server.py && git commit -m "feat: Re-enable episode ingestion after duplicate cleanup (Task 3)"
2. Push to main: git push origin main
3. Monitor consciousness.jsonl for THINK entries
```

---

### Option B: Step-by-Step Manual Execution

If the script fails or you need to debug each step:

#### STEP 1: Create/Verify remove_duplicates.py

```bash
ssh vault-neo 'test -f /home/neo/karma-sade/karma-core/scripts/remove_duplicates.py && echo "File exists" || echo "File missing - create it"'
```

If file is missing, copy it:
```bash
scp /c/dev/Karma/karma-core/scripts/remove_duplicates.py root@arknexus.net:/home/neo/karma-sade/karma-core/scripts/
```

#### STEP 2: Run dry-run to identify duplicates

```bash
ssh vault-neo "cd /home/neo/karma-sade && python karma-core/scripts/remove_duplicates.py"
```

**Expected output**:
```
DRY RUN MODE (no changes made)

Would delete N duplicate entities:

  Would delete: entity_id_1       Entity Name 1                  (type)
  Would delete: entity_id_2       Entity Name 2                  (type)
  ...

================================================================================
Summary: Would delete N entities, keep M canonical

Run with --confirm to execute deletion:
  python scripts/remove_duplicates.py --confirm
```

**Document the number N** (duplicates to be deleted)

#### STEP 3: Run with --confirm to actually delete

```bash
ssh vault-neo "cd /home/neo/karma-sade && python karma-core/scripts/remove_duplicates.py --confirm"
```

**Expected output**:
```
DELETING N duplicate entities...

✓ Deleted: entity_id_1       Entity Name 1                  (type)
✓ Deleted: entity_id_2       Entity Name 2                  (type)
...

================================================================================
Summary: Deleted N entities, kept M canonical
```

#### STEP 4: Verify duplicates are gone

```bash
ssh vault-neo "cd /home/neo/karma-sade && python karma-core/scripts/identify_duplicates.py"
```

**Expected output**:
```
DRY RUN MODE (no changes made)
No duplicates found
```

**If duplicates remain**: Stop and investigate. Contact support.

#### STEP 5: Update server.py to re-enable ingestion

```bash
ssh vault-neo 'sed -i "s/ingest_episode_fn=None,.*Disabled: Graphiti has corrupted entities.*/ingest_episode_fn=ingest_episode,  # Re-enabled after duplicate cleanup (Task 3)/g" /opt/seed-vault/memory_v1/karma-core/server.py'
```

**Verify the change**:
```bash
ssh vault-neo "sed -n '1610,1615p' /opt/seed-vault/memory_v1/karma-core/server.py"
```

**Expected output** (line 1612 must show):
```
            ingest_episode_fn=ingest_episode,  # Re-enabled after duplicate cleanup (Task 3)
```

#### STEP 6: Rebuild Docker image

```bash
ssh vault-neo "cd /opt/seed-vault && docker build -t karma-core:latest /home/neo/karma-sade/karma-core/ 2>&1 | tail -20"
```

**Expected output**:
```
Successfully tagged karma-core:latest
```

**If build fails**: Check for SyntaxError in output. Verify server.py was edited correctly.

#### STEP 7: Restart container

```bash
ssh vault-neo "docker stop karma-server && docker rm karma-server"
```

```bash
ssh vault-neo "cd /opt/seed-vault && docker-compose up -d karma-server"
```

**Check startup** (wait 5 seconds):
```bash
ssh vault-neo "docker logs karma-server 2>&1 | tail -30"
```

**Expected**:
```
[GRAPHITI] Client initialized
[SERVER] Karma server ready at 0.0.0.0:8000
```

#### STEP 8: Verify consciousness THINK execution

Wait 60+ seconds, then:

```bash
ssh vault-neo "tail -5 /opt/seed-vault/memory_v1/ledger/consciousness.jsonl | jq '.action'"
```

**Expected** (NOT NO_ACTION):
```
"THINK"
"THINK"
"REFLECT"
...
```

**If still NO_ACTION**: Wait another 60s and check again. Consciousness cycle is 60s.

#### STEP 9: Verify episode ingestion

```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt); curl -s -H 'Authorization: Bearer \$TOKEN' https://hub.arknexus.net/v1/cypher -d '{\"cypher\": \"MATCH (e:Episode) RETURN COUNT(e) as episodes\"}' 2>&1 | jq '.data[0][0]'"
```

**Expected output**:
```
1147
```
(or higher - must be > 0)

---

## After Execution: Commit to Git

Once the script completes successfully on vault-neo:

```bash
cd /c/dev/Karma
git add karma-core/server.py
git commit -m "feat: Re-enable episode ingestion after duplicate cleanup (Task 3, Session 34)"
git push origin main
```

**Verify**:
```bash
git log --oneline -1
```

Should show your commit message.

---

## Troubleshooting

### SSH Connection Timeout
- If `ssh vault-neo` times out, try:
  - Check network connectivity: `ping arknexus.net`
  - Try with explicit timeout: `ssh -o ConnectTimeout=30 root@arknexus.net`
  - Use a cloud terminal (AWS/GCP) if available
  - Contact infrastructure team to verify vault-neo is online

### Duplicates Still Exist After --confirm
- Verify exit code: `echo $?` after running remove_duplicates.py --confirm
- Check Redis connection: `redis-cli -h falkordb ping` (if accessible)
- Check FalkorDB logs: `docker logs falkordb 2>&1 | tail -50`

### Docker Build Fails
- Revert server.py: `git checkout karma-core/server.py`
- Check Python syntax: `python -m py_compile karma-core/server.py`
- Rebuild with verbose output: `docker build -t karma-core:latest /home/neo/karma-sade/karma-core/ --progress=plain`

### Consciousness Still Shows NO_ACTION
- Wait another 60-120 seconds (consciousness cycle may be in progress)
- Check karma-server logs: `docker logs karma-server 2>&1 | grep -i consciousness | tail -20`
- Verify ingestion_fn is enabled: `grep -n 'ingest_episode_fn' /opt/seed-vault/memory_v1/karma-core/server.py`
- Manually trigger consciousness signal: `curl -X POST -H "Authorization: Bearer $(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)" -H "Content-Type: application/json" -d '{"signal":"reset","reason":"Manual reset for Task 3"}' https://hub.arknexus.net/v1/consciousness`

---

## Success Criteria Checklist

- [ ] remove_duplicates.py exists on vault-neo
- [ ] Dry-run shows duplicates found (N > 0)
- [ ] --confirm mode runs successfully
- [ ] identify_duplicates.py shows "No duplicates found"
- [ ] server.py line 1612 changed from `ingest_episode_fn=None` to `ingest_episode_fn=ingest_episode`
- [ ] Docker image rebuilt successfully
- [ ] karma-server container restarted
- [ ] consciousness.jsonl shows THINK actions (not NO_ACTION)
- [ ] FalkorDB episode count > 0
- [ ] Changes committed to git main branch

---

## Files Involved

**Local** (C:\dev\Karma):
- `karma-core/scripts/remove_duplicates.py` — Duplicate deletion script
- `karma-core/scripts/identify_duplicates.py` — Verification script
- `karma-core/server.py` — Line 1612 changed
- `task3_execute.sh` — Full automation script (optional)

**Remote** (vault-neo):
- `/home/neo/karma-sade/karma-core/scripts/remove_duplicates.py` — Must exist
- `/opt/seed-vault/memory_v1/karma-core/server.py` — Must be updated
- `/opt/seed-vault/memory_v1/ledger/consciousness.jsonl` — Verification checkpoint
- `/opt/seed-vault/memory_v1/ledger/memory.jsonl` — Episode ledger (read-only)

**Docker**:
- `karma-core:latest` image (rebuilt)
- `karma-server` container (restarted)

---

## Why This Task Matters

**Session 32 Problem**:
- `batch_ingest --skip-dedup` created duplicate Entity nodes in FalkorDB
- This corrupted the graph, making consciousness loop unreliable
- Decision: Disable ingestion until duplicates are cleaned

**Session 34 Solution** (This Task):
- Remove duplicate entities from FalkorDB
- Re-enable real-time ingestion
- Consciousness loop can now observe and THINK on new episodes

**Unblocks**:
- Consciousness THINK phase execution (blocked in Session 33)
- Episode ingestion pipeline (blocked in Session 32)
- Resurrection Protocol Step 3 (depends on consciousness working)

---

## Expected Outcome

After successful execution:

1. **consciousness.jsonl** grows with THINK entries (not NO_ACTION)
2. **New episodes** in memory.jsonl are ingested to FalkorDB
3. **Consciousness loop** becomes active (60s THINK cycles)
4. **Phase 1 Step 2** verified complete (consciousness THINKING)
5. **Unblocks** Phase 1 Step 3 (Resurrection Protocol)

---

## Next Session Context

When the next session starts, update MEMORY.md with:
```markdown
## Session 34: Task 3 Completion — Re-Enable Episode Ingestion ✅ COMPLETE

**What was completed**:
- Duplicates removed: [N] entities deleted, [M] canonical kept
- server.py updated: ingest_episode_fn re-enabled (line 1612)
- karma-core image rebuilt and restarted
- consciousness loop now THINKING (THINK entries in consciousness.jsonl)
- Episode ingestion verified working (FalkorDB count [N])

**Verification status**:
- ✅ Q1 (end-to-end test): consciousness loop THINKS on new episodes
- ✅ Q2 (user can verify): tail -5 consciousness.jsonl | jq '.action' shows THINK
- ✅ Q3 (no side effects): All previous systems still working, no new errors
- ✅ Q4 (reproducible): Any new session can run remove_duplicates.py again if needed

**Git commits**:
- [hash] feat: Re-enable episode ingestion after duplicate cleanup (Task 3)

**Next steps for Session 35**:
- [ ] Step 1: Verify Phase 1 foundation (UI, consciousness, resurrection) all working
- [ ] Step 2: Build and test K2 resumption mechanism
- [ ] Step 3: Implement consciousness proposal feedback loop
```

