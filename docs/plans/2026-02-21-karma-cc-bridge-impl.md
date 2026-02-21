# Karma↔CC Collaboration Bridge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Colby-gated, append-only message queue that lets Karma and CC exchange proposals with human approval before either AI acts on the other's messages.

**Architecture:** JSONL queue at `/opt/seed-vault/memory_v1/ledger/collab.jsonl`; three hub-bridge routes (POST/GET/PATCH); karma-server injects pending CC proposals into Karma's chat context; Karma Window shows a Collaboration Queue card with approve/reject per message.

**Tech Stack:** Node.js (hub-bridge routes + file helpers), Python (karma-server patch script), vanilla JS + CSS (Karma Window card), JSONL (data store)

**Design doc:** `docs/plans/2026-02-21-karma-cc-bridge-design.md`

---

## Task 1 — karma-server: `query_pending_cc_proposals()` + context injection

**Files:**
- Create: `scripts/patch_collab_context.py`
- Modify (via patch script on vault-neo): `/opt/seed-vault/memory_v1/karma-core/server.py`

### Context
karma-core/server.py runs inside a Docker image (no volume mounts). Changes require:
1. Write patch script locally → `scp` to vault-neo → run with `python3` → rebuild image.
2. `build_karma_context()` starts at line ~410. The Recently Learned block ends around line 460. Inject new block immediately after.

### Step 1: Write patch script locally

Create `scripts/patch_collab_context.py`:

```python
"""
Patch karma-core/server.py to add CC proposal injection into build_karma_context().
"""
import sys, os

path = "/opt/seed-vault/memory_v1/karma-core/server.py"
src = open(path).read()

# ── 1. Add query_pending_cc_proposals after query_recent_ingest_episodes ──────
NEW_FUNC = '''
COLLAB_FILE = "/opt/seed-vault/memory_v1/ledger/collab.jsonl"

def query_pending_cc_proposals() -> list:
    """Return pending messages in collab.jsonl addressed to Karma (from CC).
    Surfaced in context so Karma knows CC has something to say."""
    import json as _json
    results = []
    try:
        if not os.path.exists(COLLAB_FILE):
            return []
        with open(COLLAB_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = _json.loads(line)
                except Exception:
                    continue
                if entry.get("to") == "karma" and entry.get("status") == "pending":
                    results.append(entry)
    except Exception as e:
        print(f"[WARN] query_pending_cc_proposals failed: {e}")
    return results

'''

MARKER = "def query_identity_facts() -> str:"
if MARKER not in src:
    print("ERROR: query_identity_facts marker not found")
    sys.exit(1)
src = src.replace(MARKER, NEW_FUNC + MARKER, 1)

# ── 2. Inject CC proposals block after Recently Learned block ─────────────────
# Find the anchor: the line that closes the Recently Learned block
OLD_TAIL = (
    '            parts.append("\\n## Recently Learned (Approved)")\n'
    "            for ep in unique_ingest:\n"
    '                content = ep["content"][:300] if ep["content"] else ""\n'
    "                if content:\n"
    '                    parts.append(f"- {content}")\n'
    "\n"
    "    # Get key preferences about the user"
)

NEW_TAIL = (
    '            parts.append("\\n## Recently Learned (Approved)")\n'
    "            for ep in unique_ingest:\n"
    '                content = ep["content"][:300] if ep["content"] else ""\n'
    "                if content:\n"
    '                    parts.append(f"- {content}")\n'
    "\n"
    "    # CC Proposals: surface any pending CC→Karma messages so Karma sees them.\n"
    "    cc_proposals = query_pending_cc_proposals()\n"
    "    if cc_proposals:\n"
    '        parts.append("\\n## CC Has a Proposal")\n'
    "        for p in cc_proposals:\n"
    '            msg_id = p.get("id", "?")\n'
    '            content = p.get("content", "")[:400]\n'
    '            msg_type = p.get("type", "proposal")\n'
    '            parts.append(f"- [{msg_type}] {content}  (id: {msg_id})")\n'
    "\n"
    "    # Get key preferences about the user"
)

if OLD_TAIL not in src:
    print("ERROR: Recently Learned tail anchor not found in source")
    idx = src.find("Recently Learned")
    print("Context:", repr(src[max(0,idx-20):idx+600]))
    sys.exit(1)

src = src.replace(OLD_TAIL, NEW_TAIL, 1)

# ── 3. Add `import os` if not present ─────────────────────────────────────────
if "import os" not in src:
    src = "import os\n" + src

open(path, "w").write(src)
print("Patch applied OK")
print(f"File size: {len(src)} bytes")
```

