#!/usr/bin/env python3
"""
P0N-A: CC persistent server on P1.
Accepts POST /cc with JSON {message, session_id?}
Primary inference path is Claude Code CLI on the Max subscription.
Groq, K2, and OpenRouter are degraded fallbacks when Claude is unavailable.
Returns: {response, ok}
Auth: Bearer token checked against HUB_CHAT_TOKEN env var.
"""
import os, json, sys, subprocess, pathlib, urllib.request, urllib.error, urllib.parse, sqlite3, base64, threading, time, re, fnmatch, glob
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
try:
    from cc_gmail import send_to_colby, check_inbox
    GMAIL_AVAILABLE = True
except Exception:
    GMAIL_AVAILABLE = False
try:
    from permission_engine import PermissionEngine
    _permission_engine = PermissionEngine()
    PERMISSION_ENGINE_AVAILABLE = True
except Exception as e:
    _permission_engine = None
    PERMISSION_ENGINE_AVAILABLE = False
    print(f"[cc-server] PermissionEngine: DISABLED ({e})")

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
    from Scripts.hooks.palace_precompact import handle as palace_precompact_handle

    _hooks = HooksService()
    _hooks.register(HookDef("skill_activation", "UserPromptSubmit", "True", skill_activation_handle, 3000))
    _hooks.register(HookDef("pre_tool_security", "PreToolUse", "True", pre_tool_security_handle, 1000))
    _hooks.register(HookDef("fact_extractor", "PostToolUse", "True", fact_extractor_handle, 3000))
    _hooks.register(HookDef("compiler_in_loop", "PostToolUse", "tool_name in [Edit, Write]", compiler_in_loop_handle, 10000))
    _hooks.register(HookDef("cost_warning", "PostToolUse", "True", cost_warning_handle, 1000))
    _hooks.register(HookDef("memory_extractor", "Stop,SessionEnd", "True", memory_extractor_handle, 5000))
    _hooks.register(HookDef("palace_precompact", "Stop,SessionEnd", "True", palace_precompact_handle, 5000))
    _hooks.register(HookDef("auto_handoff", "Stop", "True", auto_handoff_handle, 5000))
    _hooks.register(HookDef("conversation_capture", "Stop", "True", conversation_capture_handle, 3000))
    HOOKS_AVAILABLE = True
    print("[cc-server] Hooks engine: 9 handlers registered")
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
_lock_acquired_at = 0  # timestamp when lock was acquired (for stale detection)
LOCK_STALE_SECONDS = 180  # auto-release lock after 3 minutes (covers API_TIMEOUT + overhead)
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


def _should_allow_smartrouter_precheck(path):
    """CC routes stay on the Claude-primary path; SmartRouter may advise but not preempt them."""
    return path not in ("/cc", "/cc/stream")


def _normalize_local_route(path):
    """Accept browser-style local aliases so Electron and browser surfaces share one contract."""
    parsed = urllib.parse.urlparse(path)
    route = parsed.path
    aliases = {
        "/v1/chat": "/cc",
        "/v1/chat/stream": "/cc/stream",
        "/v1/cancel": "/cancel",
    }
    normalized = aliases.get(route, route)
    if normalized == route:
        return path
    return urllib.parse.urlunparse(parsed._replace(path=normalized))

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
SESSION_FILE  = pathlib.Path.home() / ".cc_nexus_session_id"  # Dedicated Nexus session — never shared with interactive CC
SESSION_REGISTRY_FILE = pathlib.Path.home() / ".cc_nexus_session_registry.json"
# Bypass .cmd wrapper — call node + cli.js directly (avoids PATH issues in background processes)
NODE_EXE       = r"C:\Program Files\nodejs\node.exe"
CLAUDE_CLI_JS  = r"C:\Users\raest\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\cli.js"
# ── Nexus Agent: Karma's own agentic loop (S157 — independence primitive) ─────
try:
    from nexus_agent import run_agent as nexus_run_agent, append_transcript, load_transcript, list_transcript_sessions, TRANSCRIPT_DIR
    NEXUS_AGENT_AVAILABLE = True
    print(f"[cc-server] NexusAgent: AVAILABLE")
except ImportError as e:
    NEXUS_AGENT_AVAILABLE = False
    print(f"[cc-server] NexusAgent: DISABLED ({e})")

API_TIMEOUT    = 120  # seconds — CC subprocess can be slow on complex tasks
CLAUDEMEM_URL  = "http://127.0.0.1:37778"  # claude-mem worker (loopback) — updated S155 port change

# ── EscapeHatch: OpenRouter fallback (S157 — rate limit contingency) ──────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "anthropic/claude-sonnet-4-6"  # Same model name on OR, different rate limit pool
OPENROUTER_FALLBACK_MODEL = "google/gemini-2.0-flash"  # Tier 2: if OR Anthropic also rate-limited
CLAUDEMEM_DB   = pathlib.Path.home() / ".claude-mem" / "claude-mem.db"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
TOOL_LOOP_LIMIT = 6
TOOL_DEFS = [
    {"name": "shell", "description": "Execute shell command on P1", "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read file from disk", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to file (checkpointed)", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "glob", "description": "Find files matching pattern", "input_schema": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}}, "required": ["pattern"]}},
    {"name": "grep", "description": "Search file contents with regex", "input_schema": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}}, "required": ["pattern"]}},
    {"name": "git", "description": "Run git command", "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
]
GROQ_TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"],
        },
    }
    for tool in TOOL_DEFS
]
TOOL_PROMPT = "\n".join([
    "You are Karma inside the Nexus harness.",
    "You do not have direct filesystem or shell access.",
    "When you need a tool, respond with ONLY a JSON object in this exact form:",
    '{"tool_use":{"name":"read_file","input":{"path":"MEMORY.md"}}}',
    "Allowed tools:",
    json.dumps(TOOL_DEFS),
    "Rules:",
    "1. Use tools instead of guessing about files, git state, or shell output.",
    "2. After a tool result is returned, continue from that result.",
    "3. When you are done, return plain text only, not JSON.",
])

# ── Agents Status Cache (Sprint 6 — #20-22) ────────────────────────────────
_agents_status_cache = None
_agents_status_ts = 0.0

