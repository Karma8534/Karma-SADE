// Phase B — RED tests for DRIFT #1 (pricing) and DRIFT #2 (MODEL_DEEP default)
// These tests must FAIL against stubs, then PASS after Phase C implementation.

import { test } from "node:test";
import assert from "node:assert/strict";
import { pricePer1M, estimateUsd, validatePricingEnv } from "../lib/pricing.js";

// ── Helpers ──────────────────────────────────────────────────────────────────

function mockEnv(overrides = {}) {
  return {
    MODEL_DEFAULT: "glm-4.7-flash",
    MODEL_DEEP: "gpt-4o-mini",
    PRICE_GPT_4O_MINI_INPUT_PER_1M: "0.15",
    PRICE_GPT_4O_MINI_OUTPUT_PER_1M: "0.60",
    PRICE_CLAUDE_INPUT_PER_1M: "3.0",
    PRICE_CLAUDE_OUTPUT_PER_1M: "15.0",
    MONTHLY_USD_CAP: "35.00",
    ...overrides,
  };
}

// ── B1: Pricing correctness ───────────────────────────────────────────────────

test("B1-a: GLM model input price is $0 (free tier)", () => {
  const env = mockEnv();
  assert.equal(pricePer1M("glm-4.7-flash", "input", env), 0,
    "GLM input price must be 0 — Z.ai free tier");
});

test("B1-b: GLM model output price is $0 (free tier)", () => {
  const env = mockEnv();
  assert.equal(pricePer1M("glm-4.7-flash", "output", env), 0,
    "GLM output price must be 0 — Z.ai free tier");
});

test("B1-c: gpt-4o-mini input uses PRICE_GPT_4O_MINI_INPUT_PER_1M (not GPT_5_2)", () => {
  const env = mockEnv({ PRICE_GPT_4O_MINI_INPUT_PER_1M: "0.15" });
  assert.equal(pricePer1M("gpt-4o-mini", "input", env), 0.15,
    "gpt-4o-mini input must use PRICE_GPT_4O_MINI_INPUT_PER_1M = 0.15");
});

test("B1-d: gpt-4o-mini output uses PRICE_GPT_4O_MINI_OUTPUT_PER_1M (not GPT_5_2)", () => {
  const env = mockEnv({ PRICE_GPT_4O_MINI_OUTPUT_PER_1M: "0.60" });
  assert.equal(pricePer1M("gpt-4o-mini", "output", env), 0.60,
    "gpt-4o-mini output must use PRICE_GPT_4O_MINI_OUTPUT_PER_1M = 0.60");
});

test("B1-e: GLM request estimateUsd returns $0 regardless of token count", () => {
  const env = mockEnv();
  const cost = estimateUsd("glm-4.7-flash", 10000, 5000, env);
  assert.equal(cost, 0, "10k input + 5k output tokens on GLM must cost $0");
});

test("B1-f: GLM spend near cap does NOT trigger cap enforcement", () => {
  // Cap = 35.00, current spend = 34.99. GLM request adds $0 → no violation.
  const env = mockEnv({ MONTHLY_USD_CAP: "35.00" });
  const glmCost = estimateUsd("glm-4.7-flash", 100000, 50000, env);
  const spendAfter = 34.99 + glmCost;
  assert.ok(spendAfter <= 35.00,
    `GLM request at 34.99 spend must not exceed cap; got ${spendAfter}`);
});

test("B1-g: OpenAI gpt-4o-mini spend near cap DOES trigger cap enforcement", () => {
  // Cap = 35.00, current spend = 34.999. gpt-4o-mini request adds >0 → violation.
  const env = mockEnv({ MONTHLY_USD_CAP: "35.00" });
  const openaiCost = estimateUsd("gpt-4o-mini", 10000, 5000, env);
  assert.ok(openaiCost > 0, "gpt-4o-mini must have cost > 0");
  const spendAfter = 34.999 + openaiCost;
  assert.ok(spendAfter > 35.00,
    `gpt-4o-mini request at 34.999 spend must exceed cap; got ${spendAfter}`);
});

test("B1-h: validatePricingEnv throws if OpenAI price vars missing", () => {
  const env = mockEnv({
    PRICE_GPT_4O_MINI_INPUT_PER_1M: undefined,
    PRICE_GPT_4O_MINI_OUTPUT_PER_1M: undefined,
  });
  assert.throws(
    () => validatePricingEnv(env),
    /PRICE_GPT_4O_MINI/,
    "validatePricingEnv must throw naming the missing price vars"
  );
});

test("B1-i: validatePricingEnv passes when all required vars present", () => {
  const env = mockEnv();
  assert.doesNotThrow(() => validatePricingEnv(env));
});
