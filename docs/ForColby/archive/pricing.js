/**
 * Pricing authority — single source of truth for LLM cost estimation.
 *
 * Decision #35 (2026-03-26): 3-tier cost-optimal model stack.
 *   - gpt-5.4-mini: $0.75/$4.50 per 1M (default)
 *   - gpt-5.4: $2.50/$15.00 per 1M (escalation)
 *   - claude-sonnet-4-6: $3.00/$15.00 per 1M (verifier)
 *   - claude-haiku-4-5: $1.00/$5.00 per 1M (legacy)
 *   - GLM models: $0 (Z.ai free tier)
 *   - Unknown model: returns 1e9 (sentinel — triggers cap enforcement defensively)
 */

function isGlmModel(model) {
  return typeof model === "string" && model.startsWith("glm-");
}

function isAnthropicModel(model) {
  return typeof model === "string" && model.startsWith("claude-");
}

function isGpt5Model(model) {
  return typeof model === "string" && model.startsWith("gpt-5");
}

/**
 * Validate that required pricing env vars are present.
 * @param {Record<string,string>} env
 */
export function validatePricingEnv(env) {
  // No hard requirement on env vars — pricing is now hardcoded for known models.
  // Env vars override if present.
}

// Hardcoded pricing (per 1M tokens) — updated 2026-03-26
const PRICING = {
  "gpt-5.4-mini":  { input: 0.75,  output: 4.50  },
  "gpt-5.4":       { input: 2.50,  output: 15.00 },
  "gpt-4o-mini":   { input: 0.15,  output: 0.60  },
  // Anthropic pricing from env (allows override), defaults here
  "claude-sonnet-4-6":          { input: 3.00, output: 15.00 },
  "claude-haiku-4-5-20251001":  { input: 1.00, output: 5.00  },
  "claude-3-5-haiku-20241022":  { input: 1.00, output: 5.00  },
};

/**
 * Return price per 1M tokens for a given model and direction.
 * @param {string} model
 * @param {"input"|"output"} dir
 * @param {Record<string,string>} env
 * @returns {number}
 */
export function pricePer1M(model, dir, env) {
  // GLM models: Z.ai free tier
  if (isGlmModel(model)) return 0;

  // Check hardcoded pricing table first
  const entry = PRICING[model];
  if (entry) {
    return dir === "input" ? entry.input : entry.output;
  }

  // Anthropic fallback (unknown claude- model)
  if (isAnthropicModel(model)) {
    return dir === "input"
      ? Number(env.PRICE_CLAUDE_INPUT_PER_1M || "3.00")
      : Number(env.PRICE_CLAUDE_OUTPUT_PER_1M || "15.00");
  }

  // GPT-5.x fallback (unknown gpt-5 variant)
  if (isGpt5Model(model)) {
    return dir === "input" ? 2.50 : 15.00;
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
