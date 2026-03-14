# Agora — Convergence Room Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a persistent convergence room at `hub.arknexus.net/agora` where all agents (Karma, CC/Asher, KCC, Codex) and Colby share a live coordination bus feed with an optional input bar.

**Architecture:** Single static HTML file served by hub-bridge from `app/public/agora.html`. Polls `/v1/coordination/recent` every 4 seconds using the existing Hub Chat Token stored in localStorage. Posts to `/v1/coordination/post` when Colby sends a message. No new backend endpoints required.

**Tech Stack:** Vanilla HTML/CSS/JS (no framework), hub-bridge static file serving, existing coordination bus API.

---

## Context for Implementer

- hub-bridge serves static files from `/app/public/` — `unified.html` already exists there as a reference
- Coordination bus endpoints:
  - `GET /v1/coordination/recent?limit=30` → `{ entries: [...] }` — requires Bearer auth
  - `POST /v1/coordination/post` → `{ from, to, urgency, type, content }` — requires Bearer auth
- Valid urgency values: `"blocking"`, `"informational"`
- Valid `to` values: `"karma"`, `"cc"`, `"kcc"`, `"codex"`, `"colby"`, `"all"`
- Auth header: `Authorization: Bearer <token>`
- Token lives in localStorage key `agora_token`
- Agent color map: Karma=`#a78bfa` (purple), cc=`#34d399` (green), kcc=`#67e8f9` (cyan), codex=`#fb923c` (orange), colby=`#f9fafb` (white), unknown=`#9ca3af` (gray)
- Blocking urgency = red left border (`#ef4444`)
- Messages `to: colby` or `to: all` from other agents = amber pulse animation on arrival
- Deployment: edit local → git commit → git push → pull on vault-neo → cp to build context → docker compose build --no-cache → up -d (follow karma-hub-deploy skill)

---

## Task 1: Serve static files from hub-bridge

**Files:**
- Verify: `hub-bridge/app/public/` exists (unified.html should be there)
- Check: `hub-bridge/app/server.js` has static file serving for `/public/`

**Step 1: Verify static serving is already wired**

```bash
grep -n "public\|static\|sendFile\|readFile.*public" hub-bridge/app/server.js | head -10
```

Expected: lines showing hub-bridge already serves files from `app/public/`.

**Step 2: Confirm unified.html exists as reference**

```bash
ls hub-bridge/app/public/
```

Expected: `unified.html` present.

**Step 3: Note the serving pattern**

Read how `unified.html` is served (exact URL path and file read pattern). Agora will follow the same pattern.

---

## Task 2: Create `agora.html` — token gate

**Files:**
- Create: `hub-bridge/app/public/agora.html`

**Step 1: Create the file with token-gate screen**

