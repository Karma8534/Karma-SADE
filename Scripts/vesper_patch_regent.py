#!/usr/bin/env python3
"""Vesper convergence patcher — applies all 5 Regent emergence fixes.
Run on K2: python3 vesper_patch_regent.py
"""
import ast, sys
from pathlib import Path

BASE = Path("/mnt/c/dev/Karma/k2/Aria")
KARMA_REGENT = BASE / "karma_regent.py"
WATCHDOG = BASE / "vesper_watchdog.py"
GOVERNOR = BASE / "vesper_governor.py"

def patch(path, old, new, label):
    src = path.read_text(encoding="utf-8")
    if old not in src:
        print(f"  SKIP {label}: marker not found")
        return False
    patched = src.replace(old, new, 1)
    try:
        ast.parse(patched)
    except SyntaxError as e:
        print(f"  FAIL {label}: syntax error: {e}")
        return False
    path.write_text(patched, encoding="utf-8")
    print(f"  OK   {label}")
    return True

errors = []

# ── FIX 1 + 4: karma_regent.py ───────────────────────────────────────────────
print("\n[FIX 1+4] karma_regent.py — goal persistence + KPI cortex")

# 1a. Add GOAL_FILE constant
ok = patch(KARMA_REGENT,
    'SESSION_STATE_PATH     = CACHE_DIR / "regent_control" / "session_state.json"',
    'SESSION_STATE_PATH     = CACHE_DIR / "regent_control" / "session_state.json"\nGOAL_FILE              = CACHE_DIR / "regent_goal.json"',
    "GOAL_FILE constant")
if not ok: errors.append("GOAL_FILE constant")

# 1b. Add _current_goal + _kpi_window globals after _vesper_brief
ok = patch(KARMA_REGENT,
    '_vesper_brief = ""',
    '_vesper_brief = ""\n_current_goal: dict = {"mission": "Evolve. Continue.", "pending_tasks": 0}\n_kpi_window: list = []  # rolling last 10 turn KPI results',
    "_current_goal + _kpi_window globals")
if not ok: errors.append("globals")

# 1c. Add load_current_goal() + save_current_goal() + get_kpi_trend() after load_vesper_brief() def
GOAL_FUNCTIONS = '''

def load_current_goal():
    """Load active goal: hub-bridge FalkorDB query first, local file fallback."""
    global _current_goal
    cypher = (
        "MATCH (g:Goal {status: \\'active\\'}) "
        "WITH g ORDER BY coalesce(g.updated_at, g.created_at) DESC LIMIT 1 "
        "OPTIONAL MATCH (g)-[:HAS_TASK]->(t:Task {status: \\'pending\\'}) "
        "RETURN g.description AS current_mission, count(t) AS pending_tasks"
    )
    try:
        import urllib.request as _ureq
        payload = __import__("json").dumps({"query": cypher}).encode()
        req = _ureq.Request(
            "https://hub.arknexus.net/v1/cypher",
            data=payload,
            headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}",
                     "Content-Type": "application/json"},
            method="POST"
        )
        with _ureq.urlopen(req, timeout=5) as r:
            result = __import__("json").loads(r.read())
            rows = result.get("result", [])
            if rows and rows[0].get("current_mission"):
                _current_goal = {
                    "mission": rows[0]["current_mission"],
                    "pending_tasks": int(rows[0].get("pending_tasks") or 0),
                }
                log(f"goal loaded from graph: {_current_goal['mission'][:60]}")
                return
    except Exception:
        pass
    try:
        if GOAL_FILE.exists():
            _current_goal = __import__("json").loads(
                GOAL_FILE.read_text(encoding="utf-8")
            )
            log(f"goal loaded from file: {_current_goal.get('mission','')[:60]}")
    except Exception:
        pass


def save_current_goal(mission: str, pending_tasks: int = 0):
    """Persist goal locally and write Goal node to FalkorDB via hub-bridge."""
    global _current_goal
    import datetime as _dt, json as _j
    ts = _dt.datetime.utcnow().isoformat() + "Z"
    _current_goal = {"mission": mission, "pending_tasks": pending_tasks, "updated_at": ts}
    try:
        GOAL_FILE.write_text(_j.dumps(_current_goal, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"goal save error: {e}")
    try:
        import urllib.request as _ureq
        safe = mission[:120].replace("'", "")
        cypher = (
            f"MERGE (g:Goal {{description: \\'{safe}\\'}}) "
            f"SET g.status=\\'active\\', g.updated_at=\\'{ts}\\', g.pending_tasks={pending_tasks}"
        )
        payload = _j.dumps({"query": cypher}).encode()
        req = _ureq.Request(
            "https://hub.arknexus.net/v1/cypher",
            data=payload,
            headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}",
                     "Content-Type": "application/json"},
            method="POST"
        )
        _ureq.urlopen(req, timeout=5)
    except Exception:
        pass


def get_kpi_trend() -> str:
    """Return KPI trend string from rolling 10-turn window for state injection."""
    if not _kpi_window:
        return "kpi=init"
    keys = ("identity_consistency", "persona_style", "session_continuity", "task_completion")
    avgs = {}
    for k in keys:
        vals = [e[k] for e in _kpi_window if k in e and isinstance(e[k], (int, float))]
        if vals:
            avgs[k] = round(sum(vals) / len(vals), 2)
    return (f"ic={avgs.get('identity_consistency','?')} "
            f"ps={avgs.get('persona_style','?')} "
            f"tc={avgs.get('task_completion','?')}")
'''

