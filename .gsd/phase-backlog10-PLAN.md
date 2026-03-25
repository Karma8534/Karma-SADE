# Phase Backlog-10 — Julian Memory Primitives PLAN
**Created:** 2026-03-25 | **Session:** 144

## Tasks

### Task 1 — Check HUB_CAPTURE_TOKEN in hub.env
**What:** Verify the ambient capture token is available in hub-bridge environment
<verify>grep HUB_CAPTURE_TOKEN in hub.env on vault-neo — token present</verify>
<done>[ ] token confirmed</done>

### Task 2 — Add classifyMemoryKind() + computeSalience() helpers to server.js
**What:** Two pure functions, ~60 lines total, no external deps
- classifyMemoryKind(text) → "Constraint"|"Procedure"|"Preference"|"Definition"|"Observation"
- computeSalience(text, kind, isPinned) → float 0.0–1.0
<verify>Unit test: classifyMemoryKind("never use worktrees") === "Constraint"; computeSalience("x", "Constraint", false) > 0.5</verify>
<done>[ ] helpers in server.js, logic confirmed</done>

### Task 3 — Inject kind + salience into buildVaultRecord()
**What:** buildVaultRecord() already called for all vault writes — add kind + salience fields
- Detect [PINNED] prefix → set pinned=true, strip prefix from content
- Pass kind + salience into the record metadata
<verify>Manual trace: buildVaultRecord({content:"never use worktrees"}) → kind:"Constraint", salience>0.5</verify>
<done>[ ] buildVaultRecord updated</done>

### Task 4 — Wire bus → ledger in POST /v1/coordination/post
**What:** After writing coord entry, fire-and-forget POST to vault-api /v1/ambient
- Use VAULT_AMBIENT_URL (already used elsewhere in server.js) + HUB_CAPTURE_TOKEN
- Tags: ["bus", "coordination", from_agent, msg_type]
- Apply classifyMemoryKind + computeSalience to message content
- Fire-and-forget (don't await, don't block coord response)
<verify>Post a test bus message → check vault ledger: `ssh vault-neo "tail -5 /opt/seed-vault/memory_v1/ledger/memory.jsonl | python3 -m json.tool"` → entry with tags including "bus"</verify>
<done>[ ] bus messages appear in ledger</done>

### Task 5 — Deploy + verify end-to-end
**What:** karma-hub-deploy skill → confirm all 4 primitives live
<verify>
- HUB_CAPTURE_TOKEN present in running container env
- Post to /v1/coordination/post → ledger entry appears within 5s
- buildVaultRecord output includes kind + salience fields
- [PINNED] prefix handling confirmed
</verify>
<done>[ ] all primitives live in production</done>
