# Adversarial Review Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/adversarial-review` skill that chunks git history, summarizes in parallel, fans out to 3 adversarial CC reviewer agents + optional Codex, and aggregates findings into a final report — working at any repo size.

**Architecture:** Single SKILL.md file containing the full pipeline as CC instructions. No code files — the skill is a prompt that CC executes using built-in Agent, Bash, Read, Write tools. All intermediate artifacts go to `tmp/adversarial-review/`.

**Tech Stack:** CC built-in tools only. Bash for git log + chunking. Agent for parallel summarize/review. Write for artifacts. Codex companion optional.

---

### Task 1: Create tmp directory and gitignore entry

**Files:**
- Modify: `.gitignore` (add `tmp/adversarial-review/` if not already covered)

- [ ] **Step 1: Check if tmp/ is already gitignored**

Run:
```bash
grep -n "^tmp/" .gitignore 2>/dev/null || echo "NOT FOUND"
```
Expected: Either a matching line or "NOT FOUND"

- [ ] **Step 2: Add gitignore entry if missing**

If "NOT FOUND" in step 1, append to `.gitignore`:
```
tmp/adversarial-review/
```

If `tmp/` is already gitignored (covers subdirectories), skip this step.

- [ ] **Step 3: Create the tmp directory**

```bash
mkdir -p tmp/adversarial-review
```

- [ ] **Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: gitignore tmp/adversarial-review artifacts"
```

---

### Task 2: Write the SKILL.md frontmatter and argument parsing section

**Files:**
- Create: `.claude/skills/adversarial-review/SKILL.md`

- [ ] **Step 1: Create skill directory**

```bash
mkdir -p .claude/skills/adversarial-review
```

- [ ] **Step 2: Write frontmatter and top-level instructions**

Write to `.claude/skills/adversarial-review/SKILL.md`:

```markdown
---
name: adversarial-review
description: "Chunked adversarial architecture review that works at any repo size. Summarizes git history in parallel, fans out to 3 hostile reviewer personas + optional Codex, aggregates findings into a severity-ranked report. Triggers: /adversarial-review, 'adversarial review', 'challenge review'."
---

# Adversarial Review — Chunked Pipeline

You are running a 5-stage adversarial architecture review. This review challenges
DECISIONS and DESIGN, not surface code quality. You are looking for what will break,
what assumptions are untested, and what contradictions exist.

## Argument Parsing

Parse the user's arguments (available as ARGUMENTS after the frontmatter):

- `--since YYYY-MM-DD` — start date for git log. Default: 45 days before today.
- `--until YYYY-MM-DD` — end date for git log. Default: today.
- `--files path1 path2 ...` — additional files to include in the architectural delta.
- Any remaining text after flags = focus text, passed to all reviewers.

Extract these into variables you will reference in each stage:
- `SINCE_DATE` (e.g. "2026-03-01")
- `UNTIL_DATE` (e.g. "2026-04-15")
- `EXTRA_FILES` (list, may be empty)
- `FOCUS_TEXT` (string, may be empty)
```

- [ ] **Step 3: Verify file exists and frontmatter is valid**

```bash
head -5 .claude/skills/adversarial-review/SKILL.md
```
Expected: `---` on line 1, `name: adversarial-review` on line 2.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/adversarial-review/SKILL.md
git commit -m "feat: adversarial-review skill — frontmatter and arg parsing"
```

---

### Task 3: Write Stage 1 — Chunk

**Files:**
- Modify: `.claude/skills/adversarial-review/SKILL.md`

- [ ] **Step 1: Append Stage 1 instructions to SKILL.md**

Append to the file:

