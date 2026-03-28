# Phase 5-2: Slash Commands — PLAN

## Tasks

### T1: Slash command parser + client-side commands in unified.html
- Add `parseSlashCommand(text)` function before `sendMessage()`
- Intercept `/` prefix in `sendMessage()`, dispatch to handler
- `/clear` → calls `clearConversation()`, shows system msg "Conversation cleared."
- `/model` → shows system msg with model info (cc-sovereign, Max $0)
- `/rename <name>` → updates `document.title` and stores label in localStorage
- `/help` → shows available commands
- `/effort <level>` → stores in localStorage, shows confirmation system msg
- `/compact` → shows system msg with session ID (manual compact — CLI limitation)
<verify>Type `/clear` in input → conversation clears. `/model` → shows model info. `/help` → shows command list.</verify>
<done>All client-side commands respond correctly.</done>

### T2: Effort param threading (unified.html → proxy.js → cc_server_p1.py)
- unified.html: read `effortLevel` from localStorage, include `effort` field in /v1/chat body
- proxy.js: pass `effort` from request body through to harness payload
- cc_server_p1.py: read `effort` from request JSON, add `--effort <level>` to claude CLI args
<verify>Set `/effort high`, send a message. cc_server_p1.py log shows `--effort high` in CLI args.</verify>
<done>Effort level threads end-to-end.</done>

### T3: Visual feedback — effort indicator + command hint
- Show current effort level in route-hint bar (e.g., "effort → HIGH")
- Update route-hint when effort changes
- Input placeholder hints at slash commands
<verify>After `/effort high`, route-hint shows effort level. Input placeholder mentions /help.</verify>
<done>Visual indicators present.</done>

### T4: Deploy to vault-neo + verify
- git commit + push
- scp unified.html to build context on vault-neo
- Rebuild + restart proxy container
- Verify from browser: slash commands work at hub.arknexus.net
<verify>Open hub.arknexus.net, type `/help`, see command list. Type `/effort high`, send message, get response.</verify>
<done>Slash commands live in production.</done>
