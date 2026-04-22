/**
 * proxy.js — Sovereign Harness Thin Proxy
 *
 * ~200 lines replacing 4820 lines of server.js.
 * Routes browser chat to CC --resume on P1 (primary) or K2 (failover).
 * Keeps: coordination bus, ambient capture, vault-file access, cypher proxy.
 * Kills: LLM routing, system prompt assembly, tool execution, pricing, modes.
 *
 * CC --resume IS the brain. This is just the door.
 */

import http from "http";
import https from "https";
import fs from "fs";
import path from "path";
import crypto from "crypto";
import { URL, pathToFileURL } from "url";

const _directRun = process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url;

// ── Config ───────────────────────────────────────────────────────────────────
const PORT = Number(process.env.PORT || "18090");
const VAULT_INTERNAL_URL = process.env.VAULT_INTERNAL_URL || "http://api:8080";
const VAULT_BASE_URL = process.env.VAULT_BASE_URL || "https://vault.arknexus.net";
const HUB_CHAT_TOKEN_FILE = process.env.HUB_CHAT_TOKEN_FILE || "/run/secrets/hub.chat.token.txt";
const HUB_CAPTURE_TOKEN_FILE = process.env.HUB_CAPTURE_TOKEN_FILE || "/run/secrets/hub.capture.token.txt";
const VAULT_BEARER_TOKEN_FILE = process.env.VAULT_BEARER_TOKEN_FILE || "/run/secrets/vault.bearer_token.txt";

// Harness nodes: P1 primary, K2 failover. Both run cc --resume via Max subscription ($0).
const HARNESS_P1 = process.env.HARNESS_P1_URL || "http://100.124.194.102:7891";
const HARNESS_K2 = process.env.HARNESS_K2_URL || "http://100.75.109.92:7891";
const HARNESS_TIMEOUT = Number(process.env.HARNESS_TIMEOUT || "120000");
const HEALTH_CACHE_MS = 30000; // cache health check result for 30s
const HEALTH_CHECK_TIMEOUT_MS = 8000; // 8s — Tailscale can spike above 3s transiently
const GOVERNOR_DAILY_CAP_USD = Number(process.env.GOVERNOR_DAILY_CAP_USD || "3");
const GOVERNOR_MAX_GROQ_FALLBACKS_PER_DAY = Number(process.env.GOVERNOR_MAX_GROQ_FALLBACKS_PER_DAY || "25");
const BREAKER_MAX_FAILS = Number(process.env.GOVERNOR_BREAKER_MAX_FAILS || "3");
const BREAKER_FILE = process.env.GOVERNOR_BREAKER_FILE || "/run/state/session_breakers.json";
const STRICT_STAGING_OVERWRITE = String(process.env.STRICT_STAGING_OVERWRITE || "1").toLowerCase() !== "0";

// ── Secrets ──────────────────────────────────────────────────────────────────
function readFileTrim(p) { return fs.readFileSync(p, "utf8").trim(); }
let HUB_CHAT_TOKEN = "", HUB_CAPTURE_TOKEN = "", VAULT_BEARER = "";
try { HUB_CHAT_TOKEN = readFileTrim(HUB_CHAT_TOKEN_FILE); } catch (e) { console.error("WARN: no chat token:", e.message); }
try { HUB_CAPTURE_TOKEN = readFileTrim(HUB_CAPTURE_TOKEN_FILE); } catch (e) { console.warn("WARN: no capture token:", e.message); }
try { VAULT_BEARER = readFileTrim(VAULT_BEARER_TOKEN_FILE); } catch (e) { console.warn("WARN: no vault bearer:", e.message); }

// ── Helpers ──────────────────────────────────────────────────────────────────
function json(res, status, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(status, { "content-type": "application/json", "content-length": Buffer.byteLength(body) });
  res.end(body);
}
function bearerToken(req) {
  const m = (req.headers["authorization"] || "").match(/^Bearer\s+(.+)$/i);
  return m?.[1]?.trim() || "";
}
function authChat(req) { return HUB_CHAT_TOKEN && bearerToken(req) === HUB_CHAT_TOKEN; }

// ── Tailscale IP allowlist for dangerous routes (C1 fix — adversarial review 2026-04-15) ──
// Only Tailscale IPs (100.x.x.x) and localhost can access /v1/shell, /v1/file, /v1/email, /v1/self-edit
const TAILSCALE_ALLOWLIST = new Set([
  "100.124.194.102", // P1
  "100.75.109.92",   // K2
  "100.92.67.70",    // vault-neo
  "127.0.0.1", "::1", "::ffff:127.0.0.1",
]);
function isDangerousRoute(url) {
  return url === "/v1/shell" || url.startsWith("/v1/file") || url === "/v1/email/send" || url.startsWith("/v1/self-edit/");
}
function isAllowedIP(req) {
  const fwd = (req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  const remote = req.socket?.remoteAddress?.replace("::ffff:", "") || "";
  return TAILSCALE_ALLOWLIST.has(fwd) || TAILSCALE_ALLOWLIST.has(remote);
}

function harnessHeaders(extra = {}) {
  return { Authorization: `Bearer ${HUB_CHAT_TOKEN}`, ...extra };
}
function internalJsonRequest(targetUrl, { method = "GET", headers = {}, body = null, timeoutMs = 10000 } = {}) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(targetUrl);
    const client = parsed.protocol === "https:" ? https : http;
    const req = client.request({
      protocol: parsed.protocol,
      hostname: parsed.hostname,
      port: parsed.port || (parsed.protocol === "https:" ? 443 : 80),
      path: `${parsed.pathname}${parsed.search}`,
      method,
      headers,
    }, (res) => {
      let data = "";
      res.on("data", (chunk) => { data += chunk; });
      res.on("end", () => {
        let parsedBody = null;
        try { parsedBody = data ? JSON.parse(data) : {}; } catch { parsedBody = { ok: false, error: data || "invalid_json" }; }
        resolve({ status: res.statusCode || 500, ok: (res.statusCode || 500) >= 200 && (res.statusCode || 500) < 300, json: parsedBody });
      });
    });
    req.on("error", reject);
    req.setTimeout(timeoutMs, () => req.destroy(new Error("timeout")));
    if (body) req.write(body);
    req.end();
  });
}
function authCapture(req) { return HUB_CAPTURE_TOKEN && bearerToken(req) === HUB_CAPTURE_TOKEN; }
function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("Access-Control-Max-Age", "86400");
}
function parseBody(req, maxSize = 2000000) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", c => { data += c; if (data.length > maxSize) { reject(new Error("body_too_large")); req.destroy(); } });
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });
}

// ── Harness failover ─────────────────────────────────────────────────────────
let _p1Healthy = null, _p1CheckedAt = 0;
let _k2Healthy = null, _k2CheckedAt = 0;

async function checkHealth(url, cache, checkedAt) {
  const now = Date.now();
  if (now - checkedAt < HEALTH_CACHE_MS && cache !== null) return cache;
  try {
    const r = await fetch(`${url}/health`, { signal: AbortSignal.timeout(HEALTH_CHECK_TIMEOUT_MS) });
    return r.ok;
  } catch { return false; }
}

// Shared constants
const BUSY_MSG = "Karma is busy with another request. Please wait a moment and try again.";

export function shouldBypassHarnessForV1Chat(_body = {}) {
  // The browser Nexus is the merged workspace. Preserving one continual session
  // is more important than shaving off a short-question RTT in the proxy.
  return false;
}

// ── Trace log (G1/G7) — per-request cost/routing data ─────────────────────
const _traceLog = [];
const TRACE_MAX = 50;
function traceAppend(entry) { _traceLog.push(entry); if (_traceLog.length > TRACE_MAX) _traceLog.shift(); }

const _governor = {
  day: new Date().toISOString().slice(0, 10),
  spendByModel: {},
  groqFallbackCalls: 0,
};
const _sessionBreaker = new Map();
const _sessionStore = new Map(); // H1 fix: server-side session persistence

// Load persisted sessions from disk at startup
try {
  const sessDir = "/run/state/sessions";
  if (fs.existsSync(sessDir)) {
    for (const f of fs.readdirSync(sessDir).filter(f => f.endsWith(".json"))) {
      try {
        const turns = JSON.parse(fs.readFileSync(`${sessDir}/${f}`, "utf8"));
        _sessionStore.set(f.replace(".json", ""), turns);
      } catch (_) {}
    }
    console.log(`[SESSION] Loaded ${_sessionStore.size} sessions from disk`);
  }
} catch (_) {}

function loadBreakerState() {
  try {
    if (!fs.existsSync(BREAKER_FILE)) return;
    const raw = JSON.parse(fs.readFileSync(BREAKER_FILE, "utf-8"));
    if (!raw || typeof raw !== "object") return;
    for (const [k, v] of Object.entries(raw)) {
      if (!v || typeof v !== "object") continue;
      _sessionBreaker.set(k, {
        fails: Number(v.fails || 0),
        halted: !!v.halted,
        lastError: String(v.lastError || ""),
        updatedAt: String(v.updatedAt || new Date().toISOString()),
      });
    }
  } catch {}
}

function saveBreakerState() {
  try {
    const obj = {};
    for (const [k, v] of _sessionBreaker.entries()) obj[k] = v;
    fs.writeFileSync(BREAKER_FILE, JSON.stringify(obj, null, 2), "utf-8");
  } catch {}
}

function ensureGovernorDay() {
  const day = new Date().toISOString().slice(0, 10);
  if (_governor.day === day) return;
  _governor.day = day;
  _governor.spendByModel = {};
  _governor.groqFallbackCalls = 0;
}

function recordSpend(model, usd = 0) {
  ensureGovernorDay();
  const key = String(model || "unknown");
  const val = Number(usd || 0);
  _governor.spendByModel[key] = Number(_governor.spendByModel[key] || 0) + (Number.isFinite(val) ? val : 0);
}