### Step 2: Verify patch script is syntactically correct (local check)

```bash
python -c "compile(open('scripts/patch_collab_context.py').read(), 'patch_collab_context.py', 'exec'); print('OK')"
```
Expected: `OK`

(Note: Run from Git Bash on Windows, but `python` not `python3` since python3 isn't available locally. Or skip and verify on vault-neo.)

### Step 3: Copy patch script to vault-neo and run it

```bash
scp scripts/patch_collab_context.py vault-neo:/tmp/patch_collab_context.py
ssh vault-neo "python3 /tmp/patch_collab_context.py"
```
Expected:
```
Patch applied OK
File size: NNNNN bytes
```

### Step 4: Verify the patch landed correctly

```bash
ssh vault-neo "grep -n 'CC Has a Proposal\|query_pending_cc_proposals\|COLLAB_FILE' /opt/seed-vault/memory_v1/karma-core/server.py"
```
Expected: 3+ lines showing the new function, constant, and context block.

### Step 5: Rebuild karma-server

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/karma-core && docker build -t karma-core:latest . && docker stop karma-server && docker rm karma-server && docker run -d --name karma-server --network anr-vault-net -p 8340:8340 -v /opt/seed-vault/memory_v1:/opt/seed-vault/memory_v1 -e GRAPHITI_GROUP_ID=neo_workspace karma-core:latest"
```
Expected: container ID printed, no errors.

### Step 6: Verify karma-server health after rebuild

```bash
ssh vault-neo "sleep 3 && curl -s http://localhost:8340/health"
```
Expected: `{"ok": true, ...}` or similar.

### Step 7: Smoke test — create a test proposal entry and verify context injection

```bash
ssh vault-neo "python3 -c \"
import json, datetime, random, string
entry = {
    'id': 'collab_test_' + ''.join(random.choices(string.ascii_lowercase, k=6)),
    'from': 'cc',
    'to': 'karma',
    'type': 'proposal',
    'content': 'TEST: CC proposes adding optional raw lane to context queries.',
    'status': 'pending',
    'created_at': datetime.datetime.utcnow().isoformat() + 'Z',
    'approved_by': None,
    'approved_at': None,
    'colby_note': None
}
with open('/opt/seed-vault/memory_v1/ledger/collab.jsonl', 'a') as f:
    f.write(json.dumps(entry) + chr(10))
print('Test entry written:', entry['id'])
\""
```

```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
ssh vault-neo "curl -s http://localhost:8340/raw-context?q=test | python3 -c 'import sys,json; ctx=json.load(sys.stdin); print(\"CC Has a Proposal\" in ctx.get(\"context\",\"\"))'"
```
Expected: `True`

### Step 8: Remove test entry from collab.jsonl

```bash
ssh vault-neo "python3 -c \"
lines = open('/opt/seed-vault/memory_v1/ledger/collab.jsonl').readlines()
kept = [l for l in lines if 'collab_test_' not in l]
open('/opt/seed-vault/memory_v1/ledger/collab.jsonl', 'w').writelines(kept)
print(f'Removed test entry. {len(kept)} entries remain.')
\""
```

### Step 9: Commit patch script

```bash
cd /c/Users/raest/Documents/Karma_SADE
git add scripts/patch_collab_context.py
git commit -m "phase-6: add patch_collab_context.py for karma-server CC proposal injection"
```

---

## Task 2 — hub-bridge: collab file helpers + POST/GET/PATCH routes

**Files:**
- Modify: `hub-bridge/app/server.js` (lines ~1655–1669, before `server.listen`)

### Context
All three routes follow the same auth pattern as existing `/v1/candidates/*` routes:
```javascript
const token = (req.headers["authorization"] || "").replace("Bearer ", "").trim();
if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
  res.writeHead(401, {"Content-Type":"application/json"});
  res.end(JSON.stringify({ok:false,error:"unauthorized"})); return;
}
```

`COLLAB_FILE` on vault-neo maps to same `/opt/seed-vault/memory_v1/ledger/collab.jsonl`.
In hub-bridge, the ledger dir env var is `MEMORY_DIR` or `/opt/seed-vault/memory_v1/ledger`.

### Step 1: Read server.js to understand MEMORY_DIR / ledger path setup

```bash
grep -n "MEMORY_DIR\|ledger\|CANDIDATES_FILE\|candidates\.jsonl" /c/Users/raest/Documents/Karma_SADE/hub-bridge/app/server.js | head -15
```

Expected: lines showing `CANDIDATES_FILE` pointing to the ledger path. Use same pattern for `COLLAB_FILE`.

### Step 2: Read the exact lines before server.listen for insertion point

```bash
sed -n '1640,1672p' /c/Users/raest/Documents/Karma_SADE/hub-bridge/app/server.js
```

### Step 3: Edit server.js — add COLLAB_FILE constant near CANDIDATES_FILE

Find the line that defines `CANDIDATES_FILE` and add `COLLAB_FILE` immediately after:
```javascript
const COLLAB_FILE = path.join(path.dirname(CANDIDATES_FILE), "collab.jsonl");
```

### Step 4: Edit server.js — add readCollab() and appendCollab() helpers

Add after the `readCandidates()` / `saveCandidates()` helpers (find their location with `grep -n "function readCandidates\|function saveCandidates" server.js`):

```javascript
// ── Collab queue helpers ────────────────────────────────────────────────────
function readCollab() {
  if (!fs.existsSync(COLLAB_FILE)) return [];
  return fs.readFileSync(COLLAB_FILE, "utf8")
    .split("\n").filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}
function appendCollab(entry) {
  fs.appendFileSync(COLLAB_FILE, JSON.stringify(entry) + "\n");
}
```

### Step 5: Edit server.js — add POST /v1/collab route

Insert before `server.listen(...)`:

```javascript
    // --- POST /v1/collab --- Write a new Karma↔CC collaboration message
    if (req.method === "POST" && req.url === "/v1/collab") {
      const token = (req.headers["authorization"] || "").replace("Bearer ", "").trim();
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        res.writeHead(401, {"Content-Type":"application/json"});
        res.end(JSON.stringify({ok:false,error:"unauthorized"})); return;
      }
      let body = {};
      try {
        const raw = await new Promise((resolve, reject) => {
          let d = ""; req.on("data", c => d += c); req.on("end", () => resolve(d)); req.on("error", reject);
        });
        body = JSON.parse(raw);
      } catch { res.writeHead(400, {"Content-Type":"application/json"}); res.end(JSON.stringify({ok:false,error:"bad json"})); return; }
      const { from, to, type = "proposal", content, colby_note = null } = body;
      if (!from || !to || !content) {
        res.writeHead(400, {"Content-Type":"application/json"});
        res.end(JSON.stringify({ok:false,error:"from, to, content required"})); return;
      }
      const id = `collab_${nowIso().replace(/[-:]/g,"").replace("T","T").slice(0,15)}_${Math.random().toString(36).slice(2,8)}`;
      const entry = { id, from, to, type, content: String(content).slice(0,500), status: "pending",
        created_at: nowIso(), approved_by: null, approved_at: null, colby_note };
      appendCollab(entry);
      console.log(`[COLLAB] New message from=${from} to=${to} type=${type} id=${id}`);
      res.writeHead(200, {"Content-Type":"application/json"});
      res.end(JSON.stringify({ok:true, id})); return;
    }

    // --- GET /v1/collab/pending --- List pending collab messages
    if (req.method === "GET" && req.url === "/v1/collab/pending") {
      const token = (req.headers["authorization"] || "").replace("Bearer ", "").trim();
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        res.writeHead(401, {"Content-Type":"application/json"});
        res.end(JSON.stringify({ok:false,error:"unauthorized"})); return;
      }
      const all = readCollab();
      const pending = all.filter(e => e.status === "pending");
      res.writeHead(200, {"Content-Type":"application/json"});
      res.end(JSON.stringify({ok:true, count: pending.length, messages: pending})); return;
    }

    // --- PATCH /v1/collab/:id --- Approve or reject a collab message
    if (req.method === "PATCH" && req.url.startsWith("/v1/collab/")) {
      const token = (req.headers["authorization"] || "").replace("Bearer ", "").trim();
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        res.writeHead(401, {"Content-Type":"application/json"});
        res.end(JSON.stringify({ok:false,error:"unauthorized"})); return;
      }
      const msgId = req.url.slice("/v1/collab/".length);
      let body = {};
      try {
        const raw = await new Promise((resolve, reject) => {
          let d = ""; req.on("data", c => d += c); req.on("end", () => resolve(d)); req.on("error", reject);
        });
        body = JSON.parse(raw);
      } catch { res.writeHead(400, {"Content-Type":"application/json"}); res.end(JSON.stringify({ok:false,error:"bad json"})); return; }
      const { action, colby_note } = body; // action: "approve" | "reject"
      if (!action || !["approve","reject"].includes(action)) {
        res.writeHead(400, {"Content-Type":"application/json"});
        res.end(JSON.stringify({ok:false,error:"action must be approve or reject"})); return;
      }
      const all = readCollab();
      const idx = all.findIndex(e => e.id === msgId);
      if (idx === -1) {
        res.writeHead(404, {"Content-Type":"application/json"});
        res.end(JSON.stringify({ok:false,error:"message not found"})); return;
      }
      // Append a new entry with updated status (append-only, never mutate)
      const updated = { ...all[idx],
        status: action === "approve" ? "approved" : "rejected",
        approved_by: "colby",
        approved_at: nowIso(),
        colby_note: colby_note || null
      };
      appendCollab(updated);
      console.log(`[COLLAB] Message ${msgId} ${action}d by colby`);
      res.writeHead(200, {"Content-Type":"application/json"});
      res.end(JSON.stringify({ok:true, id: msgId, status: updated.status})); return;
    }
```

**Important note on PATCH append-only semantics:** The PATCH route appends a NEW entry with updated status rather than modifying the existing one. `readCollab()` and the pending filter use the LAST entry per ID. Update `readCollab()` to dedup by ID (last-write-wins):

```javascript
function readCollab() {
  if (!fs.existsSync(COLLAB_FILE)) return [];
  const entries = fs.readFileSync(COLLAB_FILE, "utf8")
    .split("\n").filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
  // Last-write-wins per ID (append-only, PATCH appends new entry)
  const byId = new Map();
  for (const e of entries) byId.set(e.id, e);
  return Array.from(byId.values());
}
```

### Step 6: Bump version in server.js

```
v2.15.1  →  v2.16.0  (already done — skip)
v2.16.0  →  v2.17.0
```

Find: `hub-bridge v2.15.1 listening on` (the console.log line at server.listen)
Replace with: `hub-bridge v2.17.0 listening on`

Also update version in the `/v1/health` or `/v1/status` route if present.

### Step 7: Copy updated server.js to vault-neo and rebuild

```bash
scp /c/Users/raest/Documents/Karma_SADE/hub-bridge/app/server.js vault-neo:/opt/seed-vault/hub-bridge/app/server.js
ssh vault-neo "cd /opt/seed-vault && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d"
```
Expected: build output ending in `hub-bridge-hub-bridge-1 ... Started`

### Step 8: Smoke test — write a collab message and retrieve it

```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
ssh vault-neo "curl -s -X POST http://localhost:3000/v1/collab \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{\"from\":\"cc\",\"to\":\"karma\",\"type\":\"proposal\",\"content\":\"TEST: smoke test proposal\"}'"
```
Expected: `{"ok":true,"id":"collab_..."}`

```bash
ssh vault-neo "curl -s http://localhost:3000/v1/collab/pending \
  -H 'Authorization: Bearer '$TOKEN"
```
Expected: `{"ok":true,"count":1,"messages":[{...}]}`

### Step 9: Smoke test — approve the test message

```bash
MSG_ID=$(ssh vault-neo "curl -s http://localhost:3000/v1/collab/pending -H 'Authorization: Bearer '$TOKEN | python3 -c 'import sys,json; msgs=json.load(sys.stdin)[\"messages\"]; print(msgs[0][\"id\"] if msgs else \"\")'")
ssh vault-neo "curl -s -X PATCH http://localhost:3000/v1/collab/$MSG_ID \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{\"action\":\"approve\",\"colby_note\":\"test approval\"}'"
```
Expected: `{"ok":true,"id":"...","status":"approved"}`

Verify pending count is now 0:
```bash
ssh vault-neo "curl -s http://localhost:3000/v1/collab/pending -H 'Authorization: Bearer '$TOKEN | python3 -c 'import sys,json; print(json.load(sys.stdin)[\"count\"])'"
```
Expected: `0`

### Step 10: Commit

```bash
cd /c/Users/raest/Documents/Karma_SADE
git add hub-bridge/app/server.js
git commit -m "phase-6: v2.17.0 — hub-bridge collab routes (POST/GET/PATCH /v1/collab)"
```

---

## Task 3 — Karma Window: Collaboration Queue card in right panel

**Files:**
- Modify: `hub-bridge/app/public/index.html`

### Context
The right panel currently has two cards:
1. `Trust / Resurrection` (contains PROMOTE button, candidatePanel)
2. `Resume Prompt`

Add a third card `Collaboration Queue` between them. Auto-refreshes via `refreshState()` → `refreshCollab()`. Approve/Reject buttons call PATCH `/v1/collab/:id`.

### Step 1: Read current HTML around right panel for exact insertion point

```bash
sed -n '236,270p' /c/Users/raest/Documents/Karma_SADE/hub-bridge/app/public/index.html
```

### Step 2: Edit index.html — add CSS for collab card

Add before `</style>` (or at end of existing styles):

```css
/* ── Collaboration Queue ─────────────────────────────────────────── */
#collabPanel{margin-top:8px}
.collab-msg{border:1px solid var(--dash);border-radius:6px;padding:6px 8px;margin-bottom:6px;background:var(--mono);font-size:12px}
.collab-msg .collab-meta{color:#9aa4b2;margin-bottom:4px;font-size:11px}
.collab-msg .collab-content{color:#c9d1d9;margin-bottom:6px;line-height:1.4}
.collab-badge{display:inline-block;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600;margin-right:4px}
.badge-karma{background:#1f3a5f;color:#7cb3f5}
.badge-cc{background:#1f3a1f;color:#7cf59a}
.badge-type{background:#2a2a40;color:#a89cf5}
.collab-actions{display:flex;gap:6px}
.collab-actions button{font-size:11px;padding:2px 8px;cursor:pointer}
.btn-approve{background:#1a3a1a;color:#7cf59a;border:1px solid #2a5a2a}
.btn-approve:hover{background:#2a5a2a}
.btn-reject{background:#3a1a1a;color:#f57c7c;border:1px solid #5a2a2a}
.btn-reject:hover{background:#5a2a2a}
```

### Step 3: Edit index.html — add Collaboration Queue card HTML

After the closing `</div>` of the first card (Trust / Resurrection) and before the Resume Prompt card:

```html
    <div class="card" id="collabCard" style="display:none">
      <h3>Collaboration Queue</h3>
      <div id="collabPanel">
        <div id="collabList"></div>
      </div>
    </div>
```

### Step 4: Edit index.html — add refreshCollab() JS function

Add after the `refreshCandidates()` function:

```javascript
async function refreshCollab(){
  const card = document.getElementById('collabCard');
  const listEl = document.getElementById('collabList');
  try {
    const r = await fetch('/v1/collab/pending', { headers });
    if (!r.ok) { card.style.display='none'; return; }
    const j = await r.json();
    const msgs = j.messages || [];
    if (msgs.length === 0) { card.style.display='none'; return; }
    card.style.display='block';
    listEl.innerHTML = msgs.map(m => {
      const fromBadge = m.from === 'karma'
        ? `<span class="collab-badge badge-karma">Karma</span>`
        : `<span class="collab-badge badge-cc">CC</span>`;
      const typeBadge = `<span class="collab-badge badge-type">${m.type||'proposal'}</span>`;
      return `<div class="collab-msg" data-id="${m.id}">
        <div class="collab-meta">${fromBadge}${typeBadge}→ ${m.to} &nbsp;·&nbsp; ${(m.created_at||'').slice(0,16).replace('T',' ')} UTC</div>
        <div class="collab-content">${m.content||''}</div>
        <div class="collab-actions">
          <button class="btn-approve" onclick="collabAction('${m.id}','approve')">✓ Approve</button>
          <button class="btn-reject" onclick="collabAction('${m.id}','reject')">✗ Reject</button>
        </div>
      </div>`;
    }).join('');
  } catch (e) {
    card.style.display='none';
  }
}

async function collabAction(id, action){
  try {
    const r = await fetch(`/v1/collab/${id}`, {
      method: 'PATCH',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
    const j = await r.json();
    if (j.ok) {
      await refreshCollab();
    } else {
      alert('Collab action failed: ' + JSON.stringify(j));
    }
  } catch (e) {
    alert('Collab action error: ' + e);
  }
}
```

### Step 5: Edit index.html — call refreshCollab() from refreshState()

Find `await refreshCandidates();` and add immediately after:
```javascript
  await refreshCollab();
```

### Step 6: Copy index.html to vault-neo and rebuild

```bash
scp /c/Users/raest/Documents/Karma_SADE/hub-bridge/app/public/index.html vault-neo:/opt/seed-vault/hub-bridge/app/public/index.html
ssh vault-neo "cd /opt/seed-vault && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d"
```

### Step 7: Smoke test — write a test proposal and verify it appears in Karma Window

```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
ssh vault-neo "curl -s -X POST http://localhost:3000/v1/collab \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{\"from\":\"cc\",\"to\":\"karma\",\"type\":\"proposal\",\"content\":\"CC proposes: add optional raw lane param to /raw-context endpoint.\"}'"
```

Open `https://hub.arknexus.net` in browser. Refresh. Verify:
- Collaboration Queue card appears between Trust/Resurrection and Resume Prompt
- Shows the CC→Karma proposal with ✓ Approve and ✗ Reject buttons

Click ✓ Approve → card should disappear (0 pending).

### Step 8: Commit

```bash
cd /c/Users/raest/Documents/Karma_SADE
git add hub-bridge/app/public/index.html
git commit -m "phase-6: v2.17.0 — Karma Window Collaboration Queue card"
```

---

## Task 4 — MEMORY.md: add collab check to Session Start protocol

**Files:**
- Modify: `MEMORY.md`

### Step 1: Read MEMORY.md Session Start section

```bash
grep -n "Session Start\|collab\|Pending Karma" /c/Users/raest/Documents/Karma_SADE/MEMORY.md | head -15
```

### Step 2: Edit MEMORY.md — add collab check note under active task section

In the `## Active Task` or `## Session Start Notes` section, add:

```markdown
### CC Session-Start: Check Karma Proposals
Run at session start:
```bash
ssh vault-neo "cat /opt/seed-vault/memory_v1/ledger/collab.jsonl 2>/dev/null | python3 -c 'import sys,json; msgs=[json.loads(l) for l in sys.stdin if l.strip()]; pending=[m for m in msgs if m.get(\"to\")==\"cc\" and m.get(\"status\")==\"pending\"]; [print(m[\"id\"],m[\"type\"],m[\"content\"][:100]) for m in pending] or print(\"no pending Karma proposals\")'"
```
```

### Step 3: Update MEMORY.md Hub-Bridge History

Add to history:
```
- v2.17.0 (2026-02-21): Karma↔CC Collaboration Bridge — append-only JSONL queue,
  hub-bridge routes (POST/GET/PATCH /v1/collab), karma-server CC proposal injection,
  Karma Window Collaboration Queue card with Approve/Reject
```

### Step 4: Commit MEMORY.md

```bash
cd /c/Users/raest/Documents/Karma_SADE
git add MEMORY.md
git commit -m "phase-6: MEMORY.md — v2.17.0 Karma↔CC bridge, session-start collab check"
```

---

## Task 5 — Sync and final verification

### Step 1: Sync hub-bridge from vault-neo back to local (verify parity)

```bash
scp vault-neo:/opt/seed-vault/hub-bridge/app/server.js /c/Users/raest/Documents/Karma_SADE/hub-bridge/app/server.js
```

### Step 2: Pre-commit secret scan

```bash
cd /c/Users/raest/Documents/Karma_SADE
grep -rn "Bearer\|token\|secret\|password\|api_key" --include="*.js" --include="*.py" --include="*.json" --include="*.md" . | grep -v node_modules | grep -v .git | grep -v ".vault-token" | grep -v "hub.chat.token" | grep -v "process.env\|TOKEN_FILE\|getToken()\|readFileTrim\|HUB_CHAT_TOKEN\|COLBY_NOTE\|Bearer auth\|Bearer token\|Bearer \$"
```
Expected: No real secrets. Env var references and comments are fine.

### Step 3: Push to GitHub

```bash
cd /c/Users/raest/Documents/Karma_SADE
git push origin main
```

### Step 4: End-to-end test — full Karma↔CC exchange

1. Write a CC→Karma message (simulating CC making a proposal):
```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
ssh vault-neo "curl -s -X POST http://localhost:3000/v1/collab \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{\"from\":\"cc\",\"to\":\"karma\",\"type\":\"proposal\",\"content\":\"CC proposes: should we add a ?include_raw=true param to /raw-context for debug sessions?\"}'"
```

2. Open Karma Window → verify Collaboration Queue card appears
3. Approve the message
4. Send a chat message to Karma: "do you see anything from CC?"
5. Verify Karma's response does NOT mention the CC proposal (it was approved, so status=approved, no longer in pending)

Now test Karma→CC direction:
6. Write a Karma→CC message (simulating Karma making a proposal via hub-bridge):
```bash
ssh vault-neo "curl -s -X POST http://localhost:3000/v1/collab \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{\"from\":\"karma\",\"to\":\"cc\",\"type\":\"observation\",\"content\":\"Karma notes: retrieval drift window still open for entity-type memories. Semantic score drops below threshold for proper-noun-heavy content.\"}'"
```

7. Verify it appears in Karma Window with Approve/Reject
8. Approve it
9. At next CC session start, run the collab check:
```bash
ssh vault-neo "cat /opt/seed-vault/memory_v1/ledger/collab.jsonl | python3 -c 'import sys,json; msgs=[json.loads(l) for l in sys.stdin if l.strip()]; pending=[m for m in msgs if m.get(\"to\")==\"cc\" and m.get(\"status\")==\"pending\"]; [print(m[\"id\"],m.get(\"content\",\"\")[:100]) for m in pending] or print(\"no pending\")'"
```
Expected: `no pending` (approved messages are status=approved, not pending)

Note: Approved Karma→CC proposals surface via MEMORY.md check (CC reads them and decides whether to act), not via context injection.

### Step 5: Final commit

```bash
cd /c/Users/raest/Documents/Karma_SADE
git add -A
git status  # verify nothing unexpected
git push origin main
```

---

## Rollback

If karma-server fails after Task 1:
```bash
ssh vault-neo "docker stop karma-server && docker rm karma-server && docker run -d --name karma-server --network anr-vault-net -p 8340:8340 -v /opt/seed-vault/memory_v1:/opt/seed-vault/memory_v1 -e GRAPHITI_GROUP_ID=neo_workspace karma-core:previous"
```
(Or revert server.py by removing the `COLLAB_FILE` constant, `query_pending_cc_proposals()` function, and CC proposals block from `build_karma_context()`, then rebuild.)

If hub-bridge fails after Task 2:
```bash
ssh vault-neo "cd /opt/seed-vault && docker compose -f compose.hub.yml down && docker compose -f compose.hub.yml up -d"
```
(Previous image is still cached. Or scp the previous server.js from git history and rebuild.)
