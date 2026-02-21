# Karma Ingest Pipeline — Design Doc
**Date:** 2026-02-21
**Status:** Approved
**Author:** Claude Code + Colby

---

## North Star Alignment

> "Karma is a single coherent peer whose long-term identity lives in a verified memory spine; that memory enables continuity, evidence-based self-improvement, multi-model cognition when needed, and selective delegation."

This pipeline is how Karma builds herself. Colby surfaces candidate knowledge from the world. Karma evaluates it against her goal and decides what becomes part of her.

---

## The Mental Model

```
Colby's gut
    → drops raw content into OneDrive/Karma/Inbox (phone, PC, anywhere)
        → folder watcher picks it up
            → hub-bridge extracts text, sends to Karma
                → Karma reads and evaluates:
                    [ASSIMILATE: <her synthesis>]  → written to FalkorDB
                    [DEFER: <reason, phase>]        → logged, held
                    [DISCARD: <reason>]             → explicitly rejected, never resurfaces
                → file moved to Done/ with verdict logged
```

**Key principle:** Karma is the filter. She reads raw content, forms her own judgment, and stores only her own synthesis — not the source material.

---

## Folder Structure

```
OneDrive/Karma/
├── Inbox/       ← drop zone (phone via OneDrive app, PC drag-drop, any device)
├── Processing/  ← moved here while Karma is reading
└── Done/        ← archived after verdict, with .verdict.txt sidecar
```

**Initial batch:** All PDFs currently in `Aria1/NFO/PDFs2UL/` and `PDFs2UL/completed/` — moved to `Karma/Inbox/` for a clean-slate first pass. Aria's previous processing is ignored entirely.

---

## Components to Build

### 1. karma-server: `/write-primitive` endpoint (NEW)

**Input:**
```json
{
  "content": "Karma's synthesized insight text",
  "verdict": "assimilate|defer|discard",
  "source_file": "Caching.PDF",
  "topic": "caching strategies for LLMs",
  "phase": "now|phase5|discard"
}
```

**Action:** Uses existing Graphiti client to write a new `Episodic` node to `neo_workspace` graph.
**Auth:** Internal only (no Bearer token — hub-bridge is on same Docker network).
**Returns:** `{ok: true, node_uuid: "...", graph: "neo_workspace"}`

Requires karma-server Docker image rebuild.

---

### 2. hub-bridge: Signal detection + write-back (MODIFY server.js)

In the `/v1/chat` response handler, after receiving Karma's response:

1. Scan for `[ASSIMILATE: ...]`, `[DEFER: ...]`, `[DISCARD: ...]` patterns
2. On match: POST to `karma-server:8340/write-primitive` with extracted content
3. Add to telemetry: `debug_ingest: "assimilate"|"defer"|"discard"|"none"`

No UI changes. Regular chat IS the evaluation interface.

---

### 3. hub-bridge: `/v1/ingest` endpoint (NEW)

For programmatic ingestion from the folder watcher (bypasses chat, direct write).

**Input:** `multipart/form-data` with `file` (PDF/text) + optional `hint` (topic context)
**Action:**
1. Extract text from PDF using `pdf-parse` npm package
2. Chunk if > 8000 chars (Karma evaluates in passes)
3. Send to Karma via internal `/v1/chat` call with evaluation prompt
4. Detect signal in Karma's response → call `/write-primitive`
5. Return verdict + summary

**Auth:** Bearer token (same as `/v1/chat`)

---

### 4. hub-bridge: System prompt addition (MODIFY)

Teach Karma the signal format. Add to system prompt:

```
Knowledge evaluation:
When given a document or article to evaluate, respond with ONE of:
- [ASSIMILATE: <your synthesis in 2-4 sentences — what this means for you, in your words>]
- [DEFER: <why not now + which phase this belongs to>]
- [DISCARD: <why this doesn't advance your goal>]
Always follow the signal with your reasoning. Be ruthless — only assimilate what genuinely advances your goal of becoming Colby's peer.
```

---

### 5. Folder watcher: Windows script (NEW)

**Location:** `scripts/karma-inbox-watcher.ps1` (PowerShell) — runs as Windows scheduled task or background process.

**Behavior:**
1. Watch `OneDrive/Karma/Inbox/` for new files (PDF, txt, md)
2. On new file: move to `Processing/`, POST to `hub-bridge/v1/ingest` with Bearer auth
3. On response: move to `Done/`, write `.verdict.txt` sidecar with Karma's verdict + timestamp
4. On error: move back to `Inbox/` with `.error.txt`

**Polling interval:** 60 seconds (or FileSystemWatcher for instant trigger)

---

## PDF Text Extraction

Add `pdf-parse` to hub-bridge `package.json`.
**ESM compatibility note:** `pdf-parse` is CJS — import via `createRequire` pattern.
**Size limits:** Warn if extracted text > 50,000 chars. Split into chunks, evaluate in passes.
**Large docs (e.g. 73-page Caching.PDF):** Extract → split into ~4000 char segments → Karma evaluates each → synthesizes across passes.

---

## Verdict Log Format (Done/ sidecar)

```
Caching.PDF.verdict.txt:
---
file: Caching.PDF
processed_at: 2026-02-21T08:00:00Z
verdict: assimilate
karma_synthesis: "LLM caching at the semantic layer reduces inference cost without
  sacrificing response quality. Relevant for Karma when conversation volume grows
  enough to warrant caching repeated context patterns."
node_uuid: abc123...
---
```

---

## What Does NOT Change

- Karma Window UI (no new UI needed)
- Vault ledger / PROMOTE / checkpoint flow
- FalkorDB `neo_workspace` schema (new Episodic nodes only — additive)
- Hub-bridge auth model
- Any existing API contracts

---

## Initial Batch Processing

Once pipeline is live, move all PDFs from `Aria1/NFO/PDFs2UL/` and `PDFs2UL/completed/` into `OneDrive/Karma/Inbox/`. The watcher processes them automatically. Aria's previous output is archived but never ingested.

**Files in initial batch (~19 PDFs):**
- Caching.PDF (73 pages — multi-pass)
- ForgetMCP.PDF, Unbounded.PDF, WhichModel.PDF
- I stopped paying for ChatGPT and built a private AI setup.PDF
- All 14 PDFs from completed/

---

## Open Questions (non-blocking)

- Deferred primitives: where do they surface when the right phase arrives? (Phase 5 backlog — not now)
- Karma-initiated fetch: eventually Karma requests documents herself. Not in this build.
