# E-1-A: Corpus Builder — Plan
**Created:** 2026-03-22 (Session 121 wrap)
**Author:** CC (Ascendant)
**Context:** See phase-e1a-CONTEXT.md — design decisions locked there.

Execute one task at a time. Mark `<done>` only after `<verify>` passes.

---

## Task 1: Fetch ledger sample and inspect entry structure
<verify>Print 3 ledger entries with `hub` + `chat` tags from vault-neo. Confirm fields: user message field name, assistant_text field, tags array structure.</verify>
<done>true — user_message, assistant_text (new) / assistant_message (legacy), tags array confirmed 2026-03-22</done>

```bash
ssh vault-neo "python3 -c \"
import json
entries = []
with open('/opt/seed-vault/memory_v1/ledger/memory.jsonl') as f:
    for line in f:
        e = json.loads(line)
        tags = e.get('tags', [])
        if 'hub' in tags and 'chat' in tags:
            entries.append(e)
        if len(entries) >= 3:
            break
print(json.dumps(entries, indent=2)[:3000])
\""
```

---

## Task 2: Write corpus_builder.py on P1
<verify>File exists at Scripts/corpus_builder.py with wc -l > 60 AND python3 Scripts/corpus_builder.py --dry-run prints 'Would write N pairs' with N > 0</verify>
<done>true — 146 lines, dry-run: "Would write 168 pairs" 2026-03-22</done>

Module must implement:
- SSH to vault-neo, stream ledger, parse hub+chat entries
- Extract: user turn from `content` or `user_text` (confirm field name in Task 1), assistant turn from `assistant_text`
- Filter: skip if assistant_text < 50 chars or empty
- Write Alpaca JSONL: `{"instruction": user_text, "input": "", "output": assistant_text}`
- Output: `Logs/corpus_alpaca.jsonl`
- `--dry-run` flag: count pairs without writing
- `--limit N`: cap output for testing

Write locally (P019 — never heredoc Python files).

---

## Task 3: Run corpus_builder.py and verify output
<verify>`python3 Scripts/corpus_builder.py --limit 100` writes Logs/corpus_alpaca.jsonl with exactly 100 lines, each valid JSON with instruction/input/output fields.</verify>
<done>true — 100 lines written, structure confirmed (instruction/input/output) 2026-03-22</done>

```bash
py -3 Scripts/corpus_builder.py --limit 100
python3 -c "
import json
with open('Logs/corpus_alpaca.jsonl') as f:
    lines = f.readlines()
print(f'{len(lines)} lines')
for l in lines[:2]:
    d = json.loads(l)
    print('instruction:', d['instruction'][:80])
    print('output:', d['output'][:80])
    print()
"
```

---

## Task 4: Full corpus run + commit
<verify>Logs/corpus_alpaca.jsonl has > 500 lines. Committed to git (gitignored? check — large file). If gitignored, confirm file exists locally.</verify>
<done>true — 2817 lines, 5.2MB. Logs/ gitignored — file confirmed locally. corpus_builder.py committed. 2026-03-22</done>

Run without limit: `py -3 Scripts/corpus_builder.py`
Check line count, spot-check 5 random entries for quality.
Commit corpus_builder.py script (not the .jsonl if large — add to .gitignore if > 10MB).

---

## Summary Gate
E-1-A is COMPLETE when Task 4 verify passes.
Update PLAN.md E-1-A status to `✅ DONE [date]`.
Update MEMORY.md Next Session to E-2-A Step 1.
