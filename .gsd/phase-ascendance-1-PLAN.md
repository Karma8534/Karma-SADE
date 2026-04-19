# Phase Ascendance 1 — Persona-on-Boot

**Goal:** Julian.exe loads canonical persona automatically on cold launch — no manual paste.

**Binary criterion:** Cold-boot Julian.exe → first chat turn includes persona block sourced from `Memory/00-karma-system-prompt-live.md` (verifiable via debug echo or response identity check).

## Tasks

### Task 1 — Write CONTEXT
Write `.gsd/phase-ascendance-1-CONTEXT.md` locking:
- Source of truth for persona: `Memory/00-karma-system-prompt-live.md` on vault-neo (canonical) + local mirror path
- Load mechanism choice: bridge-injects (preferred) vs webview-fetches
- What "Persona-on-Boot" means observably (echo header? identity question response?)
- Out of scope: cross-surface parity (Phase 2), TRUE FAMILY UI (Phase 3)

### Task 2 — Locate persona load path
Read `Scripts/cc_server_p1.py` to confirm whether system prompt is already injected on `/v1/chat`. Read `frontend/src/components/MessageInput.tsx` and `frontend/src/store/karma.ts` to confirm whether the webview ever requests/displays persona on boot.

### Task 3 — Wire persona load
Implement chosen mechanism. If bridge-side: ensure `Memory/00-karma-system-prompt-live.md` is read on first `/v1/chat` request and prepended. If webview-side: add `useEffect` on app mount to GET `/v1/persona` and seed conversation.

### Task 4 — Add `/v1/persona` endpoint (if needed)
GET returns current persona text + version + source path. Used for debug + Phase 2 parity check.

### Task 5 — Verify
1. Kill Julian.exe
2. Launch fresh from ArkNexus.lnk
3. First message: "who are you"
4. Response must reference Karma identity from canonical file (not generic Claude)
5. Save evidence: `tmp/ascendance/phase-1-evidence.txt` with timestamp + response

## Done when
- [ ] CONTEXT written, mechanism chosen
- [ ] Code shipped + Tauri rebuilt
- [ ] Cold-boot identity test passes
- [ ] Evidence file committed
- [ ] STOP gate: do not start Phase 2 until Sovereign confirms

## Reference
Full directive: ARKNEXUS ASCENDANCE = 100 (offline copy held by Sovereign)
