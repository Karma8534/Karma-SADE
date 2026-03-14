"""Patch kiki_v5.py to post cycle state to coordination bus."""
import shutil
from pathlib import Path

src = Path("/mnt/c/dev/Karma/k2/scripts/karma_kiki_v5.py")
backup = Path("/mnt/c/dev/Karma/k2/scripts/karma_kiki_v5.py.bak2")
shutil.copy(src, backup)

coord_func = '''
def post_coord_state(state: dict):
    """Post kiki cycle liveness to coordination bus."""
    import time as _time, os as _os, json as _json, urllib.request
    token = HUB_AUTH_TOKEN or _os.environ.get("HUB_AUTH_TOKEN", "").strip()
    if not token:
        return
    try:
        now = _time.time()
        last_ts_str = state.get("started_at", "")
        journal = CACHE_DIR / "kiki_journal.jsonl"
        if journal.exists():
            lines = journal.read_text().strip().split("\\n")
            for line in reversed(lines):
                try:
                    entry = _json.loads(line)
                    last_ts_str = entry.get("ts", last_ts_str)
                    break
                except Exception:
                    continue
        try:
            from datetime import datetime, timezone
            last_ts = datetime.fromisoformat(last_ts_str.replace("Z", "+00:00")).timestamp()
            age = now - last_ts
        except Exception:
            age = 9999
        loop_liveness = "ACTIVE" if age <= 180 else "STALE"
        state_file = CACHE_DIR / "kiki_state.json"
        issues_file = CACHE_DIR / "kiki_issues.jsonl"
        state_age = (now - state_file.stat().st_mtime) if state_file.exists() else 9999
        issues_age = (now - issues_file.stat().st_mtime) if issues_file.exists() else 9999
        critical_artifacts_ok = (state_age <= 300 and issues_age <= 300)
        payload = _json.dumps({
            "from": "karma",
            "to": "all",
            "urgency": "informational",
            "type": "inform",
            "content": _json.dumps({
                "loop_liveness": loop_liveness,
                "cycles": state.get("cycles", 0),
                "issues_closed": state.get("issues_closed", 0),
                "critical_artifacts_ok": critical_artifacts_ok,
                "state_age_s": round(state_age),
                "issues_age_s": round(issues_age),
                "reported_at": _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime())
            })
        }).encode()
        req = urllib.request.Request(
            "https://hub.arknexus.net/v1/coordination/post",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=5)
        log.debug("[COORD] cycle state posted")
    except Exception as e:
        log.debug(f"[COORD] post_coord_state failed: {e}")

'''

content = src.read_text()
content = content.replace("def main():", coord_func + "def main():")
content = content.replace(
    "            run_cycle(state)\n            save_state(state)",
    "            run_cycle(state)\n            save_state(state)\n            post_coord_state(state)"
)
src.write_text(content)
print("patched ok")
