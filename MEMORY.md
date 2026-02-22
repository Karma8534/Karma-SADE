# Universal AI Memory — Current State

## Active Phase
Karma Core — OPERATIONAL. Multi-model routing + consciousness loop + graph distillation. 4 LLM providers active (MiniMax + GLM-5 + Groq + OpenAI).

## Phase Status
| Phase | Status | Summary |
|-------|--------|---------|
| 1 | ✅ Complete | Capture MVP — extension, hub, vault, JSONL ledger |
| 2 | ✅ Complete | Embeddings & semantic search via ChromaDB (verified operational) |
| 3 | ✅ Complete | Auto-reindexing on new entries |
| 4 | ✅ Complete | Context injection — manual (popup) + autonomous (auto-inject with preview UI) |
| Karma | ✅ Operational | Brain stack + terminal chat + real-time learning + desktop shortcut |
| Consciousness | ✅ Active | 60s OBSERVE/THINK/DECIDE/ACT/REFLECT loop — ambient awareness |
| Multi-Model | ✅ Active | MiniMax M2.5 (primary — coding/speed/general), GLM-5 (reasoning/analysis specialist, priority -1), Groq (fallback), OpenAI (final fallback). |
| Graph Distillation | ✅ Active | _distillation_cycle() in ConsciousnessLoop — reads FalkorDB every 24h, synthesizes themes/gaps/insights via LLM, writes schema-compliant fact to ledger, re-ingests key insights as FalkorDB episodes |

## Current Task
CC Resurrection LIVE (2026-02-21):
- Get-KarmaContext.ps1: fetches Karma's live canonical graph context at every CC session start
- Primary path: SSH to vault-neo → curl /raw-context?q=session_start&lane=canonical (3s timeout)
- K2 fallback: PowerShell RESP TCP client to 192.168.0.226:6379 (no redis-cli, no Docker)
  - Must use GRAPH.RO_QUERY (not GRAPH.QUERY) on replica — write commands are rejected
- Atomic write: .WriteAllText() to .tmp then Move-Item -Force to karma-context.md
- karma-context.md gitignored; CC reads it immediately after script runs
- CLAUDE.md ## Session Start: step 1 now runs resurrection script (4 steps → 5 steps)
- Scripts/resurrection/Get-KarmaContext.ps1 committed + smoke tested ✅
- Primary path smoke test: "Context written from vault-neo (1468 chars)" ✅
- K2 fallback smoke test: correctly reports 0 entities (graph currently empty — see Blockers) ✅
- Commits: 305701e (gitignore) + c3dd390 (script) + ae8d57d (RO_QUERY fix) + 51079c0 (CLAUDE.md)
- NOTE: FalkorDB neo_workspace graph is currently EMPTY on both vault-neo and K2.
  Container was recreated without persistent volume during K2 replication setup.
  Data is in JSONL ledger + PostgreSQL. Rebuild: run batch_ingest.py on vault-neo.
  Until rebuilt, resurrection context = PostgreSQL preferences only (no entity/episode data).

K2 FalkorDB Replica LIVE (2026-02-21):
- K2 (192.168.0.226) is now a live read-only FalkorDB replica of vault-neo (64.225.13.144)
- SSH tunnel: `-L 0.0.0.0:17687:localhost:6379` via neo@64.225.13.144:22 (key: C:\Users\karma\.ssh\id_ed25519)
- FalkorDB on K2 issues: `REPLICAOF host.docker.internal 17687` on tunnel connect
- Task Scheduler task: `FalkorDB-Vault-Tunnel` (AtLogOn, RunLevel=Highest, restart 5x/1min)
- Scripts: `Scripts/k2-falkordb-sync/FalkorDB-Tunnel.ps1` + `Setup-FalkorDB-Replica.ps1` (committed)
- E2E verified: master_link_status:up, connected_slaves:1, test key replicated, READONLY write-block confirmed
- NOTE: Re-run Setup-FalkorDB-Replica.ps1 on K2 after any script update to re-register the Task Scheduler task
- Lesson learned: FalkorDB port 6379=Redis replication, 7687=Bolt UI. REPLICAOF must use 6379. Docker containers can't reach host 127.0.0.1 — use host.docker.internal. PowerShell 5.1 reads UTF-8-without-BOM as ANSI: em dash (U+2014) = string terminator. Use Start-Process not Start-Job to keep SSH alive.

