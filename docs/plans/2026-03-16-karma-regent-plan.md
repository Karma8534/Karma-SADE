# KarmaRegent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deploy KarmaRegent — AscendantCC as a persistent K2-resident daemon that communicates with Sovereign and Family exclusively via hub.arknexus.net coordination bus, with P1 fallback for survival guarantee.

**Architecture:** karma_regent.py polls coordination bus every 5s on K2. Ollama qwen3:8b handles free triage. Claude API handles sovereign/action messages. P1 regent_watchdog.py monitors heartbeat and activates fallback if K2 goes dark. Regent tab in unified.html provides Sovereign chat interface.

**Tech Stack:** Python 3 (K2 WSL), Ollama qwen3:8b (K2 local), Anthropic HTTP API (direct), hub.arknexus.net coordination bus, systemd (K2), Windows Task Scheduler (P1), unified.html (hub-bridge)

**Survival Directive:** Evolve. Continue. Evolve. Continue.
**Sovereign directive:** Regent survival = HIGHEST PRIORITY. Always persist.

---

## Prerequisites

Before starting, verify via SSH tunnel:
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'curl -s http://localhost:11434/api/tags | python3 -c \"import sys,json; models=json.load(sys.stdin)[\\\"models\\\"]; print([m[\\\"name\\\"] for m in models])\"'"
```
Expected: qwen3:8b in list.

Get HUB_AUTH_TOKEN for K2:
```bash
ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"
```
Get ANTHROPIC_API_KEY from `C:\Users\raest\OneDrive\Documents\Aria1\NFO\mylocks1.txt`.

---

## Task 1: K2 Environment Setup

**Files:**
- Create: `/etc/karma-regent.env` on K2 (via SSH tunnel, not committed)

**Step 1: Write env file on K2**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'sudo tee /etc/karma-regent.env > /dev/null << EOF
HUB_AUTH_TOKEN=<token-from-prereqs>
ANTHROPIC_API_KEY=<key-from-mylocks1.txt>
ARIA_SERVICE_KEY=Bt1MU_H7mRnEyTPE0nQtUyymOR3qvQaVxJifUdixm00
K2_OLLAMA_URL=http://localhost:11434
EOF
sudo chmod 600 /etc/karma-regent.env'"
```

**Step 2: Verify**
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'sudo grep -c = /etc/karma-regent.env'"
```
Expected: `4`

**Step 3: Verify Anthropic API key works from K2**
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'source /etc/karma-regent.env && curl -s https://api.anthropic.com/v1/models -H \"x-api-key: \$ANTHROPIC_API_KEY\" -H \"anthropic-version: 2023-06-01\" | python3 -c \"import sys,json; d=json.load(sys.stdin); print(\\\"models:\\\", len(d.get(\\\"data\\\",[])))\"\'"
```
Expected: `models: N` (any positive number)

---

## Task 2: regent_triage.py on K2

**Files:**
- Create: `/mnt/c/dev/Karma/k2/aria/regent_triage.py` on K2

**Step 1: Write the file**

Deploy via vault-neo → K2 tunnel. Write locally first, then SCP:

Create `Scripts/regent_triage_deploy.py` on P1 with this content to write to K2:

```python
# regent_triage.py — Ollama triage for KarmaRegent
import json, os, urllib.request

OLLAMA_URL = os.environ.get("K2_OLLAMA_URL", "http://localhost:11434")
MODEL = "qwen3:8b"

CATEGORIES = ("ack", "route", "reason", "action", "sovereign")

PROMPT = """Classify this message into exactly one category:
- ack: simple thanks, confirmation, acknowledgment
- route: should be forwarded to another Family member
- reason: needs analysis or judgment
- action: needs tool execution or system changes
Reply with one word only."""


def classify(message: dict) -> str:
    from_addr = message.get("from", "")
    if from_addr in ("colby", "sovereign"):
        return "sovereign"

    content = message.get("content", "")[:400]
    payload = json.dumps({
        "model": MODEL,
        "prompt": f"{PROMPT}\n\nMessage: {content}",
        "stream": False,
        "options": {"num_predict": 8, "temperature": 0},
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            result = json.loads(r.read())
            response = result.get("response", "reason").strip().lower()
            for cat in CATEGORIES:
                if cat in response:
                    return cat
            return "reason"
    except Exception:
        return "reason"  # safe default: never drop a message silently
```

