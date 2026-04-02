# Phase A Context — Fix Karma (Resurrection Plan v2.1)

## What We're Doing
Fix the 4 browser-visible bugs that prevent Karma from being usable at hub.arknexus.net.

## Source
Resurrection Plan v2.1 (Memory/03-resurrection-plan-v2.1.md), Phase A.

## Architecture
```
Browser → proxy.js (vault-neo:18090, ~600 lines) → cc_server_p1.py (P1:7891) → cc --resume ($0)
```

## Constraints
- TSS: every fix must be browser-verified, not curl-verified
- nexus.md is APPEND ONLY — no edits
- proxy.js is the thin door; CC does all prompt assembly and tool execution
- Rule 5: Browser verification. Never curl.

## What We're NOT Doing
- Sprint 7 features (voice, camera, subagent panel)
- Rate limit contingency (Phase A item 5 from MEMORY.md — separate task after A1-A4)
- Any changes to CC wrapper or claude-mem

## Design Decisions
- Investigate each bug via browser DevTools (Chrome CDP MCP or Claude-in-Chrome)
- Fix in proxy.js or unified.html as needed
- Deploy via git push → vault-neo git pull → scp to build context → docker rebuild
