# Karma Ingest Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the pipeline that lets Karma evaluate raw documents from OneDrive/Karma/Inbox, write her own synthesis to FalkorDB, and process a backlog of PDFs autonomously.

**Architecture:** Folder watcher on Windows monitors OneDrive/Karma/Inbox → POSTs PDFs to hub-bridge /v1/ingest → hub-bridge extracts text, sends to Karma for evaluation → Karma responds with [ASSIMILATE/DEFER/DISCARD] signal → hub-bridge writes Karma's synthesis to FalkorDB via karma-server /write-primitive.

**Tech Stack:** Node.js ESM (hub-bridge), Python/FastAPI (karma-server), FalkorDB via Graphiti, pdf-parse (CJS, requires createRequire), PowerShell FileSystemWatcher (folder watcher)

**Design doc:** `docs/plans/2026-02-21-karma-ingest-pipeline-design.md`

---

## Known Pitfalls (read before starting)

- **karma-server has no volume mounts** — editing source on host has no effect until full rebuild: `docker build -t karma-core:latest . && docker stop karma-server && docker rm karma-server && docker run -d ...` (see CLAUDE.md Known Pitfalls for full run command with env vars)
- **hub-bridge compose build caches COPY layer** — always use `--no-cache`: `docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d`
- **hub-bridge is ESM** — `pdf-parse` is CJS. Import via: `import { createRequire } from 'module'; const require = createRequire(import.meta.url); const pdfParse = require('pdf-parse');`
- **FalkorDB graph is `neo_workspace`** — NOT `karma`
- **All containers on `anr-vault-net`** — hub-bridge reaches karma-server at `http://karma-server:8340`
- **Bearer token for smoke tests:** `TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)`

---

## Task 1: Add `/write-primitive` to karma-server

**Files:**
- Modify: `/opt/seed-vault/memory_v1/karma-core/server.py` (via scp from local)
- Read first: `ssh vault-neo "cat /opt/seed-vault/memory_v1/karma-core/server.py"` to get current state

**Step 1: Read current server.py from vault-neo**
```bash
ssh vault-neo "cat /opt/seed-vault/memory_v1/karma-core/server.py" > /tmp/karma-server-current.py
```
Read the file to find: where to insert the new endpoint, what Graphiti client is available, how existing episodic writes work.

**Step 2: Write the new endpoint**

Find the `@app.get("/raw-context")` endpoint that was added in a previous session. Insert the new endpoint immediately after it:

```python
@app.post("/write-primitive")
async def write_primitive(request: Request):
    """Write Karma's synthesized insight to FalkorDB as an Episodic node."""
    try:
        body = await request.json()
        content = body.get("content", "").strip()
        verdict = body.get("verdict", "assimilate")
        source_file = body.get("source_file", "unknown")
        topic = body.get("topic", "")

        if not content:
            return JSONResponse({"ok": False, "error": "content required"}, status_code=400)

        # Build episode text for Graphiti ingestion
        episode_text = f"[karma-ingest][{verdict}] Source: {source_file}\nTopic: {topic}\nKarma's synthesis: {content}"

        # Use existing Graphiti client to add episode
        await graphiti.add_episode(
            name=f"karma_primitive_{int(time.time())}",
            episode_body=episode_text,
            source_description=f"karma-ingest from {source_file}",
            reference_time=datetime.now(),
        )

        return JSONResponse({"ok": True, "verdict": verdict, "source": source_file})
    except Exception as e:
        print(f"[ERROR] /write-primitive failed: {e}")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
```

**Note:** Check how `graphiti` is instantiated in the existing code and what method it uses for adding episodes — it may be `add_episode`, `add_episode_async`, or similar. Adapt to match existing pattern exactly.

**Step 3: Ensure `time` and `datetime` are imported**

Check top of server.py for `import time` and `from datetime import datetime`. Add if missing.

