"""Add openssh-client to karma-server Dockerfile."""
path = '/opt/seed-vault/memory_v1/karma-core/Dockerfile'
with open(path, 'r') as f:
    content = f.read()

old = """RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    && rm -rf /var/lib/apt/lists/*"""

new = """RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl openssh-client \\
    && rm -rf /var/lib/apt/lists/*"""

content = content.replace(old, new)
with open(path, 'w') as f:
    f.write(content)
print('OK - Dockerfile patched')
