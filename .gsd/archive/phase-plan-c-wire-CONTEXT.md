# Phase: Plan-C Wire — Context
**Created:** 2026-03-23 (Session 137 wrap)
**Spec:** `Karma2/PLAN-C-wire.md`

## What We're Building
Wiring the brain (claude-mem on P1:37777) into the full stack:
- vault-neo (hub-bridge) can reach claude-mem via Tailscale
- WebMCP tool descriptors on hub.arknexus.net pages
- /memory endpoint on hub-bridge proxies to claude-mem
- Chrome session clone pattern for browser-native persistence

## Requires
- PLAN-B complete ✅ (Session 137)
- claude-mem running on P1:37777 ✅ (always on)
- P1 Tailscale IP: 100.124.194.102 ✅ (confirmed via B3 testing)

## Design Decisions Locked
1. **C1 approach TBD at execution**: first check if claude-mem supports --host binding. If yes: restart with --host 100.124.194.102. If no: hub-bridge /memory proxies to P1:37777 via Tailscale HTTP.
2. **C3 auth**: same HUB_CHAT_TOKEN Bearer as /v1/chat — no new auth surface.
3. **WebMCP**: Chrome 146 already has #enable-webmcp-testing Enabled (confirmed Session 133).

## What We're NOT Doing
- Not adding a new auth layer for /memory (existing token sufficient)
- Not rebuilding claude-mem (it's a third-party tool, just expose it)
- Not starting C4 (Chrome session clone) until C1+C3 are proven
