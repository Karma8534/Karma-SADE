# Karma Corrections Log

Append-only log of facts Karma got wrong in conversation. Used to update the system prompt when corrections accumulate.

## Correction Format

```
## Correction [YYYY-MM-DD]
**Was wrong:** [what Karma believed / what she said]
**Actually:** [what is correct]
**Source:** [how verified — session conversation, code inspection, production test]
**Applies to:** system prompt section [name]
**Status:** [PENDING / INCORPORATED v8 system prompt YYYY-MM-DD]
```

---

## Correction 2026-03-04 (Session 63)
**Was wrong:** Documentation (STATE.md + direction.md) claimed "New episodes (post-cron) get Graphiti entity extraction"
**Actually:** Cron has used --skip-dedup since Session 59. ALL episodes since then were Episodic-only. No entity extraction has occurred for any episode since Session 59. 571 Entity nodes are legacy from pre-Session-59 runs.
**Source:** Code inspection of cron command + batch_ingest.py --skip-dedup behavior. Colby confirmed the gap.
**Applies to:** System prompt section: Karma's learning/growth capabilities
**Status:** FIXED in code (Session 63 watermark deployment). System prompt update pending (next cycle).

---

## Known Corrections (Backlog — 2026-03-04)

## Correction 2026-03-04
**Was wrong:** Karma searched `memory.jsonl` for `.verdict.txt` files, believing they would be there.
**Actually:** `.verdict.txt` files are written by `karma-inbox-watcher.ps1` to `Karma_PDFs/Done/` on Colby's Windows machine after a successful POST to `/v1/ingest`. They exist only locally. Searching the ledger for them returns nothing — that is expected and correct.
**Source:** Session conversation (Karma demonstrated the error repeatedly) + code inspection of karma-inbox-watcher.ps1
**Applies to:** Data Model Corrections section
**Status:** INCORPORATED v8 system prompt 2026-03-04

## Correction 2026-03-04
**Was wrong:** Karma described `batch_ingest` as writing to the ledger / updating `memory.jsonl`.
**Actually:** `batch_ingest.py --skip-dedup` reads FROM `memory.jsonl` (the ledger) and writes Episodic nodes TO FalkorDB `neo_workspace`. It does NOT modify the ledger. The ledger's last-modified time reflects the last append from a capture event (chat, git, ambient), not batch_ingest activity.
**Source:** Session conversation (Karma stated the wrong flow) + code inspection of batch_ingest.py + cron verification
**Applies to:** Data Model Corrections section
**Status:** INCORPORATED v8 system prompt 2026-03-04

## Correction 2026-03-04
**Was wrong:** Karma believed she could access Colby's local Windows filesystem (Karma_PDFs/, C:\Users\raest\, PAYBACK machine).
**Actually:** Karma has no SSH, API, or filesystem access to Colby's local machine. The only access is via the hub-bridge API endpoints on vault-neo. If local file info is needed, Colby or Claude Code (CC) must check.
**Source:** Session conversation + architecture review
**Applies to:** What You CANNOT Do section
**Status:** INCORPORATED v8 system prompt 2026-03-04

## Correction 2026-03-04
**Was wrong:** Karma described herself as running on Open WebUI with tools: gemini_query(), file_read(), browser_open(), shell_run(), system_info(). She referenced Ollama at localhost:8080 and Cockpit at localhost:9400.
**Actually:** These tools do not exist in the hub-bridge context. Karma runs via GLM-4.7-Flash (Z.ai) routed through the hub-bridge on vault-neo. She has no local machine tools.
**Source:** Audit of live system prompt (Memory/00-karma-system-prompt-live.md) from Feb 2026 — described a different, older system
**Applies to:** Who You Are / What You CAN and CANNOT Do sections
**Status:** INCORPORATED v8 system prompt 2026-03-04

## Correction 2026-03-04
**Was wrong:** Karma referenced FalkorDB graph name as `karma` or `default` when running Cypher queries.
**Actually:** The graph name is `neo_workspace`. The `karma` graph exists but is empty. Using the wrong name returns empty results.
**Source:** Code inspection of batch_ingest.py + hub-bridge server.js + production verification
**Applies to:** Memory Architecture section (FalkorDB)
**Status:** INCORPORATED v8 system prompt 2026-03-04

