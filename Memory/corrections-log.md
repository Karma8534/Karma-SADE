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

---

## How to Add Corrections

At session end (CC protocol — Task 3.3):
1. Scan the session for moments Karma stated something wrong and was corrected
2. For each: append a correction entry above using the format template
3. If 3+ corrections exist that aren't yet in the system prompt: flag to Colby for system prompt update
4. System prompt update cycle: CC drafts → Colby approves → CC deploys (commit → push → pull → restart hub-bridge)
