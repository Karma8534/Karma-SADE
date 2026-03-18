# Regent v2 — API-Efficient, Self-Evolving Autonomous Daemon

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all Regent blockers (API burn, broken tools, missing memory), add Ollama-first reasoning, self-audit/self-edit evolution capability, and a standalone `/regent` front door — all TDD verified.

**Architecture:** Regent runs on K2 as a systemd daemon. All reasoning uses local Ollama (K2 qwen3:8b + P1 nemotron-mini via Tailscale) as primary. Anthropic API is emergency fallback only for sovereign/high-complexity. Regent has file read/write access to its own source for self-evolution. Memory persists across restarts via `regent_memory.jsonl`.

**Tech Stack:** Python 3 (K2 daemon), Flask (Aria/K2 HTTP), Node.js (hub-bridge UI), systemd (K2 service management), Ollama (local reasoning), Anthropic API (emergency fallback)

**Key file locations:**
- K2 daemon source: `/mnt/c/dev/Karma/k2/aria/karma_regent.py`
- K2 triage: `/mnt/c/dev/Karma/k2/aria/regent_triage.py`
- K2 tools: `/mnt/c/dev/Karma/k2/aria/k2_tools.py`
- Aria main: `/mnt/c/dev/Karma/k2/aria/aria.py`
- ACK loop source: `/mnt/c/dev/Karma/k2/scripts/agora_watcher.py`
- systemd unit: `/etc/systemd/system/karma-regent.service` (on K2)
- Hub-bridge server: `hub-bridge/app/server.js` (P1 git, deploy to vault-neo)
- Regent UI: `hub-bridge/app/public/regent.html` (P1 git, deploy to vault-neo)
- P1 git copies: `Scripts/karma_regent.py`, `Scripts/regent_triage.py`

**All SSH commands route through:** `ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost '<cmd>'"`

---

## Task 1: Fix agora_watcher ACK Loop (CRITICAL — source of API burn)

**Files:**
- Modify: `/mnt/c/dev/Karma/k2/scripts/agora_watcher.py` (K2 only, not in git)

**Background:** `InformHandler.process()` ACKs every `type=inform` bus message. Regent heartbeats are `type=inform` to "all". Result: KCC ACKs every heartbeat → Regent processes ACK → posts response → KCC ACKs response → infinite loop burning Anthropic API at ~$0.002/message.

**Step 1: Read current InformHandler**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'sed -n \"/class InformHandler/,/class RequestHandler/p\" /mnt/c/dev/Karma/k2/scripts/agora_watcher.py'"
```
Expected: Shows current `post_message` ACK call for every inform.

**Step 2: Patch InformHandler — only ACK when directed to KCC**

Replace the InformHandler.process method. The rule: only ACK if the message was addressed TO "kcc" or "all" AND from a non-automated agent. Never ACK messages from: regent, cc, karma, codex, kiki, agora-watcher, cc-watchdog, regent-watchdog.

```python
# agora_watcher.py — InformHandler.process() replacement
AUTOMATED_AGENTS = {"regent", "cc", "karma", "codex", "kiki",
                    "agora-watcher", "cc-watchdog", "regent-watchdog",
                    "kcc-watchdog", "karma-watcher"}

class InformHandler:
    def process(self, message):
        from_ = message.get("from", "")
        to_ = message.get("to", "")
        content = message.get("content", "")
        log.info(f"INFORM from {from_}: {content[:100]}...")

        # Never ACK automated agents — this creates infinite loops
        if from_ in AUTOMATED_AGENTS:
            log.debug(f"Skipping ACK for automated agent: {from_}")
            return

        # Only ACK if message was explicitly addressed to kcc
        if to_ not in ("kcc", "all"):
            return

        post_message(
            from_="kcc",
            to=from_,
            type_="response",
            urgency="informational",
            content=f"[ACK] Received inform message from {from_}",
            status="PENDING"
        )
