# NEXUS 5.6.0 — FULL BUILD EXECUTION PROMPT
# Paste this into a fresh CC session. Do not modify. Do not summarize.
# Expected runtime: 4-8 hours. Do not stop until VERIFICATION GATE at the end passes.

---

/resurrect

After resurrect completes, execute the following WITHOUT STOPPING. No narration. No "shall I proceed?" No summaries between tasks. Output = working code + test results. Every task uses TDD: write test → see it fail → implement → see it pass.

Read `docs/ForColby/nexus.md` (the entire file). That is your build spec. Version 5.6.0. You are building Phases 0, 1, and 3 — the MemPalace-enhanced memory architecture. Phase 2 (workspace hardening) is scaffolded. Phases 4-7 are future. Phase D/F (organic walkthrough) is skipped.

Read `docs/wip/nexux2proposal.md` for MemPalace implementation details and source file references. The MemPalace source code is at `docs/wip/leaks/mempalace-main/mempalace-main/mempalace/` — read any file you need for implementation reference.

---

## EXECUTION ORDER (19 tasks, 3 phases)

### PHASE 0: CORE EXECUTOR (4 tasks)

**0-1. gap_map.py — shared atomic gap map updater**
- File: `Scripts/gap_map.py`
- TDD: Write test that parses `Karma2/map/preclaw1-gap-map.md`, updates a row status, recomputes totals, verifies atomicity (write-temp-then-rename).
- Accept: `python gap_map.py --status auth-migration HAVE --evidence "commit abc123"` updates row + totals consistently. Round-trip parse→serialize preserves all 93+ rows.

**0-2. vesper_eval.py — hard gate rejects candidates without diff/test**
- File: `Vesper/vesper_eval.py`
- TDD: Write test with candidate missing `target_files` → REJECT. Missing `test_command` → REJECT. Missing `diff` → REJECT. All three present → PASS to governor.
- Accept: Candidates without real file deltas are auto-rejected before reaching governor. Zero noise promotions.

**0-3. vesper_governor.py — smoke test gate + atomic gap map update**
- File: `Vesper/vesper_governor.py`
- TDD: Write test that mocks a promotion, runs smoke test (exit code check), calls gap_map.py atomically. Failed smoke → rollback. Passed smoke → gap map updated.
- Accept: No promotion without smoke. Gap map row + summary update atomically via gap_map.py.

**0-4. karma_persistent.py — accept gap_closure bus messages**
- File: `Scripts/karma_persistent.py`
- TDD: Write test with mock bus message `{"type": "gap_closure", "target": "auth-migration"}`. Verify it's recognized, dispatched, retried on failure (max 3), structured output logged.
- Accept: `gap_closure` type recognized. Failed CC resume retried. Structured JSON output per attempt.

### PHASE 1: PERSISTENT MEMORY — MEMPALACE ENHANCED (9 tasks)

**1-1. 4-Layer Memory Stack — refactor buildSystemText()**
- File: `hub-bridge/app/server.js` (function `buildSystemText`)
- Read MemPalace reference: `docs/wip/leaks/mempalace-main/mempalace-main/mempalace/layers.py`
- TDD: Write test (or curl verification) that confirms buildSystemText output has 4 labeled sections: `[L0-IDENTITY]`, `[L1-ESSENTIAL]`, `[L2-CONTEXT]`, `[L3-SEARCH]`. Verify L0+L1 total < 800 tokens. Verify L2 and L3 are populated only when relevant context exists.
- Implementation: Rename existing sections in buildSystemText to L0-L3. L0=identityBlock. L1=memoryMdCache + recurringTopics. L2=karmaCtx. L3=semanticCtx. Add token budget comments. Add `// MemPalace L0-L3 pattern (nexus 5.6.0)` marker.
- Accept: `curl -X POST https://hub.arknexus.net/v1/chat -H "Authorization: Bearer $TOKEN" -d '{"message":"hello"}'` → response includes all 4 layers in system text. Verify via debug telemetry or log.
- **IMPORTANT:** This is a RENAME + REORDER of existing code, not new functionality. Do NOT break existing buildSystemText behavior. The 4 layers already exist — you are naming them.