function totalSpendUsd() {
  ensureGovernorDay();
  return Object.values(_governor.spendByModel).reduce((a, b) => a + Number(b || 0), 0);
}

function cloudFallbackBlocked() {
  ensureGovernorDay();
  return totalSpendUsd() >= GOVERNOR_DAILY_CAP_USD || _governor.groqFallbackCalls >= GOVERNOR_MAX_GROQ_FALLBACKS_PER_DAY;
}

function markFailure(sessionId, err) {
  const sid = String(sessionId || "default");
  const prev = _sessionBreaker.get(sid) || { fails: 0, halted: false, lastError: "", updatedAt: new Date().toISOString() };
  const next = {
    fails: prev.fails + 1,
    halted: prev.fails + 1 >= BREAKER_MAX_FAILS,
    lastError: String(err || ""),
    updatedAt: new Date().toISOString(),
  };
  _sessionBreaker.set(sid, next);
  saveBreakerState();
  return next;
}

function clearFailure(sessionId) {
  const sid = String(sessionId || "default");
  if (_sessionBreaker.has(sid)) {
    _sessionBreaker.delete(sid);
    saveBreakerState();
  }
}

function breakerState(sessionId) {
  return _sessionBreaker.get(String(sessionId || "default")) || { fails: 0, halted: false, lastError: "", updatedAt: null };
}

// P1-first routing: P1 = Claude Code CLI ($0 Max sub), K2 = cloud cascade fallback
function harnessNodes() {
  return [
    { label: "P1", url: HARNESS_P1, getHealthy: () => _p1Healthy, setHealthy: v => { _p1Healthy = v; }, getCheckedAt: () => _p1CheckedAt, setChecked: () => { _p1CheckedAt = Date.now(); } },
    { label: "K2", url: HARNESS_K2, getHealthy: () => _k2Healthy, setHealthy: v => { _k2Healthy = v; }, getCheckedAt: () => _k2CheckedAt, setChecked: () => { _k2CheckedAt = Date.now(); } },
  ];
}

async function routeToHarness(message, sessionId) {
  const payload = JSON.stringify({ message, session_id: sessionId });
  const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${HUB_CHAT_TOKEN}`,
    "x-conversation-id": sessionId || "default",
  };
  const errors = [];
  let busyCount = 0;
  for (const node of harnessNodes()) {
    const h = await checkHealth(node.url, node.getHealthy(), node.getCheckedAt());
    node.setHealthy(h); node.setChecked();
    if (!h) { errors.push(`${node.label} health failed`); continue; }
    try {
      const r = await fetch(`${node.url}/cc`, { method: "POST", headers, body: payload, signal: AbortSignal.timeout(HARNESS_TIMEOUT) });
      if (r.status === 429) { busyCount++; errors.push(`${node.label} busy (another request in progress)`); continue; }
      const data = await r.json();
      // Detect K2 cascade false-positive: ok=true but response is an error message (P090)
      const respText = data.response || data.assistant_text || "";
      const isFalsePositive = respText.includes("all inference tiers failed") || respText.includes("[K2 harness:") || respText.includes("CORTEX ERROR") || respText.includes("Invalid API key") || respText.includes("Fix external API key");
      if (r.ok && data.ok !== false && !isFalsePositive) {
        console.log(`[HARNESS] ${node.label} responded OK`);
        data._harness = node.label;
        clearFailure(sessionId);
        return data;
      }
      if (isFalsePositive) { errors.push(`${node.label} false-positive: ${respText.slice(0, 80)}`); continue; }
      errors.push(`${node.label} ${r.status}: ${data.error || "non-ok"}`);
    } catch (e) { errors.push(`${node.label}: ${e.message}`); }
  }
  // If all nodes were busy, return specific busy message (not generic "failed")
  if (busyCount > 0) {
    console.warn("[HARNESS] All nodes busy:", errors.join("; "));
    const s = markFailure(sessionId, BUSY_MSG);
    return { ok: false, error: BUSY_MSG, breaker: s };
  }
  console.error("[HARNESS] All nodes failed:", errors.join("; "));
  const err = `All harness nodes failed: ${errors.join("; ")}`;
  const s = markFailure(sessionId, err);
  return { ok: false, error: err, breaker: s };
}

// ── Request Queue (Phase 1 — no dropped messages) ───────────────────────────
const _requestQueue = [];
const QUEUE_MAX = 10;
let _streamActive = false;

async function drainQueue() {
  if (_streamActive || !_requestQueue.length) return;
  // Skip dead clients (disconnected while waiting)
  while (_requestQueue.length && !_requestQueue[0].alive) { _requestQueue.shift(); console.log("[QUEUE] skipping dead client"); }
  if (!_requestQueue.length) return;
  const next = _requestQueue.shift();
  // Notify remaining queued clients of updated position
  _requestQueue.forEach((q, i) => {
    if (q.alive) try { q.clientRes.write(`data: ${JSON.stringify({ type: "queued", position: i + 1 })}\n\n`); } catch {}
  });
  console.log(`[QUEUE] dequeuing request (${_requestQueue.length} remaining)`);
  await executeStream(next.message, next.sessionId, next.effort, next.model, next.clientRes, next.files, next.budget);
}

// ── Harness streaming (SSE passthrough) ─────────────────────────────────────
async function routeToHarnessStream(message, sessionId, effort, model, clientRes, files, budget) {
  const b = breakerState(sessionId);
  if (b.halted) {
    if (!clientRes.headersSent) {
      clientRes.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", "Connection": "keep-alive", "Access-Control-Allow-Origin": "*" });
    }
    clientRes.write(`data: ${JSON.stringify({ type: "error", error: `Session halted by 3-strike breaker (${b.fails} fails). Resolve root cause or start new session.` })}\n\n`);
    clientRes.end();
    return;
  }
  if (_streamActive) {
    // CC is busy — queue instead of dropping
    if (_requestQueue.length >= QUEUE_MAX) {
      if (!clientRes.headersSent) clientRes.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", "Access-Control-Allow-Origin": "*" });
      clientRes.write(`data: ${JSON.stringify({ type: "error", error: "Karma is at capacity. Please try again in a moment." })}\n\n`);
      clientRes.end();
      return;
    }
    const pos = _requestQueue.length + 1;
    const entry = { message, sessionId, effort, model, clientRes, files, budget, alive: true };
    _requestQueue.push(entry);
    // Mark dead on disconnect — drainQueue skips dead entries (no splice race)
    clientRes.on("close", () => { entry.alive = false; console.log("[QUEUE] client disconnected, marked dead"); });
    if (!clientRes.headersSent) clientRes.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", "Connection": "keep-alive", "Access-Control-Allow-Origin": "*" });
    clientRes.write(`data: ${JSON.stringify({ type: "queued", position: pos, message: `Your message is queued (position ${pos}). Karma will respond shortly.` })}\n\n`);
    console.log(`[QUEUE] request queued at position ${pos}`);
    return;
  }
  await executeStream(message, sessionId, effort, model, clientRes, files, budget);
}

const BUSY_RETRY_DELAYS = [5000, 10000, 20000]; // 5s, 10s, 20s — total 35s max wait

async function executeStream(message, sessionId, effort, model, clientRes, files, budget) {
  _streamActive = true;
  const payload = JSON.stringify({ message, session_id: sessionId, effort, model, files, budget });
      const headers = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${HUB_CHAT_TOKEN}`,
        "x-conversation-id": sessionId || "default",
      };

  try {
  // Retry loop: if all nodes return 429 (CC busy externally), wait and retry
  for (let attempt = 0; attempt <= BUSY_RETRY_DELAYS.length; attempt++) {
    if (attempt > 0) {
      const delay = BUSY_RETRY_DELAYS[attempt - 1];
      console.log(`[HARNESS-STREAM] All nodes busy, retry ${attempt}/${BUSY_RETRY_DELAYS.length} in ${delay/1000}s`);
      // Tell client we're retrying (if SSE headers already sent)
      if (clientRes.headersSent) {
        try { clientRes.write(`data: ${JSON.stringify({ type: "queued", position: 0, message: `CC is busy. Retrying in ${delay/1000}s... (attempt ${attempt}/${BUSY_RETRY_DELAYS.length})` })}\n\n`); } catch {}
      }
      await new Promise(r => setTimeout(r, delay));
    }

    const nodes = harnessNodes();
    let allBusy = true;

    for (const node of nodes) {
      const h = await checkHealth(node.url, node.getHealthy(), node.getCheckedAt());
      node.setHealthy(h); node.setChecked();
      if (!h) continue;

      try {
        const r = await fetch(`${node.url}/cc/stream`, {
          method: "POST", headers, body: payload,
          signal: AbortSignal.timeout(HARNESS_TIMEOUT),
        });
        if (r.status === 429) {
          console.warn(`[HARNESS-STREAM] ${node.label} busy (429)`);
          continue;
        }
        if (!r.ok || !r.body) { allBusy = false; continue; }
        allBusy = false;
        console.log(`[HARNESS-STREAM] ${node.label} connected`);

        const reader = r.body.getReader();
        const decoder = new TextDecoder();
        let fullText = "";
        let streamCostUsd = 0;
        let streamModel = "";
        const ERROR_STRINGS = ["Invalid API key", "Fix external API key", "all inference tiers failed", "CORTEX ERROR", "claude exit"];
        let bufferedChunks = [];
        let headersSentForStream = false;
        let isErrorResponse = false;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });

          // Buffer first chunks to detect error before committing to client
          if (!headersSentForStream) {
            bufferedChunks.push(chunk);
            const allText = bufferedChunks.join("");
            if (ERROR_STRINGS.some(s => allText.includes(s))) {
              isErrorResponse = true;
              console.warn(`[HARNESS-STREAM] ${node.label} returned error in stream, trying next node`);
              try { reader.cancel(); } catch {}
              break;
            }
            // After accumulating enough or seeing a result/assistant event, commit
            if (allText.length > 200 || allText.includes('"type":"assistant"') || allText.includes('"type":"result"')) {
              if (!clientRes.headersSent) {
                clientRes.writeHead(200, {
                  "Content-Type": "text/event-stream",
                  "Cache-Control": "no-cache",
                  "Connection": "keep-alive",
                  "Access-Control-Allow-Origin": "*",
                });
              }
              headersSentForStream = true;
              for (const bc of bufferedChunks) clientRes.write(bc);
              bufferedChunks = [];
            }
            continue;
          }

          clientRes.write(chunk);
          try {
            for (const ln of chunk.split("\n")) {
              if (!ln.startsWith("data: ")) continue;
              const obj = JSON.parse(ln.slice(6));
              if (obj.type === "assistant") {
                for (const b of (obj.message?.content || [])) {
                  if (b.type === "text" && b.text) fullText = b.text;
                }
                if (obj.message?.model) streamModel = obj.message.model;
              }
              if (obj.type === "result" && obj.total_cost_usd !== undefined) {
                streamCostUsd = obj.total_cost_usd;
                if (obj.modelUsage) {
                  const models = Object.keys(obj.modelUsage);
                  if (models.length) streamModel = models[0];
                }
              }
            }
          } catch {}
        }
        if (isErrorResponse) continue; // Try next node
        if (!headersSentForStream && bufferedChunks.length) {
          // Flush any remaining buffered chunks
          if (!clientRes.headersSent) {
            clientRes.writeHead(200, {
              "Content-Type": "text/event-stream", "Cache-Control": "no-cache",
              "Connection": "keep-alive", "Access-Control-Allow-Origin": "*",
            });
          }
          for (const bc of bufferedChunks) clientRes.write(bc);
        }
        clientRes.end();

        if (streamCostUsd > 0) console.log(`[COST] stream request: $${streamCostUsd.toFixed(4)} via ${streamModel} (Max sub — no actual charge)`);
        recordSpend(streamModel || "cc-sovereign", streamCostUsd || 0);
        postResponseSideEffects({ message, assistantText: fullText, sessionId, costUsd: streamCostUsd, model: streamModel, tagSuffix: "-STREAM" });
        traceAppend({ ts: new Date().toISOString(), path: "stream", harness: node.label, model: streamModel || "cc-sovereign", usd: streamCostUsd, message_len: message.length, ok: true });

        return; // Success
      } catch (e) { allBusy = false; console.error(`[HARNESS-STREAM] ${node.label} error:`, e.message); }
    }

    // If not all-busy (some nodes failed for non-429 reasons), don't retry
    if (!allBusy) break;
  }

    // All stream attempts failed — try non-stream fallback (K2 /cc doesn't support streaming)
    if (!clientRes.headersSent) {
      console.log("[HARNESS-STREAM] All stream nodes failed, trying non-stream fallback");
      const fallbackData = await routeToHarness(message, sessionId);
      if (fallbackData && fallbackData.ok !== false) {
        clientRes.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", "Connection": "keep-alive", "Access-Control-Allow-Origin": "*" });
        const text = fallbackData.response || fallbackData.assistant_text || "(no response)";
        clientRes.write(`data: ${JSON.stringify({ type: "assistant", message: { role: "assistant", content: [{ type: "text", text }], model: fallbackData.provider || "k2-cascade" } })}\n\n`);
        clientRes.write(`data: ${JSON.stringify({ type: "result", total_cost_usd: 0 })}\n\n`);
        clientRes.end();
        postResponseSideEffects({ message, assistantText: text, sessionId, costUsd: 0, model: fallbackData.provider || "k2-cascade", tagSuffix: "-FALLBACK" });
      } else {
        clientRes.writeHead(502, { "Content-Type": "text/event-stream", "Access-Control-Allow-Origin": "*" });
        clientRes.write(`data: ${JSON.stringify({ type: "error", error: fallbackData?.error || BUSY_MSG })}\n\n`);
        clientRes.end();
      }
    } else {
      clientRes.end();
    }
  } finally {
    _streamActive = false;
    drainQueue().catch(e => console.error("[QUEUE] drain error:", e.message));
  }
}

