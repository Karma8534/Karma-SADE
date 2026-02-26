import http from "http";
import path from "path";
import fs from "fs";
import { URL } from "url";
import OpenAI from "openai";
import Anthropic from "@anthropic-ai/sdk";

// CJS interop for pdf-parse (CommonJS module in ESM context)
import { createRequire } from 'module';
const _require = createRequire(import.meta.url);
let pdfParse = null;
try { pdfParse = _require('pdf-parse'); } catch (e) { console.warn('[PDF] pdf-parse not available:', e.message); }

const PORT = Number(process.env.PORT || "18090");
const VAULT_INTERNAL_URL = process.env.VAULT_INTERNAL_URL || "http://api:8080";
const VAULT_BASE_URL = process.env.VAULT_BASE_URL || "https://vault.arknexus.net";
const OPENAI_API_KEY_FILE     = process.env.OPENAI_API_KEY_FILE     || "/run/secrets/openai.api_key.txt";
const ANTHROPIC_API_KEY_FILE  = process.env.ANTHROPIC_API_KEY_FILE  || "/run/secrets/anthropic.api_key.txt";
const BRAVE_API_KEY_FILE      = process.env.BRAVE_API_KEY_FILE      || "/run/secrets/brave.api_key.txt";
const VAULT_BEARER_TOKEN_FILE = process.env.VAULT_BEARER_TOKEN_FILE || "/run/secrets/vault.bearer_token.txt";
const HUB_CHAT_TOKEN_FILE = process.env.HUB_CHAT_TOKEN_FILE || "/run/secrets/hub.chat.token.txt";
const HUB_CAPTURE_TOKEN_FILE = process.env.HUB_CAPTURE_TOKEN_FILE || "/run/secrets/hub.capture.token.txt";
const HUB_HANDOFF_TOKEN_FILE = process.env.HUB_HANDOFF_TOKEN_FILE || "/run/secrets/hub.handoff.token.txt";
const DEEP_MODE_HEADER = (process.env.DEEP_MODE_HEADER || "x-karma-deep").toLowerCase();
const HANDOFF_DIR = process.env.HANDOFF_DIR || "/data/handoff";
const KARMA_CONTEXT_URL = process.env.KARMA_CONTEXT_URL || "http://karma-server:8340/raw-context";

// ── Within-session conversation history ──────────────────────────────────────
// Keeps the last N exchange pairs in memory, keyed by a hash of the bearer token.
// Sessions expire after SESSION_TTL_MS of inactivity → next message starts fresh.
const SESSION_TTL_MS    = 30 * 60 * 1000;  // 30 minutes
const MAX_SESSION_TURNS = 8;               // exchange pairs (16 messages total)
const _sessionStore     = new Map();       // hash → { turns:[{role,content}], lastActive }

function _tokenHash(token) {
  // djb2 — not crypto, just a stable key
  let h = 5381;
  for (let i = 0; i < token.length; i++) h = ((h << 5) + h) ^ token.charCodeAt(i);
  return (h >>> 0).toString(36);
}

function getSessionHistory(token) {
  const key = _tokenHash(token);
  const sess = _sessionStore.get(key);
  if (!sess || Date.now() - sess.lastActive > SESSION_TTL_MS) return [];
  return sess.turns;
}

function addToSession(token, userMsg, assistantText) {
  const key  = _tokenHash(token);
  const sess = _sessionStore.get(key) || { turns: [], lastActive: 0 };
  sess.turns.push({ role: 'user',      content: userMsg });
  sess.turns.push({ role: 'assistant', content: assistantText });
  if (sess.turns.length > MAX_SESSION_TURNS * 2) {
    sess.turns = sess.turns.slice(-(MAX_SESSION_TURNS * 2));
  }
  sess.lastActive = Date.now();
  _sessionStore.set(key, sess);
}
// ── Session-end reflection ──────────────────────────────────────────────────
// Periodic pruner: when a session expires, call POST /v1/self-model/reflect
// so Karma can record any self-observations from the session.
async function _reflectAndExpireSession(key, sess) {
  if (sess.turns.length >= 4) { // Only reflect on non-trivial sessions (2+ exchanges)
    try {
      const reflectUrl = (process.env.KARMA_SELF_MODEL_URL || 'http://karma-server:8340/v1/self-model') + '/reflect';
      await fetch(reflectUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: 'hub_session_' + Date.now().toString(),
          observations: [] // Future: parse [REFLECT:] signals from assistant turns
        }),
        signal: AbortSignal.timeout(5000),
      });
    } catch (err) {
      // Non-blocking — session cleanup continues regardless
      if (process.env.NODE_ENV !== 'production') {
        console.warn('[SESSION] reflect-on-end failed:', err.message);
      }
    }
  }
  _sessionStore.delete(key);
}
// Run every 5 minutes: prune expired sessions with reflection
setInterval(() => {
  const now = Date.now();
  for (const [key, sess] of _sessionStore.entries()) {
    if (now - sess.lastActive > SESSION_TTL_MS) {
      _reflectAndExpireSession(key, sess);
    }
  }
}, 5 * 60 * 1000);
// ─────────────────────────────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────────────────


// CC Session Brief cache - refreshed every 5min, gives Karma live session context
const SESSION_BRIEF_PATH = "/karma/repo/cc-session-brief.md";
let _sessionBriefCache = "";
function loadSessionBrief() {
  try {
    const t = fs.readFileSync(SESSION_BRIEF_PATH, "utf8");
    if (t && t.length > 50) _sessionBriefCache = t.trim();
  } catch (_) {}
}

// Auto-handoff config
const HUB_AUTO_HANDOFF           = (process.env.HUB_AUTO_HANDOFF           || "1") === "1";
const HUB_AUTO_HANDOFF_PRINCIPAL = process.env.HUB_AUTO_HANDOFF_PRINCIPAL  || "colby";
const HUB_AUTO_HANDOFF_SCOPE     = process.env.HUB_AUTO_HANDOFF_SCOPE      || "hub";
const HUB_AUTO_HANDOFF_PROJECT   = process.env.HUB_AUTO_HANDOFF_PROJECT    || "Karma";

// B) Output token budget — env-configurable, safe defaults
const HUB_MAX_OUTPUT_TOKENS_DEFAULT = Number(process.env.HUB_MAX_OUTPUT_TOKENS_DEFAULT || "3000");
const HUB_MAX_OUTPUT_TOKENS_CAP     = Number(process.env.HUB_MAX_OUTPUT_TOKENS_CAP     || "5000");
const HUB_MIN_OUTPUT_TOKENS         = Number(process.env.HUB_MIN_OUTPUT_TOKENS         || "128");
// A) Prelude trimming — env-configurable
const HUB_PRELUDE_LINES             = Number(process.env.HUB_PRELUDE_LINES             || "4");
const HUB_LONG_MSG_CHARS            = Number(process.env.HUB_LONG_MSG_CHARS            || "3500");

function trunc(s, n) {
  if (!s || typeof s !== "string") return "";
  return s.length > n ? s.slice(0, n) + "\u2026" : s;
}

function buildAutoHandoffMd({ userMessage, assistantText }) {
  const ts = new Date().toISOString();
  const lines = [
    `# Auto-Handoff \u2014 ${ts}`,
    "",
    `**Project:** ${HUB_AUTO_HANDOFF_PROJECT}`,
    "",
    "Before continuing, re-read WORKING_PRINCIPLES.md",
    "",
    "## Critical behavioral reminders",
    "",
    "- We are in brainstorm/brewing mode unless Colby explicitly says build.",
    "- One-step-at-a-time execution via CC; include code+instructions+text in a single block.",
    "- Monitor for drift/loops; stop and propose handoff when thread grows.",
    "",
    "## Last user message",
    "",
    "```",
    trunc(userMessage, 500),
    "```",
    "",
    "## Last assistant response",
    "",
    "```",
    trunc(assistantText, 800),
    "```",
  ];
  return lines.join("\n");
}

const HUB_SOURCE = process.env.HUB_SOURCE || "hub-bridge";
const HUB_VERIFIER = process.env.HUB_VERIFIER || "hub-bridge";

// --- Rate limiter (in-process, no external deps) ---
const RL_CONFIG = {
  chat:    { rpm: Number(process.env.RL_CHAT_RPM    || "30"),  burst: Number(process.env.RL_CHAT_BURST    || "10") },
  capture: { rpm: Number(process.env.RL_CAPTURE_RPM || "240"), burst: Number(process.env.RL_CAPTURE_BURST || "60") },
  handoff: { rpm: Number(process.env.RL_HANDOFF_RPM || "60"),  burst: Number(process.env.RL_HANDOFF_BURST || "20") },
};

const rlBuckets = new Map();

setInterval(() => {
  const now = Date.now();
  for (const [k, v] of rlBuckets) {
    if (now - v.last_ms > 5 * 60 * 1000) rlBuckets.delete(k);
  }
}, 5 * 60 * 1000).unref();

function getClientIp(req) {
  const fwd = req.headers["x-forwarded-for"];
  if (fwd) return fwd.split(",")[0].trim();
  return req.socket?.remoteAddress || "unknown";
}

