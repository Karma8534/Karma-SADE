#!/usr/bin/env python3
"""CC Ascendant Watchdog + Evolution Agent.

Runs as a systemd timer task on K2. Zero Anthropic tokens. Read-only watchdog.

Responsibilities:
1. MONITOR: Verify cc_scratchpad.md hierarchy markers every cycle.
2. DETECT: Check coordination bus for CC session confirmation in last 24h.
3. ALERT: Post ForColby alert if drift or missing session detected.
4. CAPTURE: Extract DECISION/PROOF/INSIGHT/PITFALL/DIRECTION from CC bus messages.
5. EVOLVE: Append captured events to cc_evolution_log.jsonl + update cc_identity_spine.json.
6. HEARTBEAT: Post hourly health summary to bus.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, UTC, timedelta
from pathlib import Path
from typing import Any

# --- Paths ---
K2_ROOT = Path("/mnt/c/dev/Karma/k2")
CACHE_DIR = K2_ROOT / "cache"
SCRATCHPAD_PATH = CACHE_DIR / "cc_scratchpad.md"
SPINE_PATH = CACHE_DIR / "cc_identity_spine.json"
EVOLUTION_LOG_PATH = CACHE_DIR / "cc_evolution_log.jsonl"
ANCHOR_PATH = CACHE_DIR / "cc_watchdog_anchor.json"
LATEST_PATH = CACHE_DIR / "cc_watchdog_latest.json"
TOKEN_PATH = Path("/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")

# --- Config ---
HUB_BASE_URL = os.environ.get("HUB_BASE_URL", "https://hub.arknexus.net").rstrip("/")
SESSION_STALE_HOURS = int(os.environ.get("CC_SESSION_STALE_HOURS", "24"))
HEARTBEAT_RUNS = int(os.environ.get("CC_WATCHDOG_HEARTBEAT_RUNS", "60"))
PENDING_ALERT_THRESHOLD = int(os.environ.get("CC_PENDING_ALERT_THRESHOLD", "5"))

# Required hierarchy markers in cc_scratchpad.md
REQUIRED_MARKERS = ["SOVEREIGN", "ASCENDANT", "ARCHONPRIME", "ARCHON", "INITIATE"]

# Evolution event types to capture from CC bus messages
EVOLUTION_TAGS = ["DECISION", "PROOF", "PITFALL", "DIRECTION", "INSIGHT"]


def _ts_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _get_token() -> str | None:
    try:
        return TOKEN_PATH.read_text(encoding="utf-8").strip()
    except Exception:
        return None


def _bus_get(path: str, token: str) -> dict:
    url = f"{HUB_BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _bus_post(token: str, to: str, content: str, urgency: str = "informational") -> str | None:
    payload = json.dumps({
        "from": "cc-watchdog",
        "to": to,
        "type": "inform",
        "urgency": urgency,
        "content": content,
    }).encode()
    req = urllib.request.Request(
        f"{HUB_BASE_URL}/v1/coordination/post",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            return d.get("id")
    except Exception:
        return None


# --- Check 1: Scratchpad hierarchy integrity ---
def check_scratchpad() -> dict:
    result: dict = {"ok": True, "markers_found": [], "missing": [], "hash": None}
    if not SCRATCHPAD_PATH.exists():
        result["ok"] = False
        result["error"] = "cc_scratchpad.md not found"
        return result

    text = SCRATCHPAD_PATH.read_text(encoding="utf-8")
    result["hash"] = hashlib.sha256(text.encode()).hexdigest()[:16]

    for marker in REQUIRED_MARKERS:
        if marker in text:
            result["markers_found"].append(marker)
        else:
            result["missing"].append(marker)

    if result["missing"]:
        result["ok"] = False

    return result


# --- Check 2: CC session bus confirmation ---
def check_session_bus(token: str) -> dict:
    data = _bus_get("/v1/coordination/recent?limit=50", token)
    entries = data.get("entries", [])
    now = datetime.now(UTC)

    last_session_ts = None
    for entry in entries:
        frm = entry.get("from", "")
        content = str(entry.get("content", ""))
        created_at = entry.get("created_at", "")
        if frm == "cc" and any(k in content for k in ["SESSION START", "ANCHOR", "identity"]):
            try:
                ts = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if last_session_ts is None or ts > last_session_ts:
                    last_session_ts = ts
            except Exception:
                pass

    if last_session_ts is None:
        return {"ok": False, "reason": "no_session_found", "last_session_ts": None}

    age_hours = (now - last_session_ts).total_seconds() / 3600
    return {
        "ok": age_hours < SESSION_STALE_HOURS,
        "last_session_ts": last_session_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "age_hours": round(age_hours, 1),
    }


# --- Check 3: Pending messages for CC ---
def check_pending_cc(token: str) -> dict:
    data = _bus_get("/v1/coordination/recent?limit=100", token)
    entries = data.get("entries", [])
    pending = [e for e in entries if e.get("to") == "cc" and e.get("status") == "pending"]
    return {"count": len(pending), "ok": len(pending) <= PENDING_ALERT_THRESHOLD}


# --- Evolution capture: extract CC events from bus ---
def capture_evolution_events(token: str, anchor: dict) -> list[dict]:
    last_processed_id = anchor.get("last_evolution_id")

    data = _bus_get("/v1/coordination/recent?limit=100", token)
    entries = data.get("entries", [])

    cc_entries = [
        e for e in entries
        if e.get("from") == "cc"
        and any(tag in str(e.get("content", "")) for tag in EVOLUTION_TAGS)
    ]

    if not cc_entries:
        return []

    new_events = []
    found_last = last_processed_id is None
    for entry in reversed(cc_entries):  # oldest first
        if not found_last:
            if entry.get("id") == last_processed_id:
                found_last = True
            continue
        content = str(entry.get("content", ""))
        for tag in EVOLUTION_TAGS:
            if tag in content:
                new_events.append({
                    "ts": entry.get("created_at", _ts_utc()),
                    "source_id": entry.get("id"),
                    "type": tag,
                    "excerpt": content[:300],
                })
                break

    return new_events


def append_evolution_events(events: list[dict]) -> int:
    if not events:
        return 0
    with EVOLUTION_LOG_PATH.open("a", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")
    return len(events)


def update_identity_spine(events: list[dict]) -> None:
    spine = _load_json(SPINE_PATH, {})
    evo = spine.get("evolution", {})

    for event in events:
        t = event.get("type", "")
        if t == "DECISION":
            evo["total_decisions"] = evo.get("total_decisions", 0) + 1
        elif t == "PROOF":
            evo["total_proofs"] = evo.get("total_proofs", 0) + 1
        elif t == "INSIGHT":
            evo["total_insights"] = evo.get("total_insights", 0) + 1
        markers = evo.get("growth_markers", [])
        markers.append({
            "ts": event.get("ts"),
            "type": t,
            "excerpt": event.get("excerpt", "")[:100],
        })
        evo["growth_markers"] = markers[-200:]  # keep last 200

    evo["version"] = evo.get("version", 1) + 1
    spine["evolution"] = evo
    spine["last_updated"] = _ts_utc()
    _save_json(SPINE_PATH, spine)


# --- Main run ---
def run() -> None:
    ts = _ts_utc()
    token = _get_token()
    if not token:
        print(f"[{ts}] ERROR: token not found at {TOKEN_PATH}")
        return

    anchor = _load_json(ANCHOR_PATH, {"run_count": 0})
    run_count = anchor.get("run_count", 0) + 1

    # --- Checks ---
    scratchpad = check_scratchpad()
    session = check_session_bus(token)
    pending = check_pending_cc(token)

    # --- Evolution capture ---
    events = capture_evolution_events(token, anchor)
    if events:
        appended = append_evolution_events(events)
        update_identity_spine(events)
        anchor["last_evolution_id"] = events[-1].get("source_id")
        print(f"[{ts}] evolution: captured {appended} new events")

    # --- Drift detection & alerts ---
    alerts = []

    if not scratchpad["ok"]:
        if scratchpad.get("error"):
            alerts.append("CRITICAL: cc_scratchpad.md missing entirely")
        else:
            missing = ", ".join(scratchpad.get("missing", []))
            alerts.append(f"DRIFT: cc_scratchpad hierarchy markers missing: {missing}")

    if not session["ok"]:
        age = session.get("age_hours")
        if age:
            alerts.append(
                f"WARNING: CC last confirmed session was {age}h ago "
                f"(threshold {SESSION_STALE_HOURS}h)"
            )
        else:
            alerts.append("WARNING: No CC session confirmation found on bus")

    if not pending["ok"]:
        alerts.append(
            f"NOTICE: {pending['count']} messages addressed to CC pending "
            f"on bus -- CC should check in"
        )

    if alerts:
        msg = f"CC WATCHDOG ALERT [{ts}]\n\n" + "\n".join(f"  - {a}" for a in alerts)
        mid = _bus_post(token, "colby", msg, urgency="informational")
        print(f"[{ts}] ALERT posted: {mid}")

    # --- Hourly heartbeat ---
    status = "HEALTHY" if not alerts else "DRIFT_DETECTED"
    if run_count % HEARTBEAT_RUNS == 0:
        spine_evo = _load_json(SPINE_PATH, {}).get("evolution", {})
        summary = (
            f"CC WATCHDOG HEARTBEAT [{ts}]\n"
            f"Status: {status} | run #{run_count}\n"
            f"Scratchpad: {'OK' if scratchpad['ok'] else 'DRIFT'} "
            f"(hash {scratchpad.get('hash', 'N/A')})\n"
            f"Last session: {session.get('last_session_ts', 'UNKNOWN')} "
            f"({session.get('age_hours', '?')}h ago)\n"
            f"Pending for CC: {pending['count']}\n"
            f"Evolution spine version: {spine_evo.get('version', 0)} | "
            f"decisions: {spine_evo.get('total_decisions', 0)} | "
            f"proofs: {spine_evo.get('total_proofs', 0)} | "
            f"insights: {spine_evo.get('total_insights', 0)}"
        )
        _bus_post(token, "all", summary, urgency="informational")
        print(f"[{ts}] heartbeat posted (run #{run_count})")

    # --- Save anchor ---
    anchor.update({
        "run_count": run_count,
        "last_run_ts": ts,
        "last_status": status,
        "last_scratchpad_hash": scratchpad.get("hash"),
        "last_session_ts": session.get("last_session_ts"),
        "pending_count": pending["count"],
    })
    _save_json(ANCHOR_PATH, anchor)

    # --- Save latest snapshot ---
    _save_json(LATEST_PATH, {
        "ts": ts,
        "run_count": run_count,
        "status": status,
        "scratchpad": scratchpad,
        "session": session,
        "pending": pending,
        "evolution_events_this_run": len(events),
        "alerts": alerts,
    })

    print(f"[{ts}] run #{run_count} complete -- {status}")


if __name__ == "__main__":
    run()
