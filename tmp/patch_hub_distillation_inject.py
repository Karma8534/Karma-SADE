#!/usr/bin/env python3
"""
Patch hub-bridge server.js to inject distillation_brief into buildSystemText().

Adds a new if-block immediately after the karma_brief injection block:
  if (ckLatest && ckLatest.distillation_brief) {
    text += `\n\n--- KARMA GRAPH SYNTHESIS ---\n${ckLatest.distillation_brief}\n---`;
  }
"""

path = '/opt/seed-vault/memory_v1/hub_bridge/app/server.js'

with open(path, 'r') as f:
    src = f.read()

# Exact closing line of the karma_brief if-block (with the exact indentation from server.js)
old = '    text += `\\n\\n--- KARMA SELF-KNOWLEDGE (${ckId}) ---\\n${ckLatest.karma_brief}\\n---`;\n  }'

new = (
    '    text += `\\n\\n--- KARMA SELF-KNOWLEDGE (${ckId}) ---\\n${ckLatest.karma_brief}\\n---`;\n'
    '  }\n'
    '\n'
    '  if (ckLatest && ckLatest.distillation_brief) {\n'
    '    text += `\\n\\n--- KARMA GRAPH SYNTHESIS ---\\n${ckLatest.distillation_brief}\\n---`;\n'
    '  }'
)

if 'KARMA GRAPH SYNTHESIS' in src:
    print('ALREADY PRESENT — no patch needed')
elif old in src:
    patched = src.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(patched)
    print('PATCHED OK')
    # Verify
    with open(path, 'r') as f:
        verify = f.read()
    if 'KARMA GRAPH SYNTHESIS' in verify:
        print('VERIFICATION OK — KARMA GRAPH SYNTHESIS block found in file')
    else:
        print('VERIFICATION FAILED — block not found after write')
else:
    print('NOT FOUND — old anchor string not present, check exact string')
    # Debug: show actual lines around KARMA SELF-KNOWLEDGE
    idx = src.find('KARMA SELF-KNOWLEDGE')
    if idx >= 0:
        print('Context around KARMA SELF-KNOWLEDGE:')
        print(repr(src[max(0, idx - 150):idx + 400]))
    else:
        print('KARMA SELF-KNOWLEDGE string not found at all in file')
