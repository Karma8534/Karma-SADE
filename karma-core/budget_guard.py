"""
Step 2.5: Budget Guard (Decision #11)
$5/day, $80/month caps. Log every LLM call. Reject if over budget.

Before every LLM call: query budget_log, sum costs.
Returns BUDGET_EXHAUSTED if over limit.
"""

import sqlite3
import os
import json
from datetime import datetime, timezone

DB_PATH = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")

DAILY_LIMIT = float(os.getenv("BUDGET_DAILY_LIMIT", "5.0"))
MONTHLY_LIMIT = float(os.getenv("BUDGET_MONTHLY_LIMIT", "80.0"))


def _ensure_budget_table(db: sqlite3.Connection):
    """Create budget_log table if not exists (already in schema, but safety check)."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS budget_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            model TEXT NOT NULL,
            operation TEXT NOT NULL DEFAULT 'inference',
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cost_usd REAL NOT NULL DEFAULT 0.0,
            metadata TEXT DEFAULT '{}'
        )
    """)
    db.commit()


def log_llm_call(model: str, operation: str, input_tokens: int,
                 output_tokens: int, cost_usd: float,
                 metadata: dict = None) -> dict:
    """
    Log an LLM call to budget_log.
    Call this AFTER every LLM inference to track spend.

    Returns: {logged: True, daily_total: float, monthly_total: float,
              daily_remaining: float, monthly_remaining: float}
    """
    db = sqlite3.connect(DB_PATH)
    try:
        _ensure_budget_table(db)
        now = datetime.now(timezone.utc).timestamp()

        db.execute("""
            INSERT INTO budget_log
            (timestamp, model, operation, input_tokens, output_tokens,
             cost_usd, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (now, model, operation, input_tokens, output_tokens,
              cost_usd, json.dumps(metadata or {})))
        db.commit()

        # Get current totals
        daily_total = _get_daily_total(db, now)
        monthly_total = _get_monthly_total(db, now)

        return {
            "logged": True,
            "daily_total": round(daily_total, 4),
            "monthly_total": round(monthly_total, 4),
            "daily_remaining": round(max(0, DAILY_LIMIT - daily_total), 4),
            "monthly_remaining": round(max(0, MONTHLY_LIMIT - monthly_total), 4),
        }
    finally:
        db.close()


def check_budget() -> dict:
    """
    Check if we're within budget BEFORE making an LLM call.
    Returns: {allowed: True/False, daily_total, monthly_total,
              daily_remaining, monthly_remaining}

    If allowed=False, the caller MUST NOT make the LLM call.
    """
    db = sqlite3.connect(DB_PATH)
    try:
        _ensure_budget_table(db)
        now = datetime.now(timezone.utc).timestamp()

        daily_total = _get_daily_total(db, now)
        monthly_total = _get_monthly_total(db, now)

        daily_ok = daily_total < DAILY_LIMIT
        monthly_ok = monthly_total < MONTHLY_LIMIT

        result = {
            "allowed": daily_ok and monthly_ok,
            "daily_total": round(daily_total, 4),
            "monthly_total": round(monthly_total, 4),
            "daily_remaining": round(max(0, DAILY_LIMIT - daily_total), 4),
            "monthly_remaining": round(max(0, MONTHLY_LIMIT - monthly_total), 4),
            "daily_limit": DAILY_LIMIT,
            "monthly_limit": MONTHLY_LIMIT,
        }

        if not daily_ok:
            result["reason"] = "BUDGET_EXHAUSTED_DAILY"
        elif not monthly_ok:
            result["reason"] = "BUDGET_EXHAUSTED_MONTHLY"

        return result
    finally:
        db.close()


def get_budget_report() -> dict:
    """Full budget report: daily, monthly, all-time, recent calls."""
    db = sqlite3.connect(DB_PATH)
    try:
        _ensure_budget_table(db)
        now = datetime.now(timezone.utc).timestamp()

        daily = _get_daily_total(db, now)
        monthly = _get_monthly_total(db, now)
        all_time = db.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) FROM budget_log"
        ).fetchone()[0]
        total_calls = db.execute(
            "SELECT COUNT(*) FROM budget_log"
        ).fetchone()[0]

        # Recent calls (last 10)
        recent = db.execute("""
            SELECT timestamp, model, operation, cost_usd, input_tokens, output_tokens
            FROM budget_log ORDER BY timestamp DESC LIMIT 10
        """).fetchall()

        recent_calls = []
        for ts, model, op, cost, inp, out in recent:
            recent_calls.append({
                "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
                "model": model,
                "operation": op,
                "cost_usd": round(cost, 6),
                "tokens": {"input": inp, "output": out},
            })

        return {
            "daily_spend": round(daily, 4),
            "monthly_spend": round(monthly, 4),
            "all_time_spend": round(all_time, 4),
            "total_calls": total_calls,
            "daily_limit": DAILY_LIMIT,
            "monthly_limit": MONTHLY_LIMIT,
            "daily_remaining": round(max(0, DAILY_LIMIT - daily), 4),
            "monthly_remaining": round(max(0, MONTHLY_LIMIT - monthly), 4),
            "recent_calls": recent_calls,
        }
    finally:
        db.close()


def _get_daily_total(db: sqlite3.Connection, now: float) -> float:
    """Sum cost_usd for today (UTC midnight to now)."""
    today_midnight = _utc_midnight(now)
    row = db.execute(
        "SELECT COALESCE(SUM(cost_usd), 0) FROM budget_log WHERE timestamp >= ?",
        (today_midnight,)
    ).fetchone()
    return row[0]


def _get_monthly_total(db: sqlite3.Connection, now: float) -> float:
    """Sum cost_usd for current month (UTC)."""
    dt = datetime.fromtimestamp(now, tz=timezone.utc)
    month_start = datetime(dt.year, dt.month, 1, tzinfo=timezone.utc).timestamp()
    row = db.execute(
        "SELECT COALESCE(SUM(cost_usd), 0) FROM budget_log WHERE timestamp >= ?",
        (month_start,)
    ).fetchone()
    return row[0]


def _utc_midnight(ts: float) -> float:
    """Get UTC midnight timestamp for the day containing ts."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc).timestamp()
