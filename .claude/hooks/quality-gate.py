#!/usr/bin/env python3
"""
Quality Gate — PreToolUse hook on Bash (git push)
Runs secret scan before any git push. Exit 2 = block push.
Override: set QUALITY_GATE_BYPASS=1

JSON stdin: {tool_name, tool_input.command, hook_event_name, session_id, cwd}
"""
import json, sys, os, subprocess


# These substrings mark a line as safe (env var references, not actual values)
SAFE_SUBSTRINGS = [
    "process.env.", "os.environ", "hub.chat.token.txt", "# Bearer",
    "token.txt", "Bearer $TOKEN", "Bearer $", "${", "$(cat",
    "example", "YOUR_", "PLACEHOLDER", "<", ">",
]

# Regex patterns to detect hardcoded secrets
SECRET_PATTERN = r"(Bearer [A-Za-z0-9\-_.]{30,}|api_key\s*[:=]\s*['\"][A-Za-z0-9\-_.]{16,}|password\s*[:=]\s*['\"][^'\"]{8,}|ANTHROPIC_API_KEY\s*=\s*sk-)"


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

    cwd = data.get("cwd", os.getcwd())

    result = subprocess.run(
        ["grep", "-rn", "-E", SECRET_PATTERN,
         "--include=*.js", "--include=*.py", "--include=*.json", "--include=*.md",
         "--include=*.sh", "--include=*.env",
         "--exclude-dir=node_modules", "--exclude-dir=.git", "--exclude-dir=.claude",
         "."],
        capture_output=True, text=True, cwd=cwd
    )

    suspicious = [
        line for line in result.stdout.splitlines()
        if not any(safe in line for safe in SAFE_SUBSTRINGS)
    ]

    if suspicious:
        print(f"\n{'='*60}")
        print(f"🚨  QUALITY GATE — PUSH BLOCKED")
        print(f"{'='*60}")
        print(f"  {len(suspicious)} potential hardcoded secret(s) detected:")
        for line in suspicious[:5]:
            print(f"  {line[:120]}")
        if len(suspicious) > 5:
            print(f"  ... and {len(suspicious) - 5} more")
        print(f"")
        print(f"  Fix secrets before pushing.")
        print(f"  Override (false positive only): set QUALITY_GATE_BYPASS=1")
        print(f"{'='*60}")
        sys.exit(2)

    print("[QUALITY GATE] Secret scan clean — push allowed.", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