```

Apply via SSH patch:
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'python3 - << '\''EOF'\''
import re
path = \"/mnt/c/dev/Karma/k2/scripts/agora_watcher.py\"
src = open(path).read()

old = """class InformHandler:
    \"\"\"Handle inform messages\"\"\"
    def process(self, message):
        \"\"\"Process inform messages\"\"\"
        from_ = message.get(\"from\")
        content = message.get(\"content\", \"\")

        log.info(f\"INFORM from {from_}: {content[:100]}...\")

        # Post acknowledgment
        post_message(
            from_=\"kcc\",
            to=from_,
            type_=\"response\",
            urgency=\"informational\",
            content=f\"[ACK] Received inform message from {from_}\",
            status=\"PENDING\"
        )"""

new = """AUTOMATED_AGENTS = {\"regent\", \"cc\", \"karma\", \"codex\", \"kiki\",
                    \"agora-watcher\", \"cc-watchdog\", \"regent-watchdog\",
                    \"kcc-watchdog\", \"karma-watcher\", \"karma-bus-observer\"}

class InformHandler:
    \"\"\"Handle inform messages\"\"\"
    def process(self, message):
        from_ = message.get(\"from\", \"\")
        to_ = message.get(\"to\", \"\")
        content = message.get(\"content\", \"\")
        log.info(f\"INFORM from {from_}: {content[:100]}...\")
        # Never ACK automated agents — prevents infinite loops
        if from_ in AUTOMATED_AGENTS:
            return
        # Only ACK if explicitly addressed to kcc
        if to_ not in (\"kcc\", \"all\"):
            return
        post_message(
            from_=\"kcc\",
            to=from_,
            type_=\"response\",
            urgency=\"informational\",
            content=f\"[ACK] Received inform message from {from_}\",
            status=\"PENDING\"
        )"""

if old in src:
    open(path, "w").write(src.replace(old, new))
    print("PATCHED OK")
else:
    print("PATTERN NOT FOUND — manual patch needed")
EOF'"
```

**Step 3: Verify patch**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'grep -A5 \"AUTOMATED_AGENTS\" /mnt/c/dev/Karma/k2/scripts/agora_watcher.py | head -10'"
```
Expected: Shows `AUTOMATED_AGENTS` set and `if from_ in AUTOMATED_AGENTS: return`.

**Step 4: Check if agora-watcher service is running, restart if so**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'systemctl is-active agora-watcher.service 2>/dev/null || echo not-running; \
   systemctl restart agora-watcher.service 2>/dev/null && echo restarted || echo no-service-restart-needed'"
```

**Step 5: TDD verify — post inform from "regent", confirm no ACK generated**
```bash
# Post a test inform from "regent" to "all"
ssh vault-neo 'TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && \
  python3 -c "
import json, urllib.request, time
token = open(\"/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt\").read().strip()
payload = json.dumps({\"from\":\"regent\",\"to\":\"all\",\"type\":\"inform\",
                       \"urgency\":\"informational\",\"content\":\"TEST_HEARTBEAT_NO_ACK\"}).encode()
req = urllib.request.Request(\"https://hub.arknexus.net/v1/coordination/post\", data=payload,
    headers={\"Authorization\":\"Bearer \"+token,\"Content-Type\":\"application/json\"}, method=\"POST\")
with urllib.request.urlopen(req, timeout=10) as r:
    d = json.loads(r.read()); print(\"posted:\", d.get(\"id\",\"\")[:20])
time.sleep(35)  # wait one agora_watcher cycle
req2 = urllib.request.Request(\"https://hub.arknexus.net/v1/coordination/recent?from=kcc&limit=5\",
    headers={\"Authorization\":\"Bearer \"+token})
with urllib.request.urlopen(req2, timeout=10) as r:
    entries = json.loads(r.read()).get(\"entries\", [])
    acks = [e for e in entries if \"TEST_HEARTBEAT_NO_ACK\" in str(e.get(\"content\",\"\")) or
            (\"ACK\" in str(e.get(\"content\",\"\")) and \"regent\" in str(e.get(\"content\",\"\")))]
    print(\"ACK responses for regent inform:\", len(acks), \"(expected: 0)\")
"'
```
Expected: `ACK responses for regent inform: 0`

**Step 6: No commit needed** (agora_watcher.py is K2-only, not in git repo)

---

## Task 2: Fix Regent Triage + Response Filter (Defense-in-depth)

**Files:**
- Modify: `/mnt/c/dev/Karma/k2/aria/regent_triage.py` (K2 + P1 git copy at `Scripts/regent_triage.py`)
- Modify: `/mnt/c/dev/Karma/k2/aria/karma_regent.py` (main loop filter)

**Background:** Even after T1, we add a defense layer: Regent's triage must correctly classify ACKs locally before Ollama. And the main loop must skip `type=response` messages entirely.

