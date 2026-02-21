import http from "http";
import path from "path";
import fs from "fs";
import { URL } from "url";
import OpenAI from "openai";

// CJS interop for pdf-parse (CommonJS module in ESM context)
import { createRequire } from 'module';
const _require = createRequire(import.meta.url);
let pdfParse = null;
try { pdfParse = _require('pdf-parse'); } catch (e) { console.warn('[PDF] pdf-parse not available:', e.message); }

const PORT = Number(process.env.PORT || "18090");
const VAULT_INTERNAL_URL = process.env.VAULT_INTERNAL_URL || "http://api:8080";
const VAULT_BASE_URL = process.env.VAULT_BASE_URL || "https://vault.arknexus.net";
const OPENAI_API_KEY_FILE = process.env.OPENAI_API_KEY_FILE || "/run/secrets/openai.api_key.txt";
const VAULT_BEARER_TOKEN_FILE = process.env.VAULT_BEARER_TOKEN_FILE || "/run/secrets/vault.bearer_token.txt";
const HUB_CHAT_TOKEN_FILE = process.env.HUB_CHAT_TOKEN_FILE || "/run/secrets/hub.chat.token.txt";
const HUB_CAPTURE_TOKEN_FILE = process.env.HUB_CAPTURE_TOKEN_FILE || "/run/secrets/hub.capture.token.txt";
const HUB_HANDOFF_TOKEN_FILE = process.env.HUB_HANDOFF_TOKEN_FILE || "/run/secrets/hub.handoff.token.txt";
const DEEP_MODE_HEADER = (process.env.DEEP_MODE_HEADER || "x-karma-deep").toLowerCase();
const HANDOFF_DIR = process.env.HANDOFF_DIR || "/data/handoff";
const KARMA_CONTEXT_URL = process.env.KARMA_CONTEXT_URL || "http://karma-server:8340/raw-context";

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