**Step 4: Copy updated server.py to vault-neo and rebuild**
```bash
scp /tmp/karma-server-updated.py vault-neo:/opt/seed-vault/memory_v1/karma-core/server.py

# Get current karma-server run command (preserve all env vars)
ssh vault-neo "docker inspect karma-server --format '{{json .Config}}'" | python3 -c "
import sys, json
c = json.load(sys.stdin)
envs = ' '.join([f'-e {e}' for e in c['Env'] if not e.startswith('PATH=') and not e.startswith('PYTHON')])
print(f'Env vars: {envs[:200]}')
"

# Rebuild and restart
ssh vault-neo "cd /opt/seed-vault/memory_v1/karma-core && docker build -t karma-core:latest . 2>&1 | tail -5"
ssh vault-neo "docker stop karma-server && docker rm karma-server"
# Run with same env vars as before (see CLAUDE.md for full command)
```

**Step 5: Smoke test**
```bash
ssh vault-neo "curl -s -X POST http://172.18.0.8:8340/write-primitive \
  -H 'Content-Type: application/json' \
  -d '{\"content\":\"Test primitive — ignore\",\"verdict\":\"discard\",\"source_file\":\"test\"}'"
```
Expected: `{"ok": true, "verdict": "discard", "source": "test"}`

**Step 6: Verify in FalkorDB**
```bash
ssh vault-neo "docker exec karma-server python3 -c \"
import falkordb
r = falkordb.FalkorDB(host='falkordb', port=6379)
g = r.select_graph('neo_workspace')
result = g.query('MATCH (e:Episodic) WHERE e.content CONTAINS \\\"karma-ingest\\\" RETURN e.content ORDER BY e.created_at DESC LIMIT 1')
for row in result.result_set:
    print(row[0][:200])
\""
```

**Step 7: Commit the updated server.py locally**
```bash
# Copy from vault-neo back to local repo for tracking
scp vault-neo:/opt/seed-vault/memory_v1/karma-core/server.py /tmp/karma-server-post-primitive.py
# (Note: karma-core source is not in this repo — this is for reference only)
```

---

## Task 2: Add PDF extraction to hub-bridge

**Files:**
- Modify: `hub-bridge/package.json` — add `pdf-parse`
- Modify: `hub-bridge/server.js` — add `extractPdfText()` function

**Step 1: Add pdf-parse to package.json**

Read `hub-bridge/package.json`. Update dependencies:
```json
{
  "name": "anr-hub-bridge",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "openai": "^4.0.0",
    "pdf-parse": "^1.1.1"
  }
}
```

**Step 2: Add CJS import shim at top of server.js**

After the existing imports (find the `import` block at top of server.js), add:
```js
// CJS interop for pdf-parse (CommonJS module in ESM context)
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const pdfParse = require('pdf-parse');
```

**Step 3: Add extractPdfText() function**

After `fetchKarmaContext()` function, add:
```js
/**
 * Extract plain text from a PDF buffer.
 * Returns cleaned text string, or null on failure.
 */
async function extractPdfText(buffer) {
  try {
    const data = await pdfParse(buffer);
    // Basic cleanup: collapse whitespace, remove obvious noise
    return data.text
      .replace(/\n{3,}/g, '\n\n')
      .replace(/[ \t]{2,}/g, ' ')
      .trim();
  } catch (err) {
    console.error('[PDF] extraction failed:', err.message);
    return null;
  }
}
```

**Step 4: Smoke test extraction locally (before deploy)**

Create a test script:
```js
// /tmp/test-pdf-extract.mjs
import { createRequire } from 'module';
import { readFileSync } from 'fs';
const require = createRequire(import.meta.url);
const pdfParse = require('pdf-parse');

const buf = readFileSync('C:/Users/raest/OneDrive/Karma/Inbox/ForgetMCP.PDF');
const data = await pdfParse(buf);
console.log('Pages:', data.numpages);
console.log('Chars:', data.text.length);
console.log('Preview:', data.text.slice(0, 500));
```
Run: `node /tmp/test-pdf-extract.mjs`
Expected: page count, char count, readable text preview (not binary garbage)

---

## Task 3: Update hub-bridge system prompt

**Files:**
- Modify: `hub-bridge/server.js` — extend systemText

**Step 1: Find the systemText block**

Search for `You are Karma — Colby's AI peer` in server.js. Find the template literal that builds systemText when karmaCtx is available.

**Step 2: Add signal format instructions**