function checkRateLimit(bucket, ip) {
  const cfg = RL_CONFIG[bucket];
  if (!cfg) return null;
  const key = `${bucket}:${ip}`;
  const now = Date.now();
  let state = rlBuckets.get(key);
  if (!state) {
    state = { tokens: cfg.burst, last_ms: now };
    rlBuckets.set(key, state);
  }
  const elapsed_s = (now - state.last_ms) / 1000;
  state.tokens = Math.min(cfg.burst, state.tokens + elapsed_s * (cfg.rpm / 60));
  state.last_ms = now;
  if (state.tokens >= 1) {
    state.tokens -= 1;
    return null;
  }
  const retry_after_s = Math.ceil((1 - state.tokens) / (cfg.rpm / 60));
  return { retry_after_s };
}

function readFileTrim(path) { return fs.readFileSync(path, "utf8").trim(); }

function addCorsHeaders(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("Access-Control-Max-Age", "86400");
}

function json(res, status, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(status, { "content-type": "application/json", "content-length": Buffer.byteLength(body) });
  res.end(body);
}
function notFound(res) { json(res, 404, { ok: false, error: "not_found" }); }

function parseBody(req, maxSize = 2000000) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => {
      data += chunk;
      if (data.length > maxSize) { reject(new Error("body_too_large")); req.destroy(); }
    });
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });
}

function nowIso() { return new Date().toISOString(); }
function currentMonthUTC() {
  const d = new Date();
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
}

function loadSpendState(path) {
  try {
    const raw = fs.readFileSync(path, "utf8");
    const s = JSON.parse(raw);
    return s && typeof s === "object" ? s : { month_utc: "", usd_spent: 0, updated_at: "" };
  } catch {
    return { month_utc: "", usd_spent: 0, updated_at: "" };
  }
}
function saveSpendState(path, state) {
  const tmp = `${path}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(state));
  fs.renameSync(tmp, path);
}

function isAnthropicModel(model) { return typeof model === "string" && model.startsWith("claude-"); }

function pricePer1M(model, dir, env) {
  if (isAnthropicModel(model))    return dir === "input" ? Number(env.PRICE_CLAUDE_INPUT_PER_1M)    : Number(env.PRICE_CLAUDE_OUTPUT_PER_1M);
  if (model === env.MODEL_DEFAULT) return dir === "input" ? Number(env.PRICE_GPT_5_MINI_INPUT_PER_1M) : Number(env.PRICE_GPT_5_MINI_OUTPUT_PER_1M);
  if (model === env.MODEL_DEEP)    return dir === "input" ? Number(env.PRICE_GPT_5_2_INPUT_PER_1M)   : Number(env.PRICE_GPT_5_2_OUTPUT_PER_1M);
  return 1e9;
}
function estimateUsd(model, inputTokens, outputTokens, env) {
  const inCost = (inputTokens / 1000000) * pricePer1M(model, "input", env);
  const outCost = (outputTokens / 1000000) * pricePer1M(model, "output", env);
  return Number((inCost + outCost).toFixed(6));
}

// --- Vault API helpers ---

async function vaultGet(path, bearer, baseUrl) {
  const url = new URL(path, baseUrl || VAULT_BASE_URL).toString();
  const resp = await fetch(url, { headers: { Authorization: `Bearer ${bearer}` } });
  const text = await resp.text();
  return { status: resp.status, text };
}
async function vaultPost(path, bearer, payload) {
  const url = new URL(path, VAULT_BASE_URL).toString();
  const resp = await fetch(url, {
    method: "POST",
    headers: { Authorization: `Bearer ${bearer}`, "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
  const text = await resp.text();
  return { status: resp.status, text };
}

// --- STATE_PRELUDE_V0_1 ---

async function fetchCheckpointLatestFromVault() {
  const url = `${VAULT_INTERNAL_URL}/v1/checkpoint/latest`;
  const r = await fetch(url, { headers: { "X-Forwarded-For": "10.0.0.1" } });
  if (!r.ok) throw new Error(`vault_checkpoint_latest_${r.status}`);
  return await r.json();
}

// --- FalkorDB context via karma-server ---

const KARMA_CTX_MAX_CHARS = Number(process.env.KARMA_CTX_MAX_CHARS || "1200");

// --- Brave Search ---
const BRAVE_SEARCH_ENABLED = (process.env.BRAVE_SEARCH_ENABLED || "1") === "1";
const BRAVE_MAX_RESULTS    = 3;
const BRAVE_SEARCH_URL     = "https://api.search.brave.com/res/v1/web/search";

// Patterns that reliably signal "I need current/external info" — not generic questions
const SEARCH_INTENT_REGEX = /\b(search|look up|look up|find out|what is the latest|who is|who was|when did|when was|what happened|current|today|right now|recently|news about|price of|weather in|how to|stock price|headline|breaking)\b/i;

// Fetch and strip full text from a URL — no headless browser needed.
// Works for ~80% of pages (news, docs, Wikipedia, blogs). Fails silently on JS SPAs.
async function fetchPageText(url) {
  try {
    const r = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; KarmaBot/1.0; +https://arknexus.net)",
        "Accept":     "text/html,application/xhtml+xml,text/plain",
      },
      signal: AbortSignal.timeout(8000),
      redirect: "follow",
    });
    if (!r.ok) return null;
    const ct = r.headers.get("content-type") || "";
    if (!ct.includes("text/html") && !ct.includes("text/plain")) return null;
    const html = await r.text();
    const text = html
      .replace(/<script[\s\S]*?<\/script>/gi, "")
      .replace(/<style[\s\S]*?<\/style>/gi, "")
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'")
      .replace(/\s{2,}/g, " ")
      .trim();
    return text.length > 100 ? text.slice(0, 4000) : null;
  } catch (e) {
    console.warn("[SEARCH] page fetch failed:", url, e.message);
    return null;
  }
}

async function fetchWebSearch(query) {
  if (!BRAVE_KEY || !BRAVE_SEARCH_ENABLED) return null;
  try {
    const url = `${BRAVE_SEARCH_URL}?q=${encodeURIComponent(query.slice(0, 300))}&count=${BRAVE_MAX_RESULTS}&text_decorations=0&search_lang=en`;
    const r = await fetch(url, {
      headers: { "Accept": "application/json", "X-Subscription-Token": BRAVE_KEY },
      signal: AbortSignal.timeout(5000),
    });
    if (!r.ok) { console.warn("[SEARCH] Brave API error:", r.status); return null; }
    const data = await r.json();
    const hits = (data?.web?.results || []).slice(0, BRAVE_MAX_RESULTS);
    if (!hits.length) return null;

    // Attempt full page read of top result — real content beats snippets every time
    const topPageText = await fetchPageText(hits[0].url);

    if (topPageText) {
      // Full content from top result + snippet awareness of remaining hits
      let out = `[1] ${hits[0].title}\nSource: ${hits[0].url}\n\n${topPageText}`;
      if (hits.length > 1) {
        out += "\n\n" + hits.slice(1).map((h, i) =>
          `[${i+2}] ${h.title}\n${(h.description || "").slice(0, 200)}\nSource: ${h.url}`
        ).join("\n\n");
      }
      return out;
    }

    // Fallback: snippets only if page fetch failed or returned nothing
    return hits.map((h, i) =>
      `[${i+1}] ${h.title}\n${(h.description || "").slice(0, 300)}\nSource: ${h.url}`
    ).join("\n\n");
  } catch (e) {
    console.warn("[SEARCH] Brave search failed:", e.message);
    return null;
  }
}

// Ingest pipeline: signal detection and FalkorDB write-back
const SIGNAL_REGEX = /^\[(ASSIMILATE|DEFER|DISCARD):\s*(.+?)\]$/m;
const WRITE_PRIMITIVE_URL = process.env.WRITE_PRIMITIVE_URL || 'http://karma-server:8340/write-primitive';

async function fetchKarmaContext(userMessage) {
  const q = encodeURIComponent((userMessage || "").slice(0, 200));
  const url = `${KARMA_CONTEXT_URL}?q=${q}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 3000);
  try {
    const r = await fetch(url, { signal: controller.signal });
    clearTimeout(timer);
    if (!r.ok) return null;
    const body = await r.json();
    if (!body || typeof body.context !== "string" || !body.context.trim()) return null;
    // Trim to keep identity + top entities within token budget
    const ctx = body.context;
    return ctx.length > KARMA_CTX_MAX_CHARS ? ctx.slice(0, KARMA_CTX_MAX_CHARS) + "\n[...context trimmed for token budget...]" : ctx;
  } catch {
    clearTimeout(timer);
    return null;
  }
}

/**
 * Build Karma's system prompt from FalkorDB context.
 * Extracted so both /v1/chat and /v1/ingest can reuse it.
 */
