# Phase Backlog-4 — Karma Baseline Tools CONTEXT
**Created:** 2026-03-25 | **Session:** 144 | **Authorized:** Sovereign (Julian's discretion, obs #16550)

## What We're Building

3 structured callable tools for Karma via hub-bridge, completing AC2:

| Tool | ID | Route | Backend |
|------|----|-------|---------|
| `read_project_file(path)` | 1-B | hub-bridge → cc_server_p1.py:7891/file | P1 filesystem |
| `write_project_file(path, content)` | 1-B | hub-bridge → cc_server_p1.py:7891/file | P1 filesystem |
| `code_exec(code, language)` | 1-C | hub-bridge → K2 aria /api/exec | K2 sandboxed subprocess |
| `browser_open(url, action?)` | 1-A | hub-bridge → K2 aria /api/exec (playwright) | K2 browser |

## What We're NOT Building

- No new services — reuse cc_server_p1.py (P1) and aria /api/exec (K2)
- No raw shell_run bypass — code_exec is sandboxed with blocklist
- No unrestricted filesystem access — file tools scoped to WORK_DIR only
- No browser automation that persists state between calls (stateless per call)

## Architecture Decisions

**1-B (file read/write):**
- New endpoints on cc_server_p1.py: `GET /file?path=...` and `POST /file`
- Path validation: must be relative, resolved within WORK_DIR, no `..` traversal
- hub-bridge proxies via CC_SERVER_URL (already established pattern)

**1-C (code execution):**
- hub-bridge POSTs to aria /api/exec with wrapped command
- Python: `python3 -c "..."` with timeout 30s, output capped at 8KB
- Bash: raw command but blocklisted patterns rejected in hub-bridge before sending
- Blocklist: rm -rf, sudo, passwd, curl|wget to non-local, ssh, eval, exec
- Output: stdout + stderr + exit_code returned to Karma

**1-A (browser automation):**
- Check if playwright installed on K2 first
- If yes: `python3 -c "from playwright.sync_api import sync_playwright; ..."` via aria exec
- If no: fallback to fetch_url (HTTP-only, no JS rendering)
- Actions: navigate(url), get_text, screenshot path (saved to K2 cache)
- Stateless: new browser instance per call

## Constraints

- cc_server_p1.py changes: restart required on P1 (Start-CCServer.ps1 auto-restart handles it after kill)
- hub-bridge changes: require karma-hub-deploy skill (build + deploy to vault-neo)
- K2 playwright: if not installed, 1-A is stub returning fetch_url fallback
