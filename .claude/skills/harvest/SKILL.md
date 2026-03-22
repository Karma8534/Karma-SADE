---
name: harvest
description: Extract PITFALL/DECISION/PROOF/DIRECTION events from session .md files in docs/ccSessions/ into claude-mem, synthesize skill files and project arc narrative, move processed files to Learned/. Re-runnable — watermark prevents re-processing. Run whenever new session files are added. Trigger word: harvest.
type: rigid
---

# HARVEST — Session Corpus Ingestion

## Purpose
Build and maintain CC's permanent institutional memory from accumulated session history.
Every /harvest run makes CC measurably wiser. Every session file processed = fewer repeated mistakes.

**Re-runnable and idempotent.** Watermark tracks what's been processed. New files only.

---

## STEP 1 — Initialize

```
1a. Create docs/ccSessions/Learned/ if missing (preserve subfolder structure as files move in)
1b. Load .harvest_watermark.json — list of already-processed relative file paths
    If missing: start fresh (process all files)
1c. Process cc-harvest-pending.jsonl first — retry any failed claude-mem saves from prior runs
1d. Pre-scan for filename duplicates:
    Find .md files with identical names across different subfolders
    Root copy = canonical. Subfolder copy of same filename = Dup.
    Rename: K2Purpose.md in subfolder → K2Purpose-Dup.md BEFORE processing
1e. Count and report: "N files to process, M already done, K duplicates renamed"
```

---

## STEP 2 — Process files in priority order

**Priority:** ccSession* → KSession*/KCSession*/KarmaSession* → plan/arch docs → From CAI/

For each unprocessed file (not in watermark):

```
a. READ
   If file ≤ 200 lines: read whole file
   If file > 200 lines: chunk into 200-line windows with 20-line overlap
   Process each chunk, merge events at file level

b. EXTRACT events — quality bar (all 3 required):
   - Explicit or clearly implicit type: PITFALL / DECISION / PROOF / DIRECTION
   - Title: < 80 characters, specific (not "session update")
   - Body: explains root cause + what to do differently — NOT status narration
   Skip: "we committed X", "step N done", "reviewing files" — no actionable learning

c. DEDUP and SAVE each event:
   search claude-mem: title keywords, project="Karma_SADE", limit=5
   If no result with similarity ≥ 0.8:
     save_observation(text=body, title="[TYPE] title", project="Karma_SADE")
   If similar exists: skip (don't save duplicate)
   If save FAILS: append to cc-harvest-pending.jsonl for next run retry

d. SCOPE INDEX — for PITFALL and DECISION events only:
   Append to Karma2/cc-scope-index.md:
   Format: P0XX [slug]: Rule: [one sentence rule] | Why: [one sentence root cause]

e. MOVE file to Learned/:
   Mirror subfolder: docs/ccSessions/From CAI/K2/file.md → docs/ccSessions/Learned/From CAI/K2/file.md
   Create subfolder in Learned/ if it doesn't exist

f. WRITE WATERMARK immediately after moving (crash-safe):
   .harvest_watermark.json — append relative path to processed list
```

Report progress every 20 files: "Processed X/N files, M observations saved so far"

---

## STEP 3 — Synthesize new skill files

After all files processed, cluster extracted PITFALL events by topic keyword (first meaningful noun from title).

