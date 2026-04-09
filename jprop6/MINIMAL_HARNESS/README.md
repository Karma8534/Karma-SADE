# jprop6 Minimal Harness

## What This Scaffold Is
This is a foundation-only Electron harness scaffold under `jprop6`.
It is intentionally small and exists to prove wiring, boundary, and continuity contract seams.

## What It Proves
1. Electron shell can launch and target `https://hub.arknexus.net`.
2. Preload boundary is locked (`contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`).
3. Minimal runtime introspection API exists via `window.jprop6Harness.runtime()`.
4. Minimal continuity envelope seam exists via `readSessionEnvelope` and `writeSessionEnvelope`.
5. Fallback rendering path exists for failed hub loads and explicitly states foundation-only posture.

## What It Intentionally Does NOT Prove
1. Full merged workspace completion.
2. Full memory/continuity reliability across all real incidents.
3. Agent/orchestrator production correctness.
4. Plugin/voice/transport expansion behavior.
5. Any watcher authority for phase closure.

## Runtime Contracts This Depends On
1. Hub runtime endpoint availability at `https://hub.arknexus.net/health`.
2. Session envelope schema in `session_contract.schema.json`.
3. Binary proof scripts:
   - `scripts/proof_check.js`
   - `tests/contract_check.js`
   - `tests/break_check.js`

## How It Surfaces hub.arknexus.net
1. `main.js` sets `HUB_URL` default to `https://hub.arknexus.net`.
2. Browser window runs `win.loadURL(HUB_URL)`.
3. On load failure (`did-fail-load`), harness switches to `renderer/fallback.html` and shows target + error details.

## Browser↔Electron Continuity Intent
1. Browser and Electron are expected to share the same conceptual envelope keys (`schema_version`, `written_at`, session keys).
2. This scaffold stores envelope locally in Electron user data as a seam.
3. Cross-surface synchronization policy is defined in `jprop6.md` and validated by phase gates, not assumed by UI claims.

## Stubbed vs Real
Real now:
1. Secure Electron shell boundary.
2. Hub load path + fallback.
3. Local continuity envelope read/write seam.
4. Executable proof checks.

Stubbed/deferred:
1. Full session recovery orchestration.
2. Conflict resolution engine for multi-writer continuity.
3. Deep workspace integration (chat/cowork/code internals).
4. Watcher/governor automation authority.
