# Graphiti Watermark Entity Extraction — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Re-enable Graphiti entity extraction for new ledger episodes (forward-only) using a watermark file to track processed position, so Karma's knowledge graph grows with every new conversation.

**Architecture:** Add watermark read/write helpers to batch_ingest.py. When running in Graphiti mode (no --skip-dedup), read only episodes from watermark position forward, process via Graphiti, advance watermark per wave. Hard cap at 200 episodes per run. Cron drops --skip-dedup. Watermark lives at /ledger/.batch_watermark (host-mounted, survives container rebuilds).

**Tech Stack:** Python 3, asyncio, FalkorDB (via Graphiti), existing batch_ingest.py patterns

---

## CRITICAL CONTEXT

- **karma-server build context on vault-neo:** `/opt/seed-vault/memory_v1/karma-core/` — NOT the git repo at `/home/neo/karma-sade/karma-core/`. After git push, always cp before rebuild.
- **Ledger volume already mounted:** `/opt/seed-vault/memory_v1/ledger:/ledger` — watermark at `/ledger/.batch_watermark` persists on host automatically. No compose change needed.
- **current `filter_unprocessed()`:** count-based (counts existing nodes per provider, skips that many from ledger). This is NOT used in the new Graphiti path. New path uses watermark line-number tracking instead.
- **--skip-dedup path is UNCHANGED.** `filter_unprocessed` stays for --skip-dedup mode. Only the Graphiti (no-flag) path gets watermark.
- **Graphiti timeout threshold:** ~250 episodes. Hard cap = 200. Non-negotiable.
- **Wave size is 30** (existing). Watermark advances after each wave completes. Partial wave errors: tolerated (logged), watermark still advances.
- **SSH alias:** `vault-neo`. All droplet ops via SSH.
- **Git ops via PowerShell** (not Git Bash — index.lock issue on Windows).

---

## Task 1: Add Watermark Helper Functions

**File:** `karma-core/batch_ingest.py`

**Step 1: Add three functions after `filter_unprocessed()` (around line 127)**

```python
# ─── Watermark (forward-only Graphiti mode) ──────────────────────────────

def read_watermark(watermark_path: str, ledger_path: str) -> int:
    """Return the ledger line to start from. Initializes to current line count on first run."""
    if not os.path.exists(watermark_path):
        with open(ledger_path, "r", encoding="utf-8") as f:
            count = sum(1 for _ in f)
        write_watermark(watermark_path, count)
        log(f"  Watermark initialized at line {count} — all historical episodes skipped")
        return count
    with open(watermark_path, "r") as f:
        return int(f.read().strip())


def write_watermark(watermark_path: str, line_num: int) -> None:
    """Atomically write watermark to disk."""
    tmp = watermark_path + ".tmp"
    with open(tmp, "w") as f:
        f.write(str(line_num))
    os.replace(tmp, watermark_path)


def read_new_episodes(ledger_path: str, start_line: int, max_batch: int = 200) -> tuple[list[dict], int]:
    """
    Read up to max_batch valid conversation pairs from ledger starting at start_line.
    Returns (episodes, end_line) where end_line is the new watermark position.
    """
    episodes = []
    end_line = start_line
    with open(ledger_path, "r", encoding="utf-8") as f:
        for i, raw in enumerate(f):
            if i < start_line:
                continue
            end_line = i + 1
            if len(episodes) >= max_batch:
                break
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
                content = entry.get("content", {})
                assistant = content.get("assistant_message") or content.get("assistant_text", "")
                if content.get("user_message") and assistant:
                    episodes.append(entry)
            except json.JSONDecodeError:
                pass
    return episodes, end_line
```

**Step 2: Write the failing tests**

Create `karma-core/tests/test_watermark.py`:

```python
import json
import os
import tempfile
import pytest
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import only the functions we added — avoid importing full module (has side effects)
from batch_ingest import read_watermark, write_watermark, read_new_episodes


def _make_ledger(tmp_path, entries):
    """Write JSONL ledger file."""
    p = tmp_path / "memory.jsonl"
    with open(p, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return str(p)


def _make_entry(user="hello", assistant="hi", provider="hub-chat"):
    return {
        "tags": ["hub", "chat"],
        "content": {
            "user_message": user,
            "assistant_text": assistant,
            "provider": provider,
        }
    }


class TestWatermark:
    def test_init_creates_watermark_at_current_line_count(self, tmp_path):
        ledger = _make_ledger(tmp_path, [_make_entry() for _ in range(5)])
        wm_path = str(tmp_path / ".watermark")
        result = read_watermark(wm_path, ledger)
        assert result == 5
        assert os.path.exists(wm_path)

    def test_read_watermark_returns_existing_value(self, tmp_path):
        ledger = _make_ledger(tmp_path, [_make_entry()])
        wm_path = str(tmp_path / ".watermark")
        write_watermark(wm_path, 42)
        assert read_watermark(wm_path, ledger) == 42

    def test_write_watermark_atomic(self, tmp_path):
        wm_path = str(tmp_path / ".watermark")
        write_watermark(wm_path, 99)
        with open(wm_path) as f:
            assert f.read().strip() == "99"
        assert not os.path.exists(wm_path + ".tmp")


class TestReadNewEpisodes:
    def test_reads_from_start_line(self, tmp_path):
        entries = [_make_entry(user=f"msg{i}") for i in range(10)]
        ledger = _make_ledger(tmp_path, entries)
        episodes, end_line = read_new_episodes(ledger, start_line=5, max_batch=200)
        assert len(episodes) == 5
        assert end_line == 10

    def test_respects_max_batch(self, tmp_path):
        entries = [_make_entry() for _ in range(50)]
        ledger = _make_ledger(tmp_path, entries)
        episodes, end_line = read_new_episodes(ledger, start_line=0, max_batch=20)
        assert len(episodes) == 20

    def test_skips_entries_without_required_fields(self, tmp_path):
        entries = [
            {"content": {"user_message": "hi"}},  # no assistant — skip
            _make_entry(),  # valid
        ]
        ledger = _make_ledger(tmp_path, entries)
        episodes, _ = read_new_episodes(ledger, start_line=0, max_batch=200)
        assert len(episodes) == 1

    def test_empty_from_start_line_at_end(self, tmp_path):
        entries = [_make_entry() for _ in range(3)]
        ledger = _make_ledger(tmp_path, entries)
        episodes, end_line = read_new_episodes(ledger, start_line=3, max_batch=200)
        assert len(episodes) == 0
        assert end_line == 3
```

**Step 3: Run tests to verify they FAIL (functions not defined yet)**

```bash
cd C:\Users\raest\Documents\Karma_SADE
python -m pytest karma-core/tests/test_watermark.py -v
```

Expected: ImportError or AttributeError — functions don't exist yet.

**Step 4: Add the three functions to batch_ingest.py** (copy from Step 1 above, insert after line 127)

**Step 5: Run tests to verify PASS**

```bash
python -m pytest karma-core/tests/test_watermark.py -v
```

Expected: 7 tests PASS.

**Step 6: Commit**

```powershell
powershell -Command "cd C:\Users\raest\Documents\Karma_SADE; git add karma-core/batch_ingest.py karma-core/tests/test_watermark.py; git commit -m 'feat: add watermark helpers to batch_ingest (read/write/read_new_episodes)'"
```

---

## Task 2: Wire Watermark into Graphiti Mode in run()

**File:** `karma-core/batch_ingest.py`

**Step 1: Add --max-batch argument in `main()`**

Find this block (around line 367):
```python
    parser.add_argument("--concurrency", type=int, default=3,
```

Add after it:
```python
    parser.add_argument("--max-batch", type=int, default=200,
                        help="Max episodes per Graphiti run (default: 200, Graphiti safe limit ~250)")
```

**Step 2: Add WATERMARK_PATH env read at top of `run()`**

Find (around line 288):
```python
    ledger_path = config.LEDGER_PATH
```

Add after it:
```python
    watermark_path = os.environ.get("WATERMARK_PATH", "/ledger/.batch_watermark")
```

**Step 3: Replace the Graphiti path's episode selection in `run()`**

