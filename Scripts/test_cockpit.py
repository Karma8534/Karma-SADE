"""
Comprehensive test suite for Karma Cockpit service.
Tests every endpoint, edge case, and error path.
"""
import json
import os
import time
import urllib.request
import urllib.error
import sys
from pathlib import Path

BASE = "http://127.0.0.1:9400"
TOKEN_FILE = Path.home() / "karma" / "cockpit-token.txt"
PASS = 0
FAIL = 0
RESULTS = []


def _load_token() -> str:
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


_TOKEN = _load_token()
if not _TOKEN:
    print(f"[WARN] Cockpit token not found at {TOKEN_FILE}. Only /health will work.", file=sys.stderr)


def req(method, endpoint, data=None):
    """Make an HTTP request to the cockpit service."""
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
        with urllib.request.urlopen(r, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"error": e.reason}
        return e.code, body
    except Exception as e:
        return 0, {"error": str(e)}


def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        RESULTS.append(f"  [PASS] {name}")
    else:
        FAIL += 1
        RESULTS.append(f"  [FAIL] {name} — {detail}")


print("=" * 60)
print("Karma Cockpit — Test Suite")
print("=" * 60)

# ---------------------------------------------------------------
# 1. Health
# ---------------------------------------------------------------
print("\n--- 1. Health ---")
code, body = req("GET", "/health")
test("GET /health returns 200", code == 200)
test("Status is 'ok'", body.get("status") == "ok")
test("Service name correct", body.get("service") == "karma-cockpit")

# ---------------------------------------------------------------
# 2. Pinned tab exists
# ---------------------------------------------------------------
print("\n--- 2. Pinned Tab ---")
code, body = req("GET", "/tabs")
test("GET /tabs returns 200", code == 200)
tabs = body.get("tabs", [])
test("At least 1 tab exists", len(tabs) >= 1)
karma_tab = next((t for t in tabs if t["name"] == "_karma"), None)
test("_karma tab exists", karma_tab is not None)
if karma_tab:
    test("_karma is pinned", karma_tab.get("pinned") == True)
    test("_karma URL contains localhost:8080", "localhost:8080" in karma_tab.get("url", ""))

# ---------------------------------------------------------------
# 3. Open tab + auto-naming
# ---------------------------------------------------------------
print("\n--- 3. Open Tab ---")
code, body = req("POST", "/tab/open", {"url": "https://example.com"})
test("POST /tab/open returns 200", code == 200)
test("Tab auto-named 'example'", body.get("tab") == "example")

# Custom name
code, body = req("POST", "/tab/open", {"url": "https://httpbin.org/html", "name": "testpage"})
test("Custom name 'testpage' accepted", body.get("tab") == "testpage")

# Name collision
code, body = req("POST", "/tab/open", {"url": "https://example.com"})
test("Collision gets suffix", body.get("tab") == "example-2", f"got '{body.get('tab')}'")

# Missing URL
code, body = req("POST", "/tab/open", {})
test("Missing URL returns 400", code == 400)

# ---------------------------------------------------------------
# 4. List tabs (should have 4 now)
# ---------------------------------------------------------------
print("\n--- 4. List Tabs ---")
code, body = req("GET", "/tabs")
tabs = body.get("tabs", [])
tab_names = [t["name"] for t in tabs]
test("4 tabs open", len(tabs) == 4, f"got {len(tabs)}: {tab_names}")
test("All expected tabs present",
     all(n in tab_names for n in ["_karma", "example", "testpage", "example-2"]),
     f"got {tab_names}")

# ---------------------------------------------------------------
# 5. Read tab (raw)
# ---------------------------------------------------------------
print("\n--- 5. Read Tab (raw) ---")
code, body = req("POST", "/tab/read", {"tab": "example"})
test("Read returns 200", code == 200)
test("Has text content", len(body.get("text", "")) > 20)
test("Title is 'Example Domain'", body.get("title") == "Example Domain")
test("URL is correct", "example.com" in body.get("url", ""))

