# v8 Context — Design Decisions and Constraints

**Date:** 2026-03-04
**Purpose:** Lock design intent BEFORE writing code. These decisions cannot be changed mid-execution without Colby approval.

---

## What We Are Doing

Fixing the three gaps identified in the audit:
1. Karma's system prompt describes the wrong system
2. Context retrieval uses recency not relevance
3. Corrections made in conversation don't persist

In that order. Each phase is independent. Phase 1 can ship without Phase 2. Phase 2 can ship without Phase 3.

---

## What We Are NOT Doing

- **No new containers.** Everything runs inside existing karma-server and hub-bridge.
- **No fine-tuning or DPO.** That requires a different infrastructure decision (what model, what training pipeline, what budget). Not this plan.
- **No K2 integration.** Still deferred. K2 is offline.
- **No new API endpoints** unless strictly required.
- **No Aria reconciliation required.** These are operational fixes, not architectural changes. Aria's v7 design is compatible — we're implementing what v7 said but didn't finish.
- **No changes to the ledger pipeline, batch_ingest, or PDF watcher.** These work.
- **No Chrome extension revival.** Permanently shelved.

---

## Design Decisions

### Decision v8-1: System Prompt Is Authoritative for Karma's Self-Knowledge
The system prompt is the ONLY thing Karma reads at the start of every conversation. It must describe reality, not aspiration. If the system prompt says she has a tool, she'll try to use it. If it doesn't describe FalkorDB, she won't know it exists.

**Implication:** `00-karma-system-prompt-live.md` is the most important file in the system. Rewriting it is Phase 1. Nothing else matters until this is right.

### Decision v8-2: System Prompt Is Human-Approved, Not Auto-Updated
The system prompt can be updated by Claude Code, but only:
- With Colby's explicit approval of the proposed content
- After the old content is reviewed and understood

Karma does NOT auto-update her own system prompt. That path leads to drift and hallucination accumulation.

**What she CAN do:** Surface corrections during a conversation ("I had this wrong — should this be added to my system prompt?"). CC then writes it on Colby's approval.

### Decision v8-3: Retrieval Augments, Doesn't Replace System Prompt
The system prompt provides stable self-knowledge. FalkorDB context injection provides episodic memory. These are different layers. Don't mix them.

- System prompt: WHO Karma is, HOW she works, WHAT her architecture is
- Context injection: WHAT has happened recently, WHAT has been discussed

### Decision v8-4: Semantic Retrieval Uses ChromaDB (Already Deployed)
ChromaDB (`anr-vault-search` container) is already running on vault-neo. It supports vector search. The ledger entries need to be indexed into ChromaDB (they're currently not, or the index is stale), then hub-bridge queries ChromaDB with the incoming message to retrieve relevant memories.

**Alternative rejected:** Building a new vector store. ChromaDB is already there. Use it.

### Decision v8-5: Context Budget Is 3000 Characters
Current limit: 1800 chars (`KARMA_CTX_MAX_CHARS=1800`). This is too small. With semantic retrieval, we want:
- 500 chars for recent activity (last 2-3 episodes)
- 2000 chars for semantically relevant episodes (top K results)
- 500 chars for stable facts (identity, key decisions)

Total: ~3000 chars. Still small enough to not overwhelm the GLM context window.

### Decision v8-6: Correction Capture Is a CC Protocol, Not an Automated System
CC (Claude Code) identifies corrections at session end and proposes system prompt updates. Colby approves. CC deploys.

This is a HUMAN-IN-THE-LOOP process. No automated self-modification.

---

## Hard Constraints

| Constraint | Why |
|-----------|-----|
| Never edit files directly on vault-neo | Session-58 rule — droplet is deployment target only |
| All code changes via git → pull → rebuild | Established workflow |
| System prompt changes require Colby approval | Decision v8-2 |
| ChromaDB is the vector store | Decision v8-4 |
| No new paid services | Budget constraint |
| GLM-4.7-Flash remains primary | Decision #2 from locked decisions |
| Consciousness loop stays OBSERVE-only | Decision #3 from locked decisions |

---

## Success Criteria for v8

Phase 1 is done when:
- Karma can correctly describe her own architecture in a fresh conversation without being told
- Karma knows she has NO access to local machine tools via /v1/chat
- Karma knows what `.verdict.txt` files are without being corrected
- Karma knows her API endpoints and what they do

Phase 2 is done when:
- A question about a specific topic retrieves relevant episodes, not just recent ones
- ChromaDB index is current (within 24h of ledger)
- Context injection shows evidence of semantic relevance (tested by asking about old topics)

Phase 3 is done when:
- CC has a documented session-end correction-capture protocol
- At least one correction from a conversation has been captured, approved, and deployed to system prompt
- The next conversation shows the correction was retained

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| System prompt rewrite introduces new errors | Medium | High | Colby reviews before deploy; test conversation after deploy |
| ChromaDB index incomplete | High | Medium | Rebuild index from full ledger as part of Phase 2 |
| Context budget increase causes GLM token overflow | Low | Low | GLM-4.7-Flash has 128k context; 3000 chars is trivial |
| Correction capture protocol becomes bureaucratic overhead | Medium | Medium | Keep it simple — 1-3 corrections per session max |
