# Karma Graph Distillation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Karma reads her own FalkorDB graph every 24h, synthesizes patterns and gaps via GLM-5, writes results to the vault ledger, and injects them into her system prompt on every chat turn.

**Architecture:** A second timer runs inside `ConsciousnessLoop` alongside the 60s observation cycle. Every `DISTILLATION_INTERVAL_HOURS` hours it queries FalkorDB for structural data, calls GLM-5 to synthesize, writes a schema-compliant fact to `memory.jsonl`, re-ingests key insights as FalkorDB episodes, and SMS-notifies on high-confidence findings. Hub-bridge reads the distillation fact from vault API (same ledger-scan pattern as `karma_brief`) and injects it into `buildSystemText()`.

**Tech Stack:** Python 3.11, asyncio, FalkorDB (Redis protocol), GLM-5 via router, JSONL ledger (direct file write), Node.js hub-bridge, vault API (FastAPI)

**Critical Pitfalls (read before touching anything):**
- `karma-server` runs from a built Docker image. Editing source files has zero effect until you rebuild. Get the run command first: `docker inspect karma-server --format='{{.Config.Cmd}} {{json .HostConfig}}'`
- FalkorDB graph name is `neo_workspace` (from `config.GRAPHITI_GROUP_ID`). Do NOT use `karma`.
- FalkorDB result shape: `result[1]` is the data rows. `result[0]` is column headers. `result[1]` may be empty list `[]` — always guard.
- Vault schema REQUIRES: `id`, `type`, `tags`, `content`, `source.kind` (must be one of `["user","system","import","tool","web"]`), `confidence`, `created_at`, `updated_at`, `verification` block (protocol_version, verified_at, verifier, status, notes).
- Karma-server ledger path: `/ledger/memory.jsonl` (Docker volume mount from host `/opt/seed-vault/memory_v1/ledger/`). It can write directly — no vault API call needed.
- Hub-bridge source: `/opt/seed-vault/memory_v1/hub_bridge/app/server.js`. Always `--no-cache` rebuild.
- Vault API source: found via `find /opt/seed-vault -name 'server.js' | grep -v hub_bridge | grep -v node_modules`. Port 8080.

---

### Task 1: Add distillation config to `config.py`

**Files:**
- Modify: `/opt/seed-vault/memory_v1/karma-core/config.py`

**Step 1: Read the current file**

```bash
ssh vault-neo "cat /opt/seed-vault/memory_v1/karma-core/config.py"
```

**Step 2: Append distillation config vars at the end**

Add after the existing `BOOTSTRAP_LIMIT` line:

```python
# Graph distillation loop
DISTILLATION_ENABLED = os.getenv("DISTILLATION_ENABLED", "true").lower() in ("true", "1", "yes")
DISTILLATION_INTERVAL_HOURS = float(os.getenv("DISTILLATION_INTERVAL_HOURS", "24"))
DISTILLATION_MAX_EPISODES = int(os.getenv("DISTILLATION_MAX_EPISODES", "200"))
```

Use Python on vault-neo to append safely:

```bash
ssh vault-neo "python3 << 'PYEOF'
path = '/opt/seed-vault/memory_v1/karma-core/config.py'
addition = '''
# Graph distillation loop
DISTILLATION_ENABLED = os.getenv(\"DISTILLATION_ENABLED\", \"true\").lower() in (\"true\", \"1\", \"yes\")
DISTILLATION_INTERVAL_HOURS = float(os.getenv(\"DISTILLATION_INTERVAL_HOURS\", \"24\"))
DISTILLATION_MAX_EPISODES = int(os.getenv(\"DISTILLATION_MAX_EPISODES\", \"200\"))
'''
src = open(path).read()
if 'DISTILLATION_ENABLED' not in src:
    open(path, 'a').write(addition)
    print('OK')
else:
    print('ALREADY PRESENT')
PYEOF"
```

**Step 3: Verify**

```bash
ssh vault-neo "python3 -c 'import sys; sys.path.insert(0, \"/opt/seed-vault/memory_v1/karma-core\"); import config; print(config.DISTILLATION_INTERVAL_HOURS, config.DISTILLATION_ENABLED)'"
```