# Read nonexistent tab
code, body = req("POST", "/tab/read", {"tab": "nonexistent"})
test("Nonexistent tab returns 400", code == 400)

# Missing tab param
code, body = req("POST", "/tab/read", {})
test("Missing tab param returns 400", code == 400)

# ---------------------------------------------------------------
# 6. Read tab (Goose3 clean)
# ---------------------------------------------------------------
print("\n--- 6. Read Tab (Goose3 clean) ---")
code, body = req("POST", "/tab/read_clean", {"tab": "example"})
test("Clean read returns 200", code == 200)
test("Has extraction_method", body.get("extraction_method") in ("goose3", "fallback_raw"))
test("Has cleaned text", len(body.get("text", "")) > 10)
test("Has title", len(body.get("title", "")) > 0)

# ---------------------------------------------------------------
# 7. Links
# ---------------------------------------------------------------
print("\n--- 7. Links ---")
code, body = req("POST", "/tab/links", {"tab": "example"})
test("Links returns 200", code == 200)
links = body.get("links", [])
test("Found at least 1 link", len(links) >= 1, f"got {len(links)}")

# ---------------------------------------------------------------
# 8. Screenshot
# ---------------------------------------------------------------
print("\n--- 8. Screenshot ---")
code, body = req("POST", "/tab/screenshot", {"tab": "example"})
test("Screenshot returns 200", code == 200)
path = body.get("path", "")
test("Screenshot path exists", os.path.exists(path), f"path: {path}")
if os.path.exists(path):
    size = os.path.getsize(path)
    # Size varies depending on viewport and compression; just ensure it's non-trivial.
    test("Screenshot file > 1KB", size > 1000, f"size: {size}")
    os.remove(path)  # cleanup

# ---------------------------------------------------------------
# 9. Navigate tab
# ---------------------------------------------------------------
print("\n--- 9. Navigate ---")
code, body = req("POST", "/tab/navigate", {"tab": "testpage", "url": "https://example.com"})
test("Navigate returns 200", code == 200)

# Cannot navigate _karma
code, body = req("POST", "/tab/navigate", {"tab": "_karma", "url": "https://evil.com"})
test("Cannot navigate _karma", code == 400)

# Missing params
code, body = req("POST", "/tab/navigate", {"tab": "testpage"})
test("Missing url returns 400", code == 400)

# ---------------------------------------------------------------
# 10. Pinned tab protection
# ---------------------------------------------------------------
print("\n--- 10. Pinned Tab Protection ---")
code, body = req("POST", "/tab/close", {"tab": "_karma"})
test("Cannot close _karma", code == 400)

# In AUTONOMOUS_MODE, clicks execute immediately for normal tabs, but pinned tab actions are blocked.
code, body = req("POST", "/tab/click", {"tab": "_karma", "selector": "button"})
test("Click on _karma is blocked", code == 400)

# ---------------------------------------------------------------
# 11. Click behavior (autonomous)
# ---------------------------------------------------------------
print("\n--- 11. Click (Autonomous) ---")
code, body = req("POST", "/tab/click", {"tab": "example", "selector": "a"})
test("Click executes immediately (200)", code == 200)

# ---------------------------------------------------------------
# 12. Fill behavior (autonomous + approval for sensitive)
# ---------------------------------------------------------------
print("\n--- 12. Fill (Autonomous + Sensitive Approval) ---")

# Non-sensitive fill on a predictable form page
code, body = req("POST", "/tab/open", {"url": "https://httpbin.org/forms/post", "name": "form"})
test("Opened httpbin form tab", code == 200 and body.get("tab") == "form")
code, body = req("POST", "/tab/fill", {"tab": "form", "selector": "input[name='custname']", "text": "test"})
test("Non-sensitive fill executes immediately (200)", code == 200, f"got {code}: {body}")

