# Phase K-2: Anthropic Docs Scrape
Created: 2026-03-23 (Session 129 wrap)
Completed: 2026-03-23 (Session 130)

## Goal
Scrape all Anthropic documentation pages into `docs/anthropic-docs/`.
Batch ingest to vault ledger → FAISS indexed → searchable via FAISS.
Gate: 150+ pages scraped, indexed in FAISS, docs returned by search.

## Status: COMPLETE

## SCOPE CORRECTION (2026-03-23, K-2 Task 1)
- Sitemap.xml does not exist at docs.anthropic.com or platform.claude.com/docs
- Actual URL: platform.claude.com/docs/en/
- Real page count: **128 pages** (not 606 — original estimate was 4.7x too high)
- Inventory written to: docs/anthropic-docs/inventory.md
- Separate site: code.claude.com/docs/en/ — 30 pages (INCLUDED in scope, Session 130)
- Total scraped: **170 files** (128 platform + 30 claude-code + inventory/misc)

## Task 1 — Inventory docs.anthropic.com sitemap
<verify>Get full list of pages to scrape.</verify>
<done>true — 128 pages inventoried via RSC nav data. inventory.md written. Scope corrected.</done>

## Task 2-5 — Scrape all sections (parallel agents)
<verify>All sections scraped: agent-sdk (27), api (30+), agents-and-tools (18), build-with-claude (28+), test-and-evaluate (8), about-claude (12), claude-code (25), home/resources (6)</verify>
<done>true — 170 .md files in docs/anthropic-docs/. Sections: agent-sdk/, api/, agents-and-tools/, build-with-claude/, test-and-evaluate/, about-claude/, claude-code/. All have frontmatter with source URL and section tag.</done>

## Task 5b — Inventory + scrape code.claude.com/docs/en/
<verify>30 Claude Code pages scraped and saved to docs/anthropic-docs/claude-code/</verify>
<done>true — 25 pages written + 5 pre-existing = 30 total. claude-code-inventory.md created.</done>

## Task 6 — Batch ingest to vault ledger
<verify>All docs/anthropic-docs/*.md files POSTed to /v1/ingest. Ledger entries tagged anthropic-docs created.</verify>
<done>true — 170/170 files ingested. 124 ledger entries with tags ["anthropic-docs","knowledge","k2-scrape","capture"]. Scripts/batch-ingest-docs.ps1 created for future re-ingestion.</done>

## Task 7 — Verify FAISS indexing
<verify>anr-vault-search has reindexed. FAISS search with "claude tool use" returns docs results.</verify>
<done>true — FAISS index has 2551 vectors (up from 2185). Search query "agent SDK hooks PreToolUse PostToolUse" returns hooks.md at 0.487. Query "MCP connector remote servers" returns mcp-connector.md at 0.556. anr-vault-search fixed: (1) value-key indexing, (2) coordination tag filter, (3) null-ID synthetic line_N assignment.</done>

## Gate Check
<verify>150+ pages scraped, all in docs/anthropic-docs/, all indexed in FAISS, FAISS search returns docs results</verify>
<done>true — 170 files scraped, 124 ledger entries, 2551 FAISS vectors, docs appear in top results for SDK/MCP queries</done>

## Lessons / Pitfalls
- P056: /v1/ingest entries get id:null — search_service.py needs line_N synthetic IDs or they all deduplicate
- P057: should_index_entry must check content["value"] key for doc/knowledge entries (not just assistant_message/message)
- P058: 195k coordination bus entries also use {"value":"..."} — always filter by tags when adding value-key indexing
- WebFetch is faster than Playwright for static docs (no browser overhead). Use for bulk doc scraping.
- 6-agent parallel dispatch covers 170 pages in ~15 min (vs sequential ~4 hours)
