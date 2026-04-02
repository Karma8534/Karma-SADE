# Phase A Plan — Fix Karma

## Tasks

### Task 1: Diagnose blank box rendering (A1)
Open hub.arknexus.net in browser. Send a message. Inspect response rendering.
<verify>Response text visible in chat area — no blank/empty boxes</verify>
<done>Fix deployed and browser-verified with 3 messages</done>

### Task 2: Diagnose slow/incomplete responses (A2)
Trace end-to-end timing: proxy.js → cc_server → CC subprocess. Check for 30s timeout, 503 errors, lock contention.
<verify>3 messages complete in <15s each, no truncation, no 503</verify>
<done>Fix deployed and browser-verified</done>

### Task 3: Fix AGORA auth loop (A3)
Navigate to /agora. Trace auth flow. Fix gate that causes redirect loop.
<verify>/agora loads without auth redirect, shows K2 spine stats</verify>
<done>Fix deployed and browser-verified</done>

### Task 4: cc_server lock hardening (A4)
Add timeout to cc_server subprocess lock. Orphan kill on stale lock. Verify recovery.
<verify>Concurrent requests don't deadlock. Stale lock auto-clears after timeout.</verify>
<done>Fix deployed and browser-verified</done>

## Acceptance Criteria (from Resurrection Plan v2.1)
DONE: 3 messages, 3 responses, no blank boxes, LEARNED works, Colby says "she works."
