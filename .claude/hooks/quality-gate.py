#!/usr/bin/env python3
"""
Quality Gate — PreToolUse hook on Bash (git push)
Runs secret scan before any git push. Exit 2 = block push.
Override: set QUALITY_GATE_BYPASS=1

Windows-safe: uses Python re module (NOT subprocess grep — grep is not
guaranteed in PATH on Windows). Scans all relevant source files.

JSON stdin: {tool_name, tool_input.command, hook_event_name, session_id, cwd}
"""
import json, sys, os, re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# These substrings mark a line as safe (env var references, not actual values)
SAFE_SUBSTRINGS = [
    "process.env.", "os.environ", "hub.chat.token.txt", "# Bearer",
    "token.txt", "Bearer $TOKEN", "Bearer $", "${", "$(cat",
    "example", "YOUR_", "PLACEHOLDER", "<", ">",
    "hub_auth", "hub.capture", "capture.token", "openai.api_key.txt",
    ".txt", "read_text", "readFileSync", "fromFile", "from_file",
    "your-actual", "your-api-key", "your_api_key", "actual-api-key",
    "SETUP_GUIDE", "setup-guide", "setup_guide",
]

# Patterns to detect hardcoded secrets
SECRET_PATTERNS = [
    re.compile(r'Bearer [A-Za-z0-9\-_.]{30,}'),
    re.compile(r'api_key\s*[:=]\s*[\'"][A-Za-z0-9\-_.]{16,}', re.IGNORECASE),
    re.compile(r'password\s*[:=]\s*[\'"][^\'"]{8,}', re.IGNORECASE),
    re.compile(r'ANTHROPIC_API_KEY\s*=\s*sk-'),
    re.compile(r'sk-ant-[A-Za-z0-9\-_]{20,}'),
]

# File extensions to scan
SCAN_EXTENSIONS = {'.js', '.py', '.json', '.md', '.sh', '.env', '.yaml', '.yml', '.ts'}

# Directories to skip
SKIP_DIRS = {'node_modules', '.git', '__pycache__', '.claude', 'Logs', 'Learned',
             'docs', 'PHASE-', 'SESSION-', 'Karma_PDFs'}


def is_safe_line(line: str) -> bool:
    return any(safe in line for safe in SAFE_SUBSTRINGS)


def scan_file(file_path: Path) -> list:
    """Scan a single file for secret patterns. Returns list of (line_num, line) hits."""
    hits = []
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
        for line_num, line in enumerate(content.splitlines(), 1):
            if is_safe_line(line):
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    hits.append((str(file_path), line_num, line.strip()[:120]))
                    break  # One report per line
    except Exception:
        pass
    return hits


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    if tool_name != "Bash":
        sys.exit(0)
    if "git push" not in command:
        sys.exit(0)
    if os.environ.get("QUALITY_GATE_BYPASS") == "1":
        print("[QUALITY GATE] Bypassed via QUALITY_GATE_BYPASS=1", file=sys.stderr)
        sys.exit(0)

    cwd = Path(data.get("cwd", os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())))

    suspicious = []
    scanned = 0

    for file_path in cwd.rglob("*"):
        # Skip directories
        if file_path.is_dir():
            continue
        # Skip unwanted paths
        parts = set(file_path.parts)
        if any(skip in str(file_path) for skip in SKIP_DIRS):
            continue
        # Only scan relevant extensions
        if file_path.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        # Skip large files (> 500KB)
        try:
            if file_path.stat().st_size > 500_000:
                continue
        except Exception:
            continue

        scanned += 1
        hits = scan_file(file_path)
        suspicious.extend(hits)

        if len(suspicious) >= 20:
            break  # Enough evidence

    if suspicious:
        print(f"\n{'='*60}")
        print(f"🚨  QUALITY GATE — PUSH BLOCKED")
        print(f"{'='*60}")
        print(f"  {len(suspicious)} potential hardcoded secret(s) in {scanned} files scanned:")
        for (fp, ln, line) in suspicious[:5]:
            # Show relative path
            try:
                rel = str(Path(fp).relative_to(cwd))
            except Exception:
                rel = fp
            print(f"  {rel}:{ln}: {line}")
        if len(suspicious) > 5:
            print(f"  ... and {len(suspicious) - 5} more")
        print(f"")
        print(f"  Fix secrets before pushing.")
        print(f"  Override (false positive only): set QUALITY_GATE_BYPASS=1")
        print(f"{'='*60}")
        sys.exit(2)

    print(f"[QUALITY GATE] Secret scan clean ({scanned} files) — push allowed.", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
