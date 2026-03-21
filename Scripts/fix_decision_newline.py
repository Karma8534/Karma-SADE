"""Fix the unterminated string literal in server.py's Decision query section.
The patch previously wrote a real newline (0x0a) inside a string literal.
This script replaces it with the escaped sequence \\n (0x5c 0x6e)."""

with open("/opt/seed-vault/memory_v1/karma-core/server.py", "rb") as f:
    content = f.read()

# The bad byte sequence: parts.append("<REAL_LF>## Key Architectural Decisions")
# 0x22 0x0a 0x23 0x23 = '"', LF, '#', '#'
bad = b'parts.append("\n## Key Architectural Decisions")'

# The correct sequence: parts.append("\\n## Key Architectural Decisions")
# 0x22 0x5c 0x6e 0x23 0x23 = '"', backslash, 'n', '#', '#'
backslash = bytes([0x5c])  # literal backslash byte
n_char = bytes([0x6e])     # literal 'n' byte
nl_escape = backslash + n_char  # \n as two bytes
good = b'parts.append("' + nl_escape + b'## Key Architectural Decisions")'

print("bad in content:", bad in content)
print("bad repr:", repr(bad[:30]))
print("good repr:", repr(good[:30]))

if bad in content:
    new_content = content.replace(bad, good, 1)
    with open("/opt/seed-vault/memory_v1/karma-core/server.py", "wb") as f:
        f.write(new_content)
    print("REPLACED OK")
    # Verify
    if good in new_content and bad not in new_content:
        print("VERIFIED: good in file, bad not in file")
    else:
        print("WARNING: verification failed")
else:
    print("ERROR: bad pattern not found")
    # Find what's there
    idx = content.find(b"Key Architectural")
    if idx >= 0:
        chunk = content[idx-30:idx+50]
        print("context bytes:", repr(chunk))
