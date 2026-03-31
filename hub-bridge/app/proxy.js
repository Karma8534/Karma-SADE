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
import fs from "fs";
import path from "path";
import { URL } from "url";

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

// ── Trace log (G1/G7) — per-request cost/routing data ─────────────────────
const _traceLog = [];
const TRACE_MAX = 50;
function traceAppend(entry) { _traceLog.push(entry); if (_traceLog.length > TRACE_MAX) _traceLog.shift(); }

// P1-first routing: P1 = Claude Code CLI ($0 Max sub), K2 = cloud cascade fallback
function harnessNodes() {
  return [
    { label: "P1", url: HARNESS_P1, getHealthy: () => _p1Healthy, setHealthy: v => { _p1Healthy = v; }, getCheckedAt: () => _p1CheckedAt, setChecked: () => { _p1CheckedAt = Date.now(); } },
    { label: "K2", url: HARNESS_K2, getHealthy: () => _k2Healthy, setHealthy: v => { _k2Healthy = v; }, getCheckedAt: () => _k2CheckedAt, setChecked: () => { _k2CheckedAt = Date.now(); } },
  ];
}

async function routeToHarness(message, sessionId) {
  const payload = JSON.stringify({ message, session_id: sessionId });
  const headers = { "Content-Type": "application/json", "Authorization": `Bearer ${HUB_CHAT_TOKEN}` };
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
      if (r.ok && data.ok !== false && !isFalsePositive) { console.log(`[HARNESS] ${node.label} responded OK`); data._harness = node.label; return data; }
      if (isFalsePositive) { errors.push(`${node.label} false-positive: ${respText.slice(0, 80)}`); continue; }
      errors.push(`${node.label} ${r.status}: ${data.error || "non-ok"}`);
    } catch (e) { errors.push(`${node.label}: ${e.message}`); }
  }
  // If all nodes were busy, return specific busy message (not generic "failed")
  if (busyCount > 0) {
    console.warn("[HARNESS] All nodes busy:", errors.join("; "));
    return { ok: false, error: BUSY_MSG };
  }
  console.error("[HARNESS] All nodes failed:", errors.join("; "));
  return { ok: false, error: `All harness nodes failed: ${errors.join("; ")}` };
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
  const headers = { "Content-Type": "application/json", "Authorization": `Bearer ${HUB_CHAT_TOKEN}` };

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

function buildVaultRecord({ type, content, tags, source, confidence }) {
  return {
    type: type || "log",
    content: { text: content, format: "text" },
    tags: Array.isArray(tags) ? tags : [],
    source: { ref: source || "sovereign-proxy", kind: "system" },
    confidence: confidence ?? 0.9,
    verification: { verified_at: new Date().toISOString(), verifier: "sovereign-proxy", notes: "auto", protocol_version: "1.0", status: "verified" },
    created_at: new Date().toISOString(),
  };
}
// Shared fire-and-forget: vault write + chatlog append + cortex ingest
function postResponseSideEffects({ message, assistantText, sessionId, costUsd, model, tagSuffix }) {
  const costStr = (costUsd !== undefined && costUsd !== null) ? costUsd.toFixed(4) : "0.0000";
  const modelStr = model || "cc-sovereign";
  const suffix = tagSuffix || "";
  const chatContent = `[CHAT${suffix}] user: ${message.slice(0, 200)}\nassistant: ${assistantText.slice(0, 500)} [cost:$${costStr},model:${modelStr}]`;
  vaultPost("/v1/memory", VAULT_BEARER, buildVaultRecord({
    type: "log", content: chatContent,
    tags: ["chat", "sovereign-harness", "hub", ...(suffix ? [suffix.replace("-", "").toLowerCase()] : [])], source: "sovereign-proxy",
  })).catch(e => console.error("[VAULT] write failed:", e.message));
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
  console.log(`[REQUEST] ${req.method} ${req.url}`);

  try {
    // ── Static files ───────────────────────────────────────────────────
    if (req.method === "GET" && (req.url === "/" || req.url === "/index.html" || req.url === "/unified.html")) {
      const html = fs.readFileSync(path.join(PUBLIC_DIR, "unified.html"), "utf-8");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      return res.end(html);
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

    // ── /v1/learnings — what Karma has actually learned (from claude-mem)
    if (req.method === "GET" && req.url === "/v1/learnings") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        // Fetch from P1 cc_server (has direct claude-mem access)
        const r = await fetch(`${HARNESS_P1}/v1/learnings`, { signal: AbortSignal.timeout(10000) });
        const data = await r.json();
        return json(res, r.ok ? 200 : 502, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: `Learnings unavailable: ${e.message}` });
      }
    }

    // ── Health ─────────────────────────────────────────────────────────
    if (req.method === "GET" && req.url === "/health") {
      return json(res, 200, { ok: true, service: "sovereign-proxy", ts: new Date().toISOString() });
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
      return json(res, 200, {
        ok: true, service: "sovereign-proxy", ts: new Date().toISOString(),
        harness: { p1: { url: HARNESS_P1, healthy: _p1Healthy }, k2: { url: HARNESS_K2, healthy: _k2Healthy } },
        cost: { model: "cc-sovereign (Max subscription)", usd_per_request: 0, note: "H8: CC --resume runs on Max subscription. API cost shown in stream result events is accounting only, not billed. Actual charge: $0/request. Monthly sub: $100-200." },
      });
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

    // ── /v1/chat — proxy to sovereign harness ─────────────────────────
    if (req.method === "POST" && req.url === "/v1/chat") {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const raw = await parseBody(req, 500000);
      let body; try { body = JSON.parse(raw); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
      const message = body.message || body.content || "";
      if (!message) return json(res, 400, { ok: false, error: "message required" });
      const sessionId = body.session_id || "";

      // ── Streaming path (SSE) ──────────────────────────────────────────
      if (body.stream === true) {
        return routeToHarnessStream(message, sessionId, body.effort, body.model, res, body.files, body.budget);
      }

      // ── Batch path (JSON, backward compat) ────────────────────────────
      const result = await routeToHarness(message, sessionId);

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
    if (req.method === "PATCH" && req.url.startsWith("/v1/coordination/coord_")) {
      if (!authChat(req)) return json(res, 401, { ok: false, error: "unauthorized" });
      const id = req.url.replace("/v1/coordination/", "");
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
loadCoordFromDisk();
server.listen(PORT, () => {
  console.log(`[SOVEREIGN-PROXY] Listening on port ${PORT}`);
  console.log(`[SOVEREIGN-PROXY] Harness P1: ${HARNESS_P1}`);
  console.log(`[SOVEREIGN-PROXY] Harness K2: ${HARNESS_K2}`);
  console.log(`[SOVEREIGN-PROXY] Chat token: ${HUB_CHAT_TOKEN ? "loaded" : "MISSING"}`);
  console.log(`[SOVEREIGN-PROXY] Vault bearer: ${VAULT_BEARER ? "loaded" : "MISSING"}`);
  console.log(`[SOVEREIGN-PROXY] Cost per request: $0.00 (Max subscription)`);
});
