"""
Decision Logger — Persistence Layer for Consciousness Loop Decisions
Writes OBSERVE/THINK/DECIDE/ACT/REFLECT cycle outcomes to decision_log.jsonl
"""
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

class DecisionLogger:
    """Logs consciousness loop decisions to decision_log.jsonl"""
    
    def __init__(self, ledger_path: str = None):
        """Initialize decision logger.
        
        Args:
            ledger_path: Path to decision_log.jsonl. Defaults to environment or standard vault path.
        """
        if ledger_path is None:
            # Default: vault-neo standard path
            ledger_path = os.environ.get(
                'DECISION_LOG_PATH',
                '/opt/seed-vault/memory_v1/ledger/decision_log.jsonl'
            )
        self.ledger_path = Path(ledger_path)
        
        # Ensure parent directory exists
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def log_decision(
        self,
        decision: str,
        observation: str,
        reasoning: str,
        action: str,
        source: str = "consciousness_loop",
        **kwargs
    ) -> dict:
        """Log a consciousness cycle decision.
        
        Args:
            decision: The decision made (e.g., "LOG_INSIGHT")
            observation: Observable facts (e.g., "Episodes: 5, Entities: 12")
            reasoning: Why this decision was made
            action: What action will be taken
            source: Where this came from (default: "consciousness_loop")
            **kwargs: Additional fields to include in the log entry
        
        Returns:
            dict with entry that was written
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "CONSCIOUSNESS_DECISION",
            "decision": decision,
            "observation": observation,
            "reasoning": reasoning,
            "action": action,
            "source": source,
        }
        # Add any extra fields
        entry.update(kwargs)
        
        # Write to ledger (append mode, non-blocking)
        try:
            async def write_async():
                # Run the write in a thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._write_entry, entry)
            
            await write_async()
            return {"ok": True, "entry": entry}
        except Exception as e:
            print(f"[DECISION_LOGGER] Error writing decision log: {e}")
            return {"ok": False, "error": str(e)}
    
    def _write_entry(self, entry: dict):
        """Synchronous write operation (runs in executor)."""
        try:
            with open(self.ledger_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
                f.flush()
        except Exception as e:
            raise Exception(f"Failed to write decision log: {e}")
    
    async def read_recent(self, limit: int = 20) -> list[dict]:
        """Read the most recent N decision entries.
        
        Args:
            limit: How many recent entries to return
        
        Returns:
            List of decision entries (most recent first)
        """
        try:
            if not self.ledger_path.exists():
                return []
            
            entries = []
            with open(self.ledger_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
            
            # Return most recent N
            return entries[-limit:] if limit > 0 else entries
        except Exception as e:
            print(f"[DECISION_LOGGER] Error reading decision log: {e}")
            return []


async def verify_logger():
    """Quick test of the decision logger."""
    logger = DecisionLogger()
    result = await logger.log_decision(
        decision="TEST_DECISION",
        observation="Test observation",
        reasoning="Testing the logger",
        action="Verify it works"
    )
    print(f"Logger test result: {result}")
    recent = await logger.read_recent(1)
    print(f"Most recent entry: {recent}")


if __name__ == "__main__":
    asyncio.run(verify_logger())
