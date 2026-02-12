"""
title: Karma Agent Tools
author: Karma SADE
version: 3.0.0
description: Agentic toolset for Karma — browser control, shell execution, file I/O, web search, system monitoring. Autonomous browser actions with sensitive-field gating.
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

COCKPIT_URL = "http://127.0.0.1:9400"
TOKEN_FILE = Path.home() / "karma" / "cockpit-token.txt"


def _load_token() -> str:
    """Read the cockpit API token from disk."""
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _post(endpoint: str, data: dict = None, timeout: int = 20) -> dict:
    """POST JSON to the cockpit service."""
    url = f"{COCKPIT_URL}{endpoint}"
    body = json.dumps(data or {}).encode("utf-8")
    token = _load_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
            return err_body
        except Exception:
            return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": f"Cockpit service unreachable: {str(e)}"}


def _get(endpoint: str) -> dict:
    """GET from the cockpit service."""
    url = f"{COCKPIT_URL}{endpoint}"
    token = _load_token()
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"Cockpit service unreachable: {str(e)}"}


class Tools:
    def __init__(self):
        pass

    def browser_tabs(self) -> str:
        """
        List all open browser tabs with their names and URLs.
        Use this first to see what tabs are available before reading or acting on them.

        :return: List of open tabs with names, URLs, and titles.
        """
        result = _get("/tabs")
        if "error" in result:
            return f"Error: {result['error']}"
        tabs = result.get("tabs", [])
        if not tabs:
            return "No tabs open."
        lines = []
        for t in tabs:
            pin = " [pinned]" if t.get("pinned") else ""
            lines.append(f"@{t['name']}{pin} — {t['title']} ({t['url']})")
        return "Open tabs:\n" + "\n".join(lines)

    def browser_open(self, url: str, name: str = "") -> str:
        """
        Open a new browser tab and navigate to a URL.
        The tab is auto-named from the domain (e.g. github, cloudflare).
        You can optionally provide a custom name.

        :param url: The URL to open.
        :param name: Optional custom name for the tab.
        :return: The assigned tab name.
        """
        data = {"url": url}
        if name:
            data["name"] = name
        result = _post("/tab/open", data)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Opened @{result['tab']} → {result['url']}"

    def browser_read(self, tab: str) -> str:
        """
        Read the text content of a named browser tab.
        Use this to see what's on a page. Returns raw text.

        :param tab: The tab name (e.g. 'github', 'cloudflare'). Do NOT include the @ prefix.
        :return: The page title, URL, and text content.
        """
        result = _post("/tab/read", {"tab": tab})
        if "error" in result:
            return f"Error: {result['error']}"
        return (
            f"Tab: @{result['tab']}\n"
            f"URL: {result['url']}\n"
            f"Title: {result['title']}\n\n"
            f"{result['text']}"
        )

    def browser_read_clean(self, tab: str) -> str:
        """
        Read cleaned/extracted content from a browser tab using Goose3.
        Best for articles, docs, and content-heavy pages. Falls back to raw text if extraction yields little.

        :param tab: The tab name. Do NOT include the @ prefix.
        :return: Cleaned text content with title and metadata.
        """
        result = _post("/tab/read_clean", {"tab": tab})
        if "error" in result:
            return f"Error: {result['error']}"
        method = result.get("extraction_method", "unknown")
        parts = [
            f"Tab: @{result.get('tab', tab)}",
            f"URL: {result.get('url', '')}",
            f"Title: {result.get('title', '')}",
            f"Extraction: {method}",
        ]
        desc = result.get("meta_description", "")
        if desc:
            parts.append(f"Description: {desc}")
        parts.append("")
        parts.append(result.get("text", "(no content)"))
        return "\n".join(parts)

    def browser_navigate(self, tab: str, url: str) -> str:
        """
        Navigate an existing browser tab to a new URL.
        Use this to change what page a tab is showing without opening a new one.

        :param tab: The tab name to navigate. Do NOT include the @ prefix.
        :param url: The new URL to load.
        :return: Confirmation of navigation.
        """
        result = _post("/tab/navigate", {"tab": tab, "url": url})
        if "error" in result:
            return f"Error: {result['error']}"
        return f"@{result['tab']} navigated to {result['navigated_to']}"

    def browser_screenshot(self, tab: str) -> str:
        """
        Take a screenshot of a browser tab. The image is saved locally.

        :param tab: The tab name. Do NOT include the @ prefix.
        :return: Path to the saved screenshot file.
        """
        result = _post("/tab/screenshot", {"tab": tab})
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Screenshot of @{result['tab']} saved to: {result['path']}"

    def browser_links(self, tab: str) -> str:
        """
        Get all links from a browser tab. Useful for discovering navigation options.

        :param tab: The tab name. Do NOT include the @ prefix.
        :return: List of links with text and href.
        """
        result = _post("/tab/links", {"tab": tab})
        if "error" in result:
            return f"Error: {result['error']}"
        links = result.get("links", [])
        if not links:
            return f"No links found on @{result.get('tab', tab)}."
        lines = [f"- [{l['text']}]({l['href']})" for l in links]
        return f"Links on @{result.get('tab', tab)}:\n" + "\n".join(lines)

    def browser_click(self, tab: str, selector: str) -> str:
        """
        Click an element on a browser tab. Works autonomously — no approval needed.
        Use CSS selectors to target elements.

        :param tab: The tab name. Do NOT include the @ prefix.
        :param selector: CSS selector of the element to click.
        :return: Click confirmation.
        """
        result = _post("/tab/click", {"tab": tab, "selector": selector})
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("approval_required"):
            return result["message"]
        return f"Clicked '{result.get('selector', selector)}' on @{result.get('tab', tab)}"

    def browser_fill(self, tab: str, selector: str, text: str, confirm_code: str = "") -> str:
        """
        Fill a form field on a browser tab. Works autonomously for normal fields.
        Only password/login fields require approval — include confirm_code for those.

        :param tab: The tab name. Do NOT include the @ prefix.
        :param selector: CSS selector of the form field.
        :param text: The text to fill in.
        :param confirm_code: Only needed for password/login fields.
        :return: Fill confirmation or approval request for sensitive fields.
        """
        data = {"tab": tab, "selector": selector, "text": text}
        if confirm_code:
            data["confirm_code"] = confirm_code
        result = _post("/tab/fill", data)
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("approval_required"):
            return result["message"]
        return f"Filled '{result.get('selector', selector)}' on @{result.get('tab', tab)}"

    def browser_close(self, tab: str) -> str:
        """
        Close a browser tab. Cannot close the pinned Karma tab (_karma).

        :param tab: The tab name to close. Do NOT include the @ prefix.
        :return: Confirmation that the tab was closed.
        """
        result = _post("/tab/close", {"tab": tab})
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Closed @{result.get('closed', tab)}"

    # ------------------------------------------------------------------
    # Cockpit Customization
    # ------------------------------------------------------------------

    def cockpit_customize(self, css: str, description: str = "") -> str:
        """
        Customize the Karma cockpit appearance by injecting CSS.
        Use this when Neo asks you to change colors, backgrounds, fonts, layout, or any visual aspect.
        You generate the CSS yourself. !important is added automatically — you do not need to include it.
        Each call REPLACES the previous theme. Include ALL desired styles in one CSS block.

        Key selectors for Open WebUI:
        - Main background: "body, .app, main, div.relative.flex.flex-col { background-color: COLOR; }"
        - Sidebar: "#sidebar, nav { background-color: COLOR; }"
        - Chat bubbles: ".assistant-message, [data-message-id] { background: COLOR; }"
        - Text: ".prose, .message-content, body { color: COLOR; }"
        - Input area: "#chat-input, .ProseMirror { background-color: COLOR; }"

        :param css: CSS rules to inject. !important is auto-added.
        :param description: Brief description of the change (e.g. 'midnight blue background').
        :return: Confirmation that the style was applied.
        """
        result = _post("/cockpit/style", {"css": css, "description": description})
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Style applied: {description or 'custom CSS'}. Total active rules: {result.get('total_rules', '?')}"

    def cockpit_reset(self) -> str:
        """
        Reset all cockpit customizations back to defaults.
        Use this when Neo wants to undo all visual changes.

        :return: Confirmation that styles were reset.
        """
        result = _post("/cockpit/reset")
        if "error" in result:
            return f"Error: {result['error']}"
        return "All cockpit customizations have been reset to defaults."

    def cockpit_theme(self) -> str:
        """
        View the current cockpit theme and all active style rules.
        Use this to see what customizations are currently applied.

        :return: Current theme with all active CSS rules and descriptions.
        """
        result = _get("/cockpit/theme")
        if "error" in result:
            return f"Error: {result['error']}"
        rules = result.get("rules", [])
        if not rules:
            return "No custom styles applied. Cockpit is using default theme."
        lines = [f"Active cockpit theme ({len(rules)} rules):"]
        for i, r in enumerate(rules, 1):
            desc = r.get("description", "no description")
            lines.append(f"{i}. {desc}: {r['css'][:80]}")
        return "\n".join(lines)

    def cockpit_execute(self, js: str, description: str = "", confirm_code: str = "") -> str:
        """
        Execute JavaScript on the cockpit for advanced modifications.
        This is a MUTATION action requiring approval.
        First call without confirm_code to get an approval code.
        Then Neo must approve by saying "APPROVE <code>".

        Use this for DOM manipulation, adding elements, or changes that CSS alone cannot do.

        :param js: JavaScript code to execute on the cockpit page.
        :param description: Brief description of what the JS does.
        :param confirm_code: The approval code (leave empty on first call).
        :return: Approval request or execution result.
        """
        data = {"js": js, "description": description}
        if confirm_code:
            data["confirm_code"] = confirm_code
        result = _post("/cockpit/exec", data)
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("approval_required"):
            return result["message"]
        return f"Executed on cockpit. Result: {result.get('result', 'none')}"

    def cockpit_color_picker(self) -> str:
        """
        Open an interactive color picker overlay on the cockpit.
        Use this when Neo asks to pick colors, choose colors, or see a color picker.
        The overlay lets Neo visually pick colors for background, sidebar, text, chat bubbles, and input area.
        Colors preview live and can be saved with one click. No approval needed.
        If the picker is already open, calling this again will close it.

        :return: Confirmation that the color picker was opened.
        """
        result = _post("/cockpit/color_picker")
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Color picker overlay is now visible on the cockpit. Neo can pick colors and click 'Apply & Save'."

    def cockpit_apply_preset(self, name: str) -> str:
        """
        Apply a curated theme preset to the cockpit.
        Use this when Neo asks for a theme by name or mood.
        Available presets: midnight, cyberpunk, ocean, ember, stealth, default.
        'default' resets to stock Open WebUI appearance.

        :param name: Preset name (midnight, cyberpunk, ocean, ember, stealth, default).
        :return: Confirmation that the preset was applied.
        """
        result = _post("/cockpit/preset", {"name": name})
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("action") == "reset":
            return "Theme reset to default Open WebUI appearance."
        return f"Applied '{result.get('preset', name)}' theme preset."

    # ------------------------------------------------------------------
    # Gemini CLI (deep analysis + multimodal)
    # ------------------------------------------------------------------

    def gemini_query(self, prompt: str) -> str:
        """
        Ask Gemini Pro a question. Use this for complex reasoning, web research,
        deep analysis, or anything that needs more intelligence than your local model.
        Gemini has 1M+ token context, built-in web search, and advanced reasoning.

        :param prompt: The question or instruction for Gemini.
        :return: Gemini's response.
        """
        result = _post("/gemini/query", {"prompt": prompt}, timeout=90)
        if "error" in result:
            return f"Error: {result['error']}"
        response = result.get("response", "(no response)")
        tokens = result.get("tokens_used", "?")
        ms = result.get("duration_ms", "?")
        return f"{response}\n\n[Gemini | {tokens} tokens | {ms}ms]"

    def gemini_analyze(self, file: str, prompt: str = "Describe what you see in detail.") -> str:
        """
        Analyze a screenshot, image, or PDF using Gemini's vision.
        Pair with browser_screenshot() to visually analyze web pages.
        Example: take a screenshot, then call gemini_analyze with the screenshot path.

        :param file: Absolute path to the image/PDF file.
        :param prompt: What to analyze or look for (default: general description).
        :return: Gemini's visual analysis.
        """
        result = _post("/gemini/analyze", {"file": file, "prompt": prompt}, timeout=90)
        if "error" in result:
            return f"Error: {result['error']}"
        response = result.get("response", "(no response)")
        tokens = result.get("tokens_used", "?")
        ms = result.get("duration_ms", "?")
        return f"{response}\n\n[Gemini Vision | {tokens} tokens | {ms}ms]"

    # ------------------------------------------------------------------
    # System Tools (Agentic)
    # ------------------------------------------------------------------

    def shell_run(self, command: str, confirm_code: str = "") -> str:
        """
        Run a PowerShell command on the local machine. REQUIRES APPROVAL.
        First call without confirm_code to get an approval code.
        Neo must approve by saying "APPROVE <code>".
        Then call again with the confirm_code to execute.

        :param command: The PowerShell command to run.
        :param confirm_code: The approval code (leave empty on first call).
        :return: Command output (stdout, stderr, exit code) or approval request.
        """
        data = {"command": command}
        if confirm_code:
            data["confirm_code"] = confirm_code
        result = _post("/shell/run", data, timeout=135)
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("approval_required"):
            return result["message"]
        parts = []
        if result.get("stdout"):
            parts.append(result["stdout"])
        if result.get("stderr"):
            parts.append(f"STDERR: {result['stderr']}")
        parts.append(f"[exit {result.get('exit_code', '?')} | {result.get('duration_ms', '?')}ms]")
        return "\n".join(parts)

    def file_read(self, path: str, start_line: int = 0, end_line: int = 0) -> str:
        """
        Read the contents of a file on the local machine. No approval needed.
        Optionally specify line range to read a portion of large files.

        :param path: Absolute path to the file.
        :param start_line: Optional start line (1-indexed). 0 means from beginning.
        :param end_line: Optional end line. 0 means to end of file.
        :return: File content with metadata.
        """
        data = {"path": path}
        if start_line > 0:
            data["start_line"] = start_line
        if end_line > 0:
            data["end_line"] = end_line
        result = _post("/file/read", data)
        if "error" in result:
            return f"Error: {result['error']}"
        header = f"File: {result['path']} ({result.get('total_lines', '?')} lines, {result.get('size_bytes', '?')} bytes)"
        if result.get("truncated"):
            header += " [truncated]"
        return f"{header}\n\n{result.get('content', '')}"

    def file_write(self, path: str, content: str, mode: str = "write", confirm_code: str = "") -> str:
        """
        Write or append to a file. REQUIRES APPROVAL.
        First call without confirm_code to get an approval code.
        Neo must approve, then call again with the code.

        :param path: Absolute path to write to.
        :param content: The content to write.
        :param mode: 'write' to replace entire file, 'append' to add to end.
        :param confirm_code: Approval code (leave empty on first call).
        :return: Confirmation or approval request.
        """
        data = {"path": path, "content": content, "mode": mode}
        if confirm_code:
            data["confirm_code"] = confirm_code
        result = _post("/file/write", data)
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("approval_required"):
            return result["message"]
        return f"Written {result.get('bytes_written', '?')} bytes to {result.get('path', path)} (mode: {mode})"

    def file_patch(self, path: str, search: str, replace: str, confirm_code: str = "") -> str:
        """
        Surgical search/replace edit in a file. Like find-and-replace.
        Requires approval. First call returns a code, second call with code executes.

        :param path: Absolute path to the file.
        :param search: Exact text to find in the file.
        :param replace: Text to replace it with.
        :param confirm_code: Approval code from first call.
        :return: Patch result or approval prompt.
        """
        data = {"path": path, "search": search, "replace": replace}
        if confirm_code:
            data["confirm_code"] = confirm_code
        result = _post("/file/patch", data)
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("approval_required"):
            return result["message"]
        return f"Patched {result.get('occurrences_replaced', '?')} occurrence(s) in {result.get('path', path)}"

    def file_list(self, path: str, pattern: str = "") -> str:
        """
        List the contents of a directory. No approval needed.
        Optionally filter by glob pattern (e.g. '*.py', '*.json').

        :param path: Absolute path to the directory.
        :param pattern: Optional glob filter (e.g. '*.py').
        :return: Directory listing with file names, types, sizes.
        """
        data = {"path": path}
        if pattern:
            data["pattern"] = pattern
        result = _post("/file/list", data)
        if "error" in result:
            return f"Error: {result['error']}"
        entries = result.get("entries", [])
        if not entries:
            return f"Directory {result.get('path', path)} is empty."
        lines = [f"{result.get('path', path)} ({len(entries)} items):"]
        for e in entries:
            icon = "[DIR]" if e["type"] == "dir" else f"{e['size_bytes']}b"
            lines.append(f"  {e['name']}  {icon}  {e.get('modified', '')}")
        return "\n".join(lines)

    def file_search(self, path: str, query: str, pattern: str = "") -> str:
        """
        Search for text in files within a directory (like grep). No approval needed.
        Searches recursively, skipping binary files and large files.

        :param path: Directory to search in.
        :param query: Text to search for (case-insensitive).
        :param pattern: Optional file glob filter (e.g. '*.py').
        :return: Matching lines with file paths and line numbers.
        """
        data = {"path": path, "query": query}
        if pattern:
            data["pattern"] = pattern
        result = _post("/file/search", data)
        if "error" in result:
            return f"Error: {result['error']}"
        matches = result.get("matches", [])
        if not matches:
            return f"No matches for '{query}' in {result.get('path', path)}"
        lines = [f"Found {len(matches)} matches for '{query}':"]
        for m in matches:
            lines.append(f"  {m['file']}:{m['line_num']}  {m['line_text']}")
        if result.get("truncated"):
            lines.append("  [results truncated]")
        return "\n".join(lines)

    def file_semantic_search(self, path: str, query: str, pattern: str = "") -> str:
        """
        Semantic file search — finds files conceptually related to a query.
        Powered by Gemini. Use when you need to find files by meaning, not exact text.
        For example: "authentication logic" or "database connection setup".

        :param path: Directory to search in.
        :param query: Natural language description of what you're looking for.
        :param pattern: Optional file glob filter (e.g. '*.py').
        :return: Ranked list of relevant files.
        """
        data = {"path": path, "query": query}
        if pattern:
            data["pattern"] = pattern
        result = _post("/file/semantic_search", data)
        if "error" in result:
            return f"Error: {result['error']}"
        files = result.get("results", [])
        if not files:
            return f"No files found relevant to '{query}' in {result.get('path', path)}"
        lines = [f"Files relevant to '{query}' (ranked):"]
        for i, f in enumerate(files, 1):
            lines.append(f"  {i}. {f}")
        return "\n".join(lines)

    def system_info(self) -> str:
        """
        Get system health information: CPU, RAM, disk usage, uptime, running services.
        Use this when Neo asks about machine health, performance, or what's running.

        :return: System status summary.
        """
        result = _get("/system/info")
        if "error" in result:
            return f"Error: {result['error']}"
        lines = [
            f"{result.get('hostname', '?')} ({result.get('os', '?')})",
            f"CPU: {result.get('cpu_percent', '?')}%",
            f"RAM: {result.get('ram', {}).get('used_gb', '?')}/{result.get('ram', {}).get('total_gb', '?')} GB ({result.get('ram', {}).get('percent', '?')}%)",
            f"Disk: {result.get('disk', {}).get('used_gb', '?')}/{result.get('disk', {}).get('total_gb', '?')} GB ({result.get('disk', {}).get('percent', '?')}%)",
            f"Uptime: {result.get('uptime_hours', '?')} hours",
        ]
        services = result.get("services", [])
        if services:
            svc_names = [f"{s['name']} (PID {s['pid']})" for s in services]
            lines.append(f"Services: {', '.join(svc_names)}")
        return "\n".join(lines)

    def web_search(self, query: str, max_results: int = 5) -> str:
        """
        Search the web using DuckDuckGo. No approval needed.
        Returns titles, URLs, and snippets. Use for quick lookups.
        For deep research, follow up by opening results with browser_open.

        :param query: What to search for.
        :param max_results: Number of results (1-10, default 5).
        :return: Search results with titles, URLs, and snippets.
        """
        result = _post("/web/search", {"query": query, "max_results": max_results})
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("fallback"):
            return f"Search failed. {result.get('suggestion', 'Try gemini_query() instead.')}"
        results = result.get("results", [])
        if not results:
            return f"No results for '{query}'"
        lines = [f"Search: '{query}' ({len(results)} results)"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['title']}")
            lines.append(f"   {r['url']}")
            if r.get('snippet'):
                lines.append(f"   {r['snippet'][:150]}")
        return "\n".join(lines)

    def web_research(self, query: str, max_sources: int = 3) -> str:
        """
        Deep web research: searches, reads top results, synthesizes with Gemini.
        Like Perplexity — returns a cited, comprehensive answer.
        Use for complex questions that need multiple sources.

        :param query: Research question or topic.
        :param max_sources: Number of sources to read and synthesize (1-5, default 3).
        :return: Synthesized answer with source citations.
        """
        result = _post("/web/research", {"query": query, "max_sources": max_sources})
        if "error" in result:
            return f"Error: {result['error']}"
        synthesis = result.get("synthesis", "No synthesis available.")
        sources = result.get("sources", [])
        lines = [synthesis, "", "Sources:"]
        for i, s in enumerate(sources, 1):
            lines.append(f"  [{i}] {s.get('title', 'Untitled')} — {s.get('url', '')}")
        tokens = result.get("tokens_used")
        if tokens:
            lines.append(f"\n[Gemini: {tokens} tokens]")
        return "\n".join(lines)
