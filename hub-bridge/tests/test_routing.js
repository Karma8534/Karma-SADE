// Phase B — RED tests for DRIFT #2 (MODEL_DEEP default) and DRIFT #3 (routing)
// Phase G — RED tests for Config Validation Gate (MODEL_DEFAULT allow-list)
// These tests must FAIL against stubs, then PASS after implementation.

import { test } from "node:test";
import assert from "node:assert/strict";
import { chooseModel, validateModelEnv, ALLOWED_DEEP_MODELS } from "../lib/routing.js";

// ── Helpers ──────────────────────────────────────────────────────────────────

function mockEnv(overrides = {}) {
  return {
    MODEL_DEFAULT: "glm-4.7-flash",
    MODEL_DEEP: "gpt-4o-mini",
    ...overrides,
  };
}

// ── B2: MODEL_DEEP default validity ──────────────────────────────────────────

test("B2-a: chooseModel with no MODEL_DEEP env defaults to gpt-4o-mini (not gpt-5-mini)", () => {
  const env = mockEnv({ MODEL_DEEP: undefined });
  // In deep mode, must use a valid model — never "gpt-5-mini"
  const model = chooseModel(true, env);
  assert.notEqual(model, "gpt-5-mini", "Default MODEL_DEEP must never be gpt-5-mini");
  assert.equal(model, "gpt-4o-mini", "Default MODEL_DEEP must be gpt-4o-mini");
});

test("B2-b: validateModelEnv throws if MODEL_DEEP is gpt-5-mini", () => {
  const env = mockEnv({ MODEL_DEEP: "gpt-5-mini" });
  assert.throws(
    () => validateModelEnv(env),
    /gpt-5-mini|invalid|not allowed/i,
    "validateModelEnv must reject gpt-5-mini as MODEL_DEEP"
  );
});

test("B2-c: validateModelEnv passes if MODEL_DEEP is gpt-4o-mini", () => {
  const env = mockEnv({ MODEL_DEEP: "gpt-4o-mini" });
  assert.doesNotThrow(() => validateModelEnv(env));
});

test("B2-d: ALLOWED_DEEP_MODELS contains gpt-4o-mini, not gpt-5-mini", () => {
  assert.ok(ALLOWED_DEEP_MODELS.includes("gpt-4o-mini"), "gpt-4o-mini must be allowed");
  assert.ok(!ALLOWED_DEEP_MODELS.includes("gpt-5-mini"), "gpt-5-mini must not be allowed");
});

// ── B3: Routing correctness (chat + tool-use) ─────────────────────────────────

test("B3-a: Normal chat (deep_mode=false) routes to MODEL_DEFAULT (glm-4.7-flash)", () => {
  const env = mockEnv();
  const model = chooseModel(false, env);
  assert.equal(model, "glm-4.7-flash",
    "Non-deep request must route to MODEL_DEFAULT = glm-4.7-flash");
});

test("B3-b: Deep chat (deep_mode=true) routes to MODEL_DEEP (gpt-4o-mini)", () => {
  const env = mockEnv();
  const model = chooseModel(true, env);
  assert.equal(model, "gpt-4o-mini",
    "Deep request must route to MODEL_DEEP = gpt-4o-mini");
});

test("B3-c: Tool-use without deep header uses GLM (same routing as chat)", () => {
  // Tool-use must go through same chooseModel() as chat.
  // deep_mode=false (no x-karma-deep header) → MODEL_DEFAULT → glm-4.7-flash
  const env = mockEnv();
  const model = chooseModel(false, env);
  assert.equal(model, "glm-4.7-flash",
    "Tool-use without x-karma-deep must route to GLM, not hardcoded gpt-4o-mini");
});

test("B3-d: Tool-use with deep header uses gpt-4o-mini", () => {
  const env = mockEnv();
  const model = chooseModel(true, env);
  assert.equal(model, "gpt-4o-mini",
    "Tool-use with x-karma-deep:true must route to gpt-4o-mini");
});

test("B3-e: chooseModel handles undefined MODEL_DEFAULT gracefully", () => {
  const env = mockEnv({ MODEL_DEFAULT: undefined });
  // Should not throw; return some safe default
  assert.doesNotThrow(() => chooseModel(false, env));
});

// ── G: Config Validation Gate — MODEL_DEFAULT allow-list ─────────────────────

test("G-a: validateModelEnv throws if MODEL_DEFAULT is not in allowed list", () => {
  const env = mockEnv({ MODEL_DEFAULT: "glm-unknown-model" });
  assert.throws(
    () => validateModelEnv(env),
    /MODEL_DEFAULT.*not in allowed/,
    "validateModelEnv must reject glm-unknown-model as MODEL_DEFAULT"
  );
});

test("G-b: validateModelEnv throws if MODEL_DEEP is gpt-5 (not in allowed list)", () => {
  const env = mockEnv({ MODEL_DEEP: "gpt-5" });
  assert.throws(
    () => validateModelEnv(env),
    /MODEL_DEEP.*not in allowed/,
    "validateModelEnv must reject gpt-5 as MODEL_DEEP"
  );
});
