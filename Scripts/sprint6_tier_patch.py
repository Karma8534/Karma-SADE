#!/usr/bin/env python3
"""Sprint 6 Task 7-6: Patch julian_cortex.py with tier classification."""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "/mnt/c/dev/Karma/k2/aria/julian_cortex.py"

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

changes = 0

# 1. Add _classify_tiers function before Ollama Interface section
tier_fn = '''
def _classify_tiers():
    """Sprint 6 Task 7-6: Classify knowledge blocks into tiers based on heuristics."""
    now = time.time()
    tier_counts = {"raw": 0, "distilled": 0, "stable": 0, "archived": 0}
    for block in _knowledge_blocks:
        nb = _normalize_block(block)
        label, text, category, ingested_at = nb
        tier = "raw"
        if category in ("canonical", "state", "active"):
            tier = "stable"
        elif category in ("decision", "project_invariant", "contradiction"):
            tier = "distilled"
        elif category == "session_checkpoint":
            tier = "distilled"
        elif ingested_at and (now - ingested_at) > 7 * 86400 and category == "general":
            tier = "archived"
        if len(block) < 5:
            block.append(tier)
        else:
            block[4] = tier
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    return tier_counts

'''

marker = "# \u2500\u2500 Ollama Interface"
if marker in code and "_classify_tiers" not in code:
    code = code.replace(marker, tier_fn + marker)
    changes += 1
    print("1. Added _classify_tiers function")
elif "_classify_tiers" in code:
    print("1. SKIP: _classify_tiers already exists")
else:
    print("1. ERROR: marker not found")

# 2. Call _classify_tiers in _auto_save_loop
old_save = "def _auto_save_loop():\n    while True:\n        time.sleep(SAVE_INTERVAL)\n        with _lock:\n            save_state()"
new_save = "def _auto_save_loop():\n    while True:\n        time.sleep(SAVE_INTERVAL)\n        with _lock:\n            _classify_tiers()\n            save_state()"

if old_save in code:
    code = code.replace(old_save, new_save)
    changes += 1
    print("2. Added _classify_tiers to save loop")
elif "_classify_tiers()" in code and "_auto_save_loop" in code:
    print("2. SKIP: already in save loop")
else:
    print("2. WARN: save loop pattern not matched")

# 3. Add tier_counts to /health
if "tier_counts" not in code:
    # Find sprint6 line in health and add tier_counts
    old = '"sprint6": True,'
    new = '"sprint6": True, "tier_counts": _classify_tiers(),'
    if old in code:
        code = code.replace(old, new, 1)
        changes += 1
        print("3. Added tier_counts to /health")
    else:
        print("3. WARN: sprint6 line not found in health")
else:
    print("3. SKIP: tier_counts already present")

if changes > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"\nDONE: {changes} changes applied to {path}")
else:
    print("\nNo changes needed")
