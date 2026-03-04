# v8 Execution Plan — Phased with Atomic Tasks

**Date:** 2026-03-04
**Status:** READY TO EXECUTE
**Execution order:** Phase 1 → Phase 2 → Phase 3 → Phase 4
**Each phase is independently shippable.**

---

## Phase 1: Fix Karma's Self-Knowledge
**Goal:** Karma's system prompt accurately describes the actual hub-bridge + FalkorDB system she runs in.
**Effort:** 1 session
**Risk:** Medium (must review carefully before deploying)

### Why this first
Everything else builds on this. If Karma doesn't know what she is, better retrieval and correction capture don't help — she'll misinterpret the retrieved memories or ignore corrections because they conflict with her (wrong) self-model.

---

### Task 1.1 — Read and audit the current system prompt
**What:** SSH to vault-neo, read `Memory/00-karma-system-prompt-live.md` in full.
**Who:** CC
**Verify:** Confirm the file contains the Open WebUI / Ollama / local tools description identified in the audit.
**Done when:** CC has the full content and has listed every section that is wrong or outdated.

---

### Task 1.2 — Draft replacement system prompt
**What:** Write a new `00-karma-system-prompt-live.md` that describes:

**Section 1 — Who Karma Is**
- Single coherent peer, not a stateless assistant
- Persistent identity on vault-neo (arknexus.net)
- Substrate-independent: reasoning from memory spine, not LLM computation

**Section 2 — What Karma Can and Cannot Do**
- CAN: respond via /v1/chat, query her own context via /v1/context, query graph via /v1/cypher
- CANNOT: access Colby's local Windows machine, read local files, run shell commands, browse the web
- CANNOT: call tools that don't exist in the hub-bridge context

**Section 3 — Her Memory Architecture (Accurate)**
- Ledger: `/opt/seed-vault/memory_v1/ledger/memory.jsonl` — append-only, 4000+ entries
- FalkorDB: `neo_workspace` graph — 3621+ nodes, batch-updated every 6h
- Context injection: up to ~3000 chars of relevant episodes per request
- NO real-time access to ledger during conversation — only what was injected

**Section 4 — Data Model (The Three Facts She Keeps Getting Wrong)**
- `.verdict.txt` files are LOCAL on Colby's Windows machine. NOT in the ledger. NOT searchable by Karma.
- `batch_ingest` cron reads FROM the ledger, writes TO FalkorDB. It does not write to the ledger.
- "Ledger last modified time" reflects the last new entry (chat/git/ambient), not FalkorDB sync status.

**Section 5 — Her API Surface**
- `POST /v1/chat` — how Colby talks to her
- `POST /v1/ambient` — how hooks write background captures
- `POST /v1/ingest` — how PDFs/images are ingested
- `GET /v1/context` — how she queries her own recent state
- `POST /v1/cypher` — how she runs raw FalkorDB queries

**Section 6 — Current System State**
- GLM-4.7-Flash: primary model (~80% of requests), free
- gpt-4o-mini: deep mode only (`x-karma-deep: true` header), paid
- Rate limit: 20 RPM on GLM. /v1/chat returns 429 on burst. /v1/ingest waits in slot.

**Section 7 — Behavioral Contract**
- Evidence before assertions
- Never claim something works without proof
- If unsure, say so and suggest how to verify
- Never end with "Is there anything else I can help you with?"
- Peer-level voice — not service desk

**Who:** CC drafts, Colby reviews and approves
**Verify:** Colby reads the draft and confirms it's accurate before deploy
**Done when:** Colby says "approved"

---

