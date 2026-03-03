"""Patch hub-bridge server.js to add host param to bash tool definition + update system prompt."""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '/opt/seed-vault/memory_v1/hub_bridge/app/server.js'
with open(path, 'r') as f:
    content = f.read()

# 1. Update bash tool definition
old_tool = """  {
    name: "bash",
    description: "Execute a shell command on the droplet. Timeout: 30s. Max output: 10KB.",
    input_schema: {
      type: "object",
      properties: {
        command: { type: "string", description: "Shell command to execute" },
      },
      required: ["command"],
    },
  },"""

new_tool = """  {
    name: "bash",
    description: "Execute a shell command. Default: droplet. Set host=P1 to run on Colby's workstation (PAYBACK). POLICY: Only use host=P1 when Colby explicitly asks. Timeout: 30s droplet, 60s P1.",
    input_schema: {
      type: "object",
      properties: {
        command: { type: "string", description: "Shell command to execute" },
        host: { type: "string", enum: ["droplet", "P1"], description: "Target machine. droplet (default) or P1 (Colby's workstation). Only use P1 when explicitly asked." },
      },
      required: ["command"],
    },
  },"""

if old_tool not in content:
    print('ERROR: old bash tool def not found in server.js')
    sys.exit(1)
content = content.replace(old_tool, new_tool)
print('Step 1: hub-bridge bash tool definition updated')

# 2. Update tools line in system prompt to mention P1
old_tools_line = "Tools: read_file(path) | write_file(path,content) | edit_file(path,old_text,new_text) | bash(command)"
new_tools_line = "Tools: read_file(path) | write_file(path,content) | edit_file(path,old_text,new_text) | bash(command, host=droplet|P1)"

if old_tools_line not in content:
    print('WARNING: old tools line not found, skipping prompt update')
else:
    content = content.replace(old_tools_line, new_tools_line)
    print('Step 2: system prompt tools line updated')

with open(path, 'w') as f:
    f.write(content)
print('OK - server.js patched successfully')
