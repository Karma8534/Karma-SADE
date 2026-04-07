# Claursted Primitive Matrix

Date: 2026-04-05
Source: `C:\Users\raest\OneDrive\Documents\GitHub\claursted`
Scope: verified primitives only

## Ground Truth

- `cargo.exe` is installed on disk at `C:\Users\raest\.cargo\bin\cargo.exe`.
- `cargo` is not on PATH in the current PowerShell shell.
- Runtime proof:
  - `cargo --version`
    - output: `The term 'cargo' is not recognized...`
  - `where.exe cargo`
    - output: `INFO: Could not find files for the given pattern(s).`
  - `Test-Path 'C:\Users\raest\.cargo\bin\cargo.exe'`
    - found on disk
  - `& 'C:\Users\raest\.cargo\bin\cargo.exe' --version`
    - output: `cargo 1.94.1 (29ea6fb6a 2026-03-24)`
  - `& 'C:\Users\raest\.cargo\bin\cargo.exe' test -q`
    - partial pass with one real failure
    - failure:
      - crate: `claurst-api`
      - file: `src-rust/crates/api/src/codex_adapter.rs`
      - test: `codex_adapter::tests::test_anthropic_to_openai_request_basic`
      - class: float equality assertion
      - exact mismatch:
        - left: `Number(0.699999988079071)`
        - right: `0.7`

## Required Files Read

- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\README.md`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\spec\INDEX.md`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\spec\13_rust_codebase.md`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\Cargo.toml`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\core\src\session_storage.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\core\src\team_memory_sync.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\query\src\auto_dream.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\query\src\session_memory.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\query\src\cron_scheduler.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tools\src\cron.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tools\src\lib.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\bridge\src\lib.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\mcp\src\registry.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tui\src\session_browser.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tui\src\diff_viewer.rs`
- `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tui\src\voice_capture.rs`

## Decision Rule

- `ADOPT`: primitive fits Nexus with little conceptual change.
- `ADAPT`: primitive is strong, but must be reshaped to fit the Max-CLI / merged-workspace architecture.
- `REJECT`: primitive conflicts with the locked Nexus architecture.

## ADOPT

### 1. JSONL Transcript Persistence

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\core\src\session_storage.rs`
- Why it matters:
  - append-only JSONL session persistence
  - transcript path helpers
  - tombstone deletes
  - session summary extraction
- Code truth:
  - stores JSONL under `~/.claurst/projects/{base64url(project_root)}/{session_id}.jsonl`
  - preserves unknown entry types
  - caps read/write growth with `MAX_TRANSCRIPT_BYTES`
- Nexus fit:
  - directly supports one continual session and resumable transcript history
  - aligns with `.claude/projects/.../*.jsonl` truth model

### 2. Gated Auto-Dream Memory Consolidation

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\query\src\auto_dream.rs`
- Why it matters:
  - 3-gate trigger: time, session count, lock
  - persisted state + stale lock handling
- Code truth:
  - default gates: `24h`, `5 sessions`, `1h stale lock`
  - returns a concrete `ConsolidationTask`
- Nexus fit:
  - directly reusable for dream/consolidation discipline
  - stronger than ad hoc periodic memory jobs

### 3. Durable Internal Cron Scheduler

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\query\src\cron_scheduler.rs`
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tools\src\cron.rs`
- Why it matters:
  - real scheduler loop
  - durable task file
  - one-shot vs recurring tasks
- Code truth:
  - `cron_scheduler` wakes on minute boundary
  - `cron.rs` persists durable tasks to `~/.claurst/scheduled_tasks.json`
  - tasks older than 7 days are purged on load
- Nexus fit:
  - directly addresses prior session-scoped scheduling failures
  - better primitive than prompt-only “remember to do this later”

### 4. Diff/Session UI State Primitives

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tui\src\session_browser.rs`
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tui\src\diff_viewer.rs`
- Why it matters:
  - session browser state
  - diff viewer state, file stats, pane model
- Code truth:
  - session browser supports browse/rename/confirm states
  - diff viewer supports file list + detail pane + diff type toggle
- Nexus fit:
  - directly relevant to merged Chat + Cowork + Code workspace
  - especially useful for browser/Electron code/diff panel design

## ADAPT

### 5. Team Memory Sync

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\core\src\team_memory_sync.rs`
- Why it matters:
  - delta push
  - ETag optimistic concurrency
  - checksum-based diff
  - bounded batch packing
- Code truth:
  - max local file size `250 KB`
  - max serialized PUT body `200 KB`
  - local path validation rejects traversal and absolute paths
- Why adapt instead of adopt:
  - built for `claude.ai` team-memory API
  - Nexus uses `claude-mem` at `localhost:37778`
