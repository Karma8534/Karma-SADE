# Ambient Knowledge Layer — Unified Context for All Agents

**Date:** 2026-03-03
**Status:** Draft — pending review
**Inspired by:** Claude Echo (Anthropic, unreleased) — reverse-engineered primitives applied to local-first architecture
**Scope:** Cross-cutting infrastructure for Karma, Freya/Aria, Claude Code, and future agents

---

## 1. Problem Statement

Every agent in Colby's ecosystem operates in an information silo:

| Agent | Knows | Doesn't know |
|-------|-------|-------------|
| **Karma** (droplet) | Cloud chat conversations, vault ledger, FalkorDB graph | What Colby is doing locally, terminal activity, editor context |
| **Freya/Aria** (K2) | K2 chat conversations, SQLite facts/experience_log | What Karma discussed, what Claude Code built, browser activity |
| **Claude Code** (P1) | Current session files, git state, codebase | What Karma or Freya are doing, Colby's non-code workflow |
| **Chrome Extension** | Browser AI conversations | Everything outside the browser |

Result: Colby re-explains context constantly. Agents make decisions without full picture. Knowledge extracted by one agent is invisible to others.

Echo's insight: **the AI should know your context without you having to explain it.** We apply this locally — no cloud dependency, full ownership.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AMBIENT KNOWLEDGE LAYER                          │
│                                                                     │
│  CAPTURE SOURCES                    SHARED KNOWLEDGE STORE          │
│  ┌─────────────────┐               ┌──────────────────────┐        │
│  │ Claude Code     │──hook──┐      │                      │        │
│  │ (P1 sessions)   │        │      │   Vault Ledger       │        │
│  ├─────────────────┤        │      │   (droplet)          │        │
│  │ Git activity    │──hook──┤      │                      │        │
│  │ (P1 commits)    │        ├─────>│   memory.jsonl       │        │
│  ├─────────────────┤        │      │   + tagged by source │        │
│  │ Chrome Extension│──POST──┤      │   + timestamped      │        │
│  │ (browser chats) │        │      │   + searchable       │        │
│  ├─────────────────┤        │      │                      │        │
│  │ Freya/Aria      │──POST──┤      └──────────┬───────────┘        │
│  │ (K2 chats)      │        │                 │                     │
│  ├─────────────────┤        │      ┌──────────▼───────────┐        │
│  │ Screen Capture  │──POST──┘      │                      │        │
│  │ (P1/K2 ambient) │               │   /v1/context        │        │
│  └─────────────────┘               │   (query endpoint)   │        │
│                                     │                      │        │
│  CONSUMERS                          └──────────┬───────────┘        │
│  ┌─────────────────┐                           │                    │
│  │ Karma           │◄──────────────────────────┤                    │
│  │ (consciousness) │                           │                    │
│  ├─────────────────┤                           │                    │
│  │ Freya/Aria      │◄──────────────────────────┤                    │
│  │ (context + train)│                          │                    │
│  ├─────────────────┤                           │                    │
│  │ Claude Code     │◄──────────────────────────┤                    │
│  │ (session start) │                           │                    │
│  ├─────────────────┤                           │                    │
│  │ Future agents   │◄──────────────────────────┘                    │
│  └─────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────┘
```

**Principle:** Many writers, one store, many readers. The vault ledger is already append-only JSONL with timestamps and tags. We extend it with source tags and a query endpoint — not replace it.

---

## 3. Tiered Implementation

Each tier is independently useful. No tier depends on a later tier.

### Tier 1: Hooks (Zero New Infrastructure)

**What:** Capture Claude Code sessions and git activity into the vault ledger via the existing `/v1/chatlog` endpoint.

**Claude Code Session Hook:**
- Triggers on session end (or on significant milestones)
- Extracts: session summary, files modified, key decisions, blockers hit
- POSTs to `https://hub.arknexus.net/v1/chatlog` with Bearer auth
- Tag: `["capture", "claude-code", "session"]`
- Implementation: `.claude/hooks/session-end.sh` or Claude Code's built-in hook system

**Git Commit Hook:**
- Triggers on `post-commit`
- Extracts: commit message, files changed, diff stats, branch name
- POSTs to `/v1/chatlog`
- Tag: `["capture", "git", "commit"]`
- Implementation: `.git/hooks/post-commit` shell script

**Schema extension for ambient entries:**
```json
{
  "id": "amb_[timestamp]_[random]",
  "type": "ambient",
  "tags": ["capture", "[source]", "[category]"],
  "content": {
    "source": "claude-code|git|screen|aria|chrome-extension",
    "source_node": "P1|K2|droplet",
    "summary": "One-line description of activity",
    "detail": "Structured detail (varies by source type)",
    "captured_at": "ISO 8601"
  },
  "confidence": 1.0
}
```

**Cost:** Two shell scripts. Uses existing endpoint, existing auth, existing storage.