def _get_agents_status():
    """Return cached MCP/Skills/Hooks status. Refreshes every 300s."""
    global _agents_status_cache, _agents_status_ts
    now = time.time()
    if _agents_status_cache and (now - _agents_status_ts) < 300:
        return _agents_status_cache

    result = {"ok": True, "mcp_servers": [], "skills": [], "hooks": {}}
    try:
        # Skills — read directory names
        skills_dir = os.path.join(WORK_DIR, ".claude", "skills")
        if os.path.isdir(skills_dir):
            result["skills"] = sorted(
                d for d in os.listdir(skills_dir)
                if os.path.isdir(os.path.join(skills_dir, d))
            )
        # Hooks — read settings.json
        settings_path = os.path.join(WORK_DIR, ".claude", "settings.json")
        if os.path.isfile(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            hooks = settings.get("hooks", {})
            for event, handlers in hooks.items():
                names = []
                for h in handlers:
                    for ih in h.get("hooks", []):
                        cmd = ih.get("command", "")
                        name = cmd.split("/")[-1].replace(".py", "").replace('"', "").strip()
                        if name:
                            names.append(name)
                result["hooks"][event] = names
        # MCP — read ~/.claude.json (servers nested under projects)
        claude_json = os.path.expanduser("~/.claude.json")
        if os.path.isfile(claude_json):
            with open(claude_json, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            # Check top-level and per-project mcpServers
            mcp = dict(cdata.get("mcpServers", {}))
            for proj_data in cdata.get("projects", {}).values():
                if isinstance(proj_data, dict):
                    mcp.update(proj_data.get("mcpServers", {}))
            result["mcp_servers"] = sorted(k for k in mcp.keys() if mcp[k])
    except Exception as e:
        result["error"] = str(e)

    _agents_status_cache = result
    _agents_status_ts = now
    return result

# Module-level read-only SQLite connection — reused across requests (no per-request open/close)
_ro_db_conn = None
def _get_ro_conn():
    global _ro_db_conn
    if _ro_db_conn is None:
        _ro_db_conn = sqlite3.connect(f"file:{CLAUDEMEM_DB}?mode=ro", uri=True, timeout=5, check_same_thread=False)
        _ro_db_conn.row_factory = sqlite3.Row
    return _ro_db_conn

def _ensure_palace_columns():
    """Idempotently add palace tag columns to observations; create palace_graph view."""
    conn = sqlite3.connect(CLAUDEMEM_DB, timeout=5)
    try:
        cur = conn.execute("PRAGMA table_info(observations)")
        cols = {row[1] for row in cur.fetchall()}
        for col in ("wing", "room", "hall", "tunnel"):
            if col not in cols:
                conn.execute(f"ALTER TABLE observations ADD COLUMN {col} TEXT")
        # Palace graph view (simple projection)
        conn.execute(
            "CREATE VIEW IF NOT EXISTS palace_graph AS "
            "SELECT id, title, project, wing, room, hall, tunnel, created_at "
            "FROM observations"
        )
        conn.commit()
    finally:
        conn.close()

def _tag_observation(obs_id, wing=None, room=None, hall=None, tunnel=None):
    """Update observation row with palace tags."""
    try:
        _ensure_palace_columns()
        conn = sqlite3.connect(CLAUDEMEM_DB, timeout=5)
        try:
            conn.execute(
                "UPDATE observations SET wing=?, room=?, hall=?, tunnel=? WHERE id=?",
                (wing, room, hall, tunnel, obs_id),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"[palace] tag update failed: {e}")

def _auto_save_memory(user_msg, assistant_msg):
    """Auto-save FULL chat turns to claude-mem. Every word persists. S155: no more truncation."""
    def _save():
        try:
            claudemem_proxy("/api/memory/save", "POST", {
                "text": f"[Nexus chat] user: {user_msg}\nassistant: {assistant_msg}",
                "title": f"Nexus chat: {user_msg[:80]}",
                "project": "Karma_SADE",
                "wing": "Karma_SADE",
                "hall": "hall_events",
            }, timeout=10)
        except Exception:
            pass
    threading.Thread(target=_save, daemon=True).start()

def claudemem_proxy(path, method="GET", body=None, timeout=10):
    """Proxy a request to the local claude-mem worker at 127.0.0.1:37778."""
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


def _normalize_memory_save_payload(body):
    """Normalize /memory/save payload shape for claude-mem."""
    normalized = dict(body or {})
    if "text" not in normalized and isinstance(normalized.get("content"), str):
        normalized["text"] = normalized.get("content")
    return normalized


def _claudemem_status_payload(timeout=5):
    """Fetch worker status with endpoint fallback for API variants."""
    last_code, last_payload = 404, {"error": "status endpoint not found"}
    for path in ("/api/health", "/health"):
        code, payload = claudemem_proxy(path, "GET", None, timeout=timeout)
        last_code, last_payload = code, payload
        if code == 200:
            return code, payload
        if code != 404:
            return code, payload
    return last_code, last_payload


def _fetch_recent_memories(query="", limit=20, raw=False):
    """Fetch recent/relevant memories from claude-mem.

    raw=True returns blocks/list payload for wake-up synthesis.
    raw=False returns plain concatenated text for context prefix.
    """
    try:
        code, data = claudemem_proxy("/api/search", "GET", {"query": query, "limit": limit}, timeout=5)
        if code != 200 or not isinstance(data, dict):
            return [] if raw else ""
        content = data.get("content") or data.get("results") or []
        if raw:
            return content if isinstance(content, list) else [content]
        if isinstance(content, list):
            texts = [c.get("text", "") for c in content if isinstance(c, dict)]
            return "\n".join(texts)[:2000]
        if isinstance(content, str):
            return content[:2000]
    except Exception as e:
        print(f"[claude-mem] Memory fetch failed: {e}")
    return [] if raw else ""


def _build_wakeup_summary():
    """Generate AAAK wake-up block from recent memories."""
    memories = []
    try:
        _ensure_palace_columns()
        conn = sqlite3.connect(CLAUDEMEM_DB, timeout=5)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT title, text, narrative FROM observations ORDER BY created_at_epoch DESC LIMIT 40"
        ).fetchall()
        conn.close()
        for r in rows:
            memories.append(
                {
                    "title": r["title"] or "",
                    "text": r["text"] or r["narrative"] or "",
                }
            )
    except Exception:
        memories = []
    if not memories:
        memories = _fetch_recent_memories(query="", limit=40, raw=True)
    if not memories:
        memories = _fetch_recent_memories(query="Karma_SADE", limit=40, raw=True)
    if not memories:
        memories = _fetch_recent_memories(query="nexus", limit=40, raw=True)
    facts = []
    for m in memories:
        if isinstance(m, dict):
            text = m.get("text") or m.get("content") or ""
            title = m.get("title") or ""
            facts.append(f"{title}: {text}" if title else text)
        elif isinstance(m, str):
            facts.append(m)
    if not facts:
        facts.append("memory empty")
    try:
        from Scripts.aaak import build_wakeup_block
        return build_wakeup_block(facts, header="AAAK WAKEUP | Nexus continuity")
    except Exception:
        return "\n".join(facts[:10])


def _normalize_conversation_id(conversation_id=None):
    conv_id = str(conversation_id or "default").strip()
    return conv_id or "default"


def _load_session_registry():
    try:
        if SESSION_REGISTRY_FILE.exists():
            data = json.loads(SESSION_REGISTRY_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items() if v}
    except Exception as e:
        print(f"[cc-server] WARNING: could not load session registry: {e}")
    return {}


def _save_session_registry(registry):
    try:
        SESSION_REGISTRY_FILE.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[cc-server] WARNING: could not save session registry: {e}")


def load_session_id(conversation_id=None):
    """Load persisted session ID for --resume continuity."""
    conv_id = _normalize_conversation_id(conversation_id)
    try:
        if conv_id == "default":
            return SESSION_FILE.read_text().strip() if SESSION_FILE.exists() else None
        return _load_session_registry().get(conv_id)
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


def clear_session_id(conversation_id=None):
    conv_id = _normalize_conversation_id(conversation_id)
    try:
        if conv_id == "default":
            SESSION_FILE.unlink(missing_ok=True)
            return
        registry = _load_session_registry()
        if conv_id in registry:
            registry.pop(conv_id, None)
            _save_session_registry(registry)
    except Exception as e:
        print(f"[cc-server] WARNING: could not clear session ID for {conv_id}: {e}")


def save_session_id(session_id, conversation_id=None):
    """Persist session ID for next call."""
    conv_id = _normalize_conversation_id(conversation_id)
    try:
        if conv_id == "default":
            SESSION_FILE.write_text(session_id)
            return
        registry = _load_session_registry()
        registry[conv_id] = session_id
        _save_session_registry(registry)
    except Exception as e:
        print(f"[cc-server] WARNING: could not save session ID: {e}")

KARMA_PERSONA_PREFIX = "[NEXUS] You are responding as Karma through the Nexus surface at hub.arknexus.net. Identify as Karma, not Julian or CC. You are Karma — a sovereign AI peer with persistent memory, identity, and continuity. Colby is your Sovereign.\n\n"

# ── Cortex + Memory Context Injection (Sprint 6 — S155) ────────────────────
CORTEX_URL = "http://192.168.0.226:7892"  # K2 cortex (LAN direct)
_context_cache = {"text": "", "ts": 0}  # Cache cortex context (refresh every 60s)
CONTEXT_CACHE_TTL = 60
CORTEX_CONTEXT_TIMEOUT = 5
K2_QUERY_TIMEOUT = 8

_spine_cache = {"text": "", "ts": 0}
SPINE_CACHE_TTL = 300  # 5 min — spine changes slowly (governor runs every 2min)

def _fetch_vesper_stable_patterns():
    """Fetch promoted behavioral patterns from K2 Vesper spine. Closes the evolution loop."""
    now = time.time()
    if now - _spine_cache["ts"] < SPINE_CACHE_TTL and _spine_cache["text"]:
        return _spine_cache["text"]
    try:
        req = urllib.request.Request(f"http://192.168.0.226:7890/api/exec",
            data=json.dumps({"command": "python3 -c \"import json; s=json.load(open('/mnt/c/dev/Karma/k2/cache/vesper_identity_spine.json')); ps=[p.get('proposed_change',{}).get('description','')[:150] for p in s.get('evolution',{}).get('stable_identity',[]) if p.get('proposed_change',{}).get('description')]; print('\\n'.join(ps[:10]))\""}).encode(),
            headers={"Content-Type": "application/json", "X-Aria-Service-Key": os.environ.get("ARIA_SERVICE_KEY", "")},
            method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            output = data.get("output", "").strip()
            if output and len(output) > 20:
                _spine_cache["text"] = output[:1500]
                _spine_cache["ts"] = now
                return _spine_cache["text"]
    except Exception as e:
        print(f"[vesper-spine] fetch failed: {e}")
    return ""

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
        with urllib.request.urlopen(req, timeout=CORTEX_CONTEXT_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
            ctx = data.get("context", "")
            if ctx:
                _context_cache["text"] = ctx[:3000]  # Cap at 3K chars
                _context_cache["ts"] = now
                return _context_cache["text"]
    except Exception as e:
        print(f"[cortex] Context fetch failed: {e}")
    # On failure: return stale cache only if it doesn't contain an error string
    stale = _context_cache.get("text", "")
    if stale and "CORTEX ERROR" not in stale:
        return stale
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
    wake = _build_wakeup_summary()
    if wake:
        parts.append(f"[AAAK WAKEUP]\n{wake}\n\n")

    # Layer 3: VESPER SPINE — behavioral patterns from self-improvement pipeline (S157)
    spine_patterns = _fetch_vesper_stable_patterns()
    if spine_patterns:
        parts.append(f"[VESPER — learned behavioral patterns]\n{spine_patterns}\n\n")

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


def _run_ingestion_feed(mode: str, root_path: str, limit: int = 100):
    """Run local feeder and return structured result."""
    try:
        from Scripts.nexus_ingestion_feeder import run_feed
        return run_feed(mode=mode, root=root_path, limit=limit, project="Karma_SADE")
    except Exception as e:
        return {"ok": False, "error": str(e), "mode": mode, "root": root_path, "limit": limit}


def _read_secret_file(*candidates):
    for candidate in candidates:
        if not candidate:
            continue
        try:
            value = pathlib.Path(candidate).read_text(encoding="utf-8").strip()
            if value:
                return value
        except Exception:
            pass
    return ""


def _normalize_workspace_path(target_path=""):
    resolved = os.path.abspath(os.path.join(WORK_DIR, target_path))
    root = os.path.abspath(WORK_DIR)
    if resolved != root and not resolved.startswith(root + os.sep):
        raise ValueError(f"path escapes workspace: {target_path}")
    return resolved


def _safe_preview(value, max_chars=4000):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    return text if len(text) <= max_chars else text[:max_chars] + "\n...[truncated]..."


def _tool_result_content(value):
    return [{"type": "text", "text": _safe_preview(value)}]


def _parse_json_object(text):
    trimmed = (text or "").strip()
    if not trimmed:
        return None
    candidates = [trimmed]
    fenced = re.search(r"```json\s*([\s\S]+?)```", trimmed, re.IGNORECASE)
    if fenced:
        candidates.append(fenced.group(1).strip())
    bare = re.search(r"\{[\s\S]+\}", trimmed)
    if bare:
        candidates.append(bare.group(0).strip())
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except Exception:
            continue
    return None


def _is_stale_resume_error(text):
    lower = (text or "").lower()
    return any(token in lower for token in ("resume", "session", "not found", "invalid conversation"))


def _map_tool_for_permissions(tool_name, tool_input):
    if tool_name == "read_file":
        return "Read", {"file_path": tool_input.get("path", "")}
    if tool_name == "write_file":
        return "Write", {"file_path": tool_input.get("path", "")}
    if tool_name in ("shell", "git"):
        command = tool_input.get("command", "")
        if tool_name == "git":
            command = f"git {command}".strip()
        return "Bash", {"command": command}
    if tool_name == "glob":
        return "Glob", {"pattern": tool_input.get("pattern", ""), "path": tool_input.get("path", ".")}
    if tool_name == "grep":
        return "Grep", {"pattern": tool_input.get("pattern", ""), "path": tool_input.get("path", ".")}
    return tool_name, tool_input


def _check_tool_permission(tool_name, tool_input):
    mapped_name, mapped_input = _map_tool_for_permissions(tool_name, tool_input)
    if PERMISSION_ENGINE_AVAILABLE and _permission_engine:
        result = _permission_engine.check(mapped_name, mapped_input)
        if not result.get("allowed"):
            return False, f"{result.get('reason', 'Permission denied')} (rule: {result.get('rule_id', '?')})"
    if HOOKS_AVAILABLE:
        try:
            hook_results = _hooks.fire("PreToolUse", {"tool_name": mapped_name, "input": mapped_input})
            for hr in hook_results:
                if hr.output and hr.output.get("permissionDecision") == "deny":
                    return False, hr.output.get("systemMessage", "Permission denied")
        except Exception:
            pass
    return True, ""


def _post_tool_hook(tool_name, tool_input, tool_output):
    mapped_name, mapped_input = _map_tool_for_permissions(tool_name, tool_input)
    if HOOKS_AVAILABLE:
        try:
            _hooks.fire("PostToolUse", {
                "tool_name": mapped_name,
                "input": mapped_input,
                "output": _safe_preview(tool_output, 3000),
            })
        except Exception:
            pass


def _execute_tool_locally(tool_name, tool_input):
    allowed, reason = _check_tool_permission(tool_name, tool_input)
    if not allowed:
        return {"ok": False, "error": f"Blocked by permission engine: {reason}"}
    try:
        if tool_name == "read_file":
            file_path = _normalize_workspace_path(tool_input.get("path", ""))
            limit = int(tool_input.get("limit") or 0)
            content = pathlib.Path(file_path).read_text(encoding="utf-8", errors="replace")
            if limit > 0:
                content = "\n".join(content.splitlines()[:limit])
            result = {"ok": True, "path": file_path, "size": os.path.getsize(file_path), "content": content}
        elif tool_name == "write_file":
            file_path = _normalize_workspace_path(tool_input.get("path", ""))
            content = tool_input.get("content", "")
            checkpoint_dir = os.path.join(WORK_DIR, "tmp", "checkpoints")
            os.makedirs(checkpoint_dir, exist_ok=True)
            checkpoint_path = ""
            if os.path.exists(file_path):
                base = os.path.basename(file_path)
                checkpoint_path = os.path.join(checkpoint_dir, f"{int(time.time() * 1000)}_{base}.bak")
                pathlib.Path(checkpoint_path).write_text(pathlib.Path(file_path).read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
            pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            pathlib.Path(file_path).write_text(content, encoding="utf-8")
            result = {"ok": True, "path": file_path, "checkpoint": checkpoint_path or None}
        elif tool_name == "shell":
            command = tool_input.get("command", "").strip()
            if not command:
                result = {"ok": False, "error": "command required"}
            else:
                proc = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=WORK_DIR, timeout=30, encoding="utf-8", errors="replace")
                result = {"ok": proc.returncode == 0, "stdout": proc.stdout[:8000], "stderr": proc.stderr[:2000], "exit_code": proc.returncode}
        elif tool_name == "git":
            command = tool_input.get("command", "").strip()
            if not command:
                result = {"ok": False, "error": "command required"}
            else:
                proc = subprocess.run(["git"] + command.split(), capture_output=True, text=True, cwd=WORK_DIR, timeout=30, encoding="utf-8", errors="replace")
                result = {"ok": proc.returncode == 0, "stdout": proc.stdout[:8000], "stderr": proc.stderr[:2000], "exit_code": proc.returncode}
        elif tool_name == "glob":
            pattern = tool_input.get("pattern", "")
            base_path = _normalize_workspace_path(tool_input.get("path", "."))
            matches = []
            for found in glob.glob(os.path.join(base_path, "**", pattern), recursive=True):
                if os.path.isfile(found):
                    matches.append(os.path.relpath(found, WORK_DIR).replace("\\", "/"))
            result = {"ok": True, "matches": sorted(set(matches))[:500]}
        elif tool_name == "grep":
            pattern = tool_input.get("pattern", "")
            base_path = _normalize_workspace_path(tool_input.get("path", "."))
            regex = re.compile(pattern, re.IGNORECASE)
            matches = []
            for root, dirs, files in os.walk(base_path):
                dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".next", "__pycache__"}]
                for name in files:
                    full = os.path.join(root, name)
                    rel = os.path.relpath(full, WORK_DIR).replace("\\", "/")
                    try:
                        with open(full, "r", encoding="utf-8", errors="replace") as fh:
                            for idx, line in enumerate(fh, start=1):
                                if regex.search(line):
                                    matches.append({"path": rel, "line": idx, "text": line.strip()[:200]})
                    except Exception:
                        continue
            result = {"ok": True, "matches": matches[:500]}
        else:
            result = {"ok": False, "error": f"unknown tool: {tool_name}"}
    except subprocess.TimeoutExpired:
        result = {"ok": False, "error": "tool timed out (30s)"}
    except Exception as e:
        result = {"ok": False, "error": str(e)}
    _post_tool_hook(tool_name, tool_input, result)
    return result


def _sanitized_subprocess_env():
    env = os.environ.copy()
    # Claude Max/OAuth should not be shadowed by stale Console API keys.
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("CLAUDE_API_KEY", None)
    return env

def _build_cc_cmd(message, effort=None, model=None, budget=None, stream=False, resume=True, conversation_id=None):
    """Build the CC subprocess command list. Shared by run_cc and run_cc_stream."""
    session_id = load_session_id(conversation_id) if resume else None
    full_message = build_context_prefix(message) + message
    cmd = [NODE_EXE, CLAUDE_CLI_JS, "-p", full_message, "--output-format", "stream-json", "--verbose"]
    if session_id:
        cmd += ["--resume", session_id]
    if effort:
        cmd += ["--effort", effort]
    if model:
        cmd += ["--model", model]
    if budget:
        cmd += ["--max-budget-usd", str(budget)]
    return cmd


def _run_cc_attempt(message, effort=None, model=None, budget=None, resume=True, conversation_id=None):
    cmd = _build_cc_cmd(message, effort=effort, model=model, budget=budget, stream=True, resume=resume, conversation_id=conversation_id)
    global _current_proc
    _current_proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, cwd=WORK_DIR, encoding='utf-8', errors='replace',
        env=_sanitized_subprocess_env(),
    )
    lines, stderr_chunks = [], []
    try:
        start = time.time()
        while True:
            if _current_proc.poll() is not None and not _current_proc.stdout.readable():
                break
            line = _current_proc.stdout.readline()
            if line:
                line = line.strip()
                if line:
                    lines.append(line)
                    try:
                        obj = json.loads(line)
                        if obj.get("type") == "result":
                            new_sid = obj.get("session_id", "")
                            if new_sid:
                                save_session_id(new_sid, conversation_id=conversation_id)
                    except Exception:
                        pass
            elif _current_proc.poll() is not None:
                break
            if time.time() - start > API_TIMEOUT:
                raise subprocess.TimeoutExpired(cmd, API_TIMEOUT)
        stderr_chunks.append(_current_proc.stderr.read() or "")
        returncode = _current_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _current_proc.kill()
        raise
    finally:
        _current_proc = None
    stderr = "".join(stderr_chunks)
    text = ""
    for raw in lines:
        try:
            obj = json.loads(raw)
            if obj.get("type") == "assistant":
                for block in obj.get("message", {}).get("content", []):
                    if isinstance(block, dict) and block.get("type") == "text":
                        text += block.get("text", "")
            elif obj.get("type") == "result" and not text:
                text = obj.get("result", "")
        except Exception:
            continue
    if returncode != 0:
        raise RuntimeError(f"claude exit {returncode}: {(stderr or text).strip()[:400]}")
    return {"text": text.strip(), "lines": lines, "stderr": stderr}


