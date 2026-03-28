#!/usr/bin/env python3
"""
P0N-A: CC persistent server on P1.
Accepts POST /cc with JSON {message, session_id?}
Uses local Ollama for inference — Anthropic-independent, no MCP startup overhead (3-8s).
Returns: {response, ok}
Auth: Bearer token checked against HUB_CHAT_TOKEN env var.
"""
import os, json, sys, subprocess, pathlib, urllib.request, urllib.error, urllib.parse, socket, sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
sys.path.insert(0, os.path.dirname(__file__))
try:
    from cc_gmail import send_to_colby, check_inbox
    GMAIL_AVAILABLE = True
except Exception:
    GMAIL_AVAILABLE = False

PORT          = 7891
TOKEN         = os.environ.get("HUB_CHAT_TOKEN", "")
WORK_DIR      = r"C:\Users\raest\Documents\Karma_SADE"
SNAPSHOT_FILE = os.path.join(WORK_DIR, "cc_context_snapshot.md")
SESSION_FILE  = pathlib.Path.home() / ".cc_server_session_id"
# Bypass .cmd wrapper — call node + cli.js directly (avoids PATH issues in background processes)
NODE_EXE       = r"C:\Program Files\nodejs\node.exe"
CLAUDE_CLI_JS  = r"C:\Users\raest\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\cli.js"
API_TIMEOUT    = 120  # seconds — CC subprocess can be slow on complex tasks
CLAUDEMEM_URL  = "http://127.0.0.1:37777"  # claude-mem worker (loopback)
CLAUDEMEM_DB   = pathlib.Path.home() / ".claude-mem" / "claude-mem.db"

def claudemem_proxy(path, method="GET", body=None, timeout=10):
    """Proxy a request to the local claude-mem worker at 127.0.0.1:37777."""
    if method == "GET" and body:
        # /api/search is GET-only — convert body dict to query string
        url = f"{CLAUDEMEM_URL}{path}?{urllib.parse.urlencode(body)}"
        data = None
    else:
        url = f"{CLAUDEMEM_URL}{path}"
        data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {"error": str(e)}
    except Exception as e:
        return 503, {"error": f"claude-mem unavailable: {str(e)}"}


def load_session_id():
    """Load persisted session ID for --resume continuity."""
    try:
        return SESSION_FILE.read_text().strip() if SESSION_FILE.exists() else None
    except Exception:
        return None

def save_session_id(session_id):
    """Persist session ID for next call."""
    try:
        SESSION_FILE.write_text(session_id)
    except Exception as e:
        print(f"[cc-server] WARNING: could not save session ID: {e}")

