// test_tool_iterations.js — TDD: verify MAX_TOOL_ITERATIONS is 12 (not 5)
// Phase 1 Task 1.1: Karma needs 12 iterations for multi-step K2 exploration
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// Read server.js source to verify the constant values
const serverPath = resolve(import.meta.dirname, "../app/server.js");
const source = readFileSync(serverPath, "utf-8");

// ── RED: All three tool-calling functions must have iteration limit >= 12 ────

test("callLLMWithTools: MAX_TOOL_ITERATIONS is 12", () => {
  // Find the constant in callLLMWithTools (Anthropic path)
  // It's defined as: const MAX_TOOL_ITERATIONS = N;
  const match = source.match(/async function callLLMWithTools[\s\S]*?const MAX_TOOL_ITERATIONS\s*=\s*(\d+)/);
  assert.ok(match, "MAX_TOOL_ITERATIONS should exist in callLLMWithTools");
  const value = parseInt(match[1], 10);
  assert.equal(value, 12, `callLLMWithTools MAX_TOOL_ITERATIONS should be 12, got ${value}`);
});

test("callGPTWithTools: MAX_ITERATIONS is 12", () => {
  // Find the constant in callGPTWithTools (OpenAI/Z.ai path)
  const match = source.match(/async function callGPTWithTools[\s\S]*?const MAX_ITERATIONS\s*=\s*(\d+)/);
  assert.ok(match, "MAX_ITERATIONS should exist in callGPTWithTools");
  const value = parseInt(match[1], 10);
  assert.equal(value, 12, `callGPTWithTools MAX_ITERATIONS should be 12, got ${value}`);
});

test("callK2WithTools: MAX_ITERATIONS is 12", () => {
  // Find the constant in callK2WithTools (K2 Ollama path)
  const match = source.match(/async function callK2WithTools[\s\S]*?const MAX_ITERATIONS\s*=\s*(\d+)/);
  assert.ok(match, "MAX_ITERATIONS should exist in callK2WithTools");
  const value = parseInt(match[1], 10);
  assert.equal(value, 12, `callK2WithTools MAX_ITERATIONS should be 12, got ${value}`);
});

test("no tool-calling function has MAX_TOOL_ITERATIONS or MAX_ITERATIONS set to 5", () => {
  // Safety net: ensure we never regress back to 5
  const fivePattern = /const MAX_(?:TOOL_)?ITERATIONS\s*=\s*5\s*;/g;
  const matches = source.match(fivePattern);
  assert.equal(matches, null, `Found ${matches?.length || 0} instances of MAX_*ITERATIONS = 5 — should be 0`);
});
