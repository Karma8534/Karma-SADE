# HARVEST Skill — Design Document
**Date:** 2026-03-21
**Owner:** CC (Ascendant)
**Status:** APPROVED — implementing

## Purpose
Build and maintain CC's permanent knowledge base from accumulated session history.
267 .md files covering 108+ sessions of project work, decisions, failures, pivots.
Without this, CC re-discovers known mistakes every session. With this, CC starts from institutional memory.

## Trigger
`/harvest` — one word, re-runnable, idempotent via watermark.

## Approach Selected
**CC direct read + K2 pattern push** (Approach B+C hybrid):
- CC reads each .md file directly (no K2 dependency, observations land in real-time)
- Skill synthesis done by CC inline (no Anthropic API needed for synthesis)
- K2 watchdog_extra_patterns.json updated via SSH at end (closes Vesper loop)

## Architecture

```
docs/ccSessions/*.md (267 files, all subfolders)
    ↓ Pre-scan: rename subfolder duplicates as *-Dup.md
    ↓ Priority order: ccSession* → KSession*/Karma* → plan docs → From CAI/
    ↓ CC reads each file (chunked if >200 lines)
    ↓ Extracts: PITFALL / DECISION / PROOF / DIRECTION
    ↓ Quality bar: type + title <80 chars + actionable body (not status narration)
    ↓ Dedup: claude-mem search before each save
    ↓ Saves to claude-mem (project="Karma_SADE")
    ↓ Appends to Karma2/cc-scope-index.md
    ↓ Moves file to docs/ccSessions/Learned/ (preserving subfolder structure)
    ↓ Writes .harvest_watermark.json after EACH file (crash-safe)
    ↓ After all files: synthesize new karma-pitfall-*.md skill files
    ↓ Synthesize Karma2/cc-big-picture.md (project arc narrative)
    ↓ SSH K2: merge top PITFALLs into watchdog_extra_patterns.json
    ↓ Update cc_context_snapshot.md Active Work section
    ↓ Verify PLAN.md gates, save completion observation, update PLAN.md
```

## 18 Gaps Resolved (systematic analysis 2026-03-21)

| Gap | Resolution |
|-----|-----------|
| G1 no project arc | cc-big-picture.md synthesized at end |
| G2 no ongoing growth | resurrect Step 1f detects new files; nightly scheduled task |
| G3 skill missing | created this session |
| G4 Learned/ missing | HARVEST creates on first run |
| G5 no per-file watermark | .harvest_watermark.json written after each file |
| G6 15+ filename duplicates | pre-scan renames subfolder copies as *-Dup.md |
| G7 2849-line files | chunked into 200-line windows, 20-line overlap |
| G8 resurrect gap | Step 1f (new files detection) + Step 1g (cc-big-picture.md) added |
| G9 snapshot not updated | HARVEST Step 6 updates cc_context_snapshot.md |
| G10 watchdog patterns stale | HARVEST Step 5 SSHes K2, merges PITFALL patterns |
| G11 quality filter undefined | 3 conditions: type + title <80 + actionable body |
| G12 no verification gate | HARVEST Step 7 checks all PLAN.md PRE-PHASE gates |
| G13 IndexedDB pending | documented as Corpus Phase 2; HARVEST re-runnable |
| G14 no error resilience | failed saves → cc-harvest-pending.jsonl, retried next run |
| G15 no priority order | ccSession* first → KSession* → plan → From CAI/ |
| G16 new skill synthesis | clusters by topic, writes new karma-pitfall-*.md for 3+ file patterns |
| G17 cc-scope-index not updated | HARVEST appends new entries additively |
| G18 no completion record | save_observation at end + PLAN.md update |

## Ongoing Growth Architecture

```
NOW:          /harvest runs on 267 .md files → 50+ observations → skills → big-picture
PER-SESSION:  wrap-session saves DECISION/PROOF/PITFALL from each session (already in place)
AT-RESURRECT: Step 1f detects new unprocessed files (surfaces count)
              Step 1g reads cc-big-picture.md → PROJECT ARC context block
HOURLY:       KarmaSnapshotHourly task refreshes cc_context_snapshot.md (just deployed)
NIGHTLY:      Windows Scheduled Task runs /harvest at 3am on any new ccSessions/ files
CORPUS-2:     IndexedDB sessions extracted → /harvest auto-processes via watermark
K2-LOOP:      watchdog_extra_patterns.json updated → K2 watchdog learns session patterns
```

## Memory Layer Map

| Layer | File | Updated By | Purpose |
|-------|------|-----------|---------|
| Atomic facts | claude-mem | HARVEST + wrap-session | Searchable observations |
| Index/rules | Karma2/cc-scope-index.md | HARVEST + wrap-session | Resurrect context |
| Pattern skills | .claude/skills/karma-pitfall-*.md | HARVEST | Prevent repeating mistakes |
| Project arc | Karma2/cc-big-picture.md | HARVEST | Full project narrative |
| Session state | cc_context_snapshot.md | wrap-session + hourly task + Stop hook | /cc bridge context |
| K2 learning | watchdog_extra_patterns.json | HARVEST | Vesper pipeline patterns |

## Verification Gates (PLAN.md PRE-PHASE)
- [ ] New claude-mem observations ≥ 50 net new
- [ ] karma-pitfall-*.md files ≥ 10 total (already 10 — report additions)
- [ ] watchdog_extra_patterns.json updated on K2
- [ ] cc-scope-index.md has new entries
- [ ] cc-big-picture.md written and readable
