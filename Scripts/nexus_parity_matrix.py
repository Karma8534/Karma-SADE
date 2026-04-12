#!/usr/bin/env python3
"""
Deterministic parity matrix for Nexus browser/electron/runtime contracts.

Writes JSON artifact to tmp/parity-matrix-latest.json and exits non-zero on failure.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = pathlib.Path(r"C:\Users\raest\Documents\Karma_SADE")
OUT = ROOT / "tmp" / "parity-matrix-latest.json"
TOKEN_FILE = ROOT / ".hub-chat-token"


def _http_json(url: str, method: str = "GET", body: dict | None = None, token: str | None = None, timeout: int = 30):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        payload = json.loads(raw) if raw else {}
        return resp.status, payload, raw


def _find_latest_smoke() -> pathlib.Path | None:
    tmp = ROOT / "tmp"
    candidates = sorted(tmp.glob("electron-smoke*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _powershell_json(command: str) -> dict:
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=20,
    )
    return {
        "ok": completed.returncode == 0,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "returncode": completed.returncode,
    }


def main() -> int:
    results: dict[str, dict] = {}
    failures: list[str] = []
    token = TOKEN_FILE.read_text(encoding="utf-8").strip()

    # 1) Health parity (local/hub)
    try:
        code_local, payload_local, _ = _http_json("http://127.0.0.1:7891/health")
        code_hub, _, _ = _http_json("https://hub.arknexus.net/cc/health")
        ok = code_local == 200 and payload_local.get("ok") is True and code_hub == 200
        results["health_parity"] = {"ok": ok, "local_status": code_local, "hub_status": code_hub, "local_payload": payload_local}
        if not ok:
            failures.append("health_parity")
    except Exception as exc:  # noqa: BLE001
        results["health_parity"] = {"ok": False, "error": str(exc)}
        failures.append("health_parity")

    # 2) Chat parity (local and hub)
    probe = f"PARITY_CHAT_{int(time.time())}"
    try:
        code_local, payload_local, _ = _http_json(
            "http://127.0.0.1:7891/cc",
            method="POST",
            body={"message": f"Reply exactly {probe}", "session_id": "parity-chat-local"},
            token=token,
            timeout=120,
        )
        code_hub, payload_hub, _ = _http_json(
            "https://hub.arknexus.net/cc/v1/chat",
            method="POST",
            body={"message": f"Reply exactly {probe}", "session_id": "parity-chat-hub"},
            token=token,
            timeout=90,
        )
        text_local = str(payload_local.get("response", ""))
        text_hub = str(payload_hub.get("assistant_text", payload_hub.get("response", "")))
        ok = code_local == 200 and code_hub == 200 and probe in text_local and probe in text_hub
        results["chat_parity"] = {
            "ok": ok,
            "local_status": code_local,
            "hub_status": code_hub,
            "local_text": text_local[:120],
            "hub_text": text_hub[:120],
        }
        if not ok:
            failures.append("chat_parity")
    except Exception as exc:  # noqa: BLE001
        results["chat_parity"] = {"ok": False, "error": str(exc)}
        failures.append("chat_parity")

    # 3) Memory save/search parity on local surface
    mem_token = f"PARITY_MEM_{int(time.time())}"
    try:
        code_save, payload_save, _ = _http_json(
            "http://127.0.0.1:7891/memory/save",
            method="POST",
            body={"text": mem_token, "title": "parity-memory", "project": "Karma_SADE"},
            token=token,
            timeout=30,
        )
        code_search, payload_search, _ = _http_json(
            "http://127.0.0.1:7891/memory/search",
            method="POST",
            body={"query": mem_token, "limit": 5},
            token=token,
            timeout=30,
        )
        search_blob = json.dumps(payload_search, ensure_ascii=False)
        if mem_token not in search_blob:
            time.sleep(1.0)
            code_search, payload_search, _ = _http_json(
                "http://127.0.0.1:7891/memory/search",
                method="POST",
                body={"query": mem_token, "limit": 10},
                token=token,
                timeout=30,
            )
            search_blob = json.dumps(payload_search, ensure_ascii=False)
        ok = code_save == 200 and code_search == 200 and mem_token in search_blob
        results["memory_parity"] = {"ok": ok, "save_status": code_save, "search_status": code_search}
        if not ok:
            failures.append("memory_parity")
    except Exception as exc:  # noqa: BLE001
        results["memory_parity"] = {"ok": False, "error": str(exc)}
        failures.append("memory_parity")

    # 4) Cancel/retry parity
    try:
        stream_error: dict[str, str] = {}

        def _stream_probe():
            try:
                _http_json(
                    "http://127.0.0.1:7891/cc/stream",
                    method="POST",
                    body={"message": "Write a long response about parity in 800 words.", "session_id": "parity-cancel-stream"},
                    token=token,
                    timeout=180,
                )
            except Exception as exc:  # noqa: BLE001
                stream_error["stream"] = str(exc)

        t = threading.Thread(target=_stream_probe, daemon=True)
        t.start()
        time.sleep(1.0)
        code_cancel, payload_cancel, _ = _http_json("http://127.0.0.1:7891/cancel", token=token)
        code_retry, payload_retry, _ = _http_json(
            "http://127.0.0.1:7891/cc",
            method="POST",
            body={"message": "Reply exactly PARITY_RETRY_OK", "session_id": "parity-retry"},
            token=token,
            timeout=120,
        )
        ok = code_cancel == 200 and payload_cancel.get("ok") is True and code_retry == 200 and "PARITY_RETRY_OK" in str(payload_retry.get("response", ""))
        results["cancel_retry_parity"] = {"ok": ok, "cancel_status": code_cancel, "retry_status": code_retry}
        if not ok:
            failures.append("cancel_retry_parity")
    except Exception as exc:  # noqa: BLE001
        results["cancel_retry_parity"] = {"ok": False, "error": str(exc)}
        failures.append("cancel_retry_parity")

    # 5) Startup control parity (watchdog task + HKCU Run entries)
    try:
        task = _powershell_json("Get-ScheduledTask -TaskName KarmaProcessWatchdog -ErrorAction SilentlyContinue | Select-Object TaskName,State | ConvertTo-Json -Compress")
        run = _powershell_json("Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' | Select-Object NexusCCServer,NexusKarmaPersistent | ConvertTo-Json -Compress")
        task_ok = task["ok"] and "KarmaProcessWatchdog" in task["stdout"]
        run_ok = run["ok"] and "NexusCCServer" in run["stdout"] and "NexusKarmaPersistent" in run["stdout"]
        ok = task_ok and run_ok
        results["startup_parity"] = {"ok": ok, "task": task, "run_keys": run}
        if not ok:
            failures.append("startup_parity")
    except Exception as exc:  # noqa: BLE001
        results["startup_parity"] = {"ok": False, "error": str(exc)}
        failures.append("startup_parity")

    # 6) Electron parity uses latest smoke artifact
    try:
        latest = _find_latest_smoke()
        if not latest:
            raise RuntimeError("no electron smoke artifact found")
        payload = json.loads(latest.read_text(encoding="utf-8"))
        ok = bool(payload.get("ok")) and bool(payload.get("uiResult", {}).get("ok")) and bool(payload.get("directResult", {}).get("ok"))
        results["electron_parity"] = {"ok": ok, "artifact": str(latest), "provider": payload.get("directResult", {}).get("provider")}
        if not ok:
            failures.append("electron_parity")
    except Exception as exc:  # noqa: BLE001
        results["electron_parity"] = {"ok": False, "error": str(exc)}
        failures.append("electron_parity")

    overall = not failures
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "ok": overall,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "failures": failures,
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(str(OUT))
    if failures:
        print("FAILURES:", ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
