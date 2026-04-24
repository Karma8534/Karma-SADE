#!/usr/bin/env python3
"""
Bridge Nexus transcript history into auto-memory's expected SQLite schema.

This keeps `python -m session_recall ...` operational even when Copilot's
native session-store.db is absent on this machine.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import tempfile
from typing import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[1]
TRANSCRIPT_DIR = ROOT / "tmp" / "transcripts"
DEFAULT_DB = pathlib.Path.home() / ".copilot" / "session-store.db"
FILE_RE = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z]:[\\/][^\\s\"'`<>|]+|(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+)")
URL_RE = re.compile(r"(https?://[^\s\"'`<>]+)")


def _detect_repo() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()
    except Exception:
        return "local/Karma_SADE"
    if not out:
        return "local/Karma_SADE"
    ssh = re.match(r"git@[^:]+:(.+?)(?:\.git)?$", out)
    if ssh:
        return ssh.group(1)
    https = re.match(r"https?://[^/]+/(.+?)(?:\.git)?$", out)
    if https:
        return https.group(1)
    return "local/Karma_SADE"


def _detect_branch() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip() or "main"
    except Exception:
        return "main"


def _to_iso(ts: float | None, fallback: str) -> str:
    if ts is None:
        return fallback
    try:
        return dt.datetime.fromtimestamp(float(ts), tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return fallback


def _parse_iso_ts(text: str) -> float | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    try:
        return dt.datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def _extract_paths_and_refs(text: str) -> tuple[list[str], list[str]]:
    if not text:
        return [], []
    refs = URL_RE.findall(text)
    files = []
    for m in FILE_RE.findall(text):
        raw = m.strip().rstrip(".,;:!?)]}")
        if len(raw) < 3:
            continue
        if raw.startswith("http://") or raw.startswith("https://"):
            continue
        files.append(raw.replace("\\", "/"))
    return files, refs


def _iter_transcript_files() -> Iterable[pathlib.Path]:
    if not TRANSCRIPT_DIR.exists():
        return []
    return sorted(TRANSCRIPT_DIR.glob("*.jsonl"))


def _load_events(path: pathlib.Path) -> list[dict]:
    events: list[dict] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            role = str(obj.get("role") or "").strip().lower()
            if role not in {"user", "assistant"}:
                continue
            content = str(obj.get("content") or "").strip()
            ts = obj.get("ts")
            timestamp = str(obj.get("timestamp") or "")
            ts_value = float(ts) if isinstance(ts, (int, float)) else _parse_iso_ts(timestamp)
            events.append(
                {
                    "role": role,
                    "content": content,
                    "ts": ts_value,
                    "timestamp": timestamp,
                }
            )
    except Exception:
        return []
    events.sort(key=lambda e: (e.get("ts") or 0.0, e.get("timestamp") or ""))
    return events


def _pair_turns(events: list[dict]) -> list[dict]:
    turns: list[dict] = []
    pending_user: dict | None = None
    for evt in events:
        role = evt["role"]
        if role == "user":
            if pending_user is not None:
                turns.append(
                    {
                        "user_message": pending_user["content"],
                        "assistant_response": "",
                        "timestamp": pending_user["timestamp"] or _to_iso(pending_user.get("ts"), "1970-01-01T00:00:00Z"),
                        "ts": pending_user.get("ts"),
                    }
                )
            pending_user = evt
            continue
        if role == "assistant":
            if pending_user is None:
                # Synthetic empty-user turn so assistant-only output is still searchable.
                turns.append(
                    {
                        "user_message": "",
                        "assistant_response": evt["content"],
                        "timestamp": evt["timestamp"] or _to_iso(evt.get("ts"), "1970-01-01T00:00:00Z"),
                        "ts": evt.get("ts"),
                    }
                )
            else:
                turns.append(
                    {
                        "user_message": pending_user["content"],
                        "assistant_response": evt["content"],
                        "timestamp": evt["timestamp"] or pending_user["timestamp"] or _to_iso(evt.get("ts") or pending_user.get("ts"), "1970-01-01T00:00:00Z"),
                        "ts": evt.get("ts") or pending_user.get("ts"),
                    }
                )
                pending_user = None
    if pending_user is not None:
        turns.append(
            {
                "user_message": pending_user["content"],
                "assistant_response": "",
                "timestamp": pending_user["timestamp"] or _to_iso(pending_user.get("ts"), "1970-01-01T00:00:00Z"),
                "ts": pending_user.get("ts"),
            }
        )
    return turns


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
          id TEXT PRIMARY KEY,
          repository TEXT,
          branch TEXT,
          summary TEXT,
          created_at TEXT,
          updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS turns (
          session_id TEXT,
          turn_index INTEGER,
          user_message TEXT,
          assistant_response TEXT,
          timestamp TEXT
        );
        CREATE TABLE IF NOT EXISTS session_files (
          session_id TEXT,
          file_path TEXT,
          tool_name TEXT,
          turn_index INTEGER,
          first_seen_at TEXT
        );
        CREATE TABLE IF NOT EXISTS session_refs (
          session_id TEXT,
          ref_type TEXT,
          ref_value TEXT,
          turn_index INTEGER,
          created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS checkpoints (
          session_id TEXT,
          checkpoint_number INTEGER,
          title TEXT,
          overview TEXT,
          created_at TEXT
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
          content,
          session_id UNINDEXED,
          source_type UNINDEXED
        );
        """
    )