**1-2. Temporal Knowledge Graph — valid_from/valid_to on FalkorDB entities**
- Read MemPalace reference: `docs/wip/leaks/mempalace-main/mempalace-main/mempalace/knowledge_graph.py`
- TDD: Write a Python test script that:
  1. Adds a triple via Cypher: `MERGE (e:Entity {name:'test_kai'}) SET e.valid_from='2025-06-01', e.valid_to=NULL`
  2. Queries it with temporal filter: `MATCH (e:Entity) WHERE e.name='test_kai' AND (e.valid_to IS NULL OR e.valid_to >= '2026-04-07') RETURN e`
  3. Invalidates it: `MATCH (e:Entity {name:'test_kai'}) SET e.valid_to='2026-04-07'`
  4. Queries again — should NOT return (valid_to in past).
  5. Cleans up test node.
- Implementation: Add `valid_from` and `valid_to` properties to Entity node schema in batch_ingest. Add `invalidate_entity(name, ended)` function to karma-core server.py as a new tool. Add to TOOL_DEFINITIONS in server.js + ALLOWED_TOOLS in hooks.py.
- Accept: Round-trip test passes on vault-neo FalkorDB. Invalidated entities excluded from karmaCtx queries.

**1-3. Auto-Save Hook — mid-session-promote.sh**
- File: `.claude/hooks/mid-session-promote.sh`
- Read MemPalace reference: `docs/wip/leaks/mempalace-main/mempalace-main/hooks/mempal_save_hook.sh`
- TDD: Test the hook script locally with mock JSON input: `echo '{"session_id":"test","stop_hook_active":false,"transcript_path":"test.jsonl"}' | bash .claude/hooks/mid-session-promote.sh` → should output `{"decision":"block","reason":"..."}` when message count >= threshold. With `stop_hook_active:true` → should output `{}`.
- Implementation: Port MemPalace's save hook. Count `role:user` messages in JSONL transcript. Every 15 messages, block and inject PROMOTE instruction. Track `$STATE_DIR/${SESSION_ID}_last_save` watermark. Use `stop_hook_active` to prevent infinite loop.
- Accept: Hook returns block decision at 15-message intervals. Returns pass-through on re-entry. State file persists across invocations.
- **THEN** register in `.claude/settings.local.json` under `hooks.Stop`.

**1-4. Auto-Save Hook — pre-compact-flush.sh**
- File: `.claude/hooks/pre-compact-flush.sh`
- Read MemPalace reference: `docs/wip/leaks/mempalace-main/mempalace-main/hooks/mempal_precompact_hook.sh`
- TDD: Test with mock input: `echo '{"session_id":"test"}' | bash .claude/hooks/pre-compact-flush.sh` → MUST return `{"decision":"block","reason":"COMPACTION IMMINENT..."}` every time.
- Implementation: Port MemPalace's precompact hook. Always block. Inject emergency save instruction.
- Accept: Hook always returns block. Reason text instructs AI to save all state.
- **THEN** register in `.claude/settings.local.json` under `hooks.PreCompact`.

**1-5. General Extractor — 5-type memory classifier**
- File: `Scripts/general_extractor.py`
- Read MemPalace reference: `docs/wip/leaks/mempalace-main/mempalace-main/mempalace/general_extractor.py`
- TDD: Write pytest tests:
  - `"We decided to use GraphQL instead of REST because..."` → type=`decision`
  - `"I always use snake_case, never camelCase"` → type=`preference`
  - `"Finally got it working! The key was..."` → type=`milestone`
  - `"The bug was caused by a race condition in..."` → type=`problem`
  - `"I love how this turned out"` → type=`emotional`
  - `"Fixed the crash by adding a null check"` → type=`milestone` (resolved problem = milestone)
  - Code-heavy text with `import os` lines → code lines filtered before scoring
- Implementation: Port all 5 marker sets (DECISION_MARKERS, PREFERENCE_MARKERS, MILESTONE_MARKERS, PROBLEM_MARKERS, EMOTION_MARKERS) from MemPalace. Port `_extract_prose()` code-line filter. Port `_disambiguate()` sentiment resolution. Port `_split_into_segments()` turn detection.
- Accept: All 7 test cases pass. `python general_extractor.py <file>` prints classified memories with type counts.

