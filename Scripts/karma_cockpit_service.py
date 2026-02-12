"""
Karma Cockpit — Agentic Service v2.0.0
Manages a persistent headful Chromium browser with named tabs.
Open WebUI (Karma) is pinned as the first tab.
Flask API on 127.0.0.1:9400 for tool integration.

Features:
- Named tabs with auto-naming from domain
- Goose3 clean content extraction
- Autonomous browser actions (click/fill) with sensitive-field gating
- Shell command execution (approval-gated)
- File read/write/search/list
- System info (CPU, RAM, disk, services)
- Web search (DuckDuckGo + Gemini fallback)
- Screenshot capture
- Pinned tab protection
"""

import fnmatch
import json
import os
import platform as _platform
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, request
import logging

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PORT = 9400
HOST = "127.0.0.1"
OPEN_WEBUI_URL = "http://localhost:8080"
BROWSER_PROFILE = Path.home() / "karma" / "browser-profile"
SCREENSHOT_DIR = Path.home() / "Documents" / "Karma_SADE" / "Logs" / "screenshots"
SCREENSHOT_MAX_AGE_DAYS = 7  # Auto-cleanup screenshots older than this
MAX_CONTENT_CHARS = 8000  # Max text returned per read
PINNED_TAB_NAME = "_karma"  # Protected tab name
THEME_FILE = Path.home() / "karma" / "cockpit-theme.json"
API_TOKEN_FILE = Path.home() / "karma" / "cockpit-token.txt"
LOG_DIR = Path.home() / "Documents" / "Karma_SADE" / "Logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "cockpit-service.log"

# Ensure dirs exist
BROWSER_PROFILE.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def load_or_create_api_token():
    """Load API token from file, or generate and save a new one."""
    if API_TOKEN_FILE.exists():
        token = API_TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token
    token = secrets.token_urlsafe(32)
    API_TOKEN_FILE.write_text(token, encoding="utf-8")
    return token


API_TOKEN = load_or_create_api_token()


