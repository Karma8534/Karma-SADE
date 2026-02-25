# Task 3: Re-Enable Episode Ingestion — Execution Plan

## Objective
Clean up duplicate entities from Session 32's corrupted batch_ingest and re-enable episode ingestion.

## Executive Summary
Session 32 ran `batch_ingest.py --skip-dedup` which created duplicate Entity nodes in FalkorDB. This task removes those duplicates and re-enables the ingestion_fn in karma-server so consciousness loop can observe and process new episodes.

## Success Criteria
- [ ] Duplicate entities identified (dry-run)
- [ ] Duplicates deleted (--confirm mode)
- [ ] FalkorDB verified clean
- [ ] server.py line 1612 changed: `ingest_episode_fn=None` → `ingest_episode_fn=ingest_episode`
- [ ] karma-core Docker image rebuilt
- [ ] karma-server container restarted
- [ ] consciousness.jsonl shows THINK actions (not NO_ACTION)
- [ ] FalkorDB episode count verified > 0
- [ ] Changes committed to git

---

## Step-by-Step Implementation

### STEP 1: Verify duplicate removal script is in place
**Location**: `/home/neo/karma-sade/karma-core/scripts/remove_duplicates.py`

**Action**: Create the script on vault-neo (use method A or B below):

**Method A: Direct SSH + Heredoc (Recommended)**
```bash
ssh vault-neo 'cat > /home/neo/karma-sade/karma-core/scripts/remove_duplicates.py << "EOFPYTHON"
# [INSERT FULL PYTHON SCRIPT HERE - see remove_duplicates.py in repo]
EOFPYTHON'
```

**Method B: SCP from local**
```bash
scp /c/dev/Karma/karma-core/scripts/remove_duplicates.py root@arknexus.net:/home/neo/karma-sade/karma-core/scripts/
```

**Verify**:
```bash
ssh vault-neo "ls -lh /home/neo/karma-sade/karma-core/scripts/remove_duplicates.py"
```
Expected: File exists with size ~4K

---

### STEP 2: Run dry-run to see how many duplicates will be deleted

```bash
ssh vault-neo "cd /home/neo/karma-sade && python karma-core/scripts/remove_duplicates.py"
```

**Expected output format**:
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

**Document**: Note the number N (duplicates to delete).

---

### STEP 3: Run with --confirm to actually delete duplicates

```bash
ssh vault-neo "cd /home/neo/karma-sade && python karma-core/scripts/remove_duplicates.py --confirm"
```

**Expected output format**:
```
DELETING N duplicate entities...

✓ Deleted: entity_id_1       Entity Name 1                  (type)
✓ Deleted: entity_id_2       Entity Name 2                  (type)
...

================================================================================
Summary: Deleted N entities, kept M canonical
```

**Verify exit code**:
```bash
echo $?
```
Expected: `0` (success)

---

### STEP 4: Verify no duplicates remain

```bash
ssh vault-neo "cd /home/neo/karma-sade && python karma-core/scripts/identify_duplicates.py"
```

**Expected output**:
```
DRY RUN MODE (no changes made)
No duplicates found
```

**If duplicates still exist**: Stop here and investigate. Something failed.

---

### STEP 5: Update server.py to re-enable ingestion

**Current state (line 1612)**:
```python
ingest_episode_fn=None,  # Disabled: Graphiti has corrupted entities from batch_ingest --skip-dedup; consciousness writes to ledger only
```

**Target state**:
```python
ingest_episode_fn=ingest_episode,  # Re-enabled after duplicate cleanup (Task 3, Session 34)
```

**Execute on vault-neo**:
```bash
ssh vault-neo 'sed -i "s/ingest_episode_fn=None,.*Disabled: Graphiti has corrupted entities.*/ingest_episode_fn=ingest_episode,  # Re-enabled after duplicate cleanup (Task 3)/g" /opt/seed-vault/memory_v1/karma-core/server.py'
```

**Verify the change**:
```bash
ssh vault-neo "sed -n '1610,1615p' /opt/seed-vault/memory_v1/karma-core/server.py"
```

**Expected output**:
```
        from consciousness import ConsciousnessLoop
        app.state.consciousness = ConsciousnessLoop(
            get_falkor_fn=get_falkor,
            get_graph_stats_fn=get_graph_stats,
            get_openai_client_fn=get_openai_client,
            active_conversations_ref=active_conversations,
            router=app.state.router,
            ingest_episode_fn=ingest_episode,  # Re-enabled after duplicate cleanup (Task 3)
            sms_notify_fn=app.state.sms.notify if app.state.sms.enabled else None,
        )
```

