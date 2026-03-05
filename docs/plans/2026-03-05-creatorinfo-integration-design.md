# Design: CreatorInfo.pdf Insights → v9 Docs Integration

**Date:** 2026-03-05
**Session:** 65
**Source:** CreatorInfo.pdf — "The File That Made the Creator of Claude Code Go Viral" (Ayesha Mughal, Medium Mar 2026)
**Status:** APPROVED — proceeding to implementation

---

## Source Summary

Medium article about Boris Cherny (Anthropic, Claude Code creator) CLAUDE.md workflow.
Two chunks ingested (ASSIMILATE). Key principles:

1. **"Every mistake becomes a rule"** — PR mistake → CLAUDE.md rule. Living document.
2. **Two-tier architecture** — global (`~/.claude/CLAUDE.md` = who you are) + project-level (= what we're building)
3. **Constitution not manual** — ~2,500 token sweet spot. Long explanations → SKILL.md, referenced not embedded.
4. **Slash commands + CLAUDE.md** — standards teaching (CLAUDE.md) + workflow triggering (commands)
5. **Team knowledge system** — corrections benefit everyone via git

## Karma's Synthesis (stored FalkorDB, lane=canonical)

**Chunk 1:** Validates two-tier architecture. identity.json (global) mirrors `~/.claude/CLAUDE.md`. direction.md (project) mirrors project CLAUDE.md. Behavioral Rules section = behavioral_contract + invariants.json.

**Chunk 3:** Validates corrections-log.md. Gap identified: current capture is session-by-session; Cherny's method uses PR-review as systematic trigger. A PR-diff → rule pipeline would make this more systematic.

## Integration Decision

| File | Change | Rationale |
|------|--------|-----------|
| `direction.md` | Add external validation note + corrections-loop rationale | Rationale for existing two-tier design |
| `.gsd/ROADMAP.md` | Add to Known Quality Gaps: PR-feedback loop formalization | Gap is real, not blocking, no scheduled work |
| `Memory/00-karma-system-prompt-live.md` | Add corrections-log purpose context | Persona iteration prep — Karma should understand WHY corrections matter |
| `CLAUDE.md` | Add token-budget principle + skills-for-long-rules note | Prevent bloat as CLAUDE.md grows |
| `.gsd/REQUIREMENTS.md` | Add systematic mistake-capture as v9 Advanced Requirement | Scope formalization |
| `Current_Plan/v9/` | Re-copy all updated files | Redundancy rule |

## Gap Disposition

**PR-review-as-feedback-loop formalization** → Known Quality Gap (not a new v9 phase).
- Existing corrections-log + Session End Protocol step 2 partially addresses this
- Full automation is infrastructure work requiring Colby approval
- Natural companion to DPO mechanism design when that gets scheduled
- Does not disrupt established v9 priority order

## What Is NOT Changing

- v9 priority order: persona iteration → MENTIONS → DPO → terminal → Tier 3 (unchanged)
- No new infrastructure, no new containers
- No code changes — documentation only
