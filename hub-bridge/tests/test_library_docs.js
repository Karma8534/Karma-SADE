// test_library_docs.js — TDD for get_library_docs library URL resolution
// Tests the pure resolveLibraryUrl() function from lib/library_docs.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { resolveLibraryUrl, LIBRARY_URLS } from "../lib/library_docs.js";

// ── Known libraries resolve to HTTPS URLs ────────────────────────────────────

test("resolveLibraryUrl: redis-py returns an https URL", () => {
  const url = resolveLibraryUrl("redis-py");
  assert.ok(url, "should return a URL");
  assert.ok(url.startsWith("https://"), "URL must use HTTPS");
});

test("resolveLibraryUrl: falkordb returns an https URL", () => {
  const url = resolveLibraryUrl("falkordb");
  assert.ok(url, "should return a URL");
  assert.ok(url.startsWith("https://"), "URL must use HTTPS");
});

test("resolveLibraryUrl: falkordb-py returns an https URL", () => {
  const url = resolveLibraryUrl("falkordb-py");
  assert.ok(url, "should return a URL");
  assert.ok(url.startsWith("https://"), "URL must use HTTPS");
});

test("resolveLibraryUrl: fastapi returns an https URL", () => {
  const url = resolveLibraryUrl("fastapi");
  assert.ok(url, "should return a URL");
  assert.ok(url.startsWith("https://"), "URL must use HTTPS");
});

// ── Unknown library returns null ──────────────────────────────────────────────

test("resolveLibraryUrl: unknown library returns null", () => {
  const url = resolveLibraryUrl("some-random-library-xyz");
  assert.equal(url, null);
});

test("resolveLibraryUrl: empty string returns null", () => {
  const url = resolveLibraryUrl("");
  assert.equal(url, null);
});

// ── LIBRARY_URLS map coverage ─────────────────────────────────────────────────

test("LIBRARY_URLS has at least 4 entries", () => {
  assert.ok(Object.keys(LIBRARY_URLS).length >= 4, "should map at least 4 libraries");
});
