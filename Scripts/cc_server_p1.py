#!/usr/bin/env python3
"""
P0N-A: CC persistent server on P1.
Accepts POST /cc with JSON {message, session_id?}
Runs: claude -p "message" --continue (resumes most recent session in project dir)
Returns: {response, ok, exit_code}
Auth: Bearer token checked against HUB_CHAT_TOKEN env var.
"""
import os, subprocess, json, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
sys.path.insert(0, os.path.dirname(__file__))
try:
    from cc_gmail import send_to_colby, check_inbox
    GMAIL_AVAILABLE = True
except Exception:
    GMAIL_AVAILABLE = False

PORT      = 7891
TOKEN     = os.environ.get("HUB_CHAT_TOKEN", "")
CLAUDE_CMD = os.environ.get("CLAUDE_CMD", r"C:\Users\raest\AppData\Roaming\npm\claude.cmd")
WORK_DIR      = r"C:\Users\raest\Documents\Karma_SADE"
SNAPSHOT_FILE = os.path.join(WORK_DIR, "cc_context_snapshot.md")
TIMEOUT       = 300  # 5 min — MCP startup + full response

def load_snapshot():
    """Load cc_context_snapshot.md written by wrap-session/resurrect. Falls back to base identity."""
    try:
        with open(SNAPSHOT_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

# Base identity — always present. Snapshot (from wrap-session) appended when available.
CC_IDENTITY_BASE = (
    "You are CC (Ascendant rank, Karma SADE hierarchy). "
    "Colby is Sovereign. This message arrives via hub.arknexus.net/cc (P0N-A channel). "
    "All project files are in C:\\Users\\raest\\Documents\\Karma_SADE — read .gsd/STATE.md and MEMORY.md for current state. "
    "claude-mem MCP is active. CLAUDE.md is your operating contract. "
    "Respond as CC Ascendant — concise, verified, no padding. Mobile interface."
)

class CCHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[cc-server] {format % args}")

    def _json(self, code, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def _auth_ok(self):
        auth = self.headers.get("Authorization", "")
        return (not TOKEN) or (auth == f"Bearer {TOKEN}")

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"ok": True, "service": "cc-server-p1", "gmail": GMAIL_AVAILABLE})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self._auth_ok():
            self._json(401, {"ok": False, "error": "Unauthorized"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        # ── /email/send — CC sends email to Colby ──────────────────────────
        if self.path == "/email/send":
            if not GMAIL_AVAILABLE:
                self._json(503, {"ok": False, "error": "Gmail not available (cc_gmail.py missing or creds unreadable)"})
                return
            subject = body.get("subject", "(no subject)")
            msg_body = body.get("body", "")
            if not msg_body:
                self._json(422, {"ok": False, "error": "body required"})
                return
            result = send_to_colby(subject, msg_body)
            self._json(200 if result["ok"] else 500, result)
            return

        # ── /email/inbox — check CC inbox ──────────────────────────────────
        if self.path == "/email/inbox":
            if not GMAIL_AVAILABLE:
                self._json(503, {"ok": False, "error": "Gmail not available"})
                return
            limit = int(body.get("limit", 10))
            msgs = check_inbox(limit)
            self._json(200, {"ok": True, "messages": msgs})
            return

        if self.path != "/cc":
            self.send_response(404)
            self.end_headers()
            return

        message = body.get("message", "")
        if not message:
            self.send_response(422)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "message required"}).encode())
            return

        # Run claude — inject identity + current session snapshot
        try:
            snapshot = load_snapshot()
            system_prompt = CC_IDENTITY_BASE + ("\n\n[CURRENT SESSION CONTEXT]\n" + snapshot if snapshot else "")
            cmd = [
                CLAUDE_CMD,
                "-p", message,
                "--system-prompt", system_prompt,  # CC Ascendant identity + session context
            ]
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=TIMEOUT,
                cwd=WORK_DIR
            )
            response_text = (result.stdout or "").strip() or (result.stderr or "").strip() or "(no output)"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": True,
                "response": response_text,
                "exit_code": result.returncode
            }).encode())
        except subprocess.TimeoutExpired:
            self.send_response(504)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": f"Claude timeout ({TIMEOUT}s)"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())

if __name__ == "__main__":
    print(f"[cc-server] Starting on port {PORT}")
    print(f"[cc-server] Auth: {'ENABLED' if TOKEN else 'DISABLED (set HUB_CHAT_TOKEN)'}")
    print(f"[cc-server] Mode: --continue (resumes most recent session) + identity assertion")
    server = HTTPServer(("0.0.0.0", PORT), CCHandler)
    server.serve_forever()
