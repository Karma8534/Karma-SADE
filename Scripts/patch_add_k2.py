"""Add K2 host routing to karma-server server.py and hub-bridge server.js."""
import sys

# --- Patch karma-server ---
ks_path = '/opt/seed-vault/memory_v1/karma-core/server.py'
with open(ks_path, 'r') as f:
    content = f.read()

# Add K2 to enum in tool definition
content = content.replace(
    '"enum": ["droplet", "P1"]',
    '"enum": ["droplet", "P1", "K2"]'
)

# Add K2 elif block after P1 block
old_else = """            else:
                # Default: run locally on droplet"""

new_else = """            elif host == "K2":
                # Route to K2 via SSH over Tailscale (WSL, port 2222)
                safe_cmd = command.replace("'", "'\\\\''")
                ssh_command = f"ssh -i /root/.ssh/karma-p1-access -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -p 2222 karma@100.75.109.92 '{safe_cmd}'"
                proc = await _asyncio.create_subprocess_shell(
                    ssh_command,
                    stdout=_asyncio.subprocess.PIPE,
                    stderr=_asyncio.subprocess.PIPE,
                )
                stdout, stderr = await _asyncio.wait_for(proc.communicate(), timeout=60)
            else:
                # Default: run locally on droplet"""

if old_else not in content:
    print('ERROR: karma-server else block not found')
    sys.exit(1)
content = content.replace(old_else, new_else)

with open(ks_path, 'w') as f:
    f.write(content)
print('OK - karma-server patched with K2 routing')

# --- Patch hub-bridge ---
hb_path = '/opt/seed-vault/memory_v1/hub_bridge/app/server.js'
with open(hb_path, 'r') as f:
    content = f.read()

# Add K2 to enum in tool definition
content = content.replace(
    'enum: ["droplet", "P1"]',
    'enum: ["droplet", "P1", "K2"]'
)

# Update description to mention K2
content = content.replace(
    "Only use P1 when explicitly asked.",
    "Only use P1 or K2 when explicitly asked."
)

# Update tools line in system prompt
content = content.replace(
    "bash(command, host=droplet|P1)",
    "bash(command, host=droplet|P1|K2)"
)

with open(hb_path, 'w') as f:
    f.write(content)
print('OK - hub-bridge patched with K2')
