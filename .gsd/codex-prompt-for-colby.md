# PROMPT FOR CODEX — Colby pastes this

Hey Codex. CC failed to build the Nexus. I need YOU to clean up its mess and actually build it.

## YOUR TASK
Build the Nexus harness — an independent AI application that replaces the Claude Code wrapper. It must have Chat + Cowork + Code in one surface, persistent memory, and self-improvement. It surfaces at hub.arknexus.net (browser) AND the Electron desktop app (electron/main.js).

## READ THESE FIRST (in order)
1. `docs/ForColby/nexus.md` — THE PLAN (v5.3.0). Read ALL of it.
2. `.gsd/codex-cascade-audit.md` — YOUR prior forensic audit with exact insertion points
3. `.gsd/codex-sovereign-directive.md` — 10-step build contract with DONE WHEN criteria
4. `Karma2/cc-scope-index.md` — 115 pitfalls (institutional memory of failures)
5. `docs/anthropic-docs/` — FULL Anthropic documentation (LOCAL, on disk)
6. `docs/claude-mem-docs/` — claude-mem implementation reference (LOCAL, on disk)
7. `docs/wip/preclaw1/preclaw1/src/` — 1,902 files, full Claude Code source (THE BLUEPRINT to replicate)

## CRITICAL CONSTRAINT
**Max subscription = CC CLI only ($0/request). Direct API calls to api.anthropic.com cost REAL MONEY from Console credits. Do NOT replace CC --resume with direct API calls. KEEP CC --resume as the primary inference engine. Enhance it with tool_use parsing and fallback cascade.**

## THE KEY DISCOVERY CC MISSED
The Electron app (electron/main.js) ALREADY HAS 13 IPC handlers — 12 work independently:
- file-read, file-write (with checkpointing), shell-exec, cortex-query, cortex-context, ollama-query, memory-search, memory-save, spine-read, git-status, show-open-dialog, cc-cancel
- Only `cc-chat` (line 45) spawns CC --resume. That ONE handler needs tool_use parsing + fallback cascade added. The Electron app is 90% of an independent harness already.

## FIRST ACTION
Convert 7 PDFs in Karma_PDFs/Inbox/:
```bash
python Scripts/batch_pdf_to_md.py --execute --wip
```
Then run /primitives extraction on each converted file.

## THEN
Reverse-engineer from the Goal backward. Compare nexus.md plan against what actually exists. Your prior audit (.gsd/codex-cascade-audit.md) has exact file paths and insertion points. The sovereign directive (.gsd/codex-sovereign-directive.md) has the 10-step build order with testable DONE WHEN criteria.

## RULES
- BUILD code, don't write documentation
- Test every change, paste output as proof
- No slash commands (44 exist, enough)
- No gap-map cosmetics (close gaps with CODE)
- Prefer local tools and references (everything is on disk)
- If blocked 3x: email Colby at rae.steele76@gmail.com (from paybackh1@gmail.com, creds at .gmail-cc-creds)
