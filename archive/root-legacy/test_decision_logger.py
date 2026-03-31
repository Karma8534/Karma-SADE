#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/opt/seed-vault/memory_v1/karma-core')

from decision_logger import DecisionLogger

async def test_decision_logger():
    logger = DecisionLogger()

    # Test 1: Log a decision
    result = await logger.log_decision(
        decision="Test decision from Task 4",
        observation="Graph has 1268 entities",
        reasoning="Testing decision persistence",
        action="Verify appears in ledger"
    )
    print(f"Log result: {result}")
    assert result.get('ok'), f"Failed to log: {result}"

    # Test 2: Read recent decisions
    recent = await logger.read_recent_decisions(limit=3)
    print(f"Recent decisions count: {recent.get('count')}")
    assert recent.get('ok'), f"Failed to read: {recent}"
    assert recent.get('count') > 0, "No decisions found"

    print('✓ All DecisionLogger tests passed')

asyncio.run(test_decision_logger())
