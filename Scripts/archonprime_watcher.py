#!/usr/bin/env python3
"""
PROOF-A: ArchonPrime Watcher — KCC triggers Codex analysis on structural bus events.

Runs on P1 Windows. Polls coordination bus every 30s.
When a structural event is detected:
  1. Pipes Python script to vault-neo (python3 -) which writes prompt to K2 and runs Codex
  2. Pipes Python script to vault-neo (python3 -) to post analysis to bus

Both operations use `python3 -` (reads from stdin) to avoid ALL shell quoting issues.
K2 invocation: vault-neo SSH → K2:2223 reverse tunnel.

Structural events: bus messages where type=="structural" OR content starts with:
  [STRUCTURAL], TOOL_ADDITION:, GOVERNANCE:, POLICY_CHANGE:, PROOF_TRIGGER:, ARCHONPRIME:
"""
import json, os, subprocess, sys, time
from pathlib import Path

HUB_BASE   = "https://hub.arknexus.net"
POLL_SEC   = 30
TOKEN_FILE = Path(__file__).parent.parent / ".hub-chat-token"

STRUCTURAL_PREFIXES = (
    "[STRUCTURAL]", "TOOL_ADDITION:", "GOVERNANCE:", "POLICY_CHANGE:",
    "PROOF_TRIGGER:", "ARCHONPRIME:", "STRUCTURAL_EVENT:",
)

ARCHONPRIME_PROMPT_TMPL = (
    "You are ArchonPrime — the automated oversight function for the Karma SADE family system. "
    "A structural event occurred. Analyze it in 3-5 sentences: "
    "(1) what changed or was triggered, "
    "(2) whether it is safe and within governance constraints, "
    "(3) any risks or follow-up actions required. "
    "Event: {event}"
)


def get_token() -> str:
    tok = os.environ.get("HUB_CHAT_TOKEN", "").strip()
    if tok:
        return tok
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _vault_run(py_script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Pipe a Python script to vault-neo via 'python3 -' — zero quoting issues."""
    return subprocess.run(
        ["ssh", "vault-neo", "python3 -"],
        input=py_script,
        capture_output=True, text=True, timeout=timeout
    )


def hub_get() -> list:
    """Fetch coordination bus entries via vault-neo."""
    script = """\
import json, urllib.request
token = open('/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt').read().strip()
req = urllib.request.Request(
    'https://hub.arknexus.net/v1/coordination',
    headers={'Authorization': 'Bearer ' + token}
)
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read())
entries = data.get('entries', data.get('messages', data if isinstance(data, list) else []))
print(json.dumps(entries))
"""
    result = _vault_run(script)
    try:
        return json.loads(result.stdout)
    except Exception:
        return []


def hub_post_analysis(content: str) -> str:
    """Post ArchonPrime analysis to bus via vault-neo. Returns posted ID."""
    script = f"""\
import json, urllib.request
token = open('/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt').read().strip()
content = {json.dumps(content)}
payload = json.dumps({{
    'from': 'cc',
    'to': 'all',
    'type': 'inform',
    'urgency': 'informational',
    'content': '[ARCHONPRIME] ' + content
}}).encode()
req = urllib.request.Request(
    'https://hub.arknexus.net/v1/coordination/post',
    data=payload,
    headers={{'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}},
    method='POST'
)
with urllib.request.urlopen(req, timeout=15) as r:
    d = json.loads(r.read())
    print(d.get('id', '?'))
"""
    result = _vault_run(script, timeout=25)
    return result.stdout.strip() or f"(err: {result.stderr.strip()[:80]})"


def run_codex_on_k2(event_content: str, timeout: int = 120) -> str:
    """
    Write prompt to K2 via vault-neo, run codex exec, return analysis.
    vault-neo Python writes prompt file to K2, then invokes codex via SSH.
    """
    prompt = ARCHONPRIME_PROMPT_TMPL.format(event=event_content[:500])
    script = f"""\
import subprocess, json

prompt = {json.dumps(prompt)}

# Step 1: Write prompt to K2 temp file via stdin
r1 = subprocess.run(
    ['ssh', '-p', '2223', '-l', 'karma',
     '-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', 'localhost',
     'cat > /tmp/codex_ap_prompt.txt'],
    input=prompt, text=True, capture_output=True, timeout=10
)

# Step 2: Run codex on K2 reading from that file
r2 = subprocess.run(
    ['ssh', '-p', '2223', '-l', 'karma',
     '-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', 'localhost',
     'bash -i -c "cd /mnt/c/dev/Karma && '
     'codex exec --ephemeral --skip-git-repo-check '
     '-o /tmp/codex_ap_result.txt - < /tmp/codex_ap_prompt.txt '
     '2>/dev/null"; cat /tmp/codex_ap_result.txt'],
    capture_output=True, text=True, timeout={timeout - 15}
)
output = r2.stdout.strip()
# Strip bash noise lines
lines = [l for l in output.splitlines()
         if 'job control' not in l and 'process group' not in l]
print('\\n'.join(lines).strip())
"""
    result = _vault_run(script, timeout=timeout)
    output = result.stdout.strip()
    return output if output else f"(no output — stderr: {result.stderr.strip()[:200]})"


def is_structural(msg: dict) -> bool:
    if msg.get("type") == "structural":
        return True
    content = msg.get("content", "")
    return any(content.startswith(p) for p in STRUCTURAL_PREFIXES)


def main():
    token = get_token()
    if not token:
        print("[archonprime] ERROR: no HUB_CHAT_TOKEN")
        sys.exit(1)

    seen_ids: set = set()
    print(f"[archonprime] ArchonPrime Watcher online — polling every {POLL_SEC}s")

    while True:
        try:
            messages = hub_get()
            for msg in messages:
                msg_id = msg.get("id") or msg.get("timestamp") or str(msg)
                if msg_id in seen_ids:
                    continue
                seen_ids.add(msg_id)

                if "[ARCHONPRIME]" in msg.get("content", ""):
                    continue  # skip analysis posts

                if not is_structural(msg):
                    continue

                content = msg.get("content", "").strip()
                msg_from = msg.get("from", "unknown")
                print(f"[archonprime] Structural event from {msg_from}: {content[:80]}...")

                analysis = run_codex_on_k2(content)
                print(f"[archonprime] Codex returned ({len(analysis)} chars)")

                full = (f"Triggered by: {msg_from}\n"
                        f"Event: {content[:300]}\n\n"
                        f"Analysis:\n{analysis}")
                post_id = hub_post_analysis(full)
                print(f"[archonprime] PROOF-A: Analysis posted → {post_id}")

        except Exception as e:
            print(f"[archonprime] Error: {e}")

        time.sleep(POLL_SEC)


if __name__ == "__main__":
    main()