Line 1612 must show `ingest_episode_fn=ingest_episode,`

---

### STEP 6: Rebuild karma-core Docker image

```bash
ssh vault-neo "cd /opt/seed-vault && docker build -t karma-core:latest /home/neo/karma-sade/karma-core/ 2>&1 | tail -20"
```

**Expected output**:
```
...
Successfully tagged karma-core:latest
```

**Check for errors**: Look for any `SyntaxError` or `ERROR` in output. If found, stop and investigate.

---

### STEP 7: Stop and remove old karma-server container

```bash
ssh vault-neo "docker stop karma-server && docker rm karma-server"
```

**Expected output**:
```
karma-server
karma-server
```

---

### STEP 8: Start new karma-server container

```bash
ssh vault-neo "cd /opt/seed-vault && docker-compose up -d karma-server"
```

**Expected output**:
```
Creating karma-server ... done
```

**Check startup logs** (wait 5 seconds first):
```bash
sleep 5 && ssh vault-neo "docker logs karma-server 2>&1 | tail -30"
```

**Expected**:
```
[GRAPHITI] Client initialized
[SERVER] Karma server ready at 0.0.0.0:8000
```

**No errors**: Should show successful initialization.

---

### STEP 9: Verify consciousness loop starts THINKING

Wait 60+ seconds for next consciousness cycle, then check:

```bash
ssh vault-neo "tail -5 /opt/seed-vault/memory_v1/ledger/consciousness.jsonl | jq '.action'"
```

**Expected output** (should see THINK or REFLECT, not NO_ACTION):
```
"THINK"
"THINK"
"REFLECT"
...
```

**If still NO_ACTION**: Wait another 60s and check again. Consciousness cycle takes 60s.

---

### STEP 10: Verify episode ingestion is working

Check FalkorDB episode count:

```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt); curl -s -H 'Authorization: Bearer \$TOKEN' https://hub.arknexus.net/v1/cypher -d '{\"cypher\": \"MATCH (e:Episode) RETURN COUNT(e) as episodes\"}' 2>&1 | jq '.data[0][0]' 2>/dev/null || echo 'Query failed'"
```

**Expected output**:
```
1147
```
(or higher number - should be > 0)

---

### STEP 11: Commit changes to git

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

---

## Timeline & Checkpoints

| Step | Action | Expected Time | Blocker? |
|------|--------|----------------|----------|
| 1-3 | Copy script + duplicate deletion | 5-10 min | No |
| 4 | Verify duplicates removed | 1-2 min | **YES** - stop if duplicates remain |
| 5 | Update server.py | 2-3 min | No |
| 6 | Rebuild Docker image | 3-5 min | **YES** - stop if build fails |
| 7-8 | Restart container | 2-3 min | **YES** - stop if startup fails |
| 9 | Wait for consciousness THINK | 60+ seconds | **YES** - if NO_ACTION, investigate |
| 10 | Verify ingestion | 1-2 min | Diagnostic only |
| 11 | Commit to git | 1 min | No |

**Total time**: ~90-120 minutes (mostly waiting for consciousness cycles)

---

## Rollback Plan

If anything goes wrong:

1. **If duplicates won't delete**:
   - Check Redis connectivity: `ssh vault-neo "redis-cli -h falkordb ping"`
   - Check FalkorDB is running: `ssh vault-neo "docker ps | grep falkordb"`

2. **If Docker build fails**:
   - Revert server.py: `git checkout karma-core/server.py`
   - Check for Python syntax errors: `python -m py_compile karma-core/server.py`

3. **If consciousness still shows NO_ACTION after 2 minutes**:
   - Check consciousness logs: `ssh vault-neo "docker logs karma-server 2>&1 | grep -i consciousness"`
   - Restart consciousness loop: `ssh vault-neo "docker restart karma-server"`

4. **If episode count doesn't increase**:
   - Check FalkorDB for errors: `ssh vault-neo "docker logs falkordb 2>&1 | tail -20"`
   - Verify ingestion_fn in running code: `ssh vault-neo "grep -n 'ingest_episode_fn' /opt/seed-vault/memory_v1/karma-core/server.py"`

---

## Notes

- All commands use `ssh vault-neo` (vault-neo)
- Git changes are local only; commit at the end
- Consciousness cycle is 60s; give it at least 2 cycles to verify THINK execution
- If SSH times out, the command is still executing on vault-neo (check manually)
- FalkorDB queries require hub auth token (auto-loaded from `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt`)

