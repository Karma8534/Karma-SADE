#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/opt/seed-vault/memory_v1/karma-core')

from decision_logger import DecisionLogger

async def verify_integration():
    logger = DecisionLogger()
    recent = await logger.read_recent_decisions(limit=5)

    if recent.get('ok'):
        print(f"Decision logger read {recent.get('count')} recent decisions")
        for decision in recent.get('decisions', [])[-2:]:
            ts = decision.get('timestamp')
            dec = decision.get('decision')
            print(f"  [{ts}] {dec}")
        return True
    else:
        print(f"Failed to read decisions: {recent.get('error')}")
        return False

result = asyncio.run(verify_integration())
exit(0 if result else 1)