### Tier 2: Unified Context Endpoint

**What:** A new `/v1/context` endpoint on hub-bridge that any agent can query to understand "what has Colby been doing?"

**Endpoint:** `GET /v1/context`

**Query parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `hours` | int | Look back N hours (default: 2) |
| `source` | string | Filter by source: `claude-code`, `git`, `aria`, `chrome-extension`, `screen`, `all` |
| `node` | string | Filter by origin node: `P1`, `K2`, `droplet`, `all` |
| `limit` | int | Max entries returned (default: 20) |
| `summary` | bool | If true, return LLM-generated summary instead of raw entries (default: false) |

**Response:**
```json
{
  "ok": true,
  "window": "last 2 hours",
  "entries": [
    {
      "source": "claude-code",
      "source_node": "P1",
      "summary": "Session: deployed feedback feature to karma-server and hub-bridge",
      "captured_at": "2026-03-03T01:30:00Z"
    },
    {
      "source": "git",
      "source_node": "P1",
      "summary": "commit: feat: add thumbs up/down feedback to Karma chat",
      "captured_at": "2026-03-03T01:35:00Z"
    }
  ],
  "summary": "Colby has been working on Karma's feedback system deployment and Freya architecture planning."
}
```

**Who calls it:**
- **Karma's consciousness loop** — every OBSERVE cycle checks `/v1/context?hours=1` for cross-agent awareness
- **Freya/Aria** — session start loads recent context ("here's what happened since we last talked")
- **Claude Code** — resurrection script (`Get-KarmaContext.ps1`) can pull ambient context into `cc-session-brief.md`

**Implementation:** ~50 lines added to hub-bridge `server.js`. Reads from vault ledger JSONL with grep/filter. No new database.

**Cost:** One new endpoint. No new dependencies.

### Tier 3: Ambient Screen Capture

**What:** A lightweight daemon on P1 (and optionally K2) that periodically captures screenshots, runs them through a local vision model, and extracts structured observations.

**Capture daemon** (`ambient_capture.py`, runs on P1/K2):
```
Loop every N seconds (configurable, default 120):
  1. Check quiet hours → skip if active
  2. Check rate limit → skip if exceeded
  3. Check ignore list → skip if focused app matches
  4. Capture screenshot (PIL/mss)
  5. Send to local vision model (Ollama multimodal — llava, bakllava, or minicpm-v)
  6. Prompt: "Describe what the user is working on. Extract: active application, task context,
     any visible project names, file names, or error messages. Be concise."
  7. Parse response → structured entry
  8. POST to /v1/chatlog with tag ["capture", "screen", "{node}"]
  9. Delete screenshot (never stored permanently)
```