Append to the Rules section (after the existing 4 rules, before the closing backtick):
```
\n\nKnowledge evaluation — when given a document or article to evaluate:
- If it advances your goal of becoming Colby's peer: respond with [ASSIMILATE: your synthesis in 2-4 sentences — what this means for you specifically, in your own words]
- If relevant but wrong phase: respond with [DEFER: reason + which phase this belongs to]
- If not relevant to your goal: respond with [DISCARD: one sentence why]
Always follow the signal with your full reasoning. Be ruthless — only assimilate what genuinely advances your goal. The signal MUST be on its own line.
```

**Step 3: Verify the signal is on its own line in Karma's responses**

This is important for regex detection in Task 4. The instruction says "MUST be on its own line" so the regex can reliably find it.

---

## Task 4: ASSIMILATE/DEFER/DISCARD signal detection in /v1/chat

**Files:**
- Modify: `hub-bridge/server.js` — add signal detection after LLM response

**Step 1: Add signal detection constants**

Near the top of server.js (with other constants):
```js
const SIGNAL_REGEX = /^\[(ASSIMILATE|DEFER|DISCARD):\s*(.+?)\]$/m;
const WRITE_PRIMITIVE_URL = process.env.WRITE_PRIMITIVE_URL || 'http://karma-server:8340/write-primitive';
```

**Step 2: Add writeKarmaPrimitive() function**

After `extractPdfText()`:
```js
/**
 * Write Karma's synthesized insight to FalkorDB.
 * Called when Karma signals ASSIMILATE or DEFER in her response.
 */
async function writeKarmaPrimitive({ content, verdict, source_file = 'chat', topic = '' }) {
  try {
    const r = await fetch(WRITE_PRIMITIVE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, verdict, source_file, topic }),
      signal: AbortSignal.timeout(5000),
    });
    const body = await r.json();
    return body.ok ? body : null;
  } catch (err) {
    console.error('[INGEST] write-primitive failed:', err.message);
    return null;
  }
}
```

**Step 3: Add signal detection after LLM response in /v1/chat handler**

Find where `assistantText` is extracted from the completion response. After that line, add:
```js
// Detect ASSIMILATE/DEFER/DISCARD signals from Karma
let ingestResult = null;
const signalMatch = assistantText.match(SIGNAL_REGEX);
if (signalMatch) {
  const [, verdict, synthesis] = signalMatch;
  const v = verdict.toLowerCase();
  if (v === 'assimilate' || v === 'defer') {
    ingestResult = await writeKarmaPrimitive({
      content: synthesis.trim(),
      verdict: v,
      source_file: req.body?.source_file || 'chat',
      topic: req.body?.topic || '',
    });
  }
  console.log(`[INGEST] signal=${verdict} ingest=${ingestResult?.ok ? 'ok' : 'skipped'}`);
}
```

**Step 4: Add to telemetry**

Find where `debug_karma_ctx` is added to the response/vault record. Add alongside it:
```js
debug_ingest: signalMatch ? signalMatch[1].toLowerCase() : 'none',
```

**Step 5: Smoke test signal detection**

After deploying (Task 7), send a test message:
```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && \
curl -s -X POST http://localhost:18090/v1/chat \
  -H \"Authorization: Bearer \$TOKEN\" \
  -H 'Content-Type: application/json' \
  -d '{\"message\": \"Please evaluate this: Semantic caching reduces LLM inference cost by reusing responses for semantically similar queries. Respond with the appropriate signal.\"}'"
```
Expected: Response contains `[ASSIMILATE:` or `[DISCARD:` signal, `debug_ingest` in response shows the verdict.

---

## Task 5: hub-bridge /v1/ingest endpoint

**Files:**
- Modify: `hub-bridge/server.js` — add /v1/ingest route

**Step 1: Add multipart body parsing**

hub-bridge currently has no multipart support. Use Node.js built-in approach — read raw body, detect boundary, or use a simple approach: accept JSON with base64-encoded file content. This avoids adding a multipart library.

Add `/v1/ingest` after the `/v1/chat` route:

```js
// POST /v1/ingest — ingest a document for Karma to evaluate
// Body: { file_b64: "<base64 PDF>", filename: "foo.pdf", hint?: "topic context" }
app.post('/v1/ingest', bearerAuth, async (req, res) => {
  try {
    const { file_b64, filename = 'unknown.pdf', hint = '' } = req.body;
    if (!file_b64) return json(res, 400, { ok: false, error: 'file_b64 required' });

    const buffer = Buffer.from(file_b64, 'base64');
    const rawText = await extractPdfText(buffer);
    if (!rawText) return json(res, 422, { ok: false, error: 'pdf_extraction_failed' });

    // Chunk if large (Karma evaluates in passes)
    const CHUNK_SIZE = 6000;
    const chunks = [];
    for (let i = 0; i < rawText.length; i += CHUNK_SIZE) {
      chunks.push(rawText.slice(i, i + CHUNK_SIZE));
    }

    const results = [];
    for (let i = 0; i < chunks.length; i++) {
      const prompt = chunks.length > 1
        ? `Document: ${filename} (part ${i+1}/${chunks.length})\nHint: ${hint}\n\n${chunks[i]}\n\nEvaluate this content for your development.`
        : `Document: ${filename}\nHint: ${hint}\n\n${chunks[i]}\n\nEvaluate this content for your development.`;

      // Route through /v1/chat logic internally
      // (simplified: direct OpenAI call with same system prompt)
      const karmaCtx = await fetchKarmaContext(hint || filename);
      const systemText = buildSystemText(karmaCtx); // refactor systemText build into function

      const completion = await openai.chat.completions.create({
        model: env.MODEL_DEFAULT,
        messages: [
          { role: 'system', content: systemText },
          { role: 'user', content: prompt },
        ],
        max_completion_tokens: 1000,
      });

      const responseText = completion.choices[0]?.message?.content || '';
      const signalMatch = responseText.match(SIGNAL_REGEX);

      let ingestResult = null;
      if (signalMatch) {
        const [, verdict, synthesis] = signalMatch;
        const v = verdict.toLowerCase();
        if (v === 'assimilate' || v === 'defer') {
          ingestResult = await writeKarmaPrimitive({
            content: synthesis.trim(),
            verdict: v,
            source_file: filename,
            topic: hint,
          });
        }
      }

      results.push({
        chunk: i + 1,
        signal: signalMatch ? signalMatch[1] : 'none',
        synthesis: signalMatch ? signalMatch[2]?.slice(0, 200) : null,
        stored: !!ingestResult?.ok,
      });
    }

    return json(res, 200, { ok: true, filename, chunks: chunks.length, results });
  } catch (err) {
    console.error('[INGEST]', err);
    return json(res, 500, { ok: false, error: err.message });
  }
});
```

**Note on `buildSystemText` refactor:** The systemText construction in /v1/chat is currently inline. Extract it to a function `buildSystemText(karmaCtx)` so /v1/ingest can reuse it. This is required before /v1/ingest can work.

**Step 2: Smoke test /v1/ingest**
```bash
# Encode a small PDF and test
python3 -c "
import base64
with open('C:/Users/raest/OneDrive/Karma/Inbox/ForgetMCP.PDF', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
print(b64[:100])
" > /tmp/b64_test.txt

# Then in a proper test script...
```

---

## Task 6: PowerShell folder watcher

**Files:**
- Create: `scripts/karma-inbox-watcher.ps1`

**Step 1: Write the watcher script**

