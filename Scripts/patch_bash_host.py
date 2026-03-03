"""Patch karma-server server.py to add host=P1 routing to bash tool."""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '/opt/seed-vault/memory_v1/karma-core/server.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Update bash tool definition to include host param
old_def = '{"name": "bash", "description": "Run a shell command on the droplet. Returns stdout, stderr, exit code.",\n     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}'

new_def = '{"name": "bash", "description": "Run a shell command. Default: runs on droplet. Set host=P1 to run on Colbys workstation (PAYBACK). POLICY: Only use host=P1 when Colby explicitly asks.",\n     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}, "host": {"type": "string", "enum": ["droplet", "P1"], "default": "droplet", "description": "Target machine. droplet (default) or P1 (Colbys workstation, requires explicit request)."}}, "required": ["command"]}}'

if old_def not in content:
    print('ERROR: old bash tool def not found')
    sys.exit(1)
content = content.replace(old_def, new_def)
print('Step 1: bash tool definition updated')

# 2. Update bash handler to route via SSH when host=P1
old_handler = '''        elif tool_name == "bash":
            command = tool_input["command"]
            proc = await _asyncio.create_subprocess_shell(
                command,
                stdout=_asyncio.subprocess.PIPE,
                stderr=_asyncio.subprocess.PIPE,
                cwd="/opt/seed-vault/memory_v1"
            )
            stdout, stderr = await _asyncio.wait_for(proc.communicate(), timeout=30)
            return {
                "ok": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace")[:50_000],
                "stderr": stderr.decode("utf-8", errors="replace")[:10_000],
                "exit_code": proc.returncode
            }'''

new_handler = '''        elif tool_name == "bash":
            command = tool_input["command"]
            host = tool_input.get("host", "droplet")

            if host == "P1":
                # Route to P1 (PAYBACK) via SSH over Tailscale
                # Escape single quotes in command for SSH
                safe_cmd = command.replace("'", "'\\\\''")
                ssh_command = f"ssh -o ConnectTimeout=10 payback '{safe_cmd}'"
                proc = await _asyncio.create_subprocess_shell(
                    ssh_command,
                    stdout=_asyncio.subprocess.PIPE,
                    stderr=_asyncio.subprocess.PIPE,
                )
                stdout, stderr = await _asyncio.wait_for(proc.communicate(), timeout=60)
            else:
                # Default: run locally on droplet
                proc = await _asyncio.create_subprocess_shell(
                    command,
                    stdout=_asyncio.subprocess.PIPE,
                    stderr=_asyncio.subprocess.PIPE,
                    cwd="/opt/seed-vault/memory_v1"
                )
                stdout, stderr = await _asyncio.wait_for(proc.communicate(), timeout=30)

            return {
                "ok": proc.returncode == 0,
                "host": host,
                "stdout": stdout.decode("utf-8", errors="replace")[:50_000],
                "stderr": stderr.decode("utf-8", errors="replace")[:10_000],
                "exit_code": proc.returncode
            }'''

if old_handler not in content:
    print('ERROR: old bash handler not found')
    sys.exit(1)
content = content.replace(old_handler, new_handler)
print('Step 2: bash handler updated with host routing')

with open(path, 'w') as f:
    f.write(content)
print('OK - server.py patched successfully')
