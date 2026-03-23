# Phase K-2: Anthropic Docs Scrape (606 pages)
Created: 2026-03-23 (Session 129 wrap)

## Goal
Scrape all 606 pages of official Anthropic documentation at docs.anthropic.com into `docs/anthropic-docs/`.
Batch ingest to vault ledger → FAISS indexed → searchable via /v1/context.
Gate: 600+ pages scraped, indexed in FAISS.

## Why
CC's trained-in knowledge of Claude APIs/MCP/tool-use is suppressed. Live docs access permanently fixes
the knowledge gap (e.g., CC didn't know about 1M context window or Echo from training alone).

## Method
Playwright MCP or Claude-in-Chrome MCP → page-by-page scrape → save .md per page in `docs/anthropic-docs/` → batch ingest via hub

## Status: NOT STARTED

## Task 1 — Inventory docs.anthropic.com sitemap
<verify>Get full list of pages to scrape. Target: 606 pages. Use Playwright to fetch sitemap.xml or docs index.</verify>
<done>false</done>

## Task 2 — Scrape Claude API section
<verify>All pages under /claude-code and /claude-api saved to docs/anthropic-docs/api/</verify>
<done>false</done>

## Task 3 — Scrape MCP and Tool Use sections
<verify>All pages under /tool-use and /mcp saved to docs/anthropic-docs/mcp-tools/</verify>
<done>false</done>

## Task 4 — Scrape Claude Code and Prompt Engineering sections
<verify>All pages under /claude-code and /prompt-engineering saved to docs/anthropic-docs/</verify>
<done>false</done>

## Task 5 — Scrape Models and remaining sections
<verify>All remaining pages (models, computer-use, etc.) saved. Total count ≥ 600 files.</verify>
<done>false</done>

## Task 6 — Batch ingest to vault ledger
<verify>All docs/anthropic-docs/*.md files POSTed to /v1/ingest. Ledger entry count increased by 600+.</verify>
<done>false</done>

## Task 7 — Verify FAISS indexing
<verify>anr-vault-search has reindexed. Query /v1/context with "claude tool use" returns docs results.</verify>
<done>false</done>

## Gate Check
<verify>600+ pages scraped, all in docs/anthropic-docs/, all indexed in FAISS, /v1/context returns docs results</verify>
<done>false</done>

## Notes
- Start with sitemap.xml or docs index to get the full page list before scraping
- Save one .md per page — include URL as frontmatter header
- Use batch ingest endpoint or wip-watcher.ps1 for ingest (drop files in docs/wip/)
- Rate-limit: add delay between pages to avoid 429s