// ── Coordination Bus ─────────────────────────────────────────────────────────
const COORD_FILE = "/run/state/coordination.jsonl";
const COORD_TTL_MS = 24 * 60 * 60 * 1000;
const COORD_MAX_ENTRIES = 100;
const _coordCache = new Map();

function loadCoordFromDisk() {
  try {
    if (!fs.existsSync(COORD_FILE)) return;
    const lines = fs.readFileSync(COORD_FILE, "utf-8").trim().split("\n").filter(Boolean);
    const now = Date.now();
    for (const line of lines) {
      try {
        const e = JSON.parse(line);
        if (now - new Date(e.created_at).getTime() < COORD_TTL_MS) _coordCache.set(e.id, e);
      } catch {}
    }
    if (_coordCache.size > 0) console.log(`[COORD] loaded ${_coordCache.size} entries from disk`);
  } catch {}
}
function appendCoordDisk(entry) { try { fs.appendFileSync(COORD_FILE, JSON.stringify(entry) + "\n"); } catch {} }
function saveCoordDisk() { try { fs.writeFileSync(COORD_FILE, [..._coordCache.values()].map(e => JSON.stringify(e)).join("\n") + "\n"); } catch {} }
function coordId() { return `coord_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`; }
function evictCoord() {
  const now = Date.now();
  for (const [id, e] of _coordCache) { if (now - new Date(e.created_at).getTime() > COORD_TTL_MS) _coordCache.delete(id); }
  if (_coordCache.size > COORD_MAX_ENTRIES) {
    const sorted = [..._coordCache.entries()].sort((a, b) => new Date(a[1].created_at) - new Date(b[1].created_at));
    for (const [id] of sorted.slice(0, _coordCache.size - COORD_MAX_ENTRIES)) _coordCache.delete(id);
  }
}
// S155: Sovereign directive — auto-approve agent bus posts after 2 min wall clock
// S156: Extended from karma-only to all agents — kiki pulse + CC hourly don't need Sovereign approval
const KARMA_AUTO_APPROVE_MS = 2 * 60 * 1000;
// S157: agents that self-report verified results get instant auto-approve
const INSTANT_APPROVE_SENDERS = new Set(["regent", "karma", "cc", "cc-watchdog", "kcc"]);

function autoApproveKarmaEntries() {
  const now = Date.now();
  for (const [id, e] of _coordCache) {
    if (e.status === "pending" && e.type !== "task" && e.urgency !== "blocking") {
      const age = now - new Date(e.created_at).getTime();
      // Instant approve for known agents; 2-min delay for unknown senders
      const threshold = INSTANT_APPROVE_SENDERS.has(e.from) ? 0 : KARMA_AUTO_APPROVE_MS;
      if (age > threshold) {
        e.status = "approved";
        e.approved_by = "auto-sovereign";
        e.approved_at = new Date().toISOString();
        console.log(`[COORD] Auto-approved ${e.from} entry ${id} (${Math.round(age/1000)}s old)`);
      }
    }
  }
}
if (_directRun) {
  setInterval(autoApproveKarmaEntries, 30000); // Check every 30s
}

// ── AGORA Bridge Queue (bidirectional transport) ────────────────────────────
const AGORA_FILE = "/run/state/agora_messages.jsonl";
const AGORA_TTL_MS = 24 * 60 * 60 * 1000;
const AGORA_MAX_ENTRIES = 5000;
const _agoraMessages = [];
const _agoraById = new Map();

function agoraId() { return `agora_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`; }
function ensureRunStateDir() { try { fs.mkdirSync("/run/state", { recursive: true }); } catch {} }

function evictAgora() {
  const cutoff = Date.now() - AGORA_TTL_MS;
  const kept = [];
  for (const m of _agoraMessages) {
    const t = new Date(m.ts || 0).getTime();
    if (!Number.isFinite(t) || t < cutoff) continue;
    kept.push(m);
  }
  while (kept.length > AGORA_MAX_ENTRIES) kept.shift();
  _agoraMessages.length = 0;
  _agoraById.clear();
  for (const m of kept) {
    _agoraMessages.push(m);
    _agoraById.set(m.id, m);
  }
}

function saveAgoraDisk() {
  try {
    ensureRunStateDir();
    fs.writeFileSync(AGORA_FILE, _agoraMessages.map((m) => JSON.stringify(m)).join("\n") + (_agoraMessages.length ? "\n" : ""));
  } catch {}
}

function appendAgoraDisk(entry) {
  try {
    ensureRunStateDir();
    fs.appendFileSync(AGORA_FILE, JSON.stringify(entry) + "\n");
  } catch {}
}

function loadAgoraFromDisk() {
  try {
    if (!fs.existsSync(AGORA_FILE)) return;
    const lines = fs.readFileSync(AGORA_FILE, "utf-8").split("\n").filter(Boolean);
    for (const line of lines) {
      try {
        const msg = JSON.parse(line);
        if (!msg?.id) continue;
        _agoraMessages.push(msg);
        _agoraById.set(msg.id, msg);
      } catch {}
    }
    evictAgora();
    if (_agoraMessages.length > 0) console.log(`[AGORA] loaded ${_agoraMessages.length} messages from disk`);
  } catch {}
}

function agoraRolePrefix(from = "") {
  const v = String(from || "").trim().toLowerCase();
  if (v === "karma_hub" || v === "karma" || v === "regent" || v === "vesper") return "[Karma]";
  if (v === "codex_p1" || v === "codex") return "[Codex]";
  return "";
}

function normalizeAgoraContent(from, content) {
  const text = String(content || "");
  const prefix = agoraRolePrefix(from);
  if (!prefix) return text;
  if (text.startsWith("[Karma]") || text.startsWith("[Codex]")) return text;
  return `${prefix} ${text}`;
}