Find this block (around line 293):
```python
    all_pairs = read_conversation_pairs(ledger_path)
    log(f"  Conversation pairs in ledger: {len(all_pairs)}")

    already = get_already_ingested_count()
    total_ingested = sum(already.values())
    log(f"  Already ingested: {total_ingested} episodes")

    remaining = filter_unprocessed(all_pairs, already)
    log(f"  TO PROCESS: {len(remaining)}")
```

Replace with:
```python
    if args.skip_dedup:
        # count-based dedup for bulk historical backfill (unchanged)
        all_pairs = read_conversation_pairs(ledger_path)
        log(f"  Conversation pairs in ledger: {len(all_pairs)}")
        already = get_already_ingested_count()
        total_ingested = sum(already.values())
        log(f"  Already ingested: {total_ingested} episodes")
        remaining = filter_unprocessed(all_pairs, already)
        log(f"  TO PROCESS: {len(remaining)}")
        start_watermark = None  # not used in skip-dedup mode
    else:
        # watermark-based selection for Graphiti mode
        start_watermark = read_watermark(watermark_path, ledger_path)
        remaining, end_watermark = read_new_episodes(ledger_path, start_watermark, args.max_batch)
        log(f"  Watermark: line {start_watermark}")
        log(f"  TO PROCESS: {len(remaining)} new episodes (cap: {args.max_batch})")
        if len(remaining) == args.max_batch:
            log(f"  NOTE: Batch capped at {args.max_batch} — remainder picked up next run")
```

**Step 4: Add watermark advance after each wave in the wave loop**

Find (around line 330):
```python
    for wave_start in range(0, len(remaining), wave_size):
        wave = remaining[wave_start:wave_start + wave_size]
        wave_num = wave_start // wave_size + 1
        log(f"  Wave {wave_num}/{total_waves} ({len(wave)} eps)...")

        if args.skip_dedup:
            tasks = [ingest_one_direct(r, sem, entry, wave_start + i) for i, entry in enumerate(wave)]
        else:
            tasks = [ingest_one(graphiti, sem, entry, wave_start + i) for i, entry in enumerate(wave)]

        await asyncio.gather(*tasks)
```

Replace with:
```python
    current_watermark = start_watermark  # None in skip-dedup mode

    for wave_start in range(0, len(remaining), wave_size):
        wave = remaining[wave_start:wave_start + wave_size]
        wave_num = wave_start // wave_size + 1
        log(f"  Wave {wave_num}/{total_waves} ({len(wave)} eps)...")

        if args.skip_dedup:
            tasks = [ingest_one_direct(r, sem, entry, wave_start + i) for i, entry in enumerate(wave)]
        else:
            tasks = [ingest_one(graphiti, sem, entry, wave_start + i) for i, entry in enumerate(wave)]

        await asyncio.gather(*tasks)

        # Advance watermark after each Graphiti wave
        if not args.skip_dedup and start_watermark is not None:
            # end_watermark is absolute ledger position; advance proportionally per wave
            wave_end_line = start_watermark + end_watermark - start_watermark  # recalc below
            # Simpler: track by episode count processed so far
            episodes_done = min(wave_start + wave_size, len(remaining))
            # Approximate line advance: end_watermark covers all max_batch episodes
            # Use ratio: lines_span * (episodes_done / len(remaining))
            lines_span = end_watermark - start_watermark
            approx_line = start_watermark + int(lines_span * (episodes_done / max(len(remaining), 1)))
            write_watermark(watermark_path, approx_line)
            current_watermark = approx_line
            log(f"  Watermark advanced to line ~{approx_line}")
```

Wait — this approximation is incorrect. Let me fix with a cleaner approach.

**CORRECTION — Replace the wave loop instead with this cleaner pattern:**

The issue is `read_new_episodes` returns `end_line` which is the line AFTER the last episode read (absolute). Watermark should be set to `end_watermark` after all waves complete (or after each wave using episode-index-based slice approach).

Simplest correct implementation: write watermark to `end_watermark` only AFTER all waves finish successfully. This means: if a partial failure occurs mid-run, watermark only advances on the NEXT run after retry. Acceptable.

Replace the watermark-advance section with:

```python
        await asyncio.gather(*tasks)
        # (no per-wave watermark write — see post-loop below)
```

And after the loop (before `elapsed = ...`), add:

```python
    # Write final watermark for Graphiti mode
    if not args.skip_dedup and start_watermark is not None:
        write_watermark(watermark_path, end_watermark)
        log(f"  Watermark advanced: line {start_watermark} → {end_watermark}")
```

**Step 5: Run the existing tests to confirm nothing broken**

```bash
python -m pytest karma-core/tests/test_watermark.py -v
```

Expected: 7 PASS (no regressions).

**Step 6: Dry-run validation (local, no Docker)**

```bash
python -c "
import sys; sys.path.insert(0, 'karma-core')
import batch_ingest, tempfile, os, json
with tempfile.TemporaryDirectory() as d:
    ledger = os.path.join(d, 'memory.jsonl')
    wm = os.path.join(d, '.watermark')
    # Write 5 fake entries
    with open(ledger, 'w') as f:
        for i in range(5):
            f.write(json.dumps({'content': {'user_message': f'q{i}', 'assistant_text': f'a{i}'}, 'tags': []}) + '\n')
    # First call: init watermark at line 5
    line = batch_ingest.read_watermark(wm, ledger)
    print(f'Init watermark: {line}')
    assert line == 5, f'Expected 5, got {line}'
    # Add 3 more entries
    with open(ledger, 'a') as f:
        for i in range(3):
            f.write(json.dumps({'content': {'user_message': f'new{i}', 'assistant_text': f'ans{i}'}, 'tags': []}) + '\n')
    # Read new only
    eps, end = batch_ingest.read_new_episodes(ledger, 5, 200)
    print(f'New episodes: {len(eps)}, end_line: {end}')
    assert len(eps) == 3
    assert end == 8
    print('ALL OK')
"
```

Expected output:
```
Init watermark: 5
New episodes: 3, end_line: 8
ALL OK
```

**Step 7: Commit**

```powershell
powershell -Command "cd C:\Users\raest\Documents\Karma_SADE; git add karma-core/batch_ingest.py; git commit -m 'feat: wire watermark into Graphiti mode in batch_ingest run()'"
```

---

## Task 3: Initialize Watermark & Update Cron on vault-neo

**This task runs on vault-neo after deployment (Task 4). Listed here for ordering clarity.**

**Step 1: Initialize watermark BEFORE changing cron**

```bash
ssh vault-neo "wc -l < /opt/seed-vault/memory_v1/ledger/memory.jsonl | tr -d ' ' > /opt/seed-vault/memory_v1/ledger/.batch_watermark && cat /opt/seed-vault/memory_v1/ledger/.batch_watermark"
```

Expected: prints current line count (e.g., `4073`). This sets the watermark so no historical episodes are processed.

**Step 2: Update cron to drop --skip-dedup and add WATERMARK_PATH**

```bash
ssh vault-neo "crontab -l"
```

Expected: shows current cron including `--skip-dedup` line.

```bash
ssh vault-neo "crontab -l | sed 's|--skip-dedup ||' | sed 's|LEDGER_PATH=/ledger/memory.jsonl|LEDGER_PATH=/ledger/memory.jsonl WATERMARK_PATH=/ledger/.batch_watermark|' | crontab -"
```

**Step 3: Verify cron updated correctly**

```bash
ssh vault-neo "crontab -l | grep batch_ingest"
```

Expected output (--skip-dedup gone, WATERMARK_PATH present):
```
0 */6 * * * docker exec karma-server sh -c 'LEDGER_PATH=/ledger/memory.jsonl WATERMARK_PATH=/ledger/.batch_watermark python3 /app/batch_ingest.py >> /tmp/batch.log 2>&1'
```

---

## Task 4: Deploy to vault-neo

**Step 1: Push to GitHub**

```powershell
powershell -Command "cd C:\Users\raest\Documents\Karma_SADE; git push origin main"
```

