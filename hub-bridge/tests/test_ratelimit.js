/**
 * test_ratelimit.js — B5: GLM Rate Limiter tests
 *
 * Run from hub-bridge/app/:
 *   node --test ../tests/test_ratelimit.js
 *
 * All tests should be RED against a stub/missing GlmRateLimiter.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

// Dynamic import so we can test the exported singleton
const routingPath = new URL("../lib/routing.js", import.meta.url).pathname;
const { GlmRateLimiter, glmLimiter } = await import(routingPath);

// ── Helpers ──────────────────────────────────────────────────────────────────

/** Create a fresh limiter with overrideable clock for deterministic tests */
function freshLimiter(rpm = 20, nowFn = null) {
  const lim = new GlmRateLimiter({ rpm, nowFn });
  return lim;
}

/** Drain N slots synchronously */
function drainSlots(lim, n) {
  const results = [];
  for (let i = 0; i < n; i++) {
    results.push(lim.checkAndConsume());
  }
  return results;
}

// ── B5-a: first 20 calls → all allowed ───────────────────────────────────────
test("B5-a: first 20 checkAndConsume() calls in window all return {allowed: true}", () => {
  const lim = freshLimiter(20);
  const results = drainSlots(lim, 20);
  for (let i = 0; i < results.length; i++) {
    assert.equal(results[i].allowed, true, `Call ${i + 1} should be allowed`);
  }
});

// ── B5-b: 21st call → denied ─────────────────────────────────────────────────
test("B5-b: 21st checkAndConsume() returns {allowed: false, retryAfterMs > 0}", () => {
  const lim = freshLimiter(20);
  drainSlots(lim, 20);
  const result = lim.checkAndConsume();
  assert.equal(result.allowed, false, "21st call must be denied");
  assert.ok(result.retryAfterMs > 0, `retryAfterMs must be > 0, got ${result.retryAfterMs}`);
});

// ── B5-c: retryAfterMs accuracy ──────────────────────────────────────────────
test("B5-c: retryAfterMs is approximately (oldest_timestamp + 60_000) - now (±50ms)", () => {
  const BASE = 1_700_000_000_000; // fixed epoch
  let tick = BASE;
  const nowFn = () => tick;

  const lim = freshLimiter(20, nowFn);

  // Consume slot 0 at BASE, slot 1 at BASE+100, ..., slot 19 at BASE+1900
  for (let i = 0; i < 20; i++) {
    tick = BASE + i * 100;
    lim.checkAndConsume();
  }

  // Now at BASE+2000; oldest slot was at BASE (tick=0 offset)
  tick = BASE + 2000;
  const result = lim.checkAndConsume();

  // oldest slot expires at BASE + 60_000; retryAfterMs = (BASE + 60_000) - (BASE + 2000) = 58_000
  const expected = 58_000;
  assert.equal(result.allowed, false);
  assert.ok(
    Math.abs(result.retryAfterMs - expected) <= 50,
    `retryAfterMs should be ~${expected}, got ${result.retryAfterMs}`
  );
});

// ── B5-d: after 60s, 21st call allowed ───────────────────────────────────────
test("B5-d: after fake 60s advance, window resets and 21st call is allowed", () => {
  const BASE = 1_700_000_000_000;
  let tick = BASE;
  const nowFn = () => tick;

  const lim = freshLimiter(20, nowFn);
  drainSlots(lim, 20); // fill window at BASE

  tick = BASE + 60_001; // advance 60s+1ms — all slots expired
  const result = lim.checkAndConsume();
  assert.equal(result.allowed, true, "After window reset, next call should be allowed");
});

// ── B5-e: waitForSlot resolves when slot opens ────────────────────────────────
test("B5-e: waitForSlot resolves when a GLM slot opens (fake time advance)", async () => {
  const BASE = 1_700_000_000_000;
  let tick = BASE;
  const nowFn = () => tick;

  const lim = freshLimiter(3, nowFn); // small limit for speed
  drainSlots(lim, 3); // fill window

  // Advance time in background while waitForSlot is pending
  const advancePromise = (async () => {
    await new Promise(r => setTimeout(r, 10)); // let waitForSlot start polling
    tick = BASE + 60_001; // expire all slots
  })();

  await Promise.all([
    lim.waitForSlot(5_000), // should resolve once tick advances
    advancePromise,
  ]);
  // If we reach here without throw, test passes
});

// ── B5-f: waitForSlot throws on timeout ──────────────────────────────────────
test("B5-f: waitForSlot throws glm_slot_timeout if no slot opens within ceiling", async () => {
  const lim = freshLimiter(1); // limit of 1
  lim.checkAndConsume(); // consume the only slot

  await assert.rejects(
    () => lim.waitForSlot(50), // 50ms ceiling — will expire before 60s window resets
    (err) => {
      assert.ok(
        err.message.includes("glm_slot_timeout"),
        `Expected glm_slot_timeout, got: ${err.message}`
      );
      return true;
    }
  );
});

// ── B5-g: exported glmLimiter is singleton ────────────────────────────────────
test("B5-g: glmLimiter exported from routing.js is a GlmRateLimiter instance (singleton)", async () => {
  // Re-import routing — should return same module (ES module cache)
  const { glmLimiter: glmLimiter2 } = await import(routingPath);
  assert.ok(glmLimiter instanceof GlmRateLimiter, "glmLimiter must be GlmRateLimiter instance");
  assert.strictEqual(glmLimiter, glmLimiter2, "glmLimiter must be same object reference (singleton)");
});
