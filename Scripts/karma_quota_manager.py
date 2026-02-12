"""
Karma SADE - API Quota Management System
=========================================
Tracks and limits usage of paid APIs to control costs.

Features:
- Daily/monthly quota limits per API
- Cost tracking and alerts
- SQLite-based persistence
- Automatic reset at midnight
- Usage statistics and reporting
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger("karma.quota")

# Database path
DB_PATH = Path(__file__).parent.parent / "Data" / "karma_quotas.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class QuotaManager:
    """Manages API quotas and cost tracking"""

    # Default quota limits (optimized for 2-week budget maximization)
    # User budget: $15 Claude spread over 2 weeks = $1.07/day
    # Strategy: Save Claude for premium tasks, use cheaper alternatives
    DEFAULT_QUOTAS = {
        "claude": {
            "daily_limit": 71,          # $15 ÷ 14 days ÷ $0.015 = 71 queries/day (max budget)
            "monthly_limit": 1000,      # Max 1000/month (~$15)
            "cost_per_query": 0.015,    # Average cost
            "warning_threshold": 0.8    # Warn at 80%
        },
        "openai": {
            "daily_limit": 150,         # Allow more OpenAI since it's cheaper
            "monthly_limit": 4500,      # Max 4500/month (~$11.25)
            "cost_per_query": 0.0025,
            "warning_threshold": 0.8
        },
        "zai_paid": {
            "daily_limit": 250,         # GLM-5 is cheapest paid option
            "monthly_limit": 7500,      # Max 7500/month (~$30)
            "cost_per_query": 0.004,
            "warning_threshold": 0.8
        },
        "perplexity": {
            "daily_limit": 100,         # Cheapest, allow more for research
            "monthly_limit": 3000,      # Max 3000/month (~$3)
            "cost_per_query": 0.001,
            "warning_threshold": 0.8
        }
    }

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Usage tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cost REAL NOT NULL,
                tokens_input INTEGER DEFAULT 0,
                tokens_output INTEGER DEFAULT 0,
                model TEXT,
                success BOOLEAN DEFAULT 1
            )
        """)

        # Quota configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quota_config (
                api_name TEXT PRIMARY KEY,
                daily_limit INTEGER NOT NULL,
                monthly_limit INTEGER NOT NULL,
                cost_per_query REAL NOT NULL,
                warning_threshold REAL DEFAULT 0.8,
                enabled BOOLEAN DEFAULT 1
            )
        """)

        # Daily stats cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE NOT NULL,
                api_name TEXT NOT NULL,
                query_count INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0,
                PRIMARY KEY (date, api_name)
            )
        """)

        conn.commit()
        conn.close()

        # Initialize default quotas if not exists
        self._load_default_quotas()

    def _load_default_quotas(self):
        """Load default quota configurations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for api_name, config in self.DEFAULT_QUOTAS.items():
            cursor.execute("""
                INSERT OR IGNORE INTO quota_config
                (api_name, daily_limit, monthly_limit, cost_per_query, warning_threshold)
                VALUES (?, ?, ?, ?, ?)
            """, (
                api_name,
                config["daily_limit"],
                config["monthly_limit"],
                config["cost_per_query"],
                config["warning_threshold"]
            ))

        conn.commit()
        conn.close()

    def check_quota(self, api_name: str) -> Tuple[bool, str]:
        """
        Check if API has quota remaining

        Returns:
            (can_use, reason)
            - (True, "OK") if quota available
            - (False, "Daily limit exceeded") if blocked
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get quota config
        cursor.execute("""
            SELECT daily_limit, monthly_limit, enabled
            FROM quota_config
            WHERE api_name = ?
        """, (api_name,))

        result = cursor.fetchone()
        if not result:
            conn.close()
            return True, "No quota configured (unlimited)"

        daily_limit, monthly_limit, enabled = result

        if not enabled:
            conn.close()
            return False, "API disabled in quota config"

        # Get today's usage
        today = datetime.now().date()
        cursor.execute("""
            SELECT COUNT(*) FROM api_usage
            WHERE api_name = ? AND DATE(timestamp) = ?
        """, (api_name, today))

        daily_count = cursor.fetchone()[0]

        if daily_count >= daily_limit:
            conn.close()
            return False, f"Daily limit exceeded ({daily_count}/{daily_limit})"

        # Get this month's usage
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        cursor.execute("""
            SELECT COUNT(*) FROM api_usage
            WHERE api_name = ? AND timestamp >= ?
        """, (api_name, month_start))

        monthly_count = cursor.fetchone()[0]

        if monthly_count >= monthly_limit:
            conn.close()
            return False, f"Monthly limit exceeded ({monthly_count}/{monthly_limit})"

        conn.close()

        # Check if approaching limit (warning)
        cursor.execute("""
            SELECT warning_threshold FROM quota_config WHERE api_name = ?
        """, (api_name,))
        warning_threshold = cursor.fetchone()[0] if cursor.fetchone() else 0.8

        if daily_count >= daily_limit * warning_threshold:
            return True, f"WARNING: {daily_count}/{daily_limit} daily quota used"

        return True, "OK"

    def record_usage(
        self,
        api_name: str,
        cost: float,
        tokens_input: int = 0,
        tokens_output: int = 0,
        model: str = None,
        success: bool = True
    ):
        """Record API usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO api_usage
            (api_name, cost, tokens_input, tokens_output, model, success)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (api_name, cost, tokens_input, tokens_output, model, success))

        # Update daily stats cache
        today = datetime.now().date()
        cursor.execute("""
            INSERT INTO daily_stats (date, api_name, query_count, total_cost)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(date, api_name) DO UPDATE SET
                query_count = query_count + 1,
                total_cost = total_cost + ?
        """, (today, api_name, cost, cost))

        conn.commit()
        conn.close()

        logger.info(f"[QUOTA] {api_name}: ${cost:.4f} | Today: {self.get_daily_usage(api_name)[0]} queries")

    def get_daily_usage(self, api_name: str) -> Tuple[int, float]:
        """Get today's usage for an API"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().date()
        cursor.execute("""
            SELECT query_count, total_cost
            FROM daily_stats
            WHERE date = ? AND api_name = ?
        """, (today, api_name))

        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0], result[1]
        return 0, 0.0

    def get_monthly_usage(self, api_name: str) -> Tuple[int, float]:
        """Get this month's usage for an API"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        month_start = datetime.now().replace(day=1).date()
        cursor.execute("""
            SELECT SUM(query_count), SUM(total_cost)
            FROM daily_stats
            WHERE date >= ? AND api_name = ?
        """, (month_start, api_name))

        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return result[0], result[1]
        return 0, 0.0

    def get_all_usage_stats(self) -> Dict:
        """Get usage stats for all APIs"""
        stats = {}

        for api_name in self.DEFAULT_QUOTAS.keys():
            daily_count, daily_cost = self.get_daily_usage(api_name)
            monthly_count, monthly_cost = self.get_monthly_usage(api_name)

            config = self.DEFAULT_QUOTAS[api_name]

            stats[api_name] = {
                "daily": {
                    "count": daily_count,
                    "cost": daily_cost,
                    "limit": config["daily_limit"],
                    "remaining": config["daily_limit"] - daily_count,
                    "percent_used": (daily_count / config["daily_limit"] * 100) if config["daily_limit"] > 0 else 0
                },
                "monthly": {
                    "count": monthly_count,
                    "cost": monthly_cost,
                    "limit": config["monthly_limit"],
                    "remaining": config["monthly_limit"] - monthly_count,
                    "percent_used": (monthly_count / config["monthly_limit"] * 100) if config["monthly_limit"] > 0 else 0
                }
            }

        return stats

    def update_quota(self, api_name: str, daily_limit: int = None, monthly_limit: int = None):
        """Update quota limits for an API"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        values = []

        if daily_limit is not None:
            updates.append("daily_limit = ?")
            values.append(daily_limit)

        if monthly_limit is not None:
            updates.append("monthly_limit = ?")
            values.append(monthly_limit)

        if updates:
            values.append(api_name)
            cursor.execute(f"""
                UPDATE quota_config
                SET {', '.join(updates)}
                WHERE api_name = ?
            """, values)
            conn.commit()

        conn.close()

    def enable_api(self, api_name: str):
        """Enable API quota tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE quota_config SET enabled = 1 WHERE api_name = ?", (api_name,))
        conn.commit()
        conn.close()

    def disable_api(self, api_name: str):
        """Disable API (block all usage)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE quota_config SET enabled = 0 WHERE api_name = ?", (api_name,))
        conn.commit()
        conn.close()

    def get_usage_report(self) -> str:
        """Generate formatted usage report"""
        stats = self.get_all_usage_stats()

        report = []
        report.append("=" * 70)
        report.append("KARMA SADE - API QUOTA USAGE REPORT")
        report.append("=" * 70)
        report.append("")

        total_daily_cost = 0
        total_monthly_cost = 0

        for api_name, data in stats.items():
            daily = data["daily"]
            monthly = data["monthly"]

            total_daily_cost += daily["cost"]
            total_monthly_cost += monthly["cost"]

            report.append(f"{api_name.upper()}")
            report.append("-" * 70)
            report.append(f"  Today:  {daily['count']:3d}/{daily['limit']:3d} queries ({daily['percent_used']:5.1f}%) | ${daily['cost']:.4f}")
            report.append(f"  Month:  {monthly['count']:4d}/{monthly['limit']:4d} queries ({monthly['percent_used']:5.1f}%) | ${monthly['cost']:.2f}")
            report.append("")

        report.append("=" * 70)
        report.append(f"TOTAL COST - Today: ${total_daily_cost:.4f} | Month: ${total_monthly_cost:.2f}")
        report.append("=" * 70)

        return "\n".join(report)


# Global instance
quota_manager = QuotaManager()


if __name__ == "__main__":
    # Test the quota manager
    logging.basicConfig(level=logging.INFO)

    print("\n" + quota_manager.get_usage_report())

    # Test quota check
    for api in ["claude", "openai", "zai_paid", "perplexity"]:
        can_use, reason = quota_manager.check_quota(api)
        print(f"\n{api}: {can_use} - {reason}")
