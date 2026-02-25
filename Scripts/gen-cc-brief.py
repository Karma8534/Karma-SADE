#!/usr/bin/env python3
"""
gen-cc-brief.py — Generate a CC session brief for Claude Code.
Writes a single-document pickup file so Claude Code can resume any session
with full context in seconds.
"""

import subprocess
import json
import urllib.request
import urllib.error
import datetime
import sys
import os

MEMORY_MD = "/home/neo/karma-sade/MEMORY.md"
DECISION_LOG = "/home/neo/karma-sade/checkpoint/known_good_v1/decision_log.jsonl"
FAILURE_LOG = "/home/neo/karma-sade/checkpoint/known_good_v1/failure_log.jsonl"
IDENTITY_JSON = "/home/neo/karma-sade/identity.json"
INVARIANTS_JSON = "/home/neo/karma-sade/invariants.json"
DIRECTION_MD = "/home/neo/karma-sade/direction.md"
REPO_PATH = "/home/neo/karma-sade"
OUTPUT_PATH = "/home/neo/karma-sade/cc-session-brief.md"
RAW_CONTEXT_URL = "http://localhost:8340/raw-context"


def extract_section(text, header):
    """Extract content between ## header and next ## section."""
    lines = text.splitlines()
    in_section = False
    result = []
    for line in lines:
        if line.strip().startswith("## ") and line.strip()[3:].strip().lower().startswith(header.lower()):
            in_section = True
            continue
        if in_section:
            if line.strip().startswith("## "):
                break
            result.append(line)
    content = "\n".join(result).strip()
    return content if content else None


def read_spine_file(path, name):
    """Read resurrection spine file (identity, invariants, direction) safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            if path.endswith(".json"):
                data = json.load(f)
                return json.dumps(data, indent=2)
            else:
                return f.read()
    except Exception as e:
        return f"[ERROR reading {name}: {e}]"


def read_memory_md():
    """Extract relevant sections from MEMORY.md."""
    try:
        with open(MEMORY_MD, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        return {
            "current_task": f"Could not read MEMORY.md: {e}",
            "blockers": "Not found.",
            "next_agenda": "Not found.",
            "last_updated": "Unknown",
        }

    # Trim current_task to last 40 lines — the section accumulates all history
    raw_task = extract_section(text, "Current Task") or "Not found."
    task_lines = raw_task.splitlines()
    if len(task_lines) > 40:
        current_task = "(trimmed — showing last 40 lines)\n" + "\n".join(task_lines[-40:])
    else:
        current_task = raw_task
    blockers = extract_section(text, "Blockers") or "None."
    next_agenda = (
        extract_section(text, "Next Session Agenda")
        or extract_section(text, "Next Milestone")
        or "Not found."
    )

    # Find last "Last Updated" line anywhere in the file
    last_updated = "Unknown"
    for line in reversed(text.splitlines()):
        if "last updated" in line.lower() or "updated:" in line.lower():
            last_updated = line.strip()
            break

    return {
        "current_task": current_task,
        "blockers": blockers,
        "next_agenda": next_agenda,
        "last_updated": last_updated,
    }


def get_git_state():
    """Get branch, last 5 commits, and status from the repo."""
    results = {}

    try:
        branch = subprocess.check_output(
            ["git", "-C", REPO_PATH, "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.STDOUT,
            text=True,
        ).strip()
        results["branch"] = branch
    except Exception as e:
        results["branch"] = f"Unknown ({e})"

    try:
        log = subprocess.check_output(
            ["git", "-C", REPO_PATH, "log", "--oneline", "-5"],
            stderr=subprocess.STDOUT,
            text=True,
        ).strip()
        results["log"] = log if log else "(no commits)"
    except Exception as e:
        results["log"] = f"Error: {e}"

    try:
        status = subprocess.check_output(
            ["git", "-C", REPO_PATH, "status", "--short"],
            stderr=subprocess.STDOUT,
            text=True,
        ).strip()
        results["status"] = status if status else "clean"
    except Exception as e:
        results["status"] = f"Error: {e}"

    return results


def read_jsonl_tail(path, n=3):
    """Read last n lines from a JSONL file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        return lines[-n:] if len(lines) >= n else lines
    except Exception as e:
        return [json.dumps({"error": str(e)})]


