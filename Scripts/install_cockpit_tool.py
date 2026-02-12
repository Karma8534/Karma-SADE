"""
Install/update the Karma Browser Control v2 tool into Open WebUI
and enable it for the karma-sade-architect model.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Paths
DB_PATH = r"C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db"
TOOL_FILE = Path(__file__).parent / "openwebui_browser_tool_v2.py"

# IDs
TOOL_ID = "karma-browser-control"
USER_ID = "09494a4c-3aec-4b43-a728-95ac7ad5bccb"
TOOL_NAME = "Karma Agent Tools"
MODEL_ID = "karma-sade-architect"


def build_specs():
    """Build OpenAI-style function specs for the v2 tool."""
    return json.dumps([
        {
            "name": "browser_tabs",
            "description": "List all open browser tabs with their names and URLs",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "browser_open",
            "description": "Open a new browser tab and navigate to a URL. Auto-named from domain.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to open"},
                    "name": {"type": "string", "description": "Optional custom tab name"}
                },
                "required": ["url"]
            }
        },
        {
            "name": "browser_read",
            "description": "Read the raw text content of a named browser tab",
            "parameters": {
                "type": "object",
                "properties": {
                    "tab": {"type": "string", "description": "Tab name (e.g. 'github')"}
                },
                "required": ["tab"]
            }
        },
        {
            "name": "browser_read_clean",
            "description": "Read cleaned/extracted content from a tab using Goose3. Best for articles and docs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tab": {"type": "string", "description": "Tab name"}
                },
                "required": ["tab"]
            }
        },
        {
            "name": "browser_navigate",
            "description": "Navigate an existing tab to a new URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "tab": {"type": "string", "description": "Tab name"},
                    "url": {"type": "string", "description": "New URL to load"}
                },
                "required": ["tab", "url"]
            }
        },
        {
            "name": "browser_screenshot",
            "description": "Take a screenshot of a browser tab",
            "parameters": {
                "type": "object",
                "properties": {
                    "tab": {"type": "string", "description": "Tab name"}
                },
                "required": ["tab"]
            }
        },
        {
            "name": "browser_links",
            "description": "Get all links from a browser tab",
            "parameters": {
                "type": "object",
                "properties": {
                    "tab": {"type": "string", "description": "Tab name"}
                },
                "required": ["tab"]
            }
        },
        {
            "name": "browser_click",
            "description": "Click an element on a tab. Works autonomously — no approval needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tab": {"type": "string", "description": "Tab name"},
                    "selector": {"type": "string", "description": "CSS selector of element to click"}
                },
                "required": ["tab", "selector"]
            }
        },
        {
            "name": "browser_fill",
            "description": "Fill a form field. Autonomous for normal fields. Only password/login fields need approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tab": {"type": "string", "description": "Tab name"},
                    "selector": {"type": "string", "description": "CSS selector of the form field"},
                    "text": {"type": "string", "description": "Text to fill in"},
                    "confirm_code": {"type": "string", "description": "Only for password/login fields"}
                },
                "required": ["tab", "selector", "text"]
            }
        },
        {
            "name": "browser_close",
            "description": "Close a browser tab. Cannot close the pinned Karma tab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tab": {"type": "string", "description": "Tab name to close"}
                },
                "required": ["tab"]
            }
        },
        {
            "name": "cockpit_customize",
            "description": "Customize the cockpit appearance by injecting CSS. Use when Neo asks to change colors, backgrounds, fonts, layout. Styles persist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "css": {"type": "string", "description": "CSS rules to inject. Use !important to override defaults."},
                    "description": {"type": "string", "description": "Brief description of the change"}
                },
                "required": ["css"]
            }
        },
        {
            "name": "cockpit_reset",
            "description": "Reset all cockpit customizations back to defaults.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "cockpit_theme",
            "description": "View the current cockpit theme and all active style rules.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "cockpit_execute",
            "description": "Execute JavaScript on the cockpit for advanced modifications. Requires approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "js": {"type": "string", "description": "JavaScript code to execute"},
                    "description": {"type": "string", "description": "Brief description of what the JS does"},
                    "confirm_code": {"type": "string", "description": "Approval code (empty on first call)"}
                },
                "required": ["js"]
            }
        },
        {
            "name": "cockpit_color_picker",
            "description": "Open an interactive color picker overlay on the cockpit. Use when Neo asks to pick/choose colors. No approval needed.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "cockpit_apply_preset",
            "description": "Apply a curated theme preset. Available: midnight, cyberpunk, ocean, ember, stealth, default.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Preset name (midnight, cyberpunk, ocean, ember, stealth, default)"}
                },
                "required": ["name"]
            }
        },
        {
            "name": "gemini_query",
            "description": "Ask Gemini Pro for complex reasoning, web research, or deep analysis. 1M+ token context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The question or instruction for Gemini"}
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "gemini_analyze",
            "description": "Analyze a screenshot/image/PDF with Gemini vision. Pair with browser_screenshot().",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Absolute path to the image/PDF file"},
                    "prompt": {"type": "string", "description": "What to analyze (default: describe what you see)"}
                },
                "required": ["file"]
            }
        },
        {
            "name": "shell_run",
            "description": "Run a PowerShell command. Requires approval. First call gets code, second call with code executes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "PowerShell command to run"},
                    "confirm_code": {"type": "string", "description": "Approval code (empty on first call)"}
                },
                "required": ["command"]
            }
        },
        {
            "name": "file_read",
            "description": "Read a file's contents. No approval needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file"},
                    "start_line": {"type": "integer", "description": "Optional start line (1-indexed)"},
                    "end_line": {"type": "integer", "description": "Optional end line"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "file_write",
            "description": "Write or append to a file. Requires approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to write to"},
                    "content": {"type": "string", "description": "Content to write"},
                    "mode": {"type": "string", "description": "'write' to replace or 'append' to add"},
                    "confirm_code": {"type": "string", "description": "Approval code (empty on first call)"}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "file_patch",
            "description": "Surgical search/replace edit in a file. Requires approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file"},
                    "search": {"type": "string", "description": "Exact text to find"},
                    "replace": {"type": "string", "description": "Text to replace it with"},
                    "confirm_code": {"type": "string", "description": "Approval code (empty on first call)"}
                },
                "required": ["path", "search", "replace"]
            }
        },
        {
            "name": "file_list",
            "description": "List directory contents. No approval needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to list"},
                    "pattern": {"type": "string", "description": "Optional glob filter (e.g. *.py)"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "file_search",
            "description": "Search for text in files (grep-like). No approval needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory to search in"},
                    "query": {"type": "string", "description": "Text to search for"},
                    "pattern": {"type": "string", "description": "Optional file glob (e.g. *.py)"}
                },
                "required": ["path", "query"]
            }
        },
        {
            "name": "file_semantic_search",
            "description": "Semantic file search powered by Gemini. Finds files by meaning, not exact text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory to search in"},
                    "query": {"type": "string", "description": "Natural language query (e.g. 'authentication logic')"},
                    "pattern": {"type": "string", "description": "Optional file glob (e.g. *.py)"}
                },
                "required": ["path", "query"]
            }
        },
        {
            "name": "system_info",
            "description": "Get system health: CPU, RAM, disk, uptime, running services.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "web_search",
            "description": "Search the web via DuckDuckGo. Returns titles, URLs, snippets. No approval needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Number of results (1-10, default 5)"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "web_research",
            "description": "Deep web research: searches, reads top results, synthesizes with Gemini. Like Perplexity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Research question or topic"},
                    "max_sources": {"type": "integer", "description": "Sources to read (1-5, default 3)"}
                },
                "required": ["query"]
            }
        },
    ])


def install():
    tool_content = TOOL_FILE.read_text(encoding="utf-8")
    specs = build_specs()
    meta = json.dumps({
        "description": "Agentic toolset for Karma — browser control, shell execution, file I/O, web search, system monitoring. Autonomous browser actions with sensitive-field gating."
    })
    now = int(datetime.now().timestamp())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Upsert tool
    cursor.execute("SELECT id FROM tool WHERE id = ?", (TOOL_ID,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE tool SET content = ?, specs = ?, meta = ?, updated_at = ?
            WHERE id = ?
        """, (tool_content, specs, meta, now, TOOL_ID))
        print(f"[OK] Updated tool: {TOOL_NAME} v2.0.0")
    else:
        cursor.execute("""
            INSERT INTO tool (id, user_id, name, content, specs, meta, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (TOOL_ID, USER_ID, TOOL_NAME, tool_content, specs, meta, now, now))
        print(f"[OK] Installed tool: {TOOL_NAME} v2.0.0")

    # Enable for Karma model
    cursor.execute("SELECT meta FROM model WHERE id = ?", (MODEL_ID,))
    row = cursor.fetchone()

    if row:
        model_meta = json.loads(row[0]) if row[0] else {}
        changed = False
        # Open WebUI uses both snake_case and camelCase fields
        for field in ["toolIds", "tool_ids"]:
            tools = model_meta.get(field, [])
            if TOOL_ID not in tools:
                tools.append(TOOL_ID)
                model_meta[field] = tools
                changed = True
                print(f"[OK] Added {TOOL_ID} to {field}")
            else:
                print(f"[OK] {field} already has {TOOL_ID}")
        if changed:
            cursor.execute("UPDATE model SET meta = ? WHERE id = ?", (json.dumps(model_meta), MODEL_ID))
            print(f"[OK] Updated model: {MODEL_ID}")
        print(f"     toolIds: {model_meta.get('toolIds', [])}")
        print(f"     tool_ids: {model_meta.get('tool_ids', [])}")
    else:
        print(f"[WARN] Model '{MODEL_ID}' not found — enable manually")

    conn.commit()
    conn.close()
    print("[OK] Done. Restart Open WebUI or refresh to load changes.")


if __name__ == "__main__":
    install()
