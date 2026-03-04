/**
 * Pricing authority — single source of truth for LLM cost estimation.
 *
 * Decision #2: GLM-4.7-Flash primary (free via Z.ai), gpt-4o-mini paid fallback.
 *
 * Rules:
 *   - GLM models: always $0 (Z.ai free tier, hardcoded — no env var needed)
 *   - gpt-4o-mini: reads PRICE_GPT_4O_MINI_INPUT/OUTPUT_PER_1M from env
 *   - Anthropic: reads PRICE_CLAUDE_INPUT/OUTPUT_PER_1M from env
 *   - Unknown model: returns 1e9 (sentinel — triggers cap enforcement defensively)
 */

function isGlmModel(model) {
  return typeof model === "string" && model.startsWith("glm-");
}

function isAnthropicModel(model) {
  return typeof model === "string" && model.startsWith("claude-");
}

/**
 * Validate that required pricing env vars are present.
 * Throws with a clear error message naming the missing vars.
 * @param {Record<string,string>} env
 */
export function validatePricingEnv(env) {
  const required = [
    "PRICE_GPT_4O_MINI_INPUT_PER_1M",
    "PRICE_GPT_4O_MINI_OUTPUT_PER_1M",
  ];
  const missing = required.filter(
    (k) => !env[k] || isNaN(Number(env[k]))
  );
  if (missing.length > 0) {
    throw new Error(
      `[PRICING] Missing or non-numeric required env vars: ${missing.join(", ")}. ` +
      "Set these in hub.env before starting the hub-bridge."
    );
  }
}

/**
 * Return price per 1M tokens for a given model and direction.
 * @param {string} model
 * @param {"input"|"output"} dir
 * @param {Record<string,string>} env
 * @returns {number}
 */
export function pricePer1M(model, dir, env) {
  // GLM models: Z.ai free tier — always $0
  if (isGlmModel(model)) return 0;

  // Anthropic models
  if (isAnthropicModel(model)) {
    return dir === "input"
      ? Number(env.PRICE_CLAUDE_INPUT_PER_1M)
      : Number(env.PRICE_CLAUDE_OUTPUT_PER_1M);
  }

  // gpt-4o-mini (MODEL_DEEP)
  if (model === "gpt-4o-mini") {
    return dir === "input"
      ? Number(env.PRICE_GPT_4O_MINI_INPUT_PER_1M)
      : Number(env.PRICE_GPT_4O_MINI_OUTPUT_PER_1M);
  }

  // Unknown model — sentinel value triggers cap enforcement defensively
  return 1e9;
}

/**
 * Estimate USD cost for a request.
 * @param {string} model
 * @param {number} inputTokens
 * @param {number} outputTokens
 * @param {Record<string,string>} env
 * @returns {number}
 */
export function estimateUsd(model, inputTokens, outputTokens, env) {
  const inCost  = (inputTokens  / 1_000_000) * pricePer1M(model, "input",  env);
  const outCost = (outputTokens / 1_000_000) * pricePer1M(model, "output", env);
  return Number((inCost + outCost).toFixed(6));
}
