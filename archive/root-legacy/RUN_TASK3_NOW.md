# RUN TASK 3 NOW — Quick Start Guide

## The Challenge

Session 32 corrupted FalkorDB with duplicates. Episode ingestion is disabled. Consciousness loop cannot THINK.

**This task fixes it.**

---

## How to Run (30 seconds to execute, 2 minutes to complete)

### STEP 1: Copy Script to Vault-Neo

From your local machine:
```bash
scp C:\dev\Karma\task3_execute.sh root@arknexus.net:/tmp/
```

### STEP 2: SSH and Execute

```bash
ssh vault-neo
bash /tmp/task3_execute.sh
```

That's it. The script does everything:
1. Creates remove_duplicates.py
2. Identifies duplicates (dry-run)
3. Deletes duplicates (--confirm)
4. Verifies they're gone
5. Updates server.py
6. Rebuilds Docker image
7. Restarts karma-server
8. Waits for consciousness cycle
9. Verifies THINK execution

**Total execution time**: ~90-120 seconds

---

## What Happens During Execution

```
[STEP 1] Creating remove_duplicates.py...
✓ remove_duplicates.py created

[STEP 2] Running dry-run to identify duplicates...
✓ Dry-run completed (exit code: 0)
DRY RUN MODE (no changes made)

Would delete 47 duplicate entities:

  Would delete: entity_12345     Alice                          (person)
  Would delete: entity_12346     Bob Smith                      (person)
  ...

Summary: Would delete 47 entities, keep 1234 canonical

[STEP 3] Running with --confirm to delete duplicates...
✓ Deletion completed (exit code: 0)
DELETING 47 duplicate entities...

✓ Deleted: entity_12345     Alice                          (person)
✓ Deleted: entity_12346     Bob Smith                      (person)
...

Summary: Deleted 47 entities, kept 1234 canonical

[STEP 4] Verifying duplicates are removed...
✓ Verification completed (exit code: 0)
No duplicates found
✓ Confirmed: No duplicates remain

[STEP 5] Updating server.py to re-enable ingestion...
✓ server.py updated

[STEP 5-VERIFY] Verifying server.py change...
            ingest_episode_fn=ingest_episode,  # Re-enabled after duplicate cleanup (Task 3)

[STEP 6] Rebuilding karma-core Docker image...
✓ Docker image rebuilt successfully

[STEP 7] Stopping old karma-server container...
✓ Old container removed

[STEP 8] Starting new karma-server container...
✓ Container started

[STEP 8-VERIFY] Checking container startup logs...
[GRAPHITI] Client initialized
[SERVER] Karma server ready at 0.0.0.0:8000

[STEP 9] Waiting for consciousness cycle (60 seconds)...

[STEP 9-VERIFY] Checking consciousness.jsonl for THINK actions...
"THINK"
"THINK"
"REFLECT"

[STEP 10] Verifying FalkorDB episode count...
1147

===== TASK 3 EXECUTION COMPLETE =====

Next steps:
1. Commit changes to git: git add karma-core/server.py && git commit -m "feat: Re-enable episode ingestion after duplicate cleanup (Task 3)"
2. Push to main: git push origin main
3. Monitor consciousness.jsonl for THINK entries
```

---

## If Something Goes Wrong

### SSH Command Times Out
**Try**:
- Use explicit timeout: `ssh -o ConnectTimeout=60 root@arknexus.net`
- Verify network: `ping arknexus.net`
- Use alternate connection method (cloud terminal, VPN, etc.)

### Script Fails at Step 3 (Deletion)
**Likely cause**: Redis/FalkorDB connection issue
**Action**:
- Check if FalkorDB is running: `ssh vault-neo "docker ps | grep falkordb"`
- Check logs: `ssh vault-neo "docker logs falkordb 2>&1 | tail -30"`

### Docker Build Fails
**Likely cause**: server.py syntax error
**Action**:
- Revert: `git checkout karma-core/server.py`
- Check syntax: `python -m py_compile karma-core/server.py`

### consciousness Still Shows NO_ACTION
**Likely cause**: Not enough time for cycle
**Action**: Wait 120 seconds total, then check again

