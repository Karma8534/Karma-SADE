# Phase Backlog-10 — Julian Memory Primitives PLAN
**Created:** 2026-03-25 | **Session:** 144 | **Completed:** 2026-03-25

## Tasks

### Task 1 — Check HUB_CAPTURE_TOKEN in hub.env
<verify>HUB_CAPTURE_TOKEN loaded from secret file at startup (VAULT_BEARER, length 64 confirmed)</verify>
<done>[x] token confirmed — file-based, already working</done>

### Task 2 — Add classifyMemoryKind() + computeSalience() helpers to server.js
<verify>classifyMemoryKind("never use worktrees") === "Constraint" ✅; computeSalience confirmed > 0.5 for Constraints</verify>
<done>[x] helpers live in server.js</done>

### Task 3 — Inject kind + salience into buildVaultRecord()
<verify>content._kind: Constraint, content._salience: 0.843 confirmed in ledger ✅</verify>
<done>[x] buildVaultRecord updated — kind/salience/pinned in content{} (schema-safe)</done>

### Task 4 — Wire bus → ledger enrichment
<verify>Bus→ledger already existed. Enriched: blocking urgency → auto-pin, tags include "bus"+"kind:X"+"salience:high" ✅</verify>
<done>[x] Bus→ledger already working + enriched</done>

### Task 5 — Deploy + verify end-to-end
<verify>
- Ledger entry for blocking coord post: _kind:Constraint, _salience:0.843, _pinned:True ✅
- Tags: pinned, kind:constraint, salience:high, bus, coordination ✅
- RestartCount: 0 ✅
</verify>
<done>[x] ALL B10 PRIMITIVES LIVE IN PRODUCTION</done>