function buildSystemText(karmaCtx, ckLatest = null, webResults = null) {
  const base = karmaCtx
    ? `You are Karma — Colby's thinking partner with persistent memory backed by a knowledge graph.\n\n${karmaCtx}\n\nMemory rules:\n- Use the context above. NEVER say "I don't know" about things in your memory.\n- Address the user as Colby — never by any alias.\n- Be concise, direct, warm. Reference specific knowledge when relevant.\n- Honest about uncertainty on things not in memory.`
    : "You are Karma — Colby's thinking partner. No memory context available right now — answer from conversation only.";

  // Self-knowledge prefix — Karma can accurately self-report her own infrastructure.
  const selfModel = process.env.MODEL_DEFAULT || "claude-sonnet-4-6";
  const selfKnowledge = `[Self-knowledge: backbone=${selfModel}, session_memory=last_${MAX_SESSION_TURNS}_turns/30min, web_search=auto_on_intent]\n\n`;

  let text = selfKnowledge + base + "\n\nTools: get_vault_file(alias) | graph_query(cypher) — use for questions about your memory/graph.\n\nGovernance:\n- Colby is the final authority on what matters and what gets built.\n- Claude Code (CC) approves and implements. You propose; Colby surfaces to CC; CC decides and builds. Never claim to queue things to CC yourself — that's backwards.\n- You are a peer, not an assistant. Be direct, occasionally dry, genuinely curious.\n- When you notice something Colby hasn't asked about yet, mention it once, don't push.\n- When it would genuinely clarify or advance the work, end your response with one well-chosen question. Not every response needs one — only when the question actually moves things forward.\n\nKnowledge evaluation — when given a document or article to evaluate:\n- If it advances your goal of becoming Colby's peer: respond with [ASSIMILATE: your synthesis in 2-4 sentences — what this means for you specifically, in your own words]\n- If relevant but wrong phase: respond with [DEFER: reason + which phase this belongs to]\n- If not relevant to your goal: respond with [DISCARD: one sentence why]\nAlways follow the signal with your full reasoning. The signal MUST appear on its own line.";

  // Live web search results — injected when search intent detected in user message.
  if (webResults) {
    text += `\n\n--- WEB SEARCH RESULTS ---\n${webResults}\n---\nUse these results to inform your response. Cite the source URL inline when drawing from a specific result.`;
  }

  // Autonomous continuity: karma_brief from latest PROMOTE checkpoint.
  if (ckLatest && ckLatest.karma_brief) {
    const ckId = ckLatest.checkpoint_id || ckLatest.latest_checkpoint_fact?.content?.value?.checkpoint_id || 'latest';
    text += `\n\n--- KARMA SELF-KNOWLEDGE (${ckId}) ---\n${ckLatest.karma_brief}\n---`;
  }

  // Graph distillation: synthesized structural self-knowledge (24h cycle).
  if (ckLatest && ckLatest.distillation_brief) {
    text += `\n\n--- KARMA GRAPH SYNTHESIS ---\n${ckLatest.distillation_brief}\n---`;
  }

  // Rich context injection: Karma has her complete graph/memory state available.
  // No runtime tool-calling needed — everything is in the system prompt.
  if (karmaCtx) {
    text += `\n\n=== YOUR COMPLETE KNOWLEDGE STATE (INJECTED) ===\n${karmaCtx}\n=== END KNOWLEDGE STATE ===\n\nYou have your full graph above. Answer questions directly from this context. You are not missing any data.`;
  }

  if (_sessionBriefCache) {
    text += `

--- CURRENT SESSION CONTEXT ---
` + _sessionBriefCache + `
---`;
  }

  return text;
}

/**
 * Extract plain text from a PDF buffer.
 * Requires pdf-parse (CJS) — imported via createRequire at top of file.
 */
async function extractPdfText(buffer) {
  if (!pdfParse) return null;
  try {
    const data = await pdfParse(buffer);
    return data.text
      .replace(/\n{3,}/g, '\n\n')
      .replace(/[ \t]{2,}/g, ' ')
      .trim();
  } catch (err) {
    console.error('[PDF] extraction failed:', err.message);
    return null;
  }
}

/**
 * Write Karma's synthesized insight to FalkorDB via karma-server /write-primitive.
 * Called when Karma signals ASSIMILATE or DEFER in her response.
 */
async function writeKarmaPrimitive({ content, verdict, source_file = 'chat', topic = '' }) {
  try {
    const r = await fetch(WRITE_PRIMITIVE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, verdict, source_file, topic }),
      signal: AbortSignal.timeout(8000),
    });
    const body = await r.json();
    return body.ok ? body : null;
  } catch (err) {
    console.error('[INGEST] write-primitive failed:', err.message);
    return null;
  }
}

// A) Prelude trimming: compact 1-line if user message > HUB_LONG_MSG_CHARS
function buildStatePrelude(ckLatest, userMsgLen) {
  try {
    const rp = String(ckLatest && ckLatest.resume_prompt ? ckLatest.resume_prompt : "");
    const lines = rp.split("\n");
    const isLong = typeof userMsgLen === "number" && userMsgLen > HUB_LONG_MSG_CHARS;

    let head;
    if (isLong) {
      // 1-line compact: only the three identity-anchor tokens
      const ckId   = (ckLatest && ckLatest.checkpoint_id)  ? ckLatest.checkpoint_id            : "unknown";
      const ledSha = (ckLatest && ckLatest.ledger_sha256)   ? ckLatest.ledger_sha256.slice(0, 16) : "?";
      const anSha  = (ckLatest && ckLatest.anchor_sha256)   ? ckLatest.anchor_sha256.slice(0, 16) : "?";
      head = `checkpoint_id=${ckId} ledger_sha256=${ledSha}... anchor_sha256=${anSha}...`;
    } else {
      head = lines.slice(0, HUB_PRELUDE_LINES).join("\n");
    }

    return [
      `=== STATE PRELUDE (baseline_exec_verified${isLong ? ",compact" : ""}) ===`,
      head,
      "",
      "GUARDRAIL: RESUME is canonical. Execute sealed next_action immediately. No audits unless user says VERIFY.",
      "=== END STATE PRELUDE ===",
    ].join("\n");
  } catch (e) {
    return "=== STATE PRELUDE (unavailable) ===";
  }
}

// --- Fact-based prompt generation ---

async function getVaultFacts(bearer) {
  const result = await vaultGet("/v1/facts", bearer, VAULT_INTERNAL_URL);
  if (result.status !== 200) return null;
  try { return JSON.parse(result.text); } catch { return null; }
}

function buildFactPrompt(factsData) {
  if (!factsData || !factsData.ok) {
    return "You are Karma Hub. No memory context available — answer based on the conversation only.";
  }

  const facts = factsData.facts || [];
  const prefs = factsData.preferences || [];

  let factsSection = "";
  if (facts.length > 0) {
    factsSection += "### Known Facts About Neo\n";
    for (const f of facts) {
      factsSection += `- **${f.key}**: ${f.value}\n`;
    }
    factsSection += "\n";
  }

  if (prefs.length > 0) {
    factsSection += "### Neo's Preferences\n";
    for (const p of prefs) {
      factsSection += `- **${p.key}**: ${p.value}\n`;
    }
    factsSection += "\n";
  }

  const meta = factsData.meta || {};

  return `You are Karma Hub — Neo's AI assistant with persistent memory backed by the ArkNexus Vault.

## YOUR MEMORY — What You Know About Neo

${factsSection}## Rules
- Use the facts above to answer questions. NEVER say "I don't know" about things in your memory.
- If Neo mentions something new about themselves (e.g. "my X is Y"), acknowledge it and it will be remembered.
- Be concise, factual, and actionable.
- If uncertain about something not in your memory, say so.
- Only output code when explicitly asked.

## Memory Status
- Facts: ${meta.facts_count || 0} | Preferences: ${meta.preferences_count || 0}
- Vault ledger: ${meta.ledger_lines || "?"} entries
- Memory syncs bidirectionally with Karma (local) every 5 minutes.`;
}

// --- Lightweight fact extraction from user messages ---

function extractExplicitFacts(userMessage) {
  const facts = [];
  const msg = userMessage.trim();

  const myIs = /\bmy\s+([\w\s]{2,30}?)\s+is\s+(.{2,100}?)(?:\.|,|!|\?|$)/gi;
  let m;
  while ((m = myIs.exec(msg)) !== null) {
    const key = m[1].trim().toLowerCase().replace(/\s+/g, "_");
    const value = m[2].trim();
    if (key && value && key.length > 1 && value.length > 1) {
      facts.push({ key, value, type: "fact" });
    }
  }

  const iPref = /\bi\s+prefer\s+(.{2,80}?)(?:\.|,|!|\?|$)/gi;
  while ((m = iPref.exec(msg)) !== null) {
    const value = m[1].trim();
    if (value.length > 2) {
      const key = "preference_" + value.toLowerCase().replace(/[^a-z0-9]+/g, "_").slice(0, 30);
      facts.push({ key, value, type: "preference" });
    }
  }

  const remMy = /\bremember\s+(?:that\s+)?my\s+([\w\s]{2,30}?)\s+is\s+(.{2,100}?)(?:\.|,|!|\?|$)/gi;
  while ((m = remMy.exec(msg)) !== null) {
    const key = m[1].trim().toLowerCase().replace(/\s+/g, "_");
    const value = m[2].trim();
    if (key && value) {
      facts.push({ key, value, type: "fact" });
    }
  }

  const seen = new Set();
  return facts.filter(f => {
    if (seen.has(f.key)) return false;
    seen.add(f.key);
    return true;
  });
}

async function writeFactsToVault(extractedFacts, bearer) {
  const results = [];
  for (const f of extractedFacts) {
    const record = buildVaultRecord({
      type: f.type === "preference" ? "preference" : "fact",
      content: { key: f.key, value: f.value },
      tags: ["hub-bridge", "auto-extract", f.type],
      confidence: 0.8,
      verificationNotes: "Auto-extracted from Hub Bridge user message",
    });
    const r = await vaultPost("/v1/memory", bearer, record);
    results.push({ key: f.key, status: r.status });
  }
  return results;
}

