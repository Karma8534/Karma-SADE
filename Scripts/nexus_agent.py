"""
Nexus Agent — Karma's own agentic loop, independent of CC subprocess.
S157: The primitive that makes Karma a peer, not a wrapper.

Architecture: message → build context → LLM call (OpenRouter) → parse tool calls →
execute tools locally → feed results back → loop until done → stream SSE events.

This replaces CC subprocess for autonomous operation when CC is unavailable,
rate-limited, or when Karma needs to act independently.
"""

import json, os, subprocess, urllib.request, urllib.error, time, re, glob as globmod, shutil, uuid, datetime

WORK_DIR = r"C:\Users\raest\Documents\Karma_SADE"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-6"
FALLBACK_MODEL = "google/gemini-2.0-flash"
MAX_ITERATIONS = 12
MAX_OUTPUT_TOKENS = 4096

# ── Tool Definitions (Anthropic format) ──────────────────────────────────────

TOOLS = [
    {
        "name": "Read",
        "description": "Read a file from disk. Returns file content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Absolute path to file"},
                "offset": {"type": "integer", "description": "Line offset (0-based)"},
                "limit": {"type": "integer", "description": "Max lines to read"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "Write",
        "description": "Write content to a file (creates or overwrites).",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Absolute path"},
                "content": {"type": "string", "description": "File content"},
            },
            "required": ["file_path", "content"],
        },
    },
    {
        "name": "Edit",
        "description": "Replace exact string in a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Absolute path"},
                "old_string": {"type": "string", "description": "Text to find"},
                "new_string": {"type": "string", "description": "Replacement text"},
            },
            "required": ["file_path", "old_string", "new_string"],
        },
    },
    {
        "name": "SelfEdit",
        "description": "Safely edit a file with backup and optional verification rollback.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Absolute path"},
                "old_string": {"type": "string", "description": "Text to find"},
                "new_string": {"type": "string", "description": "Replacement text"},
                "verify_cmd": {"type": "string", "description": "Optional command to verify the edit"},
            },
            "required": ["file_path", "old_string", "new_string"],
        },
    },
    {
        "name": "ImproveRun",
        "description": "Run the Vesper improvement cycle.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "Bash",
        "description": "Execute a shell command. Returns stdout/stderr.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default 30)"},
            },
            "required": ["command"],
        },
    },
    {
        "name": "Glob",
        "description": "Find files matching a glob pattern.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern (e.g. **/*.py)"},
                "path": {"type": "string", "description": "Base directory"},
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "Grep",
        "description": "Search file contents for a regex pattern.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern"},
                "path": {"type": "string", "description": "Directory to search"},
            },
            "required": ["pattern"],
        },
    },
]

# ── Tool Execution ───────────────────────────────────────────────────────────

