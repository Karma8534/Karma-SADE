"""
Token Budget Enforcement — Decision #11
Per-session: 50K tokens (SESSION_TOKEN_BUDGET)
Monthly cap: configurable (MONTHLY_TOKEN_CAP)
"""
import json
import os
import time
import threading
from datetime import datetime, timezone
from typing import Tuple
import tiktoken
import config

# ─── Config (add to config.py) ───
# SESSION_TOKEN_BUDGET = int(os.getenv("SESSION_TOKEN_BUDGET", "50000"))
# MONTHLY_TOKEN_CAP = int(os.getenv("MONTHLY_TOKEN_CAP", "500000"))
# TOKEN_USAGE_PATH = os.getenv("TOKEN_USAGE_PATH", "/ledger/token_usage.json")

_encoder = tiktoken.get_encoding("cl100k_base")
_lock = threading.Lock()


def count_tokens(text: str) -> int:
    """Count tokens in a string using cl100k_base encoding."""
    if not text:
        return 0
    return len(_encoder.encode(text))


def count_message_tokens(messages: list[dict]) -> int:
    """Count tokens across a list of OpenAI-format messages."""
    total = 0
    for msg in messages:
        total += 4  # message overhead
        total += count_tokens(msg.get("content", ""))
        total += count_tokens(msg.get("role", ""))
    total += 2  # reply priming
    return total


class SessionBudget:
    """Tracks token usage for a single session."""
    def __init__(self, budget: int = None):
        self.budget = budget or config.SESSION_TOKEN_BUDGET
        self.used = 0
        self.started_at = time.time()

    def consume(self, tokens: int):
        self.used += tokens

    def check(self) -> Tuple[bool, int, str]:
        remaining = self.budget - self.used
        if remaining <= 0:
            return False, 0, f"Session budget exhausted ({self.used}/{self.budget} tokens)"
        return True, remaining, "ok"

    def to_dict(self) -> dict:
        return {
            "budget": self.budget,
            "used": self.used,
            "remaining": self.budget - self.used,
            "started_at": self.started_at,
        }


class MonthlyTracker:
    """Tracks cumulative token usage per calendar month.
    Persists to TOKEN_USAGE_PATH (JSON)."""
    def __init__(self):
        self.cap = config.MONTHLY_TOKEN_CAP
        self.path = config.TOKEN_USAGE_PATH
        self._data = self._load()

    def _current_month(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def _load(self) -> dict:
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self):
        with _lock:
            try:
                os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
                with open(self.path, "w") as f:
                    json.dump(self._data, f, indent=2)
            except Exception as e:
                print(f"[TOKEN_BUDGET] Failed to save monthly usage: {e}")

    def consume(self, tokens: int):
        month = self._current_month()
        self._data.setdefault(month, 0)
        self._data[month] += tokens
        self._save()

    def check(self) -> Tuple[bool, int, str]:
        month = self._current_month()
        used = self._data.get(month, 0)
        remaining = self.cap - used
        if remaining <= 0:
            return False, 0, f"Monthly cap exhausted ({used}/{self.cap} tokens for {month})"
        return True, remaining, "ok"

    def get_usage(self) -> dict:
        month = self._current_month()
        used = self._data.get(month, 0)
        return {
            "month": month,
            "used": used,
            "cap": self.cap,
            "remaining": self.cap - used,
        }


# Singleton monthly tracker (shared across sessions)
_monthly = None


def get_monthly_tracker() -> MonthlyTracker:
    global _monthly
    if _monthly is None:
        _monthly = MonthlyTracker()
    return _monthly


def check_budget(session: SessionBudget) -> Tuple[bool, dict]:
    """Check both session and monthly budgets.
    Returns (allowed, details_dict)."""
    s_ok, s_rem, s_reason = session.check()
    monthly = get_monthly_tracker()
    m_ok, m_rem, m_reason = monthly.check()
    allowed = s_ok and m_ok
    reason = "ok" if allowed else (s_reason if not s_ok else m_reason)
    return allowed, {
        "allowed": allowed,
        "reason": reason,
        "session": session.to_dict(),
        "monthly": monthly.get_usage(),
    }
