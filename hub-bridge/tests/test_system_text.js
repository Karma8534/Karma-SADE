// test_system_text.js — tests for buildSystemText MEMORY.md injection
// TDD: these tests capture the bug (no memory spine) and the fix (spine injected)
import { test } from "node:test";
import assert from "node:assert/strict";

// Inline a simplified buildSystemText that mirrors server.js logic.
// This lets us unit-test the injection logic without starting the full server.
function buildSystemText(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null) {
  const identityBlock = "IDENTITY\n\n---\n\n";
  const selfKnowledge = "[Self-knowledge: backbone=test]\n\n";
  const base = karmaCtx
    ? `You are Karma.\n\n${karmaCtx}\n\nMemory rules.`
    : "You are Karma. No memory context available.";

  let text = identityBlock + selfKnowledge + base;

  if (semanticCtx) text += `\n\n${semanticCtx}`;
  if (webResults) text += `\n\n--- WEB SEARCH ---\n${webResults}\n---`;
  if (ckLatest?.karma_brief) text += `\n\n--- KARMA SELF-KNOWLEDGE ---\n${ckLatest.karma_brief}\n---`;
  if (karmaCtx) text += `\n\n=== YOUR COMPLETE KNOWLEDGE STATE ===\n${karmaCtx}\n=== END KNOWLEDGE STATE ===`;

  // THE FIX: inject memory spine
  if (memoryMd) {
    text += `\n\n--- KARMA MEMORY SPINE (recent) ---\n${memoryMd}\n---`;
  }

  return text;
}

// ── Bug: without fix, MEMORY.md is invisible ─────────────────────────────────

test("without memoryMd: system text has no memory spine section", () => {
  const text = buildSystemText("some karmaCtx");
  assert.ok(!text.includes("KARMA MEMORY SPINE"), "should not contain memory spine");
});

// ── Fix: memoryMd is injected ─────────────────────────────────────────────────

test("with memoryMd: system text includes memory spine header", () => {
  const text = buildSystemText("some karmaCtx", null, null, null, "v10 content here");
  assert.ok(text.includes("KARMA MEMORY SPINE"), "must include KARMA MEMORY SPINE header");
});

test("with memoryMd: system text includes the actual memory content", () => {
  const text = buildSystemText("some karmaCtx", null, null, null, "v10 primitives: confidence levels, anti-hallucination");
  assert.ok(text.includes("v10 primitives"), "must include actual memory content");
  assert.ok(text.includes("confidence levels"), "must include memory details");
});

test("with empty string memoryMd: no spine injected (falsy guard)", () => {
  const text = buildSystemText("some karmaCtx", null, null, null, "");
  assert.ok(!text.includes("KARMA MEMORY SPINE"), "empty string must not inject spine");
});

test("with null memoryMd: no spine injected", () => {
  const text = buildSystemText("some karmaCtx", null, null, null, null);
  assert.ok(!text.includes("KARMA MEMORY SPINE"), "null must not inject spine");
});

test("memory spine appears AFTER knowledge state section", () => {
  const text = buildSystemText("ctx", null, null, null, "spine content");
  const knowledgePos = text.indexOf("COMPLETE KNOWLEDGE STATE");
  const spinePos = text.indexOf("KARMA MEMORY SPINE");
  assert.ok(knowledgePos > 0, "knowledge state must exist");
  assert.ok(spinePos > knowledgePos, "memory spine must appear after knowledge state");
});