**Step 2: Pull on vault-neo + sync to build context**

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main && cp karma-core/batch_ingest.py /opt/seed-vault/memory_v1/karma-core/batch_ingest.py && cp -r karma-core/tests /opt/seed-vault/memory_v1/karma-core/ 2>/dev/null || true"
```

**Step 3: Rebuild karma-server image**

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/compose && docker compose -f /opt/seed-vault/memory_v1/compose/compose.yml build --no-cache karma-server"
```

Expected: Build completes without error. Takes ~60-90 seconds.

**Step 4: Restart karma-server**

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/compose && docker compose -f /opt/seed-vault/memory_v1/compose/compose.yml up -d karma-server"
```

**Step 5: Verify container healthy**

```bash
ssh vault-neo "docker ps --filter name=karma-server --format '{{.Names}} {{.Status}}'"
```

Expected: `karma-server Up X seconds (healthy)`

**Step 6: Check RestartCount still 0**

```bash
ssh vault-neo "docker inspect karma-server --format '{{.RestartCount}}'"
```

Expected: `0`

---

## Task 5: Verify Entity Extraction Working

**Step 1: Baseline entity count before manual run**

```bash
ssh vault-neo "docker exec falkordb redis-cli -p 6379 GRAPH.QUERY neo_workspace 'MATCH (n:Entity) RETURN count(n)'"
```

Note the count (currently 571).

**Step 2: Run batch_ingest manually with Graphiti mode (dry-run first)**

```bash
ssh vault-neo "docker exec karma-server sh -c 'LEDGER_PATH=/ledger/memory.jsonl WATERMARK_PATH=/ledger/.batch_watermark python3 /app/batch_ingest.py --dry-run'"
```

Expected: Shows "TO PROCESS: N new episodes" where N is episodes added since watermark was initialized. If N=0 (no new episodes yet), note this — it means watermark is working correctly (nothing to process).

**Step 3: If N > 0, run live**

```bash
ssh vault-neo "docker exec karma-server sh -c 'LEDGER_PATH=/ledger/memory.jsonl WATERMARK_PATH=/ledger/.batch_watermark python3 /app/batch_ingest.py > /tmp/batch_graphiti_test.log 2>&1' && docker exec karma-server tail -30 /tmp/batch_graphiti_test.log"
```

Expected log output includes:
- `Watermark: line XXXX`
- `TO PROCESS: N new episodes`
- Entity extraction activity (Graphiti logs)
- `Watermark advanced: line XXXX → YYYY`
- Final graph count showing Entity nodes > 571

**Step 4: Verify entity count increased**

```bash
ssh vault-neo "docker exec falkordb redis-cli -p 6379 GRAPH.QUERY neo_workspace 'MATCH (n:Entity) RETURN count(n)'"
```

Expected: count > 571 (if any new episodes existed since watermark init).

**Step 5: Verify watermark advanced**

```bash
ssh vault-neo "cat /opt/seed-vault/memory_v1/ledger/.batch_watermark"
```

Expected: line number > initial value from Task 3 Step 1.

**Step 6: Final commit (MEMORY.md update)**

Update MEMORY.md:
- `batch_ingest` status: `✅ Watermark-based Graphiti mode. Entity extraction live for new episodes.`
- Entity graph: growing

```powershell
powershell -Command "cd C:\Users\raest\Documents\Karma_SADE; git add MEMORY.md; git commit -m 'feat: graphiti watermark live — entity extraction enabled for new episodes'; git push origin main"
```

---

## Rollback Procedure

If Graphiti mode causes issues (timeouts, errors):

```bash
# Revert to --skip-dedup via cron
ssh vault-neo "crontab -l | sed 's|python3 /app/batch_ingest.py|python3 /app/batch_ingest.py --skip-dedup|' | crontab -"
```

No data is lost. Watermark file stays in place. Re-enabling later: remove --skip-dedup from cron again.

---

## Known Risks

| Risk | Mitigation |
|------|------------|
| Graphiti timeouts if >200 new eps per window | Hard cap at 200; excess caught next run |
| Watermark file corruption on crash | Atomic write via os.replace (tmp file) |
| `end_watermark` includes non-episode lines | read_new_episodes counts ALL lines for end_line; slight overcount is safe (just skips a few blank lines) |
| cron sed command fails on vault-neo | Verify with `crontab -l` before and after |
