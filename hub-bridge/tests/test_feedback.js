import { test } from "node:test";
import assert from "node:assert/strict";
import { processFeedback, prunePendingWrites } from "../lib/feedback.js";

// ── prunePendingWrites ────────────────────────────────────────────────────────

test("prune: removes entries older than max_age_ms", () => {
  const map = new Map();
  map.set("old", { content: "x", ts: Date.now() - 60_000 });
  map.set("new", { content: "y", ts: Date.now() });
  prunePendingWrites(map, 30_000);
  assert.equal(map.has("old"), false);
  assert.equal(map.has("new"), true);
});

test("prune: no-op when all entries are fresh", () => {
  const map = new Map();
  map.set("a", { content: "x", ts: Date.now() });
  prunePendingWrites(map, 30_000);
  assert.equal(map.size, 1);
});

// ── processFeedback: thumbs up ────────────────────────────────────────────────

test("up without note: write_content is pending content", () => {
  const map = new Map();
  map.set("wr_1", { content: "Colby prefers dark mode", ts: Date.now() });
  const result = processFeedback(map, "wr_1", "up", undefined);
  assert.equal(result.write_content, "Colby prefers dark mode");
  assert.equal(result.dpo_pair.signal, "up");
  assert.equal(result.dpo_pair.proposed, "Colby prefers dark mode");
  assert.equal(result.dpo_pair.preferred, "Colby prefers dark mode");
  assert.equal(result.delete_key, "wr_1");
});

test("up with note: write_content is user's note instead", () => {
  const map = new Map();
  map.set("wr_1", { content: "Karma's phrasing", ts: Date.now() });
  const result = processFeedback(map, "wr_1", "up", "Colby's better phrasing");
  assert.equal(result.write_content, "Colby's better phrasing");
  assert.equal(result.dpo_pair.preferred, "Colby's better phrasing");
  assert.equal(result.dpo_pair.proposed, "Karma's phrasing");
});

// ── processFeedback: thumbs down ─────────────────────────────────────────────

test("down without note: write_content is null, DPO pair has null preferred", () => {
  const map = new Map();
  map.set("wr_1", { content: "bad write", ts: Date.now() });
  const result = processFeedback(map, "wr_1", "down", undefined);
  assert.equal(result.write_content, null);
  assert.equal(result.dpo_pair.signal, "down");
  assert.equal(result.dpo_pair.preferred, null);
  assert.equal(result.dpo_pair.proposed, "bad write");
});

test("down with note: write_content is null, preferred is user's note", () => {
  const map = new Map();
  map.set("wr_1", { content: "bad write", ts: Date.now() });
  const result = processFeedback(map, "wr_1", "down", "Here is the correct version");
  assert.equal(result.write_content, null);
  assert.equal(result.dpo_pair.preferred, "Here is the correct version");
});

// ── processFeedback: unknown write_id ────────────────────────────────────────

test("unknown write_id: no write_content, DPO pair has null proposed", () => {
  const map = new Map();
  const result = processFeedback(map, "unknown", "up", undefined);
  assert.equal(result.write_content, null);
  assert.equal(result.dpo_pair.proposed, null);
  assert.equal(result.delete_key, null);
});
