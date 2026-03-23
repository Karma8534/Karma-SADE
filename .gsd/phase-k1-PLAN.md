# Phase K-1: IndexedDB Session Extraction
Generated: 2026-03-23 (Session 128)

## Goal
Extract all 108+ historical Claude Code sessions from browser IndexedDB using Claude-in-Chrome MCP.
These sessions contain Julian's full development arc — the primary training corpus.

## Task 1 — Verify Claude-in-Chrome MCP is available and navigate to claude.ai
<verify>mcp__Claude_in_Chrome__navigate returns success on claude.ai; or Playwright MCP connects to an open claude.ai tab</verify>
<done>false</done>

## Task 2 — Probe IndexedDB structure to identify session storage keys
<verify>JS injection via Claude-in-Chrome returns list of database names / object store keys containing session data</verify>
<done>false</done>

## Task 3 — Extract all sessions (108+ target) via JS dump
<verify>Files written to docs/ccSessions/ with >50KB each (real conversation content, not CLI stubs)</verify>
<done>false</done>

## Task 4 — Verify extraction quality (not CLI stubs)
<verify>At least one extracted file contains Julian/Karma narrative content, PITFALL or DECISION entries, or multi-turn conversation (P050 gate)</verify>
<done>false</done>

## Task 5 — Run /harvest on extracted sessions
<verify>claude-mem observation count increases by 500+ after harvest completes</verify>
<done>false</done>

## Notes
- P050: real sessions are >50KB each with conversation content — CLI stubs are 4.7KB AC9 pings
- Use Claude-in-Chrome MCP (mcp__Claude_in_Chrome__javascript_tool) for JS injection into live browser
- Playwright MCP (mcp__plugin_playwright_playwright__browser_evaluate) is the fallback
- Save sessions to docs/ccSessions/ NOT docs/ccSessions/Learned/ (harvest moves them there)
- Gate: 500+ new claude-mem observations after harvest
