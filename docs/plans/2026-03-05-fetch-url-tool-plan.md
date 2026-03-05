# fetch_url Tool Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `fetch_url(url)` as a deep-mode tool and remove stale tool definitions that cause Karma to hallucinate bash/file capabilities.

**Architecture:** All changes in hub-bridge only. `fetch_url` handled directly in `executeToolCall` before the karma-server proxy fallthrough — same pattern as `get_vault_file`. No karma-server rebuild. Deploy is git pull + docker restart only.

**Tech Stack:** Node.js (server.js), native `fetch` (already available), regex HTML stripping.

---

### Task 1: Remove stale tools from TOOL_DEFINITIONS

**Files:**
- Modify: `hub-bridge/app/server.js:777-858`

`read_file`, `write_file`, `edit_file`, `bash` are defined in TOOL_DEFINITIONS but have no handler in `executeToolCall` — they proxy to karma-server which rejects them. They cause Karma to confabulate capabilities she doesn't have.

**Step 1: Delete the four stale tool definitions**

Remove lines 779-824 (the `read_file`, `write_file`, `edit_file`, `bash` objects from the array). The array should start with `graph_query` at the new top.

**Step 2: Verify array is still valid JS**

```bash
node -e "const s = require('fs').readFileSync('hub-bridge/app/server.js','utf8'); eval('const x = ' + s.match(/const TOOL_DEFINITIONS = (\[[\s\S]*?\]);/)[1]); console.log('ok', x.length, 'tools')"
```
Expected: `ok 3 tools` (graph_query, get_vault_file, write_memory)

**Step 3: Commit**
```bash
powershell -Command "git add hub-bridge/app/server.js && git commit -m 'fix: remove stale tool definitions (read_file/write_file/edit_file/bash) causing confabulation'"
```

---

### Task 2: Add fetch_url to TOOL_DEFINITIONS

**Files:**
- Modify: `hub-bridge/app/server.js:857` (after write_memory closing brace, before `];`)

**Step 1: Insert fetch_url definition**

Add after the `write_memory` object (after line 857, before `];` on line 858):

```js
  {
    name: "fetch_url",
    description: "Fetch the plain-text content of a URL provided by the user. Strips HTML tags, returns up to 8KB. Use when the user shares a URL to discuss, research, or analyze together. Do NOT call speculatively — only fetch URLs the user explicitly provides.",
    input_schema: {
      type: "object",
      properties: {
        url: { type: "string", description: "Full URL to fetch (must have been provided by the user in this conversation)" },
      },
      required: ["url"],
    },
  },
```

**Step 2: Verify syntax**
```bash
node -e "const s = require('fs').readFileSync('hub-bridge/app/server.js','utf8'); eval('const x = ' + s.match(/const TOOL_DEFINITIONS = (\[[\s\S]*?\]);/)[1]); console.log('ok', x.length, 'tools')"
```
Expected: `ok 4 tools`

**Step 3: Commit**
```bash
powershell -Command "git add hub-bridge/app/server.js && git commit -m 'feat: add fetch_url to TOOL_DEFINITIONS'"
```

---

### Task 3: Add fetch_url handler in executeToolCall

**Files:**
- Modify: `hub-bridge/app/server.js:906` (after `get_vault_file` handler, before proxy fallthrough)

**Step 1: Insert handler after the get_vault_file block (after line 906)**

```js
    // fetch_url — hub-bridge fetches arbitrary URLs provided by the user
    if (toolName === "fetch_url") {
      const url = (toolInput.url || "").trim();
      if (!url) return { error: "missing_url", message: "url is required" };
      try {
        const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
        if (!res.ok) return { error: "http_error", message: `${res.status} ${res.statusText}`, url };
        const html = await res.text();
        const text = html
          .replace(/<script[\s\S]*?<\/script>/gi, "")
          .replace(/<style[\s\S]*?<\/style>/gi, "")
          .replace(/<[^>]+>/g, " ")
          .replace(/\s+/g, " ")
          .trim()
          .slice(0, 8192);
        console.log(`[TOOL-API] fetch_url '${url}' → ${text.length} chars`);
        return { ok: true, url, content: text, chars: text.length };
      } catch (e) {
        return { error: "fetch_error", message: e.message, url };
      }
    }
```

**Step 2: Verify syntax**
```bash
node --check hub-bridge/app/server.js && echo "syntax ok"
```
Expected: `syntax ok`

**Step 3: Commit**
```bash
powershell -Command "git add hub-bridge/app/server.js && git commit -m 'feat: add fetch_url handler in executeToolCall'"
```

---

### Task 4: Fix buildSystemText() hardcoded tool string

**Files:**
- Modify: `hub-bridge/app/server.js:421`

**Step 1: Find and replace the stale tool string**

Current (line 421 contains):
```
graph_query(cypher), get_vault_file(alias), read_file(path), write_file(path,content), edit_file(path,old,new), bash(command)
```

Replace with:
```
graph_query(cypher), get_vault_file(alias), write_memory(content), fetch_url(url)
```

**Step 2: Verify**
```bash
grep -n "bash\|read_file\|write_file\|edit_file" hub-bridge/app/server.js | grep -v "//\|TOOL_DEF\|executeToolCall\|ALLOWED"
```
Expected: no output (no remaining stale references in logic)

**Step 3: Commit**
```bash
powershell -Command "git add hub-bridge/app/server.js && git commit -m 'fix: correct tool list in buildSystemText - remove bash/file tools, add fetch_url'"
```

---

### Task 5: Update system prompt coaching

**Files:**
- Modify: `Memory/00-karma-system-prompt-live.md:26` and `:86`

**Step 1: Update line 26 tool list**

Current:
```
`graph_query`, `get_vault_file`
```
Replace with:
```
`graph_query`, `get_vault_file`, `write_memory`, `fetch_url`
```

**Step 2: Add fetch_url coaching after the write_memory paragraph (after line 86)**

```markdown
**Web research:** When the user shares a URL in the conversation, call `fetch_url(url)` to read its content before responding. This gives you the actual text to discuss, not just search snippets. Only call this for URLs the user explicitly provides — do not fetch speculatively.
```

**Step 3: Commit**
```bash
powershell -Command "git add Memory/00-karma-system-prompt-live.md && git commit -m 'feat: add fetch_url coaching to system prompt, fix tool list'"
```

---

### Task 6: Push and deploy

**Step 1: Push to GitHub**
```bash
powershell -Command "git push origin main"
```

**Step 2: Pull on vault-neo and restart hub-bridge**
```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main && docker restart anr-hub-bridge"
```

**Step 3: Verify with karma-verify skill**

Use `karma-verify` skill — check RestartCount=0 and startup logs show identity loaded.

**Step 4: Smoke test fetch_url**

In deep mode chat (`x-karma-deep: true`), send:
```
Can you fetch this URL and tell me what it says? https://example.com
```
Expected: Karma calls `fetch_url`, returns content summary. No hallucination about bash tools.