Expected: `24.0 True`

**Step 4: Commit** *(after rebuild in Task 2 — commit config + consciousness together)*

---

### Task 2: Add `_distillation_cycle()` to `consciousness.py`

**Files:**
- Modify: `/opt/seed-vault/memory_v1/karma-core/consciousness.py`

This is the core task. Three changes:
1. `__init__`: add `_last_distillation_time = 0.0`
2. New method `_distillation_cycle()`: query graph → synthesize → write → ingest → SMS
3. `run()`: check distillation interval on every loop tick

**Step 1: Back up the file**

```bash
ssh vault-neo "cp /opt/seed-vault/memory_v1/karma-core/consciousness.py /opt/seed-vault/memory_v1/karma-core/consciousness.py.bak.distillation.$(date +%Y%m%dT%H%M%SZ)"
```

**Step 2: Add `_last_distillation_time` to `__init__`**

Find the `self._cycle_durations` line (near end of `__init__`). Add after it:

```python
        self._last_distillation_time: float = 0.0  # Unix epoch; 0 = run on first opportunity
```

Use Python patch:

```bash
ssh vault-neo "python3 << 'PYEOF'
path = '/opt/seed-vault/memory_v1/karma-core/consciousness.py'
src = open(path).read()
old = '        self._cycle_durations: list[float] = []  # Last 100 durations for avg'
new = old + '\n        self._last_distillation_time: float = 0.0  # Unix epoch; 0 = run on first opportunity'
if old in src and '_last_distillation_time' not in src:
    open(path, 'w').write(src.replace(old, new, 1))
    print('OK')
else:
    print('SKIP or ALREADY PRESENT')
PYEOF"
```

**Step 3: Add `_distillation_cycle()` method**

Insert the full method before the `def _observe(self)` line:

```python
    # ─── Graph Distillation ───────────────────────────────────────────

    async def _distillation_cycle(self):
        """Read FalkorDB graph structure, synthesize patterns/gaps via GLM-5,
        write result to vault ledger and re-ingest key insights as episodes."""
        import time as _time
        import json as _json

        print("[DISTILLATION] Starting graph distillation cycle")

        try:
            falkor = self._get_falkor()
            group_id = config.GRAPHITI_GROUP_ID

            # Query 1: Top entities by relationship count
            top_q = """
                MATCH (e:Entity)
                OPTIONAL MATCH (e)-[r]-()
                RETURN e.name, e.entity_type, count(r) AS rel_count
                ORDER BY rel_count DESC
                LIMIT 15
            """
            top_result = falkor.execute_command("GRAPH.QUERY", group_id, top_q)
            top_rows = top_result[1] if len(top_result) >= 2 and top_result[1] else []

            # Query 2: Recent episodes (last 7 days, exclude distillation self-refs)
            seven_days_ago = _time.time() - (7 * 24 * 3600)
            max_ep = config.DISTILLATION_MAX_EPISODES
            ep_q = f"""
                MATCH (ep:Episodic)
                WHERE ep.created_at > {seven_days_ago}
                RETURN ep.content, ep.created_at
                ORDER BY ep.created_at DESC
                LIMIT {max_ep}
            """
            ep_result = falkor.execute_command("GRAPH.QUERY", group_id, ep_q)
            ep_rows = ep_result[1] if len(ep_result) >= 2 and ep_result[1] else []

            # Query 3: Low-connection entities (gaps — mentioned but underdeveloped)
            gap_q = """
                MATCH (e:Entity)
                OPTIONAL MATCH (e)-[r]-()
                WITH e, count(r) AS rel_count
                WHERE rel_count <= 2
                RETURN e.name, e.entity_type, rel_count
                ORDER BY rel_count ASC
                LIMIT 10
            """
            gap_result = falkor.execute_command("GRAPH.QUERY", group_id, gap_q)
            gap_rows = gap_result[1] if len(gap_result) >= 2 and gap_result[1] else []

        except Exception as e:
            print(f"[DISTILLATION] FalkorDB query failed: {e}")
            return

        # Build context for GLM-5
        def safe_str(v):
            return str(v) if v is not None else ""

        top_entities_text = "\n".join(
            f"  - {safe_str(r[0])} ({safe_str(r[1])}): {safe_str(r[2])} connections"
            for r in top_rows[:15]
        ) or "  (none)"

        recent_episodes_text = "\n".join(
            f"  - {safe_str(r[0])[:200]}"
            for r in ep_rows[:30]
        ) or "  (none)"

        gaps_text = "\n".join(
            f"  - {safe_str(r[0])} ({safe_str(r[1])}): only {safe_str(r[2])} connections"
            for r in gap_rows[:10]
        ) or "  (none)"

        prompt = f"""You are Karma analyzing your own knowledge graph.

MOST CONNECTED ENTITIES (core of your knowledge):
{top_entities_text}

RECENT ACTIVITY (last 7 days, sample):
{recent_episodes_text}

UNDEREXPLORED ENTITIES (potential gaps):
{gaps_text}

Synthesize what you see. Respond in this exact JSON format:
{{
  "themes": ["theme1", "theme2", "theme3"],
  "gaps": ["gap1", "gap2"],
  "key_insights": ["insight1", "insight2"],
  "summary": "2-3 sentence plain-language synthesis of your knowledge structure",
  "confidence": 0.0
}}

Be specific. confidence is 0.0-1.0 reflecting how meaningful this synthesis is."""

        # Call GLM-5 via router
        if not self._router:
            print("[DISTILLATION] No router — skipping synthesis")
            return

        try:
            response = await self._router.complete(
                messages=[
                    {"role": "system", "content": "You are Karma's graph distillation engine. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                task_type="reasoning"
            )
            raw = response.get("content", "").strip()

            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            synthesis = _json.loads(raw)
        except Exception as e:
            print(f"[DISTILLATION] LLM synthesis failed: {e}")
            return

        themes = synthesis.get("themes", [])
        gaps = synthesis.get("gaps", [])
        key_insights = synthesis.get("key_insights", [])
        summary = synthesis.get("summary", "")
        confidence = float(synthesis.get("confidence", 0.5))

        print(f"[DISTILLATION] Synthesis complete — confidence={confidence:.2f}, themes={len(themes)}, gaps={len(gaps)}")

        # Write to vault ledger as schema-compliant fact
        import uuid as _uuid
        from datetime import datetime as _dt, timezone as _tz

        now_iso = _dt.now(_tz.utc).isoformat()
        fact_id = f"distillation_{int(_time.time())}"
        fact = {
            "id": fact_id,
            "type": "log",
            "tags": ["karma_distillation", "graph_synthesis"],
            "content": {
                "key": "distillation_brief",
                "distillation_brief": summary,
                "themes": themes,
                "gaps": gaps,
                "key_insights": key_insights,
            },
            "source": {"kind": "tool", "ref": "karma-consciousness:distillation"},
            "confidence": confidence,
            "created_at": now_iso,
            "updated_at": now_iso,
            "verification": {
                "protocol_version": "0.1",
                "verified_at": now_iso,
                "verifier": "karma-consciousness-distillation",
                "status": "verified",
                "notes": "auto-generated graph distillation synthesis",
            },
        }

        try:
            with open(config.LEDGER_PATH, "a", encoding="utf-8") as f:
                f.write(_json.dumps(fact) + "\n")
            print(f"[DISTILLATION] Fact written to ledger: {fact_id}")
        except Exception as e:
            print(f"[DISTILLATION] Ledger write failed: {e}")
            return

        # Re-ingest key insights as FalkorDB episodes (source tag guards against recursion)
        if self._ingest_episode and key_insights:
            from asyncio import get_event_loop as _gel
            loop = _gel()
            for insight in key_insights[:5]:
                try:
                    loop.create_task(self._ingest_episode(
                        f"[karma-distillation] {insight}",
                        "Karma's graph distillation insight",
                        source="karma-distillation"
                    ))
                except Exception as e:
                    print(f"[DISTILLATION] Episode ingest failed: {e}")

        # SMS for high-confidence synthesis
        if self._sms_notify and confidence >= 0.8:
            try:
                loop = _gel()
                loop.create_task(self._sms_notify(
                    f"Graph distillation: {summary[:200]}",
                    category="self_improvement",
                    confidence=confidence
                ))
            except Exception as e:
                print(f"[DISTILLATION] SMS failed: {e}")

        self._last_distillation_time = _time.time()
        print(f"[DISTILLATION] Cycle complete. Next in {config.DISTILLATION_INTERVAL_HOURS}h")
```

