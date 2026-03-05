# Karma Peer — v9 Plan Snapshot

**Captured:** 2026-03-05 (Session 65 start)
**Phase:** v9 IN PROGRESS — Entity Relationship Context complete; Persona iteration next

## What this folder is

A point-in-time snapshot of all planning and state documents as of the start of v9 work.
These are exact copies of the canonical files. If files diverge, the originals in the repo root are canonical.

## Files

| File | Source | Purpose |
|------|--------|---------|
| `STATE.md` | `.gsd/STATE.md` | Current decisions, blockers, verified component status |
| `ROADMAP.md` | `.gsd/ROADMAP.md` | Milestones, phases, timeline |
| `PROJECT.md` | `.gsd/PROJECT.md` | Vision, architecture, behavioral contract |
| `REQUIREMENTS.md` | `.gsd/REQUIREMENTS.md` | In-scope / out-of-scope, quality gates |
| `direction.md` | `direction.md` | What we're building and why — architecture narrative |
| `CLAUDE.md` | `CLAUDE.md` | Claude Code operator contract (full rules) |
| `00-karma-system-prompt-live.md` | `Memory/00-karma-system-prompt-live.md` | Karma's live system prompt |
| `architecture.md` | `.claude/rules/architecture.md` | Data flow, layer details, known pitfalls |
| `MEMORY.md` | `MEMORY.md` | Session history spine |

## v9 Priority Order (Session 64 decision)

1. **Persona iteration** — teach Karma to USE Entity Relationships + Recurring Topics
2. **MENTIONS edge growth verification** — confirm :MENTIONS edges growing since Session 63 watermark
3. **DPO mechanism design** — needs Colby approval (0/20 pairs)
4. **karma-terminal refresh** — stale since 2026-02-27, low priority
5. **Ambient Tier 3** — screen capture daemon; blocked on privacy approval

## System state at v9 start

- All 5 blockers resolved (Sessions 57–59)
- v8 complete: system prompt accurate, FAISS semantic retrieval live, correction capture live
- Session 63: Graphiti watermark deployed — entity extraction enabled for new episodes
- Session 64: Entity Relationships + Recurring Topics live in karmaCtx
- Session 65: CLAUDE.md strategic-question pre-read rule added
