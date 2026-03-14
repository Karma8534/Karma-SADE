"""
karma_bus_ingester.py — Converts /v1/coordination seed_issue messages
into normalized kiki_issues.jsonl entries.
Single ingestion path: no direct writes from Karma-Core to issue file.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


class BusIngester:
    def __init__(
        self,
        issues_file: str = "/mnt/c/dev/Karma/k2/cache/kiki_issues.jsonl",
        coordination_url: str = "https://hub.arknexus.net/v1/coordination",
    ):
        self.issues_file = Path(issues_file)
        self.coordination_url = coordination_url

    def filter_pending(self, messages: list[dict]) -> list[dict]:
        return [
            m for m in messages
            if m.get("type") == "seed_issue" and m.get("status") == "PENDING"
        ]

    def convert(self, msg: dict) -> dict:
        payload = msg.get("payload", {})
        return {
            "issue": payload.get("title", "Untitled intent"),
            "details": payload.get("body", ""),
            "source": "karma_core",
            "coordination_id": msg.get("id"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def ingest(self, messages: list[dict]) -> int:
        pending = self.filter_pending(messages)
        if not pending:
            return 0
        issues = [self.convert(m) for m in pending]
        self.issues_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.issues_file, "a") as f:
            for issue in issues:
                f.write(json.dumps(issue) + "\n")
        return len(issues)

    def fetch_and_ingest(self, token: str) -> int:
        req = urllib.request.Request(
            self.coordination_url,
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            messages = json.loads(resp.read())
        return self.ingest(messages)