**1-6. Duplicate Detection — semantic similarity check before filing**
- File: Add to `hub-bridge/app/server.js` (or `hub-bridge/lib/dedup.js`)
- TDD: Write test that posts the same observation twice to `/v1/ambient`. Second post should return `{"duplicate": true, "similarity": 0.95, "existing_id": "..."}` instead of appending.
- Implementation: Before appending to ledger in vault-api, query anr-vault-search with the incoming content. If top result similarity >= 0.9, return duplicate warning instead of writing. Add `X-Dedup-Check: true` header option to bypass (for forced writes).
- Accept: Duplicate content detected and rejected. Unique content passes through. Bypass header works.

**1-7. Register hooks in settings.local.json**
- File: `.claude/settings.local.json`
- TDD: Verify JSON is valid after edit. Verify hooks point to correct paths. Verify existing hooks preserved.
- Implementation: Add Stop and PreCompact hook entries pointing to the new shell scripts.
- Accept: `cat .claude/settings.local.json | python -m json.tool` succeeds. Both hooks registered.

**1-8. Integrate general_extractor into consciousness loop**
- File: `karma-core/server.py` (consciousness loop section)
- TDD: Write test that feeds a consciousness observation through general_extractor and verifies it gets a `memory_type` tag.
- Implementation: Import general_extractor. In the consciousness OBSERVE cycle, classify each new observation with `extract_memories()`. Add `memory_type` field to the observation before writing to SQLite/consciousness.jsonl.
- Accept: New consciousness observations have `memory_type` field. `docker exec karma-server python3 -c "from general_extractor import extract_memories; print(extract_memories('We decided to use Postgres'))"` returns `[{"memory_type": "decision", ...}]`.

**1-9. Integration test — full Phase 1 round-trip**
- TDD: Send a chat message to hub.arknexus.net. Verify:
  1. Response arrives (buildSystemText ran with L0-L3 labels)
  2. Observation written to ledger (check `wc -l` before/after)
  3. Duplicate check: send same message again → dedup fires
  4. General extractor: check consciousness.jsonl for memory_type tags
  5. Hook scripts exist and are executable
- Accept: All 5 checks pass with live evidence.

### PHASE 3: RETRIEVAL + PLANNING — MEMPALACE ENHANCED (6 tasks)

**3-1. AAAK Compression Dialect — compress_for_cortex()**
- File: `Scripts/aaak_dialect.py`
- Read MemPalace reference: `docs/wip/leaks/mempalace-main/mempalace-main/mempalace/dialect.py`
- TDD: Write pytest tests:
  - Input 1000-char English text → output < 100 chars (10x+ compression minimum)
  - Entity codes: "Colby" → "COL", "Julian" → "JUL", "Karma" → "KAR"
  - Emotion detection: text with "decided" → flag includes "DECISION"
  - Round-trip: compress → decode → verify key entities preserved
  - `compress_for_cortex(spine_data, max_tokens=500)` → output fits within budget
- Implementation: Port MemPalace's `Dialect` class. Add Karma-specific entity codes (COL, JUL, KAR, KIK=Kiki, CDX=Codex). Add `compress_for_cortex(text, max_tokens)` wrapper that truncates to token budget. Add Karma-specific flag: `PITFALL` (maps to our PITFALL type).
- Accept: All tests pass. Compression ratio >= 10x on real MEMORY.md content.

**3-2. Palace Structure — FalkorDB ontology naming**
- File: `karma-core/server.py` (karmaCtx builder)
- TDD: Write test that queries FalkorDB and verifies karmaCtx output uses palace vocabulary:
  - Section headers include "Wing:", "Room:", "Hall:"
  - Relationships labeled with hall type (facts/events/discoveries/preferences/advice)
