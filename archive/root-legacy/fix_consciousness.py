#!/usr/bin/env python3
"""Fix consciousness.py schema mismatch bugs"""

with open('/app/consciousness.py', 'r') as f:
    content = f.read()

# Fix line 507: observations["new_episodes"] > 0 (list comparison bug)
content = content.replace(
    'if analysis is None and observations["new_episodes"] > 0:',
    'if analysis is None and observations.get("episode_count", 0) > 0:'
)

# Fix line 519: observations["new_entities"] > 10 (non-existent key)
content = content.replace(
    'if observations["new_entities"] > 10:',
    'if observations.get("episode_count", 0) > 10:'
)

# Fix line 520 f-string
content = content.replace(
    "f\"Rapid growth: {observations['new_entities']} new entities",
    "f\"Rapid growth: {observations.get('episode_count', 0)} new episodes"
)

# Fix line 530: observations["new_entities"] > 0 (non-existent key)
content = content.replace(
    'if observations["new_entities"] > 0:',
    'if observations.get("episode_count", 0) > 0:'
)

# Fix line 531 f-string (remove reference to new_relationships)
content = content.replace(
    "f\"{observations['new_entities']} new entities, {observations['new_relationships']} new relationships\"",
    "f\"{observations.get('episode_count', 0)} new episodes\""
)

with open('/app/consciousness.py', 'w') as f:
    f.write(content)

print("✓ Fixed consciousness.py schema issues")