def cleanup_old_screenshots():
    """Remove screenshots older than SCREENSHOT_MAX_AGE_DAYS."""
    cutoff = time.time() - (SCREENSHOT_MAX_AGE_DAYS * 86400)
    removed = 0
    try:
        for f in SCREENSHOT_DIR.glob("*.png"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                removed += 1
        if removed:
            logging.info("[cleanup] Removed %d old screenshots", removed)
    except Exception as e:
        logging.warning("[cleanup] Screenshot cleanup failed: %s", e)

# ---------------------------------------------------------------------------
# Agentic Safety Framework
# ---------------------------------------------------------------------------
AUTONOMOUS_MODE = True  # Kill switch: False reverts all actions to approval-gated

# Path restrictions
ALLOWED_READ_ROOTS = [
    Path("C:/Users/raest"),
    Path("C:/openwebui"),
]
ALLOWED_WRITE_ROOTS = [
    Path("C:/Users/raest/Documents/Karma_SADE"),
    Path("C:/Users/raest/karma"),
]
BLOCKED_PATH_PREFIXES = [
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
    "C:\\ProgramData", "C:\\Recovery",
]

# Shell command blocklist (compiled regexes, case-insensitive)
_BLOCKED_COMMANDS = [
    re.compile(p, re.IGNORECASE) for p in [
        r'\bformat\b.*\b[A-Z]:',
        r'\bdiskpart\b',
        r'\bdel\s+/s\b',
        r'\brd\s+/s\b',
        r'\bRemove-Item\b.*-Recurse.*-Force',
        r'\brm\b.*\s+-rf\b',
        r'\brm\b.*-Recurse.*-Force',
        r'\breg\s+delete\b',
        r'\bbcdedit\b',
        r'\bsfc\b\s',
        r'\bdism\b',
        r'\bSet-ExecutionPolicy\b',
        r'\bInvoke-Expression\b',
        r'\biex\s',
        r'\biex\(',
        r'-EncodedCommand\b',
        r'\[Convert\]::FromBase64',
        r'\bnetsh\s+advfirewall\b',
        r'\broute\s+delete\b',
        r'\bcmdkey\b',
        r'\bStart-Process\b.*-Verb\s+RunAs',
        r'\bshutdown\b',
        r'\bRestart-Computer\b',
        r'\bStop-Computer\b',
    ]
]

# Secret patterns to redact from output
_SECRET_PATTERN = re.compile(
    r'(API[_-]?KEY|SECRET|TOKEN|PASSWORD|APIKEY|PASSWD|CREDENTIAL)\s*[=:]\s*\S+',
    re.IGNORECASE
)


def _validate_path(path_str, mode="read"):
    """Validate a file path for safety. mode='read' or 'write'."""
    if not path_str:
        raise ValueError("Path is required")
    if ".." in path_str:
        raise ValueError("Path traversal (..) is not allowed")
    p = Path(path_str).resolve()
    p_str = str(p)
    # Block system paths
    for prefix in BLOCKED_PATH_PREFIXES:
        if p_str.startswith(prefix):
            raise ValueError(f"Access denied: system path")
    # Check allowed roots
    roots = ALLOWED_WRITE_ROOTS if mode == "write" else ALLOWED_READ_ROOTS
    for root in roots:
        try:
            p.relative_to(root.resolve())
            return p
        except ValueError:
            continue
    raise ValueError(f"Path outside allowed {mode} directories")


def _validate_command(command):
    """Check a shell command against the blocklist. Returns error string or None."""
    if not command or not command.strip():
        return "Command is required"
    for pattern in _BLOCKED_COMMANDS:
        if pattern.search(command):
            return f"Blocked: command matches dangerous pattern"
    return None


def _is_sensitive_field(page, selector):
    """Check if a browser form field is sensitive (password/auth) via DOM inspection."""
    try:
        result = page.evaluate("""(selector) => {
            const el = document.querySelector(selector);
            if (!el) return false;
            if (el.type === 'password') return true;
            const ac = (el.autocomplete || '').toLowerCase();
            if (['password', 'current-password', 'new-password'].some(k => ac.includes(k))) return true;
            const id_name = ((el.id || '') + (el.name || '') + (el.className || '')).toLowerCase();
            return ['password', 'passwd', 'secret', 'token', 'otp', '2fa', 'mfa'].some(k => id_name.includes(k));
        }""", selector)
        return bool(result)
    except Exception:
        return True  # If we can't determine, treat as sensitive


def _sanitize_output(text, max_chars=MAX_CONTENT_CHARS):
    """Sanitize tool output: truncate and redact secrets."""
    if not text:
        return text
    text = str(text)
    text = _SECRET_PATTERN.sub(r'\1=***REDACTED***', text)
    if len(text) > max_chars:
        return text[:max_chars] + "\n[truncated]"
    return text


# ---------------------------------------------------------------------------
# Theme presets
# ---------------------------------------------------------------------------
THEME_PRESETS = {
    "midnight": {
        "bg": "#0d1117", "sidebar": "#161b22", "text": "#c9d1d9",
        "bubbles": "#1c2333", "input": "#0d1117",
    },
    "cyberpunk": {
        "bg": "#0a0a0a", "sidebar": "#1a0025", "text": "#00ff41",
        "bubbles": "#1a1a2e", "input": "#0f0f1a",
    },
    "ocean": {
        "bg": "#0b1622", "sidebar": "#0d2137", "text": "#a8d8ea",
        "bubbles": "#132f4c", "input": "#0b1622",
    },
    "ember": {
        "bg": "#1a0a00", "sidebar": "#2d1200", "text": "#ffb088",
        "bubbles": "#3d1a00", "input": "#1a0a00",
    },
    "stealth": {
        "bg": "#111111", "sidebar": "#1a1a1a", "text": "#888888",
        "bubbles": "#1e1e1e", "input": "#141414",
    },
}


def preset_to_css(p):
    """Convert a preset dict to a full CSS block."""
    return (
        f"body, .app, main, div.relative.flex.flex-col {{ background-color: {p['bg']}; }}\n"
        f"#sidebar, nav {{ background-color: {p['sidebar']}; }}\n"
        f".prose, .message-content, body {{ color: {p['text']}; }}\n"
        f".assistant-message, [data-message-id] {{ background: {p['bubbles']}; }}\n"
        f"#chat-input, .ProseMirror {{ background-color: {p['input']}; color: {p['text']}; }}"
    )


# ---------------------------------------------------------------------------
# Color picker overlay JS (self-contained, injected into @_karma tab)
# ---------------------------------------------------------------------------
COLOR_PICKER_JS = r"""(() => {
    const existing = document.getElementById('karma-color-picker');
    if (existing) { existing.remove(); return 'Color picker closed'; }
    const overlay = document.createElement('div');
    overlay.id = 'karma-color-picker';
    overlay.innerHTML = `
        <style>
            #karma-color-picker { position:fixed; top:50px; right:50px; width:320px; background:#1e1e2e;
                border:1px solid #444; border-radius:12px; padding:20px; z-index:999999;
                font-family:-apple-system,BlinkMacSystemFont,sans-serif; color:#e0e0e0;
                box-shadow:0 8px 32px rgba(0,0,0,0.5); }
            #karma-color-picker .kcp-header { display:flex; justify-content:space-between;
                align-items:center; margin-bottom:16px; cursor:move; }
            #karma-color-picker .kcp-title { font-size:16px; font-weight:600; color:#fff; }
            #karma-color-picker .kcp-close { background:none; border:none; color:#888;
                font-size:20px; cursor:pointer; }
            #karma-color-picker .kcp-close:hover { color:#fff; }
            #karma-color-picker .kcp-row { display:flex; justify-content:space-between;
                align-items:center; margin-bottom:12px; }
            #karma-color-picker .kcp-label { font-size:13px; color:#aaa; flex:1; }
            #karma-color-picker input[type=color] { width:50px; height:32px; border:none;
                border-radius:6px; cursor:pointer; background:none; padding:0; }
            #karma-color-picker .kcp-hex { font-size:12px; width:72px; text-align:center;
                background:#2a2a3a; border:1px solid #444; border-radius:4px; padding:4px; color:#ccc; }
            #karma-color-picker .kcp-buttons { display:flex; gap:8px; margin-top:16px; }
            #karma-color-picker .kcp-btn { flex:1; padding:8px; border:none; border-radius:6px;
                font-size:13px; font-weight:500; cursor:pointer; }
            #karma-color-picker .kcp-apply { background:#4c8bf5; color:#fff; }
            #karma-color-picker .kcp-apply:hover { background:#3d7ae5; }
            #karma-color-picker .kcp-reset { background:#3a3a4a; color:#ccc; }
            #karma-color-picker .kcp-reset:hover { background:#4a4a5a; }
            #karma-color-picker .kcp-presets { margin-top:12px; border-top:1px solid #333; padding-top:12px; }
            #karma-color-picker .kcp-presets-title { font-size:12px; color:#777; margin-bottom:8px; }
            #karma-color-picker .kcp-preset-grid { display:flex; gap:6px; flex-wrap:wrap; }
            #karma-color-picker .kcp-preset-btn { padding:4px 10px; border:1px solid #444;
                border-radius:4px; background:#2a2a3a; color:#ccc; font-size:11px; cursor:pointer; }
            #karma-color-picker .kcp-preset-btn:hover { background:#3a3a4a; border-color:#666; }
            #karma-color-picker .kcp-status { font-size:11px; color:#666; text-align:center; margin-top:8px; }
        </style>
        <div class="kcp-header" id="kcp-drag-handle">
            <span class="kcp-title">✨ Cockpit Theme</span>
            <button class="kcp-close" id="kcp-close">×</button>
        </div>
        <div class="kcp-row">
            <span class="kcp-label">Background</span>
            <input type="color" id="kcp-bg" value="#1e1e2e">
            <input type="text" class="kcp-hex" id="kcp-bg-hex" value="#1e1e2e">
        </div>
        <div class="kcp-row">
            <span class="kcp-label">Sidebar</span>
            <input type="color" id="kcp-sidebar" value="#161b22">
            <input type="text" class="kcp-hex" id="kcp-sidebar-hex" value="#161b22">
        </div>
        <div class="kcp-row">
            <span class="kcp-label">Text</span>
            <input type="color" id="kcp-text" value="#e0e0e0">
            <input type="text" class="kcp-hex" id="kcp-text-hex" value="#e0e0e0">
        </div>
        <div class="kcp-row">
            <span class="kcp-label">Chat Bubbles</span>
            <input type="color" id="kcp-bubbles" value="#2a2a3a">
            <input type="text" class="kcp-hex" id="kcp-bubbles-hex" value="#2a2a3a">
        </div>
        <div class="kcp-row">
            <span class="kcp-label">Input Area</span>
            <input type="color" id="kcp-input" value="#1e1e2e">
            <input type="text" class="kcp-hex" id="kcp-input-hex" value="#1e1e2e">
        </div>
        <div class="kcp-buttons">
            <button class="kcp-btn kcp-apply" id="kcp-apply">Apply & Save</button>
            <button class="kcp-btn kcp-reset" id="kcp-reset">Reset All</button>
        </div>
        <div class="kcp-presets">
            <div class="kcp-presets-title">Quick Presets</div>
            <div class="kcp-preset-grid">
                <button class="kcp-preset-btn" data-preset="midnight">Midnight</button>
                <button class="kcp-preset-btn" data-preset="cyberpunk">Cyberpunk</button>
                <button class="kcp-preset-btn" data-preset="ocean">Ocean</button>
                <button class="kcp-preset-btn" data-preset="ember">Ember</button>
                <button class="kcp-preset-btn" data-preset="stealth">Stealth</button>
            </div>
        </div>
        <div class="kcp-status" id="kcp-status">Pick colors and click Apply</div>
    `;
    document.body.appendChild(overlay);
    const presets = {
        midnight:  {bg:'#0d1117',sidebar:'#161b22',text:'#c9d1d9',bubbles:'#1c2333',input:'#0d1117'},
        cyberpunk: {bg:'#0a0a0a',sidebar:'#1a0025',text:'#00ff41',bubbles:'#1a1a2e',input:'#0f0f1a'},
        ocean:     {bg:'#0b1622',sidebar:'#0d2137',text:'#a8d8ea',bubbles:'#132f4c',input:'#0b1622'},
        ember:     {bg:'#1a0a00',sidebar:'#2d1200',text:'#ffb088',bubbles:'#3d1a00',input:'#1a0a00'},
        stealth:   {bg:'#111111',sidebar:'#1a1a1a',text:'#888888',bubbles:'#1e1e1e',input:'#141414'},
    };
    const zones = ['bg','sidebar','text','bubbles','input'];
    const pvId = 'karma-theme-preview';
    function buildCSS() {
        const v = {}; zones.forEach(z => v[z] = document.getElementById('kcp-'+z).value);
        return `body,.app,main,div.relative.flex.flex-col{background-color:${v.bg} !important}
#sidebar,nav{background-color:${v.sidebar} !important}
.prose,.message-content,body{color:${v.text} !important}
.assistant-message,[data-message-id]{background:${v.bubbles} !important}
#chat-input,.ProseMirror{background-color:${v.input} !important;color:${v.text} !important}`;
    }
    function livePreview() {
        let el = document.getElementById(pvId);
        if(!el){el=document.createElement('style');el.id=pvId;document.head.appendChild(el);}
        el.textContent = buildCSS();
    }
    zones.forEach(z => {
        const pk = document.getElementById('kcp-'+z);
        const hx = document.getElementById('kcp-'+z+'-hex');
        pk.addEventListener('input', () => { hx.value=pk.value; livePreview(); });
        hx.addEventListener('change', () => { pk.value=hx.value; livePreview(); });
    });
    document.getElementById('kcp-close').addEventListener('click', () => {
        overlay.remove();
        const pv = document.getElementById(pvId); if(pv) pv.remove();
    });
    document.getElementById('kcp-apply').addEventListener('click', () => {
        const css = buildCSS();
        fetch('http://127.0.0.1:9400/cockpit/style', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({css:css, description:'Color picker theme'})
        }).then(r => r.json()).then(() => {
            const btn = document.getElementById('kcp-apply');
            btn.textContent='✓ Saved!'; btn.style.background='#2ea043';
            setTimeout(()=>{btn.textContent='Apply & Save';btn.style.background='#4c8bf5';},1500);
            const pv = document.getElementById(pvId); if(pv) pv.remove();
            document.getElementById('kcp-status').textContent = 'Theme saved and applied!';
        }).catch(e => {
            document.getElementById('kcp-status').textContent = 'Save failed: '+e;
        });
    });
    document.getElementById('kcp-reset').addEventListener('click', () => {
        fetch('http://127.0.0.1:9400/cockpit/reset',{method:'POST'}).then(() => {
            zones.forEach(z => {
                const def = {bg:'#1e1e2e',sidebar:'#161b22',text:'#e0e0e0',bubbles:'#2a2a3a',input:'#1e1e2e'};
                document.getElementById('kcp-'+z).value = def[z];
                document.getElementById('kcp-'+z+'-hex').value = def[z];
            });
            const pv = document.getElementById(pvId); if(pv) pv.remove();
            document.getElementById('kcp-status').textContent = 'Theme reset to defaults';
        });
    });
    document.querySelectorAll('.kcp-preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const p = presets[btn.dataset.preset]; if(!p) return;
            zones.forEach(z => {
                document.getElementById('kcp-'+z).value = p[z];
                document.getElementById('kcp-'+z+'-hex').value = p[z];
            });
            livePreview();
            document.getElementById('kcp-status').textContent = btn.dataset.preset+' preset loaded (click Apply to save)';
        });
    });
    let dragging=false, ox=0, oy=0;
    document.getElementById('kcp-drag-handle').addEventListener('mousedown', e => {
        dragging=true; ox=e.clientX-overlay.offsetLeft; oy=e.clientY-overlay.offsetTop;
    });
    document.addEventListener('mousemove', e => {
        if(!dragging) return;
        overlay.style.left=(e.clientX-ox)+'px'; overlay.style.top=(e.clientY-oy)+'px'; overlay.style.right='auto';
    });
    document.addEventListener('mouseup', () => { dragging=false; });
    return 'Color picker overlay opened';
})()""";


# ---------------------------------------------------------------------------
# Domain -> short name mapping
# ---------------------------------------------------------------------------
DOMAIN_NAMES = {
    "dash.cloudflare.com": "cloudflare",
    "admin.google.com": "google-admin",
    "console.cloud.google.com": "gcp",
    "github.com": "github",
    "vault.arknexus.net": "vault",
    "hub.arknexus.net": "hub",
    "platform.openai.com": "openai",
    "app.digitalocean.com": "digitalocean",
    "cloud.digitalocean.com": "digitalocean",
    "perplexity.ai": "perplexity",
    "payback": "meshcentral",
}


ALLOWED_SCHEMES = {"http", "https"}


def normalize_url(url):
    """Add https:// if no protocol, reject unsafe schemes."""
    if not url:
        return url
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
    elif parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError(f"Blocked URL scheme: {parsed.scheme}://. Only http/https allowed.")
    return url


def auto_name_from_url(url):
    """Generate a short tab name from a URL."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or "unknown"
        port = parsed.port

        # Check localhost special cases
        if hostname in ("localhost", "127.0.0.1"):
            if port == 8080:
                return PINNED_TAB_NAME
            return f"local-{port}" if port else "localhost"

        # Check domain map
        for domain, name in DOMAIN_NAMES.items():
            if domain in hostname or domain in url:
                return name

        # Fallback: first meaningful part of hostname
        parts = hostname.replace("www.", "").split(".")
        return parts[0] if parts else "unknown"
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Goose3 clean extraction
# ---------------------------------------------------------------------------
def extract_clean_content(html, url):
    """Use Goose3 to extract clean article/page content from raw HTML."""
    try:
        from goose3 import Goose

        g = Goose()
        article = g.extract(raw_html=html, url=url)
        result = {
            "title": article.title or "",
            "meta_description": article.meta_description or "",
            "text": (article.cleaned_text or "")[:MAX_CONTENT_CHARS],
            "links": [],
        }
        # Extract top links if available
        if article.links:
            result["links"] = list(article.links)[:20]
        g.close()
        return result
    except Exception as e:
        return {"error": f"Goose3 extraction failed: {str(e)}"}


# ---------------------------------------------------------------------------
# Theme persistence
# ---------------------------------------------------------------------------
def load_theme():
    """Load saved theme from disk."""
    try:
        if THEME_FILE.exists():
            return json.loads(THEME_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"css": "", "rules": []}


def save_theme(theme):
    """Save theme to disk."""
    THEME_FILE.write_text(json.dumps(theme, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Approval system for mutation actions
# ---------------------------------------------------------------------------
_pending_approval = {}  # code -> {action, tab, details, expires}


def generate_approval_code():
    """Generate a 4-digit approval code."""
    code = str(secrets.randbelow(9000) + 1000)
    return code


def request_approval(action, tab, details):
    """Create a pending approval and return the code."""
    code = generate_approval_code()
    _pending_approval[code] = {
        "action": action,
        "tab": tab,
        "details": details,
        "expires": time.time() + 300,  # 5 min expiry
    }
    return code


def validate_approval(code, action, tab):
    """Validate an approval code. Returns True if valid, consumes the code."""
    # Clean expired codes
    now = time.time()
    expired = [k for k, v in _pending_approval.items() if v["expires"] < now]
    for k in expired:
        del _pending_approval[k]

    if code not in _pending_approval:
        return False
    entry = _pending_approval[code]
    if entry["action"] == action and entry["tab"] == tab:
        del _pending_approval[code]
        return True
    return False


# ---------------------------------------------------------------------------
# Browser Manager (Playwright)
# ---------------------------------------------------------------------------
class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.tabs = {}  # name -> page
        self._lock = threading.Lock()
        # Keep @_karma alive and ready
        self._keepalive_thread = None
        self._stop_keepalive = threading.Event()
        self._reopening_karma = False  # Guard against recursive reopen

    def start(self):
        """Launch browser with persistent profile and pin Open WebUI."""
        from playwright.sync_api import sync_playwright

        logging.info("[start] Launching Playwright persistent context at %s", BROWSER_PROFILE)
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE),
            headless=False,
            viewport={"width": 1400, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )

        # Close ALL restored pages from the persistent context except the first one
        # This prevents blank-tab accumulation across restarts
        restored = self.context.pages[:]
        if restored:
            pinned = restored[0]
            for orphan in restored[1:]:
                try:
                    orphan.close()
                except Exception:
                    pass
            logging.info("[start] Closed %d orphaned restored pages", len(restored) - 1)
        else:
            pinned = self.context.new_page()

        try:
            pinned.goto(OPEN_WEBUI_URL, timeout=10000)
            logging.info("[start] Navigated pinned tab to %s", OPEN_WEBUI_URL)
        except Exception as e:
            logging.warning("[start] Could not navigate pinned tab yet: %s", e)

        self.tabs[PINNED_TAB_NAME] = pinned
        logging.info("[start] Pinned tab set: %s", PINNED_TAB_NAME)
        print(f"[Cockpit] Browser started. Open WebUI pinned at {OPEN_WEBUI_URL}")

        # Reopen @_karma if manually closed
        try:
            pinned.on("close", lambda: self._reopen_karma_tab())
        except Exception as e:
            logging.warning("[start] Could not bind close handler: %s", e)

        # Inject saved theme
        self.inject_theme()

        # Set window title to ArkNexus Cockpit
        try:
            pinned.evaluate("""() => {
                document.title = 'ArkNexus Cockpit';
                new MutationObserver(() => {
                    if (document.title !== 'ArkNexus Cockpit')
                        document.title = 'ArkNexus Cockpit';
                }).observe(document.querySelector('title'), {childList: true});
            }""")
        except Exception as e:
            logging.warning("[start] Branding injection failed: %s", e)

        # Start keepalive monitor
        if not self._keepalive_thread or not self._keepalive_thread.is_alive():
            self._stop_keepalive.clear()
            self._keepalive_thread = threading.Thread(target=self._keepalive_loop, daemon=True)
            self._keepalive_thread.start()
            logging.info("[start] Keepalive thread started")

    def stop(self):
        """Close browser."""
        try:
            self._stop_keepalive.set()
            if self._keepalive_thread and self._keepalive_thread.is_alive():
                self._keepalive_thread.join(timeout=2)
        except Exception:
            pass
        if self.context:
            try:
                self.context.close()
            except Exception as e:
                logging.warning("[stop] context.close failed: %s", e)
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception as e:
                logging.warning("[stop] playwright.stop failed: %s", e)
        logging.info("[stop] Cockpit stopped")
        print("[Cockpit] Browser closed.")

    def _resolve_tab(self, name):
        """Find a tab by name. Returns (page, error_msg)."""
        if name in self.tabs:
            page = self.tabs[name]
            # Check if page is still open
            try:
                _ = page.url
                return page, None
            except Exception:
                del self.tabs[name]
                return None, f"Tab '{name}' was closed externally."
        return None, f"Tab '{name}' not found. Use /tabs to list open tabs."

    def _reopen_karma_tab(self):
        """(Re)create the pinned @_karma tab if missing/closed."""
        # Guard against recursive/concurrent reopen
        if self._reopening_karma:
            logging.debug("[_reopen_karma_tab] Already reopening, skipping")
            return
        self._reopening_karma = True
        try:
            page = self.context.new_page()
            try:
                page.goto(OPEN_WEBUI_URL, timeout=15000, wait_until="domcontentloaded")
                logging.info("[_reopen_karma_tab] Navigated to %s", OPEN_WEBUI_URL)
            except Exception as e:
                logging.warning("[_reopen_karma_tab] Navigation failed: %s", e)
            self.tabs[PINNED_TAB_NAME] = page
            try:
                page.on("close", lambda: self._reopen_karma_tab())
            except Exception as e:
                logging.warning("[_reopen_karma_tab] Close bind failed: %s", e)
            # Re-apply branding and theme
            try:
                page.evaluate("""() => {
                    document.title = 'ArkNexus Cockpit';
                    new MutationObserver(() => {
                        if (document.title !== 'ArkNexus Cockpit')
                            document.title = 'ArkNexus Cockpit';
                    }).observe(document.querySelector('title'), {childList: true});
                }""")
            except Exception as e:
                logging.warning("[_reopen_karma_tab] Branding injection failed: %s", e)
            self.inject_theme()
        except Exception as e:
            logging.error("[_reopen_karma_tab] Exception: %s", e)
        finally:
            self._reopening_karma = False

    def _refocus_karma(self):
        """Bring @_karma tab back to the foreground."""
        try:
            page = self.tabs.get(PINNED_TAB_NAME)
            if page:
                page.bring_to_front()
        except Exception as e:
            logging.debug("[_refocus_karma] %s", e)

    def _keepalive_loop(self):
        while not self._stop_keepalive.is_set():
            try:
                page = self.tabs.get(PINNED_TAB_NAME)
                if page is None:
                    self._reopen_karma_tab()
                else:
                    # Ensure Open WebUI stays loaded in @_karma
                    # All page access wrapped to handle greenlet thread conflicts
                    try:
                        url = page.url
                        if "localhost:8080" not in url:
                            logging.warning("[keepalive] @_karma URL drifted to %s — navigating back", url)
                            page.goto(OPEN_WEBUI_URL, timeout=10000)
                    except Exception as e:
                        # Greenlet/thread errors are expected here — skip silently
                        if "greenlet" not in str(e).lower():
                            logging.warning("[keepalive] URL check failed: %s", e)
                    # Warm up chat input selector lazily
                    try:
                        page.wait_for_selector("#chat-input, div.ProseMirror[contenteditable='true'], [contenteditable='true'][id*='chat']", timeout=1000)
                    except Exception:
                        pass  # Expected during concurrent Flask requests
            except Exception:
                pass
            time.sleep(5)

    def list_tabs(self):
        """List all named tabs with URL and title."""
        # Ensure @_karma exists
        if PINNED_TAB_NAME not in self.tabs:
            logging.warning("[list_tabs] @_karma missing — reopening")
            self._reopen_karma_tab()
        result = []
        dead = []
        for name, page in self.tabs.items():
            try:
                result.append({
                    "name": name,
                    "url": page.url,
                    "title": page.title(),
                    "pinned": name == PINNED_TAB_NAME,
                })
            except Exception:
                dead.append(name)
        for name in dead:
            del self.tabs[name]
        return result

    def open_tab(self, url, name=None):
        """Open a new tab, navigate to URL, auto-name it."""
        try:
            url = normalize_url(url)
        except ValueError as e:
            return None, str(e)
        if name:
            name = name.lstrip("@")  # Strip @ prefix if model passes it
        with self._lock:
            page = self.context.new_page()
            try:
                page.goto(url, timeout=15000, wait_until="domcontentloaded")
            except Exception as e:
                page.close()
                return None, f"Failed to navigate to {url}: {str(e)}"

            if not name:
                name = auto_name_from_url(url)

            # Handle name collisions
            base_name = name
            counter = 2
            while name in self.tabs:
                name = f"{base_name}-{counter}"
                counter += 1

            self.tabs[name] = page
            self._refocus_karma()
            return name, None

    def close_tab(self, name):
        """Close a named tab."""
        if name == PINNED_TAB_NAME:
            return "Cannot close the pinned Karma tab."
        page, err = self._resolve_tab(name)
        if err:
            return err
        try:
            page.close()
        except Exception:
            pass
        del self.tabs[name]
        self._refocus_karma()
        return None

    def navigate_tab(self, name, url):
        """Navigate an existing tab to a new URL."""
        try:
            url = normalize_url(url)
        except ValueError as e:
            return str(e)
        if name == PINNED_TAB_NAME:
            return "Cannot navigate the pinned Karma tab."
        page, err = self._resolve_tab(name)
        if err:
            return err
        try:
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            self._refocus_karma()
            return None
        except Exception as e:
            return f"Navigation failed: {str(e)}"

    def read_tab(self, name):
        """Read text content from a named tab."""
        page, err = self._resolve_tab(name)
        if err:
            return None, err
        try:
            url = page.url
            title = page.title()
            text = page.inner_text("body")[:MAX_CONTENT_CHARS]
            return {
                "tab": name,
                "url": url,
                "title": title,
                "text": text,
            }, None
        except Exception as e:
            return None, f"Read failed: {str(e)}"

    def read_tab_clean(self, name):
        """Read cleaned content from a named tab using Goose3."""
        page, err = self._resolve_tab(name)
        if err:
            return None, err
        try:
            url = page.url
            html = page.content()
            result = extract_clean_content(html, url)
            result["tab"] = name
            result["url"] = url
            # If Goose3 returned very little, fall back to raw text
            if not result.get("text") or len(result.get("text", "")) < 50:
                result["text"] = page.inner_text("body")[:MAX_CONTENT_CHARS]
                result["extraction_method"] = "fallback_raw"
            else:
                result["extraction_method"] = "goose3"
            return result, None
        except Exception as e:
            return None, f"Clean read failed: {str(e)}"

    def screenshot_tab(self, name):
        """Take a screenshot of a named tab."""
        page, err = self._resolve_tab(name)
        if err:
            return None, err
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{ts}.png"
            filepath = SCREENSHOT_DIR / filename
            page.screenshot(path=str(filepath), full_page=False)
            return {"tab": name, "path": str(filepath), "filename": filename}, None
        except Exception as e:
            return None, f"Screenshot failed: {str(e)}"

    def click_element(self, name, selector):
        """Click an element on a named tab (requires prior approval)."""
        if name == PINNED_TAB_NAME:
            return "Cannot perform actions on the pinned Karma tab."
        page, err = self._resolve_tab(name)
        if err:
            return err
        try:
            page.click(selector, timeout=5000)
            return None
        except Exception as e:
            return f"Click failed: {str(e)}"

    def fill_element(self, name, selector, text):
        """Fill a form field on a named tab (requires prior approval)."""
        if name == PINNED_TAB_NAME:
            return "Cannot perform actions on the pinned Karma tab."
        page, err = self._resolve_tab(name)
        if err:
            return err
        try:
            page.fill(selector, text, timeout=5000)
            return None
        except Exception as e:
            return f"Fill failed: {str(e)}"

    def get_links(self, name):
        """Get all links from a named tab."""
        page, err = self._resolve_tab(name)
        if err:
            return None, err
        try:
            links = page.eval_on_selector_all(
                "a[href]",
                """els => els.map(e => ({
                    text: e.innerText.trim().substring(0, 80),
                    href: e.href
                })).filter(l => l.text && l.href).slice(0, 30)"""
            )
            return links, None
        except Exception as e:
            return None, f"Get links failed: {str(e)}"


    # ------------------------------------------------------------------
    # Cockpit customization
    # ------------------------------------------------------------------
    def inject_theme(self):
        """Inject the saved theme CSS into the _karma tab."""
        theme = load_theme()
        css = theme.get("css", "")
        page, err = self._resolve_tab(PINNED_TAB_NAME)
        if err or not css:
            return
        try:
            page.evaluate("""(css) => {
                let el = document.getElementById('karma-theme');
                if (!el) { el = document.createElement('style'); el.id = 'karma-theme'; document.head.appendChild(el); }
                el.textContent = css;
            }""", css)
        except Exception:
            pass

    @staticmethod
    def _ensure_important(css):
        """Auto-add !important to every CSS declaration that lacks it."""
        import re
        def add_imp(match):
            val = match.group(1)
            if '!important' in val:
                return match.group(0)
            return val.rstrip().rstrip(';') + ' !important;'
        # Match property values ending with ; inside rule blocks
        return re.sub(r'(:[^;}{]+;)', add_imp, css)

    def add_style(self, css, description=""):
        """Replace the entire theme with a new CSS rule, persist, and inject."""
        # If model sent bare declarations without a selector, wrap in body
        css = css.strip()
        if css and '{' not in css:
            css = 'body, .app, main { ' + css.rstrip(';') + '; }'
        css = self._ensure_important(css)
        # Replace mode: each customize call is the new theme
        theme = {
            "css": css,
            "rules": [{
                "css": css,
                "description": description,
                "added": datetime.now().isoformat(),
            }],
        }
        save_theme(theme)
        self.inject_theme()
        return theme

    def reset_theme(self):
        """Clear all custom styles."""
        save_theme({"css": "", "rules": []})
        page, err = self._resolve_tab(PINNED_TAB_NAME)
        if not err:
            try:
                page.evaluate("() => { let el = document.getElementById('karma-theme'); if (el) el.remove(); }")
            except Exception:
                pass

    def execute_on_cockpit(self, js_code):
        """Execute JavaScript on the _karma tab."""
        page, err = self._resolve_tab(PINNED_TAB_NAME)
        if err:
            return None, err
        try:
            result = page.evaluate(js_code)
            return result, None
        except Exception as e:
            return None, f"JS execution failed: {str(e)}"

    def type_on_cockpit(self, selector, text, press_enter=False):
        """Use Playwright's native keyboard to type on the _karma tab.
        Robustly locate and focus the Tiptap/ProseMirror chat editor."""
        page, err = self._resolve_tab(PINNED_TAB_NAME)
        if err:
            return err
        try:
            candidates = [
                selector or "#chat-input",
                "#chat-input",
                "div#chat-input",
                "div.ProseMirror[contenteditable='true']",
                "[contenteditable='true'][id*='chat']",
                "[contenteditable='true']",
                "div[role='textbox']",
                "textarea[placeholder*='Send']",
                "textarea",
            ]
            clicked = False
            for sel in candidates:
                try:
                    loc = page.locator(sel).first
                    if loc.count() > 0:
                        loc.click(timeout=800)
                        clicked = True
                        break
                except Exception:
                    continue
            if not clicked:
                # Fallback: click near bottom center of viewport to focus editor
                box = page.viewport_size or {"width": 1200, "height": 900}
                page.mouse.click(int(box["width"]) // 2, int(box["height"]) - 80)
            import time as _time
            _time.sleep(0.2)
            # Select all existing content and delete it
            try:
                page.keyboard.press("Control+a")
                page.keyboard.press("Backspace")
            except Exception:
                pass
            _time.sleep(0.1)
            page.keyboard.type(text, delay=15)
            _time.sleep(0.2)
            if press_enter:
                page.keyboard.press("Enter")
            return None
        except Exception as e:
            return f"Type failed: {str(e)}"

    def wait_for_response(self, timeout=90):
        """Wait for Karma to finish generating a response on the cockpit.
        Returns the response text or error."""
        page, err = self._resolve_tab(PINNED_TAB_NAME)
        if err:
            return None, err
        import time as _time
        start = _time.time()
        # Wait until we detect an assistant message and generation stop
        while _time.time() - start < timeout:
            _time.sleep(2)
            try:
                status = page.evaluate("""(() => {
                    const stopBtn = document.getElementById('stop-response-button');
                    if (stopBtn) return 'GENERATING';
                    const sels = ['[data-message-id]', 'article', '[data-testid="message"]', '[class*="assistant"], .assistant-message'];
                    let count = 0; for (const s of sels) count = Math.max(count, document.querySelectorAll(s).length);
                    if (count >= 1) return 'DONE:' + count; // allow first assistant message
                    return 'WAITING:' + count;
                })()""")
                if str(status).startswith('DONE'):
                    _time.sleep(1)
                    break
            except Exception:
                pass
        # Read the last message using robust selectors
        try:
            result = page.evaluate("""(() => {
                const sels = ['[data-message-id]', 'article', '[data-testid="message"]', '[class*="assistant"], .assistant-message'];
                let nodes = [];
                for (const s of sels) {
                    const n = Array.from(document.querySelectorAll(s));
                    if (n.length > nodes.length) nodes = n;
                }
                if (nodes.length < 1) return {error: 'No response messages found', count: 0};
                const last = nodes[nodes.length - 1];
                return { text: (last.innerText||'').trim().substring(0, 4000), count: nodes.length };
            })()""")
            return result, None
        except Exception as e:
            return None, f"Read failed: {str(e)}"

    def get_theme(self):
        """Get the current theme."""
        return load_theme()

    def inject_color_picker(self):
        """Inject the interactive color picker overlay into @_karma."""
        page, err = self._resolve_tab(PINNED_TAB_NAME)
        if err:
            return None, err
        try:
            result = page.evaluate(COLOR_PICKER_JS)
            return result, None
        except Exception as e:
            return None, f"Color picker injection failed: {str(e)}"

    def apply_preset(self, name):
        """Apply a named theme preset."""
        if name == "default":
            self.reset_theme()
            return {"preset": "default", "action": "reset"}, None
        preset = THEME_PRESETS.get(name)
        if not preset:
            available = list(THEME_PRESETS.keys()) + ["default"]
            return None, f"Unknown preset '{name}'. Available: {', '.join(available)}"
        css = preset_to_css(preset)
        theme = self.add_style(css, f"Preset: {name}")
        return {"preset": name, "applied": True, "total_rules": len(theme["rules"])}, None


# ---------------------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------------------
app = Flask(__name__)
mgr = BrowserManager()

# Unauthenticated routes (health check for monitoring)
_PUBLIC_ROUTES = {"/health"}


@app.before_request
def check_api_token():
    """Require Bearer token for all routes except health."""
    if request.path in _PUBLIC_ROUTES or request.method == "OPTIONS":
        return None
    auth = request.headers.get("Authorization", "")
    if auth == f"Bearer {API_TOKEN}":
        return None
    return jsonify({"error": "Unauthorized. Provide Authorization: Bearer <token>"}), 401


@app.after_request
def add_cors_headers(response):
    """Allow cross-origin requests from the cockpit browser (localhost:8080 -> 127.0.0.1:9400)."""
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8080"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.route("/health", methods=["GET"])
def health():
    # Report whether @_karma is present and chat appears ready
    ready = False
    try:
        page = mgr.tabs.get(PINNED_TAB_NAME)
        if page:
            try:
                url = page.url
            except Exception:
                url = "(unavailable)"
            if "localhost:8080" in str(url):
                try:
                    page.wait_for_selector("#chat-input, div.ProseMirror[contenteditable='true']", timeout=500)
                    ready = True
                except Exception:
                    ready = False
        else:
            logging.warning("[health] @_karma not in tabs")
    except Exception as e:
        logging.error("[health] Exception: %s", e)
        ready = False
    return jsonify({"status": "ok", "service": "karma-cockpit", "version": "2.0.0", "karma_ready": ready})


@app.route("/tabs", methods=["GET"])
def list_tabs():
    tabs = mgr.list_tabs()
    return jsonify({"tabs": tabs})


@app.route("/tab/open", methods=["POST"])
def open_tab():
    data = request.json or {}
    url = data.get("url")
    name = data.get("name")
    if not url:
        return jsonify({"error": "url is required"}), 400
    tab_name, err = mgr.open_tab(url, name)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"tab": tab_name, "url": url})


@app.route("/tab/close", methods=["POST"])
def close_tab():
    data = request.json or {}
    tab = data.get("tab")
    if not tab:
        return jsonify({"error": "tab name is required"}), 400
    err = mgr.close_tab(tab)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"closed": tab})


@app.route("/tab/navigate", methods=["POST"])
def navigate_tab():
    data = request.json or {}
    tab = data.get("tab")
    url = data.get("url")
    if not tab or not url:
        return jsonify({"error": "tab and url are required"}), 400
    err = mgr.navigate_tab(tab, url)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"tab": tab, "navigated_to": url})


@app.route("/tab/read", methods=["POST"])
def read_tab():
    data = request.json or {}
    tab = data.get("tab")
    if not tab:
        return jsonify({"error": "tab name is required"}), 400
    result, err = mgr.read_tab(tab)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@app.route("/tab/read_clean", methods=["POST"])
def read_tab_clean():
    data = request.json or {}
    tab = data.get("tab")
    if not tab:
        return jsonify({"error": "tab name is required"}), 400
    result, err = mgr.read_tab_clean(tab)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@app.route("/tab/screenshot", methods=["POST"])
def screenshot_tab():
    data = request.json or {}
    tab = data.get("tab")
    if not tab:
        return jsonify({"error": "tab name is required"}), 400
    result, err = mgr.screenshot_tab(tab)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@app.route("/tab/links", methods=["POST"])
def get_links():
    data = request.json or {}
    tab = data.get("tab")
    if not tab:
        return jsonify({"error": "tab name is required"}), 400
    result, err = mgr.get_links(tab)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"tab": tab, "links": result})


@app.route("/tab/click", methods=["POST"])
def click_element():
    """Click an element. Autonomous in AUTONOMOUS_MODE, otherwise approval-gated."""
    data = request.json or {}
    tab = data.get("tab")
    selector = data.get("selector")
    confirm_code = data.get("confirm_code")

    if not tab or not selector:
        return jsonify({"error": "tab and selector are required"}), 400

    # Autonomous mode: execute immediately (no approval needed for clicks)
    if AUTONOMOUS_MODE and not confirm_code:
        err = mgr.click_element(tab, selector)
        if err:
            return jsonify({"error": err}), 400
        return jsonify({"clicked": selector, "tab": tab})

    if not confirm_code:
        code = request_approval("click", tab, f"Click '{selector}' on tab '{tab}'")
        return jsonify({
            "approval_required": True,
            "code": code,
            "message": f"APPROVAL REQUIRED: To click '{selector}' on tab '{tab}', "
                       f"Neo must say: APPROVE {code}",
            "action": "click",
            "tab": tab,
            "selector": selector,
        }), 202

    if not validate_approval(confirm_code, "click", tab):
        return jsonify({"error": "Invalid or expired approval code."}), 403

    err = mgr.click_element(tab, selector)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"clicked": selector, "tab": tab})


@app.route("/tab/fill", methods=["POST"])
def fill_element():
    """Fill a form field. Autonomous for non-sensitive fields, approval-gated for passwords."""
    data = request.json or {}
    tab = data.get("tab")
    selector = data.get("selector")
    text = data.get("text", "")
    confirm_code = data.get("confirm_code")

    if not tab or not selector:
        return jsonify({"error": "tab, selector are required"}), 400

    # Autonomous mode: check field sensitivity before deciding
    if AUTONOMOUS_MODE and not confirm_code:
        page, perr = mgr._resolve_tab(tab)
        if perr:
            return jsonify({"error": perr}), 400
        if not _is_sensitive_field(page, selector):
            err = mgr.fill_element(tab, selector, text)
            if err:
                return jsonify({"error": err}), 400
            return jsonify({"filled": selector, "tab": tab})
        # Sensitive field: fall through to approval

    if not confirm_code:
        code = request_approval("fill", tab, f"Fill '{selector}' with '{text[:50]}' on tab '{tab}'")
        return jsonify({
            "approval_required": True,
            "code": code,
            "message": f"APPROVAL REQUIRED: To fill '{selector}' on tab '{tab}', "
                       f"Neo must say: APPROVE {code}",
            "action": "fill",
            "tab": tab,
            "selector": selector,
            "text_preview": text[:50],
        }), 202

    if not validate_approval(confirm_code, "fill", tab):
        return jsonify({"error": "Invalid or expired approval code."}), 403

    err = mgr.fill_element(tab, selector, text)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"filled": selector, "tab": tab})



# ---------------------------------------------------------------------------
# Cockpit Customization Endpoints
# ---------------------------------------------------------------------------

@app.route("/cockpit/style", methods=["POST"])
def cockpit_style():
    """Add CSS to the cockpit theme."""
    data = request.json or {}
    css = data.get("css", "")
    description = data.get("description", "")
    if not css:
        return jsonify({"error": "css is required"}), 400
    theme = mgr.add_style(css, description)
    return jsonify({"applied": True, "description": description, "total_rules": len(theme["rules"])})


@app.route("/cockpit/exec", methods=["POST"])
def cockpit_exec():
    """Execute JS on the cockpit. Requires approval."""
    data = request.json or {}
    js_code = data.get("js", "")
    confirm_code = data.get("confirm_code")
    description = data.get("description", "")
    if not js_code:
        return jsonify({"error": "js is required"}), 400

    if not confirm_code:
        code = request_approval("exec", "_karma", f"Execute JS: {description or js_code[:80]}")
        return jsonify({
            "approval_required": True,
            "code": code,
            "message": f"APPROVAL REQUIRED: To execute JS on cockpit, Neo must say: APPROVE {code}",
            "description": description or js_code[:80],
        }), 202

    if not validate_approval(confirm_code, "exec", "_karma"):
        return jsonify({"error": "Invalid or expired approval code."}), 403

    result, err = mgr.execute_on_cockpit(js_code)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"executed": True, "result": str(result) if result is not None else None})


@app.route("/cockpit/theme", methods=["GET"])
def cockpit_theme():
    """Get the current cockpit theme."""
    theme = mgr.get_theme()
    return jsonify(theme)


@app.route("/cockpit/reset", methods=["POST"])
def cockpit_reset():
    """Reset all cockpit customizations."""
    mgr.reset_theme()
    return jsonify({"reset": True})


@app.route("/cockpit/reinject", methods=["POST"])
def cockpit_reinject():
    """Re-inject the saved theme (useful after page refresh)."""
    mgr.inject_theme()
    return jsonify({"reinjected": True})


@app.route("/cockpit/color_picker", methods=["POST"])
def cockpit_color_picker():
    """Inject the interactive color picker overlay into the cockpit."""
    result, err = mgr.inject_color_picker()
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"opened": True, "result": result})


@app.route("/cockpit/preset", methods=["POST"])
def cockpit_preset():
    """Apply a named theme preset."""
    data = request.json or {}
    name = data.get("name", "").lower().strip()
    if not name:
        available = list(THEME_PRESETS.keys()) + ["default"]
        return jsonify({"error": f"name is required. Available: {', '.join(available)}"}), 400
    result, err = mgr.apply_preset(name)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@app.route("/cockpit/type", methods=["POST"])
def cockpit_type():
    """Type text into an element on the cockpit using Playwright's native keyboard.
    This works with ProseMirror/Tiptap editors. Requires approval."""
    data = request.json or {}
    selector = data.get("selector", "#chat-input")
    text = data.get("text", "")
    press_enter = data.get("press_enter", False)
    confirm_code = data.get("confirm_code")

    if not text:
        return jsonify({"error": "text is required"}), 400

    if not confirm_code:
        code = request_approval("type", "_karma", f"Type '{text[:50]}' into {selector}")
        return jsonify({
            "approval_required": True,
            "code": code,
            "message": f"APPROVAL REQUIRED: To type on cockpit, say: APPROVE {code}",
            "text_preview": text[:50],
        }), 202

    if not validate_approval(confirm_code, "type", "_karma"):
        return jsonify({"error": "Invalid or expired approval code."}), 403

    err = mgr.type_on_cockpit(selector, text, press_enter)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"typed": True, "selector": selector, "press_enter": press_enter})


@app.route("/cockpit/send", methods=["POST"])
def cockpit_send():
    """Send a message in the Open WebUI chat (type + Enter) and wait for response.
    Convenience endpoint combining type + wait. Requires approval."""
    data = request.json or {}
    text = data.get("text", "")
    wait = data.get("wait", 90)
    confirm_code = data.get("confirm_code")

    if not text:
        return jsonify({"error": "text is required"}), 400

    if not confirm_code:
        code = request_approval("send", "_karma", f"Send message: '{text[:50]}'")
        return jsonify({
            "approval_required": True,
            "code": code,
            "message": f"APPROVAL REQUIRED: To send message, say: APPROVE {code}",
            "text_preview": text[:50],
        }), 202

    if not validate_approval(confirm_code, "send", "_karma"):
        return jsonify({"error": "Invalid or expired approval code."}), 403

    # Ensure chat editor is present (open a new chat if needed)
    try:
        page, perr = mgr._resolve_tab("_karma")
        if perr:
            return jsonify({"error": perr}), 400
        try:
            page.wait_for_selector('#chat-input, div.ProseMirror[contenteditable="true"]', timeout=1200)
        except Exception:
            # Click "New Chat" to open the composer
            try:
                page.evaluate("""(() => { const btn = Array.from(document.querySelectorAll('a,button')).find(e => ((e.getAttribute('aria-label')||e.innerText||'').trim() === 'New Chat')); if (btn) btn.click(); })()""")
                page.wait_for_selector('#chat-input, div.ProseMirror[contenteditable="true"]', timeout=3000)
            except Exception:
                pass
    except Exception as e:
        return jsonify({"error": f"Prepare editor failed: {str(e)}"}), 400

    # Type
    err = mgr.type_on_cockpit("#chat-input", text, press_enter=False)
    if err:
        return jsonify({"error": err}), 400

    # Try clicking the explicit send button; fallback to pressing Enter in the editor
    try:
        page, perr = mgr._resolve_tab("_karma")
        if perr:
            return jsonify({"error": perr}), 400
        import time as _time
        _time.sleep(0.2)
        clicked = False
        try:
            page.click('#send-message-button', timeout=800)
            clicked = True
        except Exception:
            clicked = False
        if not clicked:
            # Try any visible submit button
            try:
                btn = page.locator('button[type=submit]:visible').first
                if btn and btn.count() > 0:
                    btn.click(timeout=800)
                    clicked = True
            except Exception:
                clicked = False
        if not clicked:
            # Focus the editor and hit Enter/Ctrl+Enter to submit
            try:
                loc = page.locator('#chat-input, div.ProseMirror[contenteditable="true"], [contenteditable="true"][id*="chat"], [contenteditable="true"]').first
                if loc and loc.count() > 0:
                    loc.click(timeout=800)
            except Exception:
                # Fallback: click near bottom center
                box = page.viewport_size or {"width": 1200, "height": 900}
                page.mouse.click(int(box["width"]) // 2, int(box["height"]) - 80)
            _time.sleep(0.1)
            page.keyboard.press('Enter')
            _time.sleep(0.2)
            # Try Ctrl+Enter as alternate submission
            page.keyboard.press('Control+Enter')
            _time.sleep(0.2)
    except Exception as e:
        return jsonify({"error": f"Send click failed: {str(e)}"}), 400

    # Wait for response
    result, err = mgr.wait_for_response(timeout=wait)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"sent": text[:50], "response": result})


@app.route("/cockpit/read_messages", methods=["GET"])
def cockpit_read_messages():
    """Read all messages from the current Open WebUI chat."""
    js = """(() => {
        const sels = [
            '[data-message-id]',
            'article',
            '[data-testid="message"]',
            '[class*="assistant"], .assistant-message, [class*="user"], .user-message',
        ];
        let nodes = [];
        for (const s of sels) {
            const n = Array.from(document.querySelectorAll(s));
            if (n.length > nodes.length) nodes = n;
        }
        return nodes.map((m, i) => ({ index: i, text: (m.innerText||'').trim().substring(0, 2000) }));
    })()"""
    result, err = mgr.execute_on_cockpit(js)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"messages": result or []})


# ---------------------------------------------------------------------------
# Gemini CLI Endpoints
# ---------------------------------------------------------------------------
GEMINI_CMD = os.path.join(os.environ.get("APPDATA", ""), "npm", "gemini.cmd")


def _run_gemini(prompt, file_path=None, timeout=60):
    """Run Gemini CLI in headless mode via stdin pipe. Returns (response_text, stats, error)."""
    # Build the prompt — prepend @file reference if a file is provided
    full_prompt = prompt
    if file_path:
        full_prompt = f"@{file_path} {prompt}"

    # Ensure GEMINI_API_KEY is available
    env = os.environ.copy()
    # Also check persistent user env in case session doesn't have it
    if "GEMINI_API_KEY" not in env:
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                val, _ = winreg.QueryValueEx(key, "GEMINI_API_KEY")
                env["GEMINI_API_KEY"] = val
        except Exception:
            pass
    if "GEMINI_API_KEY" not in env:
        return None, None, "GEMINI_API_KEY not set. Set it as a user environment variable."

    try:
        proc = subprocess.run(
            [GEMINI_CMD, "--output-format", "json"],
            input=full_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            # Parse common Gemini errors into friendly messages
            stderr_lower = stderr.lower()
            if "quota" in stderr_lower or "rate limit" in stderr_lower or "429" in stderr:
                return None, None, "Gemini API quota exceeded. Wait for daily reset or check your plan."
            if "api_key" in stderr_lower or "authentication" in stderr_lower or "401" in stderr:
                return None, None, "Gemini API key invalid or expired. Update GEMINI_API_KEY."
            if "permission" in stderr_lower or "403" in stderr:
                return None, None, "Gemini API permission denied. Check your API key permissions."
            return None, None, f"Gemini CLI error (code {proc.returncode}): {stderr[:300]}"

        # Parse JSON output — skip any non-JSON preamble lines (e.g. "Hook registry initialized")
        stdout = proc.stdout.strip()
        json_start = stdout.find("{")
        if json_start == -1:
            # Fallback: treat entire output as plain text response
            return stdout[:4000], None, None
        try:
            data = json.loads(stdout[json_start:])
        except json.JSONDecodeError:
            return stdout[:4000], None, None

        response = data.get("response", "(no response)")
        stats = data.get("stats", {})
        return response, stats, None

    except subprocess.TimeoutExpired:
        return None, None, f"Gemini CLI timed out after {timeout}s"
    except FileNotFoundError:
        return None, None, "Gemini CLI not installed. Run: npm install -g @google/gemini-cli"
    except Exception as e:
        return None, None, f"Gemini CLI error: {str(e)}"


@app.route("/gemini/query", methods=["POST"])
def gemini_query():
    """General-purpose Gemini query. Runs headlessly, returns response."""
    data = request.json or {}
    prompt = data.get("prompt", "")
    file_path = data.get("file")
    timeout = data.get("timeout", 60)
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    start = time.time()
    response, stats, err = _run_gemini(prompt, file_path, timeout)
    duration_ms = int((time.time() - start) * 1000)

    if err:
        return jsonify({"error": err}), 400

    result = {"response": response, "duration_ms": duration_ms}
    if stats:
        # Extract token count and model info
        models = stats.get("models", {})
        total_tokens = 0
        model_names = []
        for name, info in models.items():
            model_names.append(name)
            total_tokens += info.get("tokens", {}).get("total", 0)
        result["tokens_used"] = total_tokens
        result["models"] = model_names
    return jsonify(result)


@app.route("/gemini/analyze", methods=["POST"])
def gemini_analyze():
    """Multimodal analysis — analyze a screenshot, image, or PDF with Gemini."""
    data = request.json or {}
    file_path = data.get("file", "")
    prompt = data.get("prompt", "Describe what you see in detail.")
    timeout = data.get("timeout", 60)
    if not file_path:
        return jsonify({"error": "file path is required"}), 400
    if not os.path.exists(file_path):
        return jsonify({"error": f"File not found: {file_path}"}), 400

    start = time.time()
    response, stats, err = _run_gemini(prompt, file_path, timeout)
    duration_ms = int((time.time() - start) * 1000)

    if err:
        return jsonify({"error": err}), 400

    result = {"response": response, "file": file_path, "duration_ms": duration_ms}
    if stats:
        models = stats.get("models", {})
        total_tokens = sum(info.get("tokens", {}).get("total", 0) for info in models.values())
        result["tokens_used"] = total_tokens
    return jsonify(result)


# ---------------------------------------------------------------------------
# Agentic System Endpoints
# ---------------------------------------------------------------------------

@app.route("/shell/run", methods=["POST"])
def shell_run():
    """Run a PowerShell command. Always approval-gated."""
    data = request.json or {}
    command = data.get("command", "")
    confirm_code = data.get("confirm_code")
    timeout = min(data.get("timeout", 30), 120)

    blocked = _validate_command(command)
    if blocked:
        return jsonify({"error": blocked}), 403

    if not confirm_code:
        code = request_approval("shell", "_system", f"Run: {command[:100]}")
        return jsonify({
            "approval_required": True,
            "code": code,
            "message": f"APPROVAL REQUIRED: To run '{command[:100]}', "
                       f"Neo must say: APPROVE {code}",
            "command": command,
        }), 202

    if not validate_approval(confirm_code, "shell", "_system"):
        return jsonify({"error": "Invalid or expired approval code."}), 403

    start = time.time()
    try:
        proc = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", command],
            capture_output=True, text=True, timeout=timeout,
        )
        duration_ms = int((time.time() - start) * 1000)
        return jsonify({
            "stdout": _sanitize_output(proc.stdout),
            "stderr": _sanitize_output(proc.stderr, 2000),
            "exit_code": proc.returncode,
            "duration_ms": duration_ms,
            "command": command,
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": f"Command timed out after {timeout}s"}), 408
    except Exception as e:
        return jsonify({"error": f"Shell execution failed: {str(e)}"}), 500


@app.route("/file/read", methods=["POST"])
def file_read():
    """Read file contents. No approval needed."""
    data = request.json or {}
    path_str = data.get("path", "")
    start_line = data.get("start_line")
    end_line = data.get("end_line")

    try:
        path = _validate_path(path_str, "read")
    except ValueError as e:
        return jsonify({"error": str(e)}), 403

    if not path.is_file():
        return jsonify({"error": f"Not a file: {path}"}), 404

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines(keepends=True)
        total_lines = len(lines)

        if start_line is not None:
            s = max(0, int(start_line) - 1)
            e = int(end_line) if end_line else total_lines
            content = "".join(lines[s:e])

        truncated = len(content) > MAX_CONTENT_CHARS
        return jsonify({
            "path": str(path),
            "content": _sanitize_output(content),
            "size_bytes": path.stat().st_size,
            "total_lines": total_lines,
            "truncated": truncated,
        })
    except Exception as e:
        return jsonify({"error": f"Read failed: {str(e)}"}), 500


@app.route("/file/write", methods=["POST"])
def file_write():
    """Write or append to a file. Always approval-gated."""
    data = request.json or {}
    path_str = data.get("path", "")
    content = data.get("content", "")
    mode = data.get("mode", "write")
    confirm_code = data.get("confirm_code")

    try:
        path = _validate_path(path_str, "write")
    except ValueError as e:
        return jsonify({"error": str(e)}), 403

    if mode not in ("write", "append"):
        return jsonify({"error": "mode must be 'write' or 'append'"}), 400

    if not confirm_code:
        preview = content[:200] + ("..." if len(content) > 200 else "")
        code = request_approval("file_write", "_system",
                                f"{mode} {path.name}: {preview[:80]}")
        return jsonify({
            "approval_required": True,
            "code": code,
            "message": f"APPROVAL REQUIRED: To {mode} '{path.name}', "
                       f"Neo must say: APPROVE {code}",
            "path": str(path),
            "mode": mode,
            "content_preview": preview,
        }), 202

    if not validate_approval(confirm_code, "file_write", "_system"):
        return jsonify({"error": "Invalid or expired approval code."}), 403

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        open_mode = "a" if mode == "append" else "w"
        with open(path, open_mode, encoding="utf-8") as f:
            f.write(content)
        return jsonify({
            "path": str(path),
            "bytes_written": len(content.encode("utf-8")),
            "mode": mode,
        })
    except Exception as e:
        return jsonify({"error": f"Write failed: {str(e)}"}), 500


@app.route("/file/patch", methods=["POST"])
def file_patch():
    """Surgical search/replace edit. Always approval-gated."""
    data = request.json or {}
    path_str = data.get("path", "")
    search_text = data.get("search", "")
    replace_text = data.get("replace", "")
    confirm_code = data.get("confirm_code")

    if not search_text:
        return jsonify({"error": "search text is required"}), 400

    try:
        path = _validate_path(path_str, "write")
    except ValueError as e:
        return jsonify({"error": str(e)}), 403

    if not path.is_file():
        return jsonify({"error": f"Not a file: {path}"}), 404

    content = path.read_text(encoding="utf-8", errors="replace")
    count = content.count(search_text)
    if count == 0:
        return jsonify({"error": "Search text not found in file"}), 404

    if not confirm_code:
        preview_s = search_text[:80] + ("..." if len(search_text) > 80 else "")
        preview_r = replace_text[:80] + ("..." if len(replace_text) > 80 else "")
        code = request_approval("file_patch", "_system",
                                f"Patch {path.name}: '{preview_s}' -> '{preview_r}'")
        return jsonify({
            "approval_required": True,
            "code": code,
            "message": f"APPROVAL REQUIRED: To patch '{path.name}' ({count} occurrence(s)), "
                       f"Neo must say: APPROVE {code}",
            "path": str(path),
            "occurrences": count,
            "search_preview": preview_s,
            "replace_preview": preview_r,
        }), 202

    if not validate_approval(confirm_code, "file_patch", "_system"):
        return jsonify({"error": "Invalid or expired approval code."}), 403

    try:
        new_content = content.replace(search_text, replace_text)
        path.write_text(new_content, encoding="utf-8")
        return jsonify({
            "path": str(path),
            "occurrences_replaced": count,
            "size_bytes": len(new_content.encode("utf-8")),
        })
    except Exception as e:
        return jsonify({"error": f"Patch failed: {str(e)}"}), 500


@app.route("/file/list", methods=["POST"])
def file_list():
    """List directory contents. No approval needed."""
    data = request.json or {}
    path_str = data.get("path", "")
    pattern = data.get("pattern", "")

    try:
        path = _validate_path(path_str, "read")
    except ValueError as e:
        return jsonify({"error": str(e)}), 403

    if not path.is_dir():
        return jsonify({"error": f"Not a directory: {path}"}), 400

    try:
        entries = []
        for item in sorted(path.iterdir()):
            if pattern and not fnmatch.fnmatch(item.name, pattern):
                continue
            try:
                stat = item.stat()
                entries.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size_bytes": stat.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                })
            except Exception:
                entries.append({"name": item.name, "type": "unknown",
                                "size_bytes": 0, "modified": ""})
            if len(entries) >= 100:
                break
        return jsonify({"path": str(path), "entries": entries,
                        "count": len(entries)})
    except Exception as e:
        return jsonify({"error": f"List failed: {str(e)}"}), 500


@app.route("/file/search", methods=["POST"])
def file_search():
    """Search file contents (grep-like). No approval needed."""
    data = request.json or {}
    path_str = data.get("path", "")
    query = data.get("query", "")
    pattern = data.get("pattern", "")
    max_results = min(data.get("max_results", 20), 50)

    if not query:
        return jsonify({"error": "query is required"}), 400

    try:
        path = _validate_path(path_str, "read")
    except ValueError as e:
        return jsonify({"error": str(e)}), 403

    if not path.is_dir():
        return jsonify({"error": f"Not a directory: {path}"}), 400

    try:
        matches = []
        query_lower = query.lower()
        skip_dirs = {'.git', 'node_modules', '__pycache__', 'venv', '.venv',
                     'browser-profile'}

        for root, dirs, files in os.walk(str(path)):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]
            for fname in files:
                if pattern and not fnmatch.fnmatch(fname, pattern):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    if os.path.getsize(fpath) > 1_000_000:
                        continue
                except Exception:
                    continue
                # Skip binary
                try:
                    with open(fpath, 'rb') as bf:
                        if b'\x00' in bf.read(512):
                            continue
                except Exception:
                    continue
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        for line_num, line in enumerate(f, 1):
                            if query_lower in line.lower():
                                matches.append({
                                    "file": fpath,
                                    "line_num": line_num,
                                    "line_text": line.strip()[:200],
                                })
                                if len(matches) >= max_results:
                                    break
                except Exception:
                    continue
                if len(matches) >= max_results:
                    break
            if len(matches) >= max_results:
                break

        return jsonify({
            "query": query, "path": str(path),
            "matches": matches, "total_matches": len(matches),
            "truncated": len(matches) >= max_results,
        })
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500


@app.route("/file/semantic_search", methods=["POST"])
def file_semantic_search():
    """Semantic file search powered by Gemini. Finds conceptually relevant files."""
    data = request.json or {}
    path_str = data.get("path", "")
    query = data.get("query", "")
    pattern = data.get("pattern", "")
    max_files = min(data.get("max_files", 10), 30)

    if not query:
        return jsonify({"error": "query is required"}), 400

    try:
        path = _validate_path(path_str, "read")
    except ValueError as e:
        return jsonify({"error": str(e)}), 403

    if not path.is_dir():
        return jsonify({"error": f"Not a directory: {path}"}), 400

    # Collect file inventory: name + first few lines
    skip_dirs = {'.git', 'node_modules', '__pycache__', 'venv', '.venv',
                 'browser-profile'}
    file_summaries = []
    for root, dirs, files in os.walk(str(path)):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]
        for fname in files:
            if pattern and not fnmatch.fnmatch(fname, pattern):
                continue
            fpath = os.path.join(root, fname)
            try:
                if os.path.getsize(fpath) > 500_000:
                    continue
            except Exception:
                continue
            # Read first 3 lines for context
            try:
                with open(fpath, 'rb') as bf:
                    if b'\x00' in bf.read(512):
                        continue
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    head = [f.readline().strip() for _ in range(3)]
                rel = os.path.relpath(fpath, str(path))
                file_summaries.append(f"{rel}: {' | '.join(h for h in head if h)}")
            except Exception:
                continue
            if len(file_summaries) >= 200:
                break
        if len(file_summaries) >= 200:
            break

    if not file_summaries:
        return jsonify({"query": query, "results": [], "note": "No text files found"})

    # Ask Gemini to rank
    inventory = "\n".join(file_summaries)
    prompt = (f"Given this file inventory, list the top {max_files} files most relevant to: \"{query}\"\n"
              f"Return ONLY a JSON array of file paths (relative), most relevant first. No explanation.\n\n"
              f"{inventory}")

    response, stats, err = _run_gemini(prompt, None, 30)
    if err:
        return jsonify({"error": f"Gemini ranking failed: {err}"}), 500

    # Parse Gemini response — extract JSON array
    try:
        # Handle markdown code blocks
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        ranked = json.loads(text)
        if not isinstance(ranked, list):
            ranked = [ranked]
    except (json.JSONDecodeError, IndexError):
        # Fall back to line-by-line parsing
        ranked = [l.strip().strip('"').strip("'").strip(',') for l in response.strip().splitlines() if l.strip()]

    return jsonify({"query": query, "path": str(path), "results": ranked[:max_files]})


@app.route("/system/info", methods=["GET"])
def system_info():
    """Machine status snapshot. No approval needed."""
    try:
        import psutil

        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        ram = {
            "used_gb": round(mem.used / (1024**3), 1),
            "total_gb": round(mem.total / (1024**3), 1),
            "percent": mem.percent,
        }
        disk = shutil.disk_usage("C:\\")
        disk_info = {
            "used_gb": round(disk.used / (1024**3), 1),
            "total_gb": round(disk.total / (1024**3), 1),
            "percent": round(disk.used / disk.total * 100, 1),
        }
        boot = psutil.boot_time()
        uptime_hours = round((time.time() - boot) / 3600, 1)

        services = []
        svc_map = {"python": "Open WebUI", "ollama": "Ollama",
                   "node": "Gemini CLI", "pwsh": "PowerShell"}
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                pname = proc.info['name'].lower().replace('.exe', '')
                if pname in svc_map:
                    services.append({
                        "name": svc_map[pname],
                        "pid": proc.info['pid'],
                        "status": proc.info['status'],
                    })
            except Exception:
                continue

        return jsonify({
            "hostname": _platform.node(),
            "os": f"{_platform.system()} {_platform.release()}",
            "cpu_percent": cpu_percent,
            "ram": ram, "disk": disk_info,
            "uptime_hours": uptime_hours,
            "services": services,
        })
    except ImportError:
        return jsonify({"error": "psutil not installed. Run: pip install psutil"}), 500
    except Exception as e:
        return jsonify({"error": f"System info failed: {str(e)}"}), 500


@app.route("/web/search", methods=["POST"])
def web_search():
    """Search the web using DuckDuckGo. No approval needed."""
    data = request.json or {}
    query = data.get("query", "")
    max_results = min(data.get("max_results", 5), 10)

    if not query:
        return jsonify({"error": "query is required"}), 400

    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=max_results)
        formatted = [{
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "snippet": r.get("body", ""),
        } for r in results]
        return jsonify({"query": query, "results": formatted,
                        "source": "duckduckgo"})
    except ImportError:
        return jsonify({"error": "ddgs not installed. "
                        "Run: pip install ddgs"}), 500
    except Exception as e:
        return jsonify({
            "query": query, "results": [], "source": "duckduckgo",
            "fallback": True,
            "suggestion": f"DuckDuckGo failed ({str(e)[:80]}). "
                          "Use gemini_query() instead.",
        })


@app.route("/web/research", methods=["POST"])
def web_research():
    """Deep web research: search -> scrape top results -> synthesize with Gemini."""
    data = request.json or {}
    query = data.get("query", "")
    max_sources = min(data.get("max_sources", 3), 5)
    timeout = min(data.get("timeout", 60), 120)

    if not query:
        return jsonify({"error": "query is required"}), 400

    # Step 1: Search
    try:
        from ddgs import DDGS
        search_results = DDGS().text(query, max_results=max_sources + 2)
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

    if not search_results:
        return jsonify({"query": query, "synthesis": "No search results found.",
                        "sources": []})

    # Step 2: Scrape content from top results using browser
    sources = []
    for r in search_results[:max_sources]:
        url = r.get("href", "")
        title = r.get("title", "")
        snippet = r.get("body", "")
        content = snippet  # Fallback to snippet

        # Try to scrape full content via browser
        tab_name = f"_research_{len(sources)}"
        try:
            mgr.open_tab(url, tab_name)
            time.sleep(2)
            result, err = mgr.read_tab_clean(tab_name)
            if not err and result.get("text"):
                content = result["text"][:3000]  # Cap per source
            mgr.close_tab(tab_name)
        except Exception:
            try:
                mgr.close_tab(tab_name)
            except Exception:
                pass

        sources.append({
            "title": title,
            "url": url,
            "content": content[:3000],
        })

    # Step 3: Synthesize with Gemini
    source_text = ""
    for i, s in enumerate(sources, 1):
        source_text += f"\n--- Source {i}: {s['title']} ({s['url']}) ---\n{s['content']}\n"

    prompt = (f"Based on the following web sources, provide a comprehensive answer to: \"{query}\"\n"
              f"Cite sources by number [1], [2], etc. Be thorough but concise.\n"
              f"{source_text}")

    response, stats, err = _run_gemini(prompt, None, timeout)
    if err:
        # Return raw sources without synthesis
        return jsonify({
            "query": query,
            "synthesis": f"Gemini synthesis failed: {err}. Raw sources provided below.",
            "sources": [{"title": s["title"], "url": s["url"],
                         "snippet": s["content"][:300]} for s in sources],
        })

    return jsonify({
        "query": query,
        "synthesis": response,
        "sources": [{"title": s["title"], "url": s["url"]} for s in sources],
        "tokens_used": sum(info.get("tokens", {}).get("total", 0)
                          for info in (stats or {}).get("models", {}).values()),
    })


@app.route("/debug/state", methods=["GET"])
def debug_state():
    try:
        info = {
            "tabs": list(mgr.tabs.keys()),
            "has_context": mgr.context is not None,
        }
        try:
            if PINNED_TAB_NAME in mgr.tabs:
                info["_karma_url"] = mgr.tabs[PINNED_TAB_NAME].url
        except Exception as e:
            info["_karma_url"] = f"err: {e}"
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Setup logging
    logging.basicConfig(filename=str(LOG_FILE), level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    # Suppress noisy Playwright greenlet callback errors from keepalive thread
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)
    logging.info("[main] Cockpit starting")
    print("=" * 60)
    print("Karma Cockpit — Agentic Service v2.0.0")
    print("=" * 60)
    print(f"API: http://{HOST}:{PORT}")
    print(f"API token: {API_TOKEN_FILE}")
    print(f"Browser profile: {BROWSER_PROFILE}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print("=" * 60)

    # Cleanup old screenshots
    cleanup_old_screenshots()

    # Register dashboard routes
    try:
        import cockpit_dashboard_addon
        cockpit_dashboard_addon.register_dashboard_routes(app, mgr)
        print("[OK] Dashboard enabled at http://{HOST}:{PORT}/dashboard")
        logging.info("[main] Dashboard routes registered")
    except ImportError as e:
        print(f"[WARN] Dashboard addon not found: {e}")
        logging.warning("[main] Dashboard addon not available")
    except Exception as e:
        print(f"[ERROR] Dashboard registration failed: {e}")
        logging.error("[main] Dashboard registration failed: %s", e)

    # Start browser
    mgr.start()

    # Run Flask (single-threaded: Playwright sync API requires main-thread access)
    try:
        app.run(host=HOST, port=PORT, threaded=False, use_reloader=False)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error("[main] Flask crashed: %s", e)
    finally:
        mgr.stop()


if __name__ == "__main__":
    main()