v2.11.0 COMPLETE — Karma can now surf the web (full page content, not snippets) (2026-02-21):
- v2.8.0: Within-session memory (session store, MAX_SESSION_TURNS=8, 30min TTL). buildSystemText governance fix. "One good question" instruction. Distillation brief now actually deployed (was committed but never built).
- v2.9.0: Anthropic SDK added to hub-bridge. callLLM() unified helper routes "claude-*" models to Anthropic API, everything else to OpenAI. MODEL_DEFAULT=claude-sonnet-4-6 (best model on account). MODEL_DEEP=gpt-5-mini. Smoke test: provider=anthropic, model=claude-sonnet-4-6, ok=true ✅
- v2.10.0: Brave Search API integrated. SEARCH_INTENT_REGEX detects search-intent queries. fetchWebSearch() calls Brave API, returns top 3 results. Self-knowledge prefix injected into every system prompt (backbone model, session memory params, web search status). debug_search telemetry field added.
- v2.11.0: fetchPageText() added — plain HTTP fetch of top Brave result URL, strips <script>/<style>/all HTML tags, decodes entities, returns up to 4000 chars of real page content. Falls back to Brave snippets if fetch fails. Smoke test: debug_search=hit, Karma cited $100B OpenAI deal + $110B India Reliance investment from actual article. ✅
- Key file: /opt/seed-vault/memory_v1/session/brave.api_key.txt (mounted read-only in container)
- Available Claude models on account: claude-sonnet-4-6, claude-opus-4-6, claude-opus-4-5, claude-haiku-4-5, claude-sonnet-4-5, claude-opus-4, claude-sonnet-4

PROMOTE complete — ckpt_20260221T124058_KUQaf_ (trust: baseline_exec_verified, 2026-02-21T12:41Z).
karma_brief covers: identity-resurrection via Vault ledger + Resurrection Packs, three-lane memory model, Karma Window UI. Open question logged: "What triggers promotion from candidate to canonical — who decides, under what criteria?"

Memory Integrity Gate DEPLOYED (2026-02-21):
- ASSIMILATE → lane=candidate (conf 0.85) in FalkorDB + candidates.jsonl
- DEFER → lane=raw (conf 0.50) — stored, not surfaced in context
- Contradiction check on candidate writes: same-entity conflict → lane=conflict, flagged in PROMOTE panel
- PROMOTE now promotes candidates → canonical in FalkorDB (real promotion, not just checkpoint write)
- Context (fetchKarmaContext) filters to canonical only (?lane=canonical on /raw-context)
- Karma Window: PROMOTE button shows pending count "PROMOTE (N ⚠)" with conflict warning
- candidates.jsonl: /opt/seed-vault/memory_v1/ledger/candidates.jsonl