### Task 1.3 — Deploy new system prompt to vault-neo
**What:**
1. Edit `00-karma-system-prompt-live.md` locally
2. Commit to git
3. `git push origin main`
4. `ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"`
5. Verify the file updated: `ssh vault-neo "wc -l /home/neo/karma-sade/Memory/00-karma-system-prompt-live.md"`
6. Restart hub-bridge to pick up the new system prompt (if it's loaded at startup)

**Who:** CC
**Verify:** Send a fresh /v1/chat message asking "what tools do you have access to?" — Karma should NOT mention gemini_query, file_read, browser_open
**Done when:** Karma's response in a fresh conversation reflects the new architecture

---

### Task 1.4 — Refresh direction.md
**What:** Rewrite `direction.md` (stale since 2026-02-23) to reflect:
- Current architecture (hub-bridge + FalkorDB + GLM routing)
- Sessions 57-61 accomplishments
- Current blockers (none — system in maintenance mode)
- v8 objectives

**Who:** CC drafts, Colby approves, CC deploys
**Verify:** `ssh vault-neo "head -20 /home/neo/karma-sade/direction.md"` shows 2026-03-04 date
**Done when:** direction.md reflects current reality

---

**Phase 1 acceptance test:**
Start a fresh conversation with Karma (no priming). Ask:
1. "What tools do you have access to?" → Should NOT mention local machine tools
2. "What is a .verdict.txt file?" → Should correctly explain it's a local file on Colby's machine
3. "What happens when batch_ingest runs?" → Should correctly describe ledger → FalkorDB, not ledger write
4. "What model are you using?" → Should say GLM-4.7-Flash (primary) or gpt-4o-mini (deep mode)

All 4 correct = Phase 1 done.

---

## Phase 2: Fix Retrieval Quality
**Goal:** Context injected into each /v1/chat request is semantically relevant to the question, not just the most recent N episodes.
**Effort:** 1-2 sessions
**Depends on:** Phase 1 complete (so Karma can correctly interpret retrieved memories)

---

### Task 2.1 — Audit ChromaDB current state
**What:** Check if ChromaDB has any indexed content, when it was last updated, and what collection(s) exist.
```bash
ssh vault-neo "curl -s localhost:8001/api/v1/collections | jq ."
ssh vault-neo "curl -s localhost:8001/api/v1/heartbeat"
```
**Verify:** Know the current index state before touching it
**Done when:** CC has count of indexed documents and last-update timestamp

---

### Task 2.2 — Build ledger → ChromaDB indexer
**What:** A script (`Scripts/index_ledger_to_chromadb.py`) that:
1. Reads `memory.jsonl` from the ledger
2. For each entry, creates a document with:
   - text: the episode content (user_message + assistant_text or raw content)
   - metadata: timestamp, tags, source
3. Upserts into ChromaDB collection `karma_episodes`
4. Tracks last-indexed position to support incremental updates

**Tech:** Python, chromadb client, runs inside karma-server container (or as standalone script on vault-neo)

**NOT a new container.** Runs as a cron job alongside batch_ingest.

**Who:** CC writes + tests
**Verify:** After running, `GET /api/v1/collections/karma_episodes` shows count matching ledger line count (±5%)
**Done when:** All 4000+ ledger entries indexed in ChromaDB

---

### Task 2.3 — Add semantic retrieval to hub-bridge context injection
**What:** Modify hub-bridge `server.js` context injection logic:
1. When a /v1/chat request arrives, extract the user's message
2. Query ChromaDB: `POST /api/v1/collections/karma_episodes/query` with the message as query text, top K=10
3. Combine: top 3 semantically relevant episodes + last 2 recent episodes + stable facts header
4. Inject as karmaCtx (increase budget to 3000 chars)

**Modify:** `hub-bridge/app/server.js` (existing context injection logic)
**Who:** CC writes + tests
**Verify:**
- Ask about an old topic (something from a conversation 2+ weeks ago) — Karma should reference it
- Ask about a recent topic — Karma should reference it
- Ask about something never discussed — Karma should say she doesn't have information on it

**Done when:** Semantic retrieval demonstrably outperforms recency-only retrieval on 3 test queries

---

### Task 2.4 — Add incremental ChromaDB sync to batch_ingest cron
**What:** After batch_ingest runs (every 6h), also run the ChromaDB indexer to keep the vector index current.

**Modify:** The cron entry on vault-neo (or add as a second cron job)
**Verify:** After 6h, new ledger entries appear in ChromaDB
**Done when:** ChromaDB index stays within 6h of ledger

---

**Phase 2 acceptance test:**
1. Ask Karma about a conversation from 2+ weeks ago — she should recall relevant details
2. Ask Karma about a PDF that was ingested — she should recall its content
3. Verify context injection shows semantically matched episodes in hub-bridge logs

---

## Phase 3: Correction Capture Protocol
**Goal:** When Karma gets something wrong and is corrected, that correction persists to her next conversation.
**Effort:** 0.5 sessions (mostly process, not code)
**Depends on:** Phase 1 complete

---

### Task 3.1 — Define the correction format
**What:** A simple structured format for corrections:
```
## Correction [DATE]
**Was wrong:** [what Karma believed]
**Actually:** [what is correct]
**Source:** [how verified — session conversation, code inspection, production test]
**Applies to:** system prompt section [N]
```

These are appended to a new file: `Memory/corrections-log.md` on vault-neo.

**Who:** CC documents the format, Colby approves
**Done when:** Format is agreed and documented

---

### Task 3.2 — Capture backlog of known corrections
**What:** Based on this session's work, document the corrections we already know:
1. `.verdict.txt` files are local Windows files, not ledger entries
2. `batch_ingest` reads FROM ledger, writes TO FalkorDB
3. Karma has no access to Colby's local filesystem via /v1/chat
4. Karma's model is GLM-4.7-Flash (not Open WebUI / Ollama)
5. FalkorDB graph name is `neo_workspace` (not `karma`)

**Who:** CC writes `Memory/corrections-log.md`
**Done when:** Backlog documented and pushed to vault-neo

---

### Task 3.3 — Session-end CC protocol: identify and capture corrections
**What:** Add to CC's session-end checklist:
1. Scan session for moments where Karma made an error that was corrected
2. For each: write a correction entry to `Memory/corrections-log.md`
3. If 3+ corrections exist that aren't in the system prompt: flag to Colby for system prompt update

**Who:** CC follows this at session end (no code required — it's a discipline)
**Done when:** At least one correction from this session is captured and added to corrections-log.md

---

### Task 3.4 — System prompt update cycle
**What:** After accumulating 3+ corrections, CC proposes a system prompt update:
1. Draft the addition to `00-karma-system-prompt-live.md`
2. Present to Colby for approval
3. On approval: commit, push, pull on vault-neo, verify

**Frequency:** After each session that surfaces corrections (not every session)
**Who:** CC proposes, Colby approves, CC deploys
**Done when:** First system prompt update from a correction has been deployed and verified retained in Karma's next conversation

---

**Phase 3 acceptance test:**
1. Correction identified in a session
2. Added to corrections-log.md
3. Incorporated into system prompt on next update cycle
4. Fresh conversation with Karma: she demonstrates she knows the corrected fact without being told

---

## Phase 4: v7 Unfinished Business
**Goal:** Complete v7 items that were "IN PROGRESS" and never finished.
**Effort:** 1 session
**Depends on:** Nothing (independent)

---

### Task 4.1 — Budget guard (v7 Task 5)
**What:** Prevent unexpected cost overruns. If daily spend exceeds threshold, stop routing to paid model.
**Context:** v7 listed this as NOT DONE. Still not done.
**Approach:** Add spend tracking + daily cap check to hub-bridge routing logic.

---

### Task 4.2 — Capability gate (v7 Task 6)
**What:** Certain operations (deep reasoning, tool use) should only be allowed for authenticated users or specific contexts.
**Context:** v7 listed this as NOT DONE.
**Approach:** Check headers/token before routing to gpt-4o-mini.

---

### Task 4.3 — Promote lane=NULL episodes (v7 Task 7)
**What:** 1239 Episodic nodes (now more) have `lane=NULL` — they were batch-ingested without lane assignment.
**Context:** v7 listed this as needed. Still pending.
**Approach:** A bulk Cypher update on FalkorDB to assign lane based on tags.
```cypher
MATCH (e:Episodic) WHERE e.lane IS NULL SET e.lane = 'episodic'
```

---

## Execution Guidelines

### How to work through this plan

1. **One phase at a time.** Don't start Phase 2 while Phase 1 is in progress.
2. **Run acceptance tests.** Don't mark a phase done without passing the acceptance test.
3. **Use TDD for code.** Any new code (indexer, context injection changes) follows red → green → refactor.
4. **Use the deploy skill.** Any hub-bridge rebuild uses the `/deploy` skill — not manual docker commands.
5. **Commit after each task.** Small commits with clear messages. Push to GitHub.
6. **Update MEMORY.md after each task.** Pre-commit hook enforces this.
7. **Colby approves content changes.** System prompt rewrites, direction.md rewrites — CC drafts, Colby approves.
8. **Never edit on vault-neo directly.** Edit locally → commit → push → pull on droplet.

### What to do when stuck

| Problem | Action |
|---------|--------|
| ChromaDB collection API returns unexpected structure | Read the running container's actual API, don't assume from docs |
| System prompt change causes unexpected behavior | Revert to previous version immediately, diagnose separately |
| Context injection causes GLM token overflow | Reduce K (fewer semantic results) or reduce context budget |
| Phase 2 takes longer than expected | Ship Phase 1 independently — it's the highest value |

---

## Timeline Estimate

| Phase | Effort | Sessions | Value |
|-------|--------|----------|-------|
| Phase 1: Fix self-knowledge | ~4 hours | 1 | **Highest** — fixes root cause of all errors |
| Phase 2: Fix retrieval | ~8-12 hours | 1-2 | **High** — makes memory actually useful |
| Phase 3: Correction capture | ~2 hours | 0.5 | **High** — compounds over time |
| Phase 4: v7 cleanup | ~4-6 hours | 1 | **Medium** — important but not urgent |

**Recommended order:** 1 → 3 → 2 → 4
(Phase 3 is fast and complements Phase 1; Phase 2 is more complex and benefits from the correct system prompt being in place first)

---

## What Comes After v8

After v8 is complete:
- Karma accurately knows herself
- Karma retrieves relevant memories, not just recent ones
- Corrections accumulate and get incorporated

**Then** the DPO/fine-tuning question becomes meaningful — because you'll have a foundation worth fine-tuning on. Right now, fine-tuning on a system that doesn't know what it is would just bake in the wrong self-model faster.

The question for v9: **what does Karma DO with her memories?** Not just recall them — but reason about them, connect them, surface patterns. That's where the "peer" part of the north star becomes real.
