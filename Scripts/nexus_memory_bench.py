#!/usr/bin/env python3
"""Nexus memory bench harness (LongMemEval-style smoke)."""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

SERVER = "http://127.0.0.1:7891"
OUT = Path("C:/Users/raest/Documents/Karma_SADE/tmp/nexus_memory_bench_latest.json")
TOKEN_FILE = Path("C:/Users/raest/Documents/Karma_SADE/.hub-chat-token")


def _auth_headers() -> dict:
    token = (os.environ.get("HUB_CHAT_TOKEN") or "").strip()
    if not token and TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8", errors="replace").strip()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _post(path: str, payload: dict, timeout: int = 10):
    req = urllib.request.Request(
        f"{SERVER}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers=_auth_headers(),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))


def _get(path: str, params: dict | None = None, timeout: int = 10):
    url = f"{SERVER}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method="GET", headers=_auth_headers())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))


def main():
    cases = [
        ("BENCH_TOKEN_ALPHA", "Decision token alpha for bench recall.", "hall_facts"),
        ("BENCH_TOKEN_BETA", "Event token beta for bench recall.", "hall_events"),
        ("BENCH_TOKEN_GAMMA", "Discovery token gamma for bench recall.", "hall_discoveries"),
    ]
    writes = []
    for token, text, hall in cases:
        payload = {
            "text": f"{text} token={token}",
            "title": f"bench:{token}",
            "project": "Karma_SADE",
            "wing": "Karma_SADE",
            "room": "bench",
            "hall": hall,
        }
        writes.append(_post("/memory/save", payload))

    start = time.time()
    search_hits = 0
    palace_hits = 0
    for token, _text, hall in cases:
        _s_code, s_data = _post("/memory/search", {"query": token, "limit": 5})
        body = json.dumps(s_data)
        if token in body:
            search_hits += 1
        _p_code, p_data = _post("/memory/search/palace", {"hall": hall, "limit": 20})
        body2 = json.dumps(p_data)
        if token in body2:
            palace_hits += 1

    _w_code, wake = _get("/memory/wakeup")
    duration_ms = int((time.time() - start) * 1000)
    result = {
        "ok": True,
        "writes": [code for code, _ in writes],
        "search_hits": search_hits,
        "palace_hits": palace_hits,
        "wakeup_has_bench_token": "BENCH_TOKEN_" in json.dumps(wake),
        "duration_ms": duration_ms,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    if search_hits < 2 or palace_hits < 2:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
