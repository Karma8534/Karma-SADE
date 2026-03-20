#!/usr/bin/env python3
"""
P0N-A: CC persistent server on P1.
Accepts POST /cc with JSON {message, session_id?}
Runs: claude -p "message" --continue (resumes most recent session in project dir)
Returns: {response, ok, exit_code}
Auth: Bearer token checked against HUB_CHAT_TOKEN env var.
"""
import os, subprocess, json
from http.server import HTTPServer, BaseHTTPRequestHandler

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

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "service": "cc-server-p1"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        # Auth check
        auth = self.headers.get("Authorization", "")
        if TOKEN and auth != f"Bearer {TOKEN}":
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "Unauthorized"}).encode())
            return

        if self.path != "/cc":
            self.send_response(404)
            self.end_headers()
            return

        # Read body
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
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
                "--system-prompt", system_prompt,  # assert CC Ascendant identity + session context
                "--dangerously-skip-permissions",      # no interactive prompts in subprocess
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
