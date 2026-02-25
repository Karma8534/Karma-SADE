#!/usr/bin/env python3
"""
Patch consciousness.py to add decision logging to _act method.
"""

import re

# Read the file
with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'r') as f:
    content = f.read()

# Find the _act method and locate the consciousness journal write section
# We want to insert decision logging right after the journal entry is written

# Pattern to find: the line where we write to the journal
pattern = r'(        try:\n            journal_path = config\.CONSCIOUSNESS_JOURNAL\n            with open\(journal_path, "a", encoding="utf-8"\) as f:\n                f\.write\(json\.dumps\(entry\) \+ "\\n"\)\n        except Exception as e:\n            print\(f"\[CONSCIOUSNESS\] Failed to write journal: \{e\}"\))'

decision_logging_code = '''        try:
            journal_path = config.CONSCIOUSNESS_JOURNAL
            with open(journal_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\\n")
        except Exception as e:
            print(f"[CONSCIOUSNESS] Failed to write journal: {e}")

        # ─── Log to decision_log.jsonl ──────────────────────────────────
        try:
            decision_logger = DecisionLogger()
            # Extract decision details from action and analysis
            decision_str = action
            observation_str = f"Episodes: {observations.get('new_episodes', 0)}, Entities: {observations.get('new_entities', 0)}, Relationships: {observations.get('new_relationships', 0)}"
            reasoning_str = reason
            action_str = f"Cycle #{cycle_num}: {action}"

            # Log synchronously (convert to sync call)
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, schedule as task
                loop.create_task(decision_logger.log_decision(
                    decision=decision_str,
                    observation=observation_str,
                    reasoning=reasoning_str,
                    action=action_str,
                    source="consciousness_loop"
                ))
        except Exception as e:
            print(f"[CONSCIOUSNESS] Failed to write decision log: {e}")'''

# Replace the pattern
content = re.sub(pattern, decision_logging_code, content)

# Write back
with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'w') as f:
    f.write(content)

print('Patched consciousness.py with decision logging')