# Sensitive fill should require approval (GitHub login has a password field)
code, body = req("POST", "/tab/open", {"url": "https://github.com/login", "name": "ghlogin"})
test("Opened GitHub login tab", code == 200 and body.get("tab") == "ghlogin")
code, body = req("POST", "/tab/fill", {"tab": "ghlogin", "selector": "input[name='password']", "text": "not-a-real-password"})
test("Sensitive fill returns approval (202)", code == 202)
test("Sensitive fill includes approval code", "code" in body)

# Cleanup extra tabs created in this section
for name in ["form", "ghlogin"]:
    req("POST", "/tab/close", {"tab": name})

# ---------------------------------------------------------------
# 13. Cockpit customization (CSS)
# ---------------------------------------------------------------
print("\n--- 13. Cockpit CSS Customization ---")
# Apply a style
code, body = req("POST", "/cockpit/style", {"css": "body { border: 1px solid red !important; }", "description": "test border"})
test("Style applied", code == 200 and body.get("applied") == True)
test("Rule count is 1", body.get("total_rules") == 1)

# Check theme
code, body = req("GET", "/cockpit/theme")
test("Theme has 1 rule", len(body.get("rules", [])) == 1)
test("Theme CSS contains test border", "red" in body.get("css", ""))

# Add second style (note: style endpoint replaces the theme; it does not append rules)
code, body = req("POST", "/cockpit/style", {"css": "h1 { color: blue; }", "description": "test heading"})
test("Second style applied (replace mode)", body.get("total_rules") == 1)
code, theme = req("GET", "/cockpit/theme")
test("Theme CSS contains second style", "blue" in theme.get("css", ""))
test("Theme CSS no longer contains first style", "red" not in theme.get("css", ""))

# Reset
code, body = req("POST", "/cockpit/reset")
test("Reset returns 200", code == 200 and body.get("reset") == True)

# Verify reset
code, body = req("GET", "/cockpit/theme")
test("Theme empty after reset", len(body.get("rules", [])) == 0)

# Missing CSS param
code, body = req("POST", "/cockpit/style", {"description": "no css"})
test("Missing css returns 400", code == 400)

# ---------------------------------------------------------------
# 14. Cockpit exec (JS)
# ---------------------------------------------------------------
print("\n--- 14. Cockpit JS Exec ---")
code, body = req("POST", "/cockpit/exec", {"js": "1 + 1", "description": "math test"})
test("Exec without code returns 202", code == 202)
exec_code = body.get("code", "")

code, body = req("POST", "/cockpit/exec", {"js": "1 + 1", "description": "math test", "confirm_code": exec_code})
test("Exec with code returns result", code == 200)
test("Result is '2'", body.get("result") == "2", f"got {body.get('result')}")

# ---------------------------------------------------------------
# 15. Reinject
# ---------------------------------------------------------------
print("\n--- 15. Reinject ---")
code, body = req("POST", "/cockpit/reinject")
test("Reinject returns 200", code == 200)

# ---------------------------------------------------------------
# 16. Close tabs (cleanup)
# ---------------------------------------------------------------
print("\n--- 16. Close Tabs ---")
for name in ["example", "example-2", "testpage"]:
    code, body = req("POST", "/tab/close", {"tab": name})
    test(f"Closed {name}", code == 200)

# Verify only _karma remains
code, body = req("GET", "/tabs")
tabs = body.get("tabs", [])
test("Only _karma tab remains", len(tabs) == 1 and tabs[0]["name"] == "_karma",
     f"remaining: {[t['name'] for t in tabs]}")

# ---------------------------------------------------------------
# 17. Theme file persistence
# ---------------------------------------------------------------
print("\n--- 17. Persistence ---")
theme_file = os.path.expanduser("~/karma/cockpit-theme.json")
test("Theme file exists on disk", os.path.exists(theme_file))

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print(f"RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print("=" * 60)
if FAIL > 0:
    print("\nFailed tests:")
    for r in RESULTS:
        if "[FAIL]" in r:
            print(r)
print()