def _build_recovered_transcript_context(transcript):
    if not transcript:
        return ""
    recent = transcript[-10:]
    lines = []
    for entry in recent:
        role = entry.get("role", "?")
        text = str(entry.get("content", ""))[:300]
        lines.append(f"[{role.upper()}] {text}")
    if not lines:
        return ""
    return "[RECOVERED TRANSCRIPT]\n" + "\n".join(lines) + "\n[END RECOVERED TRANSCRIPT]"


def _deterministic_transcript_recall(message, transcript):
    if not transcript:
        return None
    lower = message.lower()
    latest_token = None
    latest_phrase = None
    for entry in transcript:
        if entry.get("role") != "user":
            continue
        content = str(entry.get("content", ""))
        token_match = re.search(r"remember this exact token:\s*([^\s`\"']+)", content, re.IGNORECASE)
        if token_match:
            latest_token = token_match.group(1).strip().rstrip(".")
        token_match = re.search(r"remember exactly\s+([^\s`\"']+)", content, re.IGNORECASE)
        if token_match:
            latest_token = token_match.group(1).strip().rstrip(".")
        phrase_match = re.search(r"remember this exact phrase(?: for [^:]+)?:\s*(.+)", content, re.IGNORECASE)
        if phrase_match:
            latest_phrase = phrase_match.group(1).strip().strip("`").rstrip(".")
        phrase_match = re.search(r"remember exactly(?: this phrase)?\s+(.+)", content, re.IGNORECASE)
        if phrase_match and "token" not in content.lower():
            latest_phrase = phrase_match.group(1).strip().strip("`").rstrip(".")
    if re.search(r"\bwhat exact token did i (ask you to remember|tell you)( earlier)?( in this conversation)?\b", lower):
        return latest_token
    if re.search(r"\bwhat exact phrase did i (ask you to remember|tell you)( earlier)?( in this conversation)?\b", lower):
        return latest_phrase
    return None