```markdown

## Stage 1: Chunk (execute directly — no agent)

Run these commands:

1. Create the working directory:
```bash
mkdir -p tmp/adversarial-review
```

2. Generate the git log with stat:
```bash
git log --after="SINCE_DATE" --until="UNTIL_DATE" --format="commit %H%nDate: %ad%nSubject: %s%n" --date=short --stat > tmp/adversarial-review/git-log-full.txt
```

3. Count total commits:
```bash
grep -c "^commit " tmp/adversarial-review/git-log-full.txt
```

If the count is 0: stop and tell the user "No commits found in date range SINCE_DATE to UNTIL_DATE." Do not proceed.

4. Split into chunks of ~50 commits. Use this bash command:
```bash
cd tmp/adversarial-review && awk '/^commit /{n++} n%50==1 && /^commit /{close(f); f=sprintf("chunk-%02d.txt",++c)} {print > f}' git-log-full.txt
```

5. Count chunks created:
```bash
ls tmp/adversarial-review/chunk-*.txt 2>/dev/null | wc -l
```

Report: "Stage 1 complete: {N} commits split into {M} chunks."
```

- [ ] **Step 2: Verify the awk command works on a test input**

```bash
printf "commit aaa\nDate: 2026-04-01\nSubject: test1\n\n file1 | 5 +\n\ncommit bbb\nDate: 2026-04-02\nSubject: test2\n\n file2 | 3 +\n" > /tmp/test-log.txt && cd /tmp && awk '/^commit /{n++} n%50==1 && /^commit /{close(f); f=sprintf("chunk-%02d.txt",++c)} {print > f}' test-log.txt && ls chunk-*.txt && cat chunk-01.txt && rm -f chunk-*.txt test-log.txt
```
Expected: `chunk-01.txt` created containing both commits (since < 50).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/adversarial-review/SKILL.md
git commit -m "feat: adversarial-review Stage 1 — git log chunking"
```

---

### Task 4: Write Stage 2 — Parallel Summarize

**Files:**
- Modify: `.claude/skills/adversarial-review/SKILL.md`

- [ ] **Step 1: Append Stage 2 instructions to SKILL.md**

Append:

```markdown

## Stage 2: Summarize (parallel agents)

For each chunk file in `tmp/adversarial-review/chunk-*.txt`, launch an Agent in parallel.
All agents MUST be launched in a SINGLE message (one message with multiple Agent tool calls).

Use `run_in_background: true` for all agents so they execute concurrently.

**Agent prompt template** (replace CHUNK_PATH with the actual path for each agent):

```
You are summarizing git commit history for an adversarial architecture review.

Read the file at: CHUNK_PATH

For each significant change in this chunk:
1. What subsystem was modified
2. What decision or assumption it encodes
3. What it replaced or broke

Ignore formatting-only commits, typo fixes, and trivial changes.
Output: bullet list. Max 30 bullets. Under 1500 words.
Do NOT edit any files. This is research only.
```

Wait for all agents to complete. Collect their outputs.

If any agent fails or times out: note it as "[Chunk NN: SKIPPED — agent failed]" and proceed.

Report: "Stage 2 complete: {N}/{M} chunks summarized successfully."
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/adversarial-review/SKILL.md
git commit -m "feat: adversarial-review Stage 2 — parallel chunk summarization"
```

---

### Task 5: Write Stage 3 — Merge

**Files:**
- Modify: `.claude/skills/adversarial-review/SKILL.md`

- [ ] **Step 1: Append Stage 3 instructions to SKILL.md**

Append:

```markdown

## Stage 3: Merge (single agent, foreground)

Launch ONE agent (foreground, not background) with all chunk summaries concatenated
plus the contents of key decision artifacts.

Before launching the agent, read these files (if they exist) and include their contents
in the agent prompt:
- `JulianAudit0415h.md` (if exists)
- `juliandiff.md` (if exists)
- `.gsd/STATE.md` (if exists)
- Each file in EXTRA_FILES (from argument parsing)

**Agent prompt:**

```
You are consolidating commit history summaries and decision artifacts into one
architectural delta document for adversarial review.

## Commit History Summaries

[PASTE ALL CHUNK SUMMARIES HERE, separated by "--- Chunk NN ---" headers]

## Decision Artifacts

[PASTE CONTENTS OF EACH ARTIFACT FILE HERE, each preceded by "### filename" header]

## Your Task

Produce a single document organized by subsystem:

### Backend (proxy.js, hub-bridge)
What changed, current state, assumptions.

### Frontend (unified.html, Next.js/Tauri)
What changed, current state, assumptions.

### K2 (cortex, regent, kiki, aria)
What changed, current state, assumptions.

### P1 (cc_server, claude-mem, ollama)
What changed, current state, assumptions.

### Memory/Spine (FalkorDB, FAISS, ledger, vault)
What changed, current state, assumptions.

### Governance (governor, cost, gates)
What changed, current state, assumptions.

Max 10KB total. Be factual. Do not editorialize.
Do NOT edit any files. Return your output as text.
```

