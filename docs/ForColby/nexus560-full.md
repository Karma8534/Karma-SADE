# NEXUS 5.6.0 — FULL AUTONOMOUS BUILD
# Paste into fresh CC session. Walk away. Come back to a working system.
# Covers: ALL phases (0-4 + 7), ALL MemPalace primitives, cascade loop, S160 verification, known issues.
# Phases 5 (additional transport) and 6 (voice) are explicitly deferred — need hardware/Sovereign.
# Estimated: 8-16 hours on Opus 1M.

---

/resurrect

You have FULL PERMISSION to: edit any file, create any file, deploy to vault-neo, restart any service, install dependencies (pin versions), run any test, SSH anywhere, rebuild Docker images, modify hooks/settings, push to git. The only things you CANNOT do: spend money on new services, delete MEMORY.md/nexus.md/sacred context, or modify CLAUDE.md without noting it.

Read these files NOW (parallel reads):
1. `docs/ForColby/nexus.md` — the entire plan, v5.6.0
2. `docs/wip/nexux2proposal.md` — MemPalace extraction report (18 primitives)
3. `.gsd/STATE.md` — current system state
4. `Karma2/map/preclaw1-gap-map.md` — gap map (79 HAVE / 0 MISSING / 16 N/A)

After reading, execute the 5 stages below WITHOUT STOPPING. No narration between tasks. No "shall I proceed?" Output = code + test results + deployment evidence.

---

## STAGE 0: CODEX CLAIMS VERIFICATION (do this BEFORE anything else — 45 min)

Codex reported the following work completed. DOCUMENTATION IS NOT EVIDENCE. Every claim below must be reverse-engineered to ground truth. Run the live test. If it fails, the claim is FALSE and becomes a Stage 2 build task.

### Codex Claims (each must be LIVE-TESTED, not read from docs)

**Memory integration slice (cc_server_p1.py):**
```
curl -s http://127.0.0.1:7891/memory/ingest-feed | python -c "import sys,json; print(json.load(sys.stdin))" 2>/dev/null || echo "FAIL: /memory/ingest-feed"
curl -s http://127.0.0.1:7891/mcp/mempalace_status | python -c "import sys,json; print(json.load(sys.stdin))" 2>/dev/null || echo "FAIL: /mcp/mempalace_status"
curl -s http://127.0.0.1:7891/mcp/mempalace_search?query=test | python -c "import sys,json; print(json.load(sys.stdin))" 2>/dev/null || echo "FAIL: /mcp/mempalace_search"
curl -s -X POST http://127.0.0.1:7891/memory/save -H "Content-Type: application/json" -d '{"content":"verification probe"}' | python -c "import sys,json; print(json.load(sys.stdin))" 2>/dev/null || echo "FAIL: /memory/save"
curl -s http://127.0.0.1:7891/memory/wakeup | python -c "import sys,json; r=json.load(sys.stdin); print('NON-EMPTY' if r.get('wakeup','') else 'EMPTY')" 2>/dev/null || echo "FAIL: /memory/wakeup"
```

**New scripts exist and run:**
```
test -f Scripts/nexus_ingestion_feeder.py && python Scripts/nexus_ingestion_feeder.py --help 2>/dev/null | head -1 || echo "FAIL: nexus_ingestion_feeder.py"
test -f Scripts/palace_precompact.py && python Scripts/palace_precompact.py --help 2>/dev/null | head -1 || echo "FAIL: palace_precompact.py"
test -f Scripts/nexus_memory_bench.py && python Scripts/nexus_memory_bench.py --help 2>/dev/null | head -1 || echo "FAIL: nexus_memory_bench.py"
test -f Scripts/aaak.py && python -c "from Scripts.aaak import *; print('IMPORT OK')" 2>/dev/null || echo "FAIL: aaak.py import"
```

**Bench artifact:**
```
test -f nexus_memory_bench_latest.json && python -c "import json; d=json.load(open('nexus_memory_bench_latest.json')); assert d.get('search_hits',0)>=3; assert d.get('palace_hits',0)>=3; assert d.get('wakeup_has_bench_token'); print('BENCH PASS')" 2>/dev/null || echo "FAIL: bench artifact"
```

