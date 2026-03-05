# Design: fetch_url Deep-Mode Tool

**Date:** 2026-03-05
**Status:** Approved
**Scope:** hub-bridge only — no karma-server rebuild required

## Problem
Brave Search returns 3 snippets (title + URL + ~100 chars). Insufficient for research/collaboration discussions where Karma needs to read actual content from URLs the user provides.

## Solution
Add `fetch_url(url)` as a deep-mode tool, handled directly in `executeToolCall` (same pattern as `get_vault_file`). Simultaneously fix the stale tool list in `buildSystemText()` that causes Karma to hallucinate bash/file tools.

## Changes (3 files, 1 deploy)

### 1. `hub-bridge/app/server.js`

**TOOL_DEFINITIONS** — add:
```json
{
  "name": "fetch_url",
  "description": "Fetch the text content of a URL provided by the user. Strips HTML, returns plain text (max 8KB). Use for research, article reading, and collaboration on specific pages the user shares.",
  "input_schema": {
    "type": "object",
    "properties": {
      "url": { "type": "string", "description": "Full URL to fetch (must be provided by the user)" }
    },
    "required": ["url"]
  }
}
```

**executeToolCall** — add handler before proxy fallthrough:
```js
if (toolName === "fetch_url") {
  const url = (toolInput.url || "").trim();
  if (!url) return { error: "missing_url", message: "url is required" };
  const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
  if (!res.ok) return { error: "http_error", message: `${res.status} ${res.statusText}` };
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
}
```

**buildSystemText() line 421** — replace stale hardcoded tool string with:
`graph_query(cypher), get_vault_file(alias), write_memory(content), fetch_url(url)`
Remove: `read_file, write_file, edit_file, bash` — these do not exist in Karma's context.

### 2. `Memory/00-karma-system-prompt-live.md`

Add `fetch_url(url)` to the deep-mode tools section. Coaching:
- Use when user explicitly provides a URL to discuss or analyze
- Do not fetch speculatively without a URL from the user
- Content is truncated at 8KB — sufficient for most articles

### 3. Deploy

`git commit → git push → ssh vault-neo git pull → docker restart anr-hub-bridge`
No rebuild needed (system prompt is file-loaded at startup).

## Constraints
- User-provided URLs only (by design and coaching)
- 10s timeout, 8KB content cap
- Prompt injection risk acknowledged — mitigated by user controlling URLs
- No `read_file`/`write_file`/`edit_file`/`bash` tools — remove from TOOL_DEFINITIONS to eliminate confabulation