**Privacy controls (Echo's design, applied locally):**

| Control | How it works |
|---------|-------------|
| **Quiet hours** | Configurable start/end time. No capture during these hours. |
| **Weekend mode** | Optional toggle. No capture on Sat/Sun. |
| **Rate limit** | Max captures per hour (default: 30 = every 2 minutes) |
| **Ignore list** | List of app names/window titles to skip (e.g., banking apps, password managers) |
| **Ephemeral screenshots** | Screenshots are processed and immediately deleted. Only the text summary is stored. |
| **Kill switch** | `ambient_capture.py stop` or tray icon toggle |

**Vision model requirements:**
- Must run locally (no cloud). Ollama supports multimodal models.
- `minicpm-v` (~3B) or `llava:7b` — fits in VRAM alongside other workloads
- If VRAM is occupied (Freya inference on K2, training on P1), falls back to CPU inference
- Accuracy doesn't need to be perfect — "good enough to know what app and general task" is sufficient

**What this captures that nothing else does:**
- Colby working in VS Code (which files, which project)
- Colby reading documentation in a browser (which docs, which topic)
- Colby in a terminal running commands (what's happening)
- Colby in Figma, Notion, or any other tool
- Error messages on screen that Colby hasn't explicitly reported to any agent

**What this does NOT capture:**
- Anything in the ignore list (banking, passwords, private messaging if configured)
- Anything during quiet hours
- Raw screenshots are never stored — only text summaries
- No audio, no webcam, no keystrokes — screen content only

**Cost:** One Python script, one Ollama multimodal model (~3-5GB disk), negligible compute at 2-minute intervals.

---

## 4. Data Flow: How Agents Consume Ambient Knowledge

### Karma (consciousness loop — droplet)
```
Every OBSERVE cycle (60s):
  → GET /v1/context?hours=1&summary=true
  → Inject into consciousness prompt: "Recent ambient context: {summary}"
  → Karma now knows what Colby is doing across all tools
  → Can proactively comment, warn, or suggest
```

### Freya/Aria (session start + training — K2)
```
On session start:
  → GET /v1/context?hours=24&source=all
  → "Since we last talked: {entries}"
  → No re-explaining needed

On training cycle (weekly):
  → Ambient entries become supplementary training data
  → Freya learns Colby's workflow patterns, not just conversation patterns
```

### Claude Code (session start — P1)
```
Get-KarmaContext.ps1 (resurrection script):
  → GET /v1/context?hours=4&source=all
  → Append to cc-session-brief.md: "## Ambient Context"
  → CC starts with full awareness of recent activity across all agents
```

### Proactive Intelligence (future — any agent)
```
Pattern detection layer (could run on any agent):
  → Reads /v1/context over longer windows (days, weeks)
  → Detects: "Colby debugs Docker issues every Monday"
  → Detects: "Colby switches to Aria after hitting a Claude Code blocker"
  → Generates proactive nudges (Echo's "proactive notifications" primitive)
  → Feedback loop: was this nudge helpful? (reuses thumbs up/down)
```

---

## 5. Tagging Taxonomy

Every ambient entry gets consistent tags for filtering:

| Tag position | Purpose | Values |
|-------------|---------|--------|
| `[0]` | Type marker | `capture` (always) |
| `[1]` | Source tool | `claude-code`, `git`, `chrome-extension`, `aria`, `screen`, `karma` |
| `[2]` | Category | `session`, `commit`, `conversation`, `observation`, `fact`, `decision` |
| `[3+]` | Optional | Project name, language, topic |

Examples:
- `["capture", "claude-code", "session", "karma-sade"]`
- `["capture", "git", "commit", "feature/freya"]`
- `["capture", "screen", "observation", "debugging"]`
- `["capture", "aria", "conversation"]`

---

## 6. What This Enables That Echo Can't

| Capability | Echo (Anthropic) | Ambient Knowledge Layer (ours) |
|-----------|-----------------|-------------------------------|
| Data ownership | Anthropic's cloud (separate API key) | Local vault ledger on our droplet |
| Multi-agent awareness | Single agent (Echo) | Karma + Freya + Claude Code + future |
| Training data | Not available to user | Feeds directly into Freya's QLoRA pipeline |
| Cross-machine | Single desktop | P1 + K2 + droplet mesh |
| Customizable extraction | Fixed prompts | User-editable prompts per source |
| Privacy model | Anthropic's terms | You own everything, nothing leaves your network |
| Knowledge persistence | Unclear (cloud) | Append-only ledger, versioned, backed up |

---

## 7. Implementation Sequence

| Phase | What | Effort | Depends on |
|-------|------|--------|-----------|
| **Tier 1a** | Git commit hook → vault | 1 hour | Nothing |
| **Tier 1b** | Claude Code session hook → vault | 2 hours | Hook system config |
| **Tier 2** | `/v1/context` endpoint on hub-bridge | 3 hours | Tier 1 (for data to query) |
| **Tier 3a** | Screen capture daemon (P1) | 4 hours | Ollama multimodal model |
| **Tier 3b** | Screen capture daemon (K2) | 1 hour | Tier 3a (same script, copy over) |
| **Integration** | Wire Karma consciousness loop to `/v1/context` | 2 hours | Tier 2 |
| **Integration** | Wire Freya session start to `/v1/context` | 1 hour | Tier 2 |
| **Integration** | Wire `Get-KarmaContext.ps1` to `/v1/context` | 1 hour | Tier 2 |

Total: ~15 hours across all tiers. Each tier is independently shippable.

---

## 8. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Screen capture performance impact | Low | 2-minute intervals, CPU fallback, lightweight daemon |
| Vision model hallucinations | Medium | Summaries are supplementary context, not authoritative. Tagged as `confidence: 0.7` |
| Vault ledger growth from ambient data | Medium | Rate limiting + periodic archival of entries older than 30 days |
| Privacy — sensitive content captured | High | Ignore list (banking apps, password managers), quiet hours, ephemeral screenshots, kill switch |
| Ambient data noise overwhelming signal | Medium | `/v1/context` endpoint filters by source, time, and can return LLM-summarized view |
| VRAM contention (vision model vs Freya) | Medium | CPU fallback for vision model when GPU is occupied; or schedule captures during low-activity |

---

## 9. Relationship to Other Architecture Documents

- **Freya.md** — Freya's training pipeline consumes ambient entries as supplementary training data (Tier 3 → weekly export)
- **CLAUDE.md** — Session Start Protocol can be extended to pull `/v1/context` into `cc-session-brief.md`
- **resurrection-architecture.md** — Resurrection packs can include ambient context summary for richer state recovery
- **architecture.md** — Chrome extension capture is already Tier 1 equivalent for browser conversations; this extends the pattern to all tools

---

*The future of AI is not a chat box you type into when you have a question. It's a persistent presence that knows your context without being told.*

*Echo proves the concept. We build it locally, for ourselves, feeding every agent in the ecosystem.*
