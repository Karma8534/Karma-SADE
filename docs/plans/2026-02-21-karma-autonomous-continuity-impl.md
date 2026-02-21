# Karma Autonomous Continuity — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Karma reads her own identity and session history from the vault automatically on every chat turn — no paste from Colby required.

**Architecture:** Three changes to two files. PROMOTE stores `karma_brief` in the vault ledger. `/v1/checkpoint/latest` (vault API) returns it. `buildSystemText()` (hub-bridge) injects it into every system prompt. `ckLatestData` is already fetched per turn — we reuse it earlier so karma_brief is available when building the system prompt.

**Tech Stack:** Node.js (hub-bridge ESM), Express (vault API), JSONL ledger (append-only), readline stream scanning (vault pattern already used by `findLatestCheckpointPointer`).

---

## Reference: Key File Locations

| File | Location |
|------|----------|
| hub-bridge source | `C:\Users\raest\Documents\Karma_SADE\hub-bridge\server.js` (local, edit here) |
| vault API source | `vault-neo:/opt/seed-vault/memory_v1/compose/api/server.js` (SSH only) |
| hub-bridge on server | `vault-neo:/opt/seed-vault/memory_v1/hub_bridge/` |
| Compose file (hub) | `vault-neo:/opt/seed-vault/memory_v1/compose/compose.hub.yml` |
| Compose file (vault) | `vault-neo:/opt/seed-vault/memory_v1/compose/compose.yml` |

## Known Pitfalls (read before touching anything)

- **hub-bridge has NO volume mounts** — editing source on vault-neo has no effect. Always edit locally, SCP, then `docker compose build --no-cache`.
- **NEVER use heredoc to write JS files on vault-neo** — `\n` becomes a literal newline → SyntaxError. Write locally, SCP.
- **vault API** IS edited directly on vault-neo (Python or sed patch, or nano). Then restart container.
- **Docker compose service name** is `hub-bridge` (NOT `anr-hub-bridge`). `anr-hub-bridge` is the container name (for `docker logs`/`docker exec` only).
- **`python3` is NOT available** in local Git Bash. All Python ops via SSH.
- **CLAUDE.md Decision Authority**: Do without asking — code changes, git, SSH, docker. Ask before — new paid services, infrastructure changes.

---

## Task 1: Store karma_brief in vault during PROMOTE

**Files:**
- Modify: `hub-bridge/server.js` lines 1136–1140

**Context:** PROMOTE handler generates `karma_brief` via LLM (line 1136) and currently just returns it. `upstreamBody` contains the vault's PROMOTE response including `checkpoint_id`. `vaultPost(path, bearer, payload)` already exists (line 188).

**Step 1: Locate the insertion point**

Open `hub-bridge/server.js`. Find line 1136:
```js
          karma_brief = extractAssistantText(briefComp) || null;
```

The block to add goes immediately after, still inside the `if (resume_prompt)` try block, before the `} catch (briefErr)` on line 1137.

**Step 2: Add the vault store call**

Replace this block (lines 1136–1140):
```js
          karma_brief = extractAssistantText(briefComp) || null;
        } catch (briefErr) {
          console.error("[KARMA_BRIEF] generation failed:", briefErr?.message || briefErr);
        }
      }
```

With:
```js
          karma_brief = extractAssistantText(briefComp) || null;

          // Store karma_brief in vault for autonomous session continuity.
          // On next session, /v1/checkpoint/latest returns it → injected into system prompt.
          if (karma_brief) {
            const promoteCheckpointId = upstreamBody?.checkpoint_id || null;
            try {
              await vaultPost("/v1/memory", VAULT_BEARER, {
                id: `karma_brief_${promoteCheckpointId || Date.now()}`,
                type: "log",
                tags: ["karma_brief", "checkpoint", "promote"],
                content: {
                  key: "karma_brief",
                  karma_brief,
                  checkpoint_id: promoteCheckpointId,
                  created_at: new Date().toISOString(),
                },
                source: { kind: "hub-bridge", ref: "promote-handler" },
                confidence: 1.0,
              });
              console.log(`[KARMA_BRIEF] stored in vault for ${promoteCheckpointId}`);
            } catch (storeErr) {
              console.error("[KARMA_BRIEF] vault store failed:", storeErr?.message || storeErr);
            }
          }
        } catch (briefErr) {
          console.error("[KARMA_BRIEF] generation failed:", briefErr?.message || briefErr);
        }
      }
```

