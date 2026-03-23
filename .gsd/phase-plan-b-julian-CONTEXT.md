# Phase: Plan-B Julian — Context
**Created:** 2026-03-23 (Session 136)
**Spec:** `Karma2/PLAN-B-julian.md`

---

## Goal
Replace hub.arknexus.net/cc's llama3.1:8b impersonator with real CC (Claude Code CLI) using --resume for session continuity. Make /cc serve actual CC responses, not local Ollama.

## Why This Matters
cc_server_p1.py currently proxies /cc calls to Ollama (llama3.1:8b). This is not Julian. It has no memory, no identity, no actual capability. Plan-B replaces this with real CC CLI subprocess using `--resume` to maintain session context across calls.

## What We're NOT Doing
- NOT using Python Anthropic Agent SDK (PITFALL from Session 133 — wrong path)
- NOT rebuilding cc_server from scratch — surgical 40-line change to the run_cc() function
- NOT adding new auth surfaces — /cc route on hub-bridge uses same Bearer token as /v1/chat
- NOT NSSM service (complex) — Task Scheduler startup task is sufficient for B4

## Architecture (After Plan-B)
```
hub.arknexus.net/cc
  → hub-bridge /cc route (B3)
  → Tailscale → P1:7891 (cc_server_p1.py, B1+B2)
  → claude CLI subprocess with --resume
  → Real CC responses with session continuity
```

## Key Constraints
- cc_server must be single-process (B1 kills zombies)
- --resume requires session .jsonl file exists (~/.cc_server_session_id tracks it)
- claude CLI must be on PATH for cc_server subprocess to find it
- Hub-bridge /cc route timeout: 120s (CC can be slow)
- B4 startup task: Task Scheduler (not NSSM — already familiar pattern from KarmaSessionIndexer)

## Key Files
- `Scripts/cc_server_p1.py` — the impersonator to replace
- `Scripts/Start-CCServer.ps1` — the restart loop to fix (B1)
- `hub-bridge/app/server.js` — add /cc route (B3)
- `~/.cc_server_session_id` — session persistence file (B2)
