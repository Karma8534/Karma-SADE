"""
Nexus Agent — Karma's own agentic loop, independent of CC subprocess.
S157: The primitive that makes Karma a peer, not a wrapper.

Architecture: message → build context → LLM call (OpenRouter) → parse tool calls →
execute tools locally → feed results back → loop until done → stream SSE events.

This replaces CC subprocess for autonomous operation when CC is unavailable,
rate-limited, or when Karma needs to act independently.
"""

import json, os, subprocess, pathlib, urllib.request, urllib.error, time, re, glob as globmod

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
    """Execute a tool and return the result string."""
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

def _transcript_path(session_id):
    return os.path.join(TRANSCRIPT_DIR, f"{session_id}.jsonl")

def append_transcript(session_id, entry):
    """Append-first: write BEFORE processing. Crash-safe."""
    with open(_transcript_path(session_id), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def load_transcript(session_id):
    """Load transcript for resume/recovery."""
    path = _transcript_path(session_id)
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


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
