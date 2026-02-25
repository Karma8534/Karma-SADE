# karma-core/decision_logger.py
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

class DecisionLogger:
    """Persist consciousness loop decisions to decision_log.jsonl ledger."""

    def __init__(self, ledger_path: str = "/opt/seed-vault/memory_v1/ledger/decision_log.jsonl"):
        self.ledger_path = ledger_path

    async def log_decision(self,
                          decision: str,
                          observation: str,
                          reasoning: str,
                          action: str,
                          source: str = "consciousness_loop") -> Dict[str, Any]:
        """
        Append decision entry to decision_log.jsonl.

        Args:
            decision: The decision made
            observation: What was observed
            reasoning: The reasoning behind the decision
            action: What action to take
            source: Source identifier (default: consciousness_loop)

        Returns:
            {"ok": True, "timestamp": "...", "entry_hash": "..."} or error dict
        """
        try:
            entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "type": "CONSCIOUSNESS_DECISION",
                "decision": decision,
                "observation": observation,
                "reasoning": reasoning,
                "action": action,
                "source": source
            }

            # Append to JSONL (atomic write)
            with open(self.ledger_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

            return {
                "ok": True,
                "timestamp": entry["timestamp"],
                "entry_hash": hash(json.dumps(entry, sort_keys=True)) & 0x7FFFFFFF
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

    async def read_recent_decisions(self, limit: int = 10) -> Dict[str, Any]:
        """Read most recent decisions from ledger."""
        try:
            with open(self.ledger_path, "r") as f:
                lines = f.readlines()

            # Get last N entries
            recent_lines = lines[-limit:] if limit > 0 else lines
            decisions = [json.loads(line) for line in recent_lines if line.strip()]

            return {
                "ok": True,
                "count": len(decisions),
                "decisions": decisions
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "count": 0,
                "decisions": []
            }