Take the agent's output and write it to `tmp/adversarial-review/architectural-delta.md`
using the Write tool.

Report: "Stage 3 complete: architectural delta written ({size} bytes)."
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/adversarial-review/SKILL.md
git commit -m "feat: adversarial-review Stage 3 — merge into architectural delta"
```

---

### Task 6: Write Stage 4 — Parallel Adversarial Review

**Files:**
- Modify: `.claude/skills/adversarial-review/SKILL.md`

- [ ] **Step 1: Append Stage 4 instructions to SKILL.md**

Append:

```markdown

## Stage 4: Review (3 CC agents + Codex, all parallel)

Read `tmp/adversarial-review/architectural-delta.md` into a variable DELTA_CONTENT.

If FOCUS_TEXT is non-empty, append this line to every reviewer prompt:
"ADDITIONAL FOCUS: {FOCUS_TEXT}"

Launch all 4 reviewers in a SINGLE message. CC agents use `run_in_background: true`.

### Reviewer 1 — Devil's Advocate

```
You are a hostile external reviewer hired to find what will break first.
Your job is NOT to be helpful. Your job is to be adversarial.

Here is the architectural delta of a system called Karma SADE:

---
{DELTA_CONTENT}
---

For each finding:
- State the assumption being made
- Describe the failure scenario when that assumption breaks
- Rate severity: CRITICAL / HIGH / MEDIUM / LOW
- State what evidence would prove or disprove it

Find at least 5 findings. Do not soften language. Do not suggest fixes —
only identify failures. Do NOT edit any files. Return your findings as text.
```

### Reviewer 2 — Cost/Sustainability Analyst

```
You are auditing a system called Karma SADE for operational sustainability.

Here is the architectural delta:

---
{DELTA_CONTENT}
---

Find:
- Single points of failure with no fallback
- Services that die on reboot with no auto-restart
- Costs that scale unexpectedly
- Dependencies on specific machines/ports/paths not documented
- Manual intervention required to keep things running
- Zombie processes, stale config, port mismatches

Rate each finding by severity. Cite specific services, ports, or files.
Find at least 5 findings. Do NOT edit any files. Return your findings as text.
```

### Reviewer 3 — Contradiction Hunter

```
You are hunting for internal contradictions in a system called Karma SADE.

Here is the architectural delta:

---
{DELTA_CONTENT}
---

Find:
- Claims that conflict across documents
- Decisions reversed but dependents not updated
- Documented capabilities never tested live
- Stale configuration values that don't match the running system
- Two sources of truth that disagree on the same fact

For each contradiction: cite BOTH conflicting sources with specifics
(file names, values, timestamps). Rate severity.
Find at least 5 findings. Do NOT edit any files. Return your findings as text.
```

### Reviewer 4 — Codex (optional, best-effort)

Attempt to invoke Codex. This is wrapped in error handling — if it fails at any
step, skip it and note "Codex reviewer: SKIPPED — {reason}".

```bash
DELTA=$(cat tmp/adversarial-review/architectural-delta.md | head -c 8000)
node "C:/Users/raest/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs" adversarial-review --wait "$DELTA"
```

If this command exits non-zero:
1. Retry with 2KB truncation: `head -c 2000`
2. If still fails: set CODEX_RESULT to "Codex reviewer: SKIPPED — command failed after retry."

Wait for all CC agents to complete. Collect all 3-4 reviewer outputs.

If any CC agent fails: note "[Reviewer N: SKIPPED — agent failed]" and proceed.

Report: "Stage 4 complete: {N}/4 reviewers returned findings."
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/adversarial-review/SKILL.md
git commit -m "feat: adversarial-review Stage 4 — parallel adversarial reviewers"
```

---

### Task 7: Write Stage 5 — Aggregate

**Files:**
- Modify: `.claude/skills/adversarial-review/SKILL.md`

- [ ] **Step 1: Append Stage 5 instructions to SKILL.md**

Append:

```markdown