Use a Python patch script written locally and SCP'd to vault-neo (never use heredoc for JS/Python with escape sequences):

```python
# Save this as tmp/patch_distillation.py locally, then SCP and run
path = '/opt/seed-vault/memory_v1/karma-core/consciousness.py'
src = open(path).read()

# Insert the new method before _observe
insert_before = '    # ─── Phase 1: OBSERVE'
if insert_before not in src:
    insert_before = '    def _observe(self)'  # fallback

new_method = '''    # ─── Graph Distillation ───────────────────────────────────────────

    async def _distillation_cycle(self):
        # [full method body from Step 3 above]
        pass  # replace with full implementation

'''

if '_distillation_cycle' not in src and insert_before in src:
    patched = src.replace(insert_before, new_method + insert_before, 1)
    open(path, 'w').write(patched)
    print('OK')
else:
    print('SKIP or ALREADY PRESENT')
```

**Step 4: Add distillation check to `run()` loop**

Find the existing `run()` loop body:
```python
            try:
                await asyncio.sleep(config.CONSCIOUSNESS_INTERVAL)
                if not self._running:
                    break
                await self._cycle()
```

Add distillation check after `await self._cycle()`:

```python
                # Check if distillation interval has elapsed
                if config.DISTILLATION_ENABLED:
                    import time as _t
                    hours_elapsed = (_t.time() - self._last_distillation_time) / 3600
                    if hours_elapsed >= config.DISTILLATION_INTERVAL_HOURS:
                        await self._distillation_cycle()
```

Patch this with Python on vault-neo using the same pattern.

**Step 5: Get the current karma-server docker run command**

```bash
ssh vault-neo "docker inspect karma-server --format='{{json .Config}} {{json .HostConfig}}' | python3 -m json.tool | grep -E 'Cmd|Env|Binds|Image|NetworkMode|Ports' | head -30"
```

Save this output — you'll need it to restart the container after rebuild.