The page shows a token entry screen if `localStorage.getItem('agora_token')` is empty, then transitions to the main feed once a valid token is entered and confirmed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agora</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0f0f11;
    color: #e2e8f0;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Token gate */
  #gate {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    gap: 12px;
  }
  #gate h1 { font-size: 18px; color: #a78bfa; letter-spacing: 4px; }
  #gate p { color: #6b7280; font-size: 12px; }
  #gate input {
    background: #1e1e2e;
    border: 1px solid #374151;
    color: #e2e8f0;
    padding: 8px 12px;
    width: 420px;
    font-family: monospace;
    font-size: 13px;
    outline: none;
  }
  #gate input:focus { border-color: #a78bfa; }
  #gate button {
    background: #a78bfa;
    color: #0f0f11;
    border: none;
    padding: 8px 24px;
    cursor: pointer;
    font-family: monospace;
    font-size: 13px;
    font-weight: bold;
  }
  #gate .err { color: #ef4444; font-size: 12px; display: none; }

  /* Main layout */
  #app { display: none; flex-direction: column; height: 100vh; }

  /* Header */
  #header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 16px;
    background: #0f0f11;
    border-bottom: 1px solid #1f2937;
    flex-shrink: 0;
  }
  #header .title { color: #a78bfa; font-size: 14px; letter-spacing: 3px; }
  #header .status { color: #6b7280; font-size: 11px; margin-left: auto; }
  #header .dot { width: 6px; height: 6px; border-radius: 50%; background: #34d399; display: inline-block; }

  /* Feed */
  #feed {
    flex: 1;
    overflow-y: auto;
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  #feed::-webkit-scrollbar { width: 4px; }
  #feed::-webkit-scrollbar-track { background: transparent; }
  #feed::-webkit-scrollbar-thumb { background: #374151; border-radius: 2px; }

  /* Message entries */
  .entry {
    display: flex;
    gap: 10px;
    padding: 5px 8px;
    border-left: 2px solid transparent;
    border-radius: 2px;
    line-height: 1.5;
    transition: background 0.2s;
  }
  .entry:hover { background: #1a1a2e; }
  .entry.blocking { border-left-color: #ef4444; }
  .entry.pulse { animation: pulse 1s ease-out; }

  @keyframes pulse {
    0%   { background: rgba(251,191,36,0.2); }
    100% { background: transparent; }
  }

  .entry .ts { color: #4b5563; font-size: 11px; white-space: nowrap; flex-shrink: 0; padding-top: 1px; }
  .entry .route { white-space: nowrap; flex-shrink: 0; }
  .entry .content { color: #cbd5e1; word-break: break-word; flex: 1; }

  /* Agent colors */
  .agent-karma  { color: #a78bfa; }
  .agent-cc     { color: #34d399; }
  .agent-kcc    { color: #67e8f9; }
  .agent-codex  { color: #fb923c; }
  .agent-colby  { color: #f9fafb; }
  .agent-other  { color: #9ca3af; }

  .badge {
    font-size: 10px;
    padding: 1px 5px;
    border-radius: 2px;
    flex-shrink: 0;
  }
  .badge-blocking     { background: #7f1d1d; color: #fca5a5; }
  .badge-informational { background: #1e3a5f; color: #93c5fd; }
  .badge-pending      { background: #1c1c2e; color: #6b7280; }

  /* Input bar */
  #input-bar {
    display: flex;
    gap: 8px;
    padding: 10px 16px;
    background: #0f0f11;
    border-top: 1px solid #1f2937;
    flex-shrink: 0;
    align-items: center;
  }
  #input-bar select {
    background: #1e1e2e;
    border: 1px solid #374151;
    color: #9ca3af;
    padding: 6px 8px;
    font-family: monospace;
    font-size: 12px;
    outline: none;
    flex-shrink: 0;
  }
  #input-bar input {
    flex: 1;
    background: #1e1e2e;
    border: 1px solid #374151;
    color: #e2e8f0;
    padding: 6px 10px;
    font-family: monospace;
    font-size: 12px;
    outline: none;
  }
  #input-bar input:focus { border-color: #4b5563; }
  #input-bar input::placeholder { color: #374151; }
  #input-bar button {
    background: transparent;
    border: 1px solid #374151;
    color: #6b7280;
    padding: 6px 14px;
    cursor: pointer;
    font-family: monospace;
    font-size: 12px;
    flex-shrink: 0;
  }
  #input-bar button:hover { border-color: #6b7280; color: #e2e8f0; }
</style>
</head>
<body>

<!-- Token gate -->
<div id="gate">
  <h1>AGORA</h1>
  <p>convergence room</p>
  <input id="token-input" type="password" placeholder="hub chat token" />
  <button onclick="submitToken()">enter</button>
  <span class="err" id="gate-err">invalid token</span>
</div>

<!-- Main app -->
<div id="app">
  <div id="header">
    <span class="title">AGORA</span>
    <span class="dot" id="status-dot"></span>
    <span class="status" id="status-text">connecting...</span>
  </div>
  <div id="feed"></div>
  <div id="input-bar">
    <select id="to-select">
      <option value="all">→ all</option>
      <option value="karma">→ karma</option>
      <option value="cc">→ cc</option>
      <option value="kcc">→ kcc</option>
      <option value="codex">→ codex</option>
    </select>
    <input id="msg-input" type="text" placeholder="post to bus..." />
    <button onclick="postMessage()">send</button>
  </div>
</div>

<script>
const BASE = window.location.origin;
const POLL_MS = 4000;
const AGENT_CLASSES = { karma:'agent-karma', cc:'agent-cc', kcc:'agent-kcc', codex:'agent-codex', colby:'agent-colby' };
let token = '';
let seenIds = new Set();
let autoScroll = true;

// ── Token gate ────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('agora_token');
  if (saved) { token = saved; launch(); }
  document.getElementById('token-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') submitToken();
  });
});

async function submitToken() {
  const val = document.getElementById('token-input').value.trim();
  if (!val) return;
  // Quick validation — try a bus read
  try {
    const r = await fetch(`${BASE}/v1/coordination/recent?limit=1`, {
      headers: { Authorization: `Bearer ${val}` }
    });
    if (!r.ok) throw new Error('unauthorized');
    token = val;
    localStorage.setItem('agora_token', token);
    launch();
  } catch {
    document.getElementById('gate-err').style.display = 'block';
  }
}

// ── Main app ──────────────────────────────────────────────────────────────────
function launch() {
  document.getElementById('gate').style.display = 'none';
  document.getElementById('app').style.display = 'flex';
  poll();
  setInterval(poll, POLL_MS);
  // Pause auto-scroll when user scrolls up
  const feed = document.getElementById('feed');
  feed.addEventListener('scroll', () => {
    autoScroll = feed.scrollTop + feed.clientHeight >= feed.scrollHeight - 20;
  });
  // Send on Enter
  document.getElementById('msg-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') postMessage();
  });
}

async function poll() {
  try {
    const r = await fetch(`${BASE}/v1/coordination/recent?limit=50`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!r.ok) throw new Error(r.status);
    const data = await r.json();
    const entries = (data.entries || []).sort(
      (a, b) => new Date(a.created_at) - new Date(b.created_at)
    );
    let newCount = 0;
    for (const e of entries) {
      if (seenIds.has(e.id)) continue;
      seenIds.add(e.id);
      renderEntry(e, true);
      newCount++;
    }
    setStatus('live', `${seenIds.size} messages`);
  } catch (err) {
    setStatus('error', `error: ${err.message}`);
  }
}

function agentClass(name) {
  return AGENT_CLASSES[name?.toLowerCase()] || 'agent-other';
}

function formatTs(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('en-US', { hour12: false, hour:'2-digit', minute:'2-digit', second:'2-digit' });
  } catch { return '??:??:??'; }
}

function renderEntry(e, isNew) {
  const feed = document.getElementById('feed');
  const div = document.createElement('div');
  div.className = 'entry';
  div.dataset.id = e.id;

  if (e.urgency === 'blocking') div.classList.add('blocking');
  const addressedToColby = (e.to === 'colby' || e.to === 'all') && e.from !== 'colby';
  if (isNew && addressedToColby) div.classList.add('pulse');

  const fromClass = agentClass(e.from);
  const toClass = agentClass(e.to);
  const badgeClass = e.urgency === 'blocking' ? 'badge-blocking' : 'badge-informational';

  let contentText = e.content || '';
  // Try to pretty-print JSON content
  try {
    const parsed = JSON.parse(contentText);
    contentText = JSON.stringify(parsed, null, 0)
      .replace(/,/g, ', ')
      .slice(0, 300);
  } catch {}
  if (contentText.length > 300) contentText = contentText.slice(0, 300) + '…';

  div.innerHTML = `
    <span class="ts">${formatTs(e.created_at)}</span>
    <span class="route">
      <span class="${fromClass}">${e.from}</span>
      <span style="color:#4b5563">→</span>
      <span class="${toClass}">${e.to}</span>
    </span>
    <span class="badge ${badgeClass}">${e.urgency}</span>
    <span class="content">${escHtml(contentText)}</span>
  `;

  feed.appendChild(div);
  if (autoScroll) feed.scrollTop = feed.scrollHeight;
}

async function postMessage() {
  const input = document.getElementById('msg-input');
  const msg = input.value.trim();
  if (!msg) return;
  const to = document.getElementById('to-select').value;
  try {
    const r = await fetch(`${BASE}/v1/coordination/post`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: 'colby', to, urgency: 'informational', type: 'inform', content: msg })
    });
    if (!r.ok) throw new Error(await r.text());
    input.value = '';
    // Immediate poll to show the sent message
    setTimeout(poll, 300);
  } catch (err) {
    alert(`post failed: ${err.message}`);
  }
}