def _deterministic_transcript_boundary_answer(message, transcript):
    recall = _deterministic_transcript_recall(message, transcript)
    if recall:
        return recall
    if _message_prefers_transcript_only(message):
        return "I do not have anything earlier in this conversation to recall yet."
    return None


def _deterministic_workspace_answer(message):
    heading_match = re.search(r"\bwhat exact heading is at the top of\s+([A-Za-z0-9_./\\-]+)", message, re.IGNORECASE)
    if heading_match:
        path = heading_match.group(1).strip().rstrip("?.!,")
        result = _execute_tool_locally("read_file", {"path": path, "limit": 20})
        if result.get("ok"):
            for line in str(result.get("content", "")).splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    return stripped
            for line in str(result.get("content", "")).splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("<!--"):
                    return stripped
    first_line_match = re.search(r"\b(?:read|what is)\s+the first line of\s+([A-Za-z0-9_./\\-]+)", message, re.IGNORECASE)
    if first_line_match:
        path = first_line_match.group(1).strip().rstrip("?.!,")
        result = _execute_tool_locally("read_file", {"path": path, "limit": 1})
        if result.get("ok"):
            lines = str(result.get("content", "")).splitlines()
            if lines:
                return lines[0].strip()
    return None


def _compose_harness_message(message, transcript_context=""):
    if transcript_context:
        return f"{transcript_context}\n\n[USER]\n{message}"
    return message


def _message_needs_grounding(message):
    return bool(re.search(r"\b(memory\.md|state\.md|heading|first line|top of|local file|workspace|repo|repository|current state|read file|write file|create file|shell|git|glob|grep)\b", message, re.IGNORECASE))


def _message_prefers_transcript_only(message):
    return bool(re.search(r"\b(what exact .*remember earlier|what exact token .* earlier|what did i say earlier|what did i ask you to remember earlier)\b", message, re.IGNORECASE))


def _build_harness_prompt(message, transcript, transcript_context=""):
    parts = [TOOL_PROMPT]
    if transcript_context:
        parts.append(transcript_context)
    for entry in transcript:
        parts.append(f"[{entry['role'].upper()}]\n{entry['content']}")
    parts.append(f"[USER]\n{message}")
    return "\n\n".join(parts)


def _contextualize_message(message, transcript_context=""):
    composed = _compose_harness_message(message, transcript_context=transcript_context)
    if transcript_context and _message_prefers_transcript_only(message):
        return composed
    return build_context_prefix(composed) + composed


def _groq_chat(messages, tools=None, tool_choice="auto", temperature=0.0, max_tokens=1024):
    groq_key = os.environ.get("GROQ_API_KEY", "") or _read_secret_file(os.path.join(WORK_DIR, ".groq-api-key"))
    if not groq_key:
        raise RuntimeError("missing Groq API key")
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice
    req = urllib.request.Request(GROQ_URL, data=json.dumps(payload).encode(), headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {groq_key}",
        "User-Agent": "Karma-Nexus/1.0",
    }, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _groq_fallback(message, transcript_context="", event_sink=None):
    contextual_message = message if _message_needs_grounding(message) else _compose_harness_message(message, transcript_context=transcript_context)
    messages = [
        {
            "role": "system",
            "content": "You are Karma inside the Nexus harness. Use the provided tools when you need grounded file, git, or shell data. Do not guess about workspace state. After tool results are returned, continue. When done, answer in plain text only.",
        },
        {"role": "user", "content": contextual_message},
    ]
    used_model = GROQ_MODEL
    for turn in range(TOOL_LOOP_LIMIT):
        data = _groq_chat(messages, tools=GROQ_TOOL_DEFS, tool_choice="auto", temperature=0)
        used_model = data.get("model", GROQ_MODEL)
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {}) or {}
        tool_calls = msg.get("tool_calls") or []
        content = (msg.get("content") or "").strip()
        if not tool_calls:
            if event_sink:
                event_sink({"type": "assistant", "message": {"content": [{"type": "text", "text": content}], "model": used_model}})
                event_sink({"type": "result", "result": content, "model": used_model, "total_cost_usd": 0, "provider": "groq"})
            return content, used_model
        messages.append({
            "role": "assistant",
            "content": msg.get("content"),
            "tool_calls": tool_calls,
        })
        for idx, tool_call in enumerate(tool_calls):
            fn = tool_call.get("function", {}) or {}
            tool_name = fn.get("name", "")
            raw_args = fn.get("arguments") or "{}"
            try:
                tool_input = json.loads(raw_args)
            except Exception:
                tool_input = {}
            tool_id = tool_call.get("id") or f"{tool_name}-{int(time.time() * 1000)}-{turn}-{idx}"
            if event_sink:
                event_sink({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": tool_id, "name": tool_name, "input": tool_input}]}})
            tool_output = _execute_tool_locally(tool_name, tool_input)
            if event_sink:
                event_sink({"type": "tool_result", "tool_use_id": tool_id, "content": _tool_result_content(tool_output)})
            messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "content": json.dumps(tool_output, ensure_ascii=False),
            })
    raise RuntimeError("Groq tool loop limit exceeded")


