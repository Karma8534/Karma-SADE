"""
TITANS Memory Tier Helpers for karma_regent.py
Imported at module level: from regent_memory_titans import *
Provides: LTM_FILE, PERSISTENT_FILE, LTM_DECAY_DAYS,
          _ltm_append_counter, _surprise_score, _ltm_trim,
          _ltm_entry_fresh, append_memory_ltm, append_memory_persistent,
          get_memory_context_tiered
"""
import json
import datetime
from pathlib import Path

# These must match CACHE_DIR in karma_regent.py
CACHE_DIR = Path("/mnt/c/dev/Karma/k2/cache")
LTM_FILE = CACHE_DIR / "regent_memory_ltm.jsonl"
PERSISTENT_FILE = CACHE_DIR / "regent_memory_persistent.jsonl"
LTM_DECAY_DAYS = 7

_ltm_append_counter = 0


def _surprise_score(entry_type: str, from_addr: str = "", content: str = "") -> float:
    """Heuristic surprise score 0.0-1.0 for memory tier routing."""
    if from_addr in ("colby", "sovereign"):
        return 1.0
    if entry_type in ("directive", "decision", "goal"):
        return 0.8
    if entry_type in ("guardrail_block", "error", "failure"):
        return 0.7
    if entry_type == "tool_result":
        return 0.5
    if entry_type in ("heartbeat", "online_check", "status"):
        return 0.1
    return 0.3


def _ltm_entry_fresh(line: str, cutoff: datetime.datetime) -> bool:
    """Return True if LTM entry is newer than cutoff."""
    try:
        ts_str = json.loads(line).get("ts", "")
        if not ts_str:
            return True
        return datetime.datetime.fromisoformat(ts_str.rstrip("Z")) >= cutoff
    except Exception:
        return True


def _ltm_trim(log_fn=None):
    """Remove LTM entries older than LTM_DECAY_DAYS."""
    if not LTM_FILE.exists():
        return
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=LTM_DECAY_DAYS)
        lines = [l for l in LTM_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
        kept = [l for l in lines if _ltm_entry_fresh(l, cutoff)]
        LTM_FILE.write_text(("\n".join(kept) + "\n") if kept else "", encoding="utf-8")
    except Exception as e:
        if log_fn:
            log_fn(f"ltm trim error: {e}")


def append_memory_ltm(entry: dict, log_fn=None):
    """Append entry to LTM file."""
    try:
        with open(LTM_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        if log_fn:
            log_fn(f"ltm append error: {e}")


def append_memory_persistent(entry: dict, log_fn=None):
    """Append entry to persistent memory file."""
    try:
        with open(PERSISTENT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        if log_fn:
            log_fn(f"persistent append error: {e}")


def get_memory_context_tiered(working_memory: list) -> str:
    """Return memory context: persistent + LTM (recent 10) + working (last 5 interactions).

    Args:
        working_memory: the _memory list from karma_regent (loaded at startup)
    """
    sections = []

    # Tier 2: Persistent (all entries, never decayed)
    if PERSISTENT_FILE.exists():
        try:
            lines = [l for l in PERSISTENT_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
            if lines:
                entries = [json.loads(l) for l in lines]
                p_lines = [f"[{e['ts'][:16]}] {e.get('content', '')}" for e in entries]
                sections.append("[PERSISTENT MEMORY]\n" + "\n".join(p_lines))
        except Exception:
            pass

    # Tier 1: LTM (recent 10, not decayed)
    if LTM_FILE.exists():
        try:
            cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=LTM_DECAY_DAYS)
            lines = [l for l in LTM_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
            fresh = [json.loads(l) for l in lines[-50:] if _ltm_entry_fresh(l, cutoff)]
            if fresh:
                ltm_lines = [f"[{e['ts'][:16]}] {e.get('content', '')}" for e in fresh[-10:]]
                sections.append("[LTM]\n" + "\n".join(ltm_lines))
        except Exception:
            pass

    # Tier 0: Working (last 5 interactions)
    interactions = [e for e in working_memory if e.get("type") == "interaction"][-5:]
    if interactions:
        i_lines = [f"[{e['ts'][:16]}] {e.get('content', '')}" for e in interactions]
        sections.append("[RECENT INTERACTIONS]\n" + "\n".join(i_lines))

    return "\n\n".join(sections)
