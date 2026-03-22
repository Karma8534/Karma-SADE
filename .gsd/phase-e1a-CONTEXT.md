# E-1-A: Corpus Builder — Context
**Created:** 2026-03-22 (Session 121 wrap)
**Author:** CC (Ascendant)

## What We're Building
`Scripts/corpus_builder.py` — runs on P1, extracts instruction/response pairs from the hub/chat ledger JSONL, writes a training corpus in Alpaca JSONL format. No GPU required.

## Why
E-2-A (Unsloth Studio on K2) needs structured training data. The ledger has 6,500+ entries including real Karma conversations. corpus_builder.py is the extraction step that makes those usable for fine-tuning.

## Input
- `Logs/ledger_snapshot.jsonl` OR direct IMAP to vault-neo ledger via SSH
- Ledger entries with `tags` containing `hub` + `chat` have `assistant_text` + paired user message
- Canonical ledger path on vault-neo: `/opt/seed-vault/memory_v1/ledger/memory.jsonl`

## Output Format — Alpaca JSONL
```json
{"instruction": "<user message>", "input": "", "output": "<assistant_text>"}
```
One line per pair. Written to `Logs/corpus_alpaca.jsonl`.

## What We Are NOT Doing
- No GPU processing at this stage
- No fine-tuning in this step (that's E-2-A)
- No deduplication beyond exact-match (keep it simple)
- No vault-neo file modifications

## Design Decisions (Locked)
1. **Pull ledger via SSH** — fetch from vault-neo at runtime, no local copy needed
2. **Alpaca format** — Unsloth Studio reads this natively (verified against Unsloth docs)
3. **Filter criteria** — include only entries with both user turn + assistant_text, skip empty/error responses
4. **Min response length** — 50 chars (filters junk like "OK" or error stubs)
5. **P1 only** — runs locally, no K2 involvement
