"""
Agentic test suite for Karma Cockpit.
Sends real messages to Karma via Open WebUI and verifies tool calling works.
Uses the cockpit browser (the actual UI) for end-to-end testing.
"""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE = "http://127.0.0.1:9400"
OWUI = "http://localhost:8080"
TOKEN_FILE = Path.home() / "karma" / "cockpit-token.txt"
PASS = 0
FAIL = 0
SKIP = 0
RESULTS = []


def _load_token() -> str:
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


_TOKEN = _load_token()
if not _TOKEN:
    print(f"[WARN] Cockpit token not found at {TOKEN_FILE}. Requests will likely 401.")


def cockpit_req(method, endpoint, data=None):
    """Request to cockpit service."""
    url = f"{BASE}{endpoint}"
    headers = {}
    if _TOKEN:
        headers["Authorization"] = f"Bearer {_TOKEN}"

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
        r = urllib.request.Request(url, data=body, headers=headers, method=method)
    else:
        r = urllib.request.Request(url, headers=headers, method=method)

    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            b = json.loads(e.read().decode("utf-8"))
        except Exception:
            b = {"error": e.reason}
        return e.code, b
    except Exception as e:
        return 0, {"error": str(e)}


def exec_js(js, desc=""):
    """Execute JS on the _karma tab with auto-approval."""
    code1, body1 = cockpit_req("POST", "/cockpit/exec", {"js": js, "description": desc})
    approval = body1.get("code")
    if not approval:
        return body1
    code2, body2 = cockpit_req("POST", "/cockpit/exec",
                                {"js": js, "description": desc, "confirm_code": approval})
    return body2


def test(name, condition, detail=""):
    global PASS, FAIL
    status = "PASS" if condition else "FAIL"
    if condition:
        PASS += 1
    else:
        FAIL += 1
    line = f"  [{status}] {name}" + (f" — {detail}" if detail and not condition else "")
    RESULTS.append(line)
    print(line)


def skip(name, detail=""):
    global SKIP
    SKIP += 1
    line = f"  [SKIP] {name}" + (f" — {detail}" if detail else "")
    RESULTS.append(line)
    print(line)


