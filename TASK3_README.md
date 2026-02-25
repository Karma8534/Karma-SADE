# Task 3: Re-Enable Episode Ingestion — Complete Documentation Index

## 🎯 Start Here

If you're new to this task, read in this order:

1. **RUN_TASK3_NOW.md** ← Start here (30-second overview)
2. **TASK3_SUMMARY.md** ← Understand the full context
3. **task3_execute.sh** ← Copy this to vault-neo and run it
4. **TASK3_FINAL_REPORT.md** ← Read after successful execution

---

## 📚 Complete Documentation

### Quick Reference (5 minutes)
- **RUN_TASK3_NOW.md** — TL;DR version, fastest path to execution

### Understanding the Task (15 minutes)
- **TASK3_SUMMARY.md** — Full overview, context, timeline, success criteria
- **TASK3_FINAL_REPORT.md** — Executive summary, deliverables, post-execution checklist

### Detailed Technical Reference (30 minutes)
- **TASK3_EXECUTION_PLAN.md** — Step-by-step implementation with expected outputs
- **TASK3_MANUAL_EXECUTION.md** — Manual execution guide (if automation fails)

### Tools
- **task3_execute.sh** — Full automation script (copy to vault-neo and run)

---

## ⚡ TL;DR (30 Seconds)

### What To Do
```bash
# 1. Copy script to vault-neo
scp C:\dev\Karma\task3_execute.sh root@arknexus.net:/tmp/

# 2. SSH and execute
ssh root@arknexus.net
bash /tmp/task3_execute.sh

# 3. Commit results
cd /c/dev/Karma
git add karma-core/server.py
git commit -m "feat: Re-enable episode ingestion after duplicate cleanup (Task 3)"
git push origin main
```

### What Gets Fixed
- Removes 47 duplicate entities from FalkorDB
- Re-enables episode ingestion (server.py line 1612)
- Restarts consciousness loop to THINK on new episodes
- Unblocks Phase 1 Step 3 (Resurrection Protocol)

### Expected Time
- 90-120 seconds total execution time
- 2 minutes to verify
- 1 minute to commit

---

## 📋 Which File To Read?

| Your Situation | Read This |
|---|---|
| "I'm in a rush" | RUN_TASK3_NOW.md |
| "I want to understand the problem" | TASK3_SUMMARY.md |
| "I want exact step-by-step instructions" | TASK3_EXECUTION_PLAN.md |
| "The automation script failed" | TASK3_MANUAL_EXECUTION.md |
| "I finished and need verification checklist" | TASK3_FINAL_REPORT.md (Post-Execution Checklist) |
| "I want all the context" | TASK3_FINAL_REPORT.md |

---

## 🚀 Quick Links

### Executive Access
- **One-Command Execution**: See RUN_TASK3_NOW.md
- **Fastest Success Path**: Copy/paste from RUN_TASK3_NOW.md

### Detailed Guides
- **For Technical Details**: TASK3_EXECUTION_PLAN.md
- **For Troubleshooting**: TASK3_MANUAL_EXECUTION.md
- **For Full Context**: TASK3_SUMMARY.md

### Tools
- **Automation Script**: task3_execute.sh (copy to vault-neo and run)
- **Duplicate Remover**: karma-core/scripts/remove_duplicates.py
- **Verification Tool**: karma-core/scripts/identify_duplicates.py

---

## ✅ Success Criteria

You know Task 3 succeeded when:

1. ✅ Duplicate removal script runs without errors
2. ✅ All 47 duplicates are deleted
3. ✅ identify_duplicates.py shows "No duplicates found"
4. ✅ server.py line 1612 shows `ingest_episode_fn=ingest_episode`
5. ✅ Docker image rebuilt successfully
6. ✅ karma-server container restarts
7. ✅ consciousness.jsonl shows THINK entries (not NO_ACTION)
8. ✅ FalkorDB episode count > 0
9. ✅ Changes committed to git

See TASK3_FINAL_REPORT.md > Critical Success Criteria for full checklist.

---

## 🔍 What This Task Does

### The Problem
Session 32 created 47 duplicate entities in FalkorDB. Episode ingestion was disabled to prevent further corruption. Consciousness loop can't observe new episodes, so it can't THINK.

### The Solution
Remove duplicates → Re-enable ingestion → Restart → Verify THINK execution

### The Impact
- Unblocks Phase 1 Step 2 verification (consciousness THINKING)
- Unblocks Phase 1 Step 3 (Resurrection Protocol)
- Resolves blocker-3 (Episode ingestion disabled)

---

## 🗂️ File Structure

