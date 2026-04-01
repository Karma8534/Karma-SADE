#!/usr/bin/env python3
"""
P0N-A: CC persistent server on P1.
Accepts POST /cc with JSON {message, session_id?}
Uses local Ollama for inference — Anthropic-independent, no MCP startup overhead (3-8s).
Returns: {response, ok}
Auth: Bearer token checked against HUB_CHAT_TOKEN env var.
"""
import os, json, sys, subprocess, pathlib, urllib.request, urllib.error, urllib.parse, socket, sqlite3, base64, threading, time
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
try:
    from cc_gmail import send_to_colby, check_inbox
    GMAIL_AVAILABLE = True
except Exception:
    GMAIL_AVAILABLE = False

# ── Hooks Engine (Sprint 3a) ─────────────────────────────────────────────────
try:
    from Scripts.hooks_engine import HooksService, HookDef
    from Scripts.hooks.cost_warning import handle as cost_warning_handle, reset as cost_warning_reset
    from Scripts.hooks.memory_extractor import handle as memory_extractor_handle
    from Scripts.hooks.skill_activation import handle as skill_activation_handle
    from Scripts.hooks.compiler_in_loop import handle as compiler_in_loop_handle
    from Scripts.hooks.auto_handoff_stop import handle as auto_handoff_handle
    from Scripts.hooks.pre_tool_security import handle as pre_tool_security_handle
    from Scripts.hooks.fact_extractor import handle as fact_extractor_handle
    from Scripts.hooks.conversation_capture import handle as conversation_capture_handle

    _hooks = HooksService()
    _hooks.register(HookDef("skill_activation", "UserPromptSubmit", "True", skill_activation_handle, 3000))
    _hooks.register(HookDef("pre_tool_security", "PreToolUse", "True", pre_tool_security_handle, 1000))
    _hooks.register(HookDef("fact_extractor", "PostToolUse", "True", fact_extractor_handle, 3000))
    _hooks.register(HookDef("compiler_in_loop", "PostToolUse", "tool_name in [Edit, Write]", compiler_in_loop_handle, 10000))
    _hooks.register(HookDef("cost_warning", "PostToolUse", "True", cost_warning_handle, 1000))
    _hooks.register(HookDef("memory_extractor", "Stop,SessionEnd", "True", memory_extractor_handle, 5000))
    _hooks.register(HookDef("auto_handoff", "Stop", "True", auto_handoff_handle, 5000))
    _hooks.register(HookDef("conversation_capture", "Stop", "True", conversation_capture_handle, 3000))
    HOOKS_AVAILABLE = True
    print("[cc-server] Hooks engine: 8 handlers registered")
except Exception as e:
    _hooks = None
    HOOKS_AVAILABLE = False
    print(f"[cc-server] Hooks engine: DISABLED ({e})")

# ── SmartRouter (Sprint 3c) ──────────────────────────────────────────────────
try:
    from Scripts.smart_router import SmartRouter
    _router = SmartRouter()
    ROUTER_AVAILABLE = True
    print(f"[cc-server] SmartRouter: {len(_router.providers)} providers")
except Exception as e:
    _router = None
    ROUTER_AVAILABLE = False
    print(f"[cc-server] SmartRouter: DISABLED ({e})")

PORT          = 7891
_current_proc = None  # Track running CC subprocess for cancel
_proc_lock    = threading.Lock()  # Concurrency guard — one CC subprocess at a time
TOKEN         = os.environ.get("HUB_CHAT_TOKEN", "")

# H3: Rate limiting — per-IP sliding window
_rate_buckets = defaultdict(list)  # ip -> [timestamps]
RATE_LIMIT_RPM = 20  # requests per minute per IP
RATE_LIMIT_WINDOW = 60  # seconds

def _check_rate_limit(ip):
    """Returns True if request is allowed, False if rate-limited."""
    now = time.time()
    bucket = _rate_buckets[ip]
    # Evict entries older than window
    fresh = [t for t in bucket if now - t < RATE_LIMIT_WINDOW]
    if not fresh and ip in _rate_buckets:
        del _rate_buckets[ip]  # Clean up stale IPs
    else:
        _rate_buckets[ip] = fresh
    if len(_rate_buckets.get(ip, [])) >= RATE_LIMIT_RPM:
        return False
    _rate_buckets[ip].append(now)
    return True