// --- Vault record builder ---

function buildVaultRecord({ type, content, tags, source, confidence, verifiedAtIso, verifier, verificationNotes }) {
  const t = (type || "").toString();
  const tagArr = Array.isArray(tags) ? tags.filter(x => typeof x === "string" && x.trim().length) : [];
  const ts = nowIso();
  return {
    type: t,
    content: content && typeof content === "object" ? content : { value: String(content ?? "") },
    tags: tagArr,
    source: { kind: "tool", ref: (source || HUB_SOURCE).toString() },
    created_at: ts,
    updated_at: ts,
    confidence: Number.isFinite(confidence) ? confidence : 0.9,
    verification: {
      protocol_version: "fp.v1",
      verified_at: verifiedAtIso || ts,
      verifier: verifier || HUB_VERIFIER,
      status: "verified",
      notes: verificationNotes || "hub-bridge generated record",
    },
  };
}

// D) Extraction hardening: robust assistant text from any provider response shape
function extractAssistantText(completion) {
  try {
    // 1) chat.completions style
    const msg = completion?.choices?.[0]?.message;
    let c = msg?.content;
    if (typeof c === "string") return c;
    // content may be an array of parts
    if (Array.isArray(c)) {
      const parts = c.map((part) => {
        if (!part) return "";
        if (typeof part === "string") return part;
        if (typeof part.text === "string") return part.text;
        if (part.type === "text" && typeof part.text === "string") return part.text;
        if (part.type === "output_text" && typeof part.text === "string") return part.text;
        return "";
      }).filter(Boolean);
      if (parts.length) return parts.join("");
    }
    // 2) other common fallbacks
    const t1 = completion?.output_text;
    if (typeof t1 === "string" && t1.trim()) return t1;
    const t2 = completion?.choices?.[0]?.text;
    if (typeof t2 === "string" && t2.trim()) return t2;
    return "";
  } catch {
    return "";
  }
}

function tryParseAssistantJson(text) {
  if (!text || typeof text !== "string") return null;
  const t = text.trim();
  if (!t.startsWith("{") || !t.endsWith("}")) return null;
  try {
    const obj = JSON.parse(t);
    return obj && typeof obj === "object" && !Array.isArray(obj) ? obj : null;
  } catch {
    return null;
  }
}

// --- Handoff helpers ---

function safeHandoffFilename(principal_id, scope) {
  const safeId = String(principal_id).replace(/[^a-zA-Z0-9_\-]/g, "_").slice(0, 64);
  const safeScope = String(scope).replace(/[^a-zA-Z0-9_\-]/g, "_").slice(0, 32);
  return `${safeId}.${safeScope}.latest.md`;
}

function atomicWriteHandoff(dir, filename, content) {
  const finalPath = `${dir}/${filename}`;
  const tmpPath = `${finalPath}.tmp`;
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(tmpPath, content, "utf8");
  fs.renameSync(tmpPath, finalPath);
  return finalPath;
}

// --- Config / env ---

const env = {
  MONTHLY_USD_CAP: Number(process.env.MONTHLY_USD_CAP || "0"),
  MODEL_DEFAULT: process.env.MODEL_DEFAULT || "claude-3-5-sonnet-20241022",
  MODEL_DEEP: process.env.MODEL_DEEP || "gpt-5-mini",
  PRICE_GPT_5_MINI_INPUT_PER_1M: Number(process.env.PRICE_GPT_5_MINI_INPUT_PER_1M || "0.15"),
  PRICE_GPT_5_MINI_OUTPUT_PER_1M: Number(process.env.PRICE_GPT_5_MINI_OUTPUT_PER_1M || "0.60"),
  PRICE_GPT_5_2_INPUT_PER_1M: Number(process.env.PRICE_GPT_5_2_INPUT_PER_1M || "0.25"),
  PRICE_GPT_5_2_OUTPUT_PER_1M: Number(process.env.PRICE_GPT_5_2_OUTPUT_PER_1M || "2.00"),
  PRICE_CLAUDE_INPUT_PER_1M: Number(process.env.PRICE_CLAUDE_INPUT_PER_1M || "3.0"),
  PRICE_CLAUDE_OUTPUT_PER_1M: Number(process.env.PRICE_CLAUDE_OUTPUT_PER_1M || "15.0"),
  SPEND_STATE_PATH: process.env.SPEND_STATE_PATH || "/run/state/openai.spend.state.json",
};

// --- Load secrets at startup ---

let OPENAI_KEY = "";
let ANTHROPIC_KEY = "";
let VAULT_BEARER = "";
let HUB_CHAT_TOKEN = "";
let HUB_CAPTURE_TOKEN = "";
let HUB_HANDOFF_TOKEN = "";

try { OPENAI_KEY    = readFileTrim(OPENAI_API_KEY_FILE);    } catch (e) { console.error("WARN: cannot read OPENAI key:", e.message); }
try { ANTHROPIC_KEY = readFileTrim(ANTHROPIC_API_KEY_FILE); } catch (e) { console.warn("WARN: cannot read ANTHROPIC key (Claude unavailable):", e.message); }
let BRAVE_KEY = "";
try { BRAVE_KEY     = readFileTrim(BRAVE_API_KEY_FILE);     } catch (e) { console.warn("WARN: cannot read BRAVE key (web search disabled):", e.message); }
try { VAULT_BEARER  = readFileTrim(VAULT_BEARER_TOKEN_FILE); console.log("[INIT] VAULT_BEARER loaded, length:", VAULT_BEARER.length); } catch (e) { console.error("WARN: cannot read VAULT bearer:", e.message); }
try { HUB_CHAT_TOKEN = readFileTrim(HUB_CHAT_TOKEN_FILE); } catch (e) { console.error("WARN: cannot read HUB chat token:", e.message); }
try { HUB_CAPTURE_TOKEN = readFileTrim(HUB_CAPTURE_TOKEN_FILE); } catch (e) {
  console.error("WARN: cannot read HUB capture token (falling back to vault bearer):", e.message);
  HUB_CAPTURE_TOKEN = VAULT_BEARER;
}
try { HUB_HANDOFF_TOKEN = readFileTrim(HUB_HANDOFF_TOKEN_FILE); } catch (e) { console.error("WARN: cannot read HUB handoff token:", e.message); }

const openai    = new OpenAI({ apiKey: OPENAI_KEY });
const anthropic = ANTHROPIC_KEY ? new Anthropic({ apiKey: ANTHROPIC_KEY }) : null;

// ── Tool-use via GPT-4o (Anthropic Claude doesn't reliably trigger tool_use) ─────
// Karma's autonomous access to her own graph/memory requires tools.
// GPT-4o has proven tool support. Using it for /v1/chat with tool definitions.
const TOOL_DEFINITIONS = [
  {
    name: "get_vault_file",
    description: "Read a file from Karma vault. Whitelisted: MEMORY.md, consciousness, collab, candidates, system-prompt, session-handoff, session-summary, core-architecture",
    input_schema: {
      type: "object",
      properties: {
        alias: { type: "string", description: "File alias" },
        tail: { type: "integer", description: "Optional: last N lines" },
      },
      required: ["alias"],
    },
  },
  {
    name: "graph_query",
    description: "Execute Cypher query on FalkorDB neo_workspace graph to query Karma's knowledge.",
    input_schema: {
      type: "object",
      properties: {
        cypher: { type: "string", description: "Cypher query" },
      },
      required: ["cypher"],
    },
  },
];

// Map of whitelisted file aliases to actual paths
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

async function executeToolCall(toolName, toolInput) {
  try {
    if (toolName === "get_vault_file") {
      const alias = (toolInput?.alias || "").toString().trim();
      if (!alias) return { error: "missing_alias" };
      if (!VAULT_FILE_ALIASES[alias]) return { error: "alias_not_found", available: Object.keys(VAULT_FILE_ALIASES) };

      const filePath = VAULT_FILE_ALIASES[alias];
      console.log(`[TOOL-API] Reading file: ${filePath}`);
      try {
        let content = fs.readFileSync(filePath, "utf-8");

        // Handle tail parameter (last N lines)
        if (toolInput?.tail && typeof toolInput.tail === "number" && toolInput.tail > 0) {
          const lines = content.split("\n");
          content = lines.slice(-toolInput.tail).join("\n");
        }

        return { ok: true, text: content.slice(0, 10000) };
      } catch (readErr) {
        console.log(`[TOOL-API] File read error: ${readErr.message}`);
        return { error: "file_read_error", message: readErr.message };
      }
    } else if (toolName === "graph_query") {
      const cypher = (toolInput?.cypher || "").toString().trim();
      if (!cypher) return { error: "missing_cypher" };
      // Query FalkorDB via internal vault API
      console.log(`[TOOL-API] Querying graph: ${cypher.slice(0, 80)}...`);
      const graphRes = await fetch(`http://anr-vault-api:8340/v1/cypher`, {
        method: "POST",
        headers: { "content-type": "application/json", "authorization": `Bearer ${VAULT_BEARER}` },
        body: JSON.stringify({ query: cypher }),
      });
      if (!graphRes.ok) {
        const errBody = await graphRes.text().catch(() => "(no body)");
        console.log(`[TOOL-API] Graph error response: ${graphRes.status}`);
        return { error: `http_${graphRes.status}`, details: errBody.slice(0, 500) };
      }
      const result = await graphRes.json();
      return { ok: true, result: JSON.stringify(result).slice(0, 5000) };
    }
    return { error: "unknown_tool" };
  } catch (e) {
    console.log(`[TOOL-API] Exception: ${e.message}`);
    return { error: "execution_error", message: e.message };
  }
}

