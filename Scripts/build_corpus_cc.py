#!/usr/bin/env python3
"""
build_corpus_cc.py

Generate Karma2/training/corpus_cc.jsonl from local Claude Code session JSONL files.
This resolves the E-1-A corpus_cc gap without relying on stale stubs.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

SESSIONS_DIR = Path.home() / ".claude/projects/C--Users-raest-Documents-Karma-SADE"
OUT_PATH = Path(r"C:\Users\raest\Documents\Karma_SADE\Karma2\training\corpus_cc.jsonl")

# Keep CC corpus clean by filtering prompt-dumps and orchestration boilerplate.
EXCLUDE_SNIPPETS = (
    "ARKNEXUS ASCENDANCE = 100",
    "Base directory for this skill:",
    "Read file:",
    "mcp__plugin_claude-mem",
    "FINAL_GATE:",
)


def _parse_message_field(raw):
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            value = ast.literal_eval(raw)
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}
    return {}


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = str(block.get("text", "")).strip()
                if text:
                    parts.append(text)
        return "\n".join(parts).strip()
    return ""


def _keep_pair(user_text: str, assistant_text: str) -> bool:
    if not user_text or not assistant_text:
        return False
    if len(user_text) < 6 or len(user_text) > 700:
        return False
    if len(assistant_text) < 20 or len(assistant_text) > 5000:
        return False
    if "```" in user_text:
        return False
    upper_user = user_text.upper()
    for token in EXCLUDE_SNIPPETS:
        if token.upper() in upper_user:
            return False
    return True


def build(limit_files: int = 0) -> tuple[int, int]:
    files = sorted(SESSIONS_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if limit_files > 0:
        files = files[:limit_files]

    kept = 0
    seen = 0
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUT_PATH.open("w", encoding="utf-8") as writer:
        for fp in files:
            try:
                lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue

            pending_user = None
            for raw in lines:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    row = json.loads(raw)
                except Exception:
                    continue

                msg_obj = _parse_message_field(row.get("message", {}))
                if not msg_obj:
                    continue
                role = str(msg_obj.get("role", row.get("type", ""))).strip().lower()
                text = _extract_text(msg_obj.get("content", ""))
                if not text:
                    continue

                if role == "user":
                    pending_user = text
                elif role == "assistant" and pending_user:
                    seen += 1
                    if _keep_pair(pending_user, text):
                        writer.write(json.dumps({
                            "instruction": pending_user,
                            "input": "",
                            "output": text,
                        }, ensure_ascii=False) + "\n")
                        kept += 1
                    pending_user = None

    return kept, seen


def main():
    parser = argparse.ArgumentParser(description="Build corpus_cc.jsonl from local CC sessions")
    parser.add_argument("--limit-files", type=int, default=0, help="Optional cap on newest session files")
    args = parser.parse_args()

    kept, seen = build(limit_files=args.limit_files)
    print(json.dumps({
        "ok": True,
        "output": str(OUT_PATH),
        "pairs_seen": seen,
        "pairs_kept": kept,
    }))


if __name__ == "__main__":
    main()