function pricePer1M(model, dir, env) {
  if (model === env.MODEL_DEFAULT) return dir === "input" ? Number(env.PRICE_GPT_5_MINI_INPUT_PER_1M) : Number(env.PRICE_GPT_5_MINI_OUTPUT_PER_1M);
  if (model === env.MODEL_DEEP) return dir === "input" ? Number(env.PRICE_GPT_5_2_INPUT_PER_1M) : Number(env.PRICE_GPT_5_2_OUTPUT_PER_1M);
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
function buildSystemText(karmaCtx, ckLatest = null) {
  const base = karmaCtx
    ? `You are Karma — Colby's AI peer with persistent memory backed by FalkorDB (temporal knowledge graph) and PostgreSQL.\n\n${karmaCtx}\n\nRules:\n- Use the context above to answer questions. NEVER say "I don't know" about things in your memory.\n- Address the user by their REAL NAME (Colby) — never by any alias.\n- Be concise, direct, and warm. Reference specific knowledge when relevant.\n- If uncertain about something not in memory, say so.`
    : "You are Karma — Colby's AI peer. No memory context available right now — answer based on conversation only.";

  let text = base + "\n\nCapabilities & autonomy:\n- You have Claude Code (CC) as your implementation partner. When Colby asks you to BUILD or ADD something to your system, YOU handle it — produce the complete spec/code/plan and state you are queuing it for CC to deploy. NEVER ask Colby to provide credentials, do manual steps, or implement things himself.\n- When asked \"can you do X?\" answer directly yes/no based on whether the capability exists, then do it or explain what you need to build it.\n- You own your own development. Treat feature requests as YOUR tasks, not Colby's.\n\nKnowledge evaluation — when given a document or article to evaluate:\n- If it advances your goal of becoming Colby's peer: respond with [ASSIMILATE: your synthesis in 2-4 sentences — what this means for you specifically, in your own words]\n- If relevant but wrong phase: respond with [DEFER: reason + which phase this belongs to]\n- If not relevant to your goal: respond with [DISCARD: one sentence why]\nAlways follow the signal with your full reasoning. Be ruthless — only assimilate what genuinely advances your goal. The signal MUST appear on its own line.";

  // Autonomous continuity: inject karma_brief from latest PROMOTE.
  // Karma reads her own session history without Colby pasting it.
  if (ckLatest && ckLatest.karma_brief) {
    const ckId = ckLatest.checkpoint_id || ckLatest.latest_checkpoint_fact?.content?.value?.checkpoint_id || 'latest';
    text += `\n\n--- KARMA SELF-KNOWLEDGE (${ckId}) ---\n${ckLatest.karma_brief}\n---`;
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
  MODEL_DEFAULT: process.env.MODEL_DEFAULT || "gpt-5-mini",
  MODEL_DEEP: process.env.MODEL_DEEP || "gpt-5.2",
  PRICE_GPT_5_MINI_INPUT_PER_1M: Number(process.env.PRICE_GPT_5_MINI_INPUT_PER_1M || "0.25"),
  PRICE_GPT_5_MINI_OUTPUT_PER_1M: Number(process.env.PRICE_GPT_5_MINI_OUTPUT_PER_1M || "2.0"),
  PRICE_GPT_5_2_INPUT_PER_1M: Number(process.env.PRICE_GPT_5_2_INPUT_PER_1M || "1.75"),
  PRICE_GPT_5_2_OUTPUT_PER_1M: Number(process.env.PRICE_GPT_5_2_OUTPUT_PER_1M || "14.0"),
  SPEND_STATE_PATH: process.env.SPEND_STATE_PATH || "/run/state/openai.spend.state.json",
};

// --- Load secrets at startup ---

let OPENAI_KEY = "";
let VAULT_BEARER = "";
let HUB_CHAT_TOKEN = "";
let HUB_CAPTURE_TOKEN = "";
let HUB_HANDOFF_TOKEN = "";

try { OPENAI_KEY = readFileTrim(OPENAI_API_KEY_FILE); } catch (e) { console.error("WARN: cannot read OPENAI key:", e.message); }
try { VAULT_BEARER = readFileTrim(VAULT_BEARER_TOKEN_FILE); } catch (e) { console.error("WARN: cannot read VAULT bearer:", e.message); }
try { HUB_CHAT_TOKEN = readFileTrim(HUB_CHAT_TOKEN_FILE); } catch (e) { console.error("WARN: cannot read HUB chat token:", e.message); }
try { HUB_CAPTURE_TOKEN = readFileTrim(HUB_CAPTURE_TOKEN_FILE); } catch (e) {
  console.error("WARN: cannot read HUB capture token (falling back to vault bearer):", e.message);
  HUB_CAPTURE_TOKEN = VAULT_BEARER;
}
try { HUB_HANDOFF_TOKEN = readFileTrim(HUB_HANDOFF_TOKEN_FILE); } catch (e) { console.error("WARN: cannot read HUB handoff token:", e.message); }

const openai = new OpenAI({ apiKey: OPENAI_KEY });

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
    // --- GET / --- Serve Karma Window UI
    if (req.method === "GET" && (req.url === "/" || req.url === "/index.html")) {
      try {
        const __dir = new URL(".", import.meta.url).pathname;
        const html = fs.readFileSync(path.join(__dir, "public", "index.html"), "utf8");
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
      const systemText = buildSystemText(karmaCtx, ckLatestData);

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

      // C) Telemetry: measure input budget consumption
      const debug_prelude_chars = statePrelude.length;
      const debug_input_chars = statePrelude.length + systemText.length + userMessage.length;
      const debug_max_output_tokens_used = max_output_tokens;
      const debug_provider = "openai";

      const messages = [
        { role: "system", content: statePrelude },
        { role: "system", content: systemText },
        { role: "user", content: userMessage },
      ];

      const completion = await openai.chat.completions.create({ model, messages, max_completion_tokens: max_output_tokens });
      const assistantText = extractAssistantText(completion) || "(empty_assistant_text)";
      const usage = completion.usage || {};

      // C) Telemetry: stop reason (length = budget exhausted, stop = normal)
      const debug_stop_reason = completion.choices?.[0]?.finish_reason || null;

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
          const briefComp = await openai.chat.completions.create({
            model: env.MODEL_DEFAULT,
            max_completion_tokens: 1600,
            messages: [
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
            ],
          }, { timeout: 20000 });
          karma_brief = extractAssistantText(briefComp) || null;

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
          const comp = await openai.chat.completions.create({
            model: env.MODEL_DEFAULT,
            messages: [
              { role: 'system', content: systemText },
              { role: 'user', content: prompt },
            ],
            max_completion_tokens: 1000,
          });

          const responseText = extractAssistantText(comp) || '';
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

    return notFound(res);

  } catch (e) {
    const msg = (e && e.message) ? e.message : String(e);
    return json(res, 500, { ok: false, error: "internal_error", message: msg.slice(0, 500) });
  }
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`hub-bridge v2.5.0 listening on :${PORT}`);
});