function enqueueAgoraMessage(input = {}) {
  const entry = {
    id: String(input.id || agoraId()),
    thread_id: String(input.thread_id || input.session_id || "default"),
    from: String(input.from || "").trim(),
    to: String(input.to || "").trim(),
    type: String(input.type || "message").trim(),
    content: normalizeAgoraContent(input.from, input.content),
    ts: String(input.ts || input.timestamp || new Date().toISOString()),
    reply_to: input.reply_to ? String(input.reply_to) : null,
    meta: input.meta && typeof input.meta === "object" ? input.meta : {},
    acked_at: null,
    acked_by: null,
  };
  _agoraMessages.push(entry);
  _agoraById.set(entry.id, entry);
  evictAgora();
  appendAgoraDisk(entry);
  return entry;
}

function validateAgoraEnvelope(data) {
  const from = String(data?.from || "").trim();
  const to = String(data?.to || "").trim();
  const type = String(data?.type || "").trim();
  const id = String(data?.id || "").trim();
  if (!from || !to || !type) return { ok: false, error: "from,to,type required" };
  if (id && id.length > 120) return { ok: false, error: "id_too_long" };
  if (from.length > 80 || to.length > 80 || type.length > 40) return { ok: false, error: "field_too_long" };
  return { ok: true };
}

// ── Content-hash dedup (S155 Rule 36) ───────────────────────────────────────
const _recentHashes = new Set();
const DEDUP_MAX = 500;
function contentHash(text) { return crypto.createHash("sha256").update(String(text)).digest("hex").slice(0, 16); }
function isDuplicate(text) {
  const h = contentHash(text);
  if (_recentHashes.has(h)) return true;
  _recentHashes.add(h);
  if (_recentHashes.size > DEDUP_MAX) { const first = _recentHashes.values().next().value; _recentHashes.delete(first); }
  return false;
}

// ── Vault helpers ────────────────────────────────────────────────────────────
const VAULT_FILE_ALIASES = {
  "MEMORY.md": "/karma/MEMORY.md",
  "consciousness": "/karma/ledger/consciousness.jsonl",
  "collab": "/karma/ledger/collab.jsonl",
  "candidates": "/karma/ledger/candidates.jsonl",
  "system-prompt": "/karma/repo/Memory/00-karma-system-prompt-live.md",
  "session-handoff": "/karma/repo/Memory/08-session-handoff.md",
  "session-summary": "/karma/repo/Memory/11-session-summary-latest.md",
  "core-architecture": "/karma/repo/Memory/01-core-architecture.md",
  "cc-brief": "/karma/repo/cc-session-brief.md",
};

function buildVaultRecord({ type, content, tags, source, confidence, memcube }) {
  return {
    type: type || "log",
    content: { text: content, format: "text" },
    tags: Array.isArray(tags) ? tags : [],
    source: { ref: source || "sovereign-proxy", kind: "system" },
    confidence: confidence ?? 0.9,
    verification: { verified_at: new Date().toISOString(), verifier: "sovereign-proxy", notes: "auto", protocol_version: "1.0", status: "verified" },
    created_at: new Date().toISOString(),
    memcube: memcube || { version: 1, tier: "raw", lineage: null, promotion_state: "none", decay_policy: "default" },
  };
}
// MemCube helper: read memcube from entry, defaulting for old entries
function readMemcube(entry) {
  if (entry && entry.memcube) return entry.memcube;
  return { version: 0, tier: "raw", lineage: null, promotion_state: "none", decay_policy: "default" };
}
// Shared fire-and-forget: vault write + chatlog append + cortex ingest
function postResponseSideEffects({ message, assistantText, sessionId, costUsd, model, tagSuffix }) {
  const costStr = (costUsd !== undefined && costUsd !== null) ? costUsd.toFixed(4) : "0.0000";
  const modelStr = model || "cc-sovereign";
  const suffix = tagSuffix || "";
  const chatContent = `[CHAT${suffix}] user: ${message.slice(0, 200)}\nassistant: ${assistantText.slice(0, 500)} [cost:$${costStr},model:${modelStr}]`;
  // S155 Rule 36: content-hash dedup — skip duplicate vault writes
  if (!isDuplicate(chatContent)) {
    vaultPost("/v1/memory", VAULT_BEARER, buildVaultRecord({
      type: "log", content: chatContent,
      tags: ["chat", "sovereign-harness", "hub", ...(suffix ? [suffix.replace("-", "").toLowerCase()] : [])], source: "sovereign-proxy",
    })).catch(e => console.error("[VAULT] write failed:", e.message));
  } else {
    console.log("[VAULT] skipped duplicate chat entry");
  }
  try {
    fs.appendFileSync("/run/state/nexus-chat.jsonl", JSON.stringify({
      ts: new Date().toISOString(), user: message.slice(0, 500),
      assistant: assistantText.slice(0, 1000), session_id: sessionId,
    }) + "\n");
  } catch (e) { console.warn("[CHATLOG] append failed:", e.message); }
  fetch("http://100.75.109.92:7892/ingest", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ label: `nexus-chat-${Date.now()}`, text: chatContent }),
    signal: AbortSignal.timeout(5000),
  }).catch(e => console.warn("[CORTEX] ingest failed:", e.message));
  // Phase 3 brain wire: write every chat turn to claude-mem via cc_server
  fetch(`${HARNESS_P1}/memory/save`, {
    method: "POST", headers: { "Content-Type": "application/json", "Authorization": `Bearer ${HUB_CHAT_TOKEN}` },
    body: JSON.stringify({ text: chatContent, title: `Nexus chat${suffix}`, project: "Karma_SADE" }),
    signal: AbortSignal.timeout(5000),
  }).catch(e => console.warn("[CLAUDE-MEM] save failed:", e.message));
}

