#!/usr/bin/env python3
"""
Test consciousness._act() integration with DecisionLogger.
Simulates what the consciousness loop does when it logs decisions.
"""
import asyncio
import json
import sys
sys.path.insert(0, '/opt/seed-vault/memory_v1/karma-core')

from decision_logger import DecisionLogger

async def simulate_consciousness_act():
    """Simulate the _act() method's decision logging."""
    print("Simulating consciousness._act() decision logging...")

    # Simulate _act() parameters
    cycle_num = 42
    action = "LOG_INSIGHT"
    reason = "Detected pattern in graph queries suggesting user learning curve"
    observations = {
        "new_episodes": 5,
        "new_entities": 12,
        "new_relationships": 23,
        "active_sessions": 2
    }
    analysis = {
        "patterns": ["query_frequency_increase", "entity_diversity_expansion"],
        "insights": ["user_becoming_more_ambitious", "conversation_depth_growing"]
    }

    # Simulate what consciousness._act() does
    decision_logger = DecisionLogger()
    decision_str = action
    observation_str = f"Episodes: {observations.get('new_episodes', 0)}, Entities: {observations.get('new_entities', 0)}, Relationships: {observations.get('new_relationships', 0)}"
    reasoning_str = reason
    action_str = f"Cycle #{cycle_num}: {action}"

    # Log the decision (this is what consciousness._act() now does)
    result = await decision_logger.log_decision(
        decision=decision_str,
        observation=observation_str,
        reasoning=reasoning_str,
        action=action_str,
        source="consciousness_loop"
    )

    if result.get('ok'):
        print(f"✓ Decision logged successfully")
        print(f"  Timestamp: {result.get('timestamp')}")
        print(f"  Hash: {result.get('entry_hash')}")

        # Verify it was written
        recent = await decision_logger.read_recent_decisions(limit=1)
        if recent.get('ok') and recent.get('count') > 0:
            latest = recent.get('decisions', [])[-1]
            print(f"\n✓ Verified in ledger:")
            print(f"  Decision: {latest.get('decision')}")
            print(f"  Reasoning: {latest.get('reasoning')}")
            print(f"  Action: {latest.get('action')}")
            return True
        else:
            print("✗ Failed to verify decision in ledger")
            return False
    else:
        print(f"✗ Failed to log decision: {result.get('error')}")
        return False

result = asyncio.run(simulate_consciousness_act())
exit(0 if result else 1)
