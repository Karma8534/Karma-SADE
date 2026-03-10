// test_deferred_intent.js — 16 tests for deferred_intent.js — Phase 4 Task 2
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  generateIntentId,
  triggerMatches,
  buildActiveIntentsText,
  getSurfaceIntents,
} from "../lib/deferred_intent.js";

// ── generateIntentId ──────────────────────────────────────────────────────────

test("generateIntentId returns string starting with int_", () => {
  const id = generateIntentId();
  assert.equal(typeof id, "string");
  assert.ok(id.startsWith("int_"), `expected "${id}" to start with "int_"`);
});

test("generateIntentId returns unique IDs", () => {
  const ids = new Set(Array.from({ length: 10 }, () => generateIntentId()));
  assert.equal(ids.size, 10);
});

// ── triggerMatches ────────────────────────────────────────────────────────────

test("type=always returns true regardless of message", () => {
  const trigger = { type: "always" };
  assert.equal(triggerMatches(trigger, ""), true);
  assert.equal(triggerMatches(trigger, "anything"), true);
});

test("type=topic: returns true when keyword in message", () => {
  const trigger = { type: "topic", value: "redis-py" };
  assert.equal(triggerMatches(trigger, "how does redis-py handle keys?"), true);
});

test("type=topic: case-insensitive", () => {
  const trigger = { type: "topic", value: "Redis-Py" };
  assert.equal(triggerMatches(trigger, "tell me about redis-py"), true);
});

test("type=topic: returns false when keyword absent", () => {
  const trigger = { type: "topic", value: "redis-py" };
  assert.equal(triggerMatches(trigger, "tell me about mongodb"), false);
});

test("type=phase: matches correct phase", () => {
  const trigger = { type: "phase", value: "start" };
  assert.equal(triggerMatches(trigger, "hello", "start"), true);
  assert.equal(triggerMatches(trigger, "hello", "active"), false);
});

test("type=unknown returns false", () => {
  const trigger = { type: "semantic", value: "something" };
  assert.equal(triggerMatches(trigger, "something"), false);
});

test("null trigger returns false", () => {
  assert.equal(triggerMatches(null, "any message"), false);
});

// ── buildActiveIntentsText ────────────────────────────────────────────────────

test("returns empty string for empty array", () => {
  assert.equal(buildActiveIntentsText([]), "");
});

test("returns empty string for null", () => {
  assert.equal(buildActiveIntentsText(null), "");
});

test("contains ACTIVE INTENTS header and intent text", () => {
  const intents = [
    {
      intent_id: "int_abc",
      intent: "Offer redis-py docs",
      action: "surface_context",
      fire_mode: "once_per_conversation",
    },
  ];
  const text = buildActiveIntentsText(intents);
  assert.ok(text.includes("--- ACTIVE INTENTS ---"), "missing header");
  assert.ok(text.includes("--- END ACTIVE INTENTS ---"), "missing footer");
  assert.ok(text.includes("Offer redis-py docs"), "missing intent description");
});

// ── getSurfaceIntents ─────────────────────────────────────────────────────────

test("returns matching active intent", () => {
  const map = new Map([
    [
      "int_1",
      {
        intent_id: "int_1",
        status: "active",
        fire_mode: "always",
        intent: "redis docs",
        action: "surface_context",
        trigger: { type: "topic", value: "redis" },
      },
    ],
  ]);
  const result = getSurfaceIntents(map, new Set(), "tell me about redis", "active");
  assert.equal(result.length, 1);
});

test("skips once_per_conversation already fired", () => {
  const map = new Map([
    [
      "int_2",
      {
        intent_id: "int_2",
        status: "active",
        fire_mode: "once_per_conversation",
        intent: "redis docs",
        action: "surface_context",
        trigger: { type: "topic", value: "redis" },
      },
    ],
  ]);
  const fired = new Set(["int_2"]);
  const result = getSurfaceIntents(map, fired, "tell me about redis", "active");
  assert.equal(result.length, 0);
});

test("skips completed intents", () => {
  const map = new Map([
    [
      "int_3",
      {
        intent_id: "int_3",
        status: "completed",
        fire_mode: "always",
        intent: "redis docs",
        action: "surface_context",
        trigger: { type: "always" },
      },
    ],
  ]);
  const result = getSurfaceIntents(map, new Set(), "any message", "active");
  assert.equal(result.length, 0);
});

test("returns multiple matching intents", () => {
  const map = new Map([
    [
      "int_redis",
      {
        intent_id: "int_redis",
        status: "active",
        fire_mode: "always",
        intent: "redis topic",
        action: "surface_context",
        trigger: { type: "topic", value: "redis" },
      },
    ],
    [
      "int_always",
      {
        intent_id: "int_always",
        status: "active",
        fire_mode: "always",
        intent: "always present",
        action: "surface_context",
        trigger: { type: "always" },
      },
    ],
    [
      "int_mongo",
      {
        intent_id: "int_mongo",
        status: "active",
        fire_mode: "always",
        intent: "mongo topic",
        action: "surface_context",
        trigger: { type: "topic", value: "mongo" },
      },
    ],
  ]);
  const result = getSurfaceIntents(map, new Set(), "tell me about redis", "active");
  assert.equal(result.length, 2);
});
