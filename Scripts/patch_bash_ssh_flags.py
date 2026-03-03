"""Fix karma-server bash handler to use explicit SSH flags instead of config file."""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '/opt/seed-vault/memory_v1/karma-core/server.py'
with open(path, 'r') as f:
    content = f.read()

old_line = 'ssh_command = f"ssh -o ConnectTimeout=10 payback '
new_line = 'ssh_command = f"ssh -i /root/.ssh/karma-p1-access -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 raest@100.124.194.102 '

if old_line not in content:
    print('ERROR: old SSH command not found')
    sys.exit(1)

content = content.replace(old_line, new_line)

with open(path, 'w') as f:
    f.write(content)
print('OK - bash handler updated with explicit SSH flags')
