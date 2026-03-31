# Task 3: Re-Enable Episode Ingestion — Implementation Summary

## Task Overview

**Objective**: Clean up duplicate entities created in Session 32 and re-enable episode ingestion so consciousness loop can observe and THINK on new episodes.

**Status**: ✅ PREPARED - Awaiting execution on vault-neo

**Root Cause**: Session 32 ran `batch_ingest.py --skip-dedup` which created duplicate Entity nodes in FalkorDB. Episode ingestion was disabled as a safety measure to prevent further corruption.

**Solution**: Remove duplicates, re-enable ingestion, verify consciousness THINK execution.

---

## Deliverables

### Local (Prepared & Ready)

1. **Task3_EXECUTION_PLAN.md** - Detailed step-by-step guide
2. **TASK3_MANUAL_EXECUTION.md** - Manual execution guide (if automated fails)
3. **task3_execute.sh** - Full automation script
4. **karma-core/scripts/remove_duplicates.py** - Duplicate removal tool (already in repo)
5. **karma-core/scripts/identify_duplicates.py** - Verification tool (already in repo)

### What Needs to Happen on Vault-Neo

1. Copy `task3_execute.sh` to vault-neo and run it (one command does everything)
   OR
2. Follow manual steps in TASK3_MANUAL_EXECUTION.md

---

## Quick Start

### One-Command Execution (Recommended)

```bash
# From your local machine
scp C:\dev\Karma\task3_execute.sh root@arknexus.net:/tmp/

# Then SSH to vault-neo and run
ssh vault-neo
bash /tmp/task3_execute.sh
```

This will:
- ✅ Identify duplicates (dry-run)
- ✅ Delete duplicates (--confirm)
- ✅ Verify duplicates are gone
- ✅ Update server.py to re-enable ingestion
- ✅ Rebuild Docker image
- ✅ Restart karma-server
- ✅ Wait for consciousness cycle
- ✅ Verify THINK execution

**Expected time**: 90-120 seconds

### Manual Step-by-Step

Follow TASK3_MANUAL_EXECUTION.md for detailed instructions.

---

## What Gets Changed

### On Vault-Neo

**File**: `/opt/seed-vault/memory_v1/karma-core/server.py` (line 1612)

**Before** (DISABLED):
```python
ingest_episode_fn=None,  # Disabled: Graphiti has corrupted entities from batch_ingest --skip-dedup
```

**After** (RE-ENABLED):
```python
ingest_episode_fn=ingest_episode,  # Re-enabled after duplicate cleanup (Task 3)
```

### On Local Git

**File**: `C:\dev\Karma\karma-core\server.py` (same change, after sync)

After vault-neo completes, copy the updated file back and commit:
```bash
cd /c/dev/Karma
git add karma-core/server.py
git commit -m "feat: Re-enable episode ingestion after duplicate cleanup (Task 3, Session 34)"
git push origin main
```

---

## Verification Checkpoints

### Checkpoint 1: Duplicates Removed
```bash
ssh vault-neo "cd /home/neo/karma-sade && python karma-core/scripts/identify_duplicates.py"
```
Expected: `No duplicates found`

### Checkpoint 2: Server.py Updated
```bash
ssh vault-neo "grep -n 'ingest_episode_fn' /opt/seed-vault/memory_v1/karma-core/server.py"
```
Expected: Line 1612 shows `ingest_episode_fn=ingest_episode,`

### Checkpoint 3: Docker Image Rebuilt
```bash
ssh vault-neo "docker images karma-core:latest"
```
Expected: Image exists with recent timestamp

### Checkpoint 4: karma-server Running
```bash
ssh vault-neo "docker ps | grep karma-server"
```
Expected: Container is running

### Checkpoint 5: Consciousness THINKING
```bash
ssh vault-neo "tail -5 /opt/seed-vault/memory_v1/ledger/consciousness.jsonl | jq '.action'"
```
Expected: Shows `"THINK"` or `"REFLECT"` (NOT `"NO_ACTION"`)

### Checkpoint 6: Episode Count Growing
```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt); curl -s -H 'Authorization: Bearer \$TOKEN' https://hub.arknexus.net/v1/cypher -d '{\"cypher\": \"MATCH (e:Episode) RETURN COUNT(e) as episodes\"}' 2>&1 | jq '.data[0][0]'"
```
Expected: Number > 0 (episodes in FalkorDB)

---

## Success Criteria

- [ ] Duplicate removal script executed successfully
- [ ] Duplicates count verified as 0
- [ ] server.py line 1612 changed to enable ingestion
- [ ] Docker image rebuilt without errors
- [ ] karma-server container restarted
- [ ] consciousness.jsonl shows THINK actions
- [ ] FalkorDB episode count > 0
- [ ] Changes committed to git

---

## Potential Issues & Mitigations

### Issue: SSH Timeout
**Mitigation**: Use a different SSH client or cloud terminal with better network connectivity

### Issue: Duplicates Won't Delete
**Mitigation**: Check Redis connectivity, verify FalkorDB is running, check logs

### Issue: Docker Build Fails
**Mitigation**: Revert server.py change, check for syntax errors, rebuild step-by-step

### Issue: consciousness Still Shows NO_ACTION
**Mitigation**: Wait longer (60-120 seconds), check logs, manually trigger consciousness reset signal

---

## Files Reference

### Scripts & Tools