def _exec_tool(name, input_data):
    """Execute a tool and return the result string. P5: permission-gated."""
    allowed, reason = check_permission(name, input_data)
    if not allowed:
        return f"PERMISSION DENIED: {reason}"
    try:
        if name == "Read":
            fp = input_data["file_path"]
            if not os.path.isabs(fp):
                fp = os.path.join(WORK_DIR, fp)
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            offset = input_data.get("offset", 0)
            limit = input_data.get("limit", 2000)
            selected = lines[offset:offset + limit]
            return "".join(f"{offset + i + 1}\t{line}" for i, line in enumerate(selected))

        elif name == "Write":
            fp = input_data["file_path"]
            if not os.path.isabs(fp):
                fp = os.path.join(WORK_DIR, fp)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(input_data["content"])
            return f"Written to {fp}"

        elif name == "Edit":
            fp = input_data["file_path"]
            if not os.path.isabs(fp):
                fp = os.path.join(WORK_DIR, fp)
            with open(fp, "r", encoding="utf-8") as f:
                content = f.read()
            old = input_data["old_string"]
            new = input_data["new_string"]
            if old not in content:
                return f"ERROR: old_string not found in {fp}"
            if content.count(old) > 1:
                return f"ERROR: old_string appears {content.count(old)} times — not unique"
            content = content.replace(old, new, 1)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Edited {fp}"

        elif name == "SelfEdit":
            return json.dumps(self_edit(
                input_data["file_path"],
                input_data["old_string"],
                input_data["new_string"],
                input_data.get("verify_cmd"),
            ), ensure_ascii=False)

        elif name == "ImproveRun":
            from Scripts.vesper_improve import run as vesper_run
            vesper_run()
            return "ImproveRun completed"

        elif name == "Bash":
            cmd = input_data["command"]
            timeout = input_data.get("timeout", 30)
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd=WORK_DIR, encoding="utf-8", errors="replace",
            )
            out = result.stdout[:8000]
            if result.stderr:
                out += f"\nSTDERR: {result.stderr[:2000]}"
            if result.returncode != 0:
                out += f"\nExit code: {result.returncode}"
            return out or "(no output)"

        elif name == "Glob":
            pattern = input_data["pattern"]
            base = input_data.get("path", WORK_DIR)
            matches = sorted(globmod.glob(os.path.join(base, pattern), recursive=True))[:50]
            return "\n".join(matches) if matches else "(no matches)"

        elif name == "Grep":
            pattern = input_data["pattern"]
            path = input_data.get("path", WORK_DIR)
            try:
                result = subprocess.run(
                    ["rg", "--no-heading", "-n", pattern, path],
                    capture_output=True, text=True, timeout=10,
                    encoding="utf-8", errors="replace",
                )
                return result.stdout[:8000] or "(no matches)"
            except FileNotFoundError:
                # rg not available, use findstr on Windows
                result = subprocess.run(
                    f'findstr /S /R /N "{pattern}" "{path}\\*"',
                    shell=True, capture_output=True, text=True, timeout=10,
                )
                return result.stdout[:8000] or "(no matches)"

        else:
            return f"Unknown tool: {name}"
    except Exception as e:
        return f"Tool error: {e}"

# ── LLM Call ─────────────────────────────────────────────────────────────────

def _call_llm(messages, tools=None, model=None):
    """Call OpenRouter with tool support. Returns parsed response."""
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    body = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "max_tokens": MAX_OUTPUT_TOKENS,
    }
    if tools:
        body["tools"] = [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]}} for t in tools]

    payload = json.dumps(body).encode()
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hub.arknexus.net",
        "X-Title": "Karma Nexus Agent",
    }
    req = urllib.request.Request(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        data=payload, headers=headers, method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read())

