// test_k2_tool_routing.js — TDD: verify k2.* tool routing to K2 /api/tools/execute
// Phase 2 Task 2.4: Hub-bridge routes k2.* prefixed tools to K2's MCP surface
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const serverPath = resolve(import.meta.dirname, "../app/server.js");
const source = readFileSync(serverPath, "utf-8");

// ── executeToolCall routes k2.* tools to K2 /api/tools/execute ──

test("executeToolCall has k2.* routing block before karma-server proxy", () => {
  // The k2.* handler should appear in executeToolCall, BEFORE the karma-server proxy
  const execToolCallStart = source.indexOf("async function executeToolCall(");
  assert.ok(execToolCallStart > 0, "executeToolCall function should exist");

  const k2Block = source.indexOf('toolName.startsWith("k2.")', execToolCallStart);
  assert.ok(k2Block > 0, 'should check for k2.* prefix in executeToolCall');

  const karmaProxy = source.indexOf("karma-server:8340/v1/tools/execute", execToolCallStart);
  assert.ok(karmaProxy > 0, "karma-server proxy should exist");
  assert.ok(k2Block < karmaProxy, "k2.* routing must come BEFORE karma-server proxy fallback");
});

test("k2.* routing strips k2. prefix and sends to ARIA_URL/api/tools/execute", () => {
  // Must strip "k2." prefix: "k2.file_read" → "file_read"
  assert.ok(
    source.includes('.replace("k2.", "")') || source.includes('.slice(3)') || source.includes(".substring(3)"),
    'should strip k2. prefix from tool name'
  );

  // Must POST to /api/tools/execute
  assert.ok(
    source.includes("/api/tools/execute"),
    'should reference /api/tools/execute endpoint'
  );
});

test("k2.* routing uses ARIA_SERVICE_KEY for auth", () => {
  // The k2 tool routing block should use X-Aria-Service-Key header
  const execToolCallStart = source.indexOf("async function executeToolCall(");
  const k2Section = source.indexOf('toolName.startsWith("k2.")', execToolCallStart);
  const karmaProxy = source.indexOf("karma-server:8340/v1/tools/execute", execToolCallStart);

  // Look for the service key header between k2.* check and karma-server proxy
  const k2Block = source.slice(k2Section, karmaProxy);
  assert.ok(
    k2Block.includes("X-Aria-Service-Key") || k2Block.includes("ARIA_SERVICE_KEY"),
    'k2.* routing block should use ARIA_SERVICE_KEY for auth'
  );
});

test("k2.* routing sends tool name and input in expected format", () => {
  // Must send { tool: <stripped_name>, input: <tool_input> }
  const execToolCallStart = source.indexOf("async function executeToolCall(");
  const k2Section = source.indexOf('toolName.startsWith("k2.")', execToolCallStart);
  const karmaProxy = source.indexOf("karma-server:8340/v1/tools/execute", execToolCallStart);
  const k2Block = source.slice(k2Section, karmaProxy);

  assert.ok(
    k2Block.includes("tool:") || k2Block.includes('"tool"'),
    'should send tool name in request body'
  );
  assert.ok(
    k2Block.includes("input:") || k2Block.includes('"input"') || k2Block.includes("toolInput"),
    'should send tool input in request body'
  );
});

// ── TOOL_DEFINITIONS includes k2.* tools ──

test("TOOL_DEFINITIONS includes at least k2.file_read", () => {
  assert.ok(
    source.includes('"k2.file_read"') || source.includes("'k2.file_read'"),
    'TOOL_DEFINITIONS should include k2.file_read'
  );
});

test("TOOL_DEFINITIONS includes k2.file_write", () => {
  assert.ok(
    source.includes('"k2.file_write"') || source.includes("'k2.file_write'"),
    'TOOL_DEFINITIONS should include k2.file_write'
  );
});

test("TOOL_DEFINITIONS includes k2.python_exec", () => {
  assert.ok(
    source.includes('"k2.python_exec"') || source.includes("'k2.python_exec'"),
    'TOOL_DEFINITIONS should include k2.python_exec'
  );
});

test("TOOL_DEFINITIONS includes k2.scratchpad_read", () => {
  assert.ok(
    source.includes('"k2.scratchpad_read"') || source.includes("'k2.scratchpad_read'"),
    'TOOL_DEFINITIONS should include k2.scratchpad_read'
  );
});

test("TOOL_DEFINITIONS includes k2.service_status", () => {
  assert.ok(
    source.includes('"k2.service_status"') || source.includes("'k2.service_status'"),
    'TOOL_DEFINITIONS should include k2.service_status'
  );
});