- Implementation: In `query_relevant_context()` (or equivalent karmaCtx builder), rename output sections to use palace vocabulary. Entity nodes = Wings. Episodic clusters = Rooms. MENTIONS edges = Halls (classify by content: decisions→hall_facts, events→hall_events, insights→hall_discoveries, preferences→hall_preferences, recommendations→hall_advice). Use general_extractor's 5 types to map.
- Accept: karmaCtx output from `/v1/context` uses Wing/Room/Hall vocabulary. Existing functionality preserved.

**3-3. Agent Diaries — per-agent wing in claude-mem**
- TDD: Write test that:
  1. Saves a diary entry: `save_observation(text="SESSION:2026-04-07|built.hooks|★★★", title="DIARY: Julian session note", project="Karma_SADE_diary_julian")`
  2. Searches diary: `search(query="hooks", project="Karma_SADE_diary_julian")`
  3. Verify isolation: search with `project="Karma_SADE_diary_karma"` returns nothing.
- Implementation: Convention: each agent's diary uses project name `Karma_SADE_diary_{agent}`. Add `diary_write(agent, entry)` and `diary_read(agent, last_n)` helper functions in a new `Scripts/agent_diary.py`. Integrate into resurrect skill (read Julian's last 5 diary entries at session start). Integrate into wrap-session skill (write session summary as diary entry).
- Accept: Diary entries isolated per agent. Resurrect loads Julian diary. Wrap-session writes Julian diary.

**3-4. Contradiction Detection — query KG before asserting facts**
- File: `hub-bridge/app/server.js` (in buildSystemText or karmaCtx assembly)
- TDD: Write test where FalkorDB has fact "Kai works_on Orion (valid_to=2026-03-01)" and user asks "what does Kai work on?" → karmaCtx should flag the expired fact OR exclude it.
- Implementation: In karmaCtx assembly, filter Entity relationships by `valid_to IS NULL OR valid_to >= NOW()`. If an entity has both expired and current facts, include a `[EXPIRED]` label on old facts so Karma can say "Kai used to work on Orion but that ended in March."
- Accept: Expired facts labeled. Current facts unlabeled. Karma doesn't confidently assert stale facts.

**3-5. AAAK compression in K2 cortex injection**
- File: `k2/julian_cortex.py` or equivalent K2 state injection
- TDD: Write test that compresses MEMORY.md through `compress_for_cortex()`, verifies output fits in 2000 tokens, verifies key entities (Colby, Julian, Karma) are present as codes.
- Implementation: In K2 cortex state injection (karma_regent.py state_block or julian_cortex.py), pipe MEMORY.md content through `compress_for_cortex()` before injecting into the 32K context window. This replaces raw tail-3000-chars with compressed-full-content.
- Accept: K2 cortex receives AAAK-compressed MEMORY.md. Content fits in 2000 tokens. Decompressed content preserves all entity references.

**3-6. Integration test — full Phase 3 round-trip**
- TDD: Verify:
  1. `python aaak_dialect.py "We decided to use Postgres because of concurrent writes"` → compressed output with DECISION flag
  2. karmaCtx from `/v1/context` uses Wing/Room/Hall vocabulary
  3. Agent diary write + read round-trip works
  4. Expired FalkorDB entities excluded from karmaCtx (or labeled)
  5. K2 cortex injection uses AAAK compression (check regent log or state_block content)
- Accept: All 5 checks pass with live evidence.

---

## VERIFICATION GATE — DO NOT CLAIM DONE UNTIL ALL PASS

After all 19 tasks complete, run this verification sequence. Every line must produce evidence.