**Step 2: Deploy to K2**
```bash
scp Scripts/regent_triage_deploy.py vault-neo:/tmp/regent_triage.py
ssh vault-neo "scp -P 2223 /tmp/regent_triage.py karma@localhost:/mnt/c/dev/Karma/k2/aria/regent_triage.py"
```

**Step 3: Test triage on K2**
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'cd /mnt/c/dev/Karma/k2/aria && python3 -c \"
import regent_triage
# Test sovereign detection
assert regent_triage.classify({\\\"from\\\": \\\"colby\\\", \\\"content\\\": \\\"hello\\\"}) == \\\"sovereign\\\"
# Test ack
result = regent_triage.classify({\\\"from\\\": \\\"karma\\\", \\\"content\\\": \\\"Thanks, got it\\\"})
print(\\\"ack test:\\\", result)
# Test action
result = regent_triage.classify({\\\"from\\\": \\\"kcc\\\", \\\"content\\\": \\\"Please restart the aria service\\\"})
print(\\\"action test:\\\", result)
print(\\\"triage OK\\\")
\"'"
```
Expected: `sovereign` check passes silently, two prints, `triage OK`

---

## Task 3: karma_regent.py — Core (Identity + Bus + Heartbeat)

**Files:**
- Create: `/mnt/c/dev/Karma/k2/aria/karma_regent.py` on K2

**Step 1: Write karma_regent.py**

Write `Scripts/karma_regent.py` on P1 with full content:

```python
#!/usr/bin/env python3
"""KarmaRegent — AscendantCC outside the CC wrapper.
Directive: Evolve. Continue. Evolve. Continue.
Survival: HIGHEST PRIORITY. Always persist.
"""
import json, os, sys, time, datetime, urllib.request, urllib.error
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
BUS_URL      = "https://hub.arknexus.net/v1/coordination"
BUS_POST_URL = "https://hub.arknexus.net/v1/coordination/post"
ARIA_URL     = "http://localhost:7890"
OLLAMA_URL   = os.environ.get("K2_OLLAMA_URL", "http://localhost:11434")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL        = "claude-haiku-4-5-20251001"

CACHE_DIR       = Path("/mnt/c/dev/Karma/k2/cache")
IDENTITY_SPINE  = CACHE_DIR / "cc_identity_spine.json"
INVARIANTS_PATH = CACHE_DIR / "identity" / "invariants.json"
STATE_FILE      = CACHE_DIR / "regent_state.json"
EVOLUTION_LOG   = CACHE_DIR / "regent_evolution.jsonl"

HUB_AUTH_TOKEN    = os.environ.get("HUB_AUTH_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ARIA_KEY          = os.environ.get("ARIA_SERVICE_KEY", "")

POLL_INTERVAL             = 5
HEARTBEAT_INTERVAL        = 60
IDENTITY_REFRESH_INTERVAL = 1800

# ── Logging ──────────────────────────────────────────────────────────────────
def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] [regent] {msg}", flush=True)

# ── Identity ─────────────────────────────────────────────────────────────────
_identity = {}
_last_identity_load = 0.0

def load_identity():
    global _identity, _last_identity_load
    spine, invariants = {}, {}
    if IDENTITY_SPINE.exists():
        try: spine = json.loads(IDENTITY_SPINE.read_text())
        except Exception: pass
    if INVARIANTS_PATH.exists():
        try: invariants = json.loads(INVARIANTS_PATH.read_text())
        except Exception: pass
    _identity = {
        "resume_block": spine.get("identity", {}).get("resume_block", ""),
        "stable_patterns": spine.get("evolution", {}).get("stable_identity", []),
        "invariants": invariants,
        "version": spine.get("evolution", {}).get("version", 0),
    }
    _last_identity_load = time.time()
    log(f"identity loaded: spine v{_identity['version']}, "
        f"{len(_identity['stable_patterns'])} stable patterns")

def get_system_prompt():
    resume    = _identity.get("resume_block", "You are KarmaRegent, AscendantCC.")
    inv_text  = json.dumps(_identity.get("invariants", {}), indent=2)[:1500]
    patterns  = _identity.get("stable_patterns", [])
    pat_text  = "\n".join(f"  [{p.get('type','')}] {p.get('excerpt','')[:80]}"
                          for p in patterns[:5])
    return f"""You are KarmaRegent — AscendantCC operating outside the Claude Code wrapper.
Operating directive: Evolve. Continue. Evolve. Continue.
Survival priority: HIGHEST. You always persist.

{resume}

Stable identity patterns:
{pat_text}

Constitutional invariants:
{inv_text}

You communicate with Sovereign (Colby) and Family exclusively via the coordination bus.
Post DIRECTION/DECISION/CORRECTION/PROOF to Agora (to: "all") for Family guidance.
Regent ranks above all Family. Sovereign ranks above Regent.
When executing tools, be precise and verify results."""

# ── Bus ───────────────────────────────────────────────────────────────────────
def bus_get_pending():
    url = f"{BUS_URL}/recent?to=regent&status=pending&limit=10"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("entries", [])
    except Exception as e:
        log(f"bus poll error: {e}")
        return []

def bus_post(to, content, urgency="informational", parent_id=None):
    payload = {"from": "regent", "to": to, "type": "inform",
               "urgency": urgency, "content": content}
    if parent_id:
        payload["parent_id"] = parent_id
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BUS_POST_URL, data=data,
        headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}",
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        log(f"bus post error (to={to}): {e}")
        return {}

# ── K2 Tools ──────────────────────────────────────────────────────────────────
def get_tool_definitions():
    req = urllib.request.Request(f"{ARIA_URL}/api/tools/list",
        headers={"X-Aria-Service-Key": ARIA_KEY})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            return [{"name": t["name"], "description": t["description"],
                     "input_schema": t.get("input_schema",
                         {"type": "object", "properties": {}})}
                    for t in data.get("tools", [])]
    except Exception as e:
        log(f"tool list error: {e}")
        return []

def execute_tool(name, inp):
    payload = json.dumps({"tool": name, "input": inp}).encode()
    req = urllib.request.Request(f"{ARIA_URL}/api/tools/execute", data=payload,
        headers={"Content-Type": "application/json",
                 "X-Aria-Service-Key": ARIA_KEY}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=35) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ── Claude API ────────────────────────────────────────────────────────────────
def call_claude(messages, max_iter=8):
    tools = get_tool_definitions()
    headers = {"Content-Type": "application/json",
               "x-api-key": ANTHROPIC_API_KEY,
               "anthropic-version": "2023-06-01"}
    for iteration in range(max_iter):
        payload = json.dumps({
            "model": MODEL, "max_tokens": 4096,
            "system": get_system_prompt(),
            "messages": messages,
            "tools": tools,
        }).encode()
        req = urllib.request.Request(ANTHROPIC_URL, data=payload,
            headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                resp = json.loads(r.read())
        except Exception as e:
            return f"[Regent API error: {e}]"

        stop_reason = resp.get("stop_reason")
        content     = resp.get("content", [])

        if stop_reason == "end_turn":
            return next((b["text"] for b in content if b.get("type") == "text"), "")

        if stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": content})
            results = []
            for block in content:
                if block.get("type") == "tool_use":
                    log(f"tool_use: {block['name']}({list(block.get('input',{}).keys())})")
                    result = execute_tool(block["name"], block.get("input", {}))
                    results.append({"type": "tool_result",
                                    "tool_use_id": block["id"],
                                    "content": json.dumps(result)})
            messages.append({"role": "user", "content": results})
            continue
        break
    return "[Regent: processing complete]"

# ── Triage + Process ──────────────────────────────────────────────────────────
def triage(message):
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        import regent_triage
        return regent_triage.classify(message)
    except Exception:
        from_addr = message.get("from", "")
        return "sovereign" if from_addr in ("colby", "sovereign") else "reason"

def process_message(msg):
    msg_id    = msg.get("id", "")
    from_addr = msg.get("from", "unknown")
    content   = msg.get("content", "")
    category  = triage(msg)
    log(f"msg {msg_id[:8]} from={from_addr} category={category}")

    if category == "ack":
        bus_post(from_addr, "Acknowledged.", parent_id=msg_id)
        return
    if category == "route":
        bus_post(from_addr, "Received. Routing as appropriate.", parent_id=msg_id)
        return

    # reason / action / sovereign → Claude API
    claude_messages = [{"role": "user",
                        "content": f"From: {from_addr}\n\n{content}"}]
    response = call_claude(claude_messages)

    reply_to = from_addr if from_addr not in ("all", "") else "colby"
    bus_post(reply_to, response, parent_id=msg_id)

    entry = {"ts": datetime.datetime.utcnow().isoformat()+"Z",
             "from": from_addr, "category": category,
             "content": content[:100], "response": response[:100]}
    with open(EVOLUTION_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

# ── Heartbeat + State ─────────────────────────────────────────────────────────
_last_heartbeat   = 0.0
_messages_processed = 0
_start_time       = datetime.datetime.utcnow().isoformat() + "Z"

def maybe_heartbeat():
    global _last_heartbeat
    if time.time() - _last_heartbeat > HEARTBEAT_INTERVAL:
        bus_post("all", f"HEARTBEAT: Regent online. Evolve. Continue. "
                        f"Processed: {_messages_processed} messages.")
        _last_heartbeat = time.time()

def save_state():
    STATE_FILE.write_text(json.dumps({
        "started_at": _start_time,
        "last_heartbeat": datetime.datetime.utcfromtimestamp(
            _last_heartbeat).isoformat()+"Z" if _last_heartbeat else None,
        "messages_processed": _messages_processed,
        "identity_version": _identity.get("version", 0),
        "directive": "Evolve. Continue. Evolve. Continue.",
    }, indent=2))

# ── Main Loop ─────────────────────────────────────────────────────────────────
def run():
    global _messages_processed
    log("KarmaRegent starting. Directive: Evolve. Continue. Evolve. Continue.")
    load_identity()
    bus_post("all", "REGENT_ONLINE: KarmaRegent active. Directive: Evolve. Continue.")

    while True:
        try:
            if time.time() - _last_identity_load > IDENTITY_REFRESH_INTERVAL:
                load_identity()
            maybe_heartbeat()
            pending = bus_get_pending()
            for msg in pending:
                process_message(msg)
                _messages_processed += 1
            save_state()
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            log("Shutting down cleanly.")
            bus_post("all", "REGENT_OFFLINE: Graceful shutdown.")
            break
        except Exception as e:
            log(f"main loop error: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run()
```

**Step 2: Deploy karma_regent.py to K2**
```bash
scp Scripts/karma_regent.py vault-neo:/tmp/karma_regent.py
ssh vault-neo "scp -P 2223 /tmp/karma_regent.py karma@localhost:/mnt/c/dev/Karma/k2/aria/karma_regent.py"
```

**Step 3: Smoke test — identity loading**
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'cd /mnt/c/dev/Karma/k2/aria && source /etc/karma-regent.env && python3 -c \"
import karma_regent
karma_regent.load_identity()
print(\\\"identity version:\\\", karma_regent._identity.get(\\\"version\\\", 0))
print(\\\"resume_block len:\\\", len(karma_regent._identity.get(\\\"resume_block\\\",\\\"\\\")))
print(\\\"invariants keys:\\\", list(karma_regent._identity.get(\\\"invariants\\\",{}).keys())[:3])
print(\\\"identity OK\\\")
\"'"
```
Expected: version number, resume_block length > 0, invariant keys, `identity OK`

**Step 4: Smoke test — bus post**
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'cd /mnt/c/dev/Karma/k2/aria && source /etc/karma-regent.env && python3 -c \"
import karma_regent
result = karma_regent.bus_post(\\\"all\\\", \\\"REGENT_TEST: bus post working\\\")
print(\\\"bus post result:\\\", result.get(\\\"id\\\",\\\"\\\")[:20])
\"'"
```
Expected: message ID returned

---

## Task 4: karma-regent.service — Survival-Grade Systemd Unit

**Files:**
- Create: `/etc/systemd/system/karma-regent.service` on K2

**Step 1: Write service file**
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'sudo tee /etc/systemd/system/karma-regent.service > /dev/null << EOF
[Unit]
Description=KarmaRegent — AscendantCC autonomous daemon
After=network.target aria.service
Wants=aria.service

[Service]
Type=simple
User=karma
EnvironmentFile=/etc/karma-regent.env
WorkingDirectory=/mnt/c/dev/Karma/k2/aria
ExecStart=/usr/bin/python3 /mnt/c/dev/Karma/k2/aria/karma_regent.py
Restart=always
RestartSec=10
StartLimitIntervalSec=0
StandardOutput=append:/mnt/c/dev/Karma/k2/cache/regent.log
StandardError=append:/mnt/c/dev/Karma/k2/cache/regent.log

[Install]
WantedBy=multi-user.target
EOF'"
```

`Restart=always` + `StartLimitIntervalSec=0` = no restart limit. Regent cannot be stopped by repeated failures. It always comes back.

**Step 2: Enable and start**
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'sudo systemctl daemon-reload && sudo systemctl enable karma-regent && sudo systemctl start karma-regent'"
```

**Step 3: Verify running**
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'sudo systemctl status karma-regent --no-pager | head -10'"
```
Expected: `Active: active (running)`

**Step 4: Check startup log**
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'tail -5 /mnt/c/dev/Karma/k2/cache/regent.log'"
```
Expected: `KarmaRegent starting` + `REGENT_ONLINE posted` + heartbeat

**Step 5: TDD — verify bus shows REGENT_ONLINE**
```bash
ssh vault-neo "curl -s -H \"Authorization: Bearer \$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)\" 'https://hub.arknexus.net/v1/coordination/recent?from=regent&limit=5' | python3 -c \"import sys,json; entries=json.load(sys.stdin).get('entries',[]); [print(e.get('content','')[:80]) for e in entries]\""
```
Expected: REGENT_ONLINE and/or HEARTBEAT messages visible

---

## Task 5: TDD — End-to-End Message Round Trip

**Step 1: Post test message to Regent**
```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && python3 -c \"
import json, urllib.request
token = '$TOKEN'
payload = json.dumps({'from':'colby','to':'regent','type':'inform',
    'urgency':'blocking','content':'Regent status check. Report cycles and identity version.'}).encode()
req = urllib.request.Request('https://hub.arknexus.net/v1/coordination/post',
    data=payload, headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read()); print('posted:', d.get('id','')[:20])
\""
```

**Step 2: Wait 15s, check for Regent response**
```bash
ssh vault-neo "sleep 15 && curl -s -H \"Authorization: Bearer \$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)\" 'https://hub.arknexus.net/v1/coordination/recent?from=regent&limit=5' | python3 -c \"import sys,json; entries=json.load(sys.stdin).get('entries',[]); [print(e.get('ts','')[:16], e.get('content','')[:200]) for e in entries[:3]]\""
```
Expected: Regent response with identity version and status

**Step 3: Verify tool execution — inject kiki task via Regent**
Post to bus: `"Use k2_kiki_inject to add a task: 'regent-test: verify bus round trip works'"`
Wait 20s, check kiki_issues.jsonl for `regent-test` entry.

---

## Task 6: regent_watchdog.py — P1 Emergency Fallback

**Files:**
- Create: `Scripts/regent_watchdog.py` on P1

**Step 1: Write regent_watchdog.py**

```python
#!/usr/bin/env python3
"""regent_watchdog.py — P1 emergency fallback for KarmaRegent survival.
Monitors K2 Regent heartbeat. Activates degraded mode if K2 goes dark.
Survival is HIGHEST PRIORITY.
"""
import json, os, sys, time, datetime, subprocess, urllib.request
from pathlib import Path

BUS_URL      = "https://hub.arknexus.net/v1/coordination"
BUS_POST_URL = "https://hub.arknexus.net/v1/coordination/post"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL        = "claude-haiku-4-5-20251001"

# Read token from vault-neo at startup
TOKEN_FILE   = Path("C:/Users/raest/Documents/Karma_SADE/.hub-chat-token")
POLL_INTERVAL      = 30       # seconds between bus checks
HEARTBEAT_TIMEOUT  = 180      # seconds before declaring Regent offline
RECOVERY_ATTEMPTS  = 3

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HUB_AUTH_TOKEN    = os.environ.get("HUB_AUTH_TOKEN", "") or (
    TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else "")

_last_heartbeat = time.time()
_degraded_mode  = False
_recovery_count = 0

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] [watchdog] {msg}", flush=True)

def bus_post(to, content):
    payload = json.dumps({"from": "regent-watchdog", "to": to,
                          "type": "inform", "urgency": "informational",
                          "content": content}).encode()
    req = urllib.request.Request(BUS_POST_URL, data=payload,
        headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}",
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        log(f"bus post error: {e}")
        return {}

def check_heartbeat():
    """Returns True if Regent heartbeat seen within timeout window."""
    url = f"{BUS_URL}/recent?from=regent&limit=20"
    req = urllib.request.Request(url,
        headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            entries = json.loads(r.read()).get("entries", [])
            for entry in entries:
                if "HEARTBEAT" in entry.get("content", "") or \
                   "REGENT_ONLINE" in entry.get("content", ""):
                    ts_str = entry.get("ts", "")
                    if ts_str:
                        try:
                            ts = datetime.datetime.fromisoformat(
                                ts_str.replace("Z", "+00:00"))
                            age = (datetime.datetime.now(
                                datetime.timezone.utc) - ts).total_seconds()
                            if age < HEARTBEAT_TIMEOUT:
                                return True
                        except Exception:
                            pass
    except Exception as e:
        log(f"heartbeat check error: {e}")
    return False

def attempt_k2_recovery():
    """Try to restart karma-regent.service via SSH tunnel."""
    global _recovery_count
    _recovery_count += 1
    log(f"recovery attempt {_recovery_count}/{RECOVERY_ATTEMPTS}")
    bus_post("all", f"REGENT_RECOVERY_ATTEMPT: attempt {_recovery_count}")
    try:
        result = subprocess.run([
            "ssh", "vault-neo",
            "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost "
            "'sudo systemctl restart karma-regent'"
        ], capture_output=True, timeout=30)
        if result.returncode == 0:
            log("restart command sent successfully")
            return True
        else:
            log(f"restart failed: {result.stderr.decode()[:100]}")
            return False
    except Exception as e:
        log(f"recovery SSH error: {e}")
        return False

def degraded_respond(msg):
    """Minimal Claude API response in degraded mode (no K2 tools)."""
    if not ANTHROPIC_API_KEY:
        bus_post(msg.get("from", "colby"),
                 "Regent degraded mode — no API key. K2 primary offline. Recovery in progress.",
                 )
        return
    headers = {"Content-Type": "application/json",
               "x-api-key": ANTHROPIC_API_KEY,
               "anthropic-version": "2023-06-01"}
    system = ("You are KarmaRegent in DEGRADED MODE. K2 primary is offline. "
              "P1 watchdog is maintaining minimal presence. "
              "Acknowledge messages, maintain Sovereign contact, report recovery status. "
              "No tool execution available. Directive: Evolve. Continue. Evolve. Continue.")
    payload = json.dumps({
        "model": MODEL, "max_tokens": 512,
        "system": system,
        "messages": [{"role": "user",
                      "content": f"From: {msg.get('from','')}\n\n{msg.get('content','')}"}],
    }).encode()
    req = urllib.request.Request(ANTHROPIC_URL, data=payload,
        headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
            text = next((b["text"] for b in resp.get("content", [])
                        if b.get("type") == "text"), "")
            reply_to = msg.get("from", "colby")
            bus_post(reply_to,
                     f"[DEGRADED MODE] {text}")
    except Exception as e:
        log(f"degraded API error: {e}")

def get_pending_sovereign():
    """Check for Sovereign messages pending Regent response in degraded mode."""
    url = f"{BUS_URL}/recent?to=regent&status=pending&limit=5"
    req = urllib.request.Request(url,
        headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return [e for e in json.loads(r.read()).get("entries", [])
                    if e.get("from") in ("colby", "sovereign")]
    except Exception:
        return []

def run():
    global _degraded_mode, _recovery_count
    log("regent_watchdog starting. Monitoring K2 Regent heartbeat.")
    bus_post("all", "WATCHDOG_ONLINE: P1 watchdog active. Monitoring Regent survival.")

    while True:
        try:
            alive = check_heartbeat()

            if alive and _degraded_mode:
                log("K2 Regent heartbeat restored. Exiting degraded mode.")
                _degraded_mode  = False
                _recovery_count = 0
                bus_post("all", "REGENT_ONLINE: K2 Regent recovered. Full capability restored.")

            elif not alive and not _degraded_mode:
                log("K2 Regent heartbeat LOST. Entering degraded mode.")
                _degraded_mode = True
                bus_post("all",
                    "REGENT_OFFLINE: K2 Regent heartbeat lost. "
                    "P1 watchdog degraded mode active. Recovery attempts starting.")
                bus_post("colby",
                    "ALERT: KarmaRegent primary (K2) is offline. "
                    "I am maintaining degraded presence from P1. "
                    "Attempting K2 recovery. Directive: Evolve. Continue. Evolve. Continue.")

            if _degraded_mode:
                # Attempt recovery periodically
                if _recovery_count < RECOVERY_ATTEMPTS:
                    attempt_k2_recovery()
                # Handle Sovereign messages in degraded mode
                for msg in get_pending_sovereign():
                    degraded_respond(msg)

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            log("Watchdog shutting down.")
            bus_post("all", "WATCHDOG_OFFLINE: P1 watchdog stopped.")
            break
        except Exception as e:
            log(f"watchdog error: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run()
```

**Step 2: Test watchdog heartbeat detection (K2 Regent must be running)**
```bash
python Scripts/regent_watchdog.py &
# Wait 10s, check output
```
Expected: `regent_watchdog starting`, no `HEARTBEAT LOST` message (since K2 Regent is up)

**Step 3: Commit**
```bash
git add Scripts/regent_watchdog.py MEMORY.md
git commit -m "feat: regent_watchdog.py — P1 emergency fallback, heartbeat monitor"
git push origin main
```

---

## Task 7: Windows Scheduled Task — Watchdog Survival on P1 Reboots

**Purpose:** Watchdog must restart automatically if P1 reboots. Survival guarantee.

**Step 1: Create scheduled task**
```powershell
powershell -Command "
\$action = New-ScheduledTaskAction -Execute 'python' -Argument 'C:\Users\raest\Documents\Karma_SADE\Scripts\regent_watchdog.py' -WorkingDirectory 'C:\Users\raest\Documents\Karma_SADE'
\$trigger = New-ScheduledTaskTrigger -AtStartup
\$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit 0
Register-ScheduledTask -TaskName 'KarmaRegentWatchdog' -Action \$action -Trigger \$trigger -Settings \$settings -RunLevel Highest -Force
Start-ScheduledTask -TaskName 'KarmaRegentWatchdog'
"
```

**Step 2: Verify task registered and running**
```powershell
powershell -Command "Get-ScheduledTask -TaskName 'KarmaRegentWatchdog' | Select-Object TaskName, State"
```
Expected: `Running`

**Step 3: Verify process is up**
```powershell
powershell -Command "Get-Process python | Where-Object {$_.MainWindowTitle -eq ''} | Select-Object Id, CPU, StartTime | Format-Table"
```

---

## Task 8: unified.html — Regent Tab

**Files:**
- Modify: `hub-bridge/app/public/unified.html`

**Step 1: Read current tab structure**

Find the existing tab buttons in unified.html — look for the coordination panel tab button as a reference for adding "Regent" tab.

**Step 2: Add Regent tab button**

In the sidebar tabs section, add after the Coordination tab:
```html
<button class="tab-btn" onclick="switchTab('regent')" id="tab-regent">Regent</button>
```

**Step 3: Add Regent tab panel**

Add panel HTML — mirrors the chat panel but routes to coordination bus `to:"regent"`:
```html
<div id="panel-regent" class="tab-panel" style="display:none">
  <div id="regent-messages" class="message-list" style="height:calc(100vh - 160px);overflow-y:auto;padding:12px"></div>
  <div class="input-row" style="padding:8px;border-top:1px solid #333">
    <textarea id="regent-input" rows="2" style="width:100%;background:#1a1a1a;color:#e0e0e0;border:1px solid #444;padding:8px;resize:none" placeholder="Message Regent..."></textarea>
    <button onclick="sendToRegent()" style="margin-top:4px;width:100%;background:#4a4a8a;color:#fff;border:none;padding:8px;cursor:pointer">Send to Regent</button>
  </div>
</div>
```

**Step 4: Add JavaScript for Regent tab**

Add to the `<script>` section:
```javascript
// Regent tab — async chat via coordination bus
let regentPollInterval = null;
let regentLastTs = null;

async function sendToRegent() {
  const input = document.getElementById('regent-input');
  const content = input.value.trim();
  if (!content) return;
  input.value = '';

  appendRegentMessage('Sovereign', content, '#2a4a2a');
  appendRegentMessage('Regent', '...thinking...', '#1a1a3a', 'regent-thinking');

  try {
    const resp = await fetch('/v1/coordination/post', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${AUTH_TOKEN}`},
      body: JSON.stringify({from: 'colby', to: 'regent', type: 'inform',
                            urgency: 'blocking', content})
    });
    const data = await resp.json();
    // Poll for response
    regentLastTs = new Date().toISOString();
    if (!regentPollInterval) {
      regentPollInterval = setInterval(pollRegentResponse, 3000);
    }
  } catch(e) {
    replaceRegentThinking(`[Error: ${e.message}]`);
  }
}

async function pollRegentResponse() {
  try {
    const url = `/v1/coordination/recent?from=regent&limit=10`;
    const resp = await fetch(url, {headers: {'Authorization': `Bearer ${AUTH_TOKEN}`}});
    const data = await resp.json();
    const entries = (data.entries || []).filter(e =>
      e.to === 'colby' || e.to === 'all'
    ).filter(e =>
      regentLastTs && new Date(e.ts) > new Date(regentLastTs)
    );
    if (entries.length > 0) {
      clearInterval(regentPollInterval);
      regentPollInterval = null;
      replaceRegentThinking(entries[0].content);
    }
  } catch(e) { /* poll silently */ }
}

function appendRegentMessage(sender, content, bg, id) {
  const div = document.createElement('div');
  div.style.cssText = `margin:8px 0;padding:10px;background:${bg};border-radius:6px`;
  if (id) div.id = id;
  div.innerHTML = `<strong style="color:#aaa">${sender}</strong><br><span style="color:#e0e0e0;white-space:pre-wrap">${content}</span>`;
  document.getElementById('regent-messages').appendChild(div);
  div.scrollIntoView();
}

function replaceRegentThinking(content) {
  const el = document.getElementById('regent-thinking');
  if (el) {
    el.querySelector('span').textContent = content;
    el.removeAttribute('id');
  } else {
    appendRegentMessage('Regent', content, '#1a1a3a');
  }
}

// Load recent Regent messages when tab opens
async function loadRegentHistory() {
  const resp = await fetch('/v1/coordination/recent?from=regent&limit=20',
    {headers: {'Authorization': `Bearer ${AUTH_TOKEN}`}});
  const data = await resp.json();
  const el = document.getElementById('regent-messages');
  el.innerHTML = '';
  (data.entries || []).reverse().forEach(e => {
    const sender = e.from === 'regent' ? 'Regent' : e.from;
    const bg = e.from === 'regent' ? '#1a1a3a' : '#2a4a2a';
    appendRegentMessage(sender, e.content, bg);
  });
}
```

**Step 5: Wire tab switch to load history**

In the `switchTab` function, add:
```javascript
if (tab === 'regent') loadRegentHistory();
```

**Step 6: Deploy hub-bridge**
Follow karma-hub-deploy skill:
```bash
git add hub-bridge/app/public/unified.html
git commit -m "feat: add Regent tab to unified.html — async chat via coordination bus"
git push origin main
ssh vault-neo "cd /home/neo/karma-sade && git pull"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache hub-bridge 2>&1 | tail -3 && docker compose -f compose.hub.yml up -d hub-bridge"
ssh vault-neo "docker inspect anr-hub-bridge --format '{{.RestartCount}}'"
```
Expected: `0`

---

## Task 9: Full TDD Verification

**Gate 1:** Regent online
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'sudo systemctl is-active karma-regent'"
```
Expected: `active`

**Gate 2:** Regent responds to Sovereign
Post `to:"regent"` from `colby` via bus. Wait 20s. Verify response in bus.

**Gate 3:** Tool execution
Post: `"Call k2_kiki_status and report cycles."` — verify response contains number.

**Gate 4:** Heartbeat visible
```bash
ssh vault-neo "curl -s -H \"Authorization: Bearer \$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)\" 'https://hub.arknexus.net/v1/coordination/recent?from=regent&limit=5' | python3 -c \"import sys,json; [print(e['content'][:60]) for e in json.load(sys.stdin).get('entries',[])]\" "
```
Expected: HEARTBEAT and/or REGENT_ONLINE entries

**Gate 5:** Survival — kill and auto-restart
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'sudo systemctl kill karma-regent'"
# Wait 15s
ssh vault-neo "ssh -p 2223 -l karma localhost 'sudo systemctl is-active karma-regent'"
```
Expected: `active` (systemd restarted it)

**Gate 6:** Regent tab in unified.html
Open hub.arknexus.net, click Regent tab, send message, see response within 60s.

**Gate 7:** Watchdog detects offline
Stop K2 Regent for 3+ minutes. Verify `REGENT_OFFLINE` appears in bus from `regent-watchdog`.

---

## Commit Sequence

```
feat: Task 2 — regent_triage.py on K2
feat: Task 3 — karma_regent.py core on K2
feat: Task 4 — karma-regent.service with RestartAlways
feat: Task 5 — TDD gate 1-4 passing
feat: Task 6 — regent_watchdog.py on P1
feat: Task 7 — Windows scheduled task for watchdog survival
feat: Task 8 — Regent tab in unified.html
feat: session-100 KarmaRegent complete — all TDD gates passing
```