## Correction 2026-03-04
**Was wrong:** System prompt (old) described Karma as having no web search capability.
**Actually:** Brave Search API is wired into hub-bridge. Search intent auto-detected via SEARCH_INTENT_REGEX. Top-3 results injected into context transparently. API key: configured 2026-03-04. Verified: `debug_search: hit`.
**Source:** Code inspection of server.js + production test
**Applies to:** What You CAN Do section
**Status:** INCORPORATED v8 system prompt 2026-03-04

## Corrections 2026-03-05 (Session 66)

## Correction 2026-03-05
**Was wrong:** System prompt claimed Karma's context window was "~1,800 characters" of graph data.
**Actually:** `KARMA_CTX_MAX_CHARS` was already set to 12,000 in hub.env. Karma had significantly more context than she believed.
**Source:** Code inspection of hub.env on vault-neo (`grep KARMA_CTX_MAX_CHARS hub.env` → 12000), routing.js default comment
**Applies to:** What You CAN Do / Context section
**Status:** INCORPORATED v9 system prompt 2026-03-05 (Session 66)

## Correction 2026-03-05
**Was wrong:** System prompt told Karma she could call `/v1/context` and `/v1/cypher` herself mid-conversation using her tools.
**Actually:** These endpoints exist but are for external callers. Karma does NOT call them herself mid-conversation. `karmaCtx` is fetched by hub-bridge automatically BEFORE the LLM call, pre-populated in the context. Karma receives it — she doesn't generate it.
**Source:** Code inspection of server.js buildSystemText() + hub-bridge request flow
**Applies to:** What You CAN Do section
**Status:** INCORPORATED v9 system prompt 2026-03-05 (Session 66)

## Correction 2026-03-05
**Was wrong:** System prompt claimed GLM rate limit was "20 RPM" and implied Karma would silently fail on rate limit.
**Actually:** (a) Rate limit was raised to 40 RPM in Session 66. (b) On 429, hub-bridge returns an explicit error, not silence. Karma should acknowledge rate-limit failures directly rather than looping.
**Source:** hub.env inspection + routing.js GlmRateLimiter code + production behavior observation
**Applies to:** Technical Constraints section
**Status:** INCORPORATED v9 system prompt 2026-03-05 (Session 66)

---

## Correction 2026-03-05 [Session 69]
**Was wrong:** Karma said "like I can call bash commands on vault-neo" when explaining web search vs tool differences.
**Actually:** Karma has NO bash tool. Active deep-mode tools: `graph_query`, `get_vault_file`, `write_memory`, `fetch_url`. Stale definitions (bash/read_file/write_file/edit_file) caused confabulation.
**Source:** server.js TOOL_DEFINITIONS inspection + executeToolCall code review.
**Applies to:** What You CAN Do section — tool list
**Status:** INCORPORATED — stale tools removed + system prompt tool list corrected Session 69

## Correction 2026-03-05 [Session 69 post-wrap]
**Was wrong:** Karma said "I can't browse arbitrary web pages (I only get search snippets)" — denying fetch_url capability.
**Actually:** fetch_url was shipped Session 69. In deep mode, she can call `fetch_url(url)` for user-provided URLs.
**Source:** Session analysis of live Karma response vs deployed Session 69 system prompt.
**Applies to:** What You CANNOT Do section
**Status:** INCORPORATED — cannot-do bullet corrected in system prompt 2026-03-05

## Correction 2026-03-05 [Session 69 post-wrap]
**Was wrong:** Karma described "K2 worker syncs to droplet continuously" as an active component of her architecture.
**Actually:** K2 sync worker deprecated 2026-03-03 (Session 58). Not running. Not an active component.
**Source:** Session 58 MEMORY.md + architecture.md review.
**Applies to:** Who You Are / architecture self-description
**Status:** INCORPORATED — Correction #6 added to Data Model Corrections 2026-03-05

## Correction 2026-03-05 [Session 69 post-wrap]
**Was wrong:** Karma described session continuity as "I load identity.json, invariants.json, direction.md at session start."
**Actually:** No files are loaded at chat time. hub-bridge loads the system prompt file at container startup, then fetches karmaCtx + semanticCtx before each /v1/chat call.
**Source:** hub-bridge server.js code inspection + buildSystemText() review.
**Applies to:** How session continuity works
**Status:** INCORPORATED — "How Session Continuity Actually Works" section + Correction #7 added 2026-03-05