def _open_db(path: pathlib.Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn


def _rebuild(conn: sqlite3.Connection) -> dict:
    repo = _detect_repo()
    branch = _detect_branch()
    now_iso = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = list(_iter_transcript_files())
    conn.execute("BEGIN IMMEDIATE")
    for table in ("sessions", "turns", "session_files", "session_refs", "checkpoints", "search_index"):
        conn.execute(f"DELETE FROM {table}")
    session_count = 0
    turn_count = 0
    file_ref_count = 0
    search_rows = 0
    for tf in files:
        session_id = tf.stem.lower()
        events = _load_events(tf)
        if not events:
            continue
        turns = _pair_turns(events)
        if not turns:
            continue
        created_ts = turns[0].get("ts")
        updated_ts = turns[-1].get("ts")
        created_at = _to_iso(created_ts, now_iso)
        updated_at = _to_iso(updated_ts, created_at)
        summary_src = ""
        for t in reversed(turns):
            if t.get("assistant_response"):
                summary_src = t["assistant_response"]
                break
        if not summary_src:
            summary_src = turns[-1].get("user_message") or "Session captured from Nexus transcript"
        summary = re.sub(r"\s+", " ", summary_src).strip()[:400]
        conn.execute(
            "INSERT INTO sessions (id, repository, branch, summary, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, repo, branch, summary, created_at, updated_at),
        )
        conn.execute(
            "INSERT INTO search_index (content, session_id, source_type) VALUES (?, ?, ?)",
            (summary, session_id, "summary"),
        )
        search_rows += 1
        seen_files: set[str] = set()
        seen_refs: set[str] = set()
        checkpoint_no = 0
        for idx, t in enumerate(turns, start=1):
            user_msg = str(t.get("user_message") or "")
            assistant_msg = str(t.get("assistant_response") or "")
            ts_iso = str(t.get("timestamp") or updated_at)
            conn.execute(
                "INSERT INTO turns (session_id, turn_index, user_message, assistant_response, timestamp) VALUES (?, ?, ?, ?, ?)",
                (session_id, idx, user_msg, assistant_msg, ts_iso),
            )
            turn_count += 1
            if user_msg.strip():
                conn.execute(
                    "INSERT INTO search_index (content, session_id, source_type) VALUES (?, ?, ?)",
                    (user_msg[:2000], session_id, "user"),
                )
                search_rows += 1
            if assistant_msg.strip():
                conn.execute(
                    "INSERT INTO search_index (content, session_id, source_type) VALUES (?, ?, ?)",
                    (assistant_msg[:2000], session_id, "assistant"),
                )
                search_rows += 1
            for text in (user_msg, assistant_msg):
                paths, refs = _extract_paths_and_refs(text)
                for p in paths:
                    if p in seen_files:
                        continue
                    seen_files.add(p)
                    conn.execute(
                        "INSERT INTO session_files (session_id, file_path, tool_name, turn_index, first_seen_at) VALUES (?, ?, ?, ?, ?)",
                        (session_id, p, "transcript", idx, ts_iso),
                    )
                    file_ref_count += 1
                    conn.execute(
                        "INSERT INTO search_index (content, session_id, source_type) VALUES (?, ?, ?)",
                        (p, session_id, "file"),
                    )
                    search_rows += 1
                for r in refs:
                    if r in seen_refs:
                        continue
                    seen_refs.add(r)
                    conn.execute(
                        "INSERT INTO session_refs (session_id, ref_type, ref_value, turn_index, created_at) VALUES (?, ?, ?, ?, ?)",
                        (session_id, "url", r, idx, ts_iso),
                    )
            if "working plan" in assistant_msg.lower():
                checkpoint_no += 1
                conn.execute(
                    "INSERT INTO checkpoints (session_id, checkpoint_number, title, overview, created_at) VALUES (?, ?, ?, ?, ?)",
                    (session_id, checkpoint_no, f"Working Plan {checkpoint_no}", assistant_msg[:500], ts_iso),
                )
        session_count += 1
    conn.commit()
    return {
        "ok": True,
        "db_path": str(conn.execute("PRAGMA database_list").fetchone()["file"]),
        "sessions": session_count,
        "turns": turn_count,
        "session_files": file_ref_count,
        "search_rows": search_rows,
        "source_transcripts": len(files),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bridge Nexus transcripts into auto-memory schema.")
    parser.add_argument("--db", default=os.environ.get("SESSION_RECALL_DB", str(DEFAULT_DB)), help="Target session-store.db path")
    parser.add_argument("--quiet", action="store_true", help="Suppress JSON output")
    args = parser.parse_args()

    db_path = pathlib.Path(args.db).expanduser().resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = pathlib.Path(tempfile.mkdtemp(prefix="auto-memory-", dir=str(db_path.parent)))
    tmp_db = tmp_dir / f"{db_path.name}.tmpbuild"
    conn = _open_db(tmp_db)
    try:
        _ensure_schema(conn)
        result = _rebuild(conn)
    finally:
        conn.close()
    os.replace(str(tmp_db), str(db_path))
    try:
        tmp_dir.rmdir()
    except Exception:
        pass
    result["db_path"] = str(db_path)
    result["updated_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not args.quiet:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