```powershell
# karma-inbox-watcher.ps1
# Watches OneDrive/Karma/Inbox for new PDF files and sends them to Karma for evaluation.
# Run as: pwsh -File karma-inbox-watcher.ps1
# Or install as scheduled task: see bottom of this file.

param(
    [string]$InboxPath = "$env:USERPROFILE\OneDrive\Karma\Inbox",
    [string]$ProcessingPath = "$env:USERPROFILE\OneDrive\Karma\Processing",
    [string]$DonePath = "$env:USERPROFILE\OneDrive\Karma\Done",
    [string]$HubUrl = "https://hub.arknexus.net/v1/ingest",
    [string]$TokenFile = "$env:USERPROFILE\Documents\Karma_SADE\chrome-extension\.vault-token"
)

$token = Get-Content $TokenFile -Raw | ForEach-Object { $_.Trim() }

function Send-ToKarma {
    param([string]$FilePath)

    $filename = Split-Path $FilePath -Leaf
    $processingFile = Join-Path $ProcessingPath $filename

    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Processing: $filename"

    # Move to Processing
    Move-Item $FilePath $processingFile

    try {
        # Encode as base64
        $bytes = [System.IO.File]::ReadAllBytes($processingFile)
        $b64 = [Convert]::ToBase64String($bytes)

        # Build hint from filename (strip extension, replace dashes/underscores)
        $hint = [System.IO.Path]::GetFileNameWithoutExtension($filename) -replace '[-_]', ' '

        # POST to hub-bridge
        $body = @{
            file_b64 = $b64
            filename = $filename
            hint = $hint
        } | ConvertTo-Json -Depth 2

        $response = Invoke-RestMethod `
            -Uri $HubUrl `
            -Method POST `
            -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } `
            -Body $body `
            -TimeoutSec 120

        # Write verdict sidecar
        $verdictFile = Join-Path $DonePath "$filename.verdict.txt"
        $verdictText = @"
file: $filename
processed_at: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')
chunks: $($response.chunks)
results:
$($response.results | ForEach-Object { "  chunk $($_.chunk): $($_.signal) — $($_.synthesis)" } | Out-String)
"@
        $verdictText | Set-Content $verdictFile

        # Move to Done
        Move-Item $processingFile (Join-Path $DonePath $filename)
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Done: $filename ($($response.chunks) chunks)"

    } catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ERROR: $filename — $_"
        # Move back to Inbox for retry
        Move-Item $processingFile $FilePath -ErrorAction SilentlyContinue
        "$_" | Set-Content (Join-Path $InboxPath "$filename.error.txt")
    }
}

# Process any files already in Inbox at startup
Get-ChildItem $InboxPath -File | Where-Object { $_.Extension -in '.pdf','.PDF','.txt','.md' } | ForEach-Object {
    Send-ToKarma $_.FullName
}

# Set up FileSystemWatcher for new files
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $InboxPath
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $ext = [System.IO.Path]::GetExtension($path).ToLower()
    if ($ext -in @('.pdf', '.txt', '.md')) {
        Start-Sleep -Seconds 2  # Wait for file to finish writing
        Send-ToKarma $path
    }
}

Register-ObjectEvent $watcher Created -Action $action | Out-Null

Write-Host "Karma inbox watcher started. Watching: $InboxPath"
Write-Host "Press Ctrl+C to stop."

# Keep running
while ($true) { Start-Sleep -Seconds 10 }
```

**Step 2: Test manually**
```powershell
# Run directly to test
pwsh -File C:\Users\raest\Documents\Karma_SADE\scripts\karma-inbox-watcher.ps1
# Then drop a PDF into OneDrive/Karma/Inbox and watch the output
```

**Step 3: Commit**
```bash
git add scripts/karma-inbox-watcher.ps1
git commit -m "feat: PowerShell folder watcher for Karma/Inbox"
```

---

## Task 7: Build, deploy, end-to-end test

**Step 1: Install pdf-parse in hub-bridge Docker image**

The Dockerfile must run `npm install` with the updated package.json. Since pdf-parse is in package.json, the `--no-cache` build picks it up automatically.

```bash
scp hub-bridge/server.js vault-neo:/opt/seed-vault/memory_v1/hub_bridge/app/server.js
scp hub-bridge/package.json vault-neo:/opt/seed-vault/memory_v1/hub_bridge/app/package.json

ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && \
  docker compose -f compose.hub.yml build --no-cache 2>&1 | tail -10 && \
  docker compose -f compose.hub.yml up -d 2>&1 | tail -3"
```

**Step 2: Verify hub-bridge started**
```bash
ssh vault-neo "docker logs anr-hub-bridge --tail=5"
```
Expected: `hub-bridge v2.5.0 listening on :18090`

**Step 3: End-to-end test with ForgetMCP.PDF**
```bash
# Manually copy ForgetMCP.PDF to Karma/Inbox and run the watcher once
# OR test /v1/ingest directly:
python3 << 'EOF'
import base64, json, urllib.request

