#!/usr/bin/env python3
"""
P0N-A: CC persistent server on P1.
Accepts POST /cc with JSON {message, session_id?}
Runs: claude -p "message" --resume
Returns: {response, session_id, ok}
Auth: Bearer token checked against HUB_CHAT_TOKEN env var.
"""
import os, subprocess, json
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 7891
TOKEN = os.environ.get("HUB_CHAT_TOKEN", "")

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

        # Run claude
        try:
            result = subprocess.run(
                ["claude", "-p", message, "--resume"],
                capture_output=True, text=True, timeout=120,
                cwd="C:\\Users\\raest\\Documents\\Karma_SADE"
            )
            response_text = result.stdout.strip() or result.stderr.strip() or "(no output)"
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
            self.wfile.write(json.dumps({"ok": False, "error": "Claude timeout (120s)"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())

if __name__ == "__main__":
    print(f"[cc-server] Starting on port {PORT}")
    print(f"[cc-server] Auth: {'ENABLED' if TOKEN else 'DISABLED (set HUB_CHAT_TOKEN)'}")
    server = HTTPServer(("0.0.0.0", PORT), CCHandler)
    server.serve_forever()
