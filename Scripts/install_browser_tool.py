"""
Install the Karma Browser Control tool into Open WebUI
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Paths
DB_PATH = r"C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db"
TOOL_FILE = Path(__file__).parent / "openwebui_browser_tool.py"

# Tool metadata
TOOL_ID = "karma-browser-control"
USER_ID = "09494a4c-3aec-4b43-a728-95ac7ad5bccb"  # Neo's user ID
TOOL_NAME = "Karma Browser Control"

def install_tool():
    # Read the tool content from file
    tool_content = TOOL_FILE.read_text(encoding="utf-8")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if tool already exists
    cursor.execute("SELECT id FROM tool WHERE id = ?", (TOOL_ID,))
    existing = cursor.fetchone()
    
    now = int(datetime.now().timestamp())
    
    meta = json.dumps({
        "description": "Allows Karma to control a browser - navigate, take screenshots, and extract content from web pages."
    })
    
    specs = json.dumps([
        {
            "name": "browser_navigate",
            "description": "Navigate the browser to a URL and return the page title",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to navigate to"}
                },
                "required": ["url"]
            }
        },
        {
            "name": "browser_screenshot",
            "description": "Take a screenshot of a webpage and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to screenshot"},
                    "filename": {"type": "string", "description": "Name for the screenshot file", "default": "screenshot.png"}
                },
                "required": ["url"]
            }
        },
        {
            "name": "browser_get_content",
            "description": "Get the text content of a webpage",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to extract content from"}
                },
                "required": ["url"]
            }
        },
        {
            "name": "browser_get_links",
            "description": "Get all links from a webpage",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to extract links from"}
                },
                "required": ["url"]
            }
        },
        {
            "name": "browser_search_google",
            "description": "Search Google and return the top results",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    ])
    
    if existing:
        # Update existing tool
        cursor.execute("""
            UPDATE tool 
            SET content = ?, specs = ?, meta = ?, updated_at = ?
            WHERE id = ?
        """, (tool_content, specs, meta, now, TOOL_ID))
        print(f"[OK] Updated existing tool: {TOOL_NAME}")
    else:
        # Insert new tool
        cursor.execute("""
            INSERT INTO tool (id, user_id, name, content, specs, meta, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (TOOL_ID, USER_ID, TOOL_NAME, tool_content, specs, meta, now, now))
        print(f"[OK] Installed new tool: {TOOL_NAME}")
    
    conn.commit()
    conn.close()
    
    print(f"[OK] Tool ID: {TOOL_ID}")
    print("[INFO] Restart Open WebUI or refresh the page to see the tool")
    print("[INFO] Go to Workspace > Tools to verify installation")
    print("[INFO] Enable the tool for Karma model in Models settings")

if __name__ == "__main__":
    install_tool()
