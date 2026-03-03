"""Update Karma's awareness that K2=WSL/Linux and P1=Windows."""
import sys

# --- Patch hub-bridge server.js ---
path = '/opt/seed-vault/memory_v1/hub_bridge/app/server.js'
with open(path, 'r') as f:
    content = f.read()

# Update selfKnowledge to include OS info
old_infra = "P1=PAYBACK(colby_machine,runs_claude_code), K2=192.168.0.226(local_worker,future_sister)"
new_infra = "P1=PAYBACK(colby_machine,runs_claude_code,Windows), K2=192.168.0.226(local_worker,WSL_Ubuntu_Linux,user=karma)"

if old_infra not in content:
    print('WARNING: selfKnowledge infra string not found, skipping')
else:
    content = content.replace(old_infra, new_infra)
    print('Step 1: selfKnowledge updated with OS info')

# Update bash tool description to mention OS
old_desc = "Set host=P1 to run on Colby's workstation (PAYBACK). POLICY: Only use host=P1 when Colby explicitly asks."
new_desc = "Set host=P1 for Colby's workstation (PAYBACK, Windows) or host=K2 for local worker (WSL/Ubuntu Linux, user=karma). POLICY: Only use P1 or K2 when Colby explicitly asks. P1 uses Windows paths (C:\\\\), K2 uses Linux paths (/home/karma/)."

if old_desc not in content:
    print('WARNING: bash tool description not found, skipping')
else:
    content = content.replace(old_desc, new_desc)
    print('Step 2: bash tool description updated with OS info')

with open(path, 'w') as f:
    f.write(content)
print('OK - hub-bridge patched')
