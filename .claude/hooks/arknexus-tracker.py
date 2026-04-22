#!/usr/bin/env python3
"""arknexus-tracker.py - UserPromptSubmit hook (plan v2 §2.7 rewrite)

Computes Ascendance percentage from evidence/ascendance-run-*/EVIDENCE_INDEX.json.
Cache-disabled: every invocation recomputes; state file is snapshot-only (not truth).

Directive v3 gates G1..G14 (14 total). SHIPPED requires all 14 latest status == VERIFIED.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent.parent
EVIDENCE = ROOT / "evidence"
STATE = ROOT / ".claude" / "hooks" / ".arknexus-tracker-state.json"

GATE_IDS = [
    "G1_BOOT_DOM_ATTR", "G2_COLD_BOOT_RERUN", "G3_PARITY_BROWSER_SCREEN", "G4_PARITY_STRESS",
    "G5_WHOAMI_REAL_UI", "G6_RITUAL_STEP4_FRESH_BROWSER", "G7_RITUAL_STEP10_FIRST_PAINT",
    "G8_RITUAL_UNINTERRUPTED_RECORDING", "G9_DUAL_WRITE_DISCIPLINE", "G10_GIT_AND_MEMORY",
    "G11_QUARANTINE_CLEANUP", "G12_VAULT_PARITY", "G13_FOCUS_GATE_UNLOCK", "G14_TRACKER_SCHEMA_ALIGNMENT",
]


def latest_run_dir() -> Path | None:
    if not EVIDENCE.exists():
        return None
    candidates = [d for d in EVIDENCE.iterdir() if d.is_dir() and (d.name.startswith("ascendance-run-") or d.name.startswith("ascendance-dry-run-"))]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def load_index(run_dir: Path) -> list:
    idx = run_dir / "EVIDENCE_INDEX.json"
    if not idx.exists():
        return []
    try:
        data = json.loads(idx.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def latest_per_gate(index: list) -> dict:
    latest = {}
    for row in index:
        gid = row.get("gate_id")
        if gid not in GATE_IDS:
            continue
        attempt = row.get("attempt_n", 0)
        if gid not in latest or attempt >= latest[gid].get("attempt_n", 0):
            latest[gid] = row
    return latest


def compute(run_dir: Path | None) -> dict:
    if run_dir is None:
        return {
            "pct": 0,
            "overall": "NOT_STARTED",
            "run_dir": None,
            "gates_verified": 0,
            "gates_fail": 0,
            "gates_blocked": 0,
            "gates_missing": len(GATE_IDS),
        }
    idx = load_index(run_dir)
    latest = latest_per_gate(idx)
    verified = fail = blocked = 0
    for gid in GATE_IDS:
        row = latest.get(gid)
        if row is None:
            continue
        status = row.get("status", "")
        if status == "VERIFIED":
            verified += 1
        elif status == "FAIL":
            fail += 1
        elif status == "BLOCKED":
            blocked += 1
    missing = len(GATE_IDS) - (verified + fail + blocked)
    pct = int((verified / len(GATE_IDS)) * 100)
    # SHIPPED requires all 14 VERIFIED AND FINAL_GATE verifier exit 0 (written to run_dir/FINAL_GATE_exit)
    exit_marker = run_dir / "FINAL_GATE_exit"
    shipped = (verified == len(GATE_IDS)) and exit_marker.exists() and exit_marker.read_text().strip() == "0"
    overall = "ASCENDANCE = 100 (SHIPPED)" if shipped else "BUILDING"
    return {
        "pct": 100 if shipped else pct,
        "overall": overall,
        "run_dir": str(run_dir),
        "gates_verified": verified,
        "gates_fail": fail,
        "gates_blocked": blocked,
        "gates_missing": missing,
        "shipped": shipped,
    }


def save_snapshot(data: dict) -> None:
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        data["last_run"] = datetime.now(timezone.utc).isoformat()
        STATE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def format_block(d: dict) -> str:
    lines = [
        "=" * 66,
        f"ARKNEXUS ASCENDANCE TRACKER - {d['pct']}% - {d['overall']}",
        "=" * 66,
        f"  run_dir: {d['run_dir'] or '(none)'}",
        f"  gates: {d['gates_verified']}/14 VERIFIED | {d['gates_fail']} FAIL | {d['gates_blocked']} BLOCKED | {d['gates_missing']} MISSING",
    ]
    if d.get("shipped"):
        lines.append("  STATUS: SHIPPED - directive v3 verifier exit 0")
    else:
        lines.append("  NEXT: close remaining gates; run Scripts/ascendance-final-gate.ps1")
    lines.append("  RULES: P113 binary labels only | P064 dual-write | P089 live probe only | P114 atomic phase commits")
    lines.append("=" * 66)
    return "\n".join(lines)


def main() -> int:
    try:
        run_dir = latest_run_dir()
        d = compute(run_dir)
        save_snapshot(d)
        # Silent once shipped
        if d.get("shipped"):
            return 0
        print(format_block(d))
        return 0
    except Exception as e:
        print(f"[arknexus-tracker] non-fatal: {e}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