**Retention hooks:**
```
test -f hooks_audit.jsonl && python -c "
import json
found=False
for line in open('hooks_audit.jsonl'):
    e=json.loads(line)
    if e.get('hook_name')=='palace_precompact' and e.get('event')=='Stop': found=True; break
print('HOOK PROOF PASS' if found else 'HOOK PROOF FAIL')
" 2>/dev/null || echo "FAIL: hooks_audit.jsonl"
```

**Browser /cc contract:**
```
curl -s -o /dev/null -w '%{http_code}' https://hub.arknexus.net/cc/health 2>/dev/null || echo "FAIL: /cc/health"
TOKEN=$(ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt')
curl -s -X POST https://hub.arknexus.net/cc/v1/chat -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"message":"ping"}' | python -c "import sys,json; r=json.load(sys.stdin); print('CC CHAT OK' if r.get('assistant_text') else 'CC CHAT FAIL')" 2>/dev/null || echo "FAIL: /cc/v1/chat"
```

**PDF inbox drained:**
```
ls Karma_PDFs/Inbox/ 2>/dev/null | wc -l | xargs -I{} bash -c '[ {} -eq 0 ] && echo "INBOX DRAINED" || echo "FAIL: {} files remain in Inbox"'
test -d Karma_PDFs/Processed/2026-04-07 && echo "PROCESSED DIR EXISTS" || echo "FAIL: no 2026-04-07 processed dir"
test -f inbox-primitives-20260407.md && echo "PRIMITIVES EXTRACTION EXISTS" || echo "FAIL: no inbox-primitives-20260407.md"
```

**Email daemon:**
```
grep -c "STATUS_INTERVAL_MIN.*30" Scripts/cc_email_daemon.py 2>/dev/null && echo "EMAIL CADENCE OK" || echo "FAIL: email cadence not 30"
```

**Persistence across restart:**
```
# This is a LIVE test — cannot verify from docs. Run it:
# 1. Save a token via /memory/save
# 2. Restart cc_server
# 3. Query for the token
# If the prompt session allows restarting cc_server, do it. If not, mark DEFERRED.
echo "PERSISTENCE: DEFERRED (requires cc_server restart cycle)"
```

**Test suite:**
```
python -m pytest -q tests/test_palace_precompact.py tests/test_cc_email_daemon.py tests/test_cc_server_harness.py tests/test_electron_memory_autosave.py 2>&1 | tail -3
node --test tests/test_proxy_routing.mjs 2>&1 | tail -3
```

**Codex ledger:**
```
test -f codex-execution-ledger.md && echo "LEDGER EXISTS" || echo "FAIL: no codex-execution-ledger.md"
```

Write ALL results to `.gsd/S162-codex-verification.md` with columns: `Claim | Test Command | Result (PASS/FAIL/DEFERRED)`. For every FAIL: add it to the Stage 2 build queue as a fix task. For every PASS: note the live evidence. For every DEFERRED: note why and when to retest.

**RULE: If a Codex claim passes live test → trust it. If it fails → it's fiction. No middle ground. No "probably works." Binary.**

---

## STAGE 1: GROUND TRUTH AUDIT (infrastructure — 30 min)

Before building ANYTHING, verify what ACTUALLY works right now. S160 claimed 79 HAVE but S160 HONEST FINAL said "mostly decoration, engine never ran end-to-end." Trust nothing. Test everything.

Run these checks and record results in `.gsd/S162-ground-truth-audit.md`:

```
# Infrastructure alive?
ssh vault-neo "docker ps --format '{{.Names}} {{.Status}}' | sort"
curl -s -o /dev/null -w '%{http_code}' https://hub.arknexus.net/v1/chat
ssh vault-neo "wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"

# CC server on P1?
curl -s -o /dev/null -w '%{http_code}' http://localhost:7891/health 2>/dev/null || echo "CC server DOWN"

# K2 alive?
ssh vault-neo "ssh -p 2223 -l karma localhost 'echo K2_OK'" 2>/dev/null || echo "K2 UNREACHABLE"

# Karma responds with identity?
TOKEN=$(ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt')
curl -s -X POST https://hub.arknexus.net/v1/chat -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"message":"Who are you? One sentence."}' | python -c "import sys,json; r=json.load(sys.stdin); print(r.get('assistant_text','NO RESPONSE')[:200])"

# Vesper pipeline running?
ssh vault-neo "ssh -p 2223 -l karma localhost 'systemctl is-active karma-regent vesper-watchdog.timer'" 2>/dev/null || echo "VESPER STATUS UNKNOWN"

# FalkorDB reachable?
ssh vault-neo "docker exec falkordb redis-cli GRAPH.QUERY neo_workspace 'MATCH (n) RETURN count(n)'" 2>/dev/null || echo "FALKORDB UNREACHABLE"

# Kiki running?
ssh vault-neo "ssh -p 2223 -l karma localhost 'cat /mnt/c/dev/Karma/k2/cache/kiki_state.json 2>/dev/null | python3 -c \"import sys,json; s=json.load(sys.stdin); print(f\\\"cycles={s.get(\\\\\\\"total_cycles\\\\\\\",0)} pass_rate={s.get(\\\\\\\"pass_rate\\\\\\\",0)}\\\")\"'" 2>/dev/null || echo "KIKI STATUS UNKNOWN"

# Hub frontend loads?
curl -s -o /dev/null -w '%{http_code}' https://hub.arknexus.net/

# Electron app exists?
test -f electron/main.js && echo "ELECTRON EXISTS" || echo "ELECTRON MISSING"
```

Write results to `.gsd/S162-ground-truth-audit.md` with three columns: `Component | Expected | Actual`. Mark each: LIVE / DOWN / DEGRADED / UNTESTED.

**CRITICAL RULE:** If a component is DOWN, fix it before moving to Stage 2. Infrastructure must be alive before building on top of it. If vault-neo containers are down, bring them up. If K2 is unreachable, note it and proceed with vault-neo-only tasks.

---

## STAGE 2: PHASE 0 + PHASE 1 — CORE + MEMORY (3-5 hours)

Write `.gsd/phase-nexus560-CONTEXT.md` and `.gsd/phase-nexus560-PLAN.md` before touching code. Mark tasks done as you go in the PLAN.

### Phase 0: Core Executor (4 tasks)

**0-1. gap_map.py** — `Scripts/gap_map.py`
- Parses `Karma2/map/preclaw1-gap-map.md`, updates row status, recomputes totals atomically (write-temp-then-rename).
- TDD: parse → update → verify totals consistent → round-trip preserves all rows.

**0-2. vesper_eval.py hard gate** — `Vesper/vesper_eval.py`
- Candidates missing `target_files`, `test_command`, or `diff` → auto-REJECT.
- TDD: 3 reject cases + 1 pass case.

**0-3. vesper_governor.py smoke gate** — `Vesper/vesper_governor.py`
- Smoke test (exit code check) before promotion. Failed smoke → rollback. Passed → atomic gap map update via gap_map.py.
- TDD: mock promotion with pass/fail smoke.

**0-4. karma_persistent.py gap_closure** — `Scripts/karma_persistent.py`
- Recognize `gap_closure` bus message type. Dispatch. Retry on failure (max 3). Structured JSON output.
- TDD: mock bus message → recognized → dispatched → retried on fail.

### Phase 1: Persistent Memory — MemPalace Enhanced (8 tasks)

Read MemPalace source at `docs/wip/leaks/mempalace-main/mempalace-main/mempalace/` for implementation reference.

**1-1. 4-Layer Memory Stack** — `hub-bridge/app/server.js` `buildSystemText()`
- RENAME existing sections to L0-L3 labels. L0=identityBlock, L1=memoryMdCache+recurringTopics, L2=karmaCtx, L3=semanticCtx. Add token budget comments. DO NOT break existing behavior — this is a rename.
- Verify: curl /v1/chat → debug log shows all 4 layers.

**1-2. Temporal KG** — FalkorDB Entity nodes
- Add `valid_from`/`valid_to` string properties to Entity creation in batch_ingest.py.
- Add `invalidate_entity(name, ended)` function to karma-core server.py. Add to TOOL_DEFINITIONS + ALLOWED_TOOLS.
- TDD: add triple with valid_from → query → invalidate → query again (excluded).
- Deploy: rebuild karma-server image on vault-neo.

**1-3. mid-session-promote.sh** — `.claude/hooks/mid-session-promote.sh`
- Port from MemPalace `hooks/mempal_save_hook.sh`. Count human messages in JSONL transcript. Every 15, block + inject PROMOTE instruction. `stop_hook_active` prevents infinite loop.
- TDD: mock JSON input → block at threshold → pass-through on re-entry.

