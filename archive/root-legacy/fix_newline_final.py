#!/usr/bin/env python3

with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'rb') as f:
    content = f.read()

# Replace broken pattern using bytes
broken_bytes = b'f.write(json.dumps(reflection_entry) + "\n'
fixed_bytes = b'f.write(json.dumps(reflection_entry) + "\\\\n'

content = content.replace(broken_bytes, fixed_bytes)

with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'wb') as f:
    f.write(content)

print('[OK] Fixed newline escaping')