def format_decisions(lines):
    """Format decision log lines as bullet list."""
    if not lines:
        return "- No decisions found."
    bullets = []
    for line in lines:
        try:
            entry = json.loads(line)
            ts = entry.get("timestamp", "?")
            decision = entry.get("decision", "?")
            outcome = entry.get("outcome", "?")
            bullets.append(f"- [{ts}] {decision}\n  Outcome: {outcome}")
        except Exception:
            bullets.append(f"- (parse error) {line[:120]}")
    return "\n".join(bullets)


def format_failures(lines):
    """Format failure log lines as bullet list."""
    if not lines:
        return "- No failures found."
    bullets = []
    for line in lines:
        try:
            entry = json.loads(line)
            ts = entry.get("timestamp", "?")
            error = entry.get("error", "?")
            root_cause = entry.get("root_cause", "?")
            fix = entry.get("fix_applied", "?")
            bullets.append(
                f"- [{ts}] {error}\n  Root cause: {root_cause}\n  Fix: {fix}"
            )
        except Exception:
            bullets.append(f"- (parse error) {line[:120]}")
    return "\n".join(bullets)


def fetch_karma_context():
    """GET http://localhost:8340/raw-context and return trimmed context string."""
    try:
        req = urllib.request.Request(RAW_CONTEXT_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        context = data.get("context", str(data))
        if len(context) > 800:
            context = context[:800] + "\n... (trimmed to 800 chars)"
        return context
    except urllib.error.URLError as e:
        return f"Not available (URLError: {e.reason})"
    except Exception as e:
        return f"Not available ({type(e).__name__}: {e})"


def main():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    memory = read_memory_md()
    git = get_git_state()
    decision_lines = read_jsonl_tail(DECISION_LOG, 3)
    failure_lines = read_jsonl_tail(FAILURE_LOG, 3)
    karma_context = fetch_karma_context()

    # Load resurrection spine files
    identity_content = read_spine_file(IDENTITY_JSON, "identity.json")
    invariants_content = read_spine_file(INVARIANTS_JSON, "invariants.json")
    direction_content = read_spine_file(DIRECTION_MD, "direction.md")

    decisions_fmt = format_decisions(decision_lines)
    failures_fmt = format_failures(failure_lines)

    brief = f"""# CC Session Brief — {now}
> Auto-generated at session start. Read this instead of MEMORY.md. Full MEMORY.md available if deep dive needed.
> **RESURRECTION SPINE LOADED** — Karma identity + invariants + direction are CANONICAL and AUTHORITATIVE for this session.

## KARMA PERSISTENT IDENTITY (Resurrection Spine — Canonical Source of Truth)

### Identity (identity.json)
```json
{identity_content}
```

### Invariants (invariants.json)
```json
{invariants_content}
```

### Direction (direction.md)
```
{direction_content}
```

---

## Active Task
{memory['current_task']}

## Blockers
{memory['blockers']}

## Next Session Agenda
{memory['next_agenda']}

## Code State
Branch: {git['branch']}
Last 5 commits:
{git['log']}
Status: {git['status']}

## Recent Decisions
{decisions_fmt}

## Recent Failures (learn from these)
{failures_fmt}

## Karma Memory State
{karma_context}

---
Generated: {now} | MEMORY.md last updated: {memory['last_updated']}
"""

    try:
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8", errors="replace") as f:
            f.write(brief)
        print(f"Brief written to {OUTPUT_PATH}")
    except Exception as e:
        print(f"ERROR: Could not write brief: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