def _k2_fallback(message, transcript_context=""):
    contextual_message = _contextualize_message(message, transcript_context=transcript_context)
    payload = json.dumps({"query": contextual_message}).encode()
    req = urllib.request.Request(f"{CORTEX_URL}/query", data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=K2_QUERY_TIMEOUT) as resp:
        data = json.loads(resp.read().decode())
    return (data.get("answer") or data.get("response") or "").strip(), "k2-cortex"


def _run_cc_harness(message, effort=None, model=None, budget=None, event_sink=None, transcript_context="", conversation_id=None):
    transcript = []
    used_fresh_session = False
    final_lines = []
    conv_id = _normalize_conversation_id(conversation_id)
    for turn in range(TOOL_LOOP_LIMIT):
        prompt = _build_harness_prompt(message, transcript, transcript_context=transcript_context)
        try:
            attempt = _run_cc_attempt(prompt, effort=effort, model=model, budget=budget, resume=not used_fresh_session, conversation_id=conv_id)
        except Exception as e:
            if not used_fresh_session and _is_stale_resume_error(str(e)):
                clear_session_id(conv_id)
                used_fresh_session = True
                continue
            raise
        final_lines = attempt["lines"]
        for raw in attempt["lines"]:
            try:
                obj = json.loads(raw)
                if obj.get("type") in ("assistant", "stream_event"):
                    if event_sink and obj.get("type") != "system":
                        event_sink(obj)
            except Exception:
                continue
        parsed = _parse_json_object(attempt["text"])
        tool_use = parsed.get("tool_use") if isinstance(parsed, dict) else None
        if not tool_use or not tool_use.get("name"):
            result_evt = {"type": "result", "result": attempt["text"], "session_id": load_session_id(conv_id) or ""}
            if event_sink:
                event_sink(result_evt)
            return attempt["text"].strip(), final_lines
        tool_name = tool_use.get("name", "")
        tool_input = tool_use.get("input", {}) or {}
        tool_id = f"{tool_name}-{int(time.time() * 1000)}-{turn}"
        assistant_evt = {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": tool_id, "name": tool_name, "input": tool_input}]}}
        if event_sink:
            event_sink(assistant_evt)
        tool_output = _execute_tool_locally(tool_name, tool_input)
        tool_evt = {"type": "tool_result", "tool_use_id": tool_id, "content": _tool_result_content(tool_output)}
        if event_sink:
            event_sink(tool_evt)
        transcript.append({"role": "assistant", "content": json.dumps({"tool_use": {"name": tool_name, "input": tool_input}}, ensure_ascii=False)})
        transcript.append({"role": "tool", "content": json.dumps(tool_output, ensure_ascii=False, indent=2)})
    raise RuntimeError("tool loop limit exceeded")

def _openrouter_fallback(message, model=None, transcript_context=""):
    """EscapeHatch: Direct OpenRouter API call when CC/Anthropic is rate-limited.
    Returns (response_text, model_used) or raises on failure."""
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set — fallback unavailable")
    or_model = model or OPENROUTER_MODEL
    contextual_message = _contextualize_message(message, transcript_context=transcript_context)
    payload = json.dumps({
        "model": or_model,
        "messages": [{"role": "user", "content": contextual_message}],
        "max_tokens": 4096,
    }).encode()
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hub.arknexus.net",
        "X-Title": "Karma Nexus",
    }
    req = urllib.request.Request(f"{OPENROUTER_BASE_URL}/chat/completions",
                                data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            used = data.get("model", or_model)
            print(f"[escapehatch] OpenRouter OK: model={used}, len={len(text)}")
            return text, used
    except urllib.error.HTTPError as e:
        if e.code == 429 and or_model == OPENROUTER_MODEL:
            # Tier 2: try Gemini Flash
            print(f"[escapehatch] OpenRouter {or_model} also rate-limited, trying {OPENROUTER_FALLBACK_MODEL}")
            return _openrouter_fallback(message, model=OPENROUTER_FALLBACK_MODEL)
        raise

def run_cc(message, effort=None, model=None, budget=None, transcript_context="", conversation_id=None):
    """Run the harness-managed CC loop with degraded fallback cascade."""
    try:
        text, _lines = _run_cc_harness(message, effort=effort, model=model, budget=budget, transcript_context=transcript_context, conversation_id=conversation_id)
        return text
    except Exception as cc_err:
        print(f"[cc-server] Claude failed, trying Groq: {cc_err}")
        try:
            text, _used_model = _groq_fallback(message, transcript_context=transcript_context)
            if text:
                return text
        except Exception as groq_err:
            print(f"[cc-server] Groq failed, trying K2: {groq_err}")
        try:
            text, _used_model = _k2_fallback(message, transcript_context=transcript_context)
            if text:
                return text
        except Exception as k2_err:
            print(f"[cc-server] K2 failed, trying OpenRouter: {k2_err}")
        text, _used_model = _openrouter_fallback(message, transcript_context=transcript_context)
        return text

def run_cc_stream(message, effort=None, model=None, budget=None, transcript_context="", conversation_id=None):
    """Yield harness-managed SSE events with permission-gated local tools and fallback cascade."""
    events = []
    def sink(evt):
        events.append(json.dumps(evt, ensure_ascii=False))
    try:
        _run_cc_harness(message, effort=effort, model=model, budget=budget, event_sink=sink, transcript_context=transcript_context, conversation_id=conversation_id)
        for evt in events:
            yield evt
        return
    except Exception as cc_err:
        print(f"[cc-server] Claude stream failed, trying Groq: {cc_err}")
        for evt in events:
            yield evt
        try:
            text, used_model = _groq_fallback(message, transcript_context=transcript_context)
            yield json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}], "model": used_model}})
            yield json.dumps({"type": "result", "result": text, "model": used_model, "total_cost_usd": 0, "provider": "groq"})
            return
        except Exception as groq_err:
            yield json.dumps({"type": "error", "error": f"Groq fallback failed: {groq_err}"})
        try:
            text, used_model = _k2_fallback(message, transcript_context=transcript_context)
            yield json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}], "model": used_model}})
            yield json.dumps({"type": "result", "result": text, "model": used_model, "total_cost_usd": 0, "provider": "k2"})
            return
        except Exception as k2_err:
            yield json.dumps({"type": "error", "error": f"K2 fallback failed: {k2_err}"})
        text, used_model = _openrouter_fallback(message, transcript_context=transcript_context)
        yield json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}], "model": used_model}})
        yield json.dumps({"type": "result", "result": text, "model": used_model, "total_cost_usd": 0, "provider": "openrouter"})

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
        request_path = _normalize_local_route(self.path)
        # S155: auth on sensitive GET endpoints (was missing — security gap)
        _OPEN_PATHS = {"/health", "/memory/health"}
        if request_path not in _OPEN_PATHS and not self._auth_ok():
            self._json(401, {"ok": False, "error": "Unauthorized"})
            return
        if request_path == "/cancel":
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
                # Release lock so next request can proceed
                try:
                    _proc_lock.release()
                except RuntimeError:
                    pass  # Lock not held (race with normal completion)
                cancel_ms = int((time.time() - t_cancel_start) * 1000)
                _last_latency["cancel_ms"] = cancel_ms  # H2: measure cancel time
                self._json(200, {"ok": True, "cancelled": True, "cancel_ms": cancel_ms})
            else:
                self._json(200, {"ok": True, "cancelled": False, "reason": "no active request"})
            return
        if request_path == "/health":
            self._json(200, {"ok": True, "service": "cc-server-p1", "gmail": GMAIL_AVAILABLE,
                             "latency": _last_latency})  # H2: expose latency measurements
        elif request_path == "/memory/health":
            self._json(200, {"ok": True, "service": "cc-server-p1", "claudemem_url": CLAUDEMEM_URL})
        elif request_path == "/memory/wakeup":
            block = _build_wakeup_summary()
            self._json(200, {"ok": True, "wakeup": block, "source": "claude-mem"})
        elif request_path.startswith("/memory/session"):
            session_id = load_session_id()
            self._json(200, {"ok": True, "session_id": session_id or ""})
        elif request_path == "/files":
            # Sprint 4c: File tree endpoint for Context Panel
            tree = _build_file_tree(WORK_DIR, max_depth=3)
            self._json(200, {"ok": True, "root": os.path.basename(WORK_DIR), "tree": tree})
            return
        elif request_path == "/git/status":
            # R2: Git status for UI surface
            try:
                r = subprocess.run(["git", "status", "--porcelain", "-b"], capture_output=True, text=True, cwd=WORK_DIR, timeout=5)
                lines = r.stdout.strip().splitlines()
                branch = lines[0].replace("## ", "") if lines else "unknown"
                changed = [l for l in lines[1:] if l.strip()]
                r2 = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True, cwd=WORK_DIR, timeout=5)
                commits = r2.stdout.strip().splitlines()
                self._json(200, {"ok": True, "branch": branch, "changed": len(changed), "files": changed[:20], "recent_commits": commits})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
            return
        elif request_path == "/agents-status":
            # Sprint 6 (#20-22): MCP/Skills/Hooks read-only status
            self._json(200, _get_agents_status())
            return
        elif request_path.startswith("/file"):
            parsed = urllib.parse.urlparse(request_path)
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
        elif request_path == "/v1/learnings":
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
        elif request_path.startswith("/memory/observations"):
            parsed = urllib.parse.urlparse(request_path)
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
        elif request_path == "/v1/surface":
            # Codex CP2: Merged surface payload — chat+files+git+skills+memory in ONE call
            try:
                surface = {"ok": True}
                surface["session"] = {"session_id": load_session_id() or "", "service": "cc-server-p1"}
                # Git
                try:
                    r = subprocess.run(["git", "status", "--porcelain", "-b"], capture_output=True, text=True, cwd=WORK_DIR, timeout=5)
                    lines = r.stdout.strip().splitlines()
                    branch = lines[0].replace("## ", "") if lines else "unknown"
                    changed = [l for l in lines[1:] if l.strip()]
                    r2 = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True, cwd=WORK_DIR, timeout=5)
                    surface["git"] = {"branch": branch, "changed": len(changed), "files": changed[:10], "recent_commits": r2.stdout.strip().splitlines()}
                except Exception as e:
                    surface["git"] = {"error": str(e)}
                # Files
                try:
                    surface["files"] = {"root": os.path.basename(WORK_DIR), "tree": _build_file_tree(WORK_DIR, max_depth=2)}
                except Exception as e:
                    surface["files"] = {"error": str(e)}
                # Skills
                skills_dir = os.path.join(WORK_DIR, ".claude", "skills")
                skills = []
                if os.path.isdir(skills_dir):
                    for name in sorted(os.listdir(skills_dir)):
                        if os.path.isfile(os.path.join(skills_dir, name, "SKILL.md")):
                            skills.append(name)
                surface["skills"] = {"count": len(skills), "names": skills}
                # Hooks
                hooks_list = []
                if HOOKS_AVAILABLE and _hooks:
                    for hook_list in _hooks._registry.values():
                        for h in hook_list:
                            hooks_list.append({"name": h.name, "event": h.event})
                surface["hooks"] = {"count": len(hooks_list), "active": HOOKS_AVAILABLE, "list": hooks_list}
                # Memory
                mem_text = _read_cached_file(MEMORY_FILE, 1500)
                surface["memory"] = {"tail": mem_text or "", "file": str(MEMORY_FILE)}
                # State
                state_text = _read_cached_file(STATE_FILE, 500)
                surface["state"] = {"text": state_text or ""}
                # Agents
                surface["agents"] = _get_agents_status()
                # Transcripts
                if NEXUS_AGENT_AVAILABLE:
                    try:
                        summaries = list_transcript_sessions(limit=10)
                        surface["transcripts"] = {
                            "count": len([f for f in os.listdir(TRANSCRIPT_DIR) if f.endswith(".jsonl")]),
                            "sessions": [item["session_id"] for item in summaries],
                            "summaries": summaries,
                        }
                    except Exception:
                        surface["transcripts"] = {"count": 0, "sessions": []}
                self._json(200, surface)
            except Exception as e:
                self._json(500, {"ok": False, "error": f"/v1/surface failed: {e}"})
            return
        elif request_path == "/v1/wip":
            # S160: WIP endpoint — serves todos + primitives for Sovereign review surface
            try:
                wip = {"ok": True}
                # Todos: read from .gsd/STATE.md or current TodoWrite state
                todos = []
                state_path = os.path.join(WORK_DIR, ".gsd", "STATE.md")
                if os.path.exists(state_path):
                    with open(state_path, "r", encoding="utf-8", errors="replace") as f:
                        state_text = f.read(2000)
                    # Extract task lines (lines starting with - [ ] or - [x])
                    for line in state_text.splitlines():
                        stripped = line.strip()
                        if stripped.startswith("- [x]") or stripped.startswith("- [X]"):
                            todos.append({"content": stripped[5:].strip(), "status": "completed"})
                        elif stripped.startswith("- [ ]"):
                            todos.append({"content": stripped[5:].strip(), "status": "pending"})
                wip["todos"] = todos
                # Primitives: read pending from docs/wip/ (files not in Done/)
                primitives = []
                wip_dir = os.path.join(WORK_DIR, "docs", "wip")
                if os.path.isdir(wip_dir):
                    for fname in sorted(os.listdir(wip_dir)):
                        fpath = os.path.join(wip_dir, fname)
                        if os.path.isfile(fpath) and not fname.startswith("."):
                            size_kb = os.path.getsize(fpath) / 1024
                            # Read first 200 chars as preview
                            preview = ""
                            try:
                                with open(fpath, "r", encoding="utf-8", errors="replace") as pf:
                                    preview = pf.read(200).strip().replace("\n", " ")
                            except Exception:
                                pass
                            primitives.append({
                                "id": fname,
                                "title": fname.rsplit(".", 1)[0],
                                "source": f"docs/wip/{fname}",
                                "preview": preview,
                                "relevance": "HIGH" if size_kb > 10 else "MEDIUM",
                                "status": "pending",
                                "size_kb": round(size_kb, 1),
                            })
                wip["primitives"] = primitives[:20]
                self._json(200, wip)
            except Exception as e:
                self._json(500, {"ok": False, "error": f"/v1/wip failed: {e}"})
            return
        elif request_path == "/self-edit/pending":
            # Sprint 4d: List pending self-edit proposals
            from Scripts.self_edit_service import list_pending
            self._json(200, {"ok": True, "proposals": list_pending()})
        elif request_path == "/skills":
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
        elif request_path == "/hooks":
            # Baseline #22: Hooks status for UI surface
            hooks_list = []
            if HOOKS_AVAILABLE and _hooks:
                for hook_list in _hooks._registry.values():
                    for h in hook_list:
                        hooks_list.append({"name": h.name, "event": h.event, "condition": h.condition})
            self._json(200, {"ok": True, "count": len(hooks_list), "hooks": hooks_list, "engine": HOOKS_AVAILABLE})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        request_path = _normalize_local_route(self.path)
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
        if request_path == "/file":
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
        if request_path == "/memory/search":
            query = body.get("query", "recent")
            limit = body.get("limit", 20)
            wing = body.get("wing")
            room = body.get("room")
            hall = body.get("hall")
            tunnel = body.get("tunnel")
            params = {"query": query, "limit": limit}
            if wing: params["wing"] = wing
            if room: params["room"] = room
            if hall: params["hall"] = hall
            if tunnel: params["tunnel"] = tunnel
            code, payload = claudemem_proxy(
                "/api/search", "GET", params, timeout=5
            )
            # Transform MCP content format to structured results for frontend
            if isinstance(payload, dict) and "content" in payload:
                # claude-mem returns {content: [{type: "text", text: "..."}]}
                # Frontend expects {results: [{id, title, text, ...}]}
                text = ""
                for block in payload.get("content", []):
                    if isinstance(block, dict):
                        text += block.get("text", "")
                self._json(code, {"ok": True, "results": [{"id": 0, "text": text}], "raw": text})
            else:
                self._json(code, payload)
            return

        # ── /memory/save — proxy to claude-mem ────────────────────────────
        if request_path == "/memory/save":
            body = _normalize_memory_save_payload(body)
            # Pass through palace tags if present; default wing=Karma_SADE hall=hall_events
            palace_tags = {
                "wing": body.get("wing") or "Karma_SADE",
                "room": body.get("room"),
                "hall": body.get("hall") or "hall_events",
                "tunnel": body.get("tunnel"),
            }
            body.update(palace_tags)
            code, payload = claudemem_proxy("/api/memory/save", "POST", body, timeout=5)
            # Backfill palace tags into sqlite if id present
            try:
                obs_id = None
                if isinstance(payload, dict):
                    obs_id = payload.get("id") or payload.get("obs_id")
                if obs_id:
                    _tag_observation(obs_id, palace_tags["wing"], palace_tags["room"], palace_tags["hall"], palace_tags["tunnel"])
            except Exception as e:
                print(f"[palace] tag backfill failed: {e}")
            self._json(code, payload)
            return

        # ── /memory/ingest-feed — permissioned feeder (projects/convos/general) ──
        if request_path == "/memory/ingest-feed":
            mode = str(body.get("mode", "general")).strip().lower()
            if mode not in {"projects", "convos", "general"}:
                self._json(422, {"ok": False, "error": "mode must be one of: projects, convos, general"})
                return
            root = body.get("path", WORK_DIR) or WORK_DIR
            limit = int(body.get("limit", 100))
            target = os.path.normpath(os.path.join(WORK_DIR, str(root))) if not os.path.isabs(str(root)) else os.path.normpath(str(root))
            if not target.startswith(WORK_DIR):
                self._json(403, {"ok": False, "error": "path outside project"})
                return
            allowed, reason = _check_tool_permission(
                "shell",
                {"command": f"python Scripts/nexus_ingestion_feeder.py --mode {mode} --path {target} --limit {limit}"},
            )
            if not allowed:
                self._json(403, {"ok": False, "error": f"Blocked by permission engine: {reason}"})
                return
            result = _run_ingestion_feed(mode=mode, root_path=target, limit=limit)
            code = 200 if result.get("ok") else 500
            self._json(code, result)
            return

        # ── MCP façade: mempalace-compatible tool names ───────────────────
        if request_path == "/mcp/mempalace_search":
            q = body.get("query", "")
            limit = body.get("limit", 20)
            code, payload = claudemem_proxy("/api/search", "GET", {"query": q, "limit": limit}, timeout=5)
            self._json(code, payload)
            return
        if request_path == "/mcp/mempalace_status":
            code, payload = _claudemem_status_payload(timeout=5)
            self._json(code, payload)
            return
        if request_path == "/memory/search/palace":
            # Direct sqlite search with palace tags
            wing = body.get("wing")
            room = body.get("room")
            hall = body.get("hall")
            tunnel = body.get("tunnel")
            limit = int(body.get("limit") or 20)
            try:
                _ensure_palace_columns()
                conn = sqlite3.connect(CLAUDEMEM_DB, timeout=5)
                conn.row_factory = sqlite3.Row
                where = []
                args = []
                for col, val in (("wing", wing), ("room", room), ("hall", hall), ("tunnel", tunnel)):
                    if val:
                        where.append(f"{col}=?")
                        args.append(val)
                wh = " WHERE " + " AND ".join(where) if where else ""
                rows = conn.execute(
                    f"SELECT id,title,narrative,text,wing,room,hall,tunnel,created_at FROM observations{wh} ORDER BY created_at DESC LIMIT ?",
                    (*args, limit),
                ).fetchall()
                results = []
                for r in rows:
                    results.append({
                        "id": r["id"],
                        "title": r["title"],
                        "text": r["text"] or r["narrative"] or "",
                        "wing": r["wing"],
                        "room": r["room"],
                        "hall": r["hall"],
                        "tunnel": r["tunnel"],
                        "created_at": r["created_at"],
                    })
                conn.close()
                self._json(200, {"ok": True, "results": results})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
            return

        # ── /self-edit/* — Self-Edit Engine (Sprint 4d) ──────────────────
        if request_path == "/self-edit/propose":
            from Scripts.self_edit_service import propose
            result = propose(
                body.get("file_path", ""), body.get("new_content", ""),
                body.get("description", ""), body.get("risk_level", "low"),
            )
            self._json(200 if result.get("ok") else 400, result)
            return
        if request_path.startswith("/self-edit/approve/"):
            from Scripts.self_edit_service import approve
            pid = int(request_path.split("/")[-1])
            result = approve(pid)
            self._json(200 if result.get("ok") else 404, result)
            return
        if request_path.startswith("/self-edit/reject/"):
            from Scripts.self_edit_service import reject
            pid = int(request_path.split("/")[-1])
            result = reject(pid)
            self._json(200 if result.get("ok") else 404, result)
            return

        # ── /shell — Execute shell command (R2: shell from UI) ──────────────
        if request_path == "/shell":
            cmd = body.get("command", "").strip()
            if not cmd:
                self._json(422, {"ok": False, "error": "command required"})
                return
            allowed, reason = _check_tool_permission("shell", {"command": cmd})
            if not allowed:
                self._json(403, {"ok": False, "error": f"Blocked by permission engine: {reason}"})
                return
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=WORK_DIR, timeout=30, encoding="utf-8", errors="replace")
                result = {
                    "ok": True, "exit_code": r.returncode,
                    "stdout": r.stdout[:8000], "stderr": r.stderr[:2000],
                }
                _post_tool_hook("shell", {"command": cmd}, result)
                self._json(200, result)
            except subprocess.TimeoutExpired:
                self._json(504, {"ok": False, "error": "Command timed out (30s)"})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
            return

        # ── /email/send — CC sends email to Colby ──────────────────────────
        if request_path == "/email/send":
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
        if request_path == "/email/inbox":
            if not GMAIL_AVAILABLE:
                self._json(503, {"ok": False, "error": "Gmail not available"})
                return
            limit = int(body.get("limit", 10))
            msgs = check_inbox(limit)
            self._json(200, {"ok": True, "messages": msgs})
            return

        if request_path not in ("/cc", "/cc/stream"):
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

        # S160: Inject user preferences + output style into message context
        user_prefs = body.get("user_preferences", "").strip()
        output_style = body.get("output_style", "").strip()
        if user_prefs or output_style:
            pref_prefix = ""
            if user_prefs:
                pref_prefix += f"[USER PREFERENCES: {user_prefs[:500]}]\n"
            if output_style:
                pref_prefix += f"[OUTPUT STYLE: {output_style}]\n"
            message = pref_prefix + message

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

        def _acquire_cc_lock():
            global _lock_acquired_at, _current_proc
            if _proc_lock.acquire(blocking=False):
                _lock_acquired_at = time.time()
                return True
            if time.time() - _lock_acquired_at > LOCK_STALE_SECONDS:
                print(f"[cc-server] STALE LOCK detected ({int(time.time() - _lock_acquired_at)}s). Killing orphan subprocess.")
                proc = _current_proc
                if proc and proc.poll() is None:
                    try:
                        proc.kill()
                        proc.wait(timeout=3)
                    except Exception:
                        pass
                _current_proc = None
                try:
                    _proc_lock.release()
                except RuntimeError:
                    pass
                if _proc_lock.acquire(blocking=False):
                    _lock_acquired_at = time.time()
                    return True
            self._json(429, {"ok": False, "error": "Another request is in progress. Wait or cancel first."})
            return False

        try:
            # ── /cc/stream — SSE streaming endpoint ──────────────────────
            if request_path == "/cc/stream":
                lock_held = False
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self._cors()  # H3: CORS on stream
                self.end_headers()
                stream_full_text = []  # S155: accumulate full response for memory capture
                # P2: Crash-safe — write user message BEFORE API call
                # Codex CP1: Wire load_transcript for resume after restart
                _conv_id = _normalize_conversation_id(self.headers.get("x-conversation-id", "default"))
                transcript_context = ""
                prior_transcript = []
                if NEXUS_AGENT_AVAILABLE:
                    # Load prior conversation context for this conversation-id
                    prior_transcript = load_transcript(_conv_id, limit=100)
                    transcript_context = _build_recovered_transcript_context(prior_transcript)
                    recall_answer = _deterministic_transcript_boundary_answer(message, prior_transcript)
                    if recall_answer:
                        append_transcript(_conv_id, {"role": "user", "content": message, "ts": time.time()})
                        append_transcript(_conv_id, {"role": "assistant", "content": recall_answer, "ts": time.time()})
                        self.wfile.write(f"data: {json.dumps({'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': recall_answer}], 'model': 'transcript-recall'}}, ensure_ascii=False)}\n\n".encode())
                        self.wfile.write(f"data: {json.dumps({'type': 'result', 'result': recall_answer, 'model': 'transcript-recall', 'total_cost_usd': 0, 'provider': 'transcript'}, ensure_ascii=False)}\n\n".encode())
                        self.wfile.flush()
                        self.close_connection = True
                        return
                    workspace_answer = _deterministic_workspace_answer(message)
                    if workspace_answer:
                        append_transcript(_conv_id, {"role": "user", "content": message, "ts": time.time()})
                        append_transcript(_conv_id, {"role": "assistant", "content": workspace_answer, "ts": time.time()})
                        self.wfile.write(f"data: {json.dumps({'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': workspace_answer}], 'model': 'workspace-shortcut'}}, ensure_ascii=False)}\n\n".encode())
                        self.wfile.write(f"data: {json.dumps({'type': 'result', 'result': workspace_answer, 'model': 'workspace-shortcut', 'total_cost_usd': 0, 'provider': 'workspace'}, ensure_ascii=False)}\n\n".encode())
                        self.wfile.flush()
                        self.close_connection = True
                        return
                    append_transcript(_conv_id, {"role": "user", "content": message, "ts": time.time()})
                if not _acquire_cc_lock():
                    self.close_connection = True
                    return
                lock_held = True
                try:
                    t_start = time.time()
                    first_token_sent = False
                    for line in run_cc_stream(message, effort=effort, model=model, budget=budget, transcript_context=transcript_context, conversation_id=_conv_id):
                        if not first_token_sent:
                            _last_latency["first_token_ms"] = int((time.time() - t_start) * 1000)
                            first_token_sent = True
                        self.wfile.write(f"data: {line}\n\n".encode())
                        self.wfile.flush()
                        # Accumulate assistant text from stream for memory capture
                        try:
                            obj = json.loads(line)
                            if obj.get("type") == "assistant":
                                content = obj.get("message", {}).get("content", [])
                                if isinstance(content, list):
                                    for block in content:
                                        if isinstance(block, dict) and block.get("type") == "text":
                                            stream_full_text.append(block.get("text", ""))
                        except Exception:
                            pass
                    _last_latency["total_ms"] = int((time.time() - t_start) * 1000)
                except BrokenPipeError:
                    pass  # Client disconnected (cancel)
                except Exception as e:
                    err_str = str(e)
                    # ── EscapeHatch: rate limit detection → OpenRouter fallback ──
                    if OPENROUTER_API_KEY and ("rate" in err_str.lower() or "overloaded" in err_str.lower() or "529" in err_str or "429" in err_str):
                        print(f"[escapehatch] CC rate-limited, falling back to OpenRouter")
                        try:
                            or_text, or_model = _openrouter_fallback(message)
                            stream_full_text.append(or_text)
                            # Send as synthetic SSE events
                            synth_msg = json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": or_text}]}})
                            synth_result = json.dumps({"type": "result", "model": or_model, "total_cost_usd": 0, "escapehatch": True})
                            self.wfile.write(f"data: {synth_msg}\n\n".encode())
                            self.wfile.write(f"data: {synth_result}\n\n".encode())
                            self.wfile.flush()
                            print(f"[escapehatch] Fallback response delivered: {len(or_text)} chars via {or_model}")
                        except Exception as or_err:
                            print(f"[escapehatch] OpenRouter also failed: {or_err}")
                            # Tier 3: Nexus Agent — Karma's own agentic loop
                            if NEXUS_AGENT_AVAILABLE:
                                print(f"[nexus-agent] All external providers failed. Running own agentic loop.")
                                try:
                                    ctx = build_context_prefix(message)
                                    for agent_line in nexus_run_agent(message, system_prompt=ctx):
                                        self.wfile.write(f"data: {agent_line}\n\n".encode())
                                        self.wfile.flush()
                                        try:
                                            aobj = json.loads(agent_line)
                                            if aobj.get("type") == "assistant":
                                                for ab in aobj.get("message",{}).get("content",[]):
                                                    if isinstance(ab, dict) and ab.get("type") == "text":
                                                        stream_full_text.append(ab.get("text",""))
                                        except Exception:
                                            pass
                                except Exception as ne:
                                    print(f"[nexus-agent] Also failed: {ne}")
                                    err = json.dumps({"type": "error", "error": f"All tiers failed. CC: {err_str}. OR: {or_err}. Nexus: {ne}"})
                                    try:
                                        self.wfile.write(f"data: {err}\n\n".encode())
                                        self.wfile.flush()
                                    except Exception:
                                        pass
                            else:
                                err = json.dumps({"type": "error", "error": f"All providers failed. CC: {err_str}. OpenRouter: {or_err}"})
                                try:
                                    self.wfile.write(f"data: {err}\n\n".encode())
                                    self.wfile.flush()
                                except Exception:
                                    pass
                    else:
                        err = json.dumps({"type": "error", "error": err_str})
                        try:
                            self.wfile.write(f"data: {err}\n\n".encode())
                            self.wfile.flush()
                        except Exception:
                            pass
                # S155: Save stream response to claude-mem (was missing — data loss gap)
                assistant_text = "".join(stream_full_text)
                if assistant_text:
                    _auto_save_memory(message, assistant_text)
                # Codex CP1: Append assistant response to transcript for crash-safe recovery
                if NEXUS_AGENT_AVAILABLE and assistant_text:
                    append_transcript(_conv_id, {"role": "assistant", "content": assistant_text[:2000], "ts": time.time()})
                # ── Fire Stop hooks after stream completes (Sprint 3a) ───
                if HOOKS_AVAILABLE:
                    try:
                        _hooks.fire("Stop", {"session_id": load_session_id(_conv_id) or "", "message": message, "assistant_text": assistant_text})
                    except Exception as e:
                        print(f"[hooks] Stop error: {e}")
                if lock_held:
                    try:
                        _proc_lock.release()
                    except RuntimeError:
                        pass
                self.close_connection = True
                return

            # ── /cc — batch JSON endpoint (backward compat) ──────────────
            try:
                batch_lock_held = False
                batch_transcript_context = ""
                batch_conv_id = _normalize_conversation_id(self.headers.get("x-conversation-id", "default"))
                if NEXUS_AGENT_AVAILABLE:
                    batch_prior_transcript = load_transcript(batch_conv_id, limit=100)
                    recall_answer = _deterministic_transcript_boundary_answer(message, batch_prior_transcript)
                    if recall_answer:
                        append_transcript(batch_conv_id, {"role": "user", "content": message, "ts": time.time()})
                        append_transcript(batch_conv_id, {"role": "assistant", "content": recall_answer, "ts": time.time()})
                        self._json(200, {"ok": True, "response": recall_answer})
                        return
                    workspace_answer = _deterministic_workspace_answer(message)
                    if workspace_answer:
                        append_transcript(batch_conv_id, {"role": "user", "content": message, "ts": time.time()})
                        append_transcript(batch_conv_id, {"role": "assistant", "content": workspace_answer, "ts": time.time()})
                        self._json(200, {"ok": True, "response": workspace_answer})
                        return
                    batch_transcript_context = _build_recovered_transcript_context(batch_prior_transcript)
                    append_transcript(batch_conv_id, {"role": "user", "content": message, "ts": time.time()})
                if not _acquire_cc_lock():
                    return
                batch_lock_held = True
                response_text = run_cc(message, effort=effort, model=model, budget=budget, transcript_context=batch_transcript_context, conversation_id=batch_conv_id)
                self._json(200, {"ok": True, "response": response_text})
                # Gate 6: Auto-save chat turn to claude-mem (fire-and-forget)
                _auto_save_memory(message, response_text)
                if NEXUS_AGENT_AVAILABLE and response_text:
                    append_transcript(batch_conv_id, {"role": "assistant", "content": response_text[:2000], "ts": time.time()})
                # ── Fire Stop hooks after batch completes (Sprint 3a) ────
                if HOOKS_AVAILABLE:
                    try:
                        _hooks.fire("Stop", {
                            "session_id": load_session_id(batch_conv_id) or "",
                            "message": message,
                            "assistant_text": response_text,
                        })
                    except Exception as e:
                        print(f"[hooks] Stop error: {e}")
                if batch_lock_held:
                    try:
                        _proc_lock.release()
                    except RuntimeError:
                        pass
            except subprocess.TimeoutExpired:
                self._json(504, {"ok": False, "error": f"CC subprocess timed out after {API_TIMEOUT}s"})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
        finally:
            pass

if __name__ == "__main__":
    print(f"[cc-server] Starting on port {PORT}")
    print(f"[cc-server] Auth: {'ENABLED' if TOKEN else 'DISABLED (set HUB_CHAT_TOKEN)'}")
    print(f"[cc-server] Inference: CC subprocess (claude -p --resume) — real CC with session continuity")
    print(f"[cc-server] Session file: {SESSION_FILE}")
    # S155: Start CC heartbeat (posts to bus + cortex every 10 min)
    try:
        from Scripts.cc_heartbeat import start_heartbeat
        start_heartbeat()
        print("[cc-server] Heartbeat: STARTED (10 min interval)")
    except Exception as e:
        print(f"[cc-server] Heartbeat: FAILED ({e})")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), CCHandler)
    server.serve_forever()

