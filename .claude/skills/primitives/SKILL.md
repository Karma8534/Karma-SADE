---
name: primitives
description: Extract architectural patterns, techniques, and mechanisms from any source (URLs, local paths, pasted text) for assimilation into Karma SADE. Scores relevance, saves HIGH items to claude-mem. Trigger words: primitives, extract primitives, pull primitives.
type: rigid
---

# PRIMITIVES — Architecture Pattern Extraction & Scoring

## Purpose
Extract reusable architectural primitives from external sources and score them against Karma's current architecture. Saves high-priority findings to claude-mem for cross-session persistence.

**Accepts multiple sources per invocation.** URLs, local paths, and inline text can be mixed.

---

## STEP 1 — Parse Sources

```
1a. Parse the user's message for sources. Sources can be:
    - GitHub URLs (https://github.com/org/repo) → use gh CLI to fetch tree + key files
    - Local paths (C:\..., /home/...) → use Glob + Read to explore
    - Web URLs → use WebFetch to retrieve content
    - Inline text (pasted directly) → use as-is

1b. For each source, identify what it IS:
    - Repo: read README, file tree, key config files
    - Directory: glob for *.md, *.py, *.js, *.ts, *.json, *.yaml
    - Single file: read it
    - Pasted text: parse directly

1c. Report: "Found N sources. Processing..."
```

## STEP 2 — Extract Primitives

For each source, launch an Agent (subagent_type: general-purpose) to extract primitives in parallel when sources are independent. Each agent receives this prompt template:

```
Research [SOURCE] and extract ALL primitives — architectural patterns, techniques, mechanisms.

Karma SADE context for relevance scoring:
- Wraps Claude Code CLI into a persistent AI peer with memory and self-improvement
- Five layers: SPINE (vault-neo truth) → ORCHESTRATOR (proxy.js) → CORTEX (K2 qwen3.5:4b) → CLOUD (CC --resume) → CC (execution)
- Has: hooks, skills, agents, MCP servers, coordination bus, claude-mem (persistent memory), vault spine (FalkorDB + FAISS), Vesper pipeline (self-improvement), Kiki (autonomous agent)
- UI: unified.html chat at hub.arknexus.net + Electron scaffold
- Key constraint: zero external API dependence is the north star (no SDK lock-in)
- Auth: Max Pro subscription ($200/month), CC CLI is the stable interface

For EACH primitive found, report:
1. Pattern name (short, memorable)
2. What it does (1-2 sentences)
3. How it works (mechanism — specific files, functions, protocols)
4. Relevance to Karma (what it would replace/enhance/enable)
5. Priority: HIGH (should adopt — closes a gap or significant upgrade), MEDIUM (interesting, consider), LOW (already have equivalent or not applicable)
6. Adoption effort: TRIVIAL (<1hr), SMALL (1-4hr), MEDIUM (4-16hr), LARGE (>16hr)

Do NOT write any code. Research only. Return structured report.
```

## STEP 3 — Score & Deduplicate

```
3a. Collect all agent reports
3b. Deduplicate: if two sources describe the same pattern, merge into one entry
    citing both sources
3c. Sort by priority: HIGH first, then MEDIUM, then LOW
3d. Within each priority tier, sort by adoption effort: TRIVIAL first
3e. Count totals: "Extracted N primitives: X HIGH, Y MEDIUM, Z LOW"
```

## STEP 4 — Present Results

Present a unified report to the user with this format:

```markdown
## Primitives Extraction Report

**Sources:** [list of sources processed]
**Extracted:** N primitives (X HIGH, Y MEDIUM, Z LOW)

### TIER 1: Adopt Now (HIGH priority)

| # | Pattern | Source | Effort | What It Does |
|---|---------|--------|--------|-------------|
| 1 | Name    | repo   | SMALL  | Description |

[For each HIGH primitive: 2-3 sentence details + mechanism]

### TIER 2: Consider (MEDIUM priority)

[Same table format, details only if user asks]

### TIER 3: Note for Later (LOW priority)

[Table only, no details]

### Conflicts with Karma Doctrine
[Flag any primitives that violate: zero API dependence, no SDK lock-in,
 spine is truth, droplet-primary architecture]
```

## STEP 5 — Persist

```
5a. Save ALL HIGH-priority primitives to claude-mem as a single observation:
    title: "INSIGHT: N primitives extracted from [sources]"
    text: numbered list of HIGH primitives with pattern name + 1-line summary
    project: Karma_SADE

5b. If any HIGH primitive directly maps to a nexus.md gap or sprint item,
    note the mapping explicitly in the observation.

5c. Do NOT save MEDIUM or LOW to claude-mem (noise reduction).
    User can request explicit save of specific items.
```

## Rules

- **Parallel extraction:** When multiple independent sources are provided, launch agents in parallel. Do not process sequentially.
- **No code writing:** This skill extracts and scores. It does not implement. If the user wants to build something from the report, transition to brainstorming or writing-plans.
- **Doctrine filter:** Flag (do not silently drop) any primitive that requires SDK dependencies, external API lock-in, or violates the family doctrine. Let the user decide.
- **Dedup across sessions:** Before saving to claude-mem, search for existing primitives observations. If a prior extraction already captured the same pattern, update rather than duplicate.
- **Source attribution:** Every primitive must cite its source. No orphan patterns.