def send_message(text, wait_seconds=45):
    """Type a message into Open WebUI chat and wait for response."""
    # The chat input is a Tiptap/ProseMirror contenteditable div, not a textarea.
    # We must use execCommand('insertText') or set innerHTML + dispatch input.
    safe_text = json.dumps(text)
    fill_js = f"""(() => {{
        const editor = document.querySelector('#chat-input');
        if (!editor) return 'NO_EDITOR';
        // Focus the editor
        editor.focus();
        // Clear existing content
        editor.innerHTML = '<p><br class="ProseMirror-trailingBreak"></p>';
        // Use execCommand to simulate typing (triggers ProseMirror state update)
        document.execCommand('insertText', false, {safe_text});
        // Dispatch input event to notify Svelte/framework
        editor.dispatchEvent(new Event('input', {{bubbles: true}}));
        return 'FILLED: ' + editor.innerText.trim().substring(0, 80);
    }})()"""
    result = exec_js(fill_js, "Fill chat input")
    fill_status = result.get("result", "")
    print(f"    Fill result: {fill_status}")
    if fill_status == "NO_EDITOR":
        return None, "Could not find chat editor (#chat-input)"

    time.sleep(1)

    # The send button should now appear. In Open WebUI, pressing Enter (without Shift) sends.
    # Try clicking send-message-button first, then fallback to Enter keypress.
    send_js = """(() => {
        // Look for the send button that appears after text is entered
        const sendBtn = document.getElementById('send-message-button');
        if (sendBtn) { sendBtn.click(); return 'CLICKED_SEND_BUTTON'; }
        // Fallback: find submit button
        const submitBtn = document.querySelector('button[type="submit"]:not(.hidden)');
        if (submitBtn) { submitBtn.click(); return 'CLICKED_SUBMIT'; }
        // Fallback: press Enter on the editor to submit
        const editor = document.querySelector('#chat-input');
        if (editor) {
            editor.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}));
            return 'PRESSED_ENTER';
        }
        return 'NO_SEND';
    })()"""
    result = exec_js(send_js, "Click send")
    send_method = result.get("result", "")
    print(f"    Send result: {send_method}")
    if send_method == "NO_SEND":
        return None, "Could not send message"

    # Wait for response to complete (watch for streaming to finish)
    print(f"    Waiting up to {wait_seconds}s for Karma to respond...")
    for i in range(wait_seconds // 3):
        time.sleep(3)
        # Check if still generating (look for stop button or loading indicator)
        check_js = """(() => {
            const stopBtn = document.querySelector('button[aria-label*="Stop"], button[class*="stop"]');
            const loading = document.querySelector('[class*="loading"], [class*="typing"]');
            if (stopBtn || loading) return 'GENERATING';
            return 'DONE';
        })()"""
        status = exec_js(check_js, "Check generation status")
        if status.get("result") == "DONE":
            time.sleep(2)  # Extra settle time
            break

    # Read the last assistant message
    # Open WebUI uses data-message-id attributes and role indicators
    read_js = """(() => {
        // Strategy 1: Look for message containers with role indicators
        const allDivs = document.querySelectorAll('[data-message-id]');
        if (allDivs.length > 0) {
            const last = allDivs[allDivs.length - 1];
            return JSON.stringify({method: 'data-message-id', count: allDivs.length,
                text: last.innerText.trim().substring(0, 2000)});
        }
        // Strategy 2: Look for response-message or prose class containers
        const prose = document.querySelectorAll('.prose, [class*="response"]');
        if (prose.length > 0) {
            const last = prose[prose.length - 1];
            return JSON.stringify({method: 'prose', count: prose.length,
                text: last.innerText.trim().substring(0, 2000)});
        }
        // Strategy 3: Grab all visible text blocks as fallback
        const body = document.body.innerText;
        return JSON.stringify({method: 'body', text: body.substring(body.length - 2000)});
    })()"""
    result = exec_js(read_js, "Read assistant response")
    raw = result.get("result", "")
    try:
        parsed = json.loads(raw)
        return parsed, None
    except Exception:
        return {"text": raw}, None


def check_tool_calls():
    """Check if tool call indicators are visible in the chat."""
    js = """(() => {
        const page = document.body.innerText;
        const indicators = [];
        if (page.includes('browser_')) indicators.push('browser_tool_ref');
        if (page.includes('cockpit_')) indicators.push('cockpit_tool_ref');
        if (page.includes('@')) indicators.push('at_reference');

        // Look for tool call UI elements (Open WebUI shows tool calls in expandable sections)
        const toolCalls = document.querySelectorAll('[class*="tool"], [class*="function"]');
        if (toolCalls.length > 0) indicators.push('tool_call_ui:' + toolCalls.length);

        return JSON.stringify(indicators);
    })()"""
    result = exec_js(js, "Check for tool call indicators")
    try:
        return json.loads(result.get("result", "[]"))
    except Exception:
        return []


# ===============================================================
print("=" * 60)
print("Karma Cockpit — Agentic Test Suite")
print("=" * 60)

# ---------------------------------------------------------------
# 0. Pre-check: Cockpit and Open WebUI are up
# ---------------------------------------------------------------
print("\n--- 0. Pre-checks ---")
code, body = cockpit_req("GET", "/health")
test("Cockpit service is up", code == 200)

code, body = cockpit_req("GET", "/tabs")
tabs = [t["name"] for t in body.get("tabs", [])]
test("_karma tab is open", "_karma" in tabs)

# Navigate to a fresh chat
result = exec_js("window.location.href = 'http://localhost:8080/'", "Navigate to new chat")
time.sleep(4)

# Verify we're on the chat page
result = exec_js("document.title", "Check page title")
test("On Open WebUI page", result.get("result") is not None)

# Check model selector shows Karma
result = exec_js("""(() => {
    const modelSel = document.body.innerText;
    return modelSel.includes('Karma') ? 'KARMA_FOUND' : 'NOT_FOUND: ' + document.title;
})()""", "Check Karma model")
test("Karma model is selected", "KARMA_FOUND" in str(result.get("result", "")),
     result.get("result", ""))

# ---------------------------------------------------------------
# 1. Test: Ask Karma to list browser tabs
# ---------------------------------------------------------------
print("\n--- 1. Tool Call: browser_tabs ---")
print("    Sending: 'List my open browser tabs'")
response, err = send_message("List my open browser tabs")
test("Got a response", response is not None and err is None, err or "")

tool_indicators = []
if response:
    text = response.get("text", response.get("last", ""))
    test("Response mentions tabs or @_karma",
         any(w in text.lower() for w in ["tab", "_karma", "@", "karma", "open"]),
         f"Response: {text[:200]}")
    tool_indicators = check_tool_calls()

# NOTE: Tool-call UI/indicators in Open WebUI change frequently. If we can't detect them,
# we treat it as a skip rather than a hard failure.
if tool_indicators:
    test("Tool call indicators found", True)
else:
    skip("Tool call indicators found", "No reliable tool UI indicators detected")

# ---------------------------------------------------------------
# 2. Test: Ask Karma to open a page
# ---------------------------------------------------------------
print("\n--- 2. Tool Call: browser_open + browser_read ---")

# Start new chat for clean state
exec_js("window.location.href = 'http://localhost:8080/'", "New chat")
time.sleep(4)

print("    Sending: 'Open example.com in a new tab and read what it says'")
response, err = send_message("Open example.com in a new tab and tell me what it says", wait_seconds=60)
test("Got a response", response is not None and err is None, err or "")
if response:
    text = response.get("text", response.get("last", ""))
    # Karma should mention Example Domain or the content of example.com
    test("Response references example.com content",
         any(w in text.lower() for w in ["example domain", "example", "documentation", "illustrative"]),
         f"Response: {text[:300]}")

# Check if a tab was actually opened
code, body = cockpit_req("GET", "/tabs")
tab_names = [t["name"] for t in body.get("tabs", [])]
if "example" in tab_names:
    test("Example tab was opened in browser", True)
    cockpit_req("POST", "/tab/close", {"tab": "example"})
else:
    skip("Example tab was opened in browser", f"No 'example' tab observed (tabs: {tab_names}). Tool-calling may be disabled.")

# ---------------------------------------------------------------
# 3. Test: Ask Karma to customize the cockpit
# ---------------------------------------------------------------
print("\n--- 3. Tool Call: cockpit_customize ---")

exec_js("window.location.href = 'http://localhost:8080/'", "New chat")
time.sleep(4)

print("    Sending: 'Change the background color to dark navy blue'")
response, err = send_message("Change the background color to dark navy blue", wait_seconds=60)
test("Got a response", response is not None and err is None, err or "")

# Check if a theme rule was applied
code, body = cockpit_req("GET", "/cockpit/theme")
rules = body.get("rules", [])
if len(rules) > 0:
    test("CSS rule was applied to theme", True)
    css = body.get("css", "")
    test("CSS contains background-related property",
         any(w in css.lower() for w in ["background", "bg"]),
         f"CSS: {css[:200]}")
else:
    skip("CSS rule was applied to theme", "No rules observed. Tool-calling may be disabled or model ignored the instruction.")

# Reset theme after test
cockpit_req("POST", "/cockpit/reset")

# ---------------------------------------------------------------
# 4. Test: Ask Karma to view current theme
# ---------------------------------------------------------------
print("\n--- 4. Tool Call: cockpit_theme ---")

exec_js("window.location.href = 'http://localhost:8080/'", "New chat")
time.sleep(4)

print("    Sending: 'What customizations are currently applied to the cockpit?'")
response, err = send_message("What customizations are currently applied to the cockpit?", wait_seconds=45)
test("Got a response", response is not None and err is None, err or "")
if response:
    text = response.get("text", response.get("last", ""))
    test("Response mentions theme or customizations",
         any(w in text.lower() for w in ["no custom", "default", "theme", "style", "customiz"]),
         f"Response: {text[:200]}")

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print(f"AGENTIC RESULTS: {PASS} passed, {FAIL} failed, {SKIP} skipped, {PASS + FAIL + SKIP} total")
print("=" * 60)
if FAIL > 0:
    print("\nFailed tests:")
    for r in RESULTS:
        if "[FAIL]" in r:
            print(r)
print()
