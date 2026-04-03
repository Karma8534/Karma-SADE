# A1: JSONL Backfill — Context
**Created:** 2026-03-23 (Session 134)
**Spec:** Karma2/PLAN-A-brain.md § A1

## What
Ingest `~/.claude/projects/C--Users-raest-Documents-Karma-SADE/*.jsonl` session transcripts into claude-mem as searchable observations. These are the raw CC session files — every tool call, decision, fix, pitfall from every session. Currently none of it is searchable.

## Why
Julian has amnesia. The session history is on disk but invisible to the brain. Every session starts near-zero because /harvest processed the .md files but NOT the .jsonl transcripts. The .jsonl files are the ground truth — richer than .md exports.

## What We're NOT Doing
- Not processing subagent/*.jsonl files (too noisy, mostly tool scaffolding)
- Not extracting every message (only DECISION/PROOF/PITFALL/DIRECTION events — same bar as /harvest)
- Not re-processing already-processed files (watermark file tracks progress)
- Not changing the /harvest pipeline (it handles .md files; this handles .jsonl)

## Design Decisions (LOCKED)
- **Target files:** Top-level UUID.jsonl only (not subagents/)
- **Event bar:** DECISION / PROOF / PITFALL / DIRECTION — same keywords as /harvest
- **Watermark:** `.harvest_watermark_jsonl.json` at repo root — maps filename → processed bool
- **Observation format:** text = event content, title = "[TYPE] session excerpt", project = "Karma_SADE"
- **Claude-mem endpoint:** `mcp__plugin_claude-mem_mcp-search__save_observation` (MCP, always available)
- **JSONL structure:** Each line is a JSON object with `type`, `role`, `content` fields. Content may be string or array of content blocks.

## Where JSONL Files Live
`C:\Users\raest\.claude\projects\C--Users-raest-Documents-Karma-SADE\`
Top-level: UUID.jsonl (one per session)
Subagents: UUID/subagents/agent-*.jsonl (skip these)