```
# Phase 0 verification
python Scripts/gap_map.py --parse Karma2/map/preclaw1-gap-map.md | head -5
python -m pytest Vesper/test_vesper_eval.py -v
python -m pytest Vesper/test_vesper_governor.py -v

# Phase 1 verification
# 1-1: buildSystemText layers
ssh vault-neo "docker logs anr-hub-bridge --tail 20 2>&1 | grep -i 'L0\|L1\|L2\|L3'"
# 1-3 + 1-4: hooks exist and are executable
ls -la .claude/hooks/mid-session-promote.sh .claude/hooks/pre-compact-flush.sh
echo '{"session_id":"test","stop_hook_active":false,"transcript_path":"/dev/null"}' | bash .claude/hooks/mid-session-promote.sh
echo '{"session_id":"test"}' | bash .claude/hooks/pre-compact-flush.sh
# 1-5: general extractor
python Scripts/general_extractor.py Scripts/cc_server_p1.py | head -10
# 1-7: settings.local.json valid
python -c "import json; json.load(open('.claude/settings.local.json')); print('VALID')"

# Phase 3 verification
python Scripts/aaak_dialect.py "We decided to use GraphQL instead of REST because of the flexibility"
python Scripts/agent_diary.py write julian "SESSION:test|verification.gate|★★★"
python Scripts/agent_diary.py read julian 1

# Recursive reverse-engineer: current state >= nexus 5.6.0
# For each Phase 1 MemPalace primitive, verify it EXISTS and WORKS:
echo "=== NEXUS 5.6.0 REVERSE VERIFICATION ==="
echo "1. 4-Layer Stack:     $(grep -c 'L0\|L1\|L2\|L3' hub-bridge/app/server.js) references in server.js"
echo "2. Temporal KG:       $(ssh vault-neo 'docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (e:Entity) WHERE e.valid_from IS NOT NULL RETURN count(e)"' 2>/dev/null || echo 'CHECK MANUALLY')"
echo "3. Save Hook:         $(test -x .claude/hooks/mid-session-promote.sh && echo 'EXISTS+EXECUTABLE' || echo 'MISSING')"
echo "4. PreCompact Hook:   $(test -x .claude/hooks/pre-compact-flush.sh && echo 'EXISTS+EXECUTABLE' || echo 'MISSING')"
echo "5. General Extractor: $(test -f Scripts/general_extractor.py && echo 'EXISTS' || echo 'MISSING')"
echo "6. Duplicate Dedup:   $(grep -c 'dedup\|duplicate' hub-bridge/app/server.js || echo '0') references in server.js"
echo "7. AAAK Dialect:      $(test -f Scripts/aaak_dialect.py && echo 'EXISTS' || echo 'MISSING')"
echo "8. Palace Vocabulary: $(grep -c 'Wing\|Room\|Hall\|Tunnel' karma-core/server.py || echo '0') references in server.py"
echo "9. Agent Diaries:     $(test -f Scripts/agent_diary.py && echo 'EXISTS' || echo 'MISSING')"
echo "10. Contradiction:    $(grep -c 'valid_to\|expired\|EXPIRED' hub-bridge/app/server.js || echo '0') references in server.js"
echo "=== END VERIFICATION ==="
```

Every line must show EXISTS/PASS/non-zero. Any MISSING/FAIL/0 = go back and fix before claiming done.

After verification passes: update MEMORY.md, save to claude-mem, commit, push, invoke wrap-session.

---

## RULES FOR THIS SESSION

1. **TDD MANDATORY:** Write test FIRST. See it FAIL. Implement. See it PASS. No exceptions.
2. **NO NARRATION:** Do not explain what you're about to do. Do it. Output = code + test results.
3. **NO STOPPING:** If a task fails, fix it and continue. Do not ask "should I proceed?" You should.
4. **DEPLOY AFTER EACH PHASE:** After Phase 0 completes, deploy to vault-neo. After Phase 1, deploy. After Phase 3, deploy. Use the `/deploy` skill.
5. **GSD DISCIPLINE:** Write `.gsd/phase-nexus560-CONTEXT.md` and `.gsd/phase-nexus560-PLAN.md` before touching code. Mark tasks done as you go.
6. **DROPLET IS DEPLOYMENT TARGET:** Edit on P1 → git push → git pull on vault-neo → rebuild. NEVER edit files on vault-neo.
7. **POWERSHELL FOR GIT:** No Git Bash. PowerShell only.
8. **INVOKE SKILLS:** `superpowers:test-driven-development` before each implementation task. `superpowers:verification-before-completion` before claiming any task done. `superpowers:systematic-debugging` if anything breaks.
9. **SAME ACCEPTANCE CRITERION FAILED 3X:** STOP. Post to bus. Do not attempt #4.
10. **EVIDENCE BEFORE ASSERTIONS:** "I checked" is not evidence. Terminal output is evidence.

BEGIN.
