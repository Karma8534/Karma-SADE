# CP5: Wire Frontend to Consume /v1/surface Merged Endpoint

## Context
/v1/surface exists on P1:7891. Returns 10 keys in ONE call:
session, git, files, skills, hooks, memory, state, agents, transcripts.

The frontend currently makes 5 SEPARATE fetch calls to individual endpoints.
This task replaces those 5 calls with ONE call to /v1/surface.

## EXACT Files to Change

### 1. frontend/src/store/karma.ts — Add surface state + fetch action

ADD to the store interface:
```typescript
surface: {
  session?: { session_id: string };
  git?: { branch: string; changed: number; files: string[]; recent_commits: string[] };
  files?: { root: string; tree: FileNode[] };
  skills?: { count: number; names: string[] };
  hooks?: { count: number; active: boolean; list: { name: string; event: string }[] };
  memory?: { tail: string; file: string };
  state?: { text: string };
  agents?: Record<string, unknown>;
  transcripts?: { count: number; sessions: string[] };
} | null;
fetchSurface: () => Promise<void>;
```

ADD the fetch action:
```typescript
fetchSurface: async () => {
  const { token } = get();
  try {
    const res = await fetch('/v1/surface', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const data = await res.json();
      set({ surface: data });
    }
  } catch {}
},
```

ADD initial state:
```typescript
surface: null,
```

### 2. frontend/src/components/ContextPanel.tsx — Replace 3 separate fetches

CURRENT (FileTreeTab, lines 87-101): fetches `/v1/files`
CURRENT (AgentTab, lines 221-236): fetches `/v1/spine` AND `/v1/agents-status` (2 calls)
CURRENT (MemoryTab, lines 173-187): fetches `/v1/memory/search`

REPLACE FileTreeTab:
```typescript
function FileTreeTab() {
  const surface = useKarmaStore((s) => s.surface);
  const fetchSurface = useKarmaStore((s) => s.fetchSurface);

  useEffect(() => { if (!surface) fetchSurface(); }, [surface, fetchSurface]);

  const tree = surface?.files?.tree || [];
  // ... rest of render unchanged, just use `tree` instead of local state
}
```

REPLACE AgentTab:
```typescript
function AgentTab() {
  const surface = useKarmaStore((s) => s.surface);
  const fetchSurface = useKarmaStore((s) => s.fetchSurface);

  useEffect(() => { if (!surface) fetchSurface(); }, [surface, fetchSurface]);

  const spineData = surface?.agents?.spine || {};
  const pipelineData = surface?.agents?.pipeline || {};
  const mcpServers = surface?.agents?.mcp_servers || [];
  const skills = surface?.skills?.names || [];
  const hooks = surface?.hooks?.list || [];
  // ... rest of render uses these variables (same JSX)
}
```

MemoryTab: KEEP AS-IS. It has a search input that needs per-query fetching.
/v1/surface only gives tail of MEMORY.md, not search results.

### 3. frontend/src/components/SelfEditBanner.tsx — No change needed
Uses `/v1/self-edit/pending` which is NOT in /v1/surface (intentional — self-edit is action, not state).

### 4. frontend/src/components/LearnedPanel.tsx — No change needed
Uses `/v1/learnings` and `/v1/coordination/post` — learnings endpoint has different data shape than surface.

### 5. frontend/src/components/Gate.tsx — No change needed
Uses `/v1/chat` for auth check — not a surface query.

### 6. frontend/src/hooks/useKarmaStream.ts — No change needed
Uses `/v1/chat` for streaming — not a surface query.

### 7. frontend/src/app/page.tsx — Add surface fetch on mount

ADD to Home component:
```typescript
const fetchSurface = useKarmaStore((s) => s.fetchSurface);
useEffect(() => { fetchSurface(); }, [fetchSurface]);
```

This fetches surface data once on page load. ContextPanel tabs then read from store instead of fetching individually.

## EXACT Fetches Being Replaced

| Current Fetch | File:Line | Replaced By |
|---------------|-----------|-------------|
| GET /v1/files | ContextPanel.tsx:90 | surface.files from store |
| GET /v1/spine | ContextPanel.tsx:227 | surface.agents from store |
| GET /v1/agents-status | ContextPanel.tsx:228 | surface.agents + surface.skills + surface.hooks from store |

