"""
Patch karma-core/server.py to add CC proposal injection into build_karma_context().

Applies two changes:
1. Inserts query_pending_cc_proposals() function before query_identity_facts()
2. Injects CC proposal surfacing block after the Recently Learned section

NOTE: This patch has already been applied to the live server. Re-running it
on an already-patched file will fail at the anchor checks (which is correct
behaviour -- anchors are replaced and won't match a second time).

Pitfall documented: heredoc on Windows Git Bash turns \n into literal newlines
when writing Python source files. Workaround: use chr(92)+chr(110) to build
backslash-n sequences that must appear in the patched Python source.
"""
import sys, os

path = "/opt/seed-vault/memory_v1/karma-core/server.py"
src = open(path).read()

# -- 1. Add query_pending_cc_proposals before query_identity_facts ------
NEW_FUNC = '''
COLLAB_FILE = "/opt/seed-vault/memory_v1/ledger/collab.jsonl"

def query_pending_cc_proposals() -> list:
    """Return pending messages in collab.jsonl addressed to Karma (from CC).
    Surfaced in context so Karma knows CC has something to say."""
    import json as _json
    results = []
    try:
        if not os.path.exists(COLLAB_FILE):
            return []
        with open(COLLAB_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = _json.loads(line)
                except Exception:
                    continue
                if entry.get("to") == "karma" and entry.get("status") == "pending":
                    results.append(entry)
    except Exception as e:
        print(f"[WARN] query_pending_cc_proposals failed: {e}")
    return results

'''

MARKER = "def query_identity_facts() -> str:"
if MARKER not in src:
    print("ERROR: query_identity_facts marker not found")
    sys.exit(1)
src = src.replace(MARKER, NEW_FUNC + MARKER, 1)
print("Step 1 OK: query_pending_cc_proposals inserted")

# -- 2. Inject CC proposals block after Recently Learned block -----------------
# Use chr(92)+chr(110) to produce backslash+n in the output Python source file.
# Direct use of \n in heredoc-written scripts produces a literal newline instead.
bsn = chr(92) + chr(110)  # = \n (two chars: backslash + n)

OLD_TAIL = '                    parts.append(f"- {content}")\n\n    # Get key preferences about the user'

NEW_TAIL = (
    '                    parts.append(f"- {content}")\n'
    "\n"
    "    # CC Proposals: surface any pending CC->Karma messages so Karma sees them.\n"
    "    cc_proposals = query_pending_cc_proposals()\n"
    "    if cc_proposals:\n"
    '        parts.append("' + bsn + '## CC Has a Proposal")\n'
    "        for p in cc_proposals:\n"
    '            msg_id = p.get("id", "?")\n'
    '            content = p.get("content", "")[:400]\n'
    '            msg_type = p.get("type", "proposal")\n'
    '            parts.append(f"- [{msg_type}] {content}  (id: {msg_id})")\n'
    "\n"
    "    # Get key preferences about the user"
)

if OLD_TAIL not in src:
    print("ERROR: OLD_TAIL anchor not found in source")
    idx = src.find("Recently Learned")
    print("Context:", repr(src[max(0, idx-20):idx+400]))
    sys.exit(1)

src = src.replace(OLD_TAIL, NEW_TAIL, 1)
print("Step 2 OK: CC proposals block injected")

# -- 3. Add import os if not present -------------------------------------------
if "import os" not in src:
    src = "import os\n" + src
    print("Step 3: added import os")
else:
    print("Step 3 OK: import os already present")

open(path, "w").write(src)
print("Patch applied OK")
print(f"File size: {len(src)} bytes")

# -- 4. Syntax check -----------------------------------------------------------
import subprocess
result = subprocess.run(["python3", "-m", "py_compile", path], capture_output=True, text=True)
if result.returncode == 0:
    print("Syntax check: PASS")
else:
    print("Syntax check FAILED:", result.stderr)
    sys.exit(1)