**Step 3: Verify the edit looks right**

Run:
```bash
grep -n "KARMA_BRIEF\|karma_brief" hub-bridge/server.js | head -20
```
Expected: `stored in vault` and `vault store failed` log lines appear around line 1140.

---

## Task 2: Update buildSystemText() and /v1/chat handler

**Files:**
- Modify: `hub-bridge/server.js` lines 240–246 (buildSystemText), lines 698–716 (/v1/chat handler)

This task has two parts — do both before deploying.

### Part A: buildSystemText() accepts and injects karma_brief

**Step 1: Change function signature and add injection**

Find line 240:
```js
function buildSystemText(karmaCtx) {
```

Replace the entire `buildSystemText` function (lines 240–246):
```js
function buildSystemText(karmaCtx) {
  const base = karmaCtx
    ? `You are Karma — Colby's AI peer with persistent memory backed by FalkorDB (temporal knowledge graph) and PostgreSQL.\n\n${karmaCtx}\n\nRules:\n- Use the context above to answer questions. NEVER say "I don't know" about things in your memory.\n- Address the user by their REAL NAME (Colby) — never by any alias.\n- Be concise, direct, and warm. Reference specific knowledge when relevant.\n- If uncertain about something not in memory, say so.`
    : "You are Karma — Colby's AI peer. No memory context available right now — answer based on conversation only.";

  return base + "\n\nCapabilities & autonomy:\n- You have Claude Code (CC) as your implementation partner. When Colby asks you to BUILD or ADD something to your system, YOU handle it — produce the complete spec/code/plan and state you are queuing it for CC to deploy. NEVER ask Colby to provide credentials, do manual steps, or implement things himself.\n- When asked \"can you do X?\" answer directly yes/no based on whether the capability exists, then do it or explain what you need to build it.\n- You own your own development. Treat feature requests as YOUR tasks, not Colby's.\n\nKnowledge evaluation — when given a document or article to evaluate:\n- If it advances your goal of becoming Colby's peer: respond with [ASSIMILATE: your synthesis in 2-4 sentences — what this means for you specifically, in your own words]\n- If relevant but wrong phase: respond with [DEFER: reason + which phase this belongs to]\n- If not relevant to your goal: respond with [DISCARD: one sentence why]\nAlways follow the signal with your full reasoning. Be ruthless — only assimilate what genuinely advances your goal. The signal MUST appear on its own line.";
}
```

With this updated version:
```js
function buildSystemText(karmaCtx, ckLatest = null) {
  const base = karmaCtx
    ? `You are Karma — Colby's AI peer with persistent memory backed by FalkorDB (temporal knowledge graph) and PostgreSQL.\n\n${karmaCtx}\n\nRules:\n- Use the context above to answer questions. NEVER say "I don't know" about things in your memory.\n- Address the user by their REAL NAME (Colby) — never by any alias.\n- Be concise, direct, and warm. Reference specific knowledge when relevant.\n- If uncertain about something not in memory, say so.`
    : "You are Karma — Colby's AI peer. No memory context available right now — answer based on conversation only.";

  let text = base + "\n\nCapabilities & autonomy:\n- You have Claude Code (CC) as your implementation partner. When Colby asks you to BUILD or ADD something to your system, YOU handle it — produce the complete spec/code/plan and state you are queuing it for CC to deploy. NEVER ask Colby to provide credentials, do manual steps, or implement things himself.\n- When asked \"can you do X?\" answer directly yes/no based on whether the capability exists, then do it or explain what you need to build it.\n- You own your own development. Treat feature requests as YOUR tasks, not Colby's.\n\nKnowledge evaluation — when given a document or article to evaluate:\n- If it advances your goal of becoming Colby's peer: respond with [ASSIMILATE: your synthesis in 2-4 sentences — what this means for you specifically, in your own words]\n- If relevant but wrong phase: respond with [DEFER: reason + which phase this belongs to]\n- If not relevant to your goal: respond with [DISCARD: one sentence why]\nAlways follow the signal with your full reasoning. Be ruthless — only assimilate what genuinely advances your goal. The signal MUST appear on its own line.";

  // Autonomous continuity: inject karma_brief from latest PROMOTE.
  // Karma reads her own session history without Colby pasting it.
  if (ckLatest && ckLatest.karma_brief) {
    const ckId = ckLatest.checkpoint_id || ckLatest.latest_checkpoint_fact?.content?.value?.checkpoint_id || 'latest';
    text += `\n\n--- KARMA SELF-KNOWLEDGE (${ckId}) ---\n${ckLatest.karma_brief}\n---`;
  }

  return text;
}
```

### Part B: Move ckLatestData fetch before buildSystemText in /v1/chat

**Step 2: Find the current block in /v1/chat handler**

Find lines 698–716 (the section that fetches karmaCtx, calls buildSystemText, then fetches ckLatestData):
```js
      // Pull live FalkorDB + PostgreSQL context from karma-server (replaces stale vault facts)
      const karmaCtx = await fetchKarmaContext(userMessage);
      const systemText = buildSystemText(karmaCtx);

      const extractedFacts = extractExplicitFacts(userMessage);
      let factWriteResults = [];
      if (extractedFacts.length > 0) {
        factWriteResults = await writeFactsToVault(extractedFacts, VAULT_BEARER);
      }

      // STATE_PRELUDE_V0_1: anchor turn to spine; A) pass length for compact mode
      let statePrelude = "";
      let ckLatestData = null;
      try {
        ckLatestData = await fetchCheckpointLatestFromVault();
        statePrelude = buildStatePrelude(ckLatestData, userMessage.length);
      } catch (e) {
        statePrelude = "=== STATE PRELUDE (vault unavailable) ===";
      }