### Everything Worked, But consciousness Shows NO_ACTION After 2 Minutes
**Likely cause**: Ingestion still not working despite code change
**Action**:
- Check if container has new code: `ssh vault-neo "docker logs karma-server 2>&1 | grep 'ingest_episode'"`
- If not present, container may have cached old image. Force rebuild: `ssh vault-neo "cd /opt/seed-vault && docker build --no-cache -t karma-core:latest /home/neo/karma-sade/karma-core/"`

---

## After Success: Commit to Git

Once the script completes successfully:

```bash
cd /c/dev/Karma

# Verify server.py was updated (should show "ingest_episode" without "None")
grep -n "ingest_episode_fn" karma-core/server.py

# Commit the change
git add karma-core/server.py
git commit -m "feat: Re-enable episode ingestion after duplicate cleanup (Task 3, Session 34)"

# Push to main
git push origin main

# Verify it's committed
git log --oneline -1
```

---

## Verification Checklist (After Script Completes)

Run these commands to verify Task 3 succeeded:

```bash
# Check 1: Duplicates are gone
ssh vault-neo "cd /home/neo/karma-sade && python karma-core/scripts/identify_duplicates.py"
# Expected: No duplicates found

# Check 2: server.py is updated
ssh vault-neo "sed -n '1612p' /opt/seed-vault/memory_v1/karma-core/server.py"
# Expected: Contains "ingest_episode_fn=ingest_episode"

# Check 3: Container is running
ssh vault-neo "docker ps | grep karma-server"
# Expected: Container listed as running

# Check 4: consciousness is THINKING
ssh vault-neo "tail -10 /opt/seed-vault/memory_v1/ledger/consciousness.jsonl | jq '.action'"
# Expected: Some entries show "THINK" or "REFLECT"

# Check 5: Episodes exist in FalkorDB
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt); curl -s -H 'Authorization: Bearer \$TOKEN' https://hub.arknexus.net/v1/cypher -d '{\"cypher\": \"MATCH (e:Episode) RETURN COUNT(e) as episodes\"}' 2>&1 | jq '.data[0][0]'"
# Expected: Number > 0

# Check 6: Git is committed
cd /c/dev/Karma && git log --oneline -1
# Expected: Shows your Task 3 commit
```

---

## Why This Task Matters

### The Problem
```
Session 32: batch_ingest --skip-dedup runs
    ↓
Creates 47 duplicate Entity nodes in FalkorDB
    ↓
consciousness loop queries duplicates, gets confused
    ↓
consciousness returns NO_ACTION (can't think)
    ↓
Ingestion disabled as safety measure
    ↓
NEW episodes NOT added to FalkorDB
    ↓
consciousness can't observe anything
    ↓
BLOCKER: Can't verify Phase 1 Step 2 (consciousness THINKING)
```

### The Solution (This Task)
```
Remove duplicate entities
    ↓
Re-enable ingestion in server.py
    ↓
Restart karma-server with new code
    ↓
consciousness observes new episodes
    ↓
consciousness THINKS on observations
    ↓
UNBLOCKS: Phase 1 Step 2 verification
    ↓
Can proceed to Phase 1 Step 3 (Resurrection Protocol)
```

---

## TL;DR

### One command (locally):
```bash
scp C:\dev\Karma\task3_execute.sh root@arknexus.net:/tmp/
```

### One command (on vault-neo):
```bash
bash /tmp/task3_execute.sh
```

### Then commit:
```bash
cd /c/dev/Karma && git add karma-core/server.py && git commit -m "feat: Re-enable episode ingestion after duplicate cleanup (Task 3)" && git push origin main
```

---

## More Details?

- **TASK3_SUMMARY.md** — Overview and context
- **TASK3_EXECUTION_PLAN.md** — Detailed technical steps
- **TASK3_MANUAL_EXECUTION.md** — Step-by-step manual version (if automated fails)
- **task3_execute.sh** — The automation script itself

---

## Expected Result

After successful execution:

1. **consciousness.jsonl** shows THINK entries (not NO_ACTION)
2. **New episodes** are ingested to FalkorDB
3. **consciousness loop** is actively thinking (every 60 seconds)
4. **Phase 1 Step 2** is VERIFIED COMPLETE
5. **blocker-3** is RESOLVED
6. **Ready to proceed** to Phase 1 Step 3 (Resurrection Protocol)

