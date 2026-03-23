# PROOF-A: Codex as Automated ArchonPrime Service — Plan
**Created:** 2026-03-22 (Session 123 wrap)
**Author:** CC (Ascendant)
**Context:** See phase-proof-a-CONTEXT.md

Execute one task at a time. Mark `<done>` only after `<verify>` passes.

---

## Task 1: Verify Codex exec non-interactive mode works from KCC context
<verify>`codex exec "What is 2+2?" --sandbox` completes without launching TUI, returns text output to stdout, exits cleanly. Run from C:\Users\karma context.</verify>
<done>true — 2026-03-23 Session 133</done>

**PROOF:** `npx codex exec --sandbox read-only --skip-git-repo-check "What is 2+2? Respond with just the number."` → stdout: `4\n`, rc: 0. Model: gpt-5.4, provider: openai. Runs on K2 (karma user). Flags required: `--sandbox read-only --skip-git-repo-check`.

```bash
# Verified invocation on K2:
npx codex exec --sandbox read-only --skip-git-repo-check "$PROMPT"
```

---

## Task 2: Write KCC Codex trigger script
<verify>Script `Scripts/kcc_codex_trigger.ps1` exists, accepts a `-Prompt` parameter, runs `codex exec --sandbox`, captures output, returns text. Test with a simple prompt.</verify>
<done>false</done>

Script should:
1. Accept `-Prompt` (the analysis request)
2. Run: `codex exec "$Prompt" --sandbox`
3. Capture stdout
4. Return output string

---

## Task 3: Wire KCC bus event detection → Codex trigger
<verify>When a structural bus event arrives (type="request" or content contains "ArchonPrime"), KCC calls `kcc_codex_trigger.ps1` and posts the Codex response to the coordination bus.</verify>
<done>false</done>

Structural event pattern to detect: bus messages with `to="codex"` OR `content` containing "analyze" OR "ArchonPrime".
Post result back: `from=codex, to=all, type=inform, content="[ARCHONPRIME] <codex output>"`.

---

## Task 4: End-to-end gate test
<verify>Colby posts one bus message addressed to `codex` with an analysis request → KCC detects it → triggers Codex → Codex posts ArchonPrime analysis back to bus. Full cycle logged. Colby did NOT manually run anything after the initial bus post.</verify>
<done>false</done>

Test message:
```
from=colby, to=codex, type=request, content="ArchonPrime analysis: review the current CURRENT SPRINT status and flag any risks."
```
Expected bus response within 60s: `from=codex, content="[ARCHONPRIME] ..."`

---

## Summary Gate
PROOF-A COMPLETE when Task 4 verify passes.
Update PLAN.md CURRENT SPRINT to mark PROOF-A ✅ DONE.
Update MEMORY.md Next Session to S-1 (Interface audit design).
