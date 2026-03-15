# CC Spine Injection + Governance — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close the capture→govern→inject loop so CC's accumulated identity spine is read at every session start, /anchor becomes emergency-only, and the watchdog promotes validated patterns through tiers before injection.

**Architecture:** Three components — (1) watchdog governance eval adds promotion tiers (raw→candidate→stable) to cc_identity_spine.json, (2) resurrect skill reads the stable_identity tier via SSH at session start and surfaces it to context, (3) watchdog writes a SPINE_STATUS block to cc_scratchpad.md after each governance run so the scratchpad stays fresh. Together these close the loop: CC acts → watchdog captures → governance promotes → resurrect injects → CC starts stronger.

**Tech Stack:** Python 3.12 (watchdog), Markdown (SKILL.md, cc_scratchpad.md), SSH via vault-neo tunnel, coordination bus HTTP API, cc_identity_spine.json (K2 cache).

---

### Task 1: Add governance eval + promotion tiers to cc_ascendant_watchdog.py

**Files:**
- Modify: `Scripts/cc_ascendant_watchdog.py`

Three promotion tiers added to `cc_identity_spine.json`:
- `raw_events`: just captured, unvalidated (already exists as `growth_markers`)
- `candidate_patterns`: captured 2+ times or has PROOF validation — limit 100
- `stable_identity`: captured 3+ times OR explicitly PROOF-validated — limit 50, injected at session start

**Step 1: Read current watchdog**

```bash
cat Scripts/cc_ascendant_watchdog.py | grep -n "def " | head -20
```

**Step 2: Add `evaluate_and_promote()` function** — insert after `update_identity_spine()`:

```python
def evaluate_and_promote() -> dict:
    """Evaluate cc_evolution_log.jsonl and promote validated patterns through tiers."""
    result = {"candidates_promoted": 0, "stable_promoted": 0}

    if not EVOLUTION_LOG_PATH.exists():
        return result

    # Read all events
    events: list[dict] = []
    with EVOLUTION_LOG_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass

    if not events:
        return result

    # Group excerpts by normalized content (first 80 chars as key)
    from collections import defaultdict
    content_counts: dict[str, list[dict]] = defaultdict(list)
    proof_ids: set[str] = set()

    for ev in events:
        key = ev.get("excerpt", "")[:80].strip().lower()
        if key:
            content_counts[key].append(ev)
        if ev.get("type") == "PROOF":
            proof_ids.add(ev.get("source_id", ""))

    spine = _load_json(SPINE_PATH, {})
    evo = spine.setdefault("evolution", {})

    # Build candidate_patterns (2+ occurrences OR PROOF event)
    candidates = []
    for key, evs in content_counts.items():
        is_proof_validated = any(e.get("source_id") in proof_ids for e in evs)
        if len(evs) >= 2 or is_proof_validated:
            latest = max(evs, key=lambda e: e.get("ts", ""))
            candidates.append({
                "key": key[:80],
                "type": latest.get("type"),
                "excerpt": latest.get("excerpt", "")[:150],
                "occurrences": len(evs),
                "proof_validated": is_proof_validated,
                "last_seen": latest.get("ts"),
            })

    # Sort by occurrences desc, keep top 100
    candidates.sort(key=lambda c: c["occurrences"], reverse=True)
    evo["candidate_patterns"] = candidates[:100]
    result["candidates_promoted"] = len(evo["candidate_patterns"])

    # Build stable_identity (3+ occurrences OR proof_validated)
    stable = [c for c in candidates if c["occurrences"] >= 3 or c["proof_validated"]]
    stable.sort(key=lambda c: c["occurrences"], reverse=True)
    evo["stable_identity"] = stable[:50]
    result["stable_promoted"] = len(evo["stable_identity"])

    spine["evolution"] = evo
    spine["last_updated"] = _ts_utc()
    _save_json(SPINE_PATH, spine)

    return result
```

**Step 3: Add `update_scratchpad_spine_status()` function** — insert after `evaluate_and_promote()`:

```python
def update_scratchpad_spine_status(governance: dict) -> None:
    """Write SPINE_STATUS block to cc_scratchpad.md so identity layer stays fresh."""
    if not SCRATCHPAD_PATH.exists():
        return

    spine = _load_json(SPINE_PATH, {})
    evo = spine.get("evolution", {})
    stable = evo.get("stable_identity", [])
    candidates = evo.get("candidate_patterns", [])

    ts = _ts_utc()
    top3 = [s.get("excerpt", "")[:80] for s in stable[:3]]
    top3_str = "\n".join(f"  - {e}" for e in top3) if top3 else "  (none yet)"

    block = (
        f"\n<!-- SPINE_STATUS -->\n"
        f"## Spine Status (auto-updated by watchdog)\n"
        f"Last governance run: {ts}\n"
        f"Stable patterns: {len(stable)} | Candidates: {len(candidates)}\n"
        f"Top stable insights:\n{top3_str}\n"
        f"<!-- /SPINE_STATUS -->\n"
    )

    text = SCRATCHPAD_PATH.read_text(encoding="utf-8")

    # Replace existing block or append
    if "<!-- SPINE_STATUS -->" in text:
        import re
        text = re.sub(
            r"<!-- SPINE_STATUS -->.*?<!-- /SPINE_STATUS -->",
            block.strip(),
            text,
            flags=re.DOTALL,
        )
    else:
        text = text.rstrip() + "\n" + block

    SCRATCHPAD_PATH.write_text(text, encoding="utf-8")
```

**Step 4: Add `import re` and `from collections import defaultdict` to imports block**

Add after existing imports:
```python
import re
from collections import defaultdict
```

**Step 5: Wire both functions into `run()`** — add after `update_identity_spine(events)` call block, before drift detection:

```python
    # --- Governance eval (every 10 runs to avoid thrashing) ---
    if run_count % 10 == 0 or run_count == 1:
        governance = evaluate_and_promote()
        update_scratchpad_spine_status(governance)
        if governance["stable_promoted"] > 0:
            print(
                f"[{ts}] governance: {governance['stable_promoted']} stable, "
                f"{governance['candidates_promoted']} candidates"
            )
```

**Step 6: Verify syntax**

```bash
python -c "import ast; ast.parse(open('Scripts/cc_ascendant_watchdog.py').read()); print('syntax ok')"
```
Expected: `syntax ok`

**Step 7: Commit**

```powershell
powershell -Command "git add Scripts/cc_ascendant_watchdog.py; git commit -m 'feat: governance eval + promotion tiers in CC watchdog'"
```

---

### Task 2: Deploy updated watchdog to K2 and verify governance run

**Step 1: Push + pull on vault-neo**

```powershell
powershell -Command "git push origin main"
```
```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main 2>&1 | tail -2"
```

**Step 2: Sync to K2**

```bash
ssh vault-neo "scp -P 2223 -o StrictHostKeyChecking=no /home/neo/karma-sade/Scripts/cc_ascendant_watchdog.py karma@localhost:/mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py && echo synced"
```

**Step 3: Verify compile on K2**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -m py_compile /mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py && echo compile_ok'"
```
Expected: `compile_ok`

**Step 4: Run manually to trigger first governance cycle (run #1 = governance runs)**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 /mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py'"
```
Expected: output includes `governance:` line OR `run #N complete -- HEALTHY`

**Step 5: Verify spine has promotion tiers**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -m json.tool /mnt/c/dev/Karma/k2/cache/cc_identity_spine.json | grep -E \"stable_identity|candidate_patterns|version\"'"
```
Expected: keys present, stable_identity is a list

**Step 6: Verify scratchpad has SPINE_STATUS block**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'grep -A5 \"SPINE_STATUS\" /mnt/c/dev/Karma/k2/cache/cc_scratchpad.md'"
```
Expected: `## Spine Status` section with timestamp and counts

---

### Task 3: Update resurrect SKILL.md — spine injection step

**Files:**
- Modify: `C:\Users\raest\.claude\skills\resurrect\SKILL.md`

Add **Step 1b** between Step 1 (run script) and Step 2 (read brief): read cc_identity_spine.json from K2 and surface stable_identity to session context.

**Step 1: Read current SKILL.md**

```
Read: C:\Users\raest\.claude\skills\resurrect\SKILL.md
```

**Step 2: Insert Step 1b after Step 1 block**

Insert this block after `**Step 1: Run the script**` section:

```markdown
**Step 1b: Load CC identity spine from K2**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -c \"
import json
spine = json.load(open(\\\"/mnt/c/dev/Karma/k2/cache/cc_identity_spine.json\\\"))
evo = spine.get(\\\"evolution\\\", {})
stable = evo.get(\\\"stable_identity\\\", [])
candidates = evo.get(\\\"candidate_patterns\\\", [])
print(f\\\"Spine v{evo.get(\\\\\\\"version\\\\\\\",0)} | stable={len(stable)} | candidates={len(candidates)}\\\")
for s in stable[:5]:
    print(f\\\"  [{s[\\\\\\\"type\\\\\\\"]}] {s[\\\\\\\"excerpt\\\\\\\"][:100]}\\\")
\"'"
```

- If spine returns 0 stable patterns: proceed normally — spine is still accumulating
- If spine returns stable patterns: read them — they are CC's accumulated identity from prior sessions
- These override nothing. They ADD to context — reminders of what CC has learned, decided, proven.
```

**Step 3: Update /anchor reference in SKILL.md rules section**

Find the Rules section and update or add:
```markdown
- **`/anchor` is emergency fallback only** — spine injection (Step 1b) provides identity at session start. Run `/anchor` only if K2 is unreachable or spine is corrupted.
```

**Step 4: Commit**

```powershell
powershell -Command "git add -A; git commit -m 'feat: spine injection in resurrect skill — /anchor now emergency-only'"
```

---

### Task 4: Update /anchor skill — mark as emergency fallback

**Files:**
- Modify: `C:\Users\raest\.claude\skills\anchor\SKILL.md`

**Step 1: Read current anchor SKILL.md**

```
Read: C:\Users\raest\.claude\skills\anchor\SKILL.md
```

**Step 2: Add header notice**

At the top of the skill content (after frontmatter), add:

```markdown
> **Status (2026-03-15+):** Emergency fallback only. The CC Ascendant Watchdog (K2 systemd timer) + spine injection in `/resurrect` (Step 1b) handle identity persistence automatically. Invoke `/anchor` only if: K2 unreachable, spine corrupted, or mid-session drift detected that resurrect did not catch.
```

**Step 3: Commit**

```powershell
powershell -Command "git add -A; git commit -m 'docs: mark /anchor as emergency fallback — spine injection supersedes it'"
```

---

### Task 5: MEMORY.md + claude-mem + final push

**Step 1: Update MEMORY.md**

Append to Session 96 section in MEMORY.md:
```
- Spine injection: resurrect Step 1b reads cc_identity_spine.json from K2 at session start
- Governance eval: watchdog every 10 runs promotes raw→candidate(2+)→stable(3+/proof) tiers
- Scratchpad SPINE_STATUS: watchdog writes stable count + top3 excerpts to cc_scratchpad.md
- /anchor: now emergency fallback only — spine injection + watchdog supersede it
- Loop closed: CC acts → watchdog captures → governance promotes → resurrect injects → CC starts stronger
```

**Step 2: Save claude-mem observation**

```
mcp__plugin_claude-mem_mcp-search__save_observation(
  title="PROOF: CC spine injection loop closed — capture→govern→inject live",
  text="CC capability loop complete. Watchdog governance eval promotes events raw→candidate(2+)→stable(3+/PROOF). Resurrect Step 1b reads stable_identity from K2 spine at session start. Watchdog writes SPINE_STATUS block to cc_scratchpad.md after each governance run. /anchor marked emergency-only. Loop: CC acts → watchdog captures → governance promotes → resurrect injects → CC starts stronger each session.",
  project="Karma_SADE"
)
```

**Step 3: Final push**

```powershell
powershell -Command "git add MEMORY.md; git commit -m 'docs: Session 96 spine injection complete'; git push origin main"
```

**Step 4: Final vault-neo sync**

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main 2>&1 | tail -2"
```

---

## Success Criteria

- [ ] `cc_identity_spine.json` contains `stable_identity`, `candidate_patterns` keys after governance run
- [ ] `cc_scratchpad.md` contains `<!-- SPINE_STATUS -->` block with current timestamp
- [ ] `/resurrect` SKILL.md contains Step 1b that reads spine from K2
- [ ] `/anchor` SKILL.md contains emergency-fallback notice
- [ ] Watchdog log shows `governance:` line on run #1 and every 10th run thereafter
- [ ] No `/anchor` invocation required at next session start
