/**
 * Routing authority — single source of truth for model selection.
 *
 * Decision #3 (2026-03-10): Claude Haiku 3.5 primary for both standard and deep mode.
 * Decision #29 (2026-03-10): Migrated to claude-haiku-4-5-20251001 — haiku-20241022 RETIRED 2026-02-19.
 * (Replaced Decision #2: GLM-4.7-Flash / gpt-4o-mini)
 *
 * Rules:
 *   - deep_mode=false (no x-karma-deep header): MODEL_DEFAULT (claude-haiku-4-5-20251001)
 *   - deep_mode=true  (x-karma-deep: true):     MODEL_DEEP   (claude-haiku-4-5-20251001)
 *   - Tool-use requests: same routing — routes through Anthropic SDK
 *   - GlmRateLimiter kept for compatibility but not invoked for claude- models
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

/** Allowed values for MODEL_DEFAULT. */
export const ALLOWED_DEFAULT_MODELS = ["claude-haiku-4-5-20251001", "claude-3-5-haiku-20241022", "glm-4.7-flash"];

/** Allowed values for MODEL_DEEP. */
export const ALLOWED_DEEP_MODELS = ["claude-haiku-4-5-20251001", "claude-3-5-haiku-20241022", "gpt-4o-mini"];

const DEFAULT_MODEL_DEFAULT = "claude-haiku-4-5-20251001";
const DEFAULT_MODEL_DEEP    = "claude-haiku-4-5-20251001";

/**
 * Validate model env vars at startup. Throws if either model is not in its allowed set.
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

  const deepModel = env.MODEL_DEEP || DEFAULT_MODEL_DEEP;
  if (!ALLOWED_DEEP_MODELS.includes(deepModel)) {
    throw new Error(
      `[CONFIG] MODEL_DEEP="${deepModel}" not in allowed list: [${ALLOWED_DEEP_MODELS.join(", ")}]. ` +
      "Fix MODEL_DEEP in hub.env. Refusing to start."
    );
  }
}

/**
 * Choose the model for a request.
 * Both chat and tool-use routes go through this function — no bypass.
 *
 * @param {boolean} deepMode  — true if x-karma-deep header was set
 * @param {Record<string,string>} env
 * @returns {string} model name
 */
export function chooseModel(deepMode, env) {
  if (deepMode) {
    return env.MODEL_DEEP || DEFAULT_MODEL_DEEP;
  }
  return env.MODEL_DEFAULT || DEFAULT_MODEL_DEFAULT;
}
