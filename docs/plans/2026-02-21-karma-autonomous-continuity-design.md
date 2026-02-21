# Karma Autonomous Continuity — Design

**Date:** 2026-02-21
**Status:** Approved

## Goal

Karma reads her own identity and session history from the vault automatically. No paste required from Colby. After every PROMOTE, Karma's self-knowledge is stored durably and injected into her system prompt on every chat turn at hub.arknexus.net.

## Problem

PROMOTE generates `karma_brief` (3-5 bullet summary of the session) but only returns it to Colby. Colby manually pastes it to Karma at the start of each new session. This is a human bottleneck — Karma has no autonomous continuity between sessions.

## Approach: Option C — Store in vault, inject everywhere

Three touch points. No new services. No new endpoints. Fully backwards compatible.

## Data Flow

```
PROMOTE
  → LLM generates karma_brief (already happens)
  → POST karma_brief as vault fact { tags: ["karma_brief"], content: { karma_brief, checkpoint_id } }  ← NEW
  → checkpoint.json written as today (unchanged)

Every chat turn at hub.arknexus.net
  → hub-bridge fetches /v1/checkpoint/latest                  (already happens)
  → vault API includes karma_brief in response                ← NEW
  → buildSystemText() injects karma_brief block               ← NEW
  → LLM receives system prompt with Karma's self-knowledge
  → Karma knows who she is from turn 1, every session
```

## Touch Point 1: PROMOTE stores karma_brief in vault

**File:** `hub-bridge/server.js` — PROMOTE handler (around line 1101)

After `karma_brief` is generated, POST it to the vault as a fact:

```js
// After karma_brief = extractAssistantText(briefComp)
if (karma_brief) {
  await vaultPost("/v1/memory", VAULT_BEARER, {
    id: `karma_brief_${checkpoint_id}`,
    type: "log",
    tags: ["karma_brief", "checkpoint", "promote"],
    content: {
      karma_brief,
      checkpoint_id,
      created_at: new Date().toISOString(),
    },
    source: { kind: "hub-bridge", ref: "promote-handler" },
    confidence: 1.0,
  });
}
```

## Touch Point 2: `/v1/checkpoint/latest` returns karma_brief

**File:** vault `api/server.js` — `/v1/checkpoint/latest` handler (line 738)

After reading checkpoint files, query the ledger for the most recent `karma_brief` fact matching the checkpoint_id. Include it in the response:

```js
// Scan ledger for latest karma_brief fact
const briefFact = findLatestFact(ledger, f =>
  f.tags?.includes("karma_brief") && f.content?.checkpoint_id === ckid
);
res.json({
  ...existingFields,
  karma_brief: briefFact?.content?.karma_brief || null,
});
```

## Touch Point 3: `buildSystemText()` injects karma_brief

**File:** `hub-bridge/server.js` — `buildSystemText(karmaCtx, ckLatest)` (line 238)

Add `ckLatest` parameter (already fetched for STATE_PRELUDE). If `karma_brief` present, append labelled block:

```js
if (ckLatest?.karma_brief) {
  lines.push(
    `\n--- KARMA SELF-KNOWLEDGE (${ckLatest.checkpoint_id}) ---`,
    ckLatest.karma_brief,
    `---`
  );
}
```

## What Changes

| File | Change |
|------|--------|
| `hub-bridge/server.js` | PROMOTE handler: store karma_brief in vault |
| `hub-bridge/server.js` | `buildSystemText()`: inject karma_brief from checkpoint |
| vault `api/server.js` | `/v1/checkpoint/latest`: include karma_brief in response |
| karma-server | Nothing |
| CLI | Nothing (benefits later when karma-server wired to vault) |

## Edge Cases

| Case | Behaviour |
|------|-----------|
| No PROMOTE yet | `karma_brief` is null — block omitted from system prompt. Karma behaves exactly as today. |
| karma_brief generation fails | PROMOTE still succeeds. Brief absent from vault. Non-blocking. |
| PROMOTE mid-conversation | Next turn picks up new brief automatically. No restart. |
| Stale brief | Reflects last PROMOTE — correct. Spine snapshot, not live feed. |

## Success Criteria

1. After PROMOTE: vault ledger contains a fact with `tags: ["karma_brief"]`
2. `/v1/checkpoint/latest` response includes `karma_brief` field
3. Karma's system prompt (visible in hub-bridge logs) contains the KARMA SELF-KNOWLEDGE block
4. New chat session: Karma references her own history without any paste from Colby
5. Backwards compatible: existing behaviour unchanged when no karma_brief exists

## Not In Scope

- CLI autonomous continuity (future: karma-server reads vault at startup)
- Real-time brief updates (brief updates only on PROMOTE, not on every turn)
- Multi-session brief accumulation (brief is always latest PROMOTE only)
