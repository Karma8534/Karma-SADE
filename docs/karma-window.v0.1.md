# Karma Window v0.1 — Contract (Single-Screen State Cockpit)
## Purpose
Provide a web-facing interaction surface for Karma that makes the spine visible and usable:
- chat as the primary interaction
- state and resurrection status always visible
- a copy/paste Resume Prompt for cross-session continuity
## Non-negotiable invariants
- Canonical memory spine remains Vault ledger + Resurrection Packs (no parallel truth).
- Raw lane is non-canonical; promotion required.
- UI never talks to Vault directly; UI calls Hub Bridge only.
- Verification/trust envelope is first-class (trust_level + proof_refs).
## Layout (one screen)
### Left (primary): Chat
- chat stream
- input box
- Private toggle (future): disables capture/promote actions for a window
### Right (always visible): State panels
1) **Resurrection / Trust**
- trust_level
- checkpoint_id, pack_id
- ledger_sha256, anchor_sha256
- packs count, quarantine count
- buttons (phase 2 UI): Capture / Verify / Prune
2) **Resume Prompt**
- full `resume_prompt` text area
- Copy button
3) **Facts & Preferences summary**
- counts + last updated
- "view all" (modal) (phase 2 UI)
## Backend contract (Hub Bridge only)
### Required endpoints (already live)
- `POST /v1/chat` (chat)
- `GET /v1/checkpoint/latest` (returns: resume_prompt + artifacts + proof refs; token-gated)
### Authentication
- UI includes `Authorization: Bearer <HUB_CHAT_TOKEN>` for Hub endpoints that require it.
## Data flow
User message → Hub `/v1/chat` → (Hub calls LLM + logs to Vault) → response to UI
State panel refresh → Hub `/v1/checkpoint/latest` → (Hub proxies Vault) → UI renders trust + resume prompt
## Success criteria (v0.1)
- Chat works through Hub.
- State panel shows trust envelope and proof refs.
- Resume Prompt is copyable and sufficient to resume in a new chat without repo discovery.
