# E-1-A: Corpus Builder — Summary
**Completed:** 2026-03-22 (Session 122)
**Author:** CC (Ascendant)

## What Was Built

`Scripts/corpus_builder.py` — A tool that SSHes to vault-neo, streams the vault ledger, and extracts hub+chat conversation turns into Alpaca-format JSONL for fine-tuning.

**Output:** `Logs/corpus_alpaca.jsonl` — 2817 pairs, 5.2MB (gitignored, local only)

## Key Findings

### Ledger Entry Structure (Task 1)
Two formats exist:
- **Legacy** (early sessions): `content.user_message` + `content.assistant_message`
- **Newer** (`kind=chat_turn`): `content.user_message` + `content.assistant_text`

The script handles both transparently.

### Corpus Quality
- Raw hub+chat entries: 3191
- Valid pairs produced: 2817 (88%)
- Skipped: 374 (assistant text < 50 chars or missing fields)

Spot-check confirmed real Karma conversations: memory recall, hierarchy questions, tool usage, session-continuity interactions — exactly the training signal we want.

## What's NOT In the Corpus (by design)
- Short/test responses (< 50 chars)
- Entries missing user or assistant text
- Non-hub+chat tags (session hooks, git commits, ambient)

## Pitfalls Encountered
1. **`--limit` caps pairs, not raw entries** — original implementation capped raw entries, producing fewer than N output pairs. Fixed to early-exit after N valid pairs are found.
2. **Windows UTF-8 encoding** — `open()` without `encoding='utf-8'` fails on Windows with cp1252. Script uses `ensure_ascii=False` + explicit encoding on write.

## Next Steps (E-2-A)
Per PLAN.md: E-2-A will use this corpus for fine-tuning or evaluation. The 2817-pair corpus is ready.
