#!/usr/bin/env python3
"""K2 MCP Server — exposes K2 tools to Claude Code via MCP stdio protocol.

Proxies to Aria /api/tools/execute on K2 (Tailscale: 100.75.109.92:7890)
plus direct K2 Ollama and Vesper state access.

Tools exposed:
  k2_file_read, k2_file_write, k2_file_list, k2_file_search
  k2_python_exec, k2_service_status, k2_service_restart
  k2_scratchpad_read, k2_scratchpad_write
  k2_bus_post, k2_kiki_status, k2_kiki_inject
  k2_ollama_chat  — direct Ollama at 100.75.109.92:11434
  k2_vesper_state — reads regent_state.json + vesper_brief.md
"""
import json
import sys
import os
import urllib.request

K2_ARIA_URL    = os.environ.get("K2_ARIA_URL",   "http://100.75.109.92:7890")
K2_OLLAMA_URL  = os.environ.get("K2_OLLAMA_URL", "http://100.75.109.92:11434")

# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _post(url, payload, timeout=30, headers=None):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def aria_tool(tool_name, tool_input):
    return _post(f"{K2_ARIA_URL}/api/tools/execute", {"tool": tool_name, "input": tool_input})

def ollama_chat(model, messages, system=None):
    msgs = ([{"role": "system", "content": system}] + messages) if system else messages
    resp = _post(f"{K2_OLLAMA_URL}/api/chat",
                 {"model": model, "messages": msgs, "stream": False,
                  "options": {"num_predict": 2048}}, timeout=120)
    if "message" in resp:
        return {"ok": True, "result": {"content": resp["message"].get("content", "")}}
    return {"ok": False, "error": resp.get("error", str(resp))}

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "k2_file_read",
        "description": "Read a file on K2. Returns content, size, exists.",
        "inputSchema": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Absolute path on K2 (WSL)"}
        }, "required": ["path"]}
    },
    {
        "name": "k2_file_write",
        "description": "Write content to a file on K2. Creates parent dirs.",
        "inputSchema": {"type": "object", "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"},
            "mode": {"type": "string", "enum": ["write", "append"], "default": "write"}
        }, "required": ["path", "content"]}
    },
    {
        "name": "k2_file_list",
        "description": "List directory contents on K2 with optional glob.",
        "inputSchema": {"type": "object", "properties": {
            "path": {"type": "string"},
            "pattern": {"type": "string"}
        }, "required": ["path"]}
    },
    {
        "name": "k2_file_search",
        "description": "Search for regex pattern in files on K2 (recursive grep).",
        "inputSchema": {"type": "object", "properties": {
            "path": {"type": "string"},
            "pattern": {"type": "string"}
        }, "required": ["path", "pattern"]}
    },
    {
        "name": "k2_python_exec",
        "description": "Execute Python code on K2. Returns stdout, stderr, exit_code.",
        "inputSchema": {"type": "object", "properties": {
            "code": {"type": "string"}
        }, "required": ["code"]}
    },
    {
        "name": "k2_service_status",
        "description": "Check systemd service status on K2 (karma-regent, vesper-watchdog, aria, ollama...).",
        "inputSchema": {"type": "object", "properties": {
            "service": {"type": "string"}
        }, "required": ["service"]}
    },
    {
        "name": "k2_service_restart",
        "description": "Restart a systemd service on K2.",
        "inputSchema": {"type": "object", "properties": {
            "service": {"type": "string"}
        }, "required": ["service"]}
    },
    {
        "name": "k2_scratchpad_read",
        "description": "Read the CC scratchpad on K2 (/mnt/c/dev/Karma/k2/cache/cc_scratchpad.md).",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "k2_scratchpad_write",
        "description": "Write to the CC scratchpad on K2.",
        "inputSchema": {"type": "object", "properties": {
            "content": {"type": "string"},
            "mode": {"type": "string", "enum": ["append", "replace"], "default": "append"}
        }, "required": ["content"]}
    },
    {
        "name": "k2_bus_post",
        "description": "Post a message to the coordination bus (all agents see it).",
        "inputSchema": {"type": "object", "properties": {
            "content": {"type": "string"},
            "to": {"type": "string", "default": "all"},
            "urgency": {"type": "string", "enum": ["informational", "important", "critical"],
                        "default": "informational"}
        }, "required": ["content"]}
    },
    {
        "name": "k2_kiki_status",
        "description": "Get Kiki evolution loop status and recent cycle summary on K2.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "k2_kiki_inject",
        "description": "Inject a directive or task into Kiki's next evolution cycle.",
        "inputSchema": {"type": "object", "properties": {
            "directive": {"type": "string"}
        }, "required": ["directive"]}
    },
    {
        "name": "k2_ollama_chat",
        "description": "Run inference on K2 Ollama directly. Available models depend on live K2 inventory; default is qwen3.5:4b.",
        "inputSchema": {"type": "object", "properties": {
            "model": {"type": "string", "default": "qwen3.5:4b"},
            "messages": {"type": "array", "items": {"type": "object"}},
            "system": {"type": "string"}
        }, "required": ["messages"]}
    },
    {
        "name": "k2_vesper_state",
        "description": "Get Vesper's current runtime state, session brief, and identity spine summary.",
        "inputSchema": {"type": "object", "properties": {}}
    },
]

