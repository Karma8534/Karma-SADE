# Karma2 — Baseline Capability Plan
**Created:** 2026-03-20
**Owner:** CC (Ascendant)
**Status:** PLANNING — not yet executing
**Last updated:** 2026-03-20

---

## The North Star

> Karma is a self-improving entity whose baseline equals the union of:
> Claude Code + Cowork + Chat + Codex + Memory Persistence + Identity/Persona Cohesion + Growth & Learning

Every capability Anthropic ships in their baseline products should already exist in Karma.
If it doesn't, that's a gap — not a design choice.

---

## Capability Audit (Live State: 2026-03-20)

| Capability | Have It? | How | Gap |
|------------|----------|-----|-----|
| **Chat** | ✅ | hub.arknexus.net/v1/chat via hub-bridge | — |
| **Memory persistence** | ✅ | Ledger (193k entries) + FalkorDB + FAISS + MEMORY.md spine | — |
| **Identity/persona cohesion** | ✅ | vesper_identity_spine.json (v78, 20 stable patterns) | — |
| **Growth & learning** | ✅ | watchdog→eval→governor pipeline, 75 promotions applied | — |
| **Browser automation** | ⚠️ | Chromium exists on K2 (`/snap/bin/chromium`). Karma HAS used it before. Not currently wired as a callable tool. | Wire Playwright/CDP as a hub-bridge tool |
| **File read/write (project)** | ⚠️ | `shell_run` can do this on K2. Not scoped to Colby's machine. `get_vault_file` reads canonical files. | Extend tool scope |
| **Code execution** | ⚠️ | `shell_run` executes arbitrary commands on K2. Not sandboxed or structured. | Formalize as `run_code` tool |
| **Git operations** | ⚠️ | Via `shell_run` on K2 only. Not on P1/project repo. | Extend or add `git_op` tool |
| **Cowork (collaborative editing)** | ❌ | Not wired. No real-time file collaboration channel. | New tool + protocol |
| **Codex (structured code reasoning)** | ⚠️ | Local models via K2. No structured code-generation pipeline. | Wire Codex as reasoning tier |
| **Background/unattended execution** | ✅ | karma-regent.service runs 24/7, processes bus autonomously | — |
| **Mobile check-in** | ✅ | hub.arknexus.net accessible from any browser | — |

---

## What Dispatch Has That Karma Should Too

Anthropic's Dispatch (Claude desktop app feature):
- Background task execution ← **Karma already has this** (karma-regent.service)
- Browser actions ← **Gap: Chromium on K2, not wired**
- File outputs ← **Gap: scoped to K2, not P1/project**
- Phone check-in ← **Karma already has this** (hub.arknexus.net)

Dispatch is NOT part of our hierarchy. It has no coordination bus access. It is a separate Claude.ai product with no channel into the family.

---

## Phase 1 — Close the Baseline Gaps

Priority order (smallest to largest blast radius):

### P1-A: Browser Automation Tool
- Chromium already installed on K2 (`/snap/bin/chromium`, `/usr/bin/chromium-browser`)
- Karma has used it before — knowledge exists, just not persisted in current tools
- **Implementation:** Add `browser_run(action, url, selector?)` tool to hub-bridge, backed by Playwright/CDP against K2 chromium
- **Gate:** Karma can navigate to hub.arknexus.net/regent and confirm her own heartbeat is visible

### P1-B: Structured File Tool (scoped)
- `shell_run` works but is unstructured — any command, no guardrails
- **Implementation:** Add `file_read(path)` + `file_write(path, content)` tools scoped to allowed directories on K2
- **Gate:** Karma can read/write her own cache files without shell_run workaround

### P1-C: Code Execution (sandboxed)
- **Implementation:** `run_code(lang, code)` tool — executes in a constrained subprocess on K2, returns stdout/stderr
- **Gate:** Karma can run a Python snippet and get the result back

### P1-D: Cowork Protocol
- **Implementation:** Define how Karma and CC collaborate on files. Likely: CC makes changes → writes to coordination bus → Karma acknowledges/reviews
- **Gate:** Karma can review a CC file change and post a substantive response via bus

---

## Phase 2 — Vesper Evolution Pipeline (deferred from 6-item list)

See obs #8077 for full 6-item list. These are optimizations on top of Phase 1 baseline.

1. Falkor write 404 → configurable REGENT_FALKOR_WRITE_URL + retry queue
2. Option-C threshold → reduce SELF_EVAL_INTERVAL to 1 + drive real traffic
3. Learning signal narrow → expand watchdog to 4+ candidate types
4. Synthetic spine artifacts → one-time scrub (may already be resolved — verify first)
5. Dedup memory-only → persist watermark/ring in regent_control
6. Test gap → add smoke test for graph write verification

---

## Active Blockers (from Session 108)

| Blocker | Status |
|---------|--------|
| Regent restart loop (3 crashes 13:18-13:19Z) | 🔴 Undiagnosed |
| P1_OLLAMA_MODEL=nemotron-mini:latest (may not exist on P1) | 🔴 Open |
| KCC drift alert (5 consecutive runs) | 🟡 Alert active |

---

## Notes
- Chromium on K2: confirmed present, Karma has used it before, she just forgets
- Dispatch: NOT in family hierarchy, no bus access, isolated Anthropic product
- The 6-item Vesper list is Phase 2 — do not optimize the evolution pipeline before the baseline is complete
