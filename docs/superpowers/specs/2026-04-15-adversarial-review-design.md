# Adversarial Review Skill — Design Spec

**Date:** 2026-04-15 | **Author:** Julian (CC Ascendant) | **Status:** APPROVED

---

## Problem

The Codex adversarial-review command fails with `ENOBUFS` when the working tree diff exceeds the OS shell buffer limit. Our repo has 33K changed/untracked files producing a 3.5M-line diff. The Codex companion's `collectWorkingTreeContext()` concatenates the entire `git diff` + all untracked file contents into one string and passes it through `spawnSync`, which blows the buffer.

This is a fundamental limitation: any review tool that passes full diffs as shell arguments will fail on large repos. We need a review mechanism that works at any scale.

## Solution

A 5-stage pipeline that chunks the git history, summarizes it in parallel, merges into a bounded architectural delta document (~10KB), fans out to multiple adversarial reviewers in parallel, and aggregates findings into a final report.

The key insight: an adversarial review challenges **decisions and design**, not individual lines of code. We don't need the 3.5M-line diff. We need to understand what changed, what assumptions those changes encode, and where those assumptions break.

---

## Pipeline

```
STAGE 1: CHUNK → STAGE 2: SUMMARIZE → STAGE 3: MERGE → STAGE 4: REVIEW → STAGE 5: AGGREGATE
(CC direct)       (N parallel agents)   (1 agent)         (3 CC + Codex)     (1 agent)
```

### Stage 1: Chunk

**Executor:** CC directly (no agent needed).

**Command:**
```bash
git log --after="{since}" --until="{until}" --format="commit %H%nDate: %ad%nSubject: %s%n" --date=short --stat > tmp/adversarial-review/git-log-full.txt
```

**Why `--stat` not `--patch`:** `git log --stat` produces file-level change summaries (~200KB for 870 commits). `git diff --patch` produces content-level diffs (3.5M lines). We get what changed and how much without the content that blows buffers.

**Chunking:** Split `git-log-full.txt` by counting `^commit ` lines. Each chunk contains ~50 commits. Write to `tmp/adversarial-review/chunk-01.txt` through `chunk-NN.txt`.

**Bound:** ~50 commits × ~200 bytes per commit stat entry = ~10KB per chunk. Safe for any agent context.

### Stage 2: Summarize

**Executor:** N parallel `Agent()` subagents (one per chunk), launched in a single message for maximum concurrency. All run in background.

**Input:** Each agent reads its chunk file via `Read` tool.

**Prompt per agent:**
```
You are summarizing git commit history for an adversarial architecture review.
For each significant change in this chunk:
1. What subsystem was modified
2. What decision or assumption it encodes
3. What it replaced or broke

Ignore formatting-only commits, typo fixes, and trivial changes.
Output: bullet list. Max 30 bullets. Under 1500 words.
```

**Output:** Each agent returns its summary. CC collects all summaries.

### Stage 3: Merge

**Executor:** Single `Agent()` in foreground.

**Input:**
- All chunk summaries from Stage 2
- Contents of key decision artifacts (read via `Read` tool):
  - `JulianAudit0415h.md` (live-verified system state audit)
  - `juliandiff.md` (Sovereign Directive delta analysis)
  - `.gsd/STATE.md` (if exists — current project state)
  - Any files passed via `--files` argument

**Prompt:**
```
Consolidate these commit summaries and decision artifacts into one
architectural delta document organized by subsystem.

Sections:
- Backend (proxy.js, hub-bridge)
- Frontend (unified.html, Next.js/Tauri)
- K2 (cortex, regent, kiki, aria)
- P1 (cc_server, claude-mem, ollama)
- Memory/Spine (FalkorDB, FAISS, ledger, vault)
- Governance (governor, cost, gates)

For each section: what changed in the date range, what the current state
is, what assumptions it depends on. Max 10KB total output.
```

**Output:** Written to `tmp/adversarial-review/architectural-delta.md`.

### Stage 4: Review

**Executor:** 3 CC `Agent()` subagents + Codex, all launched in parallel in a single message.

**Input:** All reviewers receive `architectural-delta.md`.

**Reviewer 1 — Devil's Advocate:**
```
You are a hostile external reviewer hired to find what will break first.
Your job is NOT to be helpful. Your job is to be adversarial.

For each finding:
- State the assumption being made
- Describe the failure scenario when that assumption breaks
- Rate severity: CRITICAL / HIGH / MEDIUM / LOW
- State what evidence would prove or disprove it

Find at least 5 findings. Do not soften language. Do not suggest fixes —
only identify failures.
```

**Reviewer 2 — Cost/Sustainability Analyst:**
```
You are auditing this system for operational sustainability.

Find:
- Single points of failure with no fallback
- Services that die on reboot with no auto-restart
- Costs that scale unexpectedly
- Dependencies on specific machines/ports/paths not documented
- Manual intervention required to keep things running
- Zombie processes, stale config, port mismatches

Rate each finding by severity. Cite specific services, ports, or files.
```

