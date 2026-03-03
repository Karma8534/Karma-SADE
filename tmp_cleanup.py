path = "/opt/seed-vault/memory_v1/hub_bridge/app/server.js"
content = open(path).read()

# Remove all debug logging lines
import re

# Remove CHAT-MP debug lines
content = re.sub(r'\n\s*console\.log\(`\[CHAT-MP\].*?\n', '\n', content)
# Remove boundary counting debug
content = re.sub(r'\n\s*const sep = Buffer\.from.*?boundary occurrences.*?\n', '\n', content, flags=re.DOTALL)
# Remove preview debug
content = re.sub(r'\n\s*const preview = rawBuf.*?\n', '\n', content)
content = re.sub(r'\n\s*console\.log\(`\[CHAT-MP\] preview.*?\n', '\n', content)
# Remove INGEST-DEBUG lines
content = re.sub(r'\n\s*console\.log\(`\[INGEST-DEBUG\].*?\n', '\n', content)
content = re.sub(r'\n\s*console\.error\(`\[INGEST-DEBUG\].*?\n', '\n', content)

# Simplify: keep just the useful [CHAT] log line
# Remove count/sep/preview debug block entirely
lines = content.split('\n')
cleaned = []
skip_next = False
for i, line in enumerate(lines):
    if 'CHAT-MP' in line or 'INGEST-DEBUG' in line:
        continue
    if 'const sep = Buffer.from' in line and 'boundary' in line:
        continue
    if 'let count = 0, idx = 0;' in line:
        continue
    if 'while ((idx = rawBuf.indexOf(sep, idx))' in line:
        continue
    if 'boundary occurrences' in line:
        continue
    if 'const preview = rawBuf.subarray' in line:
        continue
    cleaned.append(line)

content = '\n'.join(cleaned)

open(path, "w").write(content)
print("OK - debug logging removed")