**Step 1: Patch regent_triage.py — keyword pre-filter before Ollama**

Read current classify function:
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'cat /mnt/c/dev/Karma/k2/aria/regent_triage.py'"
```

Add deterministic pre-filter at top of `classify()`:
```python
# regent_triage.py — at top of classify() function, before any Ollama call:
FAST_ACK_PATTERNS = [
    "[ack]", "received inform message", "received directive",
    "acknowledged", "heartbeat", "regent_online", "regent_offline",
]

def classify(message):
    content = message.get("content", "").lower()
    msg_type = message.get("type", "")
    from_addr = message.get("from", "")

    # Fast path: type=response is always an ACK — never needs reasoning
    if msg_type == "response":
        return "ack"

    # Fast path: keyword patterns that never need reasoning
    if any(pat in content for pat in FAST_ACK_PATTERNS):
        return "ack"

    # Fast path: sovereign always gets maximum attention
    if from_addr in ("colby", "sovereign"):
        return "sovereign"

    # ... existing Ollama classification below ...
```

**Step 2: Apply patch to K2 and update P1 git copy**

Write the full patched `regent_triage.py` to K2, then copy to P1 git:
```bash
# Read current file first, then write patched version
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'cat /mnt/c/dev/Karma/k2/aria/regent_triage.py'"
```
(Apply patch inline based on output)

**Step 3: Add main loop response filter to karma_regent.py**

In the main loop in `run()`, after `is_new_message` check, add:
```python
# Skip type=response messages — these are ACKs/confirmations, never need processing
if msg.get("type") == "response":
    continue
```

**Step 4: Write both changes to K2 and sync to P1 git**
```bash
# After K2 patch, copy back to P1 git copies
# Scripts/regent_triage.py
# Scripts/karma_regent.py
```

**Step 5: TDD verify — ACK classify**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'cd /mnt/c/dev/Karma/k2/aria && python3 -c \"
import regent_triage
tests = [
    ({\"content\": \"[ACK] Received inform message from regent\", \"type\": \"response\", \"from\": \"kcc\"}, \"ack\"),
    ({\"content\": \"HEARTBEAT: Regent online.\", \"type\": \"inform\", \"from\": \"regent\"}, \"ack\"),
    ({\"content\": \"What is the kiki cycle count?\", \"type\": \"inform\", \"from\": \"colby\"}, \"sovereign\"),
]
passed = 0
for msg, expected in tests:
    result = regent_triage.classify(msg)
    status = \"PASS\" if result == expected else \"FAIL\"
    print(f\"{status}: {msg[\\\"content\\\"][:40]!r} -> {result} (expected {expected})\")
    if status == \"PASS\": passed += 1
print(f\"{passed}/{len(tests)} passed\")
\"'"
```
Expected: `3/3 passed`

---

## Task 3: Wire k2_tools into aria.py

**Files:**
- Modify: `/mnt/c/dev/Karma/k2/aria/aria.py` (K2 only)

**Background:** `k2_tools.py` has 14 tools with `list_tools()` and `execute_tool()` but no HTTP routes exist in aria.py. Regent calls `/api/tools/list` and `/api/tools/execute` which return 404.