**Reviewer 3 — Contradiction Hunter:**
```
You are hunting for internal contradictions in this system.

Find:
- Claims that conflict across documents
- Decisions reversed but dependents not updated
- Documented capabilities never tested live
- Stale configuration values that don't match the running system
- Two sources of truth that disagree on the same fact

For each contradiction: cite BOTH conflicting sources with specifics
(file names, values, timestamps). Rate severity.
```

**Reviewer 4 — Codex (optional, best-effort):**

The architectural delta is already written to `tmp/adversarial-review/architectural-delta.md`. Invoke Codex with focus text pointing to the file:
```bash
DELTA=$(cat tmp/adversarial-review/architectural-delta.md | head -c 8000)
node "...codex-companion.mjs" adversarial-review --wait "$DELTA"
```

**Codex fallback chain:**
1. Try passing first 8KB of delta as shell argument (safe for OS buffer)
2. If ENOBUFS: truncate to first 2KB and retry
3. If still fails: skip Codex, log failure, proceed with CC-only findings
4. **Never use `$(cat ...)` without `head -c` bound** — unbounded command substitution is the original bug

### Stage 5: Aggregate

**Executor:** Single `Agent()` in foreground.

**Input:** All 3-4 reviewer outputs.

**Prompt:**
```
Produce the final adversarial review report.

1. Merge all findings from all reviewers
2. Deduplicate: same issue from multiple reviewers = one entry citing all
3. Rank by severity: CRITICAL first, then HIGH, MEDIUM, LOW
4. Each finding format:
   - Title (one line)
   - Assumption challenged
   - Failure scenario
   - Evidence (what was found, by which reviewer)
   - Recommended action (one sentence)
5. End with VERDICT section:
   - Is the overall architecture sound?
   - Top 3 risks that would cause production failure
   - What would you refuse to ship without fixing first?

Be harsh. Do not soften findings. This is an adversarial report.
```

**Output:** Written to `tmp/adversarial-review/ADVERSARIAL_REPORT.md`.

---

## Skill Interface

**Trigger:** `/adversarial-review` or invoke via Skill tool.

**Arguments:**
| Arg | Default | Description |
|-----|---------|-------------|
| `--since` | 45 days ago | Start date for git log (YYYY-MM-DD) |
| `--until` | today | End date for git log (YYYY-MM-DD) |
| `--files` | none | Additional files to read and include in the architectural delta |
| Focus text | none | Free text after flags, passed to all reviewers as additional context |

**Examples:**
```
/adversarial-review
/adversarial-review --since 2026-03-01
/adversarial-review --since 2026-04-01 --files proxy.js unified.html
/adversarial-review --since 2026-03-01 "Focus on session persistence and brain wire decisions"
```

---

## Error Handling

| Failure | Response |
|---------|----------|
| Agent timeout/crash | Skip that agent, note gap in final report |
| Codex ENOBUFS | Truncate input and retry; if still fails, skip Codex |
| Codex unavailable | Skip Codex, proceed CC-only |
| Zero commits in date range | Abort with message, no report |
| tmp/ directory missing | Create it |
| Previous run artifacts exist | Overwrite |

---

## Output Artifacts

All written to `tmp/adversarial-review/`:

| File | Stage | Description |
|------|-------|-------------|
| `git-log-full.txt` | 1 | Raw git log with stat |
| `chunk-NN.txt` | 1 | Individual commit chunks |
| `architectural-delta.md` | 3 | Merged subsystem-organized delta (the review input) |
| `ADVERSARIAL_REPORT.md` | 5 | Final aggregated adversarial findings |

---

## Why This Works At Any Scale

1. **Stage 1** uses `git log --stat`, not `git diff`. Output scales linearly with commit count, not with total file content. 870 commits = ~200KB.
2. **Chunking** bounds each agent's input to ~50 commits (~10KB). Even 10,000 commits = 200 chunks = 200 parallel agents, each with bounded input.
3. **Stage 3 merge** produces a fixed-size output (~10KB) regardless of how many chunks fed it. This is the review input — it never grows unbounded.
4. **Codex receives ~10KB**, not 3.5M lines. Well within shell arg limits. And if it still fails, we have 3 CC reviewers that don't depend on it.
5. **No `spawnSync` with unbounded strings.** Every shell command uses files, not string interpolation of git output.

---

## Constraints

- Skill file only — no new dependencies, no npm install, no external services
- Uses only CC built-in tools: Agent, Bash, Read, Write
- Codex is optional enhancement, not required
- All temp files in `tmp/adversarial-review/` (gitignored)
- Does not modify any source files — read-only review
- Agent count scales with commit volume but is bounded by chunk size