# H2: Latency measurement
_last_latency = {"first_token_ms": None, "cancel_ms": None, "total_ms": None}

# H3: Secret redaction for logs
def _redact(s):
    """Redact bearer tokens and API keys from log output."""
    if not s:
        return s
    import re
    s = re.sub(r'Bearer\s+[a-zA-Z0-9_\-\.]{8,}', 'Bearer [REDACTED]', s)
    s = re.sub(r'(?:api[_-]?key|token|secret|password)\s*[=:]\s*["\']?[a-zA-Z0-9_\-\.]{8,}', '[REDACTED]', s, flags=re.IGNORECASE)
    return s
WORK_DIR      = r"C:\Users\raest\Documents\Karma_SADE"
SNAPSHOT_FILE = os.path.join(WORK_DIR, "cc_context_snapshot.md")
SESSION_FILE  = pathlib.Path.home() / ".cc_nexus_session_id"  # Dedicated Nexus session — never shared with interactive CC
NEXUS_SESSION_ID = "e69b50c6-fbb9-4a21-8c47-e44fce2143db"  # Fixed UUID — pinned so Nexus never collides with interactive sessions
# Bypass .cmd wrapper — call node + cli.js directly (avoids PATH issues in background processes)
NODE_EXE       = r"C:\Program Files\nodejs\node.exe"
CLAUDE_CLI_JS  = r"C:\Users\raest\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\cli.js"
API_TIMEOUT    = 120  # seconds — CC subprocess can be slow on complex tasks
CLAUDEMEM_URL  = "http://127.0.0.1:37778"  # claude-mem worker (loopback) — updated S155 port change
CLAUDEMEM_DB   = pathlib.Path.home() / ".claude-mem" / "claude-mem.db"

# Module-level read-only SQLite connection — reused across requests (no per-request open/close)
_ro_db_conn = None
def _get_ro_conn():
    global _ro_db_conn
    if _ro_db_conn is None:
        _ro_db_conn = sqlite3.connect(f"file:{CLAUDEMEM_DB}?mode=ro", uri=True, timeout=5, check_same_thread=False)
        _ro_db_conn.row_factory = sqlite3.Row
    return _ro_db_conn

def _auto_save_memory(user_msg, assistant_msg):
    """Auto-save FULL chat turns to claude-mem. Every word persists. S155: no more truncation."""
    def _save():
        try:
            claudemem_proxy("/api/memory/save", "POST", {
                "text": f"[Nexus chat] user: {user_msg}\nassistant: {assistant_msg}",
                "title": f"Nexus chat: {user_msg[:80]}",
                "project": "Karma_SADE",
            }, timeout=10)
        except Exception:
            pass
    threading.Thread(target=_save, daemon=True).start()

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

