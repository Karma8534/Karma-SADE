// test_system_prompt_k2.js — TDD: verify K2 capability guidance in system prompt
// Phase 1 Task 1.3: Karma needs batch command guidance + sudo awareness
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const promptPath = resolve(import.meta.dirname, "../../Memory/00-karma-system-prompt-live.md");
const prompt = readFileSync(promptPath, "utf-8");

test("system prompt contains batch command guidance (conserve tool iterations)", () => {
  assert.ok(
    prompt.includes("Conserve tool iterations"),
    "should contain iteration conservation guidance"
  );
});

test("system prompt contains && separator example for shell_run batching", () => {
  assert.ok(
    prompt.includes("---SEP---"),
    "should contain separator pattern for batching shell commands"
  );
});

test("system prompt contains sudo awareness for K2", () => {
  assert.ok(
    prompt.includes("sudo") && prompt.includes("systemctl restart aria"),
    "should document that karma has sudo and can restart aria"
  );
});

test("system prompt still contains shell_run tool reference", () => {
  assert.ok(
    prompt.includes("shell_run"),
    "should reference shell_run tool"
  );
});

test("system prompt still contains K2 ownership directive", () => {
  assert.ok(
    prompt.includes("K2 is your") || prompt.includes("K2 is Karma"),
    "should contain K2 ownership language"
  );
});