# ── Tool router ───────────────────────────────────────────────────────────────

_ARIA_MAP = {
    "k2_file_read":       "file_read",
    "k2_file_write":      "file_write",
    "k2_file_list":       "file_list",
    "k2_file_search":     "file_search",
    "k2_python_exec":     "python_exec",
    "k2_service_status":  "service_status",
    "k2_service_restart": "service_restart",
    "k2_scratchpad_read": "scratchpad_read",
    "k2_scratchpad_write":"scratchpad_write",
    "k2_bus_post":        "bus_post",
    "k2_kiki_status":     "kiki_status",
    "k2_kiki_inject":     "kiki_inject",
}

def handle_tool(name, arguments):
    if name == "k2_ollama_chat":
        return ollama_chat(
            arguments.get("model", "qwen3.5:4b"),
            arguments.get("messages", []),
            arguments.get("system")
        )
    if name == "k2_vesper_state":
        cache = "/mnt/c/dev/Karma/k2/cache"
        state = aria_tool("file_read", {"path": f"{cache}/regent_state.json"})
        brief = aria_tool("file_read", {"path": f"{cache}/vesper_brief.md"})
        spine = aria_tool("file_read", {"path": f"{cache}/vesper_identity_spine.json"})
        return {"ok": True, "result": {
            "state": state.get("result", {}).get("content", "unavailable"),
            "brief": brief.get("result", {}).get("content", "unavailable"),
            "spine_version": json.loads(spine.get("result", {}).get("content") or "{}").get("identity", {}).get("version", "unknown") if spine.get("ok") else "unavailable"
        }}
    if name in _ARIA_MAP:
        return aria_tool(_ARIA_MAP[name], arguments)
    return {"ok": False, "error": f"Unknown tool: {name}"}

# ── MCP stdio protocol (JSON-RPC 2.0, Content-Length framed) ─────────────────

def write_msg(msg):
    body = json.dumps(msg).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
    sys.stdout.buffer.write(header + body)
    sys.stdout.buffer.flush()

def read_msg():
    headers = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            raise EOFError
        line = line.decode("utf-8").rstrip("\r\n")
        if not line:
            break
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    length = int(headers.get("content-length", 0))
    if length == 0:
        return None
    return json.loads(sys.stdin.buffer.read(length))

def main():
    while True:
        try:
            msg = read_msg()
            if msg is None:
                continue
        except EOFError:
            break
        except Exception:
            continue

        method = msg.get("method", "")
        msg_id = msg.get("id")

        if method == "initialize":
            write_msg({"jsonrpc": "2.0", "id": msg_id, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "k2-mcp", "version": "1.0.0"}
            }})
        elif method == "initialized":
            pass
        elif method == "tools/list":
            write_msg({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            params  = msg.get("params", {})
            name    = params.get("name", "")
            args    = params.get("arguments", {})
            result  = handle_tool(name, args)
            ok      = result.get("ok", True)
            content = json.dumps(result.get("result", result)) if ok else f"Error: {result.get('error', 'unknown')}"
            write_msg({"jsonrpc": "2.0", "id": msg_id, "result": {
                "content": [{"type": "text", "text": content}],
                "isError": not ok
            }})
        elif method == "ping":
            write_msg({"jsonrpc": "2.0", "id": msg_id, "result": {}})
        elif msg_id is not None:
            write_msg({"jsonrpc": "2.0", "id": msg_id,
                       "error": {"code": -32601, "message": f"Method not found: {method}"}})

if __name__ == "__main__":
    main()
