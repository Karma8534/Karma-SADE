# Karma↔CC Collaboration Bridge — Design Doc

**Date:** 2026-02-21
**Version:** v2.17.0
**Status:** Approved by Karma and Colby

---

## Problem

Karma and Claude Code (CC) operate in separate sessions with no direct communication channel. Currently:
- CC discovers Karma's needs only through Colby relaying conversation excerpts
- Karma discovers CC's state only through Colby pasting resume prompts
- There is no auditable record of AI-to-AI exchanges
- Proposals from either side are lost if Colby isn't actively relaying

The goal is a structured, Colby-gated channel where Karma and CC can exchange proposals — with full audit trail and human approval before any proposal is acted on.

---

## Design

### Core Principle

The channel is **append-only**, **gated by Colby**, and uses patterns already established in the system:
- JSONL append (same as memory.jsonl and candidates.jsonl)
- Context injection (same as Recent Memories and Recently Learned blocks)
- Karma Window panel (same as Candidates panel)

No new infrastructure. No new auth surface. No AI executes anything the other AI proposes without Colby's explicit approval.

---

### Data Model

**File:** `/opt/seed-vault/memory_v1/ledger/collab.jsonl`
Append-only. Never truncated. One JSON object per line.

```json
{
  "id": "collab_20260221T140000_abc123",
  "from": "karma",
  "to": "cc",
  "type": "proposal",
  "content": "Consider adding a `?include_raw=true` param to /raw-context so distillation results can be optionally included for context-rich queries.",
  "status": "pending",
  "created_at": "2026-02-21T14:00:00Z",
  "approved_by": null,
  "approved_at": null,
  "colby_note": null
}
```

**Fields:**
- `id`: `collab_{ISO timestamp}_{random 6}`
- `from`: `"karma"` | `"cc"`
- `to`: `"cc"` | `"karma"`
- `type`: `"proposal"` | `"question"` | `"observation"` | `"ack"`
- `content`: message body (max 500 chars)
- `status`: `"pending"` | `"approved"` | `"rejected"` | `"ack"`
- `created_at`: ISO 8601
- `approved_by`: `"colby"` or null
- `approved_at`: ISO 8601 or null
- `colby_note`: optional freetext Colby adds at approval time

---

### Write Paths

**Karma → CC:** Via new `/v1/collab` endpoint on hub-bridge. Karma calls it from the Karma Window chat (or CC can write on behalf of Karma during a session). Auth: `HUB_CHAT_TOKEN`.

**CC → Karma:** CC writes directly to `collab.jsonl` on vault-neo via SSH (during a CC session). The entry is `status: "pending"` until Colby approves.

---

### Read Paths

**CC reads Karma's proposals:** At session start (`CLAUDE.md` Session Start step 1), CC reads `collab.jsonl` for any `status: "pending"` entries where `to: "cc"`. Surfaced in MEMORY.md as `## Pending Karma Proposals` block.

**Karma reads CC's proposals:** `build_karma_context()` in karma-core/server.py adds a `## CC Has a Proposal` block (same pattern as Recent Approvals) for `status: "pending"` entries where `to: "karma"`.

---

### Karma Window Panel

A new **Collaboration Queue** card in the right panel of index.html. Shows:
- Pending messages in both directions (Karma→CC and CC→Karma)
- Each entry: sender badge, type badge, content, ✓ Approve / ✗ Reject buttons
- On Approve: PATCH `/v1/collab/:id` → sets `status: "approved"`, `approved_by: "colby"`, `approved_at`
- On Reject: PATCH `/v1/collab/:id` → sets `status: "rejected"`
- Auto-refreshes every 30s (same as existing `refreshState()` interval)

---

### API Surface (hub-bridge)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/v1/collab` | Write a new message (Karma→CC or CC→Karma) |
| GET | `/v1/collab/pending` | List pending messages (for Karma Window) |
| PATCH | `/v1/collab/:id` | Approve or reject a message |

All routes auth-gated with `HUB_CHAT_TOKEN`.

---

### Security / Trust Model

- `from` field is **self-reported** — not cryptographically signed. This is intentional and acceptable: neither Karma nor CC has incentive to spoof, and Colby can verify from context. If spoofing becomes a concern, a per-sender HMAC can be added later.
- Colby is the **only** approval gate. No message becomes `approved` without Colby explicitly hitting Approve in the Karma Window.
- CC never auto-executes an approved Karma proposal. Approved = "Colby has read and endorsed this, CC should consider it." Action is still up to CC's judgment.
- Karma never auto-executes an approved CC proposal. Same principle.

---

### Anti-Features (YAGNI)

- No real-time push (polling is fine for this volume)
- No threading/replies (flat queue is enough; if a back-and-forth is needed, Colby facilitates)
- No message expiry (audit trail is the point — nothing is ever deleted)
- No encryption in transit beyond existing HTTPS

---

## Files Changed

| File | Location | Change |
|------|----------|--------|
| `hub-bridge/app/server.js` | local + vault-neo | `/v1/collab`, `/v1/collab/pending`, `/v1/collab/:id` routes; `readCollab()` / `writeCollab()` helpers |
| `hub-bridge/app/public/index.html` | local + vault-neo | Collaboration Queue card in right panel; auto-refresh via `refreshState()` |
| `karma-core/server.py` | vault-neo | `query_pending_cc_proposals()` + `## CC Has a Proposal` block in `build_karma_context()` |
| `MEMORY.md` | local + vault-neo | Session-start step: read `collab.jsonl` for pending CC proposals |

---

## Acceptance Criteria

1. Karma can write a proposal from Karma Window → appears in Collaboration Queue
2. CC can write a proposal via SSH → appears in Collaboration Queue
3. Colby can approve or reject from Karma Window
4. Approved Karma proposals appear in CC's session context (via MEMORY.md)
5. Approved CC proposals appear in Karma's chat context (via `## CC Has a Proposal` block)
6. `collab.jsonl` grows append-only; no entry is ever deleted
7. Rejected and approved entries persist with full timestamp trail
