"""
k2_tools.py — Structured tool registry for Karma's K2 MCP surface.
Each tool does one thing, returns typed JSON: {ok: bool, result?: dict, error?: str}
Designed to be imported by aria.py and wired to /api/tools/list and /api/tools/execute.
"""

import os
import re
import glob
import subprocess
from datetime import datetime
from pathlib import Path

# Configurable paths (overridable for testing)
SCRATCHPAD_PATH = "/mnt/c/dev/Karma/k2/cache/scratchpad.md"

# ── Tool Registry ────────────────────────────────────────────────────────────

TOOLS = []


def _register(name, description, input_schema, handler):
    """Register a tool with its schema and handler function."""
    TOOLS.append({
        "name": name,
        "description": description,
        "input_schema": input_schema,
        "handler": handler,
    })


def list_tools():
    """Return all registered tools (without handler functions — for API response)."""
    return [{"name": t["name"], "description": t["description"], "input_schema": t["input_schema"]} for t in TOOLS]


def execute_tool(name, input_data):
    """Execute a tool by name with given input. Returns {ok, result} or {ok: false, error}."""
    for tool in TOOLS:
        if tool["name"] == name:
            try:
                return tool["handler"](input_data)
            except Exception as e:
                return {"ok": False, "error": f"Tool '{name}' raised: {str(e)}"}
    return {"ok": False, "error": f"Unknown tool: {name}"}


# ── Tool Handlers ────────────────────────────────────────────────────────────

def _file_read(input_data):
    path = input_data.get("path")
    if not path:
        return {"ok": False, "error": "path is required"}
    if not os.path.exists(path):
        return {"ok": True, "result": {"content": None, "size": 0, "exists": False, "modified": None}}
    try:
        stat = os.stat(path)
        with open(path, "r", errors="replace") as f:
            content = f.read()
        return {"ok": True, "result": {
            "content": content,
            "size": stat.st_size,
            "exists": True,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _file_write(input_data):
    path = input_data.get("path")
    content = input_data.get("content")
    if not path or content is None:
        return {"ok": False, "error": "path and content are required"}
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            written = f.write(content)
        return {"ok": True, "result": {"bytes_written": written}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _file_list(input_data):
    path = input_data.get("path", ".")
    pattern = input_data.get("pattern")
    if not os.path.isdir(path):
        return {"ok": False, "error": f"Not a directory: {path}"}
    try:
        entries = []
        for name in sorted(os.listdir(path)):
            full = os.path.join(path, name)
            if pattern and not glob.fnmatch.fnmatch(name, pattern):
                continue
            entry = {
                "name": name,
                "type": "directory" if os.path.isdir(full) else "file",
                "size": os.path.getsize(full) if os.path.isfile(full) else 0,
            }
            entries.append(entry)
        return {"ok": True, "result": {"entries": entries}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _file_search(input_data):
    path = input_data.get("path", ".")
    pattern = input_data.get("pattern")
    if not pattern:
        return {"ok": False, "error": "pattern is required"}
    try:
        matches = []
        for root, dirs, files in os.walk(path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", errors="replace") as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line):
                                matches.append({"file": fpath, "line": i, "text": line.rstrip()})
                except (PermissionError, IsADirectoryError):
                    continue
        return {"ok": True, "result": {"matches": matches}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


PYTHON_BIN = os.environ.get("K2_PYTHON_BIN", "python3")

def _python_exec(input_data):
    code = input_data.get("code")
    if not code:
        return {"ok": False, "error": "code is required"}
    try:
        result = subprocess.run(
            [PYTHON_BIN, "-c", code],
            capture_output=True, text=True, timeout=30
        )
        return {"ok": True, "result": {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }}
    except subprocess.TimeoutExpired:
        return {"ok": True, "result": {"stdout": "", "stderr": "timeout after 30s", "exit_code": -1}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _service_status(input_data):
    name = input_data.get("name")
    if not name:
        return {"ok": False, "error": "name is required"}
    # Sanitize: only allow alphanumeric + dash + underscore
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return {"ok": False, "error": "Invalid service name"}
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "status", name],
            capture_output=True, text=True, timeout=10
        )
        active = "active (running)" in result.stdout
        return {"ok": True, "result": {
            "active": active,
            "output": result.stdout[:2000],
            "exit_code": result.returncode,
        }}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _service_restart(input_data):
    name = input_data.get("name")
    if not name:
        return {"ok": False, "error": "name is required"}
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return {"ok": False, "error": "Invalid service name"}
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", name],
            capture_output=True, text=True, timeout=30
        )
        return {"ok": True, "result": {
            "restarted": result.returncode == 0,
            "output": result.stdout[:2000] + result.stderr[:2000],
            "exit_code": result.returncode,
        }}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _scratchpad_read(input_data):
    try:
        if os.path.exists(SCRATCHPAD_PATH):
            with open(SCRATCHPAD_PATH, "r") as f:
                content = f.read()
            modified = datetime.fromtimestamp(os.path.getmtime(SCRATCHPAD_PATH)).isoformat()
        else:
            content = ""
            modified = None
        return {"ok": True, "result": {"content": content, "modified": modified}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _scratchpad_write(input_data):
    content = input_data.get("content")
    mode = input_data.get("mode", "append")
    if content is None:
        return {"ok": False, "error": "content is required"}
    try:
        os.makedirs(os.path.dirname(SCRATCHPAD_PATH), exist_ok=True)
        if mode == "replace":
            with open(SCRATCHPAD_PATH, "w") as f:
                f.write(content)
        else:  # append
            with open(SCRATCHPAD_PATH, "a") as f:
                f.write(content)
        size = os.path.getsize(SCRATCHPAD_PATH)
        return {"ok": True, "result": {"size": size}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── Register All Tools ───────────────────────────────────────────────────────

_register("file_read", "Read a file's contents with metadata (size, modified, exists).", {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "Absolute path to file"}
    },
    "required": ["path"]
}, _file_read)

_register("file_write", "Write content to a file. Creates parent directories if needed.", {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "Absolute path to write"},
        "content": {"type": "string", "description": "File content to write"}
    },
    "required": ["path", "content"]
}, _file_write)

_register("file_list", "List directory contents with optional glob pattern filter.", {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "Directory path to list"},
        "pattern": {"type": "string", "description": "Optional glob pattern (e.g. '*.py')"}
    },
    "required": ["path"]
}, _file_list)

_register("file_search", "Search for a regex pattern in files under a directory (recursive grep).", {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "Directory to search in"},
        "pattern": {"type": "string", "description": "Regex pattern to match"}
    },
    "required": ["path", "pattern"]
}, _file_search)

_register("python_exec", "Execute Python code and return stdout/stderr/exit_code.", {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Python code to execute"}
    },
    "required": ["code"]
}, _python_exec)

_register("service_status", "Check systemd service status (e.g. aria, ollama).", {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Service name (e.g. 'aria', 'ollama')"}
    },
    "required": ["name"]
}, _service_status)

_register("service_restart", "Restart a systemd service (requires sudo).", {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Service name to restart"}
    },
    "required": ["name"]
}, _service_restart)

_register("scratchpad_read", "Read Karma's K2 scratchpad (working memory).", {
    "type": "object",
    "properties": {},
}, _scratchpad_read)

_register("scratchpad_write", "Write to Karma's K2 scratchpad. Mode: 'append' (default) or 'replace'.", {
    "type": "object",
    "properties": {
        "content": {"type": "string", "description": "Content to write"},
        "mode": {"type": "string", "enum": ["append", "replace"], "description": "Write mode (default: append)"}
    },
    "required": ["content"]
}, _scratchpad_write)
