# Karma SADE Session Summary (Latest)

**Date**: 2026-03-05
**Session**: 67
**Focus**: Security fix (deep-mode tool gate) + v9 Phase 3 persona coaching + v9 Phase 4 design

---

## What Was Done

### 1. Security Fix — Deep-Mode Tool Gate (commit 41b2c06)
**Problem:** Session 66 wired GLM tool-calling but called `callLLMWithTools()` unconditionally at line 1271. Standard chat requests (deep_mode=false) got full tool execution capability.

**Fix:** Branched at call site:
```javascript
const llmResult = deep_mode
  ? await callLLMWithTools(model, messages, max_output_tokens)
  : await callLLM(model, messages, max_output_tokens);
```

**Verified:** Standard smoke test returned ok:True, no tool execution, deep_mode:false in telemetry.

---

### 2. v9 Phase 3 — Persona Coaching (commit f90cea7)
**Deployed to:** `Memory/00-karma-system-prompt-live.md` → git pull + docker restart anr-hub-bridge

**Changes:**
1. Fixed stale tool list on line 26: `read_file, write_file, edit_file, bash` → `` `graph_query`, `get_vault_file` ``
2. New section **"How to Use Your Context Data"** added after "Your Memory Architecture":
   - When `## Entity Relationships` in karmaCtx → weave connections unprompted
   - When `## Recurring Topics` in karmaCtx → calibrate depth to top topics
   - When deep mode → proactively call `graph_query` before answering strategic questions

**Result:** KARMA_IDENTITY_PROMPT: 10,415 → 11,850 chars. Behavioral coaching deployed.
**Acceptance test PENDING:** Ask Karma about a Recurring Topic; verify she references relationship data unprompted.

---

### 3. karma-server LLM Analysis (no code changes)
- router.py confirmed dead code path (karma-terminal last capture 2026-02-27)
- Graphiti uses OpenAI directly — cannot swap without rewrite
- Current spend: $0.12/month. Model swap not worth it.
- ANALYSIS_MODEL config bug (defaults to glm-4.7-flash but OpenAI client at api.openai.com): non-impactful

---

### 4. v9 Phase 4 Design — Karma Write Agency
**Design approved (obs #4032).** Three-in-one mechanism:
- **Write gate**: thumbs up/down gates whether Karma's proposed memory note lands
- **DPO signal**: every rated response = preference pair (goal: 20+)
- **Corrections pipeline**: 👎 + text → corrections-log.md

**API:** `POST /v1/feedback {turn_id, rating: +1/-1, note?: string}` (turn_id already in every /v1/chat response)

**New tools for Karma:** `write_memory(content)`, `annotate_entity(name, note)`, `flag_pattern(description)`

**Routing:**
- 👍 no text → write Karma's proposed note verbatim
- 👍 + text → write user's phrasing instead
- 👎 no text → discard
- 👎 + text → corrections-log.md

**Web UI:** Thumbs up/down already present at hub.arknexus.net. Text box already opens on click. No UI build needed initially.

**NOT YET IMPLEMENTED.** Design approved, next session starts implementation.

---

## What's Live in Production

| Component | Status |
|-----------|--------|
| Deep-mode tool gate | ✅ LIVE (commit 41b2c06) |
| v9 Phase 3 persona coaching | ✅ LIVE (commit f90cea7) |
| GLM tool-calling (Session 66) | ✅ LIVE |
| graph_query + get_vault_file tools | ✅ LIVE |
| Entity Relationships + Recurring Topics | ✅ LIVE |
| FalkorDB: 3621+ nodes | ✅ LIVE |
| batch_ingest cron (every 6h, Graphiti watermark) | ✅ LIVE |
| FAISS semantic search | ✅ LIVE |
| Brave Search | ✅ LIVE |

## What's Broken / OPEN

| Problem | Status |
|---------|--------|
| karma-verify smoke test checks wrong response key (reply vs assistant_text) | OPEN |
| v9 Phase 3 acceptance test not yet run | PENDING |

## What's Next

1. **Run acceptance test for v9 Phase 3**: Ask Karma about a topic in her Recurring Topics → verify she references entity relationship data unprompted
2. **v9 Phase 4 kickoff**: `/brainstorm` → design doc → plan → implement write_memory tool + POST /v1/feedback endpoint
3. **Fix karma-verify skill**: Update smoke test key from "reply" to "assistant_text"