**Step 6: Rebuild karma-server**

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/karma-core && docker build -t karma-core:latest . 2>&1 | tail -5"
```

**Step 7: Restart karma-server with same run parameters**

```bash
ssh vault-neo "docker stop karma-server && docker rm karma-server"
# Then re-run with the same parameters captured in Step 5
# Typically:
ssh vault-neo "docker run -d [same flags as before] karma-core:latest"
```

**Step 8: Verify distillation starts**

```bash
ssh vault-neo "docker logs karma-server --follow 2>&1 | grep -i distillation"
```

Expected on startup: `[DISTILLATION] Starting graph distillation cycle` (runs immediately since `_last_distillation_time = 0`).

After completion:
```bash
ssh vault-neo "grep 'karma_distillation' /opt/seed-vault/memory_v1/ledger/memory.jsonl | tail -1 | python3 -m json.tool"
```

Expected: JSON fact with `tags: ["karma_distillation", "graph_synthesis"]` and `content.distillation_brief`.

**Step 9: Commit**

```bash
cd /path/to/local/repo
# Sync files from vault-neo first
scp vault-neo:/opt/seed-vault/memory_v1/karma-core/consciousness.py karma-core/consciousness.py
scp vault-neo:/opt/seed-vault/memory_v1/karma-core/config.py karma-core/config.py
git add karma-core/consciousness.py karma-core/config.py
git commit -m "feat: graph distillation loop — Karma reads her own graph every 24h, synthesizes via GLM-5"
```

---

### Task 3: Extend vault API `/v1/checkpoint/latest` to return `distillation_brief`

**Files:**
- Modify: vault `api/server.js` (find path with `ssh vault-neo "find /opt/seed-vault -name 'server.js' | grep -v hub_bridge | grep -v node_modules"`)

**Step 1: Find the file and locate the karma_brief scan block**

```bash
ssh vault-neo "grep -n 'karma_brief\|distillation' /path/to/vault/api/server.js | head -20"
```

**Step 2: Read the existing karma_brief scan pattern**

It looks like:
```js
const briefFact = findLatestFact(ledger, f =>
  f.tags?.includes("karma_brief") && f.content?.checkpoint_id === ckid
);
res.json({
  ...existingFields,
  karma_brief: briefFact?.content?.karma_brief || null,
});
```

**Step 3: Add distillation_brief scan after karma_brief**

Add before `res.json(...)`:

```js
// Scan ledger for latest distillation fact (not checkpoint-tied — just most recent)
const distillationFact = findLatestFact(ledger, f =>
  f.tags?.includes("karma_distillation")
);
```

Add `distillation_brief` to the response:

```js
res.json({
  ...existingFields,
  karma_brief: briefFact?.content?.karma_brief || null,
  distillation_brief: distillationFact?.content?.distillation_brief || null,
});
```

Patch with Python on vault-neo using the same heredoc-safe pattern.

**Step 4: Backup, patch, rebuild vault API**

```bash
# Backup
ssh vault-neo "cp /path/to/vault/api/server.js /path/to/vault/api/server.js.bak.distillation.$(date +%Y%m%dT%H%M%SZ)"

# Find compose file and service name for vault API
ssh vault-neo "find /opt/seed-vault -name 'compose.yml' | head -5"
# Vault API service is 'api' in compose.yml, container name anr-vault-api

# Rebuild
ssh vault-neo "cd /opt/seed-vault && docker compose -f compose.yml build --no-cache api 2>&1 | tail -5"
ssh vault-neo "cd /opt/seed-vault && docker compose -f compose.yml up -d api"
```

**Step 5: Verify**

```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s http://localhost:8080/v1/checkpoint/latest -H \"Authorization: Bearer \$TOKEN\" | python3 -m json.tool | grep -E 'distillation|karma_brief'"
```

Expected: `"distillation_brief": "..."` (or `null` if distillation hasn't run yet — run Task 2 first).

**Step 6: Commit**

```bash
scp vault-neo:/path/to/vault/api/server.js vault-api/server.js
git add vault-api/server.js
git commit -m "feat: /v1/checkpoint/latest returns distillation_brief alongside karma_brief"
```

---

### Task 4: Inject `distillation_brief` into hub-bridge `buildSystemText()`

**Files:**
- Modify: `/opt/seed-vault/memory_v1/hub_bridge/app/server.js` (local copy: `hub-bridge/server.js`)

**Step 1: Read current `buildSystemText()` — find the karma_brief injection**

```bash
ssh vault-neo "grep -n 'KARMA SELF-KNOWLEDGE\|karma_brief\|distillation' /opt/seed-vault/memory_v1/hub_bridge/app/server.js | head -20"
```

The existing karma_brief block looks like:
```js
if (ckLatest && ckLatest.karma_brief) {
  const ckId = ckLatest.checkpoint_id || ...;
  text += `\n\n--- KARMA SELF-KNOWLEDGE (${ckId}) ---\n${ckLatest.karma_brief}\n---`;
}
```

**Step 2: Add distillation_brief block immediately after karma_brief block**

```js
if (ckLatest && ckLatest.distillation_brief) {
  text += `\n\n--- KARMA GRAPH SYNTHESIS ---\n${ckLatest.distillation_brief}\n---`;
}
```

Patch with Python on vault-neo:

```bash
ssh vault-neo "python3 << 'PYEOF'
path = '/opt/seed-vault/memory_v1/hub_bridge/app/server.js'
src = open(path).read()

