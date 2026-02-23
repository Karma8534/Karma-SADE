# Unified Dashboard Redesign — 2026-02-23

## Problem
Current unified.html has three columns (Chat | Metrics | System Monitor) where the center column breaks the layout and contains stale SADE-era content (Gemini 3 Flash, Port 9401, SQLite + ChromaDB, FREE queries). The layout overflows horizontally and text is cut off.

## Approved Design (Option B — Clean Rebuild)

### Layout
Two columns only:
- **Chat panel** (left, ~70% width) — full height, chat history + input
- **Sidebar** (right, ~30% width) — combined System Health + Monitor

### Top bar
- Left: "Karma" title
- Right inline: `● All Systems Operational` | current model badge | `$X.XX / $35` spend | clock

### Chat panel
- Chat history (scrollable, full remaining height)
- File list (above input, shows selected files)
- Textarea input — Enter to send, Shift+Enter for newline
- Row below input: connection dot + status text (left) | 📎 file button + Send button (right)
- No welcome message referencing Gemini or SADE

### Sidebar (right)
Sections stacked vertically:
1. **Model** — active model name, updates from `response.model` on each reply
2. **Spend** — `$X.XX used / $35.00 cap` — updates from `response.spend` on each reply
3. **This request** — last request cost in USD — updates from `response.usd_estimate`
4. **Services** — static list: hub-bridge ✓, karma-server ✓, falkordb ✓, vault-api ✓
   (all shown as green since if chat works, stack is up)

### Data flow
- Sidebar values initialise as `—` on load
- After first successful chat response, `handleMessage()` extracts `model`, `usd_estimate`, `spend.usd_spent`, `spend.cap_usd` and updates sidebar live
- No polling, no new endpoints

### Aesthetic
- Keep existing dark theme (--bg-primary, --accent-purple, --status-healthy variables)
- Tighter, cleaner — no oversized metric cards
- Sidebar uses small label + value rows, not hero numbers

### Out of scope
- No new hub-bridge endpoints
- No Figma
- No WebSocket
- Token flow unchanged (localStorage prompt on first send)

## Implementation Notes
- Full rewrite of unified.html (not a patch)
- All JS logic preserved: handleMessage, sendMessage, file handling, token auth
- SCP to vault-neo → docker compose rebuild → verify live