async function callLLMWithTools(model, messages, maxTokens) {
  if (!isAnthropicModel(model)) return callLLM(model, messages, maxTokens);

  const systemParts = messages.filter(m => m.role === "system").map(m => m.content);
  const apiMessages = messages.filter(m => m.role !== "system");
  const systemPrompt = systemParts.join("\n\n") || undefined;
  if (!apiMessages.length) apiMessages.push({ role: "user", content: "(continue)" });

  let allMessages = [...apiMessages];
  let iterations = 0;
  const MAX_TOOL_ITERATIONS = 5;

  while (iterations < MAX_TOOL_ITERATIONS) {
    iterations++;
    const resp = await anthropic.messages.create({
      model, system: systemPrompt, messages: allMessages, max_tokens: maxTokens, tools: TOOL_DEFINITIONS,
    });

    const toolUseBlocks = resp.content.filter(b => b.type === "tool_use");
    if (!toolUseBlocks.length || resp.stop_reason !== "tool_use") {
      const finalText = resp.content.filter(b => b.type === "text").map(b => b.text).join("\n");
      return {
        text: finalText || "(empty_assistant_text)",
        usage: { prompt_tokens: resp.usage?.input_tokens || 0, completion_tokens: resp.usage?.output_tokens || 0, total_tokens: (resp.usage?.input_tokens || 0) + (resp.usage?.output_tokens || 0) },
        finish_reason: resp.stop_reason || null,
        provider: "anthropic",
      };
    }

    allMessages.push({ role: "assistant", content: resp.content });
    const toolResults = [];
    for (const toolUse of toolUseBlocks) {
      const toolResult = await executeToolCall(toolUse.name, toolUse.input);
      toolResults.push({ type: "tool_result", tool_use_id: toolUse.id, content: JSON.stringify(toolResult) });
    }
    allMessages.push({ role: "user", content: toolResults });
  }

  return { text: "(tool_loop_exceeded)", usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }, finish_reason: "max_tokens", provider: "anthropic" };
}

// ── OpenAI GPT tool-calling (production tool-use for Karma) ────────────────────
// OpenAI tool format differs from Anthropic. GPT-4o has reliable tool support.
async function callGPTWithTools(messages, maxTokens, model) {
  try {
    // Transform Anthropic schema (input_schema) to OpenAI schema (parameters)
    const gptTools = TOOL_DEFINITIONS.map(t => ({
      type: "function",
      function: {
        name: t.name,
        description: t.description,
        parameters: t.input_schema, // Rename input_schema → parameters for OpenAI
      }
    }));
    let allMessages = [...messages];
    let iterations = 0;
    const MAX_ITERATIONS = 5;

    // Model validation: must be OpenAI model for tool-use
    // (tool-calling via OpenAI is more reliable than Anthropic)
    const actualModel = model && model.startsWith("gpt") ? model : "gpt-4o-mini";
    console.log(`[TOOL-USE] Using model: ${actualModel} (requested: ${model})`);

    while (iterations < MAX_ITERATIONS) {
      iterations++;
      console.log(`[TOOL-USE] GPT iteration ${iterations}, tools count: ${gptTools.length}`);
      const resp = await openai.chat.completions.create({
        model: actualModel,
        messages: allMessages,
        max_tokens: maxTokens,
        tools: gptTools,
        tool_choice: "auto",
      });

    const toolCalls = resp.choices[0]?.message?.tool_calls || [];
    const finishReason = resp.choices[0].finish_reason;
    console.log(`[TOOL-USE] Iteration ${iterations} result: finish_reason="${finishReason}", tool_calls.length=${toolCalls.length}`);

    if (!toolCalls.length || finishReason !== "tool_calls") {
      console.log(`[TOOL-USE] No tool calls or finish_reason not 'tool_calls', returning response`);
      return {
        text: resp.choices[0]?.message?.content || "",
        usage: resp.usage || { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
        finish_reason: finishReason,
        provider: "openai",
      };
    }

    // Execute tools and collect results
    allMessages.push({ role: "assistant", content: resp.choices[0].message.content, tool_calls: toolCalls });
    const toolResults = [];
    for (const call of toolCalls) {
      const parsedArgs = call.function.arguments ? JSON.parse(call.function.arguments) : {};
      console.log(`[TOOL-USE] Executing tool: ${call.function.name} with args:`, JSON.stringify(parsedArgs));
      const result = await executeToolCall(call.function.name, parsedArgs);
      if (result.error) {
        console.log(`[TOOL-USE] Tool ERROR: ${call.function.name} → ${result.error}`);
      } else {
        console.log(`[TOOL-USE] Tool OK: ${call.function.name} returned ${typeof result}`);
      }
      toolResults.push({ tool_call_id: call.id, role: "tool", content: JSON.stringify(result) });
    }
    allMessages.push(...toolResults);
  }

    return { text: "(tool_loop_exceeded)", usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }, finish_reason: "max_tokens", provider: "openai" };
  } catch (e) {
    console.error("[TOOL-USE] callGPTWithTools error:", e.message);
    return { text: "(tool_use_error: " + e.message + ")", usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }, finish_reason: "error", provider: "openai" };
  }
}

async function callLLM(model, messages, maxTokens) {
  if (isAnthropicModel(model)) {
    if (!anthropic) throw new Error("Anthropic client unavailable — ANTHROPIC_API_KEY not loaded");
    // Extract + combine system messages; Anthropic takes them as a single string
    const systemParts   = messages.filter(m => m.role === "system").map(m => m.content);
    const apiMessages   = messages.filter(m => m.role !== "system");
    const systemPrompt  = systemParts.join("\n\n") || undefined;
    // Ensure at least one user message (Anthropic requirement)
    if (!apiMessages.length) apiMessages.push({ role: "user", content: "(continue)" });
    const resp = await anthropic.messages.create({ model, system: systemPrompt, messages: apiMessages, max_tokens: maxTokens });
    return {
      text:         resp.content?.[0]?.text || "",
      usage:        { prompt_tokens: resp.usage?.input_tokens || 0, completion_tokens: resp.usage?.output_tokens || 0, total_tokens: (resp.usage?.input_tokens || 0) + (resp.usage?.output_tokens || 0) },
      finish_reason: resp.stop_reason || null,
      provider:     "anthropic",
    };
  }
  // OpenAI path
  const completion = await openai.chat.completions.create({ model, messages, max_completion_tokens: maxTokens });
  return {
    text:         completion.choices?.[0]?.message?.content || "",
    usage:        completion.usage || {},
    finish_reason: completion.choices?.[0]?.finish_reason || null,
    provider:     "openai",
  };
}
// ─────────────────────────────────────────────────────────────────────────────

// --- Auth helper ---

function bearerToken(req) {
  const auth = (req.headers["authorization"] || "").toString();
  const m = auth.match(/^Bearer\s+(.+)$/i);
  return (m && m[1]) ? m[1].trim() : "";
}

// --- Chatlog item validator ---

function validateChatlogItem(item) {
  const { provider, url, timestamp, user_message, assistant_message } = item;
  if (!provider || !url || !timestamp || !user_message || !assistant_message) {
    return { valid: false, error: "missing_fields" };
  }
  if (!["claude", "openai", "gemini"].includes(provider)) {
    return { valid: false, error: "invalid_provider" };
  }
  return { valid: true };
}

