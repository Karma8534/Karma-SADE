#!/usr/bin/env python3
"""Fix _distillation_cycle to use sync router.complete() correctly."""

path = '/opt/seed-vault/memory_v1/karma-core/consciousness.py'
src = open(path).read()

# Fix: replace the async await call with a sync call that unpacks the tuple
old_router_call = """        try:
            response = await self._router.complete(
                messages=[
                    {"role": "system", "content": "You are Karma graph distillation engine. Output only valid JSON, no markdown."},
                    {"role": "user", "content": prompt}
                ],
                task_type="reasoning"
            )
            raw = response.get("content", "").strip()"""

new_router_call = """        try:
            raw, _model_used = self._router.complete(
                messages=[
                    {"role": "system", "content": "You are Karma graph distillation engine. Output only valid JSON, no markdown."},
                    {"role": "user", "content": prompt}
                ],
                task_type="reasoning"
            )
            raw = (raw or "").strip()"""

if old_router_call in src:
    src = src.replace(old_router_call, new_router_call, 1)
    print("Router call fixed: await removed, tuple unpacked")
else:
    print("ERROR: old_router_call not found in file")
    # Show what's around the router call for debugging
    idx = src.find('self._router.complete(')
    if idx >= 0:
        print("Found router call at char", idx, "context:")
        print(repr(src[max(0,idx-200):idx+300]))

open(path, 'w').write(src)
print("File written.")

# Verify syntax
import subprocess
result = subprocess.run(['python3', '-m', 'py_compile', path], capture_output=True, text=True)
if result.returncode == 0:
    print("SYNTAX OK")
else:
    print("SYNTAX ERROR:", result.stderr)
