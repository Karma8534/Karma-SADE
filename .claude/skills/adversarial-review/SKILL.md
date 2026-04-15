---
name: adversarial-review
description: "Chunked adversarial architecture review that works at any repo size. Summarizes git history in parallel, fans out to 3 hostile reviewer personas + optional Codex, aggregates findings into a severity-ranked report. Triggers: /adversarial-review, 'adversarial review', 'challenge review'."
---

# Adversarial Review — Chunked Pipeline

You are running a 5-stage adversarial architecture review. This review challenges
DECISIONS and DESIGN, not surface code quality. You are looking for what will break,
what assumptions are untested, and what contradictions exist.

## Argument Parsing

Parse the user's arguments (the text after the skill trigger):

- `--since YYYY-MM-DD` — start date for git log. Default: 45 days before today.
- `--until YYYY-MM-DD` — end date for git log. Default: today.
- `--files path1 path2 ...` — additional files to include in the architectural delta.
- Any remaining text after flags = focus text, passed to all reviewers.

Extract these into variables you will reference in each stage:
- `SINCE_DATE` (e.g. "2026-03-01")
- `UNTIL_DATE` (e.g. "2026-04-15")
- `EXTRA_FILES` (list, may be empty)
- `FOCUS_TEXT` (string, may be empty)

---

## Stage 1: Chunk (execute directly — no agent)

Run these steps:

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

4. Split into chunks of ~50 commits each. Use this awk command:

```bash
cd tmp/adversarial-review && awk '/^commit /{n++} n%50==1 && /^commit /{close(f); f=sprintf("chunk-%02d.txt",++c)} {print > f}' git-log-full.txt
```

5. Count chunks created:

```bash
ls tmp/adversarial-review/chunk-*.txt 2>/dev/null | wc -l
```

Report to user: "Stage 1 complete: {N} commits split into {M} chunks."

---

## Stage 2: Summarize (parallel agents)

For each chunk file in `tmp/adversarial-review/chunk-*.txt`, launch an Agent.

**CRITICAL:** All agents MUST be launched in a SINGLE message (one message with
multiple Agent tool calls) so they run concurrently. Use `run_in_background: true`.

**Agent prompt template** (replace CHUNK_PATH with the actual file path for each):

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

Wait for all agents to complete. Collect their returned text outputs.

If any agent fails or times out: note it as "[Chunk NN: SKIPPED — agent failed]"
and proceed with whatever summaries you have.

Report to user: "Stage 2 complete: {N}/{M} chunks summarized successfully."

---

## Stage 3: Merge (single agent, foreground)

Before launching the merge agent, read these files (if they exist) using the Read tool:
- `JulianAudit0415h.md`
- `juliandiff.md`
- `.gsd/STATE.md`
- Each file path in EXTRA_FILES

Launch ONE agent in the foreground (not background) with this prompt.
Paste all chunk summaries and all artifact contents directly into the prompt:

```
You are consolidating commit history summaries and decision artifacts into one
architectural delta document for adversarial review of a system called Karma SADE.

## Commit History Summaries

[INSERT ALL CHUNK SUMMARIES HERE, separated by "--- Chunk NN ---" headers]

## Decision Artifacts

[INSERT CONTENTS OF EACH ARTIFACT FILE HERE, each preceded by "### filename" header.
Skip any file that did not exist.]

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

Max 10KB total. Be factual. Do not editorialize. Do NOT edit any files.
Return your output as text only.
```

Take the agent's returned text and write it to `tmp/adversarial-review/architectural-delta.md`
using the Write tool.

Report to user: "Stage 3 complete: architectural delta written."

---

## Stage 4: Review (3 CC agents + Codex, all parallel)

Read `tmp/adversarial-review/architectural-delta.md` using the Read tool. Store
its content as DELTA_CONTENT.

If FOCUS_TEXT is non-empty, append this line to every reviewer prompt below:
"ADDITIONAL FOCUS FROM SOVEREIGN: {FOCUS_TEXT}"

Launch all reviewers in a SINGLE message for concurrency. CC agents use
`run_in_background: true`.

### Reviewer 1 — Devil's Advocate

Launch as Agent with prompt:

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

Launch as Agent with prompt:

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

Launch as Agent with prompt:

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

This reviewer is wrapped in error handling. If it fails at any step, skip it
and set CODEX_RESULT to "Codex reviewer: SKIPPED — {reason}".

Run via Bash tool:

```bash
DELTA=$(cat tmp/adversarial-review/architectural-delta.md | head -c 8000)
node "C:/Users/raest/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs" adversarial-review --wait "$DELTA"
```

If this command exits non-zero:
1. Retry with smaller input: replace `head -c 8000` with `head -c 2000`
2. If still fails: set CODEX_RESULT to "Codex reviewer: SKIPPED — command failed after retry."

Wait for all CC agents to complete. Collect all 3-4 outputs.

If any CC agent fails: note "[Reviewer N: SKIPPED — agent failed]" and proceed.

Report to user: "Stage 4 complete: {N}/4 reviewers returned findings."

---

## Stage 5: Aggregate (single agent, foreground)

Launch ONE agent in the foreground with all reviewer outputs concatenated into the prompt:

```
You are producing the final adversarial review report for a system called Karma SADE.

Here are the findings from each reviewer:

### Devil's Advocate
{REVIEWER_1_OUTPUT}

### Cost/Sustainability Analyst
{REVIEWER_2_OUTPUT}

### Contradiction Hunter
{REVIEWER_3_OUTPUT}

### Codex
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

Take the agent's returned text and write it to `tmp/adversarial-review/ADVERSARIAL_REPORT.md`
using the Write tool.

Then display the FULL report contents to the user. Do NOT summarize — show every finding.

Report to user: "Adversarial review complete. Report at tmp/adversarial-review/ADVERSARIAL_REPORT.md"