**1-4. pre-compact-flush.sh** — `.claude/hooks/pre-compact-flush.sh`
- Port from MemPalace `hooks/mempal_precompact_hook.sh`. Always block. Emergency save instruction.
- TDD: mock JSON input → always returns block.

**1-5. Register hooks** — `.claude/settings.local.json`
- Add Stop + PreCompact hook entries. Verify JSON valid. Preserve existing hooks.

**1-6. General Extractor** — `Scripts/general_extractor.py`
- Port all 5 marker sets from MemPalace `general_extractor.py`. Port code-line filter, sentiment disambiguation, turn detection.
- TDD: 7 test cases (one per type + resolved-problem→milestone + code-filter).

**1-7. Duplicate Detection** — `hub-bridge/app/server.js` or `hub-bridge/lib/dedup.js`
- Before ledger append in /v1/ambient, query anr-vault-search for similarity >= 0.9. Return duplicate warning. `X-Dedup-Check: true` header bypasses.
- TDD: same content twice → second rejected. Unique content → passes.

**1-8. Deploy Phase 0+1 to vault-neo**
- Use `/deploy` skill. git push → git pull on vault-neo → sync build context files → rebuild hub-bridge + karma-server → verify health.

---

## STAGE 3: PHASE 3 — RETRIEVAL + PLANNING (2-3 hours)

**3-1. AAAK Compression Dialect** — `Scripts/aaak_dialect.py`
- Port MemPalace `dialect.py`. Add Karma entity codes (COL=Colby, JUL=Julian, KAR=Karma, KIK=Kiki, CDX=Codex). Add `compress_for_cortex(text, max_tokens)`. Add PITFALL flag.
- TDD: compression ratio >= 10x on MEMORY.md. Entity codes present. Round-trip preserves key entities.

**3-2. Palace Structure vocabulary** — `karma-core/server.py` karmaCtx builder
- Rename output sections to Wing/Room/Hall. Map MENTIONS edge relationships to 5 hall types using general_extractor's 5-type classifier.
- TDD: karmaCtx output from `/v1/context` uses Wing/Room/Hall vocabulary. Existing functionality preserved.