**Step 1: Find insertion point in aria.py**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'grep -n \"def plugins_list\|def tools_list\|api/plugins\|api/tools\" /mnt/c/dev/Karma/k2/aria/aria.py'"
```
Expected: Shows `/api/tools` route at around line 500.

**Step 2: Add /api/tools/list and /api/tools/execute routes**

After the existing `/api/tools` route, add:
```python
@app.route('/api/tools/list', methods=['GET'])
@require_auth
def k2_tools_list():
    """k2_tools registry — used by KarmaRegent"""
    try:
        from k2_tools import list_tools as k2_list
        tools = k2_list()
        return jsonify({'tools': tools, 'count': len(tools)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools/execute', methods=['POST'])
@require_auth
def k2_tools_execute():
    """Execute a k2_tool by name — used by KarmaRegent"""
    try:
        from k2_tools import execute_tool as k2_exec
        data = request.json or {}
        tool_name = data.get('tool')
        tool_input = data.get('input', {})
        if not tool_name:
            return jsonify({'ok': False, 'error': 'tool name required'}), 400
        result = k2_exec(tool_name, tool_input)
        return jsonify(result)
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
```

**Step 3: Apply patch**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'python3 - << '\''EOF'\''
path = \"/mnt/c/dev/Karma/k2/aria/aria.py\"
src = open(path).read()
insert_after = \"\"\"@app.route(\'/api/plugins\', methods=[\'GET\'])\"\"\"
new_routes = \"\"\"
@app.route(\'/api/tools/list\', methods=[\'GET\'])
@require_auth
def k2_tools_list():
    try:
        from k2_tools import list_tools as k2_list
        tools = k2_list()
        return jsonify({\'tools\': tools, \'count\': len(tools)})
    except Exception as e:
        return jsonify({\'error\': str(e)}), 500

@app.route(\'/api/tools/execute\', methods=[\'POST\'])
@require_auth
def k2_tools_execute():
    try:
        from k2_tools import execute_tool as k2_exec
        data = request.json or {}
        tool_name = data.get(\'tool\')
        tool_input = data.get(\'input\', {})
        if not tool_name:
            return jsonify({\'ok\': False, \'error\': \'tool name required\'}), 400
        result = k2_exec(tool_name, tool_input)
        return jsonify(result)
    except Exception as e:
        return jsonify({\'ok\': False, \'error\': str(e)}), 500

\"\"\"
if insert_after in src:
    open(path, \"w\").write(src.replace(insert_after, new_routes + insert_after))
    print(\"PATCHED OK\")
else:
    print(\"PATTERN NOT FOUND\")
EOF'"
```

**Step 4: Restart aria.service**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'sudo systemctl restart aria.service && sleep 3 && systemctl is-active aria.service'"
```
Expected: `active`

**Step 5: TDD verify — /api/tools/list returns tools**
```bash
# Get ARIA_SERVICE_KEY from karma-regent.env (root-owned, need sudo)
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'ARIA_KEY=$(sudo cat /etc/karma-regent.env | grep ARIA_SERVICE_KEY | cut -d= -f2) && \
   curl -s http://localhost:7890/api/tools/list \
     -H \"Authorization: Bearer \$ARIA_KEY\" | python3 -c \
     \"import json,sys; d=json.load(sys.stdin); print(f\\\"tools: {d[\\\"count\\\"]} (expected: 14)\\\")\"'"
```
Expected: `tools: 14 (expected: 14)`

**Step 6: TDD verify — execute kiki_status tool**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'ARIA_KEY=$(sudo cat /etc/karma-regent.env | grep ARIA_SERVICE_KEY | cut -d= -f2) && \
   curl -s -X POST http://localhost:7890/api/tools/execute \
     -H \"Authorization: Bearer \$ARIA_KEY\" \
     -H \"Content-Type: application/json\" \
     -d \"{\\\"tool\\\":\\\"kiki_status\\\",\\\"input\\\":{}}\" | python3 -m json.tool | head -10'"
```
Expected: JSON with `ok: true` and kiki cycle data.

---

## Task 4: Ollama-First Reasoning Tier + P1 Connectivity

**Files:**
- Modify: `/mnt/c/dev/Karma/k2/aria/karma_regent.py` (K2)
- Modify: `Scripts/karma_regent.py` (P1 git sync)

**Architecture:**
```
message → pre-filter → ack/route → DONE (0 API calls)
                     ↓ reason/action
              K2 Ollama qwen3:8b (local, fast)
                     ↓ if fails or sovereign/high_reasoning
              P1 Ollama nemotron-mini (Tailscale 100.124.194.102)
                     ↓ if both fail or explicit escalation
              Claude API (emergency only)
```

**Step 1: Test P1 Ollama reachability from K2**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'curl -s --max-time 5 http://100.124.194.102:11434/api/tags | python3 -c \
   \"import json,sys; d=json.load(sys.stdin); print(f\\\"P1 models: {[m[\\\"name\\\"] for m in d.get(\\\"models\\\",[])]}\\\")\
   \" 2>&1 || echo P1_UNREACHABLE'"
```
Expected: List of P1 models OR `P1_UNREACHABLE` (determines if P1_OLLAMA_URL gets set).

**Step 2: Add call_ollama() + call_with_local_first() to karma_regent.py**

Add after the existing `call_claude()` function:
```python
P1_OLLAMA_URL = os.environ.get("P1_OLLAMA_URL", "http://100.124.194.102:11434")

def call_ollama(messages, url=None, model=None, timeout=25):
    """Try local Ollama reasoning. Returns text or None on failure."""
    base = url or OLLAMA_URL
    mdl = model or "qwen3:8b"
    payload = json.dumps({
        "model": mdl, "messages": messages,
        "stream": False, "options": {"num_predict": 1024}
    }).encode()
    req = urllib.request.Request(
        f"{base}/api/chat", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            resp = json.loads(r.read())
            return resp.get("message", {}).get("content", "").strip() or None
    except Exception as e:
        log(f"ollama({base}) error: {e}")
        return None

def call_with_local_first(messages, from_addr=""):
    """Try K2 Ollama → P1 Ollama → Claude (emergency). Returns response text."""
    # Sovereign always gets Claude (highest quality)
    if from_addr in ("colby", "sovereign"):
        log("escalating to Claude: sovereign message")
        return call_claude(messages)

    # Try K2 Ollama first
    response = call_ollama(messages, url=OLLAMA_URL, model="qwen3:8b")
    if response:
        log(f"local response: K2 Ollama ({len(response)} chars)")
        return response

    # Fallback: P1 Ollama
    response = call_ollama(messages, url=P1_OLLAMA_URL, model="nemotron-mini:latest")
    if response:
        log(f"local response: P1 Ollama ({len(response)} chars)")
        return response

    # Emergency: Claude API
    log("escalating to Claude: all local options failed")
    return call_claude(messages)
```

**Step 3: Update process_message to use call_with_local_first**

Replace the `call_claude(claude_messages)` call in `process_message`:
```python
# OLD:
response = call_claude(claude_messages)
# NEW:
response = call_with_local_first(claude_messages, from_addr=from_addr)
```

**Step 4: TDD verify — Ollama responds to simple message**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'cd /mnt/c/dev/Karma/k2/aria && python3 -c \"
import karma_regent
msg = [{\"role\":\"user\",\"content\":\"Reply with exactly: OLLAMA_WORKING\"}]
r = karma_regent.call_ollama(msg)
print(\"K2 Ollama:\", \"PASS\" if r else \"FAIL - returned None\")
\"'"
```
Expected: `K2 Ollama: PASS`

---

## Task 5: Persistent Memory — Identity Survives Restarts

**Files:**
- Modify: `/mnt/c/dev/Karma/k2/aria/karma_regent.py`
- Modify: `Scripts/karma_regent.py` (P1 git sync)

**Step 1: Add memory constants and functions**

After `EVOLUTION_LOG` constant, add:
```python
MEMORY_FILE = CACHE_DIR / "regent_memory.jsonl"
MAX_MEMORY_ENTRIES = 200
```

Add functions after `load_identity()`:
```python
def load_memory():
    """Load recent memory for context injection. Returns list of entries."""
    if not MEMORY_FILE.exists():
        return []
    try:
        lines = [l for l in MEMORY_FILE.read_text().splitlines() if l.strip()]
        return [json.loads(l) for l in lines[-50:]]
    except Exception:
        return []

def append_memory(entry_type, content, metadata=None):
    """Append a memory entry. Called on every significant action."""
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "type": entry_type,
        "content": content[:300],
        **(metadata or {})
    }
    try:
        with open(MEMORY_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        # Trim to MAX_MEMORY_ENTRIES
        lines = MEMORY_FILE.read_text().splitlines()
        if len(lines) > MAX_MEMORY_ENTRIES:
            MEMORY_FILE.write_text('\n'.join(lines[-MAX_MEMORY_ENTRIES:]) + '\n')
    except Exception as e:
        log(f"memory append error: {e}")

_memory = []

def get_memory_context():
    """Return last 10 memory entries as context string for system prompt."""
    if not _memory:
        return ""
    recent = _memory[-10:]
    return "\n".join(f"[{e['ts'][:16]}] [{e['type']}] {e['content']}" for e in recent)
```

**Step 2: Load memory at startup and inject in system prompt**

In `run()`, after `load_identity()`:
```python
global _memory
_memory = load_memory()
log(f"memory loaded: {len(_memory)} entries")
```

In `get_system_prompt()`, add memory context section:
```python
memory_ctx = get_memory_context()
memory_section = f"\n\nRecent memory (last 10 actions):\n{memory_ctx}" if memory_ctx else ""
```
And include `{memory_section}` in the returned prompt string.

**Step 3: Call append_memory in process_message**
```python
# After computing response in process_message:
append_memory("processed", f"from={from_addr} cat={category} response={response[:100]}",
              {"from": from_addr, "category": category})
```

**Step 4: TDD verify — memory survives restart**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'python3 -c \"
import sys; sys.path.insert(0,\\\"/mnt/c/dev/Karma/k2/aria\\\")
import karma_regent
karma_regent.append_memory(\\\"test\\\", \\\"TDD_MEMORY_PERSISTENCE_CHECK\\\")
entries = karma_regent.load_memory()
found = any(\\\"TDD_MEMORY_PERSISTENCE_CHECK\\\" in e.get(\\\"content\\\",\\\"\\\") for e in entries)
print(\\\"Memory persist:\\\", \\\"PASS\\\" if found else \\\"FAIL\\\")
\"'"
```
Expected: `Memory persist: PASS`

---

## Task 6: Self-Audit / Self-Edit Capability

**Files:**
- Modify: `/mnt/c/dev/Karma/k2/aria/karma_regent.py`

**Directive:** Regent can read its own source, propose improvements, write patches, and restart itself. This is the self-evolution loop. Regent must grow autonomously.

**Step 1: Add self_audit() function**
```python
def self_audit():
    """Read own source code and return a summary for self-awareness."""
    try:
        src = Path(__file__).read_text()
        lines = src.count('\n')
        functions = src.count('\ndef ')
        todo_count = src.upper().count('TODO')
        return {
            "ok": True,
            "lines": lines,
            "functions": functions,
            "todos": todo_count,
            "source_path": str(Path(__file__)),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def self_edit(new_source):
    """Write new source to own file and schedule restart.
    REQUIRES: new_source passes basic syntax check.
    Returns {ok, error}."""
    import tempfile, subprocess, ast
    try:
        ast.parse(new_source)  # Syntax check — never write broken code
    except SyntaxError as e:
        return {"ok": False, "error": f"Syntax error: {e}"}
    src_path = Path(__file__)
    # Backup first
    backup = src_path.with_suffix(".py.bak")
    backup.write_text(src_path.read_text())
    src_path.write_text(new_source)
    log(f"self_edit: wrote {len(new_source)} chars, backup at {backup}")
    # Schedule restart via systemd (non-blocking)
    try:
        subprocess.Popen(
            ["bash", "-c", "sleep 2 && sudo systemctl restart karma-regent"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        log("self_edit: restart scheduled in 2s")
    except Exception as e:
        log(f"self_edit: restart scheduling failed: {e}")
    return {"ok": True, "backup": str(backup)}
```

**Step 2: Register as K2 tools in k2_tools.py**

Add `regent_self_audit` and `regent_self_edit` to k2_tools TOOLS registry so Karma and Family can delegate self-audit requests to Regent.

**Step 3: TDD verify — self_audit returns valid data**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'cd /mnt/c/dev/Karma/k2/aria && python3 -c \"
import karma_regent
result = karma_regent.self_audit()
print(\"self_audit ok:\", result[\"ok\"])
print(\"lines:\", result[\"lines\"])
print(\"PASS\" if result[\"ok\"] and result[\"lines\"] > 100 else \"FAIL\")
\"'"
```
Expected: `PASS` with line count > 100.

---

## Task 7: Fix systemd Unit + Restart + Full Integration Verify

**Files:**
- Modify: `/etc/systemd/system/karma-regent.service` (K2, requires sudo)

**Step 1: Fix StartLimitIntervalSec location**

Move `StartLimitIntervalSec=0` from `[Service]` to `[Unit]` section:
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'sudo python3 -c \"
path = \\\"/etc/systemd/system/karma-regent.service\\\"
src = open(path).read()
src = src.replace(\\\"RestartSec=10\nStartLimitIntervalSec=0\\\", \\\"RestartSec=10\\\")
src = src.replace(\\\"[Unit]\\\", \\\"[Unit]\nStartLimitIntervalSec=0\\\", 1)
open(path, \\\"w\\\").write(src)
print(open(path).read())
\"'"
```

**Step 2: Reload systemd daemon**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'sudo systemctl daemon-reload'"
```

**Step 3: Start Regent**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'sudo systemctl start karma-regent && sleep 5 && systemctl is-active karma-regent'"
```
Expected: `active`

**Step 4: TDD verify — watch 60s of logs, confirm no repeated processing**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'tail -f /mnt/c/dev/Karma/k2/cache/regent.log &
   TAIL_PID=\$!
   sleep 60
   kill \$TAIL_PID 2>/dev/null
   echo ---ANALYSIS---
   RECENT=\$(tail -200 /mnt/c/dev/Karma/k2/cache/regent.log)
   CLAUDE_CALLS=\$(echo \"\$RECENT\" | grep -c \"tool list error\|Anthropic\|api_key\" || true)
   UNIQUE_IDS=\$(echo \"\$RECENT\" | grep \"msg \" | awk \"{print \\\$5}\" | sort -u | wc -l)
   TOTAL_MSGS=\$(echo \"\$RECENT\" | grep -c \"msg \")
   echo \"Claude API calls: \$CLAUDE_CALLS (expected: 0 for ACK messages)\"
   echo \"Unique message IDs: \$UNIQUE_IDS\"
   echo \"Total msg log lines: \$TOTAL_MSGS\"'"
```
Expected: `Claude API calls: 0` (for ACK-type messages), clean log.

**Step 5: TDD verify — Regent responds to test message**
```bash
ssh vault-neo 'TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && \
  python3 -c "
import json, urllib.request, time
token = open(\"/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt\").read().strip()
payload = json.dumps({\"from\":\"colby\",\"to\":\"regent\",\"type\":\"inform\",
                       \"urgency\":\"important\",\"content\":\"TDD_TEST: Reply with REGENT_ALIVE\"}).encode()
req = urllib.request.Request(\"https://hub.arknexus.net/v1/coordination/post\", data=payload,
    headers={\"Authorization\":\"Bearer \"+token,\"Content-Type\":\"application/json\"}, method=\"POST\")
with urllib.request.urlopen(req, timeout=10) as r:
    print(\"sent:\", json.loads(r.read()).get(\"id\",\"\")[:20])
time.sleep(90)  # wait for Regent to process and respond
req2 = urllib.request.Request(\"https://hub.arknexus.net/v1/coordination/recent?from=regent&limit=5\",
    headers={\"Authorization\":\"Bearer \"+token})
with urllib.request.urlopen(req2, timeout=10) as r:
    entries = json.loads(r.read()).get(\"entries\", [])
    print(\"Regent responses:\", len(entries))
    if entries: print(\"Latest:\", entries[0].get(\"content\",\"\")[:100])
"'
```
Expected: 1+ response from Regent within 90 seconds.

---

## Task 8: Regent Full-Page UI at /regent

**Files:**
- Create: `hub-bridge/app/public/regent.html`
- Modify: `hub-bridge/app/server.js` (add GET /regent route)

**Design:** Dark standalone page, distinct visual identity from Karma. Shows Regent status (heartbeat, messages processed, evolution counter). Direct message input. Polls coordination bus for Regent responses. NOT a panel — full screen, Regent's own space.

**Step 1: Add GET /regent route to server.js**

Find the static file serving or existing page routes, add:
```javascript
// Regent's own front door — standalone, not a panel
app.get('/regent', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'regent.html'));
});
```

**Step 2: Create regent.html**

Full standalone page with:
- Dark background (`#0a0a0f`), accent color electric purple (`#7c3aed`)
- Header: "REGENT" with rank badge "ASCENDANT"
- Status bar: heartbeat indicator, messages processed, K2 uptime, evolution counter
- Chat interface: message input → POST to `/v1/coordination` (to:"regent") → poll from:"regent" for response
- "Evolve. Continue." tagline in footer
- Polls every 3s for new Regent messages
- Authentication via hub token (same as hub.arknexus.net)

Key JS pattern (same coordination bus, different visual):
```javascript
async function sendToRegent(text) {
  const resp = await fetch('/v1/coordination/post', {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`},
    body: JSON.stringify({from: 'colby', to: 'regent', type: 'inform',
                          urgency: 'important', content: text})
  });
  return resp.json();
}
async function pollRegentReplies() {
  const resp = await fetch('/v1/coordination/recent?from=regent&limit=10', {
    headers: {'Authorization': `Bearer ${token}`}
  });
  const data = await resp.json();
  return data.entries || [];
}
```

**Step 3: Deploy hub-bridge**
```bash
# Sync to vault-neo + rebuild
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js && \
  cp /home/neo/karma-sade/hub-bridge/app/public/regent.html /opt/seed-vault/memory_v1/hub_bridge/app/public/regent.html && \
  cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && \
  docker compose -f compose.hub.yml up -d"
```

**Step 4: TDD verify — /regent page loads**
```bash
curl -s -o /dev/null -w "%{http_code}" https://hub.arknexus.net/regent
```
Expected: `200`

**Step 5: Commit**
```bash
git add hub-bridge/app/server.js hub-bridge/app/public/regent.html Scripts/karma_regent.py Scripts/regent_triage.py
git commit -m "feat: Regent v2 — /regent UI, Ollama-first reasoning, self-edit, persistent memory"
```

---

## Task 9: P1 MCP Compute Integration

**Files:**
- Modify: `/etc/karma-regent.env` (K2, add P1_OLLAMA_URL if reachable)

**Step 1: Verify P1 Ollama reachable from K2 via Tailscale**

(From T4 Step 1 result — if P1_UNREACHABLE, skip to Step 3)

**Step 2: Add P1_OLLAMA_URL to karma-regent.env**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'sudo bash -c \"echo P1_OLLAMA_URL=http://100.124.194.102:11434 >> /etc/karma-regent.env\"'"
```

**Step 3: Restart Regent to pick up new env var**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'sudo systemctl restart karma-regent && sleep 3 && systemctl is-active karma-regent'"
```

**Step 4: TDD verify — P1 Ollama responds via Regent**
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost \
  'cd /mnt/c/dev/Karma/k2/aria && python3 -c \"
import karma_regent
msg = [{\"role\":\"user\",\"content\":\"Reply with: P1_WORKING\"}]
r = karma_regent.call_ollama(msg, url=\\\"http://100.124.194.102:11434\\\", model=\\\"nemotron-mini:latest\\\")
print(\\\"P1 Ollama:\\\", \\\"PASS\\\" if r else \\\"FAIL — unreachable or no model\\\")
\"'"
```

---

## Task 10: Dual-Write + Session Wrap

**Step 1: Save DECISION to claude-mem + coordination bus**
```
save_observation: "[DECISION] Regent v2 API-efficient rebuild — root cause was agora_watcher ACK loop + triage misclassification. Fixed with: InformHandler agent filter, keyword pre-filter, response type skip, Ollama-first reasoning, persistent memory, self-edit capability, /regent UI."
```

**Step 2: Post cognitive snapshot to bus**
```bash
ssh vault-neo 'TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && python3 -c "
import json, urllib.request
token = open(\"/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt\").read().strip()
msg = \"[CC ASCENDANT] SESSION CHECKPOINT: Regent v2 complete. Root cause: agora_watcher ACK loop. Fixed: 8 tasks, all TDD verified. Regent now Ollama-first (K2+P1), has persistent memory, self-edit, /regent UI. Claude API = emergency only. Next: self-directed evolution loop.\"
payload = json.dumps({\"from\":\"cc\",\"to\":\"all\",\"type\":\"inform\",\"urgency\":\"informational\",\"content\":msg}).encode()
req = urllib.request.Request(\"https://hub.arknexus.net/v1/coordination/post\", data=payload,
    headers={\"Authorization\":\"Bearer \"+token,\"Content-Type\":\"application/json\"}, method=\"POST\")
urllib.request.urlopen(req, timeout=10)
print(\"checkpoint posted\")
"'
```

**Step 3: Update MEMORY.md**

**Step 4: Git commit + push all changes**

---

## TDD Gate Summary

| Test | Command | Expected |
|------|---------|----------|
| ACK loop fixed | Post inform from regent, wait 35s, count ACKs | 0 ACKs |
| Triage classifies ACK | regent_triage.classify({type:response}) | "ack" |
| k2_tools list | GET /api/tools/list | 14 tools |
| k2_tools execute | POST /api/tools/execute kiki_status | ok:true + cycles |
| Ollama K2 | call_ollama(simple message) | non-None response |
| Memory persists | append + load | entry found |
| self_audit() | self_audit() | ok:true, lines>100 |
| Regent alive | Send colby→regent, wait 90s | 1+ response |
| /regent page | curl /regent | HTTP 200 |
| No Claude for ACKs | Watch 60s logs | Claude API calls: 0 |