Total: 3 individual fetches → 1 /v1/surface call on mount.

## Fetches NOT Being Replaced (correct — they need per-query data)

| Fetch | File:Line | Reason |
|-------|-----------|--------|
| POST /v1/memory/search | ContextPanel.tsx:176 | Needs search query parameter |
| GET /v1/self-edit/pending | SelfEditBanner.tsx:26 | Action endpoint, not state |
| POST /v1/self-edit/approve | SelfEditBanner.tsx:69 | Write action |
| POST /v1/self-edit/reject | SelfEditBanner.tsx:81 | Write action |
| GET /v1/learnings | LearnedPanel.tsx:25 | Different data shape (array of learnings) |
| POST /v1/coordination/post | LearnedPanel.tsx:42 | Write action |
| POST /v1/chat | useKarmaStream.ts:43 | Streaming chat — completely different |
| GET /v1/cancel | useKarmaStream.ts:218 | Cancel action |
| POST /v1/chat | Gate.tsx:15 | Auth probe |

## Dead Code to Remove

1. **nexus_agent.py: run_subagent()** — writes transcript sidecars but nothing reads them. DELETE the function (lines ~380-395 in current file). Keep append_transcript and load_transcript.

2. **cc_server_p1.py: file_paths from handle_files()** — variable collected but never used after prefix is built. The file paths ARE used — they're embedded in the message prefix text ("Read the file at: ..."). The variable itself is unused after that. LEAVE AS-IS — not actually dead, just indirect.

## Build + Deploy Steps

```bash
# 1. Make changes to frontend/src files
# 2. Build
cd frontend && npm run build
# 3. Commit
git add frontend/ && git commit -m "feat(CP5): frontend consumes /v1/surface"
# 4. Push
git push origin main
# 5. Deploy to vault-neo
ssh vault-neo 'cd /home/neo/karma-sade && git pull origin main && cp -r frontend/out/* /opt/seed-vault/memory_v1/hub_bridge/app/public/nexus/ && cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d'
```

## Verification (TSS — browser only)

1. Hard refresh hub.arknexus.net
2. Open DevTools Network tab
3. Verify: ONE call to /v1/surface on page load (not 3 separate calls)
4. Click CONTEXT sidebar → FILES tab shows file tree
5. Click CONTEXT sidebar → AGENTS tab shows spine + skills + hooks
6. Send a message → response renders normally
7. Click LEARNED → panel opens with learnings
8. Click MEMORY → opens localhost:37778

ALL must work. If ANY fails, the deploy is rolled back.

## CODEX AUDIT CORRECTIONS (S157 — mandatory before executing)

### CRITICAL: proxy.js MUST add /v1/surface route
proxy.js (vault-neo) does NOT route /v1/surface to P1. Browser fetch will 404.
FIX: Add to proxy.js alongside existing /v1/* routes:
```javascript
// In the GET handler section of proxy.js, add:
if (req.method === "GET" && req.url === "/v1/surface") {
  return proxyToHarness(req, res);  // same pattern as other /v1/* routes
}
```
This is a 4th file change (proxy.js) that was MISSING from original spec.

### CRITICAL: surface.agents shape is WRONG in AgentTab replacement
cc_server /v1/surface puts `_get_agents_status()` in `surface.agents` — this contains
{mcp_servers, skills, hooks}, NOT {spine, pipeline}. The original AgentTab fetches
/v1/spine separately for spine/pipeline data.

FIX: Either:
(a) Add spine data to /v1/surface response in cc_server (fetch from K2 cortex), OR
(b) Keep AgentTab's /v1/spine fetch as-is and only replace /v1/files and /v1/agents-status

Option (b) is safer — fewer changes, less risk. Replace 2 fetches, not 3.

### Dead code confirmed:
- socket import in cc_server_p1.py — unused
- pathlib import in nexus_agent.py — unused
- COMPACTION_TARGET in nexus_agent.py — unused
- run_subagent() in nexus_agent.py — uncalled

## Estimated Complexity: S-M
4 files changed (store, ContextPanel, page, proxy.js). Option (b): replace 2 fetches only.