For each cluster where events came from ≥ 3 different source files:
- slug = topic keyword, lowercased, hyphened
- out_path = .claude/skills/karma-pitfall-{slug}.md
- If file already exists: SKIP (don't overwrite existing skills)
- Write new skill file:

```markdown
---
name: karma-pitfall-{slug}
description: Auto-synthesized from HARVEST. Pattern seen in {N} sessions. Invoke when working with {topic}.
type: feedback
---

## Rule
[The pattern as a single, concrete rule]

**Why:** [Root cause from evidence]
**How to apply:** [Exact trigger conditions]

## Evidence
[Bullet list of source sessions and what happened, one per session]
```

---

## STEP 4 — Synthesize cc-big-picture.md

Write Karma2/cc-big-picture.md — the project arc narrative.
This is what CC reads at resurrect to understand "where we came from."

```markdown
# Karma SADE — Project Arc
Generated: [timestamp] by HARVEST. Updated each /harvest run.

## Origin
[What problem was being solved, what Karma was meant to be at the start]

## Architecture Evolution
[Key architectural shifts — what was tried, what was changed and why]

## Key Failures and Lessons
[The most important PITFALLs across all sessions — the ones that shaped everything]

## Current State
[What's verified working, what's not, what the active mission is]

## Next
[What comes next per PLAN.md]
```

Max 600 words total. This is a readable arc, not a transcript.

---

## STEP 5 — Update watchdog_extra_patterns.json on K2

SSH to K2 and merge top PITFALL patterns from this HARVEST run:

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost '
python3 -c \"
import json, os
path = \"/mnt/c/dev/Karma/k2/cache/watchdog_extra_patterns.json\"
existing = json.load(open(path)) if os.path.exists(path) else []
new_patterns = [PITFALL_LIST_FROM_HARVEST]
merged = existing + [p for p in new_patterns if p[\"pattern\"] not in [e[\"pattern\"] for e in existing]]
json.dump(merged, open(path,\"w\"), indent=2)
print(f\"Updated: {len(merged)} total patterns\")
\"
'"
```

Report: "watchdog_extra_patterns.json updated: N total patterns on K2"

---

## STEP 6 — Update cc_context_snapshot.md

Append HARVEST summary to the Active Work section of cc_context_snapshot.md:

```
## HARVEST (last run)
[timestamp]: N files processed, M new observations, K new skill files
Big picture: Karma2/cc-big-picture.md updated
Scope index: Karma2/cc-scope-index.md updated
K2 patterns: watchdog_extra_patterns.json updated
```

---

## STEP 7 — Verification gate

Check and report against PLAN.md PRE-PHASE gates:

```
□ New claude-mem observations ≥ 50 net new?   [count/50] PASS/FAIL
□ karma-pitfall-*.md files total ≥ 10?         [count] PASS (already met)
□ watchdog_extra_patterns.json updated on K2?  PASS/FAIL
□ cc-scope-index.md has new entries?            PASS/FAIL
□ cc-big-picture.md written?                   PASS/FAIL
```

If ALL pass: PRE-PHASE gate is MET.
If ANY fail: report explicitly, do NOT mark PRE-PHASE complete.

---

## STEP 8 — Save completion record

```
save_observation(
  title="HARVEST COMPLETE [timestamp]",
  text="HARVEST run complete. N files processed, M net new observations, K new skill files.
        Gates: [list pass/fail]. Corpus Phase 2 pending: IndexedDB extraction (108+ sessions).",
  project="Karma_SADE"
)
```

Update Karma2/PLAN.md PRE-PHASE status with results.

---

## On Error

If claude-mem MCP unavailable:
→ Append failed event to `cc-harvest-pending.jsonl` (one JSON line per event)
→ Continue processing remaining files
→ Next /harvest run processes pending.jsonl first (Step 1c)

If SSH to K2 fails for Step 5:
→ Log: "K2 unreachable — watchdog_extra_patterns.json not updated. Run /harvest again when K2 available."
→ Continue — do not abort entire run for K2 SSH failure

---

## Re-run Behavior

New .md files in docs/ccSessions/ → processed
Files already in Learned/ → skipped (not re-processed)
Duplicate filenames → only processed once (root copy canonical)
Safe to run at any time. No side effects on already-processed files.

---

## Ongoing Growth

This skill is the foundation. After initial run:
- Each new session Colby adds to docs/ccSessions/ → /harvest processes it
- Resurrect Step 1f surfaces unprocessed file count automatically
- KarmaNightlyHarvest scheduled task runs /harvest at 3am if new files exist
- wrap-session adds DECISION/PROOF/PITFALL from current session to claude-mem
- IndexedDB extraction (Corpus Phase 2) feeds back into /harvest when ready