# Find the end of the karma_brief block — the closing brace after the text += line
old = \"  text += `\\\\n\\\\n--- KARMA SELF-KNOWLEDGE (\${ckId}) ---\\\\n\${ckLatest.karma_brief}\\\\n---`;\\n  }\"
new = old + \"\"\"
  if (ckLatest && ckLatest.distillation_brief) {
    text += `\\\\n\\\\n--- KARMA GRAPH SYNTHESIS ---\\\\n\${ckLatest.distillation_brief}\\\\n---`;
  }\"\"\"

# Use line-based approach instead
lines = src.split('\\n')
result = []
i = 0
while i < len(lines):
    result.append(lines[i])
    if 'KARMA SELF-KNOWLEDGE' in lines[i] and 'ckLatest.karma_brief' in lines[i]:
        # Find the closing brace of this if block
        j = i + 1
        while j < len(lines) and lines[j].strip() != '}':
            result.append(lines[j])
            j += 1
        if j < len(lines):
            result.append(lines[j])  # the closing }
            result.append('  if (ckLatest && ckLatest.distillation_brief) {')
            result.append('    text += `\\\\n\\\\n--- KARMA GRAPH SYNTHESIS ---\\\\n\${ckLatest.distillation_brief}\\\\n---`;')
            result.append('  }')
            i = j + 1
            continue
    i += 1

if 'distillation_brief' not in src:
    open(path, 'w').write('\\n'.join(result))
    print('PATCHED OK')
else:
    print('ALREADY PRESENT')
PYEOF"
```

> **Note:** If the line-based approach doesn't find the right injection point, read lines 235-260 of server.js and adjust the pattern. The goal is to insert the distillation block immediately after the karma_brief if-block inside `buildSystemText()`.

**Step 3: Backup, rebuild, deploy hub-bridge**

```bash
ssh vault-neo "cp /opt/seed-vault/memory_v1/hub_bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js.bak.distillation_inject.$(date +%Y%m%dT%H%M%SZ)"

ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache 2>&1 | tail -5"

ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml up -d && sleep 3 && docker logs anr-hub-bridge --tail=3"
```

Expected: `hub-bridge v2.5.1 listening on :18090`

**Step 4: E2E test — verify distillation appears in system prompt**

```bash
# Send a chat message and check hub-bridge logs for GRAPH SYNTHESIS
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you know about your own knowledge graph?"}' | python3 -m json.tool | head -20

# Check logs for the injection
ssh vault-neo "docker logs anr-hub-bridge --tail=20 2>&1 | grep -i 'GRAPH SYNTHESIS\|distillation'"
```

Expected: Karma's response references her own graph structure (themes, gaps) — information she got from the injected synthesis block.

**Step 5: Commit and push**

```bash
scp vault-neo:/opt/seed-vault/memory_v1/hub_bridge/app/server.js hub-bridge/server.js
cd /path/to/local/repo
# Pre-commit secret scan
grep -rn "Bearer\|token\|secret\|password\|api_key" --include="*.js" --include="*.py" hub-bridge/server.js karma-core/ | grep -v "FILE\|TOKEN_FILE\|env\|getenv"
git add hub-bridge/server.js
git commit -m "feat: v2.7.0 — inject distillation_brief into Karma system prompt via buildSystemText()"
git push
```

---

## Verification Checklist

After all 4 tasks:

- [ ] `config.py`: `python3 -c "import config; print(config.DISTILLATION_INTERVAL_HOURS)"` → `24.0`
- [ ] karma-server logs: `[DISTILLATION] Cycle complete.` within 2 minutes of startup
- [ ] Ledger: `grep karma_distillation memory.jsonl | tail -1 | python3 -m json.tool` → valid fact with `distillation_brief`
- [ ] FalkorDB: new episodes with `source: karma-distillation` present
- [ ] Vault API: `/v1/checkpoint/latest` response includes `distillation_brief` field
- [ ] Karma chat: system prompt contains `--- KARMA GRAPH SYNTHESIS ---` block
- [ ] Karma can describe her own knowledge structure unprompted