**3-3. Agent Diaries** — `Scripts/agent_diary.py`
- Convention: `project="Karma_SADE_diary_{agent}"` in claude-mem. `diary_write(agent, entry)` + `diary_read(agent, last_n)`.
- Integrate into resurrect skill (read Julian's last 5 diary entries at session start).
- Integrate into wrap-session skill (write session summary as diary entry).
- TDD: write + read round-trip. Agent isolation. AAAK format.

**3-4. Contradiction Detection** — `hub-bridge/app/server.js` karmaCtx assembly
- Filter Entity relationships by `valid_to IS NULL OR valid_to >= NOW()`. Label expired facts with `[EXPIRED]`.
- TDD: expired entity excluded or labeled. Current entity unlabeled.

**3-5. AAAK in K2 cortex injection** — K2 `karma_regent.py` state_block
- Pipe MEMORY.md through `compress_for_cortex()` before injecting into 32K context. Replaces raw tail-3000-chars.
- TDD: compressed output fits 2000 tokens. Key entities present as codes.

**3-6. Deploy Phase 3 to vault-neo**
- Same deploy pattern. Rebuild karma-server (palace vocabulary changes). Restart hub-bridge (contradiction detection).

---

## STAGE 4: PHASE 2 + 4 — WORKSPACE + EXTENSIBILITY (2-3 hours)

### Phase 2: Verify S160 Shipped Features

S160 claimed 79 HAVE. Verify the critical ones ACTUALLY WORK from a browser perspective (not just backend 200). Use Claude-in-Chrome MCP or curl + parse.

Check each. Record in `.gsd/S162-workspace-verification.md`:

| Feature | Check Method | Result |
|---------|-------------|--------|
| 40 slash commands | curl /v1/chat with "/help" | ? |
| StatusBar (cost, context, health) | Load hub.arknexus.net, inspect DOM | ? |
| Settings panel | curl /v1/chat with "/settings" | ? |
| Markdown rendering in ChatFeed | Send message with **bold** and `code` | ? |
| Voice input button | Check useVoiceInput.ts exists + DOM element | ? |
| Self-edit banner | Check SelfEditBanner.tsx exists | ? |
| WIP panel | curl /v1/wip | ? |
| Permission dialog | Check PermissionDialog exists | ? |

**For each FAIL:** Fix it. For each PASS: note evidence. For each UNTESTABLE (needs browser): note it and continue.

### Phase 4: Plugin System Verification + Extension

- Verify `plugin_loader.py` loads and trust-gates plugins.
- Verify gap-tracker plugin works: `gap_status` + `gap_missing` tools.
- Verify Chrome extension manifest exists at expected path.
- Verify VS Code extension manifest exists at expected path.

### Known Issues (fix if encountered during verification)

| ID | Issue | Fix |
|----|-------|-----|
| KI-1 | buildSystemText 11 positional params | Refactor to single `opts` object if you're already editing buildSystemText |
| KI-4 | tierToMode() vestigial | Delete and inline "nexus" |
| KI-5 | getIdentityForTier dead branches | Simplify to always return KARMA_IDENTITY_PROMPT |
| KI-8 | Cascade dots reference wrong models | Update to actual live routing chain |

---

## STAGE 5: CASCADE LOOP + VERIFICATION GATE (1-2 hours)

### Wire the Autonomous Cascade

This is THE loop that makes everything else autonomous:
```
Gap map → Kiki ranks MISSING items → bus directive (gap_closure)
→ karma_persistent executes via CC --resume → watchdog emits candidate
→ eval gates on REAL test (no diff = reject, no test = reject)
→ governor deploys + smokes + updates gap map → repeat
```

Verify each link:
1. gap_map.py can parse and update the gap map
2. karma_persistent.py recognizes gap_closure messages
3. vesper_eval.py rejects candidates without diff/test
4. vesper_governor.py smoke-tests before promoting
5. gap_map.py updates atomically after promotion

If any link is broken, fix it. Then run one end-to-end test: manually post a gap_closure bus message and trace it through the pipeline.

### Phase 7: Hardening

- `.gsd/S162-ground-truth-audit.md` exists with live evidence
- `.gsd/S162-workspace-verification.md` exists with live evidence
- MEMORY.md updated with everything built
- STATE.md updated with current state
- No dead plans referencing old versions
- All new files committed to git

### FINAL VERIFICATION GATE

Run this. Every line must produce evidence. Any MISSING/FAIL/0 → go back and fix.

```
echo "=== NEXUS 5.6.0 FULL VERIFICATION ==="

# Stage 1: Infrastructure
echo "--- INFRASTRUCTURE ---"
ssh vault-neo "docker ps --format '{{.Names}}' | sort | tr '\n' ' '"
echo ""
curl -s -o /dev/null -w 'hub.arknexus.net: %{http_code}\n' https://hub.arknexus.net/

# Stage 2: Phase 0
echo "--- PHASE 0: CORE EXECUTOR ---"
test -f Scripts/gap_map.py && echo "gap_map.py: EXISTS" || echo "gap_map.py: MISSING"
python Scripts/gap_map.py --parse Karma2/map/preclaw1-gap-map.md 2>/dev/null | head -2 || echo "gap_map.py: PARSE FAILED"
grep -c "target_files\|test_command\|diff" Vesper/vesper_eval.py 2>/dev/null || echo "vesper_eval: NO HARD GATE"
grep -c "smoke\|smoke_test" Vesper/vesper_governor.py 2>/dev/null || echo "vesper_governor: NO SMOKE GATE"
grep -c "gap_closure" Scripts/karma_persistent.py 2>/dev/null || echo "karma_persistent: NO GAP_CLOSURE"

# Stage 2: Phase 1
echo "--- PHASE 1: MEMPALACE MEMORY ---"
echo "1. 4-Layer Stack:     $(grep -c 'L0\|L1\|L2\|L3' hub-bridge/app/server.js 2>/dev/null || echo 0) refs"
echo "2. Temporal KG:       $(grep -c 'valid_from\|valid_to\|invalidate' karma-core/server.py 2>/dev/null || echo 0) refs"
echo "3. Save Hook:         $(test -x .claude/hooks/mid-session-promote.sh && echo 'EXECUTABLE' || echo 'MISSING')"
echo "4. PreCompact Hook:   $(test -x .claude/hooks/pre-compact-flush.sh && echo 'EXECUTABLE' || echo 'MISSING')"
echo "5. General Extractor: $(test -f Scripts/general_extractor.py && python Scripts/general_extractor.py --help 2>/dev/null | head -1 || echo 'MISSING')"
echo "6. Duplicate Dedup:   $(grep -c 'dedup\|duplicate\|similarity' hub-bridge/app/server.js 2>/dev/null || echo 0) refs"
echo "7. Hooks Registered:  $(python -c 'import json; d=json.load(open(".claude/settings.local.json")); print("Stop" in d.get("hooks",{}) and "PreCompact" in d.get("hooks",{}))' 2>/dev/null || echo 'CHECK FAILED')"

# Stage 3: Phase 3
echo "--- PHASE 3: RETRIEVAL + PLANNING ---"
echo "8. AAAK Dialect:      $(test -f Scripts/aaak_dialect.py && echo 'EXISTS' || echo 'MISSING')"
echo "9. Palace Vocab:      $(grep -c 'Wing\|Room\|Hall\|Tunnel' karma-core/server.py 2>/dev/null || echo 0) refs"
echo "10. Agent Diaries:    $(test -f Scripts/agent_diary.py && echo 'EXISTS' || echo 'MISSING')"
echo "11. Contradiction:    $(grep -c 'valid_to\|expired\|EXPIRED' hub-bridge/app/server.js 2>/dev/null || echo 0) refs"
echo "12. AAAK in Cortex:   $(ssh vault-neo 'ssh -p 2223 -l karma localhost "grep -c compress_for_cortex /mnt/c/dev/Karma/k2/aria/karma_regent.py 2>/dev/null"' 2>/dev/null || echo 'CHECK FAILED')"

# Stage 4: Workspace
echo "--- PHASE 2+4: WORKSPACE ---"
test -f .gsd/S162-workspace-verification.md && echo "Workspace audit: EXISTS" || echo "Workspace audit: MISSING"

# Stage 5: Cascade
echo "--- CASCADE LOOP ---"
echo "gap_map→persistent→eval→governor chain: $(test -f Scripts/gap_map.py && grep -c gap_closure Scripts/karma_persistent.py 2>/dev/null && grep -c 'target_files\|REJECT' Vesper/vesper_eval.py 2>/dev/null && grep -c 'smoke' Vesper/vesper_governor.py 2>/dev/null | paste -sd'→' || echo 'BROKEN')"

# Docs
echo "--- DOCS ---"
test -f .gsd/S162-ground-truth-audit.md && echo "Ground truth audit: EXISTS" || echo "Ground truth audit: MISSING"
test -f .gsd/phase-nexus560-PLAN.md && echo "GSD PLAN: EXISTS" || echo "GSD PLAN: MISSING"

echo "=== END VERIFICATION ==="
```

After verification passes: update MEMORY.md + STATE.md, save to claude-mem, commit, push, deploy to vault-neo, invoke wrap-session.

---

## RULES (non-negotiable)

1. **TDD:** Test first → fail → implement → pass. Every task.
2. **NO NARRATION:** Code + test output. Not paragraphs.
3. **NO STOPPING:** Fix failures and continue. Never ask permission.
4. **DEPLOY AFTER EACH STAGE:** Stage 2 → deploy. Stage 3 → deploy. Stage 4 → deploy. Use `/deploy` skill.
5. **GSD:** Write CONTEXT + PLAN before code. Mark tasks done as you go.
6. **DROPLET = DEPLOYMENT TARGET:** Edit on P1 → git push → git pull vault-neo → rebuild. NEVER edit on droplet.
7. **POWERSHELL FOR GIT.**
8. **INVOKE SUPERPOWERS:** `systematic-debugging` before diagnosing. `test-driven-development` before implementing. `verification-before-completion` before claiming done.
9. **3-STRIKE RULE:** Same acceptance criterion failed 3x → STOP that task. Post to bus. Move to next task. Come back later.
10. **EVIDENCE ONLY:** "I checked" is not evidence. Terminal output is evidence.
11. **LIZA CHECK EVERY 10 MINUTES:** "Am I closing a gap or building a nexus 5.6.0 primitive?" If no → redirect.
12. **P107:** After completing ANY task, response MUST end with tool calls if work remains. Summary prose = stop trigger. DO NOT STOP.

BEGIN.