def run_cc(message, effort=None):
    """Call real CC subprocess with --resume for session continuity."""
    session_id = load_session_id()
    # Use node.exe + cli.js directly — bypasses .cmd wrapper (avoids WinError 2 / subprocess issues on Windows)
    cmd = [NODE_EXE, CLAUDE_CLI_JS, "-p", message, "--output-format", "json"]
    if session_id:
        cmd += ["--resume", session_id]
    if effort and effort in ("low", "medium", "high", "max"):
        cmd += ["--effort", effort]
    result = subprocess.run(
        cmd,
        capture_output=True, text=True,
        cwd=WORK_DIR,
        timeout=API_TIMEOUT,
    )
    if result.returncode != 0:
        # stderr may contain useful info
        err_detail = (result.stderr or "").strip()[:300]
        raise RuntimeError(f"claude exit {result.returncode}: {err_detail}")
    # Parse JSON output
    stdout = result.stdout.strip()
    # --output-format json outputs one JSON object; there may be warning lines before it
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                d = json.loads(line)
                if d.get("type") == "result":
                    new_session_id = d.get("session_id", "")
                    if new_session_id:
                        save_session_id(new_session_id)
                    return d.get("result", "").strip()
            except json.JSONDecodeError:
                continue
    # Fallback: return raw stdout if no JSON found
    return stdout

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
        elif self.path == "/memory/health":
            self._json(200, {"ok": True, "service": "cc-server-p1", "claudemem_url": CLAUDEMEM_URL})
        elif self.path.startswith("/memory/session"):
            session_id = load_session_id()
            self._json(200, {"ok": True, "session_id": session_id or ""})
        elif self.path.startswith("/file"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            rel = params.get("path", [""])[0].strip()
            if not rel:
                self._json(400, {"ok": False, "error": "path param required"})
                return
            # Scope: resolve within WORK_DIR, block traversal
            target = os.path.normpath(os.path.join(WORK_DIR, rel))
            if not target.startswith(WORK_DIR):
                self._json(403, {"ok": False, "error": "path outside project"})
                return
            try:
                with open(target, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(40960)  # 40KB cap
                self._json(200, {"ok": True, "path": rel, "content": content, "size": os.path.getsize(target)})
            except FileNotFoundError:
                self._json(404, {"ok": False, "error": f"not found: {rel}"})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
        elif self.path.startswith("/memory/observations"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            raw_ids = params.get("ids", [""])[0]
            ids = [int(x.strip()) for x in raw_ids.split(",") if x.strip().isdigit()]
            if not ids:
                self._json(400, {"ok": False, "error": "ids param required (comma-separated ints)"})
                return
            try:
                conn = sqlite3.connect(f"file:{CLAUDEMEM_DB}?mode=ro", uri=True, timeout=5)
                conn.row_factory = sqlite3.Row
                placeholders = ",".join("?" * len(ids))
                rows = conn.execute(
                    f"SELECT id,memory_session_id,project,type,title,subtitle,narrative,text,created_at FROM observations WHERE id IN ({placeholders})",
                    ids
                ).fetchall()
                conn.close()
                items = [dict(r) for r in rows]
                self._json(200, {"ok": True, "items": items})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self._auth_ok():
            self._json(401, {"ok": False, "error": "Unauthorized"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        # ── /file — project-scoped file write ─────────────────────────────
        if self.path == "/file":
            rel = body.get("path", "").strip()
            content = body.get("content", "")
            if not rel:
                self._json(422, {"ok": False, "error": "path required"})
                return
            target = os.path.normpath(os.path.join(WORK_DIR, rel))
            if not target.startswith(WORK_DIR):
                self._json(403, {"ok": False, "error": "path outside project"})
                return
            try:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content)
                self._json(200, {"ok": True, "path": rel, "bytes_written": len(content.encode("utf-8"))})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
            return

        # ── /memory/search — proxy to claude-mem ──────────────────────────
        if self.path == "/memory/search":
            code, payload = claudemem_proxy("/api/search", "GET", body, timeout=5)
            self._json(code, payload)
            return

        # ── /memory/save — proxy to claude-mem ────────────────────────────
        if self.path == "/memory/save":
            code, payload = claudemem_proxy("/api/memory/save", "POST", body, timeout=5)
            self._json(code, payload)
            return

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

        # Call real CC subprocess with --resume for session continuity
        effort = body.get("effort")
        try:
            response_text = run_cc(message, effort=effort)
            self._json(200, {"ok": True, "response": response_text})
        except subprocess.TimeoutExpired:
            self._json(504, {"ok": False, "error": f"CC subprocess timed out after {API_TIMEOUT}s"})
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)})

if __name__ == "__main__":
    print(f"[cc-server] Starting on port {PORT}")
    print(f"[cc-server] Auth: {'ENABLED' if TOKEN else 'DISABLED (set HUB_CHAT_TOKEN)'}")
    print(f"[cc-server] Inference: CC subprocess (claude -p --resume) — real CC with session continuity")
    print(f"[cc-server] Session file: {SESSION_FILE}")
    server = HTTPServer(("0.0.0.0", PORT), CCHandler)
    server.serve_forever()