- Nexus use:
  - adapt the delta/checksum/ETag mechanics to local `claude-mem` sync and shared brain files

### 6. Session Memory Extraction

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\query\src\session_memory.rs`
- Why it matters:
  - extract structured memories from conversation
  - gate by message count and tool activity
  - persist distilled facts
- Code truth:
  - requires `20+` messages and `3+` tool calls between extractions
  - tracks extraction cursor by last message UUID
- Why adapt:
  - writes to `AGENTS.md` in this implementation
  - Nexus needs brain-first writes into `claude-mem` / spine / memory files

### 7. Bridge Session Transport

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\bridge\src\lib.rs`
- Why it matters:
  - device fingerprinting
  - session token/JWT expiry helpers
  - remote session lifecycle and polling model
- Code truth:
  - bridge active only when enabled and token present
  - device fingerprint = SHA-256 of hostname/user/home
- Why adapt:
  - current bridge is for claude.ai web UI transport
  - Nexus already has `hub-bridge` / `proxy.js`
- Nexus use:
  - reuse trusted-device/session-token/session-lifecycle ideas
  - do not replace the existing hub bridge blindly

### 8. Tool Runtime Context

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tools\src\lib.rs`
- Why it matters:
  - permission levels
  - shared tool context
  - session shell state persistence
  - snapshot manager per session
- Code truth:
  - has explicit `PermissionLevel` including `Forbidden`
  - persists per-session shell cwd/env
  - persists per-session snapshot manager
- Why adapt:
  - tool inventory is broader than current Nexus needs
  - some tool semantics differ from current P1/K2 split
- Nexus use:
  - strong reference for local tool contract normalization
  - especially shell-state persistence and turn-level snapshots

### 9. MCP Registry + Discovery

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\mcp\src\registry.rs`
- Why it matters:
  - official server index
  - search/discovery
  - optional live-registry verification
- Code truth:
  - static official registry exists even without live fetch
  - optional live URL verification is fail-closed if not fetched
- Why adapt:
  - Nexus already has local MCP/tool infrastructure and custom services
- Nexus use:
  - useful for discoverability and validation, not as the center of the system

### 10. Voice Capture Primitive

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tui\src\voice_capture.rs`
- Why it matters:
  - push-to-talk lifecycle
  - WAV encoding
  - transcription pipeline
- Code truth:
  - wraps start/stop recording
  - converts samples to WAV
  - transcription path is provider-bound afterward
- Why adapt:
  - current implementation is Rust TUI + Whisper/OpenAI-shaped
  - Nexus browser/Electron already has voice surface decisions
- Nexus use:
  - reusable capture/transcription lifecycle, not the exact provider path

## REJECT

### 11. Provider-First Multi-API Architecture

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\api\src\lib.rs`
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\api\src\providers\anthropic.rs`
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\api\src\providers\openai.rs`
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\api\src\codex_adapter.rs`
- Why reject:
  - Nexus primary path must remain Max through Claude CLI / `CC --resume`
  - direct Anthropic API cannot replace the primary path
- Runtime/test proof:
  - the one failing test is inside `codex_adapter.rs`
  - this reinforces that the provider adapter layer is a distinct subsystem, not the right Nexus floor
- Limited use:
  - fallback abstraction ideas only
  - do not import the provider-first architecture as the floor

### 12. Worktree-Centric Flows

- Files:
  - `C:\Users\raest\OneDrive\Documents\GitHub\claursted\src-rust\crates\tools\src\worktree.rs`
- Why reject:
  - current locked doctrine in this repo is main-branch work unless explicitly justified
  - prior worktree drift caused confusion and stale paths

## Best Merge Candidates For Nexus Next

1. `session_storage.rs`
   - strongest direct continuity primitive
2. `auto_dream.rs`
   - strongest self-improvement/memory consolidation primitive
3. `cron.rs` + `cron_scheduler.rs`
   - strongest “real scheduler, not fake reminders” primitive
4. `team_memory_sync.rs`
   - strongest shared-brain sync primitive after adaptation to `claude-mem`
5. `tools/src/lib.rs`
   - strongest tool runtime/permission/snapshot reference

## Current Contradictions Against Nexus

1. `claursted` is provider-first; Nexus must be Max-CLI-first.
2. `claursted` team memory targets remote claude.ai APIs; Nexus brain is local `claude-mem`.
3. `claursted` is terminal/TUI centered; Nexus product is browser + Electron merged workspace.

## Recommended Use

- Treat `claursted` as a secondary blueprint source for:
  - transcript persistence
  - dream/consolidation
  - cron scheduling
  - tool runtime context
  - team-memory sync patterns
- Do not treat it as the top-level product architecture.
