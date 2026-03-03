"""Bump MAX_TOOL_ITERATIONS from 5 to 15 in both tool-use paths."""
path = '/opt/seed-vault/memory_v1/hub_bridge/app/server.js'
with open(path, 'r') as f:
    content = f.read()

# Anthropic path
content = content.replace(
    'const MAX_TOOL_ITERATIONS = 5;',
    'const MAX_TOOL_ITERATIONS = 15;'
)

# GPT/OpenAI path
content = content.replace(
    'const MAX_ITERATIONS = 5;',
    'const MAX_ITERATIONS = 15;'
)

with open(path, 'w') as f:
    f.write(content)
print('OK - tool iterations bumped to 15')
