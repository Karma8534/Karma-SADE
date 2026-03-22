# PROOF-A: Codex as Automated ArchonPrime Service — Context
**Created:** 2026-03-22 (Session 123 wrap)
**Author:** CC (Ascendant)

## What We're Doing
Making Codex operate as an automated background service (ArchonPrime) that can be triggered by KCC from coordination bus events — without Colby initiating each analysis.

## Design Decisions (LOCKED)

### Invocation pattern: codex exec --sandbox
Per PLAN.md: `codex exec "prompt" --sandbox` — non-interactive, scriptable from bus automation.
Do NOT use bare `codex "prompt"` (launches interactive TUI).
Do NOT use `--full-auto` without sandbox.

### Trigger source: KCC
KCC detects structural coordination bus events and triggers Codex analysis.
KCC is on P1 (C:\Users\karma, Claude Code v2.1.80). It monitors the bus already.

### Output path: coordination bus post
Codex analysis result gets posted back to bus as an ArchonPrime analysis.
Bus post from KCC after receiving Codex output.

### Gate definition (from PLAN.md)
Codex posts one ArchonPrime analysis to bus from a KCC trigger, without Colby initiating.

## What We're NOT Doing
- Not replacing KCC with Codex (KCC stays, Codex is a tool KCC calls)
- Not building a full Codex-as-daemon service from scratch (use existing codex exec)
- Not requiring Sovereign approval for the KCC→Codex trigger (bus event is pre-authorized)
- Not changing the Channels bridge or CC server

## Prerequisites
- Codex installed on K2 (confirmed session 111)
- PS KCC running on P1 (C:\Users\karma) with GLM primary
- KCC can already read coordination bus

## Acceptance Criterion
`codex exec "analyze this bus event: [X]" --sandbox` runs from KCC script context,
Codex output is posted to coordination bus from KCC, without Colby in the loop.
Proof: one logged KCC-triggered Codex analysis visible in coordination bus.