with open(r'C:\Users\raest\OneDrive\Karma\Inbox\ForgetMCP.PDF', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

payload = json.dumps({"file_b64": b64, "filename": "ForgetMCP.PDF", "hint": "MCP protocol relevance for Karma"}).encode()

# Read token
with open(r'C:\Users\raest\Documents\Karma_SADE\chrome-extension\.vault-token') as f:
    token = f.read().strip()

req = urllib.request.Request('https://hub.arknexus.net/v1/ingest',
    data=payload,
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req, timeout=120)
print(json.loads(resp.read()))
EOF
```
Expected: `{"ok": true, "filename": "ForgetMCP.PDF", "chunks": 1, "results": [{"chunk": 1, "signal": "ASSIMILATE"|"DISCARD", ...}]}`

**Step 4: Verify in FalkorDB**
```bash
ssh vault-neo "docker exec karma-server python3 -c \"
import falkordb
r = falkordb.FalkorDB(host='falkordb', port=6379)
g = r.select_graph('neo_workspace')
result = g.query('MATCH (e:Episodic) WHERE e.content CONTAINS \\\"karma-ingest\\\" RETURN e.content ORDER BY e.created_at DESC LIMIT 3')
for row in result.result_set:
    print(row[0][:300])
    print('---')
\""
```

**Step 5: PROMOTE to seal checkpoint**
```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && \
curl -s -X POST http://localhost:18090/v1/promote \
  -H \"Authorization: Bearer \$TOKEN\" \
  -H 'Content-Type: application/json' \
  -d '{\"session_summary\": \"Karma ingest pipeline live. /write-primitive on karma-server, /v1/ingest on hub-bridge, ASSIMILATE/DEFER/DISCARD signal detection, PowerShell folder watcher for OneDrive/Karma/Inbox. Karma now builds herself from raw documents.\"}'"
```

---

## Task 8: Bump version and commit all

**Step 1: Update version string in server.js**

Find `hub-bridge v2.4` in server.js listen log. Change to `v2.5.0`.

**Step 2: Pre-commit secret scan**
```bash
grep -rn "Bearer\|token\|secret\|password\|api_key" --include="*.js" --include="*.py" --include="*.json" --include="*.md" --include="*.ps1" . | grep -v node_modules | grep -v .git
```
Expected: Only references to env var names or file paths — no literal secrets.

**Step 3: Commit and push**
```bash
git add hub-bridge/server.js hub-bridge/package.json scripts/karma-inbox-watcher.ps1 MEMORY.md
git commit -m "feat: v2.5.0 — Karma ingest pipeline (builds herself from documents)"
git push origin main
```

---

## Task 9: Initial batch — process all pending PDFs

Move all PDFs from `PDFs2UL` and `PDFs2UL/completed` to `OneDrive/Karma/Inbox`:

```powershell
$src1 = "C:\Users\raest\OneDrive\Documents\Aria1\NFO\PDFs2UL"
$src2 = "C:\Users\raest\OneDrive\Documents\Aria1\NFO\PDFs2UL\completed"
$dest = "C:\Users\raest\OneDrive\Karma\Inbox"

Get-ChildItem $src1 -Filter "*.PDF" | Copy-Item -Destination $dest
Get-ChildItem $src2 -Filter "*.PDF" | Copy-Item -Destination $dest

Write-Host "Files in Inbox:"
Get-ChildItem $dest | Select-Object Name
```

Then start the folder watcher — it processes the queue automatically.

---

## Summary: What changes where

| Component | Change | Deploy method |
|---|---|---|
| karma-server/server.py | Add /write-primitive endpoint | scp + docker build + docker run |
| hub-bridge/package.json | Add pdf-parse dependency | scp + --no-cache build |
| hub-bridge/server.js | extractPdfText(), writeKarmaPrimitive(), signal detection, /v1/ingest, system prompt | scp + --no-cache build |
| scripts/karma-inbox-watcher.ps1 | New PowerShell watcher | git + run locally on Windows |
| OneDrive/Karma/ | New folder structure | already created |