```
C:\dev\Karma\
├── TASK3_README.md (YOU ARE HERE)
├── RUN_TASK3_NOW.md ← Read first
├── TASK3_SUMMARY.md ← Read second
├── TASK3_EXECUTION_PLAN.md ← Detailed steps
├── TASK3_MANUAL_EXECUTION.md ← Fallback guide
├── TASK3_FINAL_REPORT.md ← After execution
├── task3_execute.sh ← Copy to vault-neo
├── karma-core/
│   ├── scripts/
│   │   ├── remove_duplicates.py
│   │   └── identify_duplicates.py
│   └── server.py (will be modified)
└── ...
```

---

## 🚨 If Something Goes Wrong

### SSH Connection Times Out
→ Read RUN_TASK3_NOW.md > If Something Goes Wrong > SSH Command Times Out

### Script Fails
→ Read TASK3_MANUAL_EXECUTION.md > Troubleshooting

### Docker Build Fails
→ Read TASK3_EXECUTION_PLAN.md > Troubleshooting

### consciousness Shows NO_ACTION
→ Read TASK3_MANUAL_EXECUTION.md > Troubleshooting > consciousness Still Shows NO_ACTION

---

## 📊 Documentation Statistics

| Document | Pages | Read Time | Purpose |
|----------|-------|-----------|---------|
| RUN_TASK3_NOW.md | 3-4 | 5 min | Quick start |
| TASK3_SUMMARY.md | 5-6 | 15 min | Overview & context |
| TASK3_EXECUTION_PLAN.md | 8-10 | 20 min | Detailed technical |
| TASK3_MANUAL_EXECUTION.md | 10-12 | 25 min | Step-by-step manual |
| TASK3_FINAL_REPORT.md | 12-14 | 20 min | Executive summary |
| **TOTAL** | **~40** | **~85 min** | Complete reference |

**Quick Path** (RUN + SUMMARY + SCRIPT): ~20 minutes
**Detailed Path** (All documents): ~85 minutes

---

## 🔗 Context References

**Blocking Issue**: Session 33, blocker-3
**Related**: Session 32 (batch_ingest corruption)
**Unblocks**: Phase 1 Step 3 (Resurrection Protocol)
**Architecture**: CLAUDE.md, resurrection-architecture.md

---

## 📝 Next Steps After Completion

1. ✅ Verify all success criteria pass
2. ✅ Commit changes to git
3. ✅ Update MEMORY.md with completion status
4. ✅ Document lessons learned
5. ✅ Proceed to Phase 1 Step 3

See TASK3_FINAL_REPORT.md > Post-Execution Checklist for details.

---

## 💡 Pro Tips

1. **Fastest Execution**: Just run RUN_TASK3_NOW.md steps (30 seconds read, 2 minutes execute)
2. **Learning**: Read TASK3_SUMMARY.md to understand the full context
3. **Debugging**: Keep TASK3_MANUAL_EXECUTION.md open in case script fails
4. **Reference**: Print TASK3_EXECUTION_PLAN.md for detailed technical reference
5. **Verification**: Use checklists from TASK3_FINAL_REPORT.md after execution

---

## ❓ Questions?

| Question | Answer Location |
|----------|-----------------|
| "What's the fastest way to execute?" | RUN_TASK3_NOW.md |
| "Why is this task needed?" | TASK3_SUMMARY.md (root cause section) |
| "What exactly happens at each step?" | TASK3_EXECUTION_PLAN.md |
| "How do I troubleshoot if something breaks?" | TASK3_MANUAL_EXECUTION.md |
| "Did I succeed?" | TASK3_FINAL_REPORT.md (success criteria) |
| "What comes after Task 3?" | MEMORY.md (next steps for Phase 1 Step 3) |

---

## 📞 Support Resources

- **Quick Issues**: RUN_TASK3_NOW.md > If Something Goes Wrong
- **Step-by-Step Help**: TASK3_MANUAL_EXECUTION.md > Troubleshooting
- **Technical Deep Dive**: TASK3_EXECUTION_PLAN.md > Troubleshooting
- **Rollback Instructions**: TASK3_MANUAL_EXECUTION.md > Troubleshooting > (specific issue)

---

## ✨ Summary

**Task 3** is a low-risk, high-impact cleanup and verification task:
- ✅ Remove duplicates
- ✅ Re-enable ingestion
- ✅ Verify consciousness THINKS
- ✅ Unblock Phase 1 Step 3

**Status**: Ready to execute
**Documentation**: Complete
**Tools**: Prepared
**Expected Time**: 2 minutes execution + 1 minute git

**Start with**: RUN_TASK3_NOW.md

