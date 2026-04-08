#!/usr/bin/env python3
"""Permissioned ingestion feeder for Nexus memory substrate.

Modes:
  - projects: code/docs files
  - convos: transcript/chat-like files
  - general: broad text ingestion
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path

CLAUDEMEM_URL = os.environ.get("CLAUDEMEM_URL", "http://127.0.0.1:37778")
DEFAULT_PROJECT = "Karma_SADE"
MAX_FILE_CHARS = 6000

PROJECT_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".txt", ".yaml", ".yml",
    ".ps1", ".sh", ".toml", ".ini", ".cfg",
}
CONVO_HINTS = ("transcript", "chat", "conversation", "session", "claude", "codex")
CONVO_EXTS = {".jsonl", ".md", ".txt", ".json"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "tmp", "dist", "build"}


def _post_json(path: str, payload: dict, timeout: int = 8):
    req = urllib.request.Request(
        f"{CLAUDEMEM_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))


def _hall_for(path: Path, text: str) -> str:
    sample = (text or "").lower()
    p = str(path).lower()
    if any(k in sample for k in ("decision", "decided", "policy", "architecture")):
        return "hall_facts"
    if any(k in sample for k in ("error", "failed", "traceback", "bug", "fix")):
        return "hall_events"
    if any(k in p for k in CONVO_HINTS):
        return "hall_events"
    return "hall_discoveries"


def _should_ingest(path: Path, mode: str) -> bool:
    ext = path.suffix.lower()
    name = path.name.lower()
    if mode == "projects":
        return ext in PROJECT_EXTS
    if mode == "convos":
        return ext in CONVO_EXTS and (any(h in name for h in CONVO_HINTS) or ext == ".jsonl")
    return ext in PROJECT_EXTS or ext in CONVO_EXTS


def run_feed(mode: str, root: str, limit: int = 100, project: str = DEFAULT_PROJECT) -> dict:
    root_path = Path(root).resolve()
    ingested = 0
    skipped = 0
    errors = []
    scanned = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if ingested >= limit:
                break
            p = Path(dirpath) / fname
            scanned += 1
            if not _should_ingest(p, mode):
                skipped += 1
                continue
            try:
                raw = p.read_text(encoding="utf-8", errors="replace")
                text = raw[:MAX_FILE_CHARS].strip()
                if not text:
                    skipped += 1
                    continue
                hall = _hall_for(p, text)
                room = mode
                title = f"{mode}:{p.name}"
                payload = {
                    "text": f"[{mode} ingest] {p}\n\n{text}",
                    "title": title[:180],
                    "project": project,
                    "wing": project,
                    "room": room,
                    "hall": hall,
                    "tunnel": None,
                }
                status, _resp = _post_json("/api/memory/save", payload, timeout=10)
                if status >= 400:
                    errors.append(f"{p}: http {status}")
                    continue
                ingested += 1
            except Exception as e:
                errors.append(f"{p}: {e}")
        if ingested >= limit:
            break

    return {
        "ok": True,
        "mode": mode,
        "root": str(root_path),
        "scanned": scanned,
        "ingested": ingested,
        "skipped": skipped,
        "errors": errors[:20],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["projects", "convos", "general"], default="general")
    ap.add_argument("--path", default=str(Path.cwd()))
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    args = ap.parse_args()
    print(json.dumps(run_feed(args.mode, args.path, args.limit, args.project), ensure_ascii=False))


if __name__ == "__main__":
    main()

