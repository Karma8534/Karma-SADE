# CONTEXT: Ambient Layer Tier 1 — Git Hooks → /v1/ambient Capture

**Phase:** Tier 1 (Ambient Capture via Git Hooks)
**Status:** Ready to Execute
**Decision date:** 2026-03-03 (Session 56)
**Locked by:** Claude Code (Karma workflow)

---

## What We're Building

Automatic context capture when Colby commits code. Flow:
```
Colby: git commit -m "fix: z.ai endpoint"
  ↓
Local hook fires: .git/hooks/post-commit
  ↓
Hook sends POST to hub-bridge: /v1/ambient
  ↓
Hub-bridge → vault-api → /opt/seed-vault/memory_v1/ledger/memory.jsonl
  ↓
Entry stored: {type: "ambient", source: "git-commit", diff, message, files}
  ↓
Next session: Karma can query consciousness.jsonl tail and see "last commits were: ..."
```

**Core value:** Automatic context capture. No manual work. Colby commits → Karma sees it.

---

## Design Decisions (Locked)

### Decision 1: Two Hooks Required
**Question:** Do we need both local hooks AND droplet hooks?

**Decided:** YES, both.
- **Local hooks** (.git/hooks/post-commit, .claude/hooks/session-end-verify.sh): Run on P1 machine when work happens
- **Droplet hooks** (vault-neo:/opt/seed-vault/.git/hooks/post-commit): Run on droplet when canonical repo commits

**Reasoning:**
- Local hooks: Capture Colby's immediate context (what he just committed)
- Droplet hooks: Capture official commits to canonical source
- Both → no blind spots

**Implication:** Must sync both to droplet. Must test both paths.

---

### Decision 2: /v1/ambient Endpoint Design
**Question:** What metadata should be captured?

**Decided:** Minimal set (no file contents):
```json
{
  "source": "git-commit",
  "timestamp": "2026-03-03T01:45:00Z",
  "commit_hash": "f21bfbf",
  "commit_message": "feat: adopt GSD file structure",
  "files_changed": [".gsd/PROJECT.md", ".gsd/REQUIREMENTS.md", ...],
  "insertions": 699,
  "deletions": 0,
  "diff_summary": "Added 5 files: .gsd config, project docs, state log"
}
```

**Reasoning:**
- Keep payloads small (token efficiency)
- Capture intent (commit message) + scope (files)
- Omit large diffs (can query git if needed)
- Searchable by function name / file name

**Implication:** /v1/ambient must parse `git log` format, extract key fields, send minimal JSON.

---

### Decision 3: Error Handling Strategy
**Question:** What if /v1/ambient endpoint is down?

**Decided:** Local hook doesn't block commit. Hook fires asynchronously.
- Hook tries to POST to hub-bridge
- If it fails (timeout, 5xx error), log to local file but don't fail commit
- Next session, check logs and retry failed POSTs manually if needed

**Reasoning:**
- Availability: Git commit must succeed even if hub-bridge down
- Recovery: Logs preserved; no data loss
- Simplicity: No retry logic needed (just log + move on)

**Implication:** Hook must have error handling. Must log failures to `.git/hook-failures.log`.

---

### Decision 4: Verification Criteria
**Question:** How do we know Tier 1 is "done"?

**Decided:** End-to-end proof:
1. ✅ Hooks synced to droplet
2. ✅ Local commit made → hook fires → POST sent
3. ✅ Hub-bridge receives POST (check hub-bridge logs)
4. ✅ Vault ledger has new entry (check `/opt/seed-vault/memory_v1/ledger/memory.jsonl`)
5. ✅ Entry contains correct commit metadata
6. ✅ Next session can query /v1/context and see the capture

**Reasoning:**
- Full chain verification (not just "hook exists")
- Proves data flows all the way to ledger
- Ensures next session can retrieve it

**Implication:** Can't claim done until step 6 passes.

---

## Out of Scope (Explicitly)

- ❌ Tier 3 (screen capture daemon) — not in this phase
- ❌ Fine-tuning /v1/ambient response format — fixed schema for now
- ❌ Batch retry mechanism — manual recovery only
- ❌ Real-time notifications — logs only, no webhooks

---

## Known Unknowns

- **Hub-bridge availability:** Is vault-neo reachable from P1? Need to verify.
- **Hook permissions:** Will droplet accept hooks in .git/ directory? May need special config.
- **Ledger format:** Will /v1/ambient write JSONL correctly? Need to verify schema.

---

## Quality Gates

Before marking Tier 1 DONE:
1. ✅ Both hooks synced to droplet
2. ✅ Local commit test passes (end-to-end verified)
3. ✅ Ledger entry has correct schema
4. ✅ Next session can retrieve via /v1/context
5. ✅ No unhandled errors (all errors logged)
6. ✅ Documented in ROADMAP.md (phase status updated)

---

**Locked:** 2026-03-03T01:45:00Z
**Ready for:** /gsd:plan-phase (atomic task breakdown)
**Owner:** Claude Code + Karma
