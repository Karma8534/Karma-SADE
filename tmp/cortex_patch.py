#!/usr/bin/env python3
"""Patch julian_cortex.py: sort canonical/state blocks to end of knowledge text."""
import sys

path = "/mnt/c/dev/Karma/k2/aria/julian_cortex.py"
with open(path, "r") as f:
    lines = f.readlines()

# Find the target: "knowledge_text = ..." join line
# Replace 3 lines starting at "knowledge_text = ..." with sorted version
patched = False
i = 0
out = []
while i < len(lines):
    line = lines[i]
    # Match: '        knowledge_text = "\n\n---\n\n".join('
    if 'knowledge_text = "\\n\\n---\\n\\n".join(' in line and not patched:
        # Check next line is the generator
        if i + 1 < len(lines) and '_knowledge_blocks' in lines[i + 1] and 'for label, text' in lines[i + 1]:
            # Insert sorting before the join
            indent = "        "
            out.append(f'{indent}# Sort: canonical/state blocks go LAST (closest to query = highest attention)\n')
            out.append(f'{indent}_PRIORITY_PREFIXES = ("canonical-", "state-", "active-")\n')
            out.append(f'{indent}sorted_blocks = sorted(\n')
            out.append(f'{indent}    _knowledge_blocks,\n')
            out.append(f'{indent}    key=lambda b: any(b[0].startswith(p) for p in _PRIORITY_PREFIXES)\n')
            out.append(f'{indent})\n')
            # Replace the join to use sorted_blocks
            out.append(line.replace('_knowledge_blocks', 'sorted_blocks'))  # keep original join line but swap var
            # Next line: f"[{label}]..." — replace _knowledge_blocks ref
            if i + 1 < len(lines):
                out.append(lines[i + 1].replace('_knowledge_blocks', 'sorted_blocks'))
                i += 2
                patched = True
                continue
    out.append(line)
    i += 1

if patched:
    with open(path, "w") as f:
        f.writelines(out)
    print("PATCH applied: knowledge block sorting with canonical-* priority")
    sys.exit(0)
else:
    print("PATCH FAILED: could not find target lines")
    sys.exit(1)