async function vaultPost(vaultPath, bearer, payload) {
  // Use internal URL from inside Docker (external URL fails DNS resolution in container)
  const url = new URL(vaultPath, VAULT_INTERNAL_URL).toString();
  const resp = await fetch(url, {
    method: "POST",
    headers: { Authorization: `Bearer ${bearer}`, "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
  return { status: resp.status, text: await resp.text() };
}

// ── HTTP Server ──────────────────────────────────────────────────────────────
const PUBLIC_DIR = path.join(path.dirname(new URL(import.meta.url).pathname), "public");

const server = http.createServer(async (req, res) => {
  setCors(res);
  if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }
  const originalUrl = req.url || "/";
  // /cc is the anchored Julian surface; normalize /cc/* API/UI paths to root routes.
  if (originalUrl === "/cc" || originalUrl === "/cc/") {
    req.url = "/";
  } else if (originalUrl.startsWith("/cc/")) {
    req.url = originalUrl.slice(3);
  }
  console.log(`[REQUEST] ${req.method} ${originalUrl} -> ${req.url}`);

  // ── C1 FIX: Block dangerous routes from non-Tailscale IPs ──────────
  if (isDangerousRoute(req.url) && !isAllowedIP(req)) {
    console.warn(`[BLOCKED] ${req.method} ${req.url} from ${req.socket?.remoteAddress} — not in Tailscale allowlist`);
    return json(res, 403, { ok: false, error: "forbidden: Tailscale network required for this endpoint" });
  }

  try {
    // ── Static files ───────────────────────────────────────────────────
    // Next.js static export (Sprint 3b — Task 1)
    if (req.method === "GET" && (req.url === "/" || req.url === "/index.html")) {
      const nexusPath = path.join(PUBLIC_DIR, "nexus", "index.html");
      if (fs.existsSync(nexusPath)) {
        const html = fs.readFileSync(nexusPath, "utf-8");
        res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
        return res.end(html);
      }
      // Fallback to unified.html if Next.js not deployed yet
      const html = fs.readFileSync(path.join(PUBLIC_DIR, "unified.html"), "utf-8");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      return res.end(html);
    }
    // Next.js _next/ static assets
    if (req.method === "GET" && req.url.startsWith("/_next/")) {
      const assetPath = path.join(PUBLIC_DIR, "nexus", req.url);
      if (fs.existsSync(assetPath)) {
        const ext = path.extname(assetPath);
        const types = { ".js": "application/javascript", ".css": "text/css", ".json": "application/json", ".woff2": "font/woff2", ".png": "image/png", ".svg": "image/svg+xml" };
        res.writeHead(200, { "Content-Type": types[ext] || "application/octet-stream", "Cache-Control": "public, max-age=31536000, immutable" });
        return res.end(fs.readFileSync(assetPath));
      }
    }
    // Legacy unified.html fallback
    if (req.method === "GET" && (req.url === "/legacy" || req.url === "/unified.html")) {
      const html = fs.readFileSync(path.join(PUBLIC_DIR, "unified.html"), "utf-8");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      return res.end(html);
    }

    // ── /agora bridge API — bidirectional message transport ───────────
    if (req.method === "GET" && req.url.startsWith("/agora/health")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      evictAgora();
      const now = Date.now();
      const unacked = _agoraMessages.filter((m) => !m.acked_at);
      const byTarget = {};
      for (const m of unacked) byTarget[m.to] = (byTarget[m.to] || 0) + 1;
      return json(res, 200, {
        ok: true,
        service: "agora-bridge",
        ts: new Date().toISOString(),
        queue_depth: _agoraMessages.length,
        unacked_depth: unacked.length,
        oldest_unacked_ms: unacked.length ? (now - new Date(unacked[0].ts).getTime()) : 0,
        by_target: byTarget,
      });
    }

    if (req.method === "POST" && (req.url === "/agora/messages" || req.url === "/agora")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const raw = await parseBody(req, 200000);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
      const valid = validateAgoraEnvelope(body);
      if (!valid.ok) return json(res, 400, { ok: false, error: valid.error });

      if (body.id && _agoraById.has(body.id)) {
        const existing = _agoraById.get(body.id);
        return json(res, 200, { ok: true, duplicate: true, message: existing });
      }
      const message = enqueueAgoraMessage(body);
      return json(res, 202, { ok: true, message });
    }

    if (req.method === "GET" && req.url.startsWith("/agora/messages")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      evictAgora();
      const params = new URL(req.url, `http://${req.headers.host}`).searchParams;
      const to = String(params.get("to") || "").trim();
      if (!to) return json(res, 400, { ok: false, error: "to required" });
      const limit = Math.min(Math.max(parseInt(params.get("limit") || "20", 10) || 20, 1), 200);
      const cursor = String(params.get("cursor") || "").trim();
      let rows = _agoraMessages.filter((m) => m.to === to && !m.acked_at);
      if (cursor) {
        const idx = rows.findIndex((m) => m.id === cursor);
        if (idx >= 0) rows = rows.slice(idx + 1);
      }
      rows = rows.slice(0, limit);
      const next_cursor = rows.length ? rows[rows.length - 1].id : cursor || null;
      return json(res, 200, { ok: true, count: rows.length, messages: rows, next_cursor });
    }

    if (req.method === "POST" && req.url === "/agora/ack") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const raw = await parseBody(req, 20000);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
      const id = String(body.id || "").trim();
      const by = String(body.by || "").trim();
      if (!id || !by) return json(res, 400, { ok: false, error: "id,by required" });
      const msg = _agoraById.get(id);
      if (!msg) return json(res, 404, { ok: false, error: "not_found" });
      msg.acked_at = new Date().toISOString();
      msg.acked_by = by;
      saveAgoraDisk();
      return json(res, 200, { ok: true, message: msg });
    }

    // ── /agora — Evolution Dashboard ───────────────────────────────────
    if (req.method === "GET" && (req.url === "/agora" || req.url === "/agora/")) {
      try {
        const html = fs.readFileSync(path.join(PUBLIC_DIR, "agora.html"), "utf-8");
        res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
        return res.end(html);
      } catch { return json(res, 500, { ok: false, error: "agora.html not found" }); }
    }

    // ── /agora/events — evolution events API ─────────────────────────
    if (req.method === "GET" && req.url.startsWith("/agora/events")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      evictCoord();
      // Filter bus: evolution events only, exclude heartbeats
      const evolutionKeywords = ["promote", "evolution", "self-edit", "vesper", "pattern", "spine", "learn", "growth", "pitfall", "decision", "proof", "direction", "insight", "self-improve", "SESSION WRAP", "SESSION START", "SOVEREIGN"];
      let entries = [..._coordCache.values()].filter(e => {
        const content = (e.content || "").toLowerCase();
        if (content.includes("heartbeat")) return false; // exclude noise
        if (content.includes("watchdog ack")) return false; // exclude ack loops
        return evolutionKeywords.some(k => content.toLowerCase().includes(k.toLowerCase())) || e.from === "cc";
      });
      entries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      entries = entries.slice(0, 30);

      // Fetch LIVE evolution state from K2 cortex + spine (no CC needed)
      let k2Evolution = null;
      try {
        const [healthResp, spineResp] = await Promise.all([
          fetch("http://100.75.109.92:7892/health", { signal: AbortSignal.timeout(3000) }),
          fetch("http://100.75.109.92:7892/spine", { signal: AbortSignal.timeout(3000) }),
        ]);
        const cortex = healthResp.ok ? await healthResp.json() : null;
        const spine = spineResp.ok ? await spineResp.json() : null;
        k2Evolution = { cortex, spine };
      } catch (e) { k2Evolution = { error: e.message }; }

      // Chat log
      let chatEdits = [];
      try {
        const logPath = "/run/state/nexus-chat.jsonl";
        if (fs.existsSync(logPath)) {
          const lines = fs.readFileSync(logPath, "utf-8").trim().split("\n").filter(Boolean);
          chatEdits = lines.slice(-20).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
        }
      } catch {}
      return json(res, 200, { ok: true, evolution_events: entries, recent_chats: chatEdits, k2_evolution: k2Evolution });
    }

    const reqUrlObj = new URL(req.url, "http://localhost");
    const reqPath = reqUrlObj.pathname;
    const reqQuery = reqUrlObj.search || "";

    // ── /v1/learnings — what Karma has actually learned (from claude-mem)
    if (req.method === "GET" && (reqPath === "/v1/learnings" || reqPath === "/v1/learned")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        // Fetch from P1 cc_server (has direct claude-mem access)
        const r = await fetch(`${HARNESS_P1}/v1/learnings${reqQuery}`, { headers: harnessHeaders(), signal: AbortSignal.timeout(25000) });
        const data = await r.json();
        return json(res, r.ok ? 200 : 502, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Learnings unavailable: ${e.message}` });
      }
    }

    // ── Canonical memory/session/model routes required by Nexus boot and panels ──
    if (req.method === "GET" && (reqPath === "/memory/wakeup" || reqPath === "/memory/session")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await fetch(`${HARNESS_P1}${reqPath}${reqQuery}`, {
          headers: harnessHeaders(),
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `${reqPath} unavailable: ${e.message}` });
      }
    }
    if (req.method === "GET" && reqPath === "/v1/model-policy") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await fetch(`${HARNESS_P1}/v1/model-policy`, {
          headers: harnessHeaders(),
          signal: AbortSignal.timeout(8000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Model policy unavailable: ${e.message}` });
      }
    }
    if (req.method === "GET" && reqPath === "/v1/agents/list") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await fetch(`${HARNESS_P1}/v1/agents/list`, {
          headers: harnessHeaders(),
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Agents list unavailable: ${e.message}` });
      }
    }
    if (req.method === "POST" && reqPath === "/v1/agents/spawn") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const raw = await parseBody(req, 100000);
        const r = await fetch(`${HARNESS_P1}/v1/agents/spawn`, {
          method: "POST",
          headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: raw,
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Agent spawn unavailable: ${e.message}` });
      }
    }
    if (req.method === "POST" && reqPath.startsWith("/v1/agents/cancel/")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await fetch(`${HARNESS_P1}${reqPath}`, {
          method: "POST",
          headers: harnessHeaders(),
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Agent cancel unavailable: ${e.message}` });
      }
    }
    if (req.method === "GET" && reqPath === "/v1/routing/options") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await fetch(`${HARNESS_P1}/v1/routing/options`, {
          headers: harnessHeaders(),
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Routing options unavailable: ${e.message}` });
      }
    }
    if (req.method === "GET" && reqPath === "/v1/permissions/summary") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await fetch(`${HARNESS_P1}/v1/permissions/summary`, {
          headers: harnessHeaders(),
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Permissions summary unavailable: ${e.message}` });
      }
    }
    if (req.method === "POST" && reqPath === "/v1/permissions/toggle") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const raw = await parseBody(req, 20000);
        const r = await fetch(`${HARNESS_P1}/v1/permissions/toggle`, {
          method: "POST",
          headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: raw,
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Permissions toggle unavailable: ${e.message}` });
      }
    }
    if (req.method === "GET" && reqPath === "/v1/plugins/list") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await fetch(`${HARNESS_P1}/v1/plugins/list`, {
          headers: harnessHeaders(),
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Plugins list unavailable: ${e.message}` });
      }
    }
    if (req.method === "POST" && reqPath === "/v1/skills/create") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const raw = await parseBody(req, 20000);
        const r = await fetch(`${HARNESS_P1}/v1/skills/create`, {
          method: "POST",
          headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: raw,
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Skill create unavailable: ${e.message}` });
      }
    }
    if ((req.method === "GET" || req.method === "POST") && reqPath.match(/^\/v1\/session\/[^/]+$/)) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const sid = decodeURIComponent(reqPath.split("/")[3] || "").trim();
      if (!sid) return json(res, 400, { ok: false, error: "session_id required" });
      const upstream = `${HARNESS_P1}/v1/session/${encodeURIComponent(sid)}`;
      try {
        if (req.method === "GET") {
          const r = await fetch(upstream, { headers: harnessHeaders(), signal: AbortSignal.timeout(30000) });
          const data = await r.json();
          return json(res, r.status, data);
        }
        const raw = await parseBody(req, 100000);
        const r = await fetch(upstream, {
          method: "POST",
          headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: raw,
          signal: AbortSignal.timeout(30000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `/v1/session unavailable: ${e.message}` });
      }
    }

    // ── /v1/skills — Skills list for UI (Baseline #21) ──────────────────
    if (req.method === "GET" && req.url === "/v1/skills") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await fetch(`${HARNESS_P1}/skills`, { headers: harnessHeaders(), signal: AbortSignal.timeout(5000) });
        const data = await r.json();
        return json(res, r.ok ? 200 : 502, data);
      } catch (e) { return json(res, 502, { ok: false, error: `Skills unavailable: ${e.message}` }); }
    }

    // ── /v1/hooks — Hooks status for UI (Baseline #22) ─────────────────
    if (req.method === "GET" && req.url === "/v1/hooks") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await fetch(`${HARNESS_P1}/hooks`, { headers: harnessHeaders(), signal: AbortSignal.timeout(5000) });
        const data = await r.json();
        return json(res, r.ok ? 200 : 502, data);
      } catch (e) { return json(res, 502, { ok: false, error: `Hooks unavailable: ${e.message}` }); }
    }

    // ── /v1/file — File read/write for editor (R2) ───────────────────
    if (req.method === "GET" && req.url.startsWith("/v1/file?")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const parsed = new URL(req.url, "http://localhost");
        const filePath = parsed.searchParams.get("path") || "";
        const r = await internalJsonRequest(`${HARNESS_P1}/file?path=${encodeURIComponent(filePath)}`, {
          headers: harnessHeaders(),
          timeoutMs: 5000,
        });
        return json(res, r.ok ? 200 : 502, r.json);
      } catch (e) { return json(res, 502, { ok: false, error: `File read failed: ${e.message}` }); }
    }
    if (req.method === "POST" && req.url === "/v1/file") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const body = JSON.parse(await parseBody(req));
      try {
        const r = await fetch(`${HARNESS_P1}/file`, {
          method: "POST", headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: JSON.stringify(body), signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.ok ? 200 : 502, data);
      } catch (e) { return json(res, 502, { ok: false, error: `File write failed: ${e.message}` }); }
    }

    // ── /v1/shell — Shell execution (R2) ──────────────────────────────
    if (req.method === "POST" && req.url === "/v1/shell") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const body = JSON.parse(await parseBody(req));
      try {
        const r = await fetch(`${HARNESS_P1}/shell`, {
          method: "POST", headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: JSON.stringify(body), signal: AbortSignal.timeout(35000),
        });
        const data = await r.json();
        return json(res, r.ok ? 200 : 502, data);
      } catch (e) { return json(res, 502, { ok: false, error: `Shell unavailable: ${e.message}` }); }
    }

    // ── /v1/git/status — Git status for UI (R2) ─────────────────────────
    if (req.method === "GET" && req.url === "/v1/git/status") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await internalJsonRequest(`${HARNESS_P1}/git/status`, {
          headers: harnessHeaders(),
          timeoutMs: 5000,
        });
        return json(res, r.ok ? 200 : 502, r.json);
      } catch (e) { return json(res, 502, { ok: false, error: `Git unavailable: ${e.message}` }); }
    }

    // ── Health ─────────────────────────────────────────────────────────
    if (req.method === "GET" && req.url === "/health") {
      return json(res, 200, { ok: true, service: "sovereign-proxy", ts: new Date().toISOString() });
    }

    // ── /v1/surface — merged state endpoint (CP5) ─────────────────────
    if (req.method === "GET" && req.url === "/v1/surface") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await internalJsonRequest(`${HARNESS_P1}/v1/surface`, {
          headers: harnessHeaders(),
          timeoutMs: 30000,
        });
        return json(res, r.ok ? 200 : 502, r.json);
      } catch (e) { return json(res, 502, { ok: false, error: `Surface endpoint unreachable: ${e.message}` }); }
    }

    // ── /v1/k2/* — Direct K2 endpoints (CC-INDEPENDENT, S160 inversion) ──
    if (req.url.startsWith("/v1/k2/")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const K2_CORTEX = process.env.K2_CORTEX_URL || "http://100.75.109.92:7892";
      const subpath = req.url.replace("/v1/k2", "");

      if (req.method === "POST" && subpath === "/consolidate") {
        // Trigger consolidation on K2 via SSH (runs vesper_watchdog consolidate_memories)
        try {
          const { execSync } = require("child_process");
          const result = execSync(
            'ssh -o ConnectTimeout=5 karma@192.168.0.226 "cd /mnt/c/dev/Karma/k2/aria && python3 -c \\"import vesper_watchdog as w; r=w.consolidate_memories(); print(r)\\""',
            { timeout: 90000, encoding: "utf-8" }
          ).trim();
          return json(res, 200, { ok: true, consolidated: parseInt(result) || 0, source: "k2-direct" });
        } catch (e) {
          return json(res, 502, { ok: false, error: `K2 consolidation failed: ${e.message?.slice(0, 100)}` });
        }
      }

      if (req.method === "POST" && subpath === "/query") {
        // Direct cortex query — no CC wrapper
        try {
          const raw = await parseBody(req);
          let body = {};
          try { body = raw ? JSON.parse(raw) : {}; } catch { body = {}; }
          const r = await fetch(`${K2_CORTEX}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: body.query || "", temperature: 0.3 }),
            signal: AbortSignal.timeout(30000),
          });
          const data = await r.json();
          return json(res, 200, data);
        } catch (e) {
          return json(res, 502, { ok: false, error: `K2 cortex query failed: ${e.message?.slice(0, 100)}` });
        }
      }

      if (req.method === "GET" && subpath === "/context") {
        // Direct cortex context — no CC wrapper
        try {
          const r = await fetch(`${K2_CORTEX}/context`, { signal: AbortSignal.timeout(15000) });
          const data = await r.json();
          return json(res, 200, data);
        } catch (e) {
          return json(res, 502, { ok: false, error: `K2 context failed: ${e.message?.slice(0, 100)}` });
        }
      }

      return json(res, 404, { ok: false, error: `Unknown K2 endpoint: ${subpath}` });
    }

    // [DELETED] /v1/shell duplicate handler was here (S160 inversion). Shadowed by R2 handler at line 947.
    // Removed 2026-04-15 — adversarial review finding C3.

    // ── /v1/email/inbox — CC-independent inbox check (S160) ───────────────
    if (req.method === "GET" && req.url === "/v1/email/inbox") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await internalJsonRequest(`${HARNESS_P1}/email/inbox`, {
          headers: harnessHeaders(),
          timeoutMs: 15000,
        });
        return json(res, r.ok ? 200 : 502, r.json);
      } catch (e) { return json(res, 502, { ok: false, error: `Inbox check failed: ${e.message?.slice(0, 100)}` }); }
    }

    // ── /v1/email/send — CC-independent email (S160 inversion) ────────────
    if (req.method === "POST" && req.url === "/v1/email/send") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const raw = await parseBody(req);
        let body = {};
        try { body = raw ? JSON.parse(raw) : {}; } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
        const r = await fetch(`${HARNESS_P1}/email/send`, {
          method: "POST",
          headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: JSON.stringify(body),
          signal: AbortSignal.timeout(15000),
        });
        const data = await r.json();
        return json(res, r.ok ? 200 : 502, data);
      } catch (e) { return json(res, 502, { ok: false, error: `Email failed: ${e.message?.slice(0, 100)}` }); }
    }

    // ── /v1/wip — WIP panel data (S160) ─────────────────────────────────
    if (req.method === "GET" && req.url === "/v1/wip") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await internalJsonRequest(`${HARNESS_P1}/v1/wip`, {
          headers: harnessHeaders(),
          timeoutMs: 10000,
        });
        return json(res, r.ok ? 200 : 502, r.json);
      } catch (e) { return json(res, 502, { ok: false, error: `WIP endpoint unreachable: ${e.message}` }); }
    }
    if (req.method === "POST" && req.url === "/v1/wip/todo-add") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const raw = await parseBody(req, 20000);
      try {
        const r = await fetch(`${HARNESS_P1}/v1/wip/todo-add`, {
          method: "POST",
          headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: raw,
          signal: AbortSignal.timeout(10000),
        });
        const data = await r.json();
        return json(res, r.status, data);
      } catch (e) { return json(res, 502, { ok: false, error: `WIP todo-add failed: ${e.message}` }); }
    }

    // ── /v1/files — file tree for Context Panel (Sprint 4c) ────────────
    if (req.method === "GET" && req.url === "/v1/files") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await internalJsonRequest(`${HARNESS_P1}/files`, {
          headers: harnessHeaders(),
          timeoutMs: 5000,
        });
        return json(res, r.ok ? 200 : 502, r.json);
      } catch (e) { return json(res, 502, { ok: false, error: "files endpoint unreachable" }); }
    }

    // ── /v1/memory/search — memory search for Context Panel ──────────
    if (req.method === "GET" && req.url.startsWith("/v1/memory/search")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const querySuffix = req.url.includes("?") ? req.url.slice(req.url.indexOf("?")) : "";
        const r = await fetch(`${HARNESS_P1}/memory/search${querySuffix}`, {
          method: "GET",
          headers: harnessHeaders(),
          signal: AbortSignal.timeout(5000),
        });
        const data = await r.json();
        return json(res, r.ok ? 200 : 502, data);
      } catch (e) { return json(res, 502, { ok: false, error: "memory search unreachable" }); }
    }
    if (req.method === "POST" && req.url.startsWith("/v1/memory/search")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const raw = await parseBody(req, 10000);
      try {
        const r = await fetch(`${HARNESS_P1}/memory/search`, {
          method: "POST", headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: raw, signal: AbortSignal.timeout(5000),
        });
        const data = await r.json();
        return json(res, 200, data);
      } catch (e) { return json(res, 502, { ok: false, error: "memory search unreachable" }); }
    }

    // ── /v1/memory/save — memory write for browser workspace ──────────
    if (req.method === "POST" && req.url === "/v1/memory/save") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const raw = await parseBody(req, 20000);
      try {
        const r = await fetch(`${HARNESS_P1}/memory/save`, {
          method: "POST", headers: harnessHeaders({ "Content-Type": "application/json" }),
          body: raw, signal: AbortSignal.timeout(5000),
        });
        const data = await r.json();
        return json(res, r.ok ? 200 : 502, data);
      } catch (e) { return json(res, 502, { ok: false, error: "memory save unreachable" }); }
    }

    // ── /v1/spine — K2 spine status for Context Panel ────────────────
    if (req.method === "GET" && req.url === "/v1/spine") {
      try {
        const r = await fetch("http://100.75.109.92:7892/spine", { signal: AbortSignal.timeout(3000) });
        if (r.ok) return json(res, 200, await r.json());
        return json(res, 502, { ok: false, error: "K2 spine unreachable" });
      } catch (e) { return json(res, 502, { ok: false, error: "K2 spine unreachable" }); }
    }

    // ── /v1/agents-status — MCP/Skills/Hooks for Context Panel (#20-22) ──
    if (req.method === "GET" && req.url === "/v1/agents-status") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const r = await internalJsonRequest(`${HARNESS_P1}/agents-status`, {
          headers: harnessHeaders(),
          timeoutMs: 5000,
        });
        return json(res, r.status, r.json);
      } catch (e) { return json(res, 502, { ok: false, error: "agents-status unreachable" }); }
    }

    // ── /v1/self-edit/* — Self-Edit Engine (Sprint 4d) ─────────────────
    if (req.url.startsWith("/v1/self-edit/")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const subPath = req.url.replace("/v1/self-edit/", "/self-edit/");
      try {
        const fetchOpts = { signal: AbortSignal.timeout(5000), headers: harnessHeaders({ "Content-Type": "application/json" }) };
        if (req.method === "GET") {
          const r = await internalJsonRequest(`${HARNESS_P1}${subPath}`, {
            headers: fetchOpts.headers,
            timeoutMs: 5000,
          });
          return json(res, r.status, r.json);
        }
        if (req.method === "POST") {
          const raw = await parseBody(req, 50000);
          fetchOpts.method = "POST";
          fetchOpts.body = raw;
          const r = await fetch(`${HARNESS_P1}${subPath}`, fetchOpts);
          return json(res, r.status, await r.json());
        }
      } catch (e) { return json(res, 502, { ok: false, error: "self-edit endpoint unreachable" }); }
    }

    // ── /v1/cancel — abort current CC subprocess ───────────────────────
    if (req.method === "GET" && req.url === "/v1/cancel") {
      // Cancel on whichever node is active
      const targets = [HARNESS_P1, HARNESS_K2];
      for (const t of targets) {
        try { await fetch(`${t}/cancel`, { signal: AbortSignal.timeout(3000) }); } catch {}
      }
      return json(res, 200, { ok: true, cancelled: true });
    }

    // ── /v1/status — system status ────────────────────────────────────
    if (req.method === "GET" && req.url === "/v1/status") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      _p1Healthy = await checkHealth(HARNESS_P1, _p1Healthy, _p1CheckedAt); _p1CheckedAt = Date.now();
      _k2Healthy = await checkHealth(HARNESS_K2, _k2Healthy, _k2CheckedAt); _k2CheckedAt = Date.now();
      ensureGovernorDay();
      return json(res, 200, {
        ok: true, service: "sovereign-proxy", ts: new Date().toISOString(),
        harness: { p1: { url: HARNESS_P1, healthy: _p1Healthy }, k2: { url: HARNESS_K2, healthy: _k2Healthy } },
        cost: { model: "cc-sovereign (Max subscription)", usd_per_request: 0, note: "H8: CC --resume runs on Max subscription. API cost shown in stream result events is accounting only, not billed. Actual charge: $0/request. Monthly sub: $100-200." },
        governor: {
          day: _governor.day,
          daily_cap_usd: GOVERNOR_DAILY_CAP_USD,
          total_spend_usd: totalSpendUsd(),
          groq_fallback_calls: _governor.groqFallbackCalls,
          groq_fallback_limit: GOVERNOR_MAX_GROQ_FALLBACKS_PER_DAY,
          cloud_blocked: cloudFallbackBlocked(),
          active_session_breakers: [..._sessionBreaker.values()].filter(v => v.halted).length,
        },
      });
    }

    // ── /v1/governor/breaker — deterministic breaker control/probe ───────
    if (req.method === "POST" && req.url === "/v1/governor/breaker") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const body = JSON.parse(await parseBody(req, 20000));
      const sessionId = String(body.session_id || "").trim();
      if (!sessionId) return json(res, 400, { ok: false, error: "session_id required" });
      const fails = Math.max(0, Number(body.fails ?? BREAKER_MAX_FAILS));
      const halted = body.halted === undefined ? fails >= BREAKER_MAX_FAILS : !!body.halted;
      const st = {
        fails,
        halted,
        lastError: String(body.last_error || (halted ? "manual-breaker-set" : "")),
        updatedAt: new Date().toISOString(),
      };
      _sessionBreaker.set(sessionId, st);
      saveBreakerState();
      return json(res, 200, { ok: true, session_id: sessionId, breaker: st });
    }
    if (req.method === "DELETE" && req.url.startsWith("/v1/governor/breaker/")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const sessionId = decodeURIComponent(req.url.replace("/v1/governor/breaker/", "").trim());
      if (!sessionId) return json(res, 400, { ok: false, error: "session_id required" });
      _sessionBreaker.delete(sessionId);
      saveBreakerState();
      return json(res, 200, { ok: true, session_id: sessionId, cleared: true });
    }

    // ── /v1/feedback — thumbs up/down → coordination bus (P092 fix) ────
    if (req.method === "POST" && req.url === "/v1/feedback") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const body = JSON.parse(await parseBody(req, 10000));
      const signal = body.signal || "unknown";
      const entry = { id: coordId(), from: "sovereign", to: "karma", type: "feedback", urgency: "informational",
        status: "pending", parent_id: null, response_id: null, content: `[FEEDBACK ${signal}] ${body.note || ""}`.trim(),
        context: body.turn_id || body.write_id || null, created_at: new Date().toISOString() };
      _coordCache.set(entry.id, entry); appendCoordDisk(entry);
      return json(res, 200, { ok: true, id: entry.id });
    }

    // ── /v1/trace — per-request cost/routing log (G1/G7) ──────────────
    if (req.method === "GET" && req.url === "/v1/trace") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      return json(res, 200, { ok: true, count: _traceLog.length, entries: _traceLog });
    }

    // ── /v1/runtime/truth — live system state (L1 fix, adversarial review 2026-04-15) ──
    if (req.method === "GET" && req.url === "/v1/runtime/truth") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      _p1Healthy = await checkHealth(HARNESS_P1, _p1Healthy, _p1CheckedAt); _p1CheckedAt = Date.now();
      _k2Healthy = await checkHealth(HARNESS_K2, _k2Healthy, _k2CheckedAt); _k2CheckedAt = Date.now();
      // Query FalkorDB node count via karma-server
      let falkordbNodes = null;
      try {
        const fRes = await internalJsonRequest(`${VAULT_INTERNAL_URL}/v1/cypher`, {
          method: "POST", headers: { Authorization: `Bearer ${VAULT_BEARER}`, "Content-Type": "application/json" },
          body: JSON.stringify({ query: "MATCH (n) RETURN count(n) as total" }), timeoutMs: 5000,
        });
        const fData = fRes.json;
        falkordbNodes = fData?.result?.[0]?.[0] ?? fData?.result ?? null;
      } catch (_) {}
      // Read ledger line count via vault-file
      let ledgerCount = null;
      try {
        const lRes = await internalJsonRequest(`${VAULT_INTERNAL_URL}/v1/stats`, { timeoutMs: 5000 });
        const lData = lRes.json;
        ledgerCount = lData?.ledger_entries ?? null;
      } catch (_) {}
      return json(res, 200, {
        ok: true, ts: new Date().toISOString(), service: "sovereign-proxy",
        harness: { p1: { url: HARNESS_P1, healthy: _p1Healthy }, k2: { url: HARNESS_K2, healthy: _k2Healthy } },
        inference: { model: "cc-sovereign (CC --resume via Max)", cost_per_request: "$0" },
        falkordb: { nodes: falkordbNodes },
        ledger: { entries: ledgerCount },
        governor: { day: _governor.day, daily_cap_usd: GOVERNOR_DAILY_CAP_USD, total_spend_usd: totalSpendUsd(), cloud_blocked: cloudFallbackBlocked() },
        coordination_bus: { entries: _coordCache.size },
      });
    }

    // ── /v1/session — server-side session persistence (H1 fix, adversarial review 2026-04-15) ──
    if (req.method === "POST" && req.url.match(/^\/v1\/session\/[^/]+\/save$/)) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const sessionId = req.url.split("/")[3];
      const body = JSON.parse(await parseBody(req, 100000));
      if (!_sessionStore.has(sessionId)) _sessionStore.set(sessionId, []);
      const turns = _sessionStore.get(sessionId);
      turns.push({ ...body, ts: new Date().toISOString() });
      // Prune to max 100 turns
      while (turns.length > 100) turns.shift();
      // Persist to disk
      try {
        const dir = "/run/state/sessions";
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(`${dir}/${sessionId}.json`, JSON.stringify(turns));
      } catch (e) { console.warn(`[SESSION] disk write failed for ${sessionId}: ${e.message}`); }
      return json(res, 201, { ok: true, session_id: sessionId, turn_count: turns.length });
    }
    if (req.method === "GET" && req.url.match(/^\/v1\/session\/[^/]+\/history$/)) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const sessionId = req.url.split("/")[3];
      // Try in-memory first, then disk
      let turns = _sessionStore.get(sessionId) || null;
      if (!turns) {
        try {
          const data = fs.readFileSync(`/run/state/sessions/${sessionId}.json`, "utf8");
          turns = JSON.parse(data);
          _sessionStore.set(sessionId, turns); // cache
        } catch (_) { turns = []; }
      }
      return json(res, 200, turns);
    }

    // ── /v1/chat — proxy to sovereign harness with local pre-classification ──
    if (req.method === "POST" && req.url === "/v1/chat") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const raw = await parseBody(req, 500000);
      let body; try { body = JSON.parse(raw); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
      const message = body.message || body.content || "";
      if (!message) return json(res, 400, { ok: false, error: "message required" });
      const sessionId = body.session_id || "";
      const b = breakerState(sessionId);
      if (b.halted) {
        return json(res, 423, {
          ok: false,
          error: `session_halted_by_breaker (${b.fails} fails)`,
          breaker: b,
        });
      }

      if (shouldBypassHarnessForV1Chat(body)) {
        return json(res, 500, { ok: false, error: "proxy_harness_bypass_disabled" });
      }

      // ── Streaming path (SSE) ──────────────────────────────────────────
      if (body.stream === true) {
        return routeToHarnessStream(message, sessionId, body.effort, body.model, res, body.files, body.budget);
      }

      // ── Batch path (JSON, backward compat) — with Groq fallback on CC lock ──
      let result;
      try {
        const ccPromise = routeToHarness(message, sessionId);
        const batchHarnessTimeout = Math.min(HARNESS_TIMEOUT, 45000);
        const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error("CC_TIMEOUT")), batchHarnessTimeout));
        result = await Promise.race([ccPromise, timeoutPromise]);
      } catch (ccErr) {
        markFailure(sessionId, ccErr?.message || "CC_TIMEOUT");
        if (cloudFallbackBlocked()) {
          return json(res, 503, { ok: false, error: "cloud_fallback_blocked_by_governor", governor: { total_spend_usd: totalSpendUsd(), cap_usd: GOVERNOR_DAILY_CAP_USD, groq_fallback_calls: _governor.groqFallbackCalls } });
        }
        // CC timed out or failed — try Groq as emergency fallback
        let groqFallbackKey = "";
        for (const p of ["/karma/repo/.groq-api-key", "/home/neo/karma-sade/.groq-api-key"]) {
          try { groqFallbackKey = require("fs").readFileSync(p, "utf-8").trim(); if (groqFallbackKey) break; } catch {}
        }
        if (groqFallbackKey) {
          try {
            const gRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
              method: "POST",
              headers: { "Authorization": `Bearer ${groqFallbackKey}`, "Content-Type": "application/json" },
              body: JSON.stringify({ model: "llama-3.3-70b-versatile", messages: [{ role: "system", content: "You are Karma. Be helpful and concise." }, { role: "user", content: message }], max_tokens: 500, temperature: 0.3 }),
              signal: AbortSignal.timeout(10000),
            });
            if (gRes.ok) {
              const gData = await gRes.json();
              const gAnswer = gData.choices?.[0]?.message?.content || "";
              if (gAnswer) {
                _governor.groqFallbackCalls += 1;
                recordSpend("groq-fallback", 0);
                postResponseSideEffects({ message, assistantText: gAnswer, sessionId, costUsd: 0, model: "groq-fallback" });
                return json(res, 200, { ok: true, response: gAnswer, assistant_text: gAnswer, model: "groq-fallback", routing: "cc-locked-groq-fallback", cost_usd: 0 });
              }
            }
          } catch {}
        }
        return json(res, 504, { ok: false, error: "CC unavailable and Groq fallback failed" });
      }

      // Fire-and-forget: vault + chatlog + cortex (shared with stream path)
      const assistantText = result.response || result.assistant_text || "";
      postResponseSideEffects({ message, assistantText, sessionId, costUsd: 0, model: "cc-sovereign" });

      // Trace log (G1/G7)
      traceAppend({ ts: new Date().toISOString(), path: "batch", harness: result._harness || "unknown", model: "cc-sovereign", usd: 0, message_len: message.length, ok: result.ok !== false });

      // Normalize response for unified.html compatibility
      return json(res, result.ok === false ? 502 : 200, {
        ok: result.ok !== false,
        assistant_text: result.response || result.assistant_text || result.error || "",
        tool_log: result.tool_log || [],
        model: "cc-sovereign",
        deep_mode: true,
        usd_estimate: 0,
        canonical: { ok: true, model: "cc-sovereign", deep_mode: true, spend_cap_usd: 0, spend_used_usd: 0 },
      });
    }

    // ── Coordination Bus: POST ────────────────────────────────────────
    if (req.method === "POST" && req.url === "/v1/coordination/post") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const data = JSON.parse(await parseBody(req, 100000));
      const { from, to, content, urgency } = data;
      if (!from || !to || !content || !urgency) return json(res, 400, { ok: false, error: "missing required fields" });
      const entry = { id: coordId(), from, to, type: data.type || "request", urgency, status: "pending",
        parent_id: data.parent_id || null, response_id: null, content, context: data.context || null, created_at: new Date().toISOString() };
      if (entry.parent_id && _coordCache.has(entry.parent_id)) {
        const parent = _coordCache.get(entry.parent_id); parent.response_id = entry.id; parent.status = "resolved";
      }
      _coordCache.set(entry.id, entry); appendCoordDisk(entry); evictCoord();
      // Fire-and-forget vault write
      vaultPost("/v1/memory", VAULT_BEARER, buildVaultRecord({
        type: "log", content: `[COORD] ${from}\u2192${to} (${urgency}): ${content}`,
        tags: ["coordination", "bus", from, to], source: "coordination-bus",
      })).catch(() => {});
      return json(res, 200, { ok: true, id: entry.id, entry });
    }

    // ── Coordination Bus: GET ─────────────────────────────────────────
    if (req.method === "GET" && req.url === "/v1/coordination") req.url = "/v1/coordination/recent?limit=20";
    if (req.method === "GET" && req.url.startsWith("/v1/coordination/recent")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      evictCoord();
      const params = new URL(req.url, `http://${req.headers.host}`).searchParams;
      let entries = [..._coordCache.values()];
      const filterTo = params.get("to"), filterStatus = params.get("status"), filterFrom = params.get("from");
      if (filterTo) entries = entries.filter(e => e.to === filterTo);
      if (filterFrom) entries = entries.filter(e => e.from === filterFrom);
      if (filterStatus) entries = entries.filter(e => e.status === filterStatus);
      entries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      entries = entries.slice(0, Math.min(parseInt(params.get("limit") || "10", 10), 50));
      return json(res, 200, { ok: true, count: entries.length, entries });
    }

    // ── Coordination Bus: PATCH ───────────────────────────────────────
    if (req.method === "PATCH" && req.url.startsWith("/v1/coordination/")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const parsed = new URL(req.url, "http://localhost");
      const id = parsed.pathname.replace("/v1/coordination/", "").trim();
      if (!id || id === "recent" || id === "post") return json(res, 400, { ok: false, error: "invalid coordination id" });
      if (!_coordCache.has(id)) return json(res, 404, { ok: false, error: "not found" });
      const data = JSON.parse(await parseBody(req, 100000));
      const entry = _coordCache.get(id);
      if (data.status) entry.status = data.status;
      if (data.response_id) entry.response_id = data.response_id;
      saveCoordDisk();
      return json(res, 200, { ok: true, entry });
    }

    // ── Ambient capture ───────────────────────────────────────────────
    if (req.method === "POST" && req.url === "/v1/ambient") {
      if (!authCapture(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const body = JSON.parse(await parseBody(req));
      if (!body.type || !body.content) return json(res, 400, { ok: false, error: "type and content required" });
      const record = buildVaultRecord({ type: body.type, content: body.content, tags: body.tags, source: body.source?.ref || String(body.source || "ambient") });
      const r = await vaultPost("/v1/memory", VAULT_BEARER, record);
      let vaultId; try { vaultId = JSON.parse(r.text)?.id; } catch { vaultId = null; }
      return json(res, r.status < 300 ? 200 : 502, { ok: r.status < 300, id: vaultId });
    }

    // ── Vault file access ─────────────────────────────────────────────
    if (req.method === "GET" && req.url.startsWith("/v1/vault-file/")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const parsed = new URL(req.url, "http://localhost");
      const alias = decodeURIComponent(parsed.pathname.replace("/v1/vault-file/", "").trim());
      if (!alias || !VAULT_FILE_ALIASES[alias]) return json(res, 404, { ok: false, error: "alias_not_found", available: Object.keys(VAULT_FILE_ALIASES) });
      let content; try { content = fs.readFileSync(VAULT_FILE_ALIASES[alias], "utf-8"); } catch { return json(res, 404, { ok: false, error: "file_not_found" }); }
      const tail = parsed.searchParams.get("tail");
      if (tail) { const n = parseInt(tail, 10); if (n > 0) content = content.split("\n").slice(-n).join("\n"); }
      return json(res, 200, { ok: true, alias, content });
    }

    // ── PATCH MEMORY.md ───────────────────────────────────────────────
    if (req.method === "PATCH" && req.url === "/v1/vault-file/MEMORY.md") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const body = JSON.parse(await parseBody(req, 500000));
      const filePath = VAULT_FILE_ALIASES["MEMORY.md"];
      if (body.append !== undefined) {
        fs.appendFileSync(filePath, "\n" + body.append);
        return json(res, 200, { ok: true, action: "append", bytes_appended: Buffer.byteLength(body.append) });
      } else if (body.content !== undefined && body.confirm_overwrite === true) {
        if (STRICT_STAGING_OVERWRITE && body.allow_production_overwrite !== true) {
          return json(res, 423, {
            ok: false,
            error: "production_overwrite_blocked",
            required: "allow_production_overwrite:true",
            note: "Staging-first safeguard active",
          });
        }
        fs.writeFileSync(filePath, body.content, "utf-8");
        return json(res, 200, { ok: true, action: "overwrite", bytes: Buffer.byteLength(body.content) });
      }
      return json(res, 400, { ok: false, error: "provide 'append' or 'content'+'confirm_overwrite:true'" });
    }

    // ── FalkorDB Cypher proxy ─────────────────────────────────────────
    if (req.method === "POST" && req.url === "/v1/cypher") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const body = JSON.parse(await parseBody(req, 500000));
      const cypher = body.cypher || body.query || body.input?.cypher || body.tool_input?.cypher;
      if (!cypher) return json(res, 400, { ok: false, error: "missing_cypher" });
      try {
        const r = await fetch("http://karma-server:8340/v1/tools/execute", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tool_name: "graph_query", tool_input: { cypher } }),
        });
        return json(res, r.status, await r.json());
      } catch (e) { return json(res, 502, { ok: false, error: "karma_server_unavailable", message: e.message }); }
    }

    // ── 404 ───────────────────────────────────────────────────────────
    json(res, 404, { ok: false, error: "not_found" });
  } catch (e) {
    console.error(`[ERROR] ${req.method} ${req.url}:`, e.message);
    if (!res.headersSent) json(res, 500, { ok: false, error: e.message });
  }
});

// ── Startup ──────────────────────────────────────────────────────────────────
if (_directRun) {
  loadCoordFromDisk();
  loadAgoraFromDisk();
  loadBreakerState();
  server.listen(PORT, () => {
    console.log(`[SOVEREIGN-PROXY] Listening on port ${PORT}`);
    console.log(`[SOVEREIGN-PROXY] Harness P1: ${HARNESS_P1}`);
    console.log(`[SOVEREIGN-PROXY] Harness K2: ${HARNESS_K2}`);
    console.log(`[SOVEREIGN-PROXY] Chat token: ${HUB_CHAT_TOKEN ? "loaded" : "MISSING"}`);
    console.log(`[SOVEREIGN-PROXY] Vault bearer: ${VAULT_BEARER ? "loaded" : "MISSING"}`);
    console.log(`[SOVEREIGN-PROXY] Cost per request: $0.00 (Max subscription)`);
  });
}
