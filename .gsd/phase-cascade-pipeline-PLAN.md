# Cascade Pipeline — Sensors to Actuators
# S159: Turn Kiki/Vesper from observers into builders
# Source: Codex yoyo-evolve analysis (obs #22158) + Julian insertion mapping

## The Loop
```
Karma2/map/preclaw1-gap-map.md
  -> Kiki scan + rank MISSING rows
  -> kiki_issues.jsonl / bus directive (type: gap_closure)
  -> karma_persistent.py executes code task via CC --resume
  -> vesper_watchdog.py emits structured gap candidates
  -> vesper_eval.py runs real tests and rejects noise
  -> vesper_governor.py applies approved patch
  -> update preclaw1-gap-map.md row + evidence
  -> repeat until queue empty
```

## File 1: Scripts/karma_persistent.py

**Insertion points:**
- Line ~52: `IGNORE_SENDERS` — remove `kiki`/`vesper` or add allowlist for `gap_closure`
- Line ~65: `ACTIONABLE_TYPES` — add `gap_closure`, `code_patch`, `deploy_patch`
- After `poll_and_act()` (~line 120): insert 3 new functions

**New functions:**
```python
def build_gap_closure_context(row):
    """Build CC prompt from gap map row: target files, acceptance criteria, test command, deploy command."""

def run_gap_closure_task(context):
    """Tell CC --resume to output a structured patch plan, not prose. Reuses existing subprocess pattern."""

def post_gap_result(row, result, diff_summary):
    """Post proof and diff summary back to coordination bus."""
```

## File 2: Vesper/vesper_watchdog.py

**Insertion point:** Line ~272 (after existing candidate extraction hooks)

**New functions:**
```python
def parse_gap_map(md_path="Karma2/map/preclaw1-gap-map.md"):
    """Parse markdown table, return list of {feature, status, category, preclaw1_ref}."""

def rank_missing_gaps(rows, limit=5):
    """Sort MISSING rows by priority (P1 categories first), return top N."""

def extract_gapmap_candidates():
    """Read gap map, emit one candidate per MISSING gap with concrete patch/test/deploy plan.
    Writes to regent_candidates/ (same output path as existing candidates)."""
```

## File 3: Scripts/vesper_eval.py

**Insertion point:** Line ~159 (hard gate BEFORE existing eval logic)

**New functions:**
```python
def evaluate_gap_candidate(candidate):
    """Gate: reject if no target_files, no test_command, no diff. THE NOISE KILLER."""

def run_candidate_test(candidate):
    """Subprocess runs test_command. Returns pass/fail + output."""

def candidate_has_real_diff(candidate):
    """Reject if no code delta exists. Generic observational candidates stay observational."""
```

**Key rule:** No file diff = auto-reject. No test command = auto-reject. This kills the 18/20 generic noise problem.

## File 4: Scripts/vesper_governor.py

**Insertion point:** End of file (after existing `apply_promotion()`)

**New functions:**
```python
def apply_gap_patch(promotion):
    """Apply approved gap closure patch to target files."""

def smoke_test_gap(promotion):
    """Run post-deploy smoke test. If fail, rollback."""

def update_gap_map_status(gap_id, status, evidence):
    """Update preclaw1-gap-map.md: MISSING -> PARTIAL or HAVE.
    Evidence = commit SHA + timestamp + test result."""
```

## File 5: Vesper/karma_regent.py (71KB)

**Insertion points:**
- Line ~876: runtime prompt assembly — inject gap backlog
- Line ~400: extend `self_evaluate()`

**New functions:**
```python
def load_gap_brief():
    """Read gap map, return summary: '69 MISSING, 16 PARTIAL, 8 HAVE. Top 3 targets: ...'"""

def load_gap_backlog_summary():
    """Inject into runtime prompt so Vesper sees the real work queue."""

def announce_gap_resolution(gap_id, evidence):
    """Post to bus when a gap is closed."""
```

**Extend:** `self_evaluate()` detects when promoted gaps actually reduced backlog count (not just generic pattern count).

## File 6: Karma2/map/preclaw1-gap-map.md

No code change. Updated in-place by governor's `update_gap_map_status()`.
Format: governor replaces `**MISSING**` with `**HAVE**` + appends evidence line.

## File 7 (NEW): Scripts/gap_map.py

**Shared helper — all pipeline stages import this.**

```python
"""gap_map.py — shared parser for preclaw1-gap-map.md"""
import re, os, datetime

GAP_MAP_PATH = os.path.join(os.path.dirname(__file__), "..", "Karma2", "map", "preclaw1-gap-map.md")

def load_gap_rows(path=None):
    """Parse markdown table rows. Returns list of dicts: {category, feature, status, gap, preclaw1_ref}."""

def top_missing_gaps(limit=5, category=None):
    """Return top N MISSING gaps, optionally filtered by category. Priority: Settings > Sessions > Commands > Agents > Permissions > Git > Plugins > Cost."""

def mark_gap_status(gap_id, new_status, evidence):
    """In-place update: find row by feature name, replace status, append evidence."""

def render_gap_row_update(row, status, evidence):
    """Format the updated markdown table row with evidence note."""
```

## Failure Modes

| Failure | Detection | Recovery |
|---------|-----------|----------|
| CC --resume busy (429) | karma_persistent already handles 429 | Queue gap_closure directive, retry next cycle |
| Test fails | run_candidate_test returns fail | Candidate stays in regent_candidates/ as rejected. Retry with different approach next cycle |
| Deploy fails | smoke_test_gap returns fail | Governor rolls back. Does NOT update gap map. Candidate marked failed. |
| Gap map parse wrong | gap_map.py validates table structure | Raise on malformed rows. Log error. Skip cycle. |
| Concurrent cycles | Two watchers try to update gap map simultaneously | File lock on gap_map.md during writes (fcntl/msvcrt pattern) |
| CC generates prose not patch | run_gap_closure_task checks output format | Reject if no structured diff in output. Retry with stricter prompt. |

## Trigger Mechanism

1. **Timer:** Kiki loop reads gap map on each cycle (every ~90s)
2. **Queue:** If MISSING > 0, writes `gap_closure` issue to `kiki_issues.jsonl` + posts `GAP_QUEUE_READY` to bus
3. **Executor:** karma_persistent receives `gap_closure` directive, calls CC --resume with patch-oriented prompt
4. **Eval:** vesper_watchdog emits candidate JSON to `regent_candidates/`
5. **Gate:** vesper_eval approves only when tests + diff evidence are real
6. **Deploy:** vesper_governor applies patch, smokes, commits, updates gap map
7. **Loop:** Next Kiki cycle sees updated gap map, picks next MISSING item

## Success Criteria

- One gap = one candidate = one diff = one test command
- No code change = auto-reject
- No passing test = auto-reject
- No gap map update = incomplete
- Sensors become actuators