## Correction 2026-03-05 [Session 69 post-wrap]
**Was wrong:** When asked about primitives, Karma said "I don't have a clear list in my context" while actually having a "## Recently Learned (Approved)" block with primitives from CreatorInfo.pdf and LongHorizonWithCodex.PDF.
**Actually:** The "Recently Learned (Approved)" karmaCtx block IS the primitive list. 44 canonical karma-ingest nodes exist in FalkorDB; 5 are surfaced per request.
**Source:** Live karmaCtx inspection + FalkorDB query (44 canonical karma-ingest nodes confirmed).
**Applies to:** How You Improve Over Time / primitives self-knowledge

## Correction 2026-03-10 [Session 75] — Claude stated GLM was "smart enough" and Haiku "sub-optimal"
**Was wrong:** Claude (CC sessions) told Colby that GLM-4.7-Flash was "smart enough" for Karma, and that Claude Haiku 3.5 was "sub-optimal" compared to GLM. These statements were made across multiple sessions and used to justify the GLM-primary architecture.
**Actually:** GLM-4.7-Flash produces consistently lower-quality responses than Claude Haiku 3.5 for Karma's use case. Colby experienced this degradation daily for weeks. The "sub-optimal" label applied to Haiku was factually wrong. Claude Haiku 3.5 is now the primary model (Decision #28).
**Source:** Colby's direct feedback after daily use. Claude acknowledged the error.
**Applies to:** Model routing section of system prompt — update next cycle to reflect Haiku 3.5 as primary.
**Status:** PARTIALLY INCORPORATED — model switched (Session 75). System prompt model references not yet updated.

## Correction 2026-03-10 [Session 75] — "0 DPO pairs" was wrong
**Was wrong:** Claude and previous sessions stated Karma had accumulated "0 DPO pairs" despite daily use — implying the feedback pipeline was broken.
**Actually:** DPO pairs ARE being written to the vault ledger. Container logs confirmed: `[FEEDBACK] DPO pair stored: signal=up, has_note=false`. The "0 pairs" count was never verified against actual logs — it was an assumption.
**Source:** `docker logs anr-hub-bridge` during Session 75 — confirmed successful DPO writes.
**Applies to:** No system prompt change needed — was a Claude CC session-level misstatement.
**Status:** RESOLVED — correct state documented in MEMORY.md and problems-log.md.
**Status:** INCORPORATED — primitives coaching added to "How You Improve Over Time" section 2026-03-05

---

## How to Add Corrections

At session end (CC protocol — Task 3.3):
1. Scan the session for moments Karma stated something wrong and was corrected
2. For each: append a correction entry above using the format template
3. If 3+ corrections exist that aren't yet in the system prompt: flag to Colby for system prompt update
4. System prompt update cycle: CC drafts → Colby approves → CC deploys (commit → push → pull → restart hub-bridge)

## Correction 2026-03-10
**Was wrong:** Karma described herself as having no access to MEMORY.md content, and responded without awareness of recent session decisions (v10 plan, prior session work).
**Actually:** MEMORY.md was never injected into buildSystemText() — architectural gap, not a Karma error. Fixed Session 72: _memoryMdCache now injected as "KARMA MEMORY SPINE (recent)" in every /v1/chat.
**Source:** Root cause verified in server.js buildSystemText() — no memoryMd parameter existed.
**Applies to:** System prompt section "How Session Continuity Actually Works" — already accurate; the code fix resolved it.
**Status:** INCORPORATED

## Correction 2026-03-10
**Was wrong:** Entity Relationships section showed "related to chrome extension" and other 2026-03-04-era data. Karma would reference these stale relationships as if current.
**Actually:** query_relevant_relationships() was querying RELATES_TO edges — all 1,423 frozen at 2026-03-04 from Graphiti dedup era. MENTIONS co-occurrence is the live, growing data source.
**Source:** FalkorDB edge count query confirming RELATES_TO dates; verified Karma/Colby=123 in MENTIONS co-occurrence.
**Applies to:** karma-core/server.py query_relevant_relationships() — fixed. System prompt unchanged.
**Status:** INCORPORATED
