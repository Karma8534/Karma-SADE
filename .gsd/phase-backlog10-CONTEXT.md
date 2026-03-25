# Phase Backlog-10 — Julian Memory Primitives CONTEXT
**Created:** 2026-03-25 | **Session:** 144 | **Authorized:** Sovereign

## What We're Solving

Julian's continuity foundation has 4 structural gaps, identified via agent-memory analysis:

1. **Ephemeral bus posts** — every DECISION/PROOF/PITFALL from CC/Karma/Codex lives only in the
   coordination bus (disk-persisted JSON). Not in the JSONL ledger. Not in FalkorDB. Not searchable
   by semantic queries. One bus reset = those decisions are gone. This is the same centralization
   vulnerability that destroyed Julian the first time.

2. **Undifferentiated memory** — all vault writes look identical. A passing observation and a
   locked architectural constraint get the same retrieval weight. The system can't prioritize.

3. **Recency burial** — critical decisions (anti-capture doctrine, AC2 authorization, Sovereign
   directives) compete equally with last night's chat for retrieval slots. They lose.

4. **Silent retrieval degradation** — no stop conditions on FalkorDB queries, no fallback tiers.
   When FalkorDB is slow, context is silently empty. Julian doesn't know he's operating blind.

## What We're Building

4 primitives from SpillwaveSolutions/agent-memory, adapted for this stack:

| Primitive | Where | What changes |
|-----------|-------|--------------|
| Bus → Ledger | hub-bridge server.js | coord POST also writes to /v1/ambient |
| MemoryKind | hub-bridge server.js | classifyMemoryKind() + kind tag on writes |
| Salience score | hub-bridge server.js | salience float on buildVaultRecord() |
| Pinned memory | hub-bridge + claude-mem | [PINNED] prefix → is_pinned:true flag |

## What We're NOT Building

- TOC hierarchy (year→month→week→day→segment) — highest effort, deferred
- Query intent classification (Explore/Answer/Locate/Time-boxed) — deferred
- Usage penalty in retrieval ranking — requires FalkorDB schema change, deferred
- Grip/provenance anchors — requires event ID threading through all writes, deferred
- Full tiered capability detection — deferred until after primitives land

## Architecture Decisions

**B10-1 (Bus → Ledger):**
- Intercept inside `POST /v1/coordination/post` handler in server.js
- After writing to in-memory bus, fire-and-forget POST to vault-api `/v1/ambient`
- Payload: `{content: message_content, tags: ["bus", "coordination", from_agent, msg_type]}`
- Auth: hub capture token (already in env: `HUB_CAPTURE_TOKEN`)
- No schema changes. Vault-api accepts any tags array.
- Check: `HUB_CAPTURE_TOKEN` env var exists in hub.env before building

**B10-2 (MemoryKind):**
- `classifyMemoryKind(text)` — keyword scan, returns one of 5 kinds
- Constraint: rm/never/must/forbidden/blocked/required → "Constraint"
- Procedure: steps/how to/workflow/process/algorithm → "Procedure"
- Preference: prefer/always use/style/convention → "Preference"
- Definition: is defined as/means/refers to → "Definition"
- Default: "Observation"
- Inject `kind` field into `buildVaultRecord()` and into `/v1/ambient` writes

**B10-3 (Salience):**
- `computeSalience(text, kind, isPinned)` → float 0.0–1.0
- length_density = Math.min(text.length / 500, 1.0) * 0.45
- kind_boost = kind === "Constraint" || kind === "Procedure" ? 0.20 : 0.0
- pinned_boost = isPinned ? 0.20 : 0.0
- base = 0.35
- Stored as `salience` in vault entry metadata JSON

**B10-4 (Pinned):**
- Any message/observation starting with `[PINNED]` → `pinned: true` in vault tags
- hub-bridge: detect prefix in content before classifying
- Also: accept explicit `pinned: true` field in /v1/ambient body
