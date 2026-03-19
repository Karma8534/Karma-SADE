#!/usr/bin/env python3
"""Vesper pipeline blocker audit."""
import json
from pathlib import Path

BASE = Path("/mnt/c/dev/Karma/k2/cache")
ARIA = Path("/mnt/c/dev/Karma/k2/Aria")

# 1. Spine state
spine = json.loads((BASE / "vesper_identity_spine.json").read_text())
evo = spine.get("evolution", {})
stable = evo.get("stable_identity", [])
cands = evo.get("candidate_patterns", [])
print(f"SPINE v{evo.get('version',0)} | stable={len(stable)} | candidates={len(cands)}")
for s in stable:
    print(f"  STABLE: {s.get('candidate_id')} conf={s.get('confidence')} type={s.get('type')}")
for c in cands[:8]:
    print(f"  CAND:   {c.get('candidate_id')} conf={c.get('confidence')} type={c.get('type')}")

# 2. Pipeline status
status = json.loads((BASE / "regent_control/vesper_pipeline_status.json").read_text())
print(f"PIPELINE: self_improving={status['self_improving']} total_promotions={status.get('total_promotions')} last_gov={status.get('last_governor_run','?')[:19]}")

# 3. Queue depths
cand_dir = BASE / "regent_candidates"
done_dir = BASE / "regent_promoted"
cand_files = list(cand_dir.glob("*.json"))
done_files = list(done_dir.glob("*.json")) if done_dir.exists() else []
print(f"QUEUE: candidates={len(cand_files)} promoted_done={len(done_files)}")

# 4. Candidate confidence distribution
if cand_files:
    confs = []
    for f in cand_files[:20]:
        try:
            d = json.loads(f.read_text())
            confs.append(d.get("confidence", 0))
        except Exception:
            pass
    zero = sum(1 for c in confs if c == 0)
    high = sum(1 for c in confs if c >= 0.7)
    print(f"CAND CONFS (sample {len(confs)}): zero={zero} high(>=0.7)={high} values={sorted(confs)[:10]}")

# 5. Evolution log structured rate
evo_log = BASE / "regent_evolution.jsonl"
lines = evo_log.read_text(encoding="utf-8").splitlines()
recent = lines[-500:]
structured = []
for l in reversed(lines):
    if len(structured) >= 50:
        break
    try:
        e = json.loads(l)
        if "source" in e and "response_len" in e:
            structured.append(e)
    except Exception:
        pass
structured = list(reversed(structured))
tool_used_count = sum(1 for e in structured if e.get("tool_used"))
print(f"EVOLOG: total_lines={len(lines)} last_50_structured={len(structured)} tool_used_in_structured={tool_used_count}")
if structured:
    grades = [e.get("grade", "?") for e in structured[-5:]]
    print(f"  last 5 grades: {grades}")

# 6. Governor audit last 5
audit = BASE / "regent_control/governor_audit.jsonl"
if audit.exists():
    for l in audit.read_text().splitlines()[-5:]:
        try:
            e = json.loads(l)
            print(f"GOV: {e.get('ts','')[:19]} {e.get('event')} {e.get('candidate_id','')}")
        except Exception:
            pass
else:
    print("GOV AUDIT: not found")

# 7. Last watchdog summary (check for brief output)
brief = BASE / "vesper_watchdog_brief.json"
if brief.exists():
    b = json.loads(brief.read_text())
    print(f"WATCHDOG BRIEF: grade={b.get('grade','?')} window={b.get('window_size','?')} tool_rate={b.get('tool_rate','?')}")
else:
    print("WATCHDOG BRIEF: not found")

# 8. Check eval queue
eval_dir = BASE / "regent_eval_queue"
approved_dir = BASE / "regent_approved"
if eval_dir.exists():
    print(f"EVAL QUEUE: {len(list(eval_dir.glob('*.json')))} pending")
if approved_dir.exists():
    approved = list(approved_dir.glob("*.json"))
    print(f"APPROVED (pre-governor): {len(approved)}")
    for f in approved[:3]:
        try:
            d = json.loads(f.read_text())
            print(f"  {f.name}: gate_passed={d.get('gate',{}).get('passed')} decision={d.get('gate',{}).get('decision')} conf={d.get('confidence')}")
        except Exception:
            pass
