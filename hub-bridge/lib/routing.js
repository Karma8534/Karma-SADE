/**
 * Routing authority — single source of truth for model selection.
 *
 * Decision #2: GLM-4.7-Flash primary (~80%), gpt-4o-mini fallback (~20%).
 *
 * Rules:
 *   - deep_mode=false (no x-karma-deep header): MODEL_DEFAULT (glm-4.7-flash)
 *   - deep_mode=true  (x-karma-deep: true):     MODEL_DEEP   (gpt-4o-mini)
 *   - Tool-use requests: same routing — no silent OpenAI override
 *   - GLM-4.7-Flash tool-calling is SUPPORTED (proven: A3 probe 2026-03-04)
 */

/** Allowed values for MODEL_DEEP. Fail-fast if configured otherwise. */
export const ALLOWED_DEEP_MODELS = ["gpt-4o-mini"];

const DEFAULT_MODEL_DEFAULT = "glm-4.7-flash";
const DEFAULT_MODEL_DEEP    = "gpt-4o-mini";

/**
 * Validate model env vars at startup. Throws if MODEL_DEEP is not in allowed set.
 * @param {Record<string,string>} env
 */
export function validateModelEnv(env) {
  const deepModel = env.MODEL_DEEP || DEFAULT_MODEL_DEEP;
  if (!ALLOWED_DEEP_MODELS.includes(deepModel)) {
    throw new Error(
      `[ROUTING] MODEL_DEEP="${deepModel}" is not in allowed set: [${ALLOWED_DEEP_MODELS.join(", ")}]. ` +
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
