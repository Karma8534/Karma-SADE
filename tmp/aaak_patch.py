from pathlib import Path
p=Path('C:/Users/raest/Documents/Karma_SADE/Scripts/cc_server_p1.py')
text=p.read_text()
needle = "    cortex_ctx = _fetch_cortex_context(user_message[:200])\n    if cortex_ctx:\n        parts.append(f\"[CORTEX — K2 working memory summary]\\n{cortex_ctx}\\n\\n\")\n    memories = _fetch_recent_memories(user_message[:200])\n    if memories:\n        parts.append(f\"[RELEVANT MEMORIES — from claude-mem spine]\\n{memories}\\n\\n\")\n\n    # Layer 3: VESPER SPINE — behavioral patterns from self-improvement pipeline (S157)\n"
if needle not in text:
    print('needle not found');
    raise SystemExit(1)
replacement = needle.replace("\n\n    # Layer 3", "\n    wake = _build_wakeup_summary()\n    if wake:\n        parts.append(f'[AAAK WAKEUP]\n{wake}\n\n')\n\n    # Layer 3")
p.write_text(text.replace(needle, replacement))
print('patched')