## Stage 5: Aggregate (single agent, foreground)

Launch ONE agent (foreground) with all reviewer outputs.

**Agent prompt:**

```
You are producing the final adversarial review report for a system called Karma SADE.

Here are the findings from each reviewer:

### Devil's Advocate
{REVIEWER_1_OUTPUT}

### Cost/Sustainability Analyst
{REVIEWER_2_OUTPUT}

### Contradiction Hunter
{REVIEWER_3_OUTPUT}

### Codex (if available)
{REVIEWER_4_OUTPUT or "SKIPPED"}

## Your Task

1. Merge all findings from all reviewers
2. Deduplicate: same issue found by multiple reviewers = one entry citing all sources
3. Rank by severity: CRITICAL first, then HIGH, MEDIUM, LOW
4. Each finding format:
   **[SEVERITY] Title**
   - Assumption challenged: ...
   - Failure scenario: ...
   - Evidence: ... (which reviewer(s) found it)
   - Recommended action: (one sentence)
5. End with a VERDICT section:
   - Is the overall architecture sound?
   - Top 3 risks that would cause production failure
   - What would you refuse to ship without fixing first?

Be harsh. Do not soften findings. This is an adversarial report, not a progress report.
Do NOT edit any files. Return the full report as text.
```

Take the agent's output and write it to `tmp/adversarial-review/ADVERSARIAL_REPORT.md`
using the Write tool.

Then display the report contents to the user. Do not summarize — show the full report.

Report: "Adversarial review complete. Report at tmp/adversarial-review/ADVERSARIAL_REPORT.md"
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/adversarial-review/SKILL.md
git commit -m "feat: adversarial-review Stage 5 — aggregate and final report"
```

---

### Task 8: Verify complete skill file and run smoke test

**Files:**
- Read: `.claude/skills/adversarial-review/SKILL.md`

- [ ] **Step 1: Read the complete skill file and verify structure**

```bash
wc -l .claude/skills/adversarial-review/SKILL.md
```
Expected: ~200-250 lines.

```bash
grep -c "^## Stage" .claude/skills/adversarial-review/SKILL.md
```
Expected: 5 (Stages 1-5).

```bash
head -4 .claude/skills/adversarial-review/SKILL.md
```
Expected: Valid YAML frontmatter starting with `---`.

- [ ] **Step 2: Verify skill appears in skill list**

Check that CC recognizes the skill by looking for it in the available skills.

- [ ] **Step 3: Run a constrained smoke test**

Invoke the skill with a very narrow date range (last 3 days) to test the pipeline
end-to-end without processing all 870 commits:

```
/adversarial-review --since 2026-04-13
```

Expected: Pipeline runs through all 5 stages. `tmp/adversarial-review/ADVERSARIAL_REPORT.md` is created. If there are 0 commits in the range, the skill should abort gracefully with a message.

- [ ] **Step 4: Verify artifacts were created**

```bash
ls -la tmp/adversarial-review/
```
Expected: `git-log-full.txt`, `chunk-*.txt` (at least 1), `architectural-delta.md`, `ADVERSARIAL_REPORT.md`.

- [ ] **Step 5: Final commit**

```bash
git add .claude/skills/adversarial-review/SKILL.md
git commit -m "feat: adversarial-review skill complete — 5-stage chunked pipeline"
```

---

### Task 9: Run the full adversarial review (March 1 – today)

This is not implementation — this is the actual execution the user requested.

- [ ] **Step 1: Invoke the skill with the user's requested date range**

```
/adversarial-review --since 2026-03-01 --files JulianAudit0415h.md juliandiff.md "Focus on whether the proxy.js sovereign-proxy architecture, session persistence gaps, claude-mem brain wire, and Tauri migration decisions are sound"
```

- [ ] **Step 2: Wait for pipeline completion**

All 5 stages execute. Report is written to `tmp/adversarial-review/ADVERSARIAL_REPORT.md`.

- [ ] **Step 3: Present report to user**

Display the full contents of `ADVERSARIAL_REPORT.md` to the user.