```
C:\dev\Karma\
├── karma-core/
│   └── scripts/
│       ├── remove_duplicates.py          ← Deletes duplicate entities
│       └── identify_duplicates.py        ← Verifies no duplicates
├── karma-core/server.py                  ← Will be modified (line 1612)
├── task3_execute.sh                      ← Full automation script (copy to vault-neo)
├── TASK3_EXECUTION_PLAN.md              ← Detailed step-by-step guide
├── TASK3_MANUAL_EXECUTION.md            ← Manual execution guide
└── TASK3_SUMMARY.md                     ← This file
```

### Vault-Neo Locations

```
vault-neo:/home/neo/karma-sade/
├── karma-core/
│   ├── scripts/remove_duplicates.py      ← Must exist
│   ├── scripts/identify_duplicates.py    ← Already exists
│   └── server.py                         ← Will be synced here
└── ...

vault-neo:/opt/seed-vault/
├── memory_v1/
│   ├── karma-core/server.py              ← Will be updated (line 1612)
│   └── ledger/
│       ├── consciousness.jsonl           ← Verification checkpoint
│       └── memory.jsonl                  ← Episode ledger
└── docker-compose.yml
```

---

## Timeline

| Step | Duration | What Happens |
|------|----------|--------------|
| 1-2 | 1-2 min | Copy script, create remove_duplicates.py |
| 3 | 1-2 min | Run dry-run (identify duplicates) |
| 4 | 2-5 min | Run --confirm (delete duplicates) |
| 5 | 1 min | Verify duplicates are gone |
| 6 | 1 min | Update server.py |
| 7-8 | 3-5 min | Rebuild Docker image |
| 9-10 | 2-3 min | Stop/restart container |
| 11 | 60 sec | Wait for consciousness cycle |
| 12 | 1 min | Verify THINK execution |
| 13 | 1 min | Verify episode count |
| Total | 90-120 sec | All steps complete |

---

## After Execution

### 1. Verify on Vault-Neo (All checkpoints pass)

```bash
ssh vault-neo "cd /home/neo/karma-sade && python karma-core/scripts/identify_duplicates.py"
# Should show: No duplicates found
```

### 2. Sync Updated server.py Back to Local

```bash
scp root@arknexus.net:/opt/seed-vault/memory_v1/karma-core/server.py C:\dev\Karma\karma-core/
```

### 3. Commit to Git

```bash
cd /c/dev/Karma
git add karma-core/server.py
git commit -m "feat: Re-enable episode ingestion after duplicate cleanup (Task 3, Session 34)"
git push origin main
```

### 4. Update MEMORY.md

Add to Session 34 section:
```markdown
## Session 34: Task 3 Complete — Re-Enable Episode Ingestion

**Status**: ✅ COMPLETE

**What was completed**:
- [X] Identified N duplicate entities
- [X] Deleted N duplicates, kept M canonical
- [X] Updated server.py line 1612 to re-enable ingestion
- [X] Rebuilt karma-core Docker image
- [X] Restarted karma-server container
- [X] Verified consciousness loop THINKING (THINK entries visible)
- [X] Verified episode ingestion working (FalkorDB count > 0)

**Verification**:
- ✅ Duplicates: 0 remaining
- ✅ server.py: ingest_episode_fn=ingest_episode
- ✅ Docker: karma-core:latest rebuilt
- ✅ Container: karma-server running
- ✅ consciousness: THINK actions present
- ✅ Episodes: Ingesting to FalkorDB

**Git commits**:
- [hash] feat: Re-enable episode ingestion after duplicate cleanup (Task 3)

**Blockers resolved**:
- [BLOCKER-3] Episode ingestion disabled → RESOLVED (duplicates cleaned, ingestion re-enabled)

**Next steps for Session 35**:
- [ ] Verify Phase 1 complete (all components working)
- [ ] Build K2 resumption loader
- [ ] Test consciousness proposal generation
```

---

## Critical Success Path

```
Session 32: batch_ingest corrupts graph (duplicates created)
    ↓
Session 33: Discovers corruption, disables ingestion
    ↓
Session 34: Task 3 (THIS TASK)
    ├── Remove duplicates
    ├── Re-enable ingestion
    ├── Restart karma-server
    └── Verify consciousness THINKS
    ↓
Session 35+: Continue with Phase 1 Step 3 (Resurrection Protocol)
```

---

## Important Notes

1. **SSH Required**: You must be able to SSH to vault-neo (root@arknexus.net) to execute this task
2. **Docker Knowledge**: Familiarity with Docker helpful for debugging if build fails
3. **Patience**: Consciousness cycle is 60 seconds; allow time for verification
4. **Rollback Ready**: Can revert server.py change if issues arise
5. **No Data Loss**: Duplicate removal is safe (deletes corrupted copies, keeps canonical)

---

## Success Indicators

### Immediate (Should appear in logs within 5 minutes)
- Docker build completes: `Successfully tagged karma-core:latest`
- Container starts: `[SERVER] Karma server ready at 0.0.0.0:8000`
- Ingestion enabled: `ingest_episode_fn=ingest_episode` visible in config

### Within 2 Minutes
- consciousness.jsonl grows with new entries
- Some entries show action=THINK (not NO_ACTION)

### Definitive (Most reliable indicator)
- `tail -5 consciousness.jsonl | jq '.action'` shows THINK or REFLECT (not NO_ACTION)
- FalkorDB episode count > 0 (new episodes being ingested)

---

## Questions?

Refer to:
- **TASK3_EXECUTION_PLAN.md** — Detailed technical guide
- **TASK3_MANUAL_EXECUTION.md** — Step-by-step manual execution
- **karma-core/scripts/remove_duplicates.py** — Source code explanation
- **MEMORY.md** — Session context and current system state