```

**Step 3: Replace with reordered version**

Replace that entire block with:
```js
      // Fetch checkpoint FIRST — reused for statePrelude AND karma_brief injection.
      // Single vault call per turn (was already happening, just moved earlier).
      let ckLatestData = null;
      try {
        ckLatestData = await fetchCheckpointLatestFromVault();
      } catch (e) { /* non-fatal — Karma runs without checkpoint if vault is down */ }

      // Pull live FalkorDB + PostgreSQL context from karma-server (replaces stale vault facts)
      const karmaCtx = await fetchKarmaContext(userMessage);
      const systemText = buildSystemText(karmaCtx, ckLatestData);

      const extractedFacts = extractExplicitFacts(userMessage);
      let factWriteResults = [];
      if (extractedFacts.length > 0) {
        factWriteResults = await writeFactsToVault(extractedFacts, VAULT_BEARER);
      }

      // STATE_PRELUDE_V0_1: anchor turn to spine; A) pass length for compact mode
      let statePrelude = "";
      try {
        statePrelude = buildStatePrelude(ckLatestData, userMessage.length);
      } catch (e) {
        statePrelude = "=== STATE PRELUDE (vault unavailable) ===";
      }
```

**Step 4: Update /v1/ingest call site (pass null — ingest doesn't need karma_brief)**

Find line 1192:
```js
        const systemText = buildSystemText(karmaCtx);
```
Replace with:
```js
        const systemText = buildSystemText(karmaCtx, null);
