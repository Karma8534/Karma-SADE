#!/usr/bin/env python3
"""K2 MCP stdio proxy — bridges Claude Code MCP protocol to K2 aria HTTP API.

Reads JSON-RPC 2.0 from stdin, proxies to K2 /api/tools/* endpoints, writes
responses to stdout. Auth via Scripts/k2_mcp.key or K2_SERVICE_KEY env var.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

K2_URL = os.environ.get("K2_URL", "http://100.75.109.92:7890")
_KEY_FILE = Path(__file__).parent / "k2_mcp.key"
K2_KEY = os.environ.get("K2_SERVICE_KEY") or (
    _KEY_FILE.read_text().strip() if _KEY_FILE.exists() else ""
)

_SERVER_INFO = {
    "name": "k2-aria",
    "version": "1.0.0",
}

_CAPABILITIES = {
    "tools": {},
}


def _k2_request(path, payload=None):
    """HTTP request to K2 aria API. Returns parsed JSON dict."""
    url = K2_URL.rstrip("/") + path
    data = json.dumps(payload).encode() if payload is not None else None
    method = "POST" if data is not None else "GET"
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Aria-Service-Key": K2_KEY,
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"K2 HTTP {e.code}: {body[:200]}") from e
    except Exception as e:
        raise RuntimeError(f"K2 request failed: {e}") from e


def _list_tools():
    """Fetch tool list from K2 and convert to MCP schema."""
    data = _k2_request("/api/tools/list")
    tools = []
    for t in data.get("tools", []):
        schema = t.get("input_schema") or {"type": "object", "properties": {}}
        tools.append({
            "name": t["name"],
            "description": t.get("description", ""),
            "inputSchema": schema,
        })
    return tools


def _call_tool(name, arguments):
    """Execute a tool on K2 and return MCP content."""
    try:
        data = _k2_request("/api/tools/execute", {"tool": name, "input": arguments or {}})
        ok = data.get("ok", False)
        result = data.get("result", {})
        text = json.dumps(result) if result else (data.get("error") or "no result")
        return [{"type": "text", "text": text}], not ok
    except RuntimeError as e:
        return [{"type": "text", "text": str(e)}], True


def _respond(msg_id, result):
    out = {"jsonrpc": "2.0", "id": msg_id, "result": result}
    line = json.dumps(out)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def _error(msg_id, code, message):
    out = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()


def handle(msg):
    msg_id = msg.get("id")
    method = msg.get("method", "")
    params = msg.get("params") or {}

    if method == "initialize":
        _respond(msg_id, {
            "protocolVersion": params.get("protocolVersion", "2024-11-05"),
            "capabilities": _CAPABILITIES,
            "serverInfo": _SERVER_INFO,
        })

    elif method == "initialized":
        pass  # notification, no response

    elif method == "ping":
        _respond(msg_id, {})

    elif method == "tools/list":
        try:
            tools = _list_tools()
            _respond(msg_id, {"tools": tools})
        except RuntimeError as e:
            _error(msg_id, -32603, str(e))

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments") or {}
        try:
            content, is_error = _call_tool(tool_name, arguments)
            _respond(msg_id, {"content": content, "isError": is_error})
        except RuntimeError as e:
            _error(msg_id, -32603, str(e))

    elif msg_id is not None:
        _error(msg_id, -32601, f"Method not found: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"[k2_mcp_proxy] JSON parse error: {e}\n")
            continue
        try:
            handle(msg)
        except Exception as e:
            msg_id = msg.get("id")
            if msg_id is not None:
                _error(msg_id, -32603, f"Internal error: {e}")
            sys.stderr.write(f"[k2_mcp_proxy] unhandled error: {e}\n")


if __name__ == "__main__":
    main()