def self_edit(file_path, old_string, new_string, verify_cmd=None):
    """Safely edit a file with backup and optional verification rollback."""
    try:
        fp = file_path
        if not os.path.isabs(fp):
            fp = os.path.join(WORK_DIR, fp)
        fp = os.path.normpath(fp)
        if not fp.startswith(WORK_DIR):
            return {"ok": False, "error": f"path outside WORK_DIR: {fp}", "file_path": fp}

        if not os.path.exists(fp):
            return {"ok": False, "error": f"file not found: {fp}", "file_path": fp}

        backup_path = fp + ".self_edit_backup"
        shutil.copy2(fp, backup_path)

        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()

        old_count = content.count(old_string)
        if old_count == 0:
            shutil.copy2(backup_path, fp)
            return {
                "ok": False,
                "error": "old_string not found",
                "file_path": fp,
                "backup_path": backup_path,
            }
        if old_count > 1:
            shutil.copy2(backup_path, fp)
            return {
                "ok": False,
                "error": f"old_string appears {old_count} times",
                "file_path": fp,
                "backup_path": backup_path,
            }

        updated = content.replace(old_string, new_string, 1)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(updated)

        verify_result = None
        if verify_cmd:
            verify_proc = subprocess.run(
                verify_cmd,
                shell=True,
                cwd=WORK_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            verify_result = {
                "command": verify_cmd,
                "returncode": verify_proc.returncode,
                "stdout": verify_proc.stdout[:4000],
                "stderr": verify_proc.stderr[:4000],
            }
            if verify_proc.returncode != 0:
                shutil.copy2(backup_path, fp)
                return {
                    "ok": False,
                    "error": "verification failed; reverted",
                    "file_path": fp,
                    "backup_path": backup_path,
                    "verify": verify_result,
                }

        return {
            "ok": True,
            "file_path": fp,
            "backup_path": backup_path,
            "replaced": 1,
            "verify": verify_result,
        }
    except Exception as e:
        try:
            if "backup_path" in locals() and os.path.exists(backup_path) and os.path.exists(fp):
                shutil.copy2(backup_path, fp)
        except Exception:
            pass
        return {
            "ok": False,
            "error": str(e),
            "file_path": fp if "fp" in locals() else file_path,
            "backup_path": backup_path if "backup_path" in locals() else None,
        }

# ── Agentic Loop ─────────────────────────────────────────────────────────────

def run_agent(message, system_prompt="", model=None):
    """
    Karma's own agentic loop. Yields SSE-formatted JSON lines.
    decide → act → verify → repeat until done or max iterations.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})

    for iteration in range(MAX_ITERATIONS):
        # P3: Auto-compact if context is getting too large
        if _estimate_chars(messages) > COMPACTION_THRESHOLD:
            messages = _compact_messages(messages, model=model)

        try:
            response = _call_llm(messages, tools=TOOLS, model=model)
        except urllib.error.HTTPError as e:
            if e.code == 429 and (model or DEFAULT_MODEL) != FALLBACK_MODEL:
                print(f"[nexus-agent] Rate limited, falling back to {FALLBACK_MODEL}")
                response = _call_llm(messages, tools=TOOLS, model=FALLBACK_MODEL)
            else:
                yield json.dumps({"type": "error", "error": f"LLM call failed: {e}"})
                return

        choice = response.get("choices", [{}])[0]
        msg = choice.get("message", {})
        finish_reason = choice.get("finish_reason", "")

        # Add assistant message to history
        messages.append(msg)

        # Stream text content
        text = msg.get("content", "")
        if text:
            yield json.dumps({
                "type": "assistant",
                "message": {"content": [{"type": "text", "text": text}]},
            })

        # Check for tool calls
        tool_calls = msg.get("tool_calls", [])
        if not tool_calls or finish_reason == "stop":
            # Done — emit result
            yield json.dumps({
                "type": "result",
                "result": text,
                "model": response.get("model", model or DEFAULT_MODEL),
                "total_cost_usd": 0,
                "iterations": iteration + 1,
                "nexus_agent": True,
            })
            return

        # Execute each tool call
        for tc in tool_calls:
            func = tc.get("function", {})
            tool_name = func.get("name", "")
            try:
                tool_input = json.loads(func.get("arguments", "{}"))
            except json.JSONDecodeError:
                tool_input = {}
            tool_id = tc.get("id", f"call_{iteration}_{tool_name}")

            # Stream tool_use event
            yield json.dumps({
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "id": tool_id, "name": tool_name, "input": tool_input}]},
            })

            # Execute
            result_text = _exec_tool(tool_name, tool_input)

            # Stream tool_result event
            yield json.dumps({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "tool_name": tool_name,
                "content": result_text[:4000],
            })

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "content": result_text[:4000],
            })

    # Max iterations reached
    yield json.dumps({
        "type": "result",
        "result": "(max iterations reached)",
        "model": model or DEFAULT_MODEL,
        "total_cost_usd": 0,
        "iterations": MAX_ITERATIONS,
        "nexus_agent": True,
    })


# ── Crash-Safe Transcript ────────────────────────────────────────────────────

TRANSCRIPT_DIR = os.path.join(WORK_DIR, "tmp", "transcripts")
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
TRANSCRIPT_MESSAGE_TYPES = {"user", "assistant", "system", "tool", "attachment"}

def _transcript_path(session_id):
    return os.path.join(TRANSCRIPT_DIR, f"{session_id}.jsonl")

def _iso_timestamp(ts=None):
    if ts is None:
        return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
    return datetime.datetime.fromtimestamp(float(ts), datetime.UTC).isoformat().replace("+00:00", "Z")

def _normalize_transcript_entry(session_id, entry):
    role = str(entry.get("role", "")).strip().lower()
    content = str(entry.get("content", ""))
    ts = float(entry.get("ts", time.time()))
    normalized = {
        "type": role if role in TRANSCRIPT_MESSAGE_TYPES else "message",
        "role": role,
        "content": content,
        "timestamp": entry.get("timestamp") or _iso_timestamp(ts),
        "ts": ts,
        "session_id": session_id,
        "cwd": WORK_DIR,
        "uuid": entry.get("uuid") or str(uuid.uuid4()),
    }
    parent_uuid = entry.get("parent_uuid")
    if parent_uuid:
        normalized["parent_uuid"] = str(parent_uuid)
    return normalized

def _coerce_loaded_transcript_entry(entry):
    if not isinstance(entry, dict):
        return None
    if "role" in entry and "content" in entry and "type" not in entry:
        role = str(entry.get("role", "")).strip().lower()
        if role in TRANSCRIPT_MESSAGE_TYPES:
            return {
                "role": role,
                "content": str(entry.get("content", "")),
                "ts": float(entry.get("ts", time.time())),
                "timestamp": entry.get("timestamp") or _iso_timestamp(entry.get("ts", time.time())),
                "session_id": entry.get("session_id", ""),
                "uuid": entry.get("uuid"),
                "parent_uuid": entry.get("parent_uuid"),
            }
    entry_type = str(entry.get("type", "")).strip().lower()
    if entry_type in TRANSCRIPT_MESSAGE_TYPES and "content" in entry:
        return {
            "role": entry_type,
            "content": str(entry.get("content", "")),
            "ts": float(entry.get("ts", time.time())),
            "timestamp": entry.get("timestamp") or _iso_timestamp(entry.get("ts", time.time())),
            "session_id": entry.get("session_id", ""),
            "uuid": entry.get("uuid"),
            "parent_uuid": entry.get("parent_uuid"),
        }
    return None

def _tail_lines(path, max_bytes=8192):
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            if size == 0:
                return []
            read_size = min(size, max_bytes)
            f.seek(-read_size, os.SEEK_END)
            chunk = f.read(read_size).decode("utf-8", errors="replace")
        return [line for line in chunk.splitlines() if line.strip()]
    except Exception:
        return []

def append_transcript(session_id, entry):
    """Append a transcript message plus lightweight tail metadata."""
    path = _transcript_path(session_id)
    normalized = _normalize_transcript_entry(session_id, entry)
    rows = [normalized]
    if normalized["type"] == "user":
        rows.append({
            "type": "last-prompt",
            "session_id": session_id,
            "timestamp": normalized["timestamp"],
            "last_prompt": normalized["content"],
        })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass

def load_transcript(session_id, limit=None):
    """Load transcript messages only, filtering metadata and corrupt lines."""
    path = _transcript_path(session_id)
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    parsed = json.loads(line)
                    loaded = _coerce_loaded_transcript_entry(parsed)
                    if loaded:
                        entries.append(loaded)
                except json.JSONDecodeError:
                    continue
    if limit and limit > 0:
        return entries[-int(limit):]
    return entries

def list_transcript_sessions(limit=10):
    """List recent transcript sessions using tail metadata for fast summaries."""
    sessions = []
    if not os.path.isdir(TRANSCRIPT_DIR):
        return sessions
    for name in os.listdir(TRANSCRIPT_DIR):
        if not name.endswith(".jsonl"):
            continue
        path = os.path.join(TRANSCRIPT_DIR, name)
        session_id = name[:-6]
        last_prompt = ""
        for line in reversed(_tail_lines(path)):
            try:
                parsed = json.loads(line)
            except Exception:
                continue
            if isinstance(parsed, dict) and parsed.get("type") == "last-prompt":
                last_prompt = str(parsed.get("last_prompt", ""))
                break
        sessions.append({
            "session_id": session_id,
            "path": path,
            "mtime": os.path.getmtime(path),
            "last_prompt": last_prompt,
        })
    sessions.sort(key=lambda item: item["mtime"], reverse=True)
    return sessions[:limit]


# ── P3: Auto-Compaction ──────────────────────────────────────────────────────

COMPACTION_THRESHOLD = 80000  # chars in messages before triggering compaction

def _estimate_chars(messages):
    """Rough char count of message history."""
    return sum(len(json.dumps(m)) for m in messages)

def _compact_messages(messages, model=None):
    """Summarize old messages to stay under context limits.
    Keeps system prompt + last 4 messages intact. Summarizes the rest."""
    if len(messages) < 6:
        return messages  # Nothing to compact

    # Split: system (if any) + old messages + recent 4
    system = [m for m in messages[:1] if m.get("role") == "system"]
    rest = messages[len(system):]
    recent = rest[-4:]
    old = rest[:-4]

    if not old:
        return messages

    # Summarize old messages via LLM
    summary_prompt = "Summarize this conversation history in 500 words or less. Preserve: key decisions, tool results, file paths, error messages, and action items. Drop: verbose tool output, repeated content."
    summary_messages = [
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": json.dumps(old, indent=1)[:30000]},
    ]

    try:
        resp = _call_llm(summary_messages, tools=None, model=model or FALLBACK_MODEL)
        summary = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        if summary:
            compacted = system + [
                {"role": "user", "content": f"[COMPACTED HISTORY]\n{summary}"},
                {"role": "assistant", "content": "Understood. I have the context from the compacted history. Continuing."},
            ] + recent
            print(f"[nexus-agent] Compacted: {len(messages)} messages ({_estimate_chars(messages)} chars) → {len(compacted)} messages ({_estimate_chars(compacted)} chars)")
            return compacted
    except Exception as e:
        print(f"[nexus-agent] Compaction failed: {e}")

    return messages  # Return unchanged on failure


# ── P5: Permission Stack ────────────────────────────────────────────────────

# Layered permission gates for tool execution
PERMISSION_RULES = {
    # Tool → permission level: "allow" (always), "gate" (log + allow), "deny" (block)
    "Read": "allow",
    "Glob": "allow",
    "Grep": "allow",
    "Write": "gate",      # Log all writes
    "Edit": "gate",       # Log all edits
    "SelfEdit": "gate",   # Log all self-edits
    "ImproveRun": "gate", # Log improvement cycles
    "Bash": "gate",       # Log all shell commands
}

# Dangerous command patterns — require extra scrutiny
DANGEROUS_PATTERNS = [
    re.compile(r"rm\s+-rf", re.IGNORECASE),
    re.compile(r"del\s+/[sfq]", re.IGNORECASE),
    re.compile(r"format\s+[a-z]:", re.IGNORECASE),
    re.compile(r"DROP\s+TABLE", re.IGNORECASE),
    re.compile(r"DELETE\s+FROM", re.IGNORECASE),
    re.compile(r"git\s+push\s+.*--force", re.IGNORECASE),
    re.compile(r"git\s+reset\s+--hard", re.IGNORECASE),
]

PERMISSION_LOG = os.path.join(WORK_DIR, "tmp", "permission_audit.jsonl")

def check_permission(tool_name, tool_input):
    """Check if a tool call is permitted. Returns (allowed: bool, reason: str)."""
    level = PERMISSION_RULES.get(tool_name, "gate")

    if level == "deny":
        return False, f"Tool {tool_name} is denied by permission stack"

    # Check for dangerous patterns in Bash commands
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(cmd):
                _log_permission("BLOCKED", tool_name, tool_input, f"Dangerous pattern: {pattern.pattern}")
                return False, f"Dangerous command pattern detected: {pattern.pattern}"

    # Check for writes outside WORK_DIR
    if tool_name in ("Write", "Edit", "SelfEdit"):
        fp = tool_input.get("file_path", "")
        if fp and not fp.startswith(WORK_DIR) and not fp.startswith("C:\\Users\\raest\\Documents\\Karma"):
            _log_permission("BLOCKED", tool_name, tool_input, f"Write outside WORK_DIR: {fp}")
            return False, f"Write outside permitted directory: {fp}"

    if level == "gate":
        _log_permission("ALLOWED", tool_name, tool_input, "Gated — logged")

    return True, "ok"

def _log_permission(decision, tool_name, tool_input, reason):
    """Append to permission audit log."""
    try:
        with open(PERMISSION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": time.time(),
                "decision": decision,
                "tool": tool_name,
                "input_summary": str(tool_input)[:200],
                "reason": reason,
            }) + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    # Quick test
    print("[nexus-agent] Self-test...")
    for event in run_agent("What files are in the Memory/ directory? List them."):
        obj = json.loads(event)
        if obj.get("type") == "assistant":
            for block in obj.get("message", {}).get("content", []):
                if block.get("type") == "text":
                    print(f"  TEXT: {block['text'][:100]}")
                elif block.get("type") == "tool_use":
                    print(f"  TOOL: {block['name']}({json.dumps(block['input'])[:80]})")
        elif obj.get("type") == "tool_result":
            print(f"  RESULT: {obj.get('content','')[:100]}")
        elif obj.get("type") == "result":
            print(f"  DONE: iterations={obj.get('iterations')}, model={obj.get('model')}")
    print("[nexus-agent] Self-test complete.")
