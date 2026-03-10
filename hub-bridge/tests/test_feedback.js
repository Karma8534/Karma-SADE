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

// ── processFeedback: general feedback (turn_id path, no pending write) ────────

test("general up: write_content null, dpo_pair has turn_id", () => {
  const r = processFeedback(new Map(), null, "up", undefined, "turn_abc");
  assert.equal(r.write_content, null);
  assert.equal(r.dpo_pair.turn_id, "turn_abc");
  assert.equal(r.dpo_pair.write_id, null);
  assert.equal(r.delete_key, null);
});

test("general down with note: dpo_pair captures correction", () => {
  const r = processFeedback(new Map(), null, "down", "Better answer", "turn_abc");
  assert.equal(r.write_content, null);
  assert.equal(r.dpo_pair.preferred, "Better answer");
  assert.equal(r.dpo_pair.signal, "down");
  assert.equal(r.dpo_pair.turn_id, "turn_abc");
});

test("general up with note: write_content still null (no pending write)", () => {
  const r = processFeedback(new Map(), null, "up", "My note", "turn_abc");
  assert.equal(r.write_content, null);
  assert.equal(r.dpo_pair.preferred, "My note");
  assert.equal(r.dpo_pair.turn_id, "turn_abc");
});

test("both null: dpo_pair has null write_id and null turn_id", () => {
  const r = processFeedback(new Map(), null, "up", undefined, null);
  assert.equal(r.dpo_pair.write_id, null);
  assert.equal(r.dpo_pair.turn_id, null);
  assert.equal(r.write_content, null);
});
