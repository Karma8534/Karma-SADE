#!/usr/bin/env python3
"""karma_approval_watcher.py — Task 0: Sovereign approval gate.

Polls coordination bus for CC "TASK [N] COMPLETE" posts.
Sends proof to Karma via /v1/chat for audit.
Posts Karma's approval/redirect back to bus.
Deployed via Kiki as persistent watcher on K2.
"""
import json, time, re, urllib.request, urllib.error, sys, os

HUB_URL = "https://hub.arknexus.net"
POLL_INTERVAL = 30  # seconds
RETRY_DELAY = 60    # seconds before retry on failure
SEEN_FILE = "/tmp/karma_watcher_seen.json"

def _get_token():
    """Read hub chat token from multiple sources."""
    # 1. Direct file (vault-neo)
    try:
        with open("/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt", "r") as f:
            return f.read().strip()
    except Exception:
        pass
    # 2. K2 env file
    try:
        with open("/mnt/c/dev/Karma/k2/aria/.watcher.env", "r") as f:
            for line in f:
                if line.startswith("HUB_CHAT_TOKEN="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    # 3. Environment variable
    return os.environ.get("HUB_CHAT_TOKEN", "")

TOKEN = _get_token()

def _load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()

def _save_seen(seen):
    try:
        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen), f)
    except Exception:
        pass

def _api(method, path, body=None):
    """Make an API call to hub.arknexus.net."""
    url = f"{HUB_URL}{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}", "body": e.read().decode()[:500]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def poll_bus():
    """Check bus for TASK [N] COMPLETE posts from CC."""
    result = _api("GET", "/v1/coordination/recent?limit=20")
    if not result.get("ok"):
        return []

    entries = result.get("entries", [])
    found = []
    for entry in entries:
        if entry.get("from") != "cc":
            continue
        content = entry.get("content", "")
        match = re.search(r"TASK\s+(\d+)\s+COMPLETE", content)
        if match:
            task_num = int(match.group(1))
            found.append({
                "task_num": task_num,
                "entry_id": entry.get("id", ""),
                "content": content,
            })
    return found

def send_to_karma(task_num, proof_text):
    """Send audit request to Karma via /v1/chat."""
    message = (
        f"KARMA AUDIT REQUIRED\n"
        f"Task: {task_num}\n"
        f"Proof: {proof_text[:3000]}\n"
        f"Approve or redirect?"
    )
    result = _api("POST", "/v1/chat", {
        "message": message,
        "stream": False,
        "session_id": "karma-watcher-audit",
    })
    return result

def extract_karma_decision(response_text, task_num):
    """Parse Karma's response for approval or redirect."""
    if f"[KARMA APPROVE Task {task_num}]" in response_text:
        return "approve", response_text
    if f"[KARMA REDIRECT Task {task_num}]" in response_text:
        return "redirect", response_text
    # Check for looser matches
    text_lower = response_text.lower()
    if "approve" in text_lower and f"task {task_num}" in text_lower:
        return "approve", response_text
    if "redirect" in text_lower or "reject" in text_lower:
        return "redirect", response_text
    return "unclear", response_text

def post_to_bus(content):
    """Post result back to coordination bus."""
    return _api("POST", "/v1/coordination/post", {
        "from": "karma-watcher",
        "to": "cc",
        "type": "response",
        "urgency": "operational",
        "content": content,
    })

def process_task(task):
    """Full audit cycle for one task."""
    task_num = task["task_num"]
    proof = task["content"]
    print(f"[watcher] Processing TASK {task_num} COMPLETE")

    # Send to Karma for audit
    result = send_to_karma(task_num, proof)

    if not result.get("ok"):
        # Retry once after 60s
        print(f"[watcher] Karma unreachable, retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
        result = send_to_karma(task_num, proof)

        if not result.get("ok"):
            # Escalate to Sovereign
            escalation = (
                f"WATCHER ESCALATION: Karma unreachable, Task {task_num} "
                f"awaiting Sovereign review.\n"
                f"Error: {result.get('error', 'unknown')}\n"
                f"Proof: {proof[:1000]}"
            )
            post_to_bus(escalation)
            print(f"[watcher] ESCALATED Task {task_num} — Karma unreachable")
            return

    # Extract Karma's response
    response_text = (
        result.get("assistant_text") or
        result.get("response") or
        result.get("content") or
        ""
    )
    decision, full_response = extract_karma_decision(response_text, task_num)

    if decision == "approve":
        bus_content = (
            f"[KARMA APPROVE Task {task_num}]\n"
            f"Karma response: {full_response[:1000]}"
        )
        post_to_bus(bus_content)
        print(f"[watcher] Task {task_num} APPROVED by Karma")
    elif decision == "redirect":
        bus_content = (
            f"[KARMA REDIRECT Task {task_num}]\n"
            f"Karma response: {full_response[:1000]}"
        )
        post_to_bus(bus_content)
        print(f"[watcher] Task {task_num} REDIRECTED by Karma")
    else:
        bus_content = (
            f"WATCHER: Karma responded to Task {task_num} but decision unclear.\n"
            f"Response: {full_response[:1000]}\n"
            f"Awaiting Sovereign clarification."
        )
        post_to_bus(bus_content)
        print(f"[watcher] Task {task_num} — unclear response, escalated")

def run():
    """Main polling loop."""
    print(f"[watcher] Starting karma_approval_watcher")
    print(f"[watcher] Hub: {HUB_URL}")
    print(f"[watcher] Poll interval: {POLL_INTERVAL}s")
    print(f"[watcher] Token: {'SET' if TOKEN else 'MISSING'}")

    seen = _load_seen()

    while True:
        try:
            tasks = poll_bus()
            for task in tasks:
                task_key = f"task_{task['task_num']}_{task['entry_id']}"
                if task_key in seen:
                    continue
                process_task(task)
                seen.add(task_key)
                _save_seen(seen)
        except Exception as e:
            print(f"[watcher] Error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    if "--test" in sys.argv:
        # Quick self-test
        print(f"Token: {'SET' if TOKEN else 'MISSING'}")
        tasks = poll_bus()
        print(f"Found {len(tasks)} TASK COMPLETE entries on bus")
        for t in tasks:
            print(f"  Task {t['task_num']}: {t['content'][:80]}")
        print("PASS")
        sys.exit(0)
    run()
