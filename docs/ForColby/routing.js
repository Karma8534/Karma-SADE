/**
 * Routing authority — single source of truth for model selection.
 *
 * Decision #35 (2026-03-26, Session 145): 3-tier cost-optimal model stack.
 *   - MODEL_DEFAULT (tier 1-2): gpt-5.4-mini ($0.75/$4.50 per 1M) — fast, cheap, tool-capable
 *   - MODEL_ESCALATION (tier 3): gpt-5.4 ($2.50/$15.00 per 1M) — frontier reasoning
 *   - MODEL_VERIFIER: claude-sonnet-4-6 — cross-provider second-opinion for structural changes
 *   - Local cortex (tier 0): qwen3.5:4b on K2/P1 — recall, classification, $0
 *
 * Routing chain: cortex ($0) → gpt-5.4-mini ($) → gpt-5.4 ($$) → sonnet verifier ($$$)
 * Strongest model is NOT default. Escalate only when complexity threshold crossed.
 */

// ── GLM Rate Limiter ─────────────────────────────────────────────────────────

const WINDOW_MS = 60_000; // sliding window width (ms)

/**
 * Sliding-window in-process rate limiter for Z.ai GLM API calls.
 *
 * @param {object} opts
 * @param {number} opts.rpm      - Max requests per 60s window (default 20)
 * @param {Function} [opts.nowFn] - Override Date.now() for testing
 */
export class GlmRateLimiter {
  constructor({ rpm = 20, nowFn = null } = {}) {
    this._rpm   = rpm;
    this._now   = nowFn || (() => Date.now());
    this._slots = []; // timestamps of consumed slots (ascending)
  }

  /** Prune slots older than the 60s window. */
  _prune() {
    const cutoff = this._now() - WINDOW_MS;
    while (this._slots.length > 0 && this._slots[0] <= cutoff) {
      this._slots.shift();
    }
  }

  /**
   * Atomic check-and-consume. If a slot is available, consumes it.
   * @returns {{ allowed: boolean, retryAfterMs: number }}
   */
  checkAndConsume() {
    this._prune();
    if (this._slots.length < this._rpm) {
      this._slots.push(this._now());
      return { allowed: true, retryAfterMs: 0 };
    }
    // Oldest slot expires at _slots[0] + WINDOW_MS
    const retryAfterMs = Math.max(0, this._slots[0] + WINDOW_MS - this._now());
    return { allowed: false, retryAfterMs };
  }

  /**
   * Block until a GLM slot opens or the timeout expires.
   * Used by /v1/ingest chunk loop — allows in-flight PDFs to continue rather
   * than failing outright.
   *
   * @param {number} timeoutMs - Max wait before throwing glm_slot_timeout
   * @returns {Promise<void>}
   * @throws {Error} with message "glm_slot_timeout" if no slot opens in time
   */
  async waitForSlot(timeoutMs) {
    const deadline = this._now() + timeoutMs;
    while (true) {
      const result = this.checkAndConsume();
      if (result.allowed) return;
      if (this._now() >= deadline) {
        const err = new Error("glm_slot_timeout");
        err.code  = "glm_slot_timeout";
        throw err;
      }
      const waitMs = Math.min(result.retryAfterMs, deadline - this._now(), 1_000);
      await new Promise(r => setTimeout(r, Math.max(1, waitMs)));
    }
  }
}

/** Default ingest per-chunk wait ceiling (ms). Overrideable via env in server.js. */
export const GLM_INGEST_SLOT_TIMEOUT_MS = 60_000;

/**
 * Singleton GLM rate limiter — shared across all routes.
 * rpm read at module load from GLM_RPM_LIMIT env var (default 20).
 */
export const glmLimiter = new GlmRateLimiter({
  rpm: Number(process.env.GLM_RPM_LIMIT || "20"),
});

// ── Model routing ────────────────────────────────────────────────────────────

/** Allowed values for MODEL_DEFAULT (tier 1-2: fast, cheap). */
export const ALLOWED_DEFAULT_MODELS = [
  "gpt-5.4-mini",
  "claude-sonnet-4-6",
  "claude-haiku-4-5-20251001",
  "claude-3-5-haiku-20241022",
  "glm-4.7-flash",
];

/** Allowed values for MODEL_ESCALATION (tier 3: frontier reasoning). */
export const ALLOWED_ESCALATION_MODELS = [
  "gpt-5.4",
  "claude-sonnet-4-6",
  "claude-haiku-4-5-20251001",
  "gpt-4o-mini",
];

/** Allowed values for MODEL_VERIFIER (cross-provider second opinion). */
export const ALLOWED_VERIFIER_MODELS = [
  "claude-sonnet-4-6",
  "claude-haiku-4-5-20251001",
  "gpt-5.4-mini",
  "gpt-5.4",
];

const DEFAULT_MODEL_DEFAULT    = "gpt-5.4-mini";
const DEFAULT_MODEL_ESCALATION = "gpt-5.4";
const DEFAULT_MODEL_VERIFIER   = "claude-sonnet-4-6";

/**
 * Validate model env vars at startup. Throws if any model is not in its allowed set.
 * @param {Record<string,string>} env
 */
export function validateModelEnv(env) {
  const defaultModel = env.MODEL_DEFAULT || DEFAULT_MODEL_DEFAULT;
  if (!ALLOWED_DEFAULT_MODELS.includes(defaultModel)) {
    throw new Error(
      `[CONFIG] MODEL_DEFAULT="${defaultModel}" not in allowed list: [${ALLOWED_DEFAULT_MODELS.join(", ")}]. ` +
      "Fix MODEL_DEFAULT in hub.env. Refusing to start."
    );
  }

  const escalationModel = env.MODEL_ESCALATION || DEFAULT_MODEL_ESCALATION;
  if (!ALLOWED_ESCALATION_MODELS.includes(escalationModel)) {
    throw new Error(
      `[CONFIG] MODEL_ESCALATION="${escalationModel}" not in allowed list: [${ALLOWED_ESCALATION_MODELS.join(", ")}]. ` +
      "Fix MODEL_ESCALATION in hub.env. Refusing to start."
    );
  }

  const verifierModel = env.MODEL_VERIFIER || DEFAULT_MODEL_VERIFIER;
  if (!ALLOWED_VERIFIER_MODELS.includes(verifierModel)) {
    throw new Error(
      `[CONFIG] MODEL_VERIFIER="${verifierModel}" not in allowed list: [${ALLOWED_VERIFIER_MODELS.join(", ")}]. ` +
      "Fix MODEL_VERIFIER in hub.env. Refusing to start."
    );
  }
}

/**
 * Choose the model for a request based on tier.
 * Tier 0 = cortex (handled before this function).
 * Tier 1-2 = default (gpt-5.4-mini). Tier 3 = escalation (gpt-5.4).
 *
 * @param {number} tier - 1, 2, or 3
 * @param {Record<string,string>} env
 * @returns {string} model name
 */
export function chooseModel(tier, env) {
  if (tier >= 3) {
    return env.MODEL_ESCALATION || DEFAULT_MODEL_ESCALATION;
  }
  return env.MODEL_DEFAULT || DEFAULT_MODEL_DEFAULT;
}

/**
 * Get the verifier model for cross-provider second opinion.
 * @param {Record<string,string>} env
 * @returns {string} model name
 */
export function getVerifierModel(env) {
  return env.MODEL_VERIFIER || DEFAULT_MODEL_VERIFIER;
}

// Legacy compatibility: chooseModel used to take (deepMode, env).
// Now takes (tier, env). deep_mode=true → tier=3.
