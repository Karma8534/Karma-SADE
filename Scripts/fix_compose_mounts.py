"""Remove config and known_hosts mounts, keep only the key file."""
path = '/opt/seed-vault/memory_v1/compose/compose.yml'
with open(path, 'r') as f:
    content = f.read()

# Remove the config and known_hosts lines
content = content.replace(
    "\n    - /opt/seed-vault/memory_v1/karma-ssh/config:/root/.ssh/config:ro",
    ""
)
content = content.replace(
    "\n    - /opt/seed-vault/memory_v1/karma-ssh/known_hosts:/root/.ssh/known_hosts:rw",
    ""
)

with open(path, 'w') as f:
    f.write(content)
print('OK - removed config/known_hosts mounts')
