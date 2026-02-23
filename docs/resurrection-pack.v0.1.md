# Resurrection Pack v0.1 (Canonical) — Spec
## Purpose
A Resurrection Pack is a validator-gated snapshot that enables truth-aligned state resurrection without corrupting memory.
## Non-Negotiable Invariants
1) Preserve validated state.
2) Archive failed paths (never delete; keep evidence + reason).
3) Discard transient noise (do not promote noise into canon).
## Outcomes (exactly one)
- **verified**: stored + eligible for rehydrate
- **failed**: archived + never eligible for rehydrate
- **discarded**: treated as noise; not eligible; may be counted but not stored as canon
## Canonical Ordering (Prefix Discipline)
Identity/invariants MUST be stable and ordered:
1) identity
2) invariants
3) project_state
4) session_state
5) conversation_tail (optional/minimal)
No mid-session mutation of identity/invariants. Any change requires version bump.
## Object Schema (JSON)
Top-level:
- id: string (respack_<ulid>)
- created_at_utc: string (ISO8601 Z)
- version: string ("0.1.0")
- status: "verified" | "failed" | "discarded"
- spine_hash: string (sha256 of the canonical ordered prefix)
- payload_sha256: string (sha256 of payload_json canonical bytes)
- notes: string (human-readable, short)
- payload_json: object (see below)
payload_json:
- identity: object (immutable core; max ~2–3 pages when rendered)
- invariants: object (truth/continuity rules; immutable per version)
- project_state: object (pointers/hashes to canonical stores; no bulky dumps)
- session_state: object (optional)
- conversation_tail: array (optional; last N turns or references)
## Promotion Rules
- Only **verified** packs may be promoted as "latest".
- **failed** packs are stored with:
  - fail_reason
  - failing_verifier
  - verifier_at_utc
- **discarded** packs must never be promoted.
## Verification Gates (v0.1)
A pack can be marked **verified** only if ALL pass:
- JSON schema validation
- spine_hash matches recomputed hash from ordered prefix
- payload_sha256 matches recomputed sha256 of canonical payload bytes
- required references reachable (e.g., ledger path exists or API reachable)
If any gate fails → status=failed (not discarded) unless explicitly categorized as noise.
## Noise Policy (v0.1 default)
Default to **failed**, not discarded, unless the event is clearly:
- duplicate
- empty
- rate-limit retry artifact
- UI-only telemetry
Those are **discarded**.
## Future-proofing
- Schema is additive only.
- No breaking removals.
- Each pack should carry:
  verification: { protocol_version, verified_at, verifier, status, notes }
## Minimal API Surface (planned; not implemented here)
- POST /v1/resurrection (create pack)
- GET /v1/resurrection/latest (fetch latest verified)
- GET /v1/resurrection/:id (fetch any by id, including failed)