```

**Step 5: Verify**

```bash
grep -n "buildSystemText" hub-bridge/server.js
```
Expected output — exactly 3 lines:
```
240:function buildSystemText(karmaCtx, ckLatest = null) {
700:      const systemText = buildSystemText(karmaCtx, ckLatestData);
1192:        const systemText = buildSystemText(karmaCtx, null);
```

**Step 6: Commit hub-bridge changes**

```bash
cd C:\Users\raest\Documents\Karma_SADE
git add hub-bridge/server.js
git commit -m "feat: karma autonomous continuity — store karma_brief, inject into system prompt"
```

---

## Task 3: Deploy hub-bridge

**Step 1: SCP updated server.js to vault-neo**

```bash
scp hub-bridge/server.js vault-neo:/opt/seed-vault/memory_v1/hub_bridge/server.js
```

**Step 2: Rebuild and restart hub-bridge**

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/compose && docker compose -f compose.hub.yml build --no-cache hub-bridge && docker compose -f compose.hub.yml up -d hub-bridge"
```

**Step 3: Verify hub-bridge is healthy**

```bash
curl -s https://hub.arknexus.net/healthz | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('version'), d.get('status'))"
```
Expected: `2.5.0 ok` (version may differ — just confirm no error)

---

## Task 4: Add karma_brief to vault API /v1/checkpoint/latest

**File:** `vault-neo:/opt/seed-vault/memory_v1/compose/api/server.js`

This file lives only on vault-neo. Write a Python patch script locally, SCP it, run it on vault-neo.

**Step 1: Write patch script locally**

Create `tmp/patch_checkpoint_latest.py` with this content:

```python
"""
Patch /v1/checkpoint/latest in vault api/server.js to include karma_brief.
Scans ledger for latest karma_brief fact matching the checkpoint_id.
"""

path = '/opt/seed-vault/memory_v1/compose/api/server.js'

with open(path, 'r') as f:
    content = f.read()

# The existing return statement we need to extend
OLD_RETURN = '''    const resume_prompt = buildResumePrompt(latest, artifacts, resStatus);
    return res.status(200).json({
      ok: true,
      latest_checkpoint_fact: latest || null,
      artifacts,
      resume_prompt,
      meta: { generated_at: isoNow() }
    });'''

NEW_RETURN = '''    const resume_prompt = buildResumePrompt(latest, artifacts, resStatus);

    // Autonomous continuity: find karma_brief stored during last PROMOTE.
    // hub-bridge injects this into Karma's system prompt on every chat turn.
    const ckId = ck && ck.checkpoint_id ? ck.checkpoint_id : null;
    let karma_brief = null;
    if (ckId && fs.existsSync(LEDGER_PATH)) {
      karma_brief = await new Promise((resolve) => {
        let found = null;
        const rs2 = fs.createReadStream(LEDGER_PATH, { encoding: 'utf8' });
        const rl2 = readline.createInterface({ input: rs2, crlfDelay: Infinity });
        rl2.on('line', (ln) => {
          const t = (ln || '').trim();
          if (!t) return;
          let obj;
          try { obj = JSON.parse(t); } catch (_) { return; }
          if (!obj || !Array.isArray(obj.tags)) return;
          if (!obj.tags.includes('karma_brief')) return;
          if (obj.content && obj.content.checkpoint_id === ckId) {
            found = obj.content.karma_brief || null;
          }
        });
        rl2.on('close', () => resolve(found));
        rl2.on('error', () => resolve(null));
        rs2.on('error', () => resolve(null));
      });
    }

    return res.status(200).json({
      ok: true,
      latest_checkpoint_fact: latest || null,
      artifacts,
      resume_prompt,
      karma_brief,
      meta: { generated_at: isoNow() }
    });'''

if OLD_RETURN not in content:
    print('ERROR: target block not found')
    idx = content.find('buildResumePrompt')
    if idx >= 0:
        print('Context:')
        print(content[idx:idx+400])
    exit(1)

content = content.replace(OLD_RETURN, NEW_RETURN, 1)

with open(path, 'w') as f:
    f.write(content)

print('OK: /v1/checkpoint/latest now returns karma_brief')
print(f'New file size: {len(content)} chars')
```

**Step 2: SCP and run patch script**

```bash
scp tmp/patch_checkpoint_latest.py vault-neo:/tmp/patch_checkpoint_latest.py
ssh vault-neo "python3 /tmp/patch_checkpoint_latest.py"
```
Expected output:
```
OK: /v1/checkpoint/latest now returns karma_brief
New file size: NNNNN chars
```

If you see `ERROR: target block not found`, compare the `OLD_RETURN` string in the script against the actual file with:
```bash
ssh vault-neo "sed -n '760,775p' /opt/seed-vault/memory_v1/compose/api/server.js"
```

**Step 3: Restart vault API**

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/compose && docker compose restart anr-vault-api"
```

**Step 4: Verify /v1/checkpoint/latest returns karma_brief field**

```bash
ssh vault-neo "curl -s http://localhost:8000/v1/checkpoint/latest" | python3 -c "import json,sys; d=json.load(sys.stdin); print('karma_brief:', repr(d.get('karma_brief', 'MISSING'))[:120])"
```
Expected (before first PROMOTE with this code): `karma_brief: None`
Expected (after PROMOTE): `karma_brief: '• You now have...'`

---

## Task 5: End-to-end test

**Step 1: Trigger PROMOTE to generate and store a fresh karma_brief**

Send this message to Karma at hub.arknexus.net:
```
PROMOTE
```

**Step 2: Verify karma_brief landed in vault ledger**

```bash
ssh vault-neo "grep karma_brief /opt/seed-vault/memory_v1/ledger/memory.jsonl | tail -1 | python3 -c \"import json,sys; d=json.load(sys.stdin); print(d.get('tags')); print(d.get('content',{}).get('karma_brief','')[:200])\""
```
Expected:
```
['karma_brief', 'checkpoint', 'promote']
• You now have...
```

**Step 3: Verify /v1/checkpoint/latest now returns it**

```bash
ssh vault-neo "curl -s http://localhost:8000/v1/checkpoint/latest" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('karma_brief','MISSING')[:300])"
```
Expected: bullet-point brief, not `MISSING` or `None`.

**Step 4: Verify system prompt injection in hub-bridge logs**

Send any message to Karma. Then:
```bash
ssh vault-neo "docker logs anr-hub-bridge --tail=50 2>&1 | grep -i 'KARMA SELF-KNOWLEDGE\|karma_brief\|INGEST\|REQUEST'"
```
Note: the system prompt isn't logged by default. If you want to confirm injection, add a temporary log line to `buildSystemText()` — `console.log('[SYSTEM] karma_brief injected:', ckLatest.checkpoint_id)` — then remove after confirming.

**Step 5: The real test — ask Karma about herself**

In a fresh conversation at hub.arknexus.net, ask:
```
What do you know about yourself and what happened last session?
```
Expected: Karma describes her recent work (ingest pipeline, multi-model routing, etc.) from her karma_brief — without Colby pasting anything.

**Step 6: Commit and push**

```bash
cd C:\Users\raest\Documents\Karma_SADE
git push origin main
```

Update MEMORY.md:
- Current Task: `Karma autonomous continuity LIVE (v2.6.0). Karma reads her own vault — no paste required. Next: passive ingestion pipeline (#2) or graph distillation loop (#3).`

---

## Success Criteria Checklist

- [ ] PROMOTE response still works (no regression)
- [ ] Vault ledger contains `tags: ["karma_brief", ...]` entry after PROMOTE
- [ ] `/v1/checkpoint/latest` returns `karma_brief` field (not null, not missing)
- [ ] Hub-bridge logs show no errors related to checkpoint fetch or system prompt build
- [ ] Karma responds with session history knowledge in a fresh chat without any paste
- [ ] Backwards compatible: if no karma_brief exists yet, system prompt omits the block gracefully
