#!/usr/bin/env python3
"""
Compaction Cliff Guard — UserPromptSubmit hook (Layer 1: Context Engineering)

Injects cc-scope-index.md PITFALL/DECISION rules as context on every user turn.
Solves the "compaction cliff" problem: static CLAUDE.md and cc-scope-index guidance
disappears mid-session when context compacts. This hook re-injects the rules
event-driven, ensuring they are always present regardless of compaction state.

Reference: 3LayerHarness.PDF p.55-56 — "solving the 'compaction cliff' problem
where static AGENTS.md and CLAUDE.md guidance disappears mid-session."

JSON stdin: {hook_event_name, session_id, prompt, cwd}
JSON stdout: {"context": "markdown rules block"}
"""
import json, sys, os
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    cwd = data.get("cwd", os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    scope_file = Path(cwd) / "Karma2" / "cc-scope-index.md"

    if not scope_file.exists():
        # Fallback: check common alternate locations
        scope_file = Path(cwd) / "cc-scope-index.md"
        if not scope_file.exists():
            sys.exit(0)

    try:
        lines = scope_file.read_text(encoding='utf-8', errors='replace').splitlines()
    except Exception:
        sys.exit(0)

    # Extract compact rules: "P0NN [pattern-name]: Rule line only"
    # Skip Why: lines (those are for learning, not runtime enforcement)
    rules = []
    current_id = None
    for line in lines:
        stripped = line.strip()
        # Match pattern headers: "P001 [pattern-name]:" or "D001 [pattern-name]:"
        if (stripped.startswith('P0') or stripped.startswith('D0')) and '[' in stripped and ']:' in stripped:
            try:
                bracket_content = stripped.split('[')[1].split(']')[0]
                current_id = stripped.split('[')[0].strip() + ' [' + bracket_content + ']'
            except Exception:
                current_id = None
        elif stripped.startswith('Rule:') and current_id:
            rule_text = stripped[5:].strip()
            # Truncate long rules to 120 chars
            if len(rule_text) > 120:
                rule_text = rule_text[:117] + '...'
            rules.append(f"• {current_id}: {rule_text}")
            current_id = None  # Reset — wait for next entry
        # Cap at 40 rules to control token usage
        if len(rules) >= 40:
            break

    if not rules:
        sys.exit(0)

    context_block = (
        "=== CC SCOPE RULES ACTIVE (compaction-cliff-guard — always present) ===\n"
        + "\n".join(rules)
        + "\n[Full context: Karma2/cc-scope-index.md | "
        "Violation → append to cc-scope-index.md + save claude-mem observation]"
    )

    # Hard cap at 3500 chars to stay token-efficient
    if len(context_block) > 3500:
        context_block = context_block[:3497] + '...'

    print(json.dumps({"context": context_block}))
    sys.exit(0)


if __name__ == "__main__":
    main()