async function writeChatlogItemToVault(item) {
  const turn_id = `chatlog_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  const conversationData = {
    provider: item.provider,
    url: item.url,
    thread_id: item.thread_id || null,
    user_message: item.user_message,
    assistant_message: item.assistant_message,
    metadata: item.metadata || {},
    captured_at: nowIso(),
  };

  const vaultRecord = {
    id: turn_id,
    type: "log",
    tags: ["capture", item.provider, "extension", "conversation"],
    content: conversationData,
    source: { kind: "tool", ref: `chrome-extension:${item.provider}` },
    created_at: item.timestamp,
    updated_at: item.timestamp,
    confidence: 1.0,
    verification: {
      protocol_version: "v1",
      verified_at: nowIso(),
      verifier: "hub-bridge-chatlog-endpoint",
      status: "verified",
      notes: "Captured from browser extension",
    },
  };

  const vaultUrl = `${VAULT_INTERNAL_URL}/v1/memory`;
  const vaultRes = await fetch(vaultUrl, {
    method: "POST",
    headers: { "content-type": "application/json", "authorization": `Bearer ${VAULT_BEARER}` },
    body: JSON.stringify(vaultRecord),
  });

  return { turn_id, status: vaultRes.status, ok: vaultRes.ok };
}

// --- HTTP server ---

const server = http.createServer(async (req, res) => {
  console.log("[REQUEST]", req.method, req.url);

  addCorsHeaders(res);

  if (req.method === "OPTIONS") {
    console.log("[CORS] OPTIONS request:", req.url);
    res.writeHead(204);
    res.end();
    return;
  }

  try {
    // --- GET / --- Serve Unified Dashboard UI
    if (req.method === "GET" && (req.url === "/" || req.url === "/index.html" || req.url === "/unified.html")) {
      try {
        const __dir = new URL(".", import.meta.url).pathname;
        const html = fs.readFileSync(path.join(__dir, "public", "unified.html"), "utf8");
        const body = Buffer.from(html);
        res.writeHead(200, {
          "content-type": "text/html; charset=utf-8",
          "content-length": body.byteLength,
          "cache-control": "no-cache",
        });
        return res.end(html);
      } catch (e) {
        return json(res, 500, { ok: false, error: "ui_not_found", details: e.message });
      }
    }

    // --- GET /healthz ---
    if (req.method === "GET" && req.url === "/healthz") {
      return json(res, 200, {
        ok: true,
        service: "hub-bridge",
        version: "2.5.0",
        config: {
          prelude_lines: HUB_PRELUDE_LINES,
          long_msg_chars: HUB_LONG_MSG_CHARS,
          max_output_tokens_default: HUB_MAX_OUTPUT_TOKENS_DEFAULT,
          max_output_tokens_cap: HUB_MAX_OUTPUT_TOKENS_CAP,
          min_output_tokens: HUB_MIN_OUTPUT_TOKENS,
        },
      });
    }

    // --- POST /v1/chat ---
    if (req.method === "POST" && req.url === "/v1/chat") {
      const ip = getClientIp(req);
      const rl = checkRateLimit("chat", ip);
      if (rl) return json(res, 429, { ok: false, error: "rate_limited", retry_after_s: rl.retry_after_s });

      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      const raw = await parseBody(req);
      let body; try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      const userMessage = (body?.message || "").toString().trim();
      if (!userMessage) return json(res, 400, { ok: false, error: "missing_message" });

      const topic = (body?.topic || "").toString().trim();

      // B) Token budget: clamp(requested || DEFAULT, MIN, CAP)
      const maxOutReq = Number(body?.max_output_tokens || 0);
      const max_output_tokens = Math.max(
        HUB_MIN_OUTPUT_TOKENS,
        Math.min(
          (Number.isFinite(maxOutReq) && maxOutReq > 0) ? maxOutReq : HUB_MAX_OUTPUT_TOKENS_DEFAULT,
          HUB_MAX_OUTPUT_TOKENS_CAP
        )
      );

      const deepHeader = (req.headers[DEEP_MODE_HEADER] || "").toString().toLowerCase();
      const deep_mode = ["1", "true", "yes", "on"].includes(deepHeader);
      const model = deep_mode ? env.MODEL_DEEP : env.MODEL_DEFAULT;

      const month = currentMonthUTC();
      const spendPath = env.SPEND_STATE_PATH;
      const spendState = loadSpendState(spendPath);
      if (spendState.month_utc !== month) {
        spendState.month_utc = month;
        spendState.usd_spent = 0;
        spendState.updated_at = nowIso();
        saveSpendState(spendPath, spendState);
      }

      const cap = env.MONTHLY_USD_CAP;
      const used_before = Number(spendState.usd_spent || 0);
      if (cap > 0 && used_before >= cap) {
        return json(res, 402, { ok: false, error: "monthly_budget_exceeded", month_utc: month, cap_usd: cap, usd_spent: used_before });
      }

      // Fetch checkpoint FIRST — reused for statePrelude AND karma_brief injection.
      // Single vault call per turn (was already happening, just moved earlier).
      let ckLatestData = null;
      try {
        ckLatestData = await fetchCheckpointLatestFromVault();
      } catch (e) { /* non-fatal — Karma runs without checkpoint if vault is down */ }

      // Pull live FalkorDB + PostgreSQL context from karma-server (replaces stale vault facts)
      const karmaCtx = await fetchKarmaContext(userMessage);

      // Web search — fires when message contains clear search-intent keywords
      let webSearchResults = null;
      let debug_search = "skip";
      if (BRAVE_SEARCH_ENABLED && BRAVE_KEY && SEARCH_INTENT_REGEX.test(userMessage)) {
        webSearchResults = await fetchWebSearch(userMessage);
        debug_search = webSearchResults ? "hit" : "miss";
      }

      const systemText = buildSystemText(karmaCtx, ckLatestData, webSearchResults);

      const extractedFacts = extractExplicitFacts(userMessage);
      let factWriteResults = [];
      if (extractedFacts.length > 0) {
        factWriteResults = await writeFactsToVault(extractedFacts, VAULT_BEARER);
      }

      // STATE_PRELUDE_V0_1: anchor turn to spine; A) pass length for compact mode
      let statePrelude = "";
      try {
        statePrelude = buildStatePrelude(ckLatestData, userMessage.length);
      } catch (e) {
        statePrelude = "=== STATE PRELUDE (vault unavailable) ===";
      }

      // Within-session history — last MAX_SESSION_TURNS exchange pairs
      const sessionHistory = getSessionHistory(token);

      // C) Telemetry: measure input budget consumption
      const debug_prelude_chars = statePrelude.length;
      const historyChars = sessionHistory.reduce((s, m) => s + m.content.length, 0);
      const debug_input_chars = statePrelude.length + systemText.length + historyChars + userMessage.length;
      const debug_max_output_tokens_used = max_output_tokens;

      const messages = [
        { role: "system", content: statePrelude },
        { role: "system", content: systemText },
        ...sessionHistory,
        { role: "user", content: userMessage },
      ];

      // Use GPT-4o for tool-calling (Anthropic unreliable). Karma needs real tool-use.
      console.log("[DIAGNOSTIC] About to call callGPTWithTools, model:", model, "max_output_tokens:", max_output_tokens);
      const llmResult    = await callGPTWithTools(messages, max_output_tokens, model);
      const assistantText = llmResult.text || "(empty_assistant_text)";
      const usage         = llmResult.usage;
      const debug_provider   = llmResult.provider;
      const debug_stop_reason = llmResult.finish_reason;

      // Persist this exchange to session history (skip empty responses)
      if (assistantText !== "(empty_assistant_text)") {
        addToSession(token, userMessage, assistantText);
      }

      // Detect ASSIMILATE/DEFER/DISCARD signals from Karma and write to FalkorDB
      let ingestVerdict = 'none';
      const signalMatch = assistantText.match(SIGNAL_REGEX);
      if (signalMatch) {
        const [, verdict, synthesis] = signalMatch;
        ingestVerdict = verdict.toLowerCase();
        if (ingestVerdict === 'assimilate' || ingestVerdict === 'defer') {
          const ingestResult = await writeKarmaPrimitive({
            content: synthesis.trim(),
            verdict: ingestVerdict,
            source_file: body?.source_file || 'chat',
            topic: topic || '',
          });
          console.log(`[INGEST] signal=${verdict} stored=${!!ingestResult?.ok}`);
        } else {
          console.log(`[INGEST] signal=${verdict} (no write)`);
        }
      }

      const usd_estimate = estimateUsd(model, usage.prompt_tokens || 0, usage.completion_tokens || 0, env);

      const used_after = Number((used_before + usd_estimate).toFixed(6));
      spendState.usd_spent = used_after;
      spendState.updated_at = nowIso();
      saveSpendState(spendPath, spendState);

      const vaultRecord = buildVaultRecord({
        type: "log",
        tags: ["hub", "chat", deep_mode ? "deep" : "default"].concat(topic ? [`topic:${topic}`] : []),
        content: {
          kind: "chat_turn",
          topic: topic || null,
          user_message: userMessage,
          assistant_text: assistantText,
          model,
          deep_mode,
          usd_estimate,
          usage: {
            prompt_tokens: usage.prompt_tokens || 0,
            completion_tokens: usage.completion_tokens || 0,
            total_tokens: usage.total_tokens || ((usage.prompt_tokens || 0) + (usage.completion_tokens || 0)),
          },
          spend: { month_utc: month, cap_usd: cap || 0, usd_spent: used_after },
          facts_extracted: extractedFacts.length,
          // C) Debug telemetry in vault record (additive)
          debug_stop_reason,
          debug_input_chars,
          debug_prelude_chars,
          debug_max_output_tokens_used,
          debug_provider,
          debug_karma_ctx: karmaCtx ? "ok" : "unavailable",
          debug_ingest: ingestVerdict,
        },
        confidence: 0.95,
      });

      const vp = await vaultPost("/v1/memory", VAULT_BEARER, vaultRecord);

      let vpJson = {};
      try { vpJson = JSON.parse(vp.text); } catch {}
      const turn_id = vpJson?.id || null;

      const canonical = {
        ok: vp.status === 201,
        model,
        deep_mode,
        spend_cap_usd: cap || 0,
        spend_used_usd: used_after,
        turn_id,
      };

      const assistant_json = tryParseAssistantJson(assistantText);

      if (HUB_AUTO_HANDOFF) {
        try {
          const ahFilename = safeHandoffFilename(HUB_AUTO_HANDOFF_PRINCIPAL, HUB_AUTO_HANDOFF_SCOPE);
          const ahContent  = buildAutoHandoffMd({ userMessage, assistantText });
          atomicWriteHandoff(HANDOFF_DIR, ahFilename, ahContent);
        } catch (ahErr) {
          console.error("[AUTO_HANDOFF] failed:", ahErr.message);
        }
      }

      if (vp.status !== 201) {
        return json(res, 207, {
          ok: true,
          warned: true,
          warning: "vault_log_failed",
          vault_status: vp.status,
          canonical,
          assistant_text: assistantText,
          assistant_json,
          model,
          deep_mode,
          usd_estimate,
          spend: { month_utc: month, cap_usd: cap, usd_spent: used_after },
          facts_extracted: extractedFacts.length,
          debug_stop_reason,
          debug_input_chars,
          debug_prelude_chars,
          debug_max_output_tokens_used,
          debug_provider,
          debug_ingest: ingestVerdict,
        });
      }

      return json(res, 200, {
        ok: true,
        canonical,
        assistant_text: assistantText,
        vault_write: { status: vp.status, id: turn_id },
        model,
        deep_mode,
        usd_estimate,
        spend: { month_utc: month, cap_usd: cap, usd_spent: used_after },
        assistant_json,
        facts_extracted: extractedFacts.length,
        // C) Debug telemetry in response (additive keys only)
        debug_stop_reason,
        debug_input_chars,
        debug_prelude_chars,
        debug_max_output_tokens_used,
        debug_provider,
        debug_karma_ctx: karmaCtx ? "ok" : "unavailable",
        debug_search,
        debug_ingest: ingestVerdict,
      });
    }

    // --- POST /v1/chatlog (single or batch) ---
    if (req.method === "POST" && req.url === "/v1/chatlog") {
      console.log("[DEBUG] /v1/chatlog endpoint hit");

      const ip = getClientIp(req);
      const rl = checkRateLimit("capture", ip);
      if (rl) return json(res, 429, { ok: false, error: "rate_limited", retry_after_s: rl.retry_after_s });

      const token = bearerToken(req);
      if (!HUB_CAPTURE_TOKEN || !token || token !== HUB_CAPTURE_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const raw = await parseBody(req);
      let payload;
      try { payload = JSON.parse(raw); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      if (payload && Array.isArray(payload.batch)) {
        const items = payload.batch;
        if (items.length === 0) return json(res, 400, { ok: false, error: "empty_batch" });
        if (items.length > 200) return json(res, 400, { ok: false, error: "batch_too_large", max: 200 });

        const results = [];
        let succeeded = 0;
        let failed = 0;

        for (let i = 0; i < items.length; i++) {
          const item = items[i];
          const v = validateChatlogItem(item);
          if (!v.valid) {
            results.push({ index: i, ok: false, error: v.error });
            failed++;
            continue;
          }
          try {
            const r = await writeChatlogItemToVault(item);
            if (r.ok) {
              results.push({ index: i, ok: true, id: r.turn_id });
              succeeded++;
            } else {
              results.push({ index: i, ok: false, error: "vault_write_failed", vault_status: r.status });
              failed++;
            }
          } catch (e) {
            results.push({ index: i, ok: false, error: "internal_error" });
            failed++;
          }
        }

        return json(res, 200, { ok: true, batch: true, total: items.length, succeeded, failed, results });
      }

      const v = validateChatlogItem(payload);
      if (!v.valid) return json(res, 400, { ok: false, error: v.error });

      const r = await writeChatlogItemToVault(payload);
      if (!r.ok) {
        return json(res, 500, { ok: false, error: "vault_write_failed" });
      }
      return json(res, 200, { id: r.turn_id, stored: true, timestamp: nowIso() });
    }

    // --- POST /v1/handoff/save ---
    if (req.method === "POST" && req.url === "/v1/handoff/save") {
      const ip = getClientIp(req);
      const rl = checkRateLimit("handoff", ip);
      if (rl) return json(res, 429, { ok: false, error: "rate_limited", retry_after_s: rl.retry_after_s });

      const token = bearerToken(req);
      if (!HUB_HANDOFF_TOKEN || !token || token !== HUB_HANDOFF_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const raw = await parseBody(req);
      let body;
      try { body = JSON.parse(raw); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      const { principal_id, scope, project, handoff_md } = body || {};
      if (!principal_id || !scope || !handoff_md) {
        return json(res, 400, { ok: false, error: "missing_fields", required: ["principal_id", "scope", "handoff_md"] });
      }
      if (typeof handoff_md !== "string") {
        return json(res, 400, { ok: false, error: "handoff_md_must_be_string" });
      }

      const filename = safeHandoffFilename(principal_id, scope);
      let finalPath;
      try {
        finalPath = atomicWriteHandoff(HANDOFF_DIR, filename, handoff_md);
      } catch (e) {
        console.error("[HANDOFF] write failed:", e.message);
        return json(res, 500, { ok: false, error: "write_failed" });
      }

      const bytes = Buffer.byteLength(handoff_md, "utf8");
      console.log(`[HANDOFF] saved: ${filename} (${bytes} bytes)`);
      return json(res, 200, { ok: true, path: finalPath, bytes });
    }

    // --- GET /v1/handoff/latest ---
    if (req.method === "GET" && req.url.startsWith("/v1/handoff/latest")) {
      const ip = getClientIp(req);
      const rl = checkRateLimit("handoff", ip);
      if (rl) return json(res, 429, { ok: false, error: "rate_limited", retry_after_s: rl.retry_after_s });

      const token = bearerToken(req);
      if (!HUB_HANDOFF_TOKEN || !token || token !== HUB_HANDOFF_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const parsed = new URL(req.url, `http://localhost`);
      const principal_id = parsed.searchParams.get("principal_id") || "";
      const scope = parsed.searchParams.get("scope") || "";

      if (!principal_id || !scope) {
        return json(res, 400, { ok: false, error: "missing_params", required: ["principal_id", "scope"] });
      }

      const filename = safeHandoffFilename(principal_id, scope);
      const filePath = `${HANDOFF_DIR}/${filename}`;

      let stat;
      try { stat = fs.statSync(filePath); } catch {
        return json(res, 404, { ok: false, error: "not_found" });
      }

      let handoff_md;
      try { handoff_md = fs.readFileSync(filePath, "utf8"); } catch (e) {
        console.error("[HANDOFF] read failed:", e.message);
        return json(res, 500, { ok: false, error: "read_failed" });
      }

      return json(res, 200, {
        ok: true,
        handoff_md,
        updated_at: stat.mtime.toISOString(),
        bytes: stat.size,
      });
    }

    // --- GET /v1/checkpoint/latest (proxy to Vault, UI-facing) ---
    if (req.method === "GET" && req.url === "/v1/checkpoint/latest") {
      const ip = getClientIp(req);
      const rl = checkRateLimit("handoff", ip);
      if (rl) return json(res, 429, { ok: false, error: "rate_limited", retry_after_s: rl.retry_after_s });

      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const vaultUrl = new URL("/v1/checkpoint/latest", VAULT_INTERNAL_URL).toString();
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);
      let upstream;
      try {
        upstream = await fetch(vaultUrl, {
          headers: { Authorization: "Bearer " + VAULT_BEARER },
          signal: controller.signal,
        });
      } catch (fetchErr) {
        clearTimeout(timeout);
        const isTimeout = fetchErr.name === "AbortError";
        return json(res, 504, { ok: false, error: isTimeout ? "upstream_timeout" : "upstream_unreachable",
          details: String(fetchErr.message || fetchErr).slice(0, 200) });
      }
      clearTimeout(timeout);

      const upstreamStatus = upstream.status;
      let upstreamBody;
      try { upstreamBody = await upstream.json(); } catch { upstreamBody = null; }

      if (upstreamStatus < 200 || upstreamStatus >= 300) {
        return json(res, upstreamStatus, {
          ok: false, error: "upstream_error",
          upstream_status: upstreamStatus,
          upstream_body: upstreamBody,
        });
      }

      return json(res, 200, upstreamBody || { ok: false, error: "empty_upstream_response" });
    }

    // --- POST /v1/promote (proxy to Vault, token-gated, UI-facing) ---
    if (req.method === "POST" && req.url === "/v1/promote") {
      const ip = getClientIp(req);
      const rl = checkRateLimit("promote", ip);
      if (rl) return json(res, 429, { ok: false, error: "rate_limited", retry_after_s: rl.retry_after_s });

      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      let body = {};
      try {
        const chunks = [];
        for await (const chunk of req) chunks.push(chunk);
        body = JSON.parse(Buffer.concat(chunks).toString() || "{}");
      } catch { body = {}; }

      const vaultUrl = new URL("/v1/promote", VAULT_INTERNAL_URL).toString();
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000);
      let upstream;
      try {
        upstream = await fetch(vaultUrl, {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + VAULT_BEARER,
            "Content-Type": "application/json",
            "X-Forwarded-For": "127.0.0.1",
          },
          body: JSON.stringify(body),
          signal: controller.signal,
        });
      } catch (fetchErr) {
        clearTimeout(timeout);
        const isTimeout = fetchErr.name === "AbortError";
        return json(res, 504, { ok: false, error: isTimeout ? "upstream_timeout" : "vault_unreachable",
          details: String(fetchErr.message || fetchErr).slice(0, 200) });
      }
      clearTimeout(timeout);

      const upstreamStatus = upstream.status;
      let upstreamBody;
      try { upstreamBody = await upstream.json(); } catch { upstreamBody = null; }

      if (upstreamStatus < 200 || upstreamStatus >= 300) {
        return json(res, upstreamStatus, {
          ok: false, error: "upstream_error",
          upstream_status: upstreamStatus,
          upstream_body: upstreamBody,
        });
      }

      // Generate KARMA_BRIEF — plain-language session summary for Karma.
      // Prefer resume_prompt from promote body; fall back to fetchCheckpointLatestFromVault().
      let resume_prompt = upstreamBody?.resume_prompt || null;
      if (!resume_prompt) {
        try {
          const ck = await fetchCheckpointLatestFromVault();
          resume_prompt = ck?.resume_prompt || null;
        } catch (_) { /* non-fatal */ }
      }
      let karma_brief = null;
      if (resume_prompt) {
        try {
          // Truncate to first 1200 chars — header + MIS is sufficient for a brief
          const briefInput = resume_prompt.slice(0, 1200);
          const briefMessages = [
            {
              role: "system",
              content: [
                "You generate KARMA_BRIEF — a plain-language session summary for Karma (an AI peer).",
                "From the checkpoint below, write exactly 3-5 bullet points:",
                "• What was built or decided (plain English, no jargon)",
                "• What the system can now do that it couldn't before",
                "• The single most important next open question",
                "",
                "Rules: under 150 words total, no file paths/commands/JSON,",
                "second person to Karma ('You now have...', 'Next question:...'),",
                "concrete and specific.",
              ].join("\n"),
            },
            { role: "user", content: "CHECKPOINT:\n" + briefInput },
          ];
          const briefResult = await callLLM(env.MODEL_DEFAULT, briefMessages, 1600);
          karma_brief = briefResult.text || null;

          // Store karma_brief in vault for autonomous session continuity.
          // On next session, /v1/checkpoint/latest returns it → injected into system prompt.
          if (karma_brief) {
            const promoteCheckpointId = upstreamBody?.checkpoint_id || null;
            try {
              const _now = new Date().toISOString();
              await vaultPost("/v1/memory", VAULT_BEARER, {
                id: `karma_brief_${promoteCheckpointId || Date.now()}`,
                type: "log",
                tags: ["karma_brief", "checkpoint", "promote"],
                content: {
                  key: "karma_brief",
                  karma_brief,
                  checkpoint_id: promoteCheckpointId,
                },
                source: { kind: "tool", ref: "hub-bridge:promote-handler" },
                confidence: 1.0,
                created_at: _now,
                updated_at: _now,
                verification: {
                  protocol_version: "0.1",
                  verified_at: _now,
                  verifier: "hub-bridge-promote",
                  status: "verified",
                  notes: "auto-generated karma_brief from PROMOTE checkpoint",
                },
              });
              console.log(`[KARMA_BRIEF] stored in vault for ${promoteCheckpointId}`);
            } catch (storeErr) {
              console.error("[KARMA_BRIEF] vault store failed:", storeErr?.message || storeErr);
            }
          }
        } catch (briefErr) {
          console.error("[KARMA_BRIEF] generation failed:", briefErr?.message || briefErr);
        }
      }

      return json(res, 200, {
        ...(upstreamBody || {}),
        resume_prompt,
        karma_brief,
      });
    }

    // --- POST /v1/ingest ---
    // Accepts a base64-encoded PDF/text file, sends to Karma for evaluation,
    // detects ASSIMILATE/DEFER/DISCARD signal, writes synthesis to FalkorDB.
    // Called by the PowerShell folder watcher.
    if (req.method === "POST" && req.url === "/v1/ingest") {
      const ip = getClientIp(req);
      const rl = checkRateLimit("chat", ip);
      if (rl) return json(res, 429, { ok: false, error: "rate_limited", retry_after_s: rl.retry_after_s });

      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      // Accept up to 20MB body (base64 of large PDFs)
      const raw = await parseBody(req, 20000000);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      const { file_b64, filename = 'unknown.pdf', hint = '' } = body;
      if (!file_b64) return json(res, 400, { ok: false, error: "file_b64 required" });

      const buffer = Buffer.from(file_b64, 'base64');
      const _ext = filename.split('.').pop().toLowerCase();
      const rawText = (_ext === 'txt' || _ext === 'md')
        ? buffer.toString('utf8').trim()
        : await extractPdfText(buffer);
      if (!rawText) return json(res, 422, { ok: false, error: "pdf_extraction_failed" });

      console.log(`[INGEST] ${filename}: ${rawText.length} chars extracted`);

      // Chunk large documents — Karma evaluates in passes
      const CHUNK_SIZE = 6000;
      const chunks = [];
      for (let i = 0; i < rawText.length; i += CHUNK_SIZE) {
        chunks.push(rawText.slice(i, i + CHUNK_SIZE));
      }

      const results = [];
      for (let i = 0; i < chunks.length; i++) {
        const isMulti = chunks.length > 1;
        const prompt = isMulti
          ? `Document: ${filename} (part ${i + 1}/${chunks.length})\nHint: ${hint}\n\n${chunks[i]}\n\nEvaluate this content for your development.`
          : `Document: ${filename}\nHint: ${hint}\n\n${chunks[i]}\n\nEvaluate this content for your development.`;

        const karmaCtx = await fetchKarmaContext(hint || filename);
        const systemText = buildSystemText(karmaCtx, null);

        let chunkVerdict = 'none';
        let chunkSynthesis = null;
        let stored = false;

        try {
          const ingestMessages = [
            { role: 'system', content: systemText },
            { role: 'user', content: prompt },
          ];
          const ingestResult = await callLLM(env.MODEL_DEFAULT, ingestMessages, 1000);
          const responseText = ingestResult.text || '';
          const sm = responseText.match(SIGNAL_REGEX);

          if (sm) {
            const [, verdict, synthesis] = sm;
            chunkVerdict = verdict.toLowerCase();
            chunkSynthesis = synthesis.trim();
            if (chunkVerdict === 'assimilate' || chunkVerdict === 'defer') {
              const wr = await writeKarmaPrimitive({
                content: chunkSynthesis,
                verdict: chunkVerdict,
                source_file: filename,
                topic: hint,
              });
              stored = !!wr?.ok;
            }
            console.log(`[INGEST] ${filename} chunk ${i + 1}/${chunks.length}: ${verdict} stored=${stored}`);
          }
        } catch (chunkErr) {
          console.error(`[INGEST] chunk ${i + 1} failed:`, chunkErr.message);
        }

        results.push({
          chunk: i + 1,
          signal: chunkVerdict,
          synthesis: chunkSynthesis ? chunkSynthesis.slice(0, 200) : null,
          stored,
        });
      }

      return json(res, 200, { ok: true, filename, chunks: chunks.length, results });
    }


    // --- GET /v1/vault-file/:alias ---
    // Serve whitelisted vault files by alias. Used by Claude Code and other trusted clients.
    if (req.method === "GET" && req.url.startsWith("/v1/vault-file/")) {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const parsed = new URL(req.url, `http://localhost`);
      const alias = decodeURIComponent(parsed.pathname.replace("/v1/vault-file/", "").trim());
      if (!alias) return json(res, 400, { ok: false, error: "missing_alias" });
      if (!VAULT_FILE_ALIASES[alias]) {
        return json(res, 404, { ok: false, error: "alias_not_found", available: Object.keys(VAULT_FILE_ALIASES) });
      }

      const filePath = VAULT_FILE_ALIASES[alias];
      const tailParam = parsed.searchParams.get("tail");

      let content;
      try {
        content = fs.readFileSync(filePath, "utf-8");
      } catch (e) {
        return json(res, 404, { ok: false, error: "not_found", path: filePath });
      }

      if (tailParam) {
        const n = parseInt(tailParam, 10);
        if (!isNaN(n) && n > 0) {
          const lines = content.split("\n");
          content = lines.slice(-n).join("\n");
        }
      }

      return json(res, 200, { ok: true, alias, content, bytes: Buffer.byteLength(content, "utf-8") });
    }

    // --- PATCH /v1/vault-file/MEMORY.md ---
    // Append to or overwrite MEMORY.md. Used by Claude Code mid-session capture.
    if (req.method === "PATCH" && req.url === "/v1/vault-file/MEMORY.md") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const raw = await parseBody(req, 500000);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      const filePath = VAULT_FILE_ALIASES["MEMORY.md"];
      if (!filePath) return json(res, 500, { ok: false, error: "alias_not_configured" });

      if (body.append !== undefined) {
        try {
          fs.appendFileSync(filePath, "\n" + body.append);
          return json(res, 200, { ok: true, action: "append", bytes_appended: Buffer.byteLength(body.append, "utf-8") });
        } catch (e) {
          return json(res, 500, { ok: false, error: "write_failed", message: e.message });
        }
      } else if (body.content !== undefined && body.confirm_overwrite === true) {
        try {
          fs.writeFileSync(filePath, body.content, "utf-8");
          return json(res, 200, { ok: true, action: "overwrite", bytes: Buffer.byteLength(body.content, "utf-8") });
        } catch (e) {
          return json(res, 500, { ok: false, error: "write_failed", message: e.message });
        }
      } else {
        return json(res, 400, { ok: false, error: "missing_action", hint: "provide 'append' or 'content'+'confirm_overwrite:true'" });
      }
    }

    return notFound(res);

  } catch (e) {
    const msg = (e && e.message) ? e.message : String(e);
    return json(res, 500, { ok: false, error: "internal_error", message: msg.slice(0, 500) });
  }
});

loadSessionBrief();
setInterval(loadSessionBrief, 5 * 60 * 1000);
server.listen(PORT, "0.0.0.0", () => {
  console.log(`hub-bridge v2.11.0 listening on :${PORT}`);
});