Next: PROMOTE to write karma_brief covering Memory Integrity Gate. Then: design promotion criteria (see Karma's observation below).

## Epistemic Gate DEPLOYED (2026-02-21) — v2.13.0
Karma's design, built as specified:

1. **Colby is the final authority** — `/promote-candidates` requires `approved_uuids` list. No UUID in the list = not promoted. No auto-promotion.
2. **Audit log on every promotion** — `promoted_by`, `promoted_at`, `promotion_reason` written to FalkorDB + candidates.jsonl. Vault audit record written on every `Approve Selected` action.
3. **Conflicts unchecked by default** — Karma Window shows checkboxes; conflicts start unchecked requiring explicit Colby approval.

> "If I can self-promote memories into canonical, the integrity of the whole system depends on my judgment in the moment. That's too fragile. You should be the gate on the gate."

**What's built:**
- PROMOTE button → vault checkpoint only (no auto-promotion)
- Candidates panel → checkboxes per candidate, conflicts unchecked by default
- "Approve Selected" → `/v1/candidates/promote` → FalkorDB + vault audit log
- Smoke tested: ASSIMILATE → candidate → Approve Selected → promoted_count=1 ✅

**Next open question:** Promotion criteria — what concrete signals make a candidate canonical-worthy? (Karma's first requirement: "explicit criteria, not vibes")

## Blockers
- **FalkorDB batch4 RUNNING** — Started 2026-02-22 ~23:24 UTC. 990 episodes, TIMEOUT=10000 set, ok:60 err:0 at 6% checkpoint. ETA ~3h from start. TIMEOUT=0 was causing 72% failure in batch3 (queries timeout). Fixed by recreating container with TIMEOUT=10000.
  - **Post-completion**: BGSAVE → verify dump.rdb → check K2 replication (already verified live: connected_slaves:1, lag:0)
- **KarmaInboxWatcher restart needed** — New Gated/ watcher script deployed (60f796f) but old PowerShell instance still running. Colby must: `Stop-Process -Name pwsh -Force` (or `Get-Process pwsh | Stop-Process`) then `Start-ScheduledTask -TaskName "KarmaInboxWatcher"`.
- Twilio A2P campaign under review — SMS delivery blocked until approved.
- Occasional stored=false on ASSIMILATE signal (write-primitive timeout edge case). Low priority — most writes succeed.
- ~~Within-session context drift~~ FIXED v2.8.0
- ~~(empty_assistant_text) on complex prompts~~ FIXED v2.7.1

## Next Milestone — Memory Integrity Gate
✅ DEPLOYED v2.12.0 (2026-02-21). Gate enforces: ASSIMILATE→candidate, DEFER→raw, PROMOTE→canonical. Context filtered to canonical only. Contradiction detection flags conflicts. PROMOTE button shows live pending count.
Observe in practice: chat → ASSIMILATE signal → check candidates.jsonl → PROMOTE → verify canonical in FalkorDB.

## Backlog
- **Karma Window Review Queue card** (in-progress): `/v1/review-queue` endpoint is live. Missing: UI card in index.html that surfaces pending items from review_queue.jsonl with click-to-load-in-chat.
- **Priority flag on ingest** (Karma design, 2026-02-22): ✅ BUILT — Gated/ directory is the flag. Drop file in `OneDrive\Karma\Gated\` → watcher sends `priority:true` → appended to `review_queue.jsonl`. Watcher restart still needed (see Blockers).
- **Synthesis gap on existing processed files**: 47 files in Done/ have entity extraction only (no Karma synthesis). Karma's decision: Option 1 acceptable for most (weak-signal files). Option 2 (conversational pass) worth doing selectively for files where the spidey-sense was strongest. Next CC session: Colby flags those specific files for re-paste to Karma.
- Thumbs up/down on Karma chat window — Karma proposed, logged as future build item. Not designed yet.
- Extension deprecation — code still in repo and Chrome. Decision made: scrap it. Cleanup not yet executed.
- Headless browser (Playwright/Puppeteer) — deferred. fetchPageText() covers ~80% of needs without Chromium overhead. Revisit if vault-neo is upgraded beyond 4GB RAM.
- Brave Search pricing: $5 free monthly credit (~1000 queries). Paid: $5/1000 queries after that. Low usage expected (intent-gated — only triggers on explicit search keywords).

## Hub-Bridge History
- v2.1.1: capture auth split, batch chatlog, rate limits, auto-handoff
- v2.2.0: STATE_PRELUDE_V0_1, prelude trimming, token budget, telemetry
- v2.3.0: KARMA_BRIEF in PROMOTE (plain-language session summary for Karma)
- v2.4.0: FalkorDB context via karma-server /raw-context injected into /v1/chat. Luna→Ollie fixed. PROMOTE: ckpt_20260221T064445_vw28bT
- v2.4.1: Token budget raised (DEFAULT 1200→2000, CAP 1600→3000), KARMA_CTX_MAX_CHARS 1800→1200. Fixes (empty_assistant_text) on gpt-5-mini. Karma Window: Enter-to-send, no Send button.
- v2.7.1: Model routing corrected. MODEL_DEFAULT→gpt-4o-mini (fast, cheap, no CoT overhead). MODEL_DEEP→gpt-5-mini (reasoning model, on-demand). Token budget raised to 16000/32000 for reasoning model. Pricing vars updated to match.
- v2.4.2: Token budget further raised (DEFAULT 2000→3000, CAP 3000→5000). System prompt autonomy ("Karma owns her own development"). Neo alias purge across FalkorDB + PostgreSQL.
- v2.5.0: Karma ingest pipeline. ASSIMILATE/DEFER/DISCARD signal detection in /v1/chat. /v1/ingest endpoint (base64 PDF, chunked). buildSystemText() refactor. pdf-parse CJS shim. writeKarmaPrimitive() → karma-server /write-primitive → direct FalkorDB write. PowerShell FileSystemWatcher for OneDrive/Karma/Inbox. Knowledge evaluation instructions in system prompt. Smoke tested: stored=true, uuid=afe90411 in neo_workspace.
- v2.5.1: /v1/ingest handles .txt and .md as plain text (was PDF-only). Enables folder watcher text file ingestion.
- v2.6.0: Autonomous continuity — karma_brief auto-injected into every /v1/chat system prompt from vault ledger. No paste from Colby required.
- v2.7.0: distillation_brief injected into buildSystemText() as --- KARMA GRAPH SYNTHESIS --- block. Karma arrives knowing her own graph structure.
- v2.8.0: Within-session memory (session store, 8 exchange pairs, 30min TTL). buildSystemText governance fix + one-good-question instruction. Distillation brief actually deployed (was code-only before).
- v2.9.0: Anthropic SDK in hub-bridge. callLLM() routes claude-* → Anthropic, else → OpenAI. MODEL_DEFAULT=claude-sonnet-4-6. MODEL_DEEP=gpt-5-mini. compose.hub.yml updated with Anthropic key mount.
- v2.10.0: Brave Search API. SEARCH_INTENT_REGEX for intent detection. fetchWebSearch() calls Brave API (top 3 results). Self-knowledge prefix in buildSystemText() (backbone, session_memory, web_search params). debug_search telemetry. Brave key mounted at /run/secrets/brave.api_key.txt.
- v2.11.0: fetchPageText() — plain HTTP fetch of top result URL, full HTML strip (<script>/<style>/tags/entities), 4000 char limit. Real article content (not snippets) injected into Karma's context. Snippet fallback if fetch fails. Smoke test: Karma cited real figures from live article ✅
- v2.12.0: Memory Integrity Gate. lane+confidence on all FalkorDB episode writes. ASSIMILATE→candidate, DEFER→raw. Contradiction detection at write time. /promote-candidates endpoint. PROMOTE now has real semantics. Context filtered to canonical only. PROMOTE button shows pending count + conflict warnings.
- v2.13.0: Epistemic Gate. /promote-candidates now requires approved_uuids list — no auto-promotion. Audit fields (promoted_by, promoted_at, promotion_reason) written to FalkorDB + candidates.jsonl + vault. PROMOTE = vault checkpoint only. New /v1/candidates/promote endpoint with Colby authorization. Karma Window: checkbox review panel, conflicts unchecked by default, "Approve Selected" triggers gate. Fixed CANDIDATES_JSONL path to /ledger container mount.
- v2.14.0: Image/screenshot ingest. /v1/ingest now handles jpg/jpeg/png/gif/webp via Anthropic vision (claude-sonnet-4-6). Watcher: default TokenFile fixed to .hub-chat-token (HUB_CHAT_TOKEN), image extensions added. .hub-chat-token copied locally. KarmaInboxWatcher registered as scheduled task (runs at login, auto-restarts). Smoke tested: HowIseeKarma.jpg ASSIMILATE'd stored=true, landed in candidates. Drop any screenshot or image in Karma/Inbox — Karma sees it and evaluates it.
- v2.15.0: Real-time vision in /v1/chat + Karma Window image attach UI. /v1/chat accepts optional image_b64 + media_type; builds Anthropic multimodal content block for claude-* models. Body parse raised to 10MB. debug_image_attached telemetry. Karma Window: 📷 attach button, file picker, paste-from-clipboard on textarea, thumbnail preview strip with remove button. addMsg() renders thumbnail in chat log. Smoke tested: 8x8 green PNG → claude-sonnet-4-6 replied "Green." ✅ Paste any screenshot directly into Karma Window and ask about it.
- v2.15.1: karma_brief now includes session history turns. Fix: brief generator was using only RP header (checkpoint metadata — IDs, hashes, pack count), producing stale summaries unrelated to session work. Now includes last 6 session turns from hub-bridge session store + Colby's next_action note. karma_brief will reflect actual work done this session.
- v2.16.0: Recent Approvals block closes retrieval-drift window. New query_recent_ingest_episodes() returns last 5 canonical [karma-ingest] episodes by created_at DESC regardless of query match. Injected into every /raw-context response as "Recently Learned (Approved)" section. Deduplicated against Recent Memories. Karma now arrives in the session after promotion already aware of approved content without needing a matching query to activate it.
- v2.17.0: Karma↔CC Collaboration Bridge. Append-only JSONL queue at /opt/seed-vault/memory_v1/hub_bridge/data/handoffs/collab.jsonl. hub-bridge: POST/GET/PATCH /v1/collab routes; readCollab() last-write-wins dedup; appendCollab() helper. karma-server: query_pending_cc_proposals() reads collab.jsonl; "## CC Has a Proposal" block injected into every /raw-context response when pending CC→Karma messages exist. Karma Window: "Collaboration Queue" card (hidden by default, shows when pending messages exist) with Approve/Reject per message; refreshCollab() auto-called from refreshState(). CC session-start check: read collab.jsonl for pending Karma→CC proposals.
- v2.17.1 (2026-02-22): Karma Window multi-file upload + any format. File input now accepts PDF/txt/md/csv + images, `multiple` attribute. Images → vision staging. Documents → `/v1/ingest` immediately with chunk-by-chunk ASSIMILATE/DEFER/DISCARD log display. `/v1/ingest` routes to `/v1/ingest` (not chat). Commits: 054dbfe.
- v2.17.2 (2026-02-22): Gated/ priority ingest. karma-inbox-watcher.ps1 adds `GatedPath` param + second FileSystemWatcher. Files in Gated/ → `priority:true` in POST to /v1/ingest → appended to review_queue.jsonl. /v1/ingest gains `priority` field extraction + `appendReviewQueue()` helper. Commit: 60f796f.
- v2.17.3 (2026-02-22): Graph access primitives. Hub-bridge: GET/PATCH `/v1/review-queue`, POST `/v1/cypher` (read-only FalkorDB proxy, write-keyword blocklist, 8s timeout, auth-gated). karma-server: POST `/graph-query` (write-keyword blocklist, `GRAPH.RO_QUERY`). Smoke tests: 219 entities, empty queue. Commit: a531daa.
- v2.17.4 (2026-02-22): 429 rate-limit retry in callLLM. Anthropic rate_limit_error (429) retried up to 3x with exponential backoff (1.5s, 3s, 6s) or honor retry-after header. Retry verified via inject test. Commit: a9dcf48.
- v2.17.5 (2026-02-22): Karma self-access file bridge. GET `/v1/vault-file/:alias` — reads MEMORY.md, CLAUDE.md, consciousness, collab, candidates, system-prompt, session-handoff, session-summary, core-architecture. Optional `?tail=N`. PATCH `/v1/vault-file/MEMORY.md` — append or overwrite (confirm required). compose.hub.yml: 3 new volume mounts (/karma/repo, /karma/ledger, /karma/MEMORY.md). Smoke tested: MEMORY.md read (29KB ok), CLAUDE.md read, consciousness tail, append. Commit: 1c42dcf.

## Karma Core Status (2026-02-21)
- **State**: OPERATIONAL + CONSCIOUS + MULTI-MODEL + DISTILLING — 4 LLM providers, task-based routing, 24h self-analysis
- **Stats**: 497 entities, 620+ episodes, 4256+ relationships in FalkorDB (neo_workspace graph)
- **Batch ingest**: 359/366 episodes processed (7 errors — RediSearch syntax + timeouts). Script: karma-core/batch_ingest.py
- **FalkorDB tuning**: TIMEOUT raised from 1s→5s (graph grew 3x, queries need more time). MAX_QUEUED=25.
- **Test passed**: Tell Karma "My name is Colby" → quit → new session → "What is my real name?" → "Colby"
- **Test passed**: "Adopted a cat named Luna" → quit → new session → "Do I have pets?" → "Luna"
- **Desktop shortcut**: `C:\Users\raest\Desktop\Talk to Karma.lnk` — one-click terminal chat
- **Real-time learning**: Every chat turn → background Graphiti ingest → entities/relationships updated in ~5-8s
- **Identity system**: Structured real_name/alias extraction from FalkorDB. Context outputs `REAL NAME: Colby` with explicit instruction to use it for greetings. Aliases labeled as secondary. Personal facts filtered to Colby entity only (pets, family, life events).
- **Query filter**: Read-only questions (/ask with "what/who/how...") skip graph ingestion to prevent self-reinforcing loops
- **Graph distillation**: 24h cycle reads FalkorDB, synthesizes via GLM-5, writes karma_distillation fact to vault ledger. Exposed via /v1/checkpoint/latest as distillation_brief. Injected into system prompt as --- KARMA GRAPH SYNTHESIS ---. First run: distillation_1771669572 ✅
- **Persona baseline**: karma_persona_baseline_1771670265 in vault ledger (tags: karma_persona, baseline, identity). CC→Karma briefed directly via hub chat API.
- **Consciousness loop**: 60s background cycle — OBSERVE/THINK/DECIDE/ACT/REFLECT
  - Idle cycles: 0 LLM calls, ~2ms, $0 cost
  - Active cycles: gpt-4o-mini analysis, ~443ms, logs insights to consciousness.jsonl
  - Insights surface naturally in next chat via context injection
  - **Journal → Graph ingestion**: Active reflections auto-ingest into FalkorDB as episodes (source: karma-consciousness)
  - **SMS alerts**: High-confidence insights (>0.8) trigger SMS to Colby via Twilio. Throttle: 3/hr, 10/day.
  - Commands: /consciousness shows loop metrics
  - Config: CONSCIOUSNESS_ENABLED, CONSCIOUSNESS_INTERVAL, CONSCIOUSNESS_JOURNAL
  - Design doc: karma-core/CONSCIOUSNESS-DESIGN.md
- **Multi-model router**: 4 models, task-based routing with intelligent fallback
  - MiniMax M2.5 (priority 0): PRIMARY for coding, speed, general (80.2% SWE-Bench)
  - GLM-5 (priority -1): REASONING + ANALYSIS specialist (BigModel/Z.ai, deep thinking). Funded 2026-02-17. Tested: 57s response time, excellent quality.
  - Groq (llama-3.3-70b-versatile, priority 5): fallback for speed/general
  - OpenAI gpt-4o-mini (priority 10): final fallback + consciousness analysis
  - `<think>` CoT tags auto-stripped from MiniMax responses
  - Classification: keyword-based (zero LLM cost), deterministic
  - Fallback chain: tries all providers for task type, then any enabled provider
  - Routing: reasoning → GLM-5 → MiniMax → Groq → OpenAI
  - Commands: /models shows providers + usage stats
  - Ledger logs which model handled each message
  - File: karma-core/router.py
- **Ollama integration explored**: `ollama pull minimax-m2.5:cloud` works locally (✅). Exposes OpenAI-compatible API at http://localhost:11434/v1/chat/completions. Server installation blocked by sudo requirement on vault-neo. Current decision: Continue with direct MiniMax API (proven, no additional setup needed). Revisit if credit-saving strategy for cloud models is verified.
- **SMS proactive triggers**: Fully implemented and tested (2026-02-17). Consciousness loop → high-confidence insight detected → SMSManager.notify() → Twilio API. Trigger flow: `consciousness.py` line 386-399 calls `sms_notify()` for ALERT/INSIGHT/GROWTH actions with confidence-based categorization. Server logs show "SMS: ACTIVE (→ 5322)". Awaiting Twilio A2P campaign approval to allow outbound SMS delivery.
- **OpenAI-compatible proxy** (`/v1/chat/completions`): Added 2026-02-17 for Claude Code integration.
  - Endpoint: `POST http://localhost:8340/v1/chat/completions`
  - Accepts OpenAI-compatible JSON format (messages, max_tokens, temperature)
  - Forces `task_type="coding"` → GLM-5 routing via priority system
  - Logs requests to ledger with `source="openai-proxy"` for analytics
  - Returns OpenAI-compatible JSON response format
  - Documentation: CLAUDE_CODE_SETUP.md (configure local Claude Code CLI)
  - Cost optimization: Redirects Claude Code from Haiku API ($0.80/1M input) to $30/mo GLM-5 unlimited
- **karma-server restart command** (verified from docker inspect):
  `docker run -d --name karma-server --network anr-vault-net --restart unless-stopped -p 8340:8340 --env-file /tmp/karma-server.env -v /opt/seed-vault/memory_v1/ledger:/ledger:rw karma-core:latest python -u server.py`

## Karma Brain Stack
- **FalkorDB**: Running on vault-neo (Docker, port 3000/7687), temporal knowledge graph
- **Graphiti**: graphiti-core[falkordb] — entity/relationship extraction, real-time episode ingestion
- **PostgreSQL**: analysis schema with 94 records (facts + preferences)
- **Chat Server**: FastAPI + WebSocket on port 8340 (karma-server container)
  - GET /health, GET /status, GET /ask?q=..., WebSocket /chat, POST /sms/webhook, POST /v1/chat/completions
  - **Remote access**: https://karma.arknexus.net (Caddy auto-TLS, bearer token auth)
  - Bearer token: KARMA_BEARER env var in /opt/seed-vault/memory_v1/compose/.env
  - Public endpoints: /health, /privacy, /terms, /sms/webhook
  - Commands: /status, /goals, /graph, /reflect, /consciousness, /models, /know, /rel
  - Logs conversations to JSONL ledger
  - Queries FalkorDB for context, PostgreSQL for preferences
  - Multi-model routing: MiniMax M2.5 (primary), Groq (fallback), OpenAI (final fallback)
  - Real-time Graphiti ingestion after every chat turn (non-blocking background task)
- **SMS**: Twilio-powered via karma-core/sms.py — **OPERATIONAL**
  - Outbound: breakthrough insights, problem prevention, cross-platform synthesis, timing-sensitive, self-improvement
  - Triggers: Consciousness loop detects high-value insights (confidence ≥ 0.8) and queues SMS via `sms_notify()`
  - Throttle: 3/hr, 10/day, confidence >= 0.8 (enforced in SMSManager)
  - Two-way: Colby texts back → Karma generates response → TwiML reply
  - Webhook: POST /sms/webhook (configure in Twilio console → https://karma.arknexus.net/sms/webhook)
  - FROM: +14848061591 → TO: +14845165322
  - Status: Twilio client initialized ✅, credentials configured ✅, A2P campaign approval ⏳ (pending)
- **CLI Client**: karma-core/cli.py (karma chat, karma status, karma ask)
- **Desktop Shortcut**: karma-chat.ps1 → SSH → docker exec → cli.py chat
- **Files**: karma-core/Dockerfile, requirements.txt, config.py, bootstrap.py, server.py, consciousness.py, router.py, sms.py, cli.py, karma-chat.ps1, create-shortcut.ps1, karma-icon.ico
- **Architecture doc**: KARMA-ARCHITECTURE.md

## Phase 4 Completion Notes (Autonomous Context Injection)
- **Step 1**: Auto-inject toggle in popup (chrome.storage.sync, real-time listener)
- **Step 2**: New conversation detector (Claude: data-test-render-count, ChatGPT: data-message-author-role, Gemini: model-response/user-query)
- **Step 3**: Input monitor with 1.5s debounce, 10-char minimum, first-50-words query extraction
- **Step 4**: Inline preview UI — dark-themed fixed-position floating div above input, shows result count + content preview + Tab/Esc hints
- **Step 5**: Keyboard handlers — Tab injects context + marks conversation injected, Esc dismisses preview
- **Bug fix**: Changed from position:absolute (clipped by overflow:auto parent) to position:fixed with calculated coordinates + body append
- sessionStorage prevents re-injection within same conversation
- All 3 platforms tested and verified via ChromeMCP

## Phase 3 Completion Notes (Manual Injection)
- Search API exposed at https://hub.arknexus.net/v1/search with CORS for claude.ai, chatgpt.com, gemini.google.com
- content-context.js: popup-triggered search → preview modal → DOM injection
- Platform-specific injection: Claude (contenteditable), ChatGPT (ProseMirror div), Gemini (Quill ql-editor)
- Fixed field name mismatches (similarity_score, content_preview, platform)

## Infrastructure
- Server: arknexus.net (vault-neo), 7 Docker containers running
- Containers: karma-server, falkordb, anr-vault-search, anr-vault-api, anr-hub-bridge, anr-vault-db, anr-vault-caddy
- FalkorDB: ~150-300MB RAM, Redis protocol on 6379 internal / 7687 external (Bolt). 6379 also exposed to 127.0.0.1 for K2 replication tunnel.
- **FalkorDB persistence + TIMEOUT — CRITICAL (verified 2026-02-22)**:
  - **Data loss root cause**: volume mounted at `/data` but FalkorDB writes to `/var/lib/falkordb/data` by default. RDB never lands on host. Every container restart = empty graph. Fix: `-e FALKORDB_DATA_PATH=/data`
  - **TIMEOUT root cause**: Default 1000ms wipes on recreation. Grows past ~250 episodes → Graphiti dedup queries exceed 1s → cascade failure. Pass via `-e FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 25'` (NOT `--GRAPH.TIMEOUT` flag — that's ignored by run.sh)
  - **Correct permanent container run command**:
    ```
    docker run -d --name falkordb --network anr-vault-net --restart unless-stopped \
      -p 6379:6379 -p 3000:3000 -v /home/neo/karma/falkordb-data:/data \
      -e FALKORDB_DATA_PATH=/data \
      -e FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 25' \
      falkordb/falkordb
    ```
  - After rebuild, force save: `docker exec falkordb redis-cli -p 6379 BGSAVE`
  - Verify: `ls -lah /home/neo/karma/falkordb-data/dump.rdb`
- **K2 FalkorDB replica**: K2 (192.168.0.226) runs FalkorDB in REPLICAOF mode off vault-neo via SSH tunnel (port 17687). Managed by Windows Task Scheduler task `FalkorDB-Vault-Tunnel`. Read-only. Tunnel scripts in Scripts/k2-falkordb-sync/.
- Cost: ~$26/mo (droplet $24 + OpenAI ~$1-2 for analysis)
- Ledger entries: check with `ssh vault-neo "wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"`
- **Vault API port: 8080** (not 8000) — `curl http://localhost:8080/v1/checkpoint/latest`
- **compose.hub.yml path**: `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml` (NOT in compose/)
- **vault API also needs --no-cache rebuild** (not just restart) when source changes — same as hub-bridge

## Hub-Bridge v2.1.0 (2026-02-19)
- `/v1/chatlog`: capture auth split from vault bearer → `HUB_CAPTURE_TOKEN` (new secret). Batch ingest (1–200 items). Route-scoped rate limits (240rpm+120burst for capture).
- `/v1/handoff/save` + `/v1/handoff/latest`: atomic file write to `/data/handoff`, `HUB_HANDOFF_TOKEN` auth.
- Tokens: `hub.capture.token.txt`, `hub.handoff.token.txt` in `/opt/seed-vault/memory_v1/hub_auth/`
- Chrome extension `background.js`: durable queue (`storage.local`), batch flush (30s alarm), single-flight guard, exponential backoff on 429. Reads `captureToken || vaultToken` (backward compat).

## Vault API Dual-Tier Rate Limit (2026-02-19)
- `isPrivateIp()`: detects 10.x, 172.16-31.x, 192.168.x, 127.x, ::1 — strips `::ffff:` prefix (Docker bridge IPv4-mapped IPv6)
- `pickRlLimits(req)`: public=30rpm+10burst, internal=240rpm+120burst
- Compose: `RL_RATE_INTERNAL=240`, `RL_BURST_INTERNAL=120` in `anr-vault-api` environment
- Proof: 75/75 sequential burst test succeeded (hub-bridge → vault, private IP path)

## Extension v2.0.0 Canonical (2026-02-19) — DEPRECATED
- Decision: extension deprecated. Never worked correctly (176 logged failures, DOM selector drift, 0 /v1/chatlog calls in 24h monitoring window). Code still in repo/Chrome; cleanup pending.
- manifest.json: v1.0.0 → v2.0.0, content-context.js per-platform (not catch-all), alarms permission retained
- background.js: captureToken preferred over vaultToken, explicit authToken variable, diagnostic log (lengths only)
- captureToken configured in extension popup (64-char hex), verified via storage.sync
- e2e smoke test: chatlog_1771535912555_kjkvknexqy landed in vault ledger ✓
- auth log: `{enabled:true, captureTokenLen:64, vaultTokenLen:0, using:'captureToken'}` ✓

## CC Session-Start: Check Karma Proposals
Run at each CC session start to see if Karma has left a proposal:
```bash
ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_bridge/data/handoffs/collab.jsonl 2>/dev/null | python3 -c 'import sys,json; msgs=[json.loads(l) for l in sys.stdin if l.strip()]; byid={}; [byid.update({m[\"id\"]:m}) for m in msgs]; pending=[m for m in byid.values() if m.get(\"to\")==\"cc\" and m.get(\"status\")==\"pending\"]; [print(m[\"id\"],m[\"type\"],m[\"content\"][:100]) for m in pending] or print(\"no pending Karma proposals\")'"
```

## Last Updated
2026-02-22 (session 2) — Major session: (1) Multi-file upload + any format in Karma Window; (2) Gated/ directory = priority ingest flag, review_queue.jsonl; (3) /v1/review-queue + /v1/cypher + karma-server /graph-query (graph access primitives, smoke tested); (4) 429 retry logic in callLLM with exponential backoff (inject test verified); (5) Karma self-access file bridge — /v1/vault-file/:alias (read MEMORY.md/CLAUDE.md/consciousness/etc, append to MEMORY.md); (6) CLAUDE.md updated: Python escape pitfall + TIMEOUT 0 pitfall + Karma File Locations section; (7) FalkorDB rebuilt with TIMEOUT=10000 (was TIMEOUT=0), batch4 running clean ok:60 err:0; (8) K2 live: connected_slaves:1, lag:0.
