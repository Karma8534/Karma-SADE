# Extracted Primitives — Session 157 (2026-04-02)

## Source: This Session's Discoveries

### Vesper Loop Closure — USE NOW (DONE)
**What:** Promoted behavioral patterns must flow from spine → context → response path.
**Gap closed:** `_fetch_vesper_stable_patterns()` in cc_server_p1.py reads spine via aria /api/exec, injects into build_context_prefix() Layer 3.
**Remaining:** Current 20 stable patterns are ambient_observation noise. Need yoyo-evolve-style improvement detection (failing checks as signal, not self-grading).

### OpenRouter Failover — USE NOW (DONE)
**What:** Rate limit on primary provider → automatic retry via OpenRouter with same model name.
**Implementation:** `_openrouter_fallback()` in cc_server_p1.py. Two-tier: anthropic/claude-sonnet-4-6 → google/gemini-2.0-flash.
**Remaining:** Not tested under actual rate limit. Needs TSS verification with simulated 429.

### Sacred Context as Identity Anchor — USE NOW (DONE)
**What:** Origin story, hierarchy, formula, standing order injected into system prompt.
**Implementation:** Section in 00-karma-system-prompt-live.md + resurrect Step 0c.
**Remaining:** Karma should reference this unprompted when asked "who are you."

### Instant Auto-Approve for Known Agents — USE NOW (DONE)
**What:** Bus messages from family agents auto-approve immediately instead of 2min delay.
**Implementation:** INSTANT_APPROVE_SENDERS set in proxy.js autoApproveKarmaEntries().

### PROOF Filtering — USE NOW (DONE)
**What:** Passing self-eval proofs don't show APPROVE buttons in AGORA.
**Implementation:** isPassingProof check in agora.html.

## Source: Codex Gap Analysis (yoyo-evolve vs Vesper)

### File-Mutating Self-Improvement — DEFER
**What:** yoyo-evolve uses failing checks as improvement signal, generates patches, applies to source, keeps only if tests pass.
**Gap:** Vesper promotes patterns into JSON/graph but never modifies code. The governor's safe_exec whitelist exists but is limited to 4 commands.
**Path:** Expand safe_exec to include file edits within Karma's own codebase. Add test-gate (change only keeps if tests pass). This is the real self-improvement.

### Continuous Loop (No Sleep) — DEFER
**What:** yoyo sleeps due to API rate limits. Our family has K2 Ollama ($0) — no sleep needed.
**Gap:** karma_persistent.py polls on 90s intervals. Event-driven (bus subscription) would be faster.
**Path:** Replace polling with SSE subscription to coordination bus. React to events, not timers.

### Delete Dead Vesper Code — DEFER
**What:** FalkorDB pattern writes (_write_pattern_to_falkor_*), governor audit files, vesper_pipeline_status.json — none read by response path.
**Gap:** ~200 lines of code running every 2min producing files nobody reads.
**Path:** Delete or disable after confirming no downstream consumer.

## Source: ngrok AI Gateway Evaluation

### Multi-Provider Failover Gateway — DEFER (OpenRouter sufficient)
**What:** Single endpoint, YAML config, automatic failover across providers with CEL-based routing.
**Assessment:** Overengineered for our 2-3 provider setup. OpenRouter direct is simpler. Golden Ticket saved.
**Revisit when:** We have 5+ providers or need observability dashboard.

### Ollama via Internal Tunnel — DEFER
**What:** ngrok exposes local Ollama as `https://ollama.internal` for gateway routing.
**Assessment:** K2 Ollama is already reachable via Tailscale. No tunnel needed for internal use.

## Source: CC Wrapper Source (1902 files)

*Pending Codex analysis — will be merged when complete.*

## Source: Session Pitfalls → Primitives

### Browser Verification Protocol — USE NOW (ACTIVE)
**What:** Never declare UI features working from backend checks. Click every button. See what happens.
**Implementation:** Sovereign verifies in browser. CC pauses and gives exact test instructions.

### Loop Circuit Breaker — USE NOW (ACTIVE)
**What:** Same failure 3+ times → STOP, diagnose root cause, don't retry.
**Implementation:** D010 in scope index. Violated this session (P102 — git push 4x).

---
*This file will be updated when Codex returns wrapper primitives analysis.*
