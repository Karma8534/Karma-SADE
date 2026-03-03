"""Add SSH mounts to karma-server in compose.yml."""
path = '/opt/seed-vault/memory_v1/compose/compose.yml'
with open(path, 'r') as f:
    content = f.read()

# Add SSH volume mounts after the existing openai.api_key.txt mount
old_mount = "    - /opt/seed-vault/memory_v1/session/openai.api_key.txt:/opt/seed-vault/memory_v1/session/openai.api_key.txt:ro"

new_mount = """    - /opt/seed-vault/memory_v1/session/openai.api_key.txt:/opt/seed-vault/memory_v1/session/openai.api_key.txt:ro
    - /opt/seed-vault/memory_v1/karma-ssh/karma-p1-access:/root/.ssh/karma-p1-access:ro
    - /opt/seed-vault/memory_v1/karma-ssh/config:/root/.ssh/config:ro
    - /opt/seed-vault/memory_v1/karma-ssh/known_hosts:/root/.ssh/known_hosts:rw"""

if old_mount not in content:
    print('ERROR: mount point not found')
    import sys; sys.exit(1)
content = content.replace(old_mount, new_mount)

with open(path, 'w') as f:
    f.write(content)
print('OK - compose.yml patched with SSH mounts')