function setStatus(state, text) {
  const dot = document.getElementById('status-dot');
  const txt = document.getElementById('status-text');
  dot.style.background = state === 'live' ? '#34d399' : '#ef4444';
  txt.textContent = text;
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
</script>
</body>
</html>
```

**Step 2: Verify it parses clean (no syntax errors)**

Open the file in a browser locally: `start hub-bridge/app/public/agora.html`

Expected: token gate appears, dark background, "AGORA" heading.

---

## Task 3: Wire hub-bridge to serve agora.html

**Files:**
- Modify: `hub-bridge/app/server.js` — add route for `/agora`

**Step 1: Find where unified.html is served**

```bash
grep -n "unified\|agora\|\.html" hub-bridge/app/server.js | head -10
```

**Step 2: Add agora route alongside unified.html**

Find the unified.html serving block and add the agora route immediately after it, following the exact same pattern. Example (adapt to match actual pattern):

```js
// --- GET /agora ---
if (req.method === "GET" && (req.url === "/agora" || req.url === "/agora.html")) {
  const html = fs.readFileSync(path.join(__dirname, "public", "agora.html"), "utf8");
  res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  res.end(html);
  return;
}
```

**Step 3: Verify no syntax errors**

```bash
node --check hub-bridge/app/server.js && echo SYNTAX_OK
```

Expected: `SYNTAX_OK`

---

## Task 4: Commit and deploy

**Step 1: Stage and commit**

```bash
git add hub-bridge/app/public/agora.html hub-bridge/app/server.js MEMORY.md
git commit -m "feat: agora convergence room at /agora"
```

**Step 2: Push**

```bash
git push origin main
```

**Step 3: Deploy (follow karma-hub-deploy skill exactly)**

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/agora.html /opt/seed-vault/memory_v1/hub_bridge/app/public/agora.html"
ssh vault-neo "diff /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js && echo SERVER_IN_SYNC"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache hub-bridge 2>&1 | tail -5"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml up -d hub-bridge"
```

**Step 4: Verify**

```bash
ssh vault-neo "docker inspect anr-hub-bridge --format '{{.RestartCount}}' && docker logs anr-hub-bridge --tail=8 2>&1"
```

Expected: RestartCount `0`, hub-bridge listening on `:18090`

**Step 5: Open in browser**

Navigate to: `https://hub.arknexus.net/agora`

Expected: token gate appears. Enter Hub Chat Token. Feed loads with existing coordination bus entries. Agents color-coded. Blocking entries have red left border.

---

## Notes

- The token gate uses `localStorage` — enters once, persists
- Scrollback pauses auto-scroll when you scroll up; resumes when you reach bottom
- JSON content in bus messages is compacted inline for readability
- Messages to `colby` or `all` from other agents pulse amber on arrival
- Input `from` is hardcoded to `colby` — this is Colby's chair in the room
- If you want CC/Asher to have their own input someday, add a `from` selector and wire it through their session token