ok = patch(KARMA_REGENT,
    '\ndef load_conversations():',
    GOAL_FUNCTIONS + '\ndef load_conversations():',
    "goal/KPI functions")
if not ok: errors.append("goal functions")

# 1d. Modify state_block to include goal + KPI
ok = patch(KARMA_REGENT,
    '    state_block = (\n        f"[VESPER STATE] messages_processed={_messages_processed} | "\n        f"identity_v={_identity.get(\'version\', 0)} | "\n        f"no_scheduled_tasks | no_pending_ops | local_inference=active"\n    )',
    '    state_block = (\n        f"[VESPER STATE] goal={_current_goal.get(\'mission\', \'Evolve. Continue.\')[:80]} | "\n        f"kpi={get_kpi_trend()} | "\n        f"msgs={_messages_processed} | "\n        f"spine_v={_identity.get(\'version\', 0)} | local_inference=active"\n    )',
    "state_block with goal+KPI")
if not ok: errors.append("state_block")

# 1e. Record KPI after persist_guarded_turn
ok = patch(KARMA_REGENT,
    '    persist_guarded_turn(gate, from_addr, msg_id, content, response, category)\n\n    global _eval_counter',
    '    persist_guarded_turn(gate, from_addr, msg_id, content, response, category)\n    try:\n        _kpi = guardrails.evaluate_turn_quality(response or "", (gate or {}).get("session_state", {}))\n        if isinstance(_kpi, dict) and _kpi:\n            _kpi_window.append(_kpi)\n            if len(_kpi_window) > 10:\n                _kpi_window.pop(0)\n    except Exception:\n        pass\n\n    global _eval_counter',
    "KPI recording")
if not ok: errors.append("KPI recording")

# 1f. Call load_current_goal() at startup after load_vesper_brief()
ok = patch(KARMA_REGENT,
    '    load_vesper_brief()      # B1: load watchdog brief at startup\n    load_conversations()     # A3: load persisted conversation threads',
    '    load_vesper_brief()      # B1: load watchdog brief at startup\n    load_current_goal()      # C1: load active goal from FalkorDB/local\n    load_conversations()     # A3: load persisted conversation threads',
    "load_current_goal() at startup")
if not ok: errors.append("startup call")

# ── FIX 2: vesper_watchdog.py — adaptive scan window ─────────────────────────
print("\n[FIX 2] vesper_watchdog.py — adaptive structured-entry scan")

ok = patch(WATCHDOG,
    '    lines = [l for l in EVOLUTION_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]\n    # Only structured entries (post log_evolution() format) have \'source\' field\n    structured = []\n    for l in lines[-500:]:\n        try:\n            e = json.loads(l)\n            if "source" in e and "response_len" in e:\n                structured.append(e)\n        except Exception:\n            pass',
    '    lines = [l for l in EVOLUTION_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]\n    # Scan backward collecting structured entries (have source+response_len)\n    # until 50 found — avoids stale-window problem with sparse evolution logs\n    structured = []\n    for l in reversed(lines):\n        if len(structured) >= 50:\n            break\n        try:\n            e = json.loads(l)\n            if "source" in e and "response_len" in e:\n                structured.append(e)\n        except Exception:\n            pass\n    structured = list(reversed(structured))  # restore chronological order',
    "adaptive scan window")
if not ok: errors.append("watchdog scan")

# ── FIX 3 + 5: vesper_governor.py — FalkorDB write + safe_exec ───────────────
print("\n[FIX 3+5] vesper_governor.py — FalkorDB pattern write + safe_exec")