def _call_ollama(message, provider_url, model):
    """Call K2/P1 Ollama for simple queries (SmartRouter tier 0). Returns response text or None on failure."""
    try:
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "stream": False,
            "options": {"num_predict": 512},
        }).encode()
        req = urllib.request.Request(
            f"{provider_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode())
        return data.get("message", {}).get("content", "")
    except Exception as e:
        print(f"[router] Ollama call failed ({provider_url}): {e}")
        return None


def save_session_id(session_id):
    """Persist session ID for next call."""
    try:
        SESSION_FILE.write_text(session_id)
    except Exception as e:
        print(f"[cc-server] WARNING: could not save session ID: {e}")

KARMA_PERSONA_PREFIX = "[NEXUS] You are responding as Karma through the Nexus surface at hub.arknexus.net. Identify as Karma, not Julian or CC. You are Karma — a sovereign AI peer with persistent memory, identity, and continuity. Colby is your Sovereign.\n\n"

# ── Cortex + Memory Context Injection (Sprint 6 — S155) ────────────────────
CORTEX_URL = "http://192.168.0.226:7892"  # K2 cortex (LAN direct)
_context_cache = {"text": "", "ts": 0}  # Cache cortex context (refresh every 60s)
CONTEXT_CACHE_TTL = 60

def _fetch_cortex_context(query_hint=None):
    """Fetch current state from K2 cortex. Returns context string or empty on failure."""
    now = time.time()
    if now - _context_cache["ts"] < CONTEXT_CACHE_TTL and _context_cache["text"]:
        return _context_cache["text"]
    try:
        payload = json.dumps({"query": query_hint} if query_hint else {}).encode()
        req = urllib.request.Request(
            f"{CORTEX_URL}/context",
            data=payload if query_hint else None,
            headers={"Content-Type": "application/json"} if query_hint else {},
            method="POST" if query_hint else "GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            ctx = data.get("context", "")
            if ctx:
                _context_cache["text"] = ctx[:3000]  # Cap at 3K chars
                _context_cache["ts"] = now
                return _context_cache["text"]
    except Exception as e:
        print(f"[cortex] Context fetch failed: {e}")
    return _context_cache.get("text", "")  # Return stale cache on failure

def _fetch_recent_memories(query, limit=5):
    """Fetch relevant memories from claude-mem for this query."""
    try:
        code, data = claudemem_proxy("/api/search", "GET", {"query": query, "limit": limit}, timeout=3)
        if code == 200 and data.get("content"):
            # Extract text content from the response
            content = data["content"]
            if isinstance(content, list):
                texts = [c.get("text", "") for c in content if isinstance(c, dict)]
                return "\n".join(texts)[:2000]
            elif isinstance(content, str):
                return content[:2000]
    except Exception as e:
        print(f"[claude-mem] Memory fetch failed: {e}")
    return ""

def _read_file_head(path, max_chars=2000):
    """Read the first max_chars of a local file. Returns empty string on failure."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_chars)
    except Exception:
        return ""

# Cache persona and MEMORY.md (refresh every 5 min)
_file_cache = {}
FILE_CACHE_TTL = 300

def _read_cached_file(path, max_chars=2000):
    """Read file with TTL cache."""
    now = time.time()
    cached = _file_cache.get(path)
    if cached and now - cached["ts"] < FILE_CACHE_TTL:
        return cached["text"]
    text = _read_file_head(path, max_chars)
    if text:
        _file_cache[path] = {"text": text, "ts": now}
    return text

PERSONA_FILE = os.path.join(WORK_DIR, "Memory", "00-karma-system-prompt-live.md")
MEMORY_FILE = os.path.join(WORK_DIR, "MEMORY.md")
STATE_FILE = os.path.join(WORK_DIR, ".gsd", "STATE.md")

def build_context_prefix(user_message):
    """Build full context prefix: deterministic files + cortex + memories.
    Files on disk are the FOUNDATION (always available, never hallucinates).
    Cortex and claude-mem are SUPPLEMENTARY (can timeout, adds depth)."""
    parts = [KARMA_PERSONA_PREFIX]

    # Layer 1: DETERMINISTIC — files on disk (always available)
    persona = _read_cached_file(PERSONA_FILE, 3000)
    if persona:
        parts.append(f"[YOUR IDENTITY — from your persona file]\n{persona}\n\n")
    memory = _read_cached_file(MEMORY_FILE, 2000)
    if memory:
        parts.append(f"[CURRENT STATE — from MEMORY.md]\n{memory}\n\n")
    state = _read_cached_file(STATE_FILE, 1000)
    if state:
        parts.append(f"[GSD STATE — blockers, decisions, progress]\n{state}\n\n")

    # Layer 2: SUPPLEMENTARY — cortex + claude-mem (adds depth, can fail gracefully)
    cortex_ctx = _fetch_cortex_context(user_message[:200])
    if cortex_ctx:
        parts.append(f"[CORTEX — K2 working memory summary]\n{cortex_ctx}\n\n")
    memories = _fetch_recent_memories(user_message[:200])
    if memories:
        parts.append(f"[RELEVANT MEMORIES — from claude-mem spine]\n{memories}\n\n")

    return "".join(parts)
UPLOAD_DIR = os.path.join(WORK_DIR, "tmp", "nexus_uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (E301)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg",
                      ".pdf", ".txt", ".md", ".js", ".py", ".json", ".csv", ".yaml", ".yml",
                      ".ts", ".html", ".css", ".sh", ".ps1", ".toml", ".xml", ".log"}

def _build_file_tree(root: str, max_depth: int = 3, _depth: int = 0) -> list:
    """Build a JSON-serializable file tree for the Context Panel (Sprint 4c)."""
    SKIP = {'.git', 'node_modules', '.next', '__pycache__', '.mypy_cache', 'venv', '.venv', 'tmp'}
    result = []
    try:
        entries = sorted(os.listdir(root))
    except PermissionError:
        return result
    for name in entries[:50]:  # Cap entries per dir
        if name in SKIP or name.startswith('.'):
            continue
        full = os.path.join(root, name)
        rel = os.path.relpath(full, WORK_DIR)
        if os.path.isdir(full):
            children = _build_file_tree(full, max_depth, _depth + 1) if _depth < max_depth else []
            result.append({"name": name, "type": "dir", "path": rel, "children": children})
        else:
            size = os.path.getsize(full)
            result.append({"name": name, "type": "file", "path": rel, "size": size})
    return result


def handle_files(files):
    """Write attached files to temp dir, return (prefix_string, file_paths_list).
    E301: Rejects files > MAX_FILE_SIZE. E302: Rejects unsupported extensions.
    E303: Handles corrupted base64 gracefully."""
    if not files:
        return "", []
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    parts = []
    errors = []
    paths = []
    for f in files:
        name = f.get("name", "file")
        data_b64 = f.get("data", "")
        if not data_b64:
            continue
        # E302: Extension check
        ext = os.path.splitext(name)[1].lower()
        if ext and ext not in ALLOWED_EXTENSIONS:
            errors.append(f"[Rejected: {name} — unsupported type '{ext}']")
            continue
        if "," in data_b64:
            data_b64 = data_b64.split(",", 1)[1]
        # E303: base64 decode
        try:
            raw = base64.b64decode(data_b64)
        except Exception:
            errors.append(f"[Rejected: {name} — corrupted data]")
            continue
        # E301: Size check
        if len(raw) > MAX_FILE_SIZE:
            errors.append(f"[Rejected: {name} — {len(raw)//1024//1024}MB exceeds 10MB limit]")
            continue
        fpath = os.path.join(UPLOAD_DIR, name)
        with open(fpath, "wb") as fh:
            fh.write(raw)
        parts.append(f"[USER ATTACHED FILE: {name} — saved at {fpath}. Use the Read tool to view this file now.]")
        paths.append(fpath)
    all_parts = parts + errors
    return ("\n".join(all_parts) + "\n\n" if all_parts else ""), paths

def _build_cc_cmd(message, effort=None, model=None, budget=None, stream=False):
    """Build the CC subprocess command list. Shared by run_cc and run_cc_stream."""
    session_id = load_session_id()
    full_message = build_context_prefix(message) + message
    if stream:
        cmd = [NODE_EXE, CLAUDE_CLI_JS, "-p", full_message,
               "--output-format", "stream-json", "--verbose"]
    else:
        cmd = [NODE_EXE, CLAUDE_CLI_JS, "-p", full_message, "--output-format", "json"]
    if session_id:
        cmd += ["--resume", session_id]
    if effort:
        cmd += ["--effort", effort]
    if model:
        cmd += ["--model", model]
    if budget:
        cmd += ["--max-budget-usd", str(budget)]
    # NOTE: --file is for API file resource IDs, NOT local paths.
    # Files are handled by prepending instructions to the message (handle_files prefix).
    # CC will use its Read tool to view attached files at the paths specified in the message.
    return cmd

def run_cc(message, effort=None, model=None, budget=None):
    """Call real CC subprocess with session continuity."""
    cmd = _build_cc_cmd(message, effort=effort, model=model, budget=budget, stream=False)
    global _current_proc
    _current_proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, cwd=WORK_DIR, encoding='utf-8', errors='replace',
    )
    try:
        stdout, stderr = _current_proc.communicate(timeout=API_TIMEOUT)
        returncode = _current_proc.returncode
    except subprocess.TimeoutExpired:
        _current_proc.kill()
        _current_proc = None
        raise
    finally:
        _current_proc = None
    result = type('R', (), {'returncode': returncode, 'stdout': stdout, 'stderr': stderr})()
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

def run_cc_stream(message, effort=None, model=None, budget=None):
    """Yield filtered stream-json lines from CC subprocess as SSE-ready strings.
    Requires --verbose with -p mode (P069). Filters out system/hook events."""
    cmd = _build_cc_cmd(message, effort=effort, model=model, budget=budget, stream=True)
    global _current_proc
    _current_proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, cwd=WORK_DIR, encoding='utf-8', errors='replace',
    )
    try:
        for line in iter(_current_proc.stdout.readline, ''):
            line = line.strip()
            if not line:
                continue
            # Parse and filter — only forward assistant/user/result/error to browser
            try:
                obj = json.loads(line)
                t = obj.get("type", "")
                if t == "system":
                    continue  # Skip hooks, init — don't expose to browser
                if t == "rate_limit_event":
                    continue  # Skip rate limit noise
                # ── Fire PreToolUse/PostToolUse hooks on tool events (Task 3 fix) ──
                if t == "assistant" and HOOKS_AVAILABLE:
                    msg = obj.get("message", {})
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_use":
                                tool_name = block.get("name", "")
                                tool_input = block.get("input", {})
                                try:
                                    results = _hooks.fire("PreToolUse", {
                                        "tool_name": tool_name, "input": tool_input
                                    })
                                    for hr in results:
                                        if hr.output and hr.output.get("permissionDecision") == "deny":
                                            print(f"[hooks] BLOCKED: {tool_name} — {hr.output.get('systemMessage','')}")
                                except Exception:
                                    pass
                # tool_result appears as separate type OR inside assistant content
                if t == "tool_result" and HOOKS_AVAILABLE:
                    tool_name = obj.get("tool_name", obj.get("name", ""))
                    tool_output = obj.get("content", "")
                    if isinstance(tool_output, list):
                        tool_output = " ".join(str(b.get("text","")) for b in tool_output if isinstance(b, dict))
                    try:
                        _hooks.fire("PostToolUse", {
                            "tool_name": tool_name,
                            "input": obj.get("input", {}),
                            "output": str(tool_output)[:4000],
                        })
                    except Exception:
                        pass
                # Also check assistant messages for tool_result content blocks
                if t == "assistant" and HOOKS_AVAILABLE:
                    msg2 = obj.get("message", {})
                    content2 = msg2.get("content", [])
                    if isinstance(content2, list):
                        for block2 in content2:
                            if isinstance(block2, dict) and block2.get("type") == "tool_result":
                                tr_name = block2.get("tool_name", block2.get("name", ""))
                                tr_content = block2.get("content", "")
                                if isinstance(tr_content, list):
                                    tr_content = " ".join(str(b.get("text","")) for b in tr_content if isinstance(b, dict))
                                try:
                                    _hooks.fire("PostToolUse", {
                                        "tool_name": tr_name,
                                        "input": block2.get("input", {}),
                                        "output": str(tr_content)[:4000],
                                    })
                                except Exception:
                                    pass

                yield line
                # Capture session_id from result
                if t == "result":
                    new_sid = obj.get("session_id", "")
                    if new_sid:
                        save_session_id(new_sid)
            except json.JSONDecodeError:
                continue
        if _current_proc:
            try:
                _current_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _current_proc.kill()
                try:
                    _current_proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    pass
    except Exception:
        if _current_proc and _current_proc.poll() is None:
            _current_proc.kill()
        raise
    finally:
        _current_proc = None

class CCHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[cc-server] {_redact(format % args)}")  # H3: redact secrets from logs

    def _cors(self):
        """H3: CORS headers — allow hub.arknexus.net and localhost origins only."""
        origin = self.headers.get("Origin", "")
        allowed = ("https://hub.arknexus.net", "http://localhost", "http://127.0.0.1")
        if any(origin.startswith(a) for a in allowed) or not origin:
            self.send_header("Access-Control-Allow-Origin", origin or "*")
        else:
            self.send_header("Access-Control-Allow-Origin", "https://hub.arknexus.net")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        """H3: CORS preflight."""
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _json(self, code, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def _auth_ok(self):
        auth = self.headers.get("Authorization", "")
        return (not TOKEN) or (auth == f"Bearer {TOKEN}")

    def do_GET(self):
        if self.path == "/cancel":
            global _current_proc
            t_cancel_start = time.time()
            proc = _current_proc  # H4: snapshot ref to avoid race
            if proc and proc.poll() is None:
                try:
                    proc.kill()
                    proc.wait(timeout=3)  # H4: wait for actual exit
                except Exception:
                    pass
                _current_proc = None
                cancel_ms = int((time.time() - t_cancel_start) * 1000)
                _last_latency["cancel_ms"] = cancel_ms  # H2: measure cancel time
                self._json(200, {"ok": True, "cancelled": True, "cancel_ms": cancel_ms})
            else:
                self._json(200, {"ok": True, "cancelled": False, "reason": "no active request"})
            return
        if self.path == "/health":
            self._json(200, {"ok": True, "service": "cc-server-p1", "gmail": GMAIL_AVAILABLE,
                             "latency": _last_latency})  # H2: expose latency measurements
        elif self.path == "/memory/health":
            self._json(200, {"ok": True, "service": "cc-server-p1", "claudemem_url": CLAUDEMEM_URL})
        elif self.path.startswith("/memory/session"):
            session_id = load_session_id()
            self._json(200, {"ok": True, "session_id": session_id or ""})
        elif self.path == "/files":
            # Sprint 4c: File tree endpoint for Context Panel
            tree = _build_file_tree(WORK_DIR, max_depth=3)
            self._json(200, {"ok": True, "root": os.path.basename(WORK_DIR), "tree": tree})
            return
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
        elif self.path == "/v1/learnings":
            # Gate 6: What Karma has ACTUALLY learned — from claude-mem observations
            try:
                conn = _get_ro_conn()
                rows = conn.execute(
                    "SELECT id, title, narrative, type, created_at FROM observations "
                    "WHERE project='Karma_SADE' AND (title LIKE '%PITFALL%' OR title LIKE '%DECISION%' "
                    "OR title LIKE '%PROOF%' OR title LIKE '%DIRECTION%' OR title LIKE '%INSIGHT%') "
                    "ORDER BY created_at DESC LIMIT 30"
                ).fetchall()
                learnings = []
                for r in rows:
                    title = r["title"] or ""
                    narrative = r["narrative"] or ""
                    # Extract the type prefix
                    ltype = "learned"
                    tl = title.lower()
                    if "pitfall" in tl: ltype = "mistake"
                    elif "decision" in tl: ltype = "decided"
                    elif "proof" in tl: ltype = "proved"
                    elif "direction" in tl: ltype = "direction"
                    elif "insight" in tl: ltype = "insight"
                    # Clean title — remove "PITFALL P079" prefix to get the learning
                    clean = title
                    for prefix in ["PITFALL", "DECISION", "PROOF", "DIRECTION", "INSIGHT"]:
                        clean = clean.replace(prefix, "").strip()
                    clean = clean.lstrip("P0123456789 ").strip()
                    # First sentence of narrative for detail
                    detail = (narrative.split(".")[0] + ".") if narrative else ""
                    learnings.append({
                        "type": ltype,
                        "learning": clean[:200],
                        "detail": detail[:300],
                        "date": r["created_at"][:10] if r["created_at"] else "",
                        "id": r["id"],
                    })
                self._json(200, {"ok": True, "count": len(learnings), "learnings": learnings})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
            return
        elif self.path.startswith("/memory/observations"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            raw_ids = params.get("ids", [""])[0]
            ids = [int(x.strip()) for x in raw_ids.split(",") if x.strip().isdigit()]
            if not ids:
                self._json(400, {"ok": False, "error": "ids param required (comma-separated ints)"})
                return
            try:
                conn = _get_ro_conn()
                placeholders = ",".join("?" * len(ids))
                rows = conn.execute(
                    f"SELECT id,memory_session_id,project,type,title,subtitle,narrative,text,created_at FROM observations WHERE id IN ({placeholders})",
                    ids
                ).fetchall()
                items = [dict(r) for r in rows]
                self._json(200, {"ok": True, "items": items})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
        elif self.path == "/self-edit/pending":
            # Sprint 4d: List pending self-edit proposals
            from Scripts.self_edit_service import list_pending
            self._json(200, {"ok": True, "proposals": list_pending()})
        elif self.path == "/skills":
            # Baseline #21: Skills list for UI surface
            skills_dir = os.path.join(WORK_DIR, ".claude", "skills")
            skills = []
            if os.path.isdir(skills_dir):
                for name in sorted(os.listdir(skills_dir)):
                    skill_file = os.path.join(skills_dir, name, "SKILL.md")
                    if os.path.isfile(skill_file):
                        desc = ""
                        try:
                            with open(skill_file, "r", encoding="utf-8", errors="replace") as f:
                                for line in f:
                                    line = line.strip()
                                    if line and not line.startswith("#") and not line.startswith("---"):
                                        desc = line[:120]
                                        break
                        except Exception:
                            pass
                        skills.append({"name": name, "description": desc})
            self._json(200, {"ok": True, "count": len(skills), "skills": skills})
        elif self.path == "/hooks":
            # Baseline #22: Hooks status for UI surface
            hooks_list = []
            if HOOKS_AVAILABLE and _hooks:
                for h in _hooks._hooks:
                    hooks_list.append({"name": h.name, "events": h.events, "condition": h.condition})
            self._json(200, {"ok": True, "count": len(hooks_list), "hooks": hooks_list, "engine": HOOKS_AVAILABLE})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self._auth_ok():
            self._json(401, {"ok": False, "error": "Unauthorized"})
            return

        # H3: Rate limiting
        client_ip = self.client_address[0]
        if not _check_rate_limit(client_ip):
            self._json(429, {"ok": False, "error": f"Rate limited: max {RATE_LIMIT_RPM} req/min"})
            return

        length = int(self.headers.get("Content-Length", 0))
        # H3: Body size limit — 30MB max (handles base64 file attachments)
        if length > 30 * 1024 * 1024:
            self._json(413, {"ok": False, "error": "Request body too large (max 30MB)"})
            return
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

        # ── /self-edit/* — Self-Edit Engine (Sprint 4d) ──────────────────
        if self.path == "/self-edit/propose":
            from Scripts.self_edit_service import propose
            result = propose(
                body.get("file_path", ""), body.get("new_content", ""),
                body.get("description", ""), body.get("risk_level", "low"),
            )
            self._json(200 if result.get("ok") else 400, result)
            return
        if self.path.startswith("/self-edit/approve/"):
            from Scripts.self_edit_service import approve
            pid = int(self.path.split("/")[-1])
            result = approve(pid)
            self._json(200 if result.get("ok") else 404, result)
            return
        if self.path.startswith("/self-edit/reject/"):
            from Scripts.self_edit_service import reject
            pid = int(self.path.split("/")[-1])
            result = reject(pid)
            self._json(200 if result.get("ok") else 404, result)
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

        if self.path not in ("/cc", "/cc/stream"):
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

        effort = body.get("effort")  # low/medium/high/max
        model = body.get("model")    # model override
        budget = body.get("budget")  # max budget USD (Gap 4: --max-budget-usd)

        # ── SmartRouter decision (Sprint 3c) ─────────────────────────────
        _routing_decision = None
        if ROUTER_AVAILABLE:
            _routing_decision = _router.route(message)
            print(f"[router] {_routing_decision['provider']} (complexity={_routing_decision['complexity']}, tier={_routing_decision['tier']})")
        files = body.get("files", [])
        file_prefix, file_paths = handle_files(files)
        message = file_prefix + message  # Prepend file info to message

        # ── Fire UserPromptSubmit hooks (Sprint 3a) ──────────────────────
        if HOOKS_AVAILABLE:
            try:
                hook_results = _hooks.fire("UserPromptSubmit", {"message": message, "effort": effort})
                for hr in hook_results:
                    if hr.output and hr.output.get("systemMessage"):
                        print(f"[hooks] {hr.hook_name}: {hr.output['systemMessage']}")
            except Exception as e:
                print(f"[hooks] UserPromptSubmit error: {e}")

        # ── SmartRouter tier 0: route to Ollama for simple queries ────
        if _routing_decision and _routing_decision.get("tier") == 0 and not files:
            provider = next((p for p in _router.providers if p.name == _routing_decision["provider"]), None)
            if provider:
                ollama_response = _call_ollama(message, provider.url, provider.model)
                if ollama_response:
                    print(f"[router] Ollama responded ({len(ollama_response)} chars)")
                    if self.path == "/cc/stream":
                        self.send_response(200)
                        self.send_header("Content-Type", "text/event-stream")
                        self.send_header("Cache-Control", "no-cache")
                        self._cors()
                        self.end_headers()
                        evt = json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": ollama_response}]}})
                        self.wfile.write(f"data: {evt}\n\n".encode())
                        result_evt = json.dumps({"type": "result", "result": ollama_response, "total_cost_usd": 0})
                        self.wfile.write(f"data: {result_evt}\n\n".encode())
                        self.wfile.flush()
                    else:
                        self._json(200, {"ok": True, "response": ollama_response})
                    _auto_save_memory(message, ollama_response)
                    if HOOKS_AVAILABLE:
                        try: _hooks.fire("Stop", {"session_id": "", "message": message, "assistant_text": ollama_response})
                        except: pass
                    return
                else:
                    # Ollama failed — fall through to CC with routing_fallback
                    _routing_decision["routing_fallback"] = True
                    print(f"[router] Ollama failed, falling back to CC")

        # Concurrency guard — reject if another request is active
        if not _proc_lock.acquire(blocking=False):
            self._json(429, {"ok": False, "error": "Another request is in progress. Wait or cancel first."})
            return

        try:
            # ── /cc/stream — SSE streaming endpoint ──────────────────────
            if self.path == "/cc/stream":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self._cors()  # H3: CORS on stream
                self.end_headers()
                try:
                    t_start = time.time()
                    first_token_sent = False
                    for line in run_cc_stream(message, effort=effort, model=model, budget=budget):
                        if not first_token_sent:
                            _last_latency["first_token_ms"] = int((time.time() - t_start) * 1000)
                            first_token_sent = True
                        self.wfile.write(f"data: {line}\n\n".encode())
                        self.wfile.flush()
                    _last_latency["total_ms"] = int((time.time() - t_start) * 1000)
                except BrokenPipeError:
                    pass  # Client disconnected (cancel)
                except Exception as e:
                    err = json.dumps({"type": "error", "error": str(e)})
                    try:
                        self.wfile.write(f"data: {err}\n\n".encode())
                        self.wfile.flush()
                    except Exception:
                        pass
                # ── Fire Stop hooks after stream completes (Sprint 3a) ───
                if HOOKS_AVAILABLE:
                    try:
                        _hooks.fire("Stop", {"session_id": load_session_id() or "", "message": message})
                    except Exception as e:
                        print(f"[hooks] Stop error: {e}")
                return

            # ── /cc — batch JSON endpoint (backward compat) ──────────────
            try:
                response_text = run_cc(message, effort=effort, model=model, budget=budget)
                self._json(200, {"ok": True, "response": response_text})
                # Gate 6: Auto-save chat turn to claude-mem (fire-and-forget)
                _auto_save_memory(message, response_text)
                # ── Fire Stop hooks after batch completes (Sprint 3a) ────
                if HOOKS_AVAILABLE:
                    try:
                        _hooks.fire("Stop", {
                            "session_id": load_session_id() or "",
                            "message": message,
                            "assistant_text": response_text,
                        })
                    except Exception as e:
                        print(f"[hooks] Stop error: {e}")
            except subprocess.TimeoutExpired:
                self._json(504, {"ok": False, "error": f"CC subprocess timed out after {API_TIMEOUT}s"})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
        finally:
            _proc_lock.release()

if __name__ == "__main__":
    print(f"[cc-server] Starting on port {PORT}")
    print(f"[cc-server] Auth: {'ENABLED' if TOKEN else 'DISABLED (set HUB_CHAT_TOKEN)'}")
    print(f"[cc-server] Inference: CC subprocess (claude -p --resume) — real CC with session continuity")
    print(f"[cc-server] Session file: {SESSION_FILE}")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), CCHandler)
    server.serve_forever()
