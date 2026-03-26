# Phase Backlog-3-F — TITANS Memory Tiers PLAN
**Created:** 2026-03-25 | **Session:** 146

## Tasks

### Task 1 — Read current `append_memory` + `get_memory_context` fully
**What:** Confirm exact lines to patch; identify all call sites for `append_memory()`
<verify>
- List all call sites of `append_memory()` in karma_regent.py
- Note current MAX_MEMORY_ENTRIES value
- Confirm MEMORY_FILE path constant
</verify>
<done>[x] All call sites identified (lines 805, 934). MAX_MEMORY_ENTRIES=200. MEMORY_FILE=CACHE_DIR/regent_memory.jsonl.</done>

### Task 2 — Add surprise scoring function + LTM/persistent append helpers
**What:** Insert into karma_regent.py after `get_memory_context()`:
- `_surprise_score(entry_type, from_addr, content)` → float 0.0–1.0
- `append_memory_ltm(entry)` — writes to regent_memory_ltm.jsonl
- `append_memory_persistent(entry)` — writes to regent_memory_persistent.jsonl
- LTM_FILE / PERSISTENT_FILE constants
- LTM_DECAY_DAYS = 7
- `_ltm_trim()` — removes LTM entries older than LTM_DECAY_DAYS, called every 100 appends
<verify>
- `python3 -c "import karma_regent"` passes on K2
</verify>
<done>[x] All helpers in regent_memory_titans.py (imported at line 7). import karma_regent passes.</done>

### Task 3 — Modify `append_memory()` to dual-write to tiers
**What:** After existing append logic, add:
```python
surprise = _surprise_score(entry_type, from_addr, content)
if surprise >= 1.0 and from_addr in ("colby", "sovereign"):
    append_memory_persistent(entry)
elif surprise >= 0.5:
    append_memory_ltm(entry)
```
Plumb `from_addr` parameter into `append_memory()` (optional kwarg, default "")
<verify>
- Syntax check passes
- Existing call sites without from_addr continue to work (default "")
</verify>
<done>[x] append_memory(entry_type, content, metadata=None, from_addr="") — TITANS routing at lines 161-169. Both call sites pass from_addr=from_addr. Syntax passes.</done>

### Task 4 — Update `get_memory_context()` to inject all tiers
**What:** New context assembly:
1. Load persistent: all entries from regent_memory_persistent.jsonl
2. Load LTM: last 10 non-decayed entries from regent_memory_ltm.jsonl
3. Load working: last 5 interactions (current behavior)
4. Combine: `[PERSISTENT]\n...\n[LTM]\n...\n[RECENT INTERACTIONS]\n...`
5. If persistent empty: skip PERSISTENT block
<verify>
- `get_memory_context()` returns string with all 3 sections when files have data
</verify>
<done>[x] get_memory_context() now calls get_memory_context_tiered(_memory) at line 173-174. Tiered logic in regent_memory_titans.py.</done>

### Task 5 — Deploy to K2 + verify
**What:** SCP updated karma_regent.py to K2, restart service, verify startup log
<verify>
- `python3 -c "import karma_regent"` passes on K2
- Regent log shows "memory loaded: N entries" after restart
- `ls -la /mnt/c/dev/Karma/k2/cache/regent_memory_ltm.jsonl` — file created on first LTM-worthy message
</verify>
<done>[x] import karma_regent passes on K2. Regent restarted clean: spine v1241, 15 stable, memory loaded 50 entries. Vesper/karma_regent.py + Vesper/regent_memory_titans.py updated on P1.</done>