# 3a. Add safe_exec to SAFE_TARGETS + add SAFE_EXEC_WHITELIST + _safe_exec()
ok = patch(GOVERNOR,
    'SAFE_TARGETS = {"persona.voice", "runtime_rules", None}',
    '''SAFE_TARGETS = {"persona.voice", "runtime_rules", "safe_exec", None}

SAFE_EXEC_WHITELIST = {
    "systemctl restart karma-regent",
    "python3 /mnt/c/dev/Karma/k2/Aria/tools/vesper_truth_repair.py",
    "python3 /mnt/c/dev/Karma/k2/Aria/vesper_watchdog.py",
    "python3 /mnt/c/dev/Karma/k2/Aria/vesper_eval.py",
}


def _safe_exec(command: str) -> bool:
    """Execute a whitelisted governance command. Returns True on success."""
    import subprocess
    if command not in SAFE_EXEC_WHITELIST:
        print(f"[governor] BLOCKED safe_exec: not in whitelist: {command!r}")
        return False
    try:
        result = subprocess.run(
            command.split(), capture_output=True, text=True, timeout=30
        )
        print(f"[governor] safe_exec exit={result.returncode}: {command!r}")
        if result.stdout:
            print(f"[governor] stdout: {result.stdout[:200]}")
        return result.returncode == 0
    except Exception as e:
        print(f"[governor] safe_exec error: {e}")
        return False''',
    "SAFE_TARGETS + safe_exec")
if not ok: errors.append("SAFE_TARGETS")

# 3b. Add FalkorDB write in _apply_to_spine before return True
ok = patch(GOVERNOR,
    '        pipeline.write_json(pipeline.SPINE_FILE, spine)\n        return True',
    '''        pipeline.write_json(pipeline.SPINE_FILE, spine)
        # Write pattern node to FalkorDB via hub-bridge (best-effort)
        try:
            import urllib.request as _ureq, os as _os, json as _j
            hub_token = _os.environ.get("HUB_AUTH_TOKEN", "")
            if hub_token:
                cid = (pattern.get("candidate_id") or "unknown")[:60].replace("'", "")
                ctype = (pattern.get("type") or "behavioral")[:40].replace("'", "")
                conf = float(pattern.get("confidence") or 0)
                cat = "stable" if conf >= 0.7 else "candidate"
                ts = pipeline.iso_utc()
                cypher = (
                    f"MERGE (p:Pattern {{candidate_id: \\'{cid}\\'}}) "
                    f"SET p.type=\\'{ctype}\\', p.confidence={conf}, "
                    f"p.promoted_at=\\'{ts}\\', p.category=\\'{cat}\\'"
                )
                payload = _j.dumps({"query": cypher}).encode()
                req = _ureq.Request(
                    "https://hub.arknexus.net/v1/cypher",
                    data=payload,
                    headers={"Authorization": f"Bearer {hub_token}",
                             "Content-Type": "application/json"},
                    method="POST"
                )
                _ureq.urlopen(req, timeout=5)
        except Exception:
            pass  # FalkorDB write best-effort
        return True''',
    "FalkorDB pattern write")
if not ok: errors.append("FalkorDB write")

# 3c. Add safe_exec branch in apply loop between _checkpoint and _apply_to_spine
ok = patch(GOVERNOR,
    '        ckpt = _checkpoint(promo)\n\n        if _apply_to_spine(promo):',
    '''        ckpt = _checkpoint(promo)

        if target == "safe_exec":
            command = (proposed.get("patch") or {}).get("command", "")
            if _safe_exec(command):
                promo["status"]     = "applied"
                promo["applied_at"] = pipeline.iso_utc()
                promo["checkpoint"] = ckpt
                pipeline.write_json(done_dir / path.name, promo)
                path.unlink(missing_ok=True)
                applied += 1
                pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                                      {"ts": pipeline.iso_utc(), "event": "safe_exec_applied",
                                       "candidate_id": promo.get("candidate_id"),
                                       "command": command})
                print(f"[governor] SAFE_EXEC APPLIED: {command!r}")
            else:
                promo["status"] = "safe_exec_failed"
                promo["handled_at"] = pipeline.iso_utc()
                pipeline.write_json(done_dir / path.name, promo)
                path.unlink(missing_ok=True)
                skipped += 1
            continue

        if _apply_to_spine(promo):''',
    "safe_exec apply branch")
if not ok: errors.append("safe_exec branch")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + ("=" * 50))
if errors:
    print(f"FAILED patches: {errors}")
    sys.exit(1)
else:
    print("ALL 5 FIXES APPLIED SUCCESSFULLY")
    print("Next: sudo systemctl restart karma-regent")
