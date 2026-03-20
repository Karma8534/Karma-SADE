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
WORK_DIR  = r"C:\Users\raest\Documents\Karma_SADE"
TIMEOUT   = 300  # 5 min — MCP startup + full response

# Identity injected into every subprocess so it knows it's CC Ascendant
CC_SYSTEM_PROMPT = (
    "You are CC (Ascendant rank, Karma SADE hierarchy). "
    "Colby is Sovereign. This is a direct message via hub.arknexus.net/cc (P0N-A channel). "
    "All project files are available: read .gsd/STATE.md for current state, MEMORY.md for session history. "
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

        # Run claude — continue most recent session with CC identity
        try:
            cmd = [
                CLAUDE_CMD,
                "-p", message,
                "--system-prompt", CC_SYSTEM_PROMPT,  # assert CC Ascendant identity
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
