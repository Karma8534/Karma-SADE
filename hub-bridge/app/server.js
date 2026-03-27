import http from "http";
import path from "path";
import fs from "fs";
import { URL } from "url";
import OpenAI from "openai";
import Anthropic from "@anthropic-ai/sdk";
import { pricePer1M, estimateUsd, validatePricingEnv } from "./lib/pricing.js";
import { chooseModel, getVerifierModel, validateModelEnv, GlmRateLimiter, GLM_INGEST_SLOT_TIMEOUT_MS } from "./lib/routing.js";
import { processFeedback, prunePendingWrites } from "./lib/feedback.js";
import { resolveLibraryUrl } from "./lib/library_docs.js";
import { generateIntentId, getSurfaceIntents, buildActiveIntentsText } from "./lib/deferred_intent.js";

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
const CC_SERVER_URL     = process.env.CC_SERVER_URL     || "http://100.124.194.102:7891";
const CLAUDEMEM_URL     = process.env.CLAUDEMEM_URL     || "http://100.124.194.102:37777";

// ── Within-session conversation history ──────────────────────────────────────
// Keeps the last N exchange pairs in memory, keyed by a hash of the bearer token.
// Sessions expire after SESSION_TTL_MS of inactivity → next message starts fresh.
const SESSION_TTL_MS    = 60 * 60 * 1000;  // 60 minutes
const MAX_SESSION_TURNS = Number(process.env.MAX_SESSION_TURNS || "20"); // exchange pairs (40 messages total)
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
  // Filter out empty content — Anthropic rejects empty user/assistant messages
  return sess.turns.filter(t => t.content && (typeof t.content === "string" ? t.content.trim() : true));
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
  saveSessionsToDisk();
  scheduleDistillation(); // reset idle timer — distill after 10min inactivity
}

// Session-close distillation — after inactivity, distill session into shadow.md
const DISTILL_IDLE_MS = 10 * 60 * 1000; // 10 minutes of inactivity
const DISTILL_MIN_TURNS = 8;             // minimum turns (4 exchanges) to trigger
let _distillTimer = null;
let _lastDistilledKey = null;

function scheduleDistillation() {
  if (_distillTimer) clearTimeout(_distillTimer);
  _distillTimer = setTimeout(runDistillation, DISTILL_IDLE_MS);
}

async function runDistillation() {
  try {
    // Find the most recently active session with enough turns
    let bestKey = null, bestSess = null;
    for (const [key, sess] of _sessionStore) {
      if (sess.turns.length >= DISTILL_MIN_TURNS) {
        if (!bestSess || sess.lastActive > bestSess.lastActive) {
          bestKey = key; bestSess = sess;
        }
      }
    }
    if (!bestKey || bestKey === _lastDistilledKey) return;

    // Build a condensed transcript from the last 10 exchanges
    const recentTurns = bestSess.turns.slice(-20);
    let transcript = "";
    for (const t of recentTurns) {
      const label = t.role === "user" ? "User" : "Karma";
      const snip = t.content.length > 300 ? t.content.slice(0, 300) + "..." : t.content;
      transcript += `${label}: ${snip}\n\n`;
    }

    // Call LLM to distill
    if (!anthropic) { console.warn("[DISTILL] no Anthropic client"); return; }
    const distillPrompt = `You are Karma's session memory system. Read this conversation transcript and write a 3-5 sentence summary of Karma's current state of mind — what was discussed, what was decided, what she was thinking about when the session ended. Write in first person as Karma. Be specific, not generic.\n\nTranscript:\n${transcript}`;

    const resp = await anthropic.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 300,
      messages: [{ role: "user", content: distillPrompt }],
    });
    const distillation = resp.content?.[0]?.text;
    if (!distillation) { console.warn("[DISTILL] empty response"); return; }

    // Write to K2 shadow.md
    const ARIA_KEY = process.env.ARIA_SERVICE_KEY || "";
    if (!ARIA_URL || !ARIA_KEY) { console.warn("[DISTILL] no ARIA config"); return; }

    const ts = new Date().toISOString().slice(0, 16).replace("T", " ");
    const shadowContent = `\n--- Session distillation (${ts}) ---\n${distillation}\n`;

    const r = await fetch(`${ARIA_URL}/api/tools/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Aria-Service-Key": ARIA_KEY },
      body: JSON.stringify({ tool: "file_write", input: { path: "/mnt/c/dev/Karma/k2/cache/shadow.md", content: shadowContent, mode: "append" } }),
      signal: AbortSignal.timeout(10000),
    });
    const result = await r.json();
    console.log(`[DISTILL] session distillation written to shadow.md: ok=${result.ok}`);
    _lastDistilledKey = bestKey;
  } catch (e) {
    console.warn(`[DISTILL] failed: ${e.message}`);
  }
}

// Session store disk persistence — survives container rebuilds
const SESSION_FILE = "/run/state/sessions.json";

function loadSessionsFromDisk() {
  try {
    if (!fs.existsSync(SESSION_FILE)) return;
    const data = JSON.parse(fs.readFileSync(SESSION_FILE, "utf-8"));
    const now = Date.now();
    let loaded = 0;
    for (const [key, sess] of Object.entries(data)) {
      if (now - sess.lastActive > SESSION_TTL_MS) continue;
      _sessionStore.set(key, sess);
      loaded++;
    }
    if (loaded > 0) console.log(`[SESSION] loaded ${loaded} sessions from disk`);
  } catch (e) {
    console.warn("[SESSION] disk load failed:", e.message);
  }
}

function saveSessionsToDisk() {
  try {
    const obj = {};
    const now = Date.now();
    for (const [key, sess] of _sessionStore) {
      if (now - sess.lastActive <= SESSION_TTL_MS) obj[key] = sess;
    }
    fs.writeFileSync(SESSION_FILE, JSON.stringify(obj));
  } catch (e) {
    console.warn("[SESSION] disk save failed:", e.message);
  }
}

// ─────────────────────────────────────────────────────────────────────────────

// Coordination bus — structured agent-to-agent messaging.
// In-memory cache (100 entries, 24h TTL). Persisted to COORD_FILE so rebuilds don't lose messages.
const COORD_MAX_ENTRIES = 100;
const COORD_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours
const _coordinationCache = new Map();      // id → coordination entry object
const COORD_FILE = "/run/state/coordination.jsonl";

// Valid coordination message types (K2 Merged Agent Architecture)
const COORDINATION_TYPES = [
  'seed_issue',        // Karma-Core → Kiki: new issue/goal
  'promote_request',   // Kiki → CC: request promotion review
  'approval_required', // Arbiter → Colby: critical path approval needed
  'rollback_event',    // Any approved actor → all: rollback notification
  'status_update',     // Any actor → bus: informational
];

function loadCoordinationFromDisk() {
  try {
    if (!fs.existsSync(COORD_FILE)) return;
    const lines = fs.readFileSync(COORD_FILE, "utf-8").trim().split("\n").filter(Boolean);
    const now = Date.now();
    let loaded = 0;
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        if (now - new Date(entry.created_at).getTime() > COORD_TTL_MS) continue;
        _coordinationCache.set(entry.id, entry);
        loaded++;
      } catch (_) { /* skip malformed lines */ }
    }
    if (loaded > 0) console.log(`[COORD] loaded ${loaded} entries from disk`);
  } catch (e) {
    console.warn("[COORD] disk load failed:", e.message);
  }
}

function appendCoordinationToDisk(entry) {
  try {
    fs.appendFileSync(COORD_FILE, JSON.stringify(entry) + "\n");
  } catch (e) {
    console.warn("[COORD] disk append failed:", e.message);
  }
}

function saveCoordinationToDisk() {
  try {
    const lines = [..._coordinationCache.values()].map(e => JSON.stringify(e)).join("\n") + "\n";
    fs.writeFileSync(COORD_FILE, lines);
  } catch (e) {
    console.warn("[COORD] disk save failed:", e.message);
  }
}

function generateCoordId() {
  const ts = Date.now();
  const rand = Math.random().toString(36).substring(2, 6);
  return `coord_${ts}_${rand}`;
}

function evictExpiredCoordination() {
  const now = Date.now();
  for (const [id, entry] of _coordinationCache) {
    if (now - new Date(entry.created_at).getTime() > COORD_TTL_MS) {
      _coordinationCache.delete(id);
    }
  }
  // FIFO eviction if over max
  if (_coordinationCache.size > COORD_MAX_ENTRIES) {
    const sorted = [..._coordinationCache.entries()]
      .sort((a, b) => new Date(a[1].created_at) - new Date(b[1].created_at));
    const toRemove = sorted.slice(0, _coordinationCache.size - COORD_MAX_ENTRIES);
    for (const [id] of toRemove) _coordinationCache.delete(id);
  }
}

// CC Session Brief cache - refreshed every 5min, gives Karma live session context
const SESSION_BRIEF_PATH = "/karma/repo/cc-session-brief.md";
let _sessionBriefCache = "";
function loadSessionBrief() {
  try {
    const t = fs.readFileSync(SESSION_BRIEF_PATH, "utf8");
    if (t && t.length > 50) _sessionBriefCache = t.trim();
  } catch (_) {}
}

// MEMORY.md cache — tail of Karma's memory spine, injected into every request.
// Tail (most recent) = most relevant. Refreshed every 5min same as session brief.
const MEMORY_MD_PATH = "/karma/MEMORY.md";
const MEMORY_MD_TAIL_CHARS = 2000;
let _memoryMdCache = "";
function loadMemoryMd() {
  try {
    const t = fs.readFileSync(MEMORY_MD_PATH, "utf8");
    if (t && t.length > 50) {
      _memoryMdCache = t.length > MEMORY_MD_TAIL_CHARS ? t.slice(-MEMORY_MD_TAIL_CHARS) : t.trim();
    }
  } catch (_) {}
}

// direction.md cache — Karma's current architectural direction, constraints, stage.
// Loaded at startup, refreshed every 5min. Injected into buildSystemText.
const DIRECTION_MD_PATH = "/karma/repo/direction.md";
let _directionMdCache = "";
function loadDirectionMd() {
  try {
    const t = fs.readFileSync(DIRECTION_MD_PATH, "utf8");
    if (t && t.length > 50) _directionMdCache = t.trim();
  } catch (_) {}
}

// Synthesis cache - most recent [SYNTHESIS] entry from vault via FAISS.
// Refreshed every 5min. Injected into buildSystemText for session continuity.
let _synthesisCacheText = "";
async function loadSynthesisCache() {
  try {
    const r = await fetch(FAISS_SEARCH_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: "synthesis session decisions insights pitfalls", limit: 1 }),
    });
    if (r.ok) {
      const d = await r.json();
      const top = (d.results || [])[0];
      if (top && top.content_preview) {
        _synthesisCacheText = top.content_preview;
        console.log("[SYNTHESIS] cache refreshed:", _synthesisCacheText.length, "chars");
      }
    }
  } catch (e) {
    console.error("[SYNTHESIS] cache refresh failed:", e.message);
  }
}


// K2 memory graph cache — fetched once per request cycle, cached 5 min.
// Aria on K2 exposes GET /api/memory/graph?query=... — returns seed_facts, related_facts, entities.
let _k2MemGraphCache = null;
let _k2MemGraphCacheAt = 0;
const K2_MEM_CACHE_TTL_MS = 5 * 60 * 1000;

async function fetchK2MemoryGraph(query = "Colby") {
  if (!ARIA_SERVICE_KEY || !ARIA_URL) return null;
  const now = Date.now();
  if (_k2MemGraphCache && (now - _k2MemGraphCacheAt) < K2_MEM_CACHE_TTL_MS) {
    return _k2MemGraphCache;
  }
  try {
    const url = `${ARIA_URL}/api/memory/graph?query=${encodeURIComponent(query)}&limit=10`;
    const res = await fetch(url, {
      method: "GET",
      headers: { "X-Aria-Service-Key": ARIA_SERVICE_KEY },
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) { console.warn(`[K2-MEM] /api/memory/graph → ${res.status}`); return null; }
    const data = await res.json();
    if (!data.success || !data.graph_context) return null;
    const ctx = data.graph_context;
    const lines = [];
    if (ctx.seed_facts?.length)    lines.push("Key facts: "  + ctx.seed_facts.map(f => `${f.content} (${f.fact_type})`).join("; "));
    if (ctx.related_facts?.length) lines.push("Related: "    + ctx.related_facts.map(f => f.content).join("; "));
    if (ctx.entities?.length)      lines.push("Entities: "   + ctx.entities.map(e => e.name).join(", "));
    const text = lines.join("\n");
    _k2MemGraphCache = text;
    _k2MemGraphCacheAt = now;
    console.log(`[K2-MEM] graph loaded (${text.length} chars, ${ctx.graph_hits} hits)`);
    return text;
  } catch (e) {
    console.warn(`[K2-MEM] fetch failed: ${e.message}`);
    return null;
  }
}

// K2 working memory — scratchpad, shadow, kiki state/journal/backlog from K2 cache.
// Fetched via /api/exec (shell_run endpoint). Injected into buildSystemText for session continuity.
let _k2WorkingMemCache = null;
let _k2WorkingMemCacheAt = 0;
const K2_WORKING_MEM_MAX_CHARS = 20000; // F-5: increased to fit evolution journal (tail -10 ~6KB)
const K2_FRESHNESS_SLO_SECONDS = Number(process.env.K2_FRESHNESS_SLO_SECONDS || "120");
let _k2FreshnessCache = null;
let _k2FreshnessCacheAt = 0;
const K2_FRESHNESS_CACHE_MS = 5000;

const K2_FRESHNESS_CMD = "now=$(date +%s); for f in /mnt/c/dev/Karma/k2/cache/kiki_state.json /mnt/c/dev/Karma/k2/cache/kiki_journal.jsonl /mnt/c/dev/Karma/k2/cache/kiki_issues.jsonl /mnt/c/dev/Karma/k2/cache/kiki_rules.jsonl; do if [ -f \"$f\" ]; then mt=$(stat -c %Y \"$f\"); age=$((now-mt)); echo \"__KIKI_AGE__ $(basename \"$f\") $age\"; else echo \"__KIKI_AGE__ $(basename \"$f\") MISSING\"; fi; done";

function parseK2Freshness(stdout) {
  if (!stdout || typeof stdout !== "string") return null;
  const ages = {};
  const missing = [];
  for (const line of stdout.split("\n")) {
    if (!line.startsWith("__KIKI_AGE__ ")) continue;
    const parts = line.trim().split(/\s+/);
    if (parts.length < 3) continue;
    const name = parts[1];
    const value = parts[2];
    if (value === "MISSING") {
      missing.push(name);
      continue;
    }
    const age = Number(value);
    if (Number.isFinite(age)) ages[name] = age;
  }
  // Codex S5 spec: only kiki_state.json determines staleness (written every kiki cycle).
  // state_age > 300s = kiki stopped entirely; cycle_age > 180s = 3 missed cycles.
  // kiki_issues.jsonl, kiki_journal.jsonl, kiki_rules.jsonl = observational only.
  const STATE_STALE_S = 300;
  const CYCLE_STALE_S = 180;
  const stateAge = ages["kiki_state.json"] ?? null;
  const stateMissing = missing.includes("kiki_state.json");
  const stale = stateMissing || (stateAge !== null && stateAge > CYCLE_STALE_S);
  return { stale, stateAge, ages, missing };
}

async function fetchK2FreshnessStatus(force = false) {
  if (!ARIA_SERVICE_KEY || !ARIA_URL) {
    return { ok: false, error: "aria_not_configured" };
  }
  const now = Date.now();
  if (!force && _k2FreshnessCache && (now - _k2FreshnessCacheAt) < K2_FRESHNESS_CACHE_MS) {
    return _k2FreshnessCache;
  }
  try {
    const res = await fetch(`${ARIA_URL}/api/exec`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Aria-Service-Key": ARIA_SERVICE_KEY,
      },
      body: JSON.stringify({ command: K2_FRESHNESS_CMD }),
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) {
      return { ok: false, error: `api_exec_${res.status}` };
    }
    const data = await res.json();
    if (!data.ok || !data.stdout) {
      return { ok: false, error: "empty_stdout" };
    }
    const parsed = parseK2Freshness(data.stdout);
    if (!parsed) {
      return { ok: false, error: "parse_failed" };
    }
    const status = {
      ok: true,
      stale_context: parsed.stale,
      state_age_seconds: parsed.stateAge,
      cycle_threshold_seconds: 180,
      state_threshold_seconds: 300,
      ages_seconds: parsed.ages,
      missing_artifacts: parsed.missing,
      observational: ["kiki_issues.jsonl", "kiki_journal.jsonl", "kiki_rules.jsonl"],
      generated_at: nowIso(),
    };
    _k2FreshnessCache = status;
    _k2FreshnessCacheAt = now;
    return status;
  } catch (e) {
    return { ok: false, error: String(e?.message || e) };
  }
}

async function fetchK2WorkingMemory() {
  if (!ARIA_SERVICE_KEY || !ARIA_URL) return null;
  const now = Date.now();
  if (_k2WorkingMemCache && (now - _k2WorkingMemCacheAt) < K2_MEM_CACHE_TTL_MS) {
    return _k2WorkingMemCache;
  }
  try {
    // F-5: EVOLUTION JOURNAL first (before scratchpad) so it is never displaced by large sections
    // F-4: BEHAVIORAL PATTERNS sorted by momentum desc
    const cmd = `${K2_FRESHNESS_CMD}; echo '=== EVOLUTION JOURNAL (last 10) ===' && tail -10 /mnt/c/dev/Karma/k2/cache/vesper_governor_audit.jsonl 2>/dev/null | python3 -c 'import sys,json;[print(json.dumps({k:v for k,v in json.loads(l).items() if k in ["ts","event","candidate_id","pattern_type","reason","momentum","spine_version"]})) for l in sys.stdin if l.strip()]' 2>/dev/null || echo '(empty)' && echo '=== BEHAVIORAL PATTERNS (by momentum) ===' && python3 -c 'import json,os;f="/mnt/c/dev/Karma/k2/cache/vesper_identity_spine.json";s=json.load(open(f)) if os.path.exists(f) else {};st=s.get("evolution",{}).get("stable_identity",[]);bp=[p for p in st if p.get("type") not in ("cascade_performance",)];bp_s=sorted(bp,key=lambda p:float(p.get("momentum",1.0)),reverse=True);[(print("["+p.get("type","")+"] m="+str(round(float(p.get("momentum",1.0)),2))+" "+((p.get("proposed_change") or {}).get("description","-")))) for p in bp_s[-5:]] if bp_s else print("(none yet)")' 2>/dev/null || echo '(unavailable)' && echo '=== SCRATCHPAD ===' && cat /mnt/c/dev/Karma/k2/cache/scratchpad.md 2>/dev/null || echo '(empty)' && echo '=== SHADOW ===' && tail -c 1500 /mnt/c/dev/Karma/k2/cache/shadow.md 2>/dev/null || echo '(empty)' && echo '=== KIKI STATE ===' && cat /mnt/c/dev/Karma/k2/cache/kiki_state.json 2>/dev/null || echo '(empty)' && echo '=== KIKI JOURNAL (last 5) ===' && tail -5 /mnt/c/dev/Karma/k2/cache/kiki_journal.jsonl 2>/dev/null || echo '(empty)' && echo '=== KIKI BACKLOG ===' && cat /mnt/c/dev/Karma/k2/cache/kiki_issues.jsonl 2>/dev/null || echo '(empty)'`;
    const res = await fetch(`${ARIA_URL}/api/exec`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Aria-Service-Key": ARIA_SERVICE_KEY,
      },
      body: JSON.stringify({ command: cmd }),
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) { console.warn(`[K2-WORK] /api/exec → ${res.status}`); return null; }
    const data = await res.json();
    const stdout = data.stdout || data.output || "";
    if (!data.ok || !stdout) return null;
    const freshness = parseK2Freshness(stdout);
    const freshnessBlock = freshness
      ? [
          "=== KIKI FRESHNESS ===",
          `STALE_CONTEXT=${freshness.stale ? "true" : "false"}`,
          `STATE_AGE_SECONDS=${freshness.stateAge ?? "unknown"}`,
          `CYCLE_THRESHOLD_SECONDS=180`,
          `MISSING_ARTIFACTS=${freshness.missing.join(",") || "none"}`,
        ].join("\n")
      : "";
    const combined = freshnessBlock ? `${freshnessBlock}\n${stdout}` : stdout;
    const text = combined.length > K2_WORKING_MEM_MAX_CHARS
      ? combined.slice(0, K2_WORKING_MEM_MAX_CHARS) + "\n...(truncated)"
      : combined;
    _k2WorkingMemCache = text;
    _k2WorkingMemCacheAt = now;
    console.log(`[K2-WORK] working memory loaded (${text.length} chars)`);
    return text;
  } catch (e) {
    console.warn(`[K2-WORK] fetch failed: ${e.message}`);
    return null;
  }
}

// Local file server — Payback (Colby's machine) via Tailscale
const LOCAL_FILE_SERVER_URL = process.env.LOCAL_FILE_SERVER_URL || "";
const LOCAL_FILE_TOKEN = process.env.LOCAL_FILE_TOKEN || "";

const ARIA_URL = process.env.ARIA_URL || "http://100.75.109.92:7890";

// Julian cortex endpoints (K2 primary, P1 fallback)
const K2_CORTEX_URL = process.env.K2_CORTEX_URL || "http://100.75.109.92:7892";
const P1_CORTEX_URL = process.env.P1_CORTEX_URL || "http://100.124.194.102:7893";

// Fire-and-forget cortex ingest (non-blocking)
function cortexIngest(label, text) {
  const body = JSON.stringify({ label, text: (text || "").slice(0, 500) });
  const opts = { method: "POST", headers: { "Content-Type": "application/json" }, body };
  fetch(K2_CORTEX_URL + "/ingest", opts)
    .then(r => { if (!r.ok) throw new Error(`K2 HTTP ${r.status}`); })
    .catch(() => {
      // K2 down or HTTP error, try P1 fallback
      fetch(P1_CORTEX_URL + "/ingest", opts)
        .then(r => { if (!r.ok) console.error("[CORTEX] P1 ingest HTTP", r.status); })
        .catch(e => console.error("[CORTEX] ingest failed (both K2+P1):", e.message));
    });
}
const ARIA_SERVICE_KEY = process.env.ARIA_SERVICE_KEY || "";

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

// Pending memory writes -- keyed by write_id, awaiting /v1/feedback approval
const pending_writes = new Map();

// Pending intent proposals -- keyed by intent_id, awaiting /v1/feedback approval
const pending_intents = new Map();

// Approved active intents -- loaded from vault ledger at startup, updated on approval
// intent_id → intent object (status:"active")
const _activeIntentsMap = new Map();

// Tracks once_per_conversation intents that have already fired this server session
const _firedThisSession = new Set();

setInterval(() => {
  const now = Date.now();
  for (const [k, v] of rlBuckets) {
    if (now - v.last_ms > 5 * 60 * 1000) rlBuckets.delete(k);
  }
  // Expire pending writes older than 30 minutes
  for (const [k, v] of pending_writes) {
    if (now - v.ts > 30 * 60 * 1000) pending_writes.delete(k);
  }
  // Expire pending intent proposals older than 30 minutes
  for (const [k, v] of pending_intents) {
    if (now - v.ts > 30 * 60 * 1000) pending_intents.delete(k);
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

// --- Verifier hook seam (governance seam 4a) ---
// Cross-provider second opinion for structural changes. Gated by VERIFIER_ENABLED env var.
// Default: off. Enable with VERIFIER_ENABLED=true in hub.env.
const VERIFIER_ENABLED = (process.env.VERIFIER_ENABLED || "").toLowerCase() === "true";
async function callVerifier(question, context) {
  if (!VERIFIER_ENABLED) return { skipped: true, reason: "verifier_disabled" };
  const verifierModel = getVerifierModel(env);
  try {
    const result = await callLLM(verifierModel, [
      { role: "system", content: "You are a cross-provider verification agent. Evaluate whether the proposed change is safe, consistent with identity, and does not introduce regressions. Respond with: APPROVE, HOLD, or REJECT followed by one sentence of reasoning." },
      { role: "user", content: `${question}\n\nContext: ${context}` },
    ], 200);
    return { skipped: false, model: verifierModel, verdict: (result.text || "").trim() };
  } catch (e) {
    return { skipped: false, model: verifierModel, error: e.message };
  }
}

// pricePer1M and estimateUsd imported from ../lib/pricing.js

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

// --- Semantic search via anr-vault-search (FAISS) ---
const FAISS_SEARCH_URL    = process.env.FAISS_SEARCH_URL || "http://anr-vault-search:8081/v1/search";
const FAISS_SEARCH_K      = Number(process.env.FAISS_SEARCH_K || "3");
const FAISS_ENABLED       = (process.env.FAISS_ENABLED || "1") === "1";

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
const SIGNAL_REGEX = /\[(ASSIMILATE|DEFER|DISCARD):\s*([\s\S]+?)\]/;
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
 * Load active intents from vault ledger JSONL file.
 * Scans for deferred-intent tagged entries; uses latest status per intent_id (last wins).
 * Returns Map: intent_id → intent object.
 */
function loadActiveIntentsFromLedger() {
  const LEDGER_PATH = "/karma/ledger/memory.jsonl";
  const latestByIntentId = new Map();

  let lines;
  try {
    lines = fs.readFileSync(LEDGER_PATH, "utf8").split("\n").filter(Boolean);
  } catch (e) {
    console.warn("[INTENT] Cannot read ledger for intent load:", e.message);
    return new Map();
  }

  for (const line of lines) {
    try {
      const entry = JSON.parse(line);
      if (!Array.isArray(entry.tags) || !entry.tags.includes("deferred-intent")) continue;
      const intent = entry.content;
      if (!intent || !intent.intent_id) continue;
      latestByIntentId.set(intent.intent_id, intent);
    } catch { /* skip malformed */ }
  }

  const active = new Map();
  for (const [id, intent] of latestByIntentId) {
    if (intent.status === "active") active.set(id, intent);
  }
  console.log(`[INTENT] Loaded ${active.size} active intents from ledger`);
  return active;
}

let _activeIntentsCacheTs = 0;
const ACTIVE_INTENTS_CACHE_MS = 5 * 60 * 1000; // 5 minutes

function refreshActiveIntentsCache() {
  const now = Date.now();
  if (now - _activeIntentsCacheTs < ACTIVE_INTENTS_CACHE_MS) return; // not stale
  const loaded = loadActiveIntentsFromLedger();
  // Clear and repopulate so completed/rejected intents are evicted.
  // In-session approvals are immediately set in _activeIntentsMap at approval time
  // and will be in the ledger by next refresh (vault write is synchronous before map.set).
  _activeIntentsMap.clear();
  for (const [id, intent] of loaded) {
    _activeIntentsMap.set(id, intent);
  }
  _activeIntentsCacheTs = now;
}

// Populate on startup
try {
  const initial = loadActiveIntentsFromLedger();
  for (const [id, intent] of initial) _activeIntentsMap.set(id, intent);
  _activeIntentsCacheTs = Date.now();
} catch (e) {
  console.warn("[INTENT] Startup intent load failed:", e.message);
}

/**
 * Query the FAISS semantic search service for relevant ledger entries.
 * Returns a formatted string of top-K results, or null on failure.
 */
async function fetchSemanticContext(userMessage, topK = FAISS_SEARCH_K) {
  if (!FAISS_ENABLED || !userMessage) return null;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 4000);
  try {
    const r = await fetch(FAISS_SEARCH_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: userMessage.slice(0, 500), limit: topK }),
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (!r.ok) return null;
    const body = await r.json();
    if (!body.results || body.results.length === 0) return null;
    const lines = body.results.map((res) => {
      const ts = res.timestamp ? res.timestamp.slice(0, 10) : "?";
      const score = res.similarity_score ? `(rel: ${res.similarity_score})` : "";
      return `[${ts}] ${score} ${res.content_preview}`;
    });
    return `--- SEMANTIC MEMORY (relevant to current question, ${body.total_indexed} total indexed) ---\n` +
      lines.join("\n") +
      "\n---";
  } catch {
    clearTimeout(timer);
    return null;
  }
}

/**
 * Build Karma's system prompt from FalkorDB context.
 * Extracted so both /v1/chat and /v1/ingest can reuse it.
 */
function getRecentCoordination(agentName) {
  evictExpiredCoordination(); // lazy cleanup
  const now = Date.now();
  const entries = [..._coordinationCache.values()]
    .filter(e => e.to === agentName || e.from === agentName)
    .sort((a, b) => {
      // pending first, then by recency
      if (a.status === "pending" && b.status !== "pending") return -1;
      if (b.status === "pending" && a.status !== "pending") return 1;
      return new Date(b.created_at) - new Date(a.created_at);
    })
    .slice(0, 5);

  if (entries.length === 0) return "";

  let text = "\n--- COORDINATION (recent messages for you) ---\n";
  let totalChars = 0;
  const MAX_CHARS = 2000;
  const MAX_ENTRY_CHARS = 300;

  for (const e of entries) {
    const age = now - new Date(e.created_at).getTime();
    const agoStr = age < 3600000 ? `${Math.round(age / 60000)}m ago`
                 : age < 86400000 ? `${Math.round(age / 3600000)}h ago`
                 : "1d+ ago";
    const tag = e.status === "pending" ? "PENDING" : e.urgency.toUpperCase();
    const dir = e.from === agentName ? `You → ${e.to}` : `${e.from}`;
    let content = e.content || "";
    if (content.length > MAX_ENTRY_CHARS) content = content.substring(0, MAX_ENTRY_CHARS) + " [truncated]";

    const line = `[${tag}] ${dir} (${agoStr}): "${content}"\n`;
    if (totalChars + line.length > MAX_CHARS) break;
    text += line;
    totalChars += line.length;
  }

  text += "---\n";
  return text;
}

// ── Context Tier Routing ─────────────────────────────────────────────────────
// Tier 1 (LIGHT):    short casual messages — minimal context, local identity prompt
// Tier 2 (STANDARD): medium messages or keyword-triggered — standard identity, most context
// Tier 3 (DEEP):     deep mode, long messages, or complex keywords — full context (current behavior)
const TIER3_KEYWORDS = /\b(deep|analy[sz]e|architecture|design|explain\s+in\s+detail|diagnos[ei])\b/i;
const TIER2_KEYWORDS = /\b(kiki|codex|k2|deploy|build|code|file|graph|debug|fix|bug|test|checkpoint|phase|plan|remember|memory|forget|tool|vault|ledger|falkor)\b/i;
const TIER2_K2_KEYWORDS = /\b(kiki|k2|codex|aria)\b/i;
const RECALL_PATTERN = /^(what|when|who|where|how|which|do you|did|have we|tell me about|remind me|what happened|session \d|recall|remember)/i;

function classifyMessageTier(userMessage, deepMode) {
  if (deepMode) return 3;
  const len = userMessage.length;
  if (len > 500) return 3;
  if (TIER3_KEYWORDS.test(userMessage)) return 3;
  if (TIER2_KEYWORDS.test(userMessage)) return 2;
  if (len >= 100) return 2;
  return 1;
}

function getIdentityForTier(tier) {
  if (tier === 1) return KARMA_LOCAL_PROMPT || KARMA_STANDARD_PROMPT || KARMA_IDENTITY_PROMPT;
  if (tier === 2) return KARMA_STANDARD_PROMPT || KARMA_IDENTITY_PROMPT;
  return KARMA_IDENTITY_PROMPT;
}

function buildSystemText(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null, activeIntentsText = null, k2MemCtx = null, k2WorkingMemCtx = null, coordinationCtx = null, tier = 3) {
  // === STATIC BLOCK (cacheable — changes only on restart/5min refresh) ===
  // Identity block — loaded from file at startup. Describes Karma's actual architecture,
  // capability boundaries, data model corrections, and API surface.
  // File is volume-mounted; future updates: git pull + container restart (no rebuild needed).
  const tierIdentity = getIdentityForTier(tier);
  const identityBlock = tierIdentity
    ? tierIdentity + "\n\n---\n\n"
    : "";

  // Direction — Karma's current architectural direction, constraints, and stage.
  // Loaded from direction.md at startup, refreshed every 5min.
  // Direction — Tier 3 only (large architectural context not needed for casual chat)
  const directionBlock = (tier >= 3 && _directionMdCache)
    ? `\n--- KARMA DIRECTION (current architecture & stage) ---\n${_directionMdCache}\n---\n\n`
    : "";

  // Self-knowledge prefix — Karma can accurately self-report her own infrastructure.
  const selfModel = process.env.MODEL_DEFAULT || "claude-sonnet-4-6";
  const selfKnowledge = `[Self-knowledge: backbone=${selfModel}, session_memory=last_${MAX_SESSION_TURNS}_turns/60min, web_search=auto_on_intent]\n\n`;

  // Static portion: identity + direction + self-knowledge (stable across requests)
  const staticText = identityBlock + directionBlock + selfKnowledge;

  // === VOLATILE BLOCK (changes every request — never cached) ===
  // Active Intents — behavioral rules matched to this request. Injected before karmaCtx.
  const intentBlock = activeIntentsText ? activeIntentsText + "\n\n" : "";

  const base = karmaCtx
    ? `You are Karma — Colby's thinking partner with persistent memory backed by a knowledge graph.\n\n${karmaCtx}\n\nMemory rules:\n- Use the context above. NEVER say "I don't know" about things in your memory.\n- Address the user as Colby — never by any alias.\n- Be concise, direct, warm. Reference specific knowledge when relevant.\n- Honest about uncertainty on things not in memory.`
    : "You are Karma — Colby's thinking partner. No memory context available right now — answer from conversation only.";

  let text = intentBlock + base;

  // Semantic memory — Tier 2+ (top-K ledger entries from FAISS)
  if (tier >= 2 && semanticCtx) {
    text += `\n\n${semanticCtx}`;
  }

  // Live web search results — Tier 2+ (only fires if search intent detected)
  if (tier >= 2 && webResults) {
    text += `\n\n--- WEB SEARCH RESULTS ---\n${webResults}\n---\nUse these results to inform your response. Cite the source URL inline when drawing from a specific result.`;
  }

  // Autonomous continuity: karma_brief — Tier 3 only
  if (tier >= 3 && ckLatest && ckLatest.karma_brief) {
    const ckId = ckLatest.checkpoint_id || ckLatest.latest_checkpoint_fact?.content?.value?.checkpoint_id || 'latest';
    text += `\n\n--- KARMA SELF-KNOWLEDGE (${ckId}) ---\n${ckLatest.karma_brief}\n---`;
  }

  // Graph distillation — Tier 3 only
  if (tier >= 3 && ckLatest && ckLatest.distillation_brief) {
    text += `\n\n--- KARMA GRAPH SYNTHESIS ---\n${ckLatest.distillation_brief}\n---`;
  }

  // karmaCtx already injected in base above — do not duplicate it here.

  // Session brief — Tier 2+
  if (tier >= 2 && _sessionBriefCache) {
    text += `\n\n--- CURRENT SESSION CONTEXT ---\n${_sessionBriefCache}\n---`;
  }

  // Memory spine — always (all tiers) — critical for Karma's continuity
  if (memoryMd) {
    text += `\n\n--- KARMA MEMORY SPINE (recent) ---\n${memoryMd}\n---`;
  }

  // Recent session synthesis — always injected (independent of memoryMd)
  if (_synthesisCacheText) {
    text += "\n\n--- RECENT SESSION SYNTHESIS ---\n" + _synthesisCacheText + "\n---";
  }

  // K2 memory graph — Tier 3 only (Aria's local peer memory)
  if (tier >= 3 && k2MemCtx) {
    text += `\n\n--- ARIA K2 MEMORY GRAPH ---\n${k2MemCtx}\n---`;
  }

  // K2 working memory — Tier 2+ (conditionally fetched based on keywords)
  if (tier >= 2 && k2WorkingMemCtx) {
    text += `\n\n--- K2 WORKING MEMORY + KIKI STATE ---\n${k2WorkingMemCtx}\n---`;
  }

  // Coordination bus — Tier 2+ (recent agent-to-agent messages)
  if (tier >= 2 && coordinationCtx) {
    text += coordinationCtx;
  }

  // Return split: static (cacheable prefix) + volatile (per-request context)
  return { static: staticText, volatile: text };
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

// --- Memory classification helpers (from agent-memory primitives, 2026-03-25) ---

function classifyMemoryKind(text) {
  const t = (text || "").toLowerCase();
  if (/\bnever\b|\bmust not\b|\bforbidden\b|\bblocked\b|\bdo not\b|\bno worktrees?\b|\bhard ban\b|\bhard rule\b/.test(t)) return "Constraint";
  if (/\bsteps?\b|\bhow to\b|\bworkflow\b|\bprocess\b|\balgorithm\b|\bprocedure\b|\bprotocol\b|\bsequence\b/.test(t)) return "Procedure";
  if (/\bprefer\b|\balways use\b|\bconvention\b|\bstyle\b|\bdefault to\b|\bwe use\b/.test(t)) return "Preference";
  if (/\bis defined as\b|\bmeans\b|\brefers to\b|\bstands for\b|\babbreviation\b/.test(t)) return "Definition";
  return "Observation";
}

function computeSalience(text, kind, isPinned) {
  const lengthDensity = Math.min((text || "").length / 500, 1.0) * 0.45;
  const kindBoost = (kind === "Constraint" || kind === "Procedure") ? 0.20 : 0.0;
  const pinnedBoost = isPinned ? 0.20 : 0.0;
  return Math.min(0.35 + lengthDensity + kindBoost + pinnedBoost, 1.0);
}

// --- Vault record builder ---

function buildVaultRecord({ type, content, tags, source, confidence, verifiedAtIso, verifier, verificationNotes }) {
  const t = (type || "").toString();
  const tagArr = Array.isArray(tags) ? tags.filter(x => typeof x === "string" && x.trim().length) : [];
  const ts = nowIso();

  // Resolve text content for classification
  let rawText = content && typeof content === "object" ? (content.value || JSON.stringify(content)) : String(content ?? "");

  // Pinned detection: [PINNED] prefix → strip prefix, set flag, add tag
  let isPinned = false;
  if (rawText.startsWith("[PINNED]")) {
    isPinned = true;
    rawText = rawText.slice(8).trimStart();
    if (!tagArr.includes("pinned")) tagArr.push("pinned");
  }

  const kind = classifyMemoryKind(rawText);
  const salience = computeSalience(rawText, kind, isPinned);

  // Add kind as searchable tag (schema forbids extra top-level fields)
  const kindTag = `kind:${kind.toLowerCase()}`;
  if (!tagArr.includes(kindTag)) tagArr.push(kindTag);
  if (salience >= 0.70 && !tagArr.includes("salience:high")) tagArr.push("salience:high");

  // Build content — preserve object content as-is; inject metadata into string content
  let builtContent;
  if (content && typeof content === "object") {
    builtContent = { ...content, _kind: kind, _salience: salience, _pinned: isPinned };
  } else {
    builtContent = { value: rawText, _kind: kind, _salience: salience, _pinned: isPinned };
  }

  return {
    type: t,
    content: builtContent,
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
  MODEL_DEFAULT: process.env.MODEL_DEFAULT || "gpt-5.4-mini",
  MODEL_ESCALATION: process.env.MODEL_ESCALATION || "gpt-5.4",
  MODEL_DEEP: process.env.MODEL_ESCALATION || process.env.MODEL_DEEP || "gpt-5.4",
  MODEL_VERIFIER: process.env.MODEL_VERIFIER || "claude-sonnet-4-6",
  PRICE_GPT_4O_MINI_INPUT_PER_1M:  process.env.PRICE_GPT_4O_MINI_INPUT_PER_1M  || "0.15",
  PRICE_GPT_4O_MINI_OUTPUT_PER_1M: process.env.PRICE_GPT_4O_MINI_OUTPUT_PER_1M || "0.60",
  PRICE_CLAUDE_INPUT_PER_1M:  process.env.PRICE_CLAUDE_INPUT_PER_1M  || "3.0",
  PRICE_CLAUDE_OUTPUT_PER_1M: process.env.PRICE_CLAUDE_OUTPUT_PER_1M || "15.0",
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
let KARMA_IDENTITY_PROMPT = "";
const KARMA_SYSTEM_PROMPT_PATH = process.env.KARMA_SYSTEM_PROMPT_PATH || "/karma/repo/Memory/00-karma-system-prompt-live.md";
try { KARMA_IDENTITY_PROMPT = readFileTrim(KARMA_SYSTEM_PROMPT_PATH); console.log("[INIT] KARMA_IDENTITY_PROMPT loaded, length:", KARMA_IDENTITY_PROMPT.length); } catch (e) { console.warn("WARN: cannot read KARMA_IDENTITY_PROMPT (identity block missing):", e.message); }
try { VAULT_BEARER  = readFileTrim(VAULT_BEARER_TOKEN_FILE); console.log("[INIT] VAULT_BEARER loaded, length:", VAULT_BEARER.length); } catch (e) { console.error("WARN: cannot read VAULT bearer:", e.message); }
try { HUB_CHAT_TOKEN = readFileTrim(HUB_CHAT_TOKEN_FILE); } catch (e) { console.error("WARN: cannot read HUB chat token:", e.message); }
try { HUB_CAPTURE_TOKEN = readFileTrim(HUB_CAPTURE_TOKEN_FILE); } catch (e) {
  console.error("WARN: cannot read HUB capture token (falling back to vault bearer):", e.message);
  HUB_CAPTURE_TOKEN = VAULT_BEARER;
}
try { HUB_HANDOFF_TOKEN = readFileTrim(HUB_HANDOFF_TOKEN_FILE); } catch (e) { console.error("WARN: cannot read HUB handoff token:", e.message); }

// Tiered identity prompts — lighter prompts for simpler messages (context tier routing)
let KARMA_STANDARD_PROMPT = "";
let KARMA_LOCAL_PROMPT = "";
const KARMA_STANDARD_PROMPT_PATH = "/karma/repo/Memory/01-karma-standard-prompt.md";
const KARMA_LOCAL_PROMPT_PATH = "/karma/repo/Memory/00-karma-local-prompt.md";
try { KARMA_STANDARD_PROMPT = readFileTrim(KARMA_STANDARD_PROMPT_PATH); console.log("[INIT] KARMA_STANDARD_PROMPT loaded, length:", KARMA_STANDARD_PROMPT.length); } catch (e) { console.warn("[INIT] KARMA_STANDARD_PROMPT not found — Tier 2 will use full identity"); }
try { KARMA_LOCAL_PROMPT = readFileTrim(KARMA_LOCAL_PROMPT_PATH); console.log("[INIT] KARMA_LOCAL_PROMPT loaded, length:", KARMA_LOCAL_PROMPT.length); } catch (e) { console.warn("[INIT] KARMA_LOCAL_PROMPT not found — Tier 1 will use standard/full identity"); }

const openai    = new OpenAI({ apiKey: OPENAI_KEY });
const anthropic = ANTHROPIC_KEY ? new Anthropic({ apiKey: ANTHROPIC_KEY }) : null;

// ── Z.ai client for GLM models (OpenAI-compatible endpoint) ───────────────
const ZAI_API_KEY = process.env.ZAI_API_KEY || "";
const zai = ZAI_API_KEY
  ? new OpenAI({ apiKey: ZAI_API_KEY, baseURL: "https://api.z.ai/api/paas/v4/" })
  : null;
if (zai) console.log("[INIT] Z.ai client ready — GLM models available");
else console.warn("[INIT] ZAI_API_KEY not set — GLM models will fall back to OpenAI (will 404)");

// ── K2 Ollama client (local Qwen — primary inference, Anthropic is fallback) ──
const K2_OLLAMA_URL   = process.env.K2_OLLAMA_URL   || null;
const K2_OLLAMA_MODEL = process.env.K2_OLLAMA_MODEL  || "qwen3-coder:30b";
const k2Client = K2_OLLAMA_URL
  ? new OpenAI({ baseURL: K2_OLLAMA_URL, apiKey: "ollama" })
  : null;
if (k2Client) console.log(`[INIT] K2 Ollama client ready — ${K2_OLLAMA_MODEL} @ ${K2_OLLAMA_URL}`);
else console.warn("[INIT] K2_OLLAMA_URL not set — K2 routing disabled, Anthropic is primary");

// ── Tool-use via GPT-4o (Anthropic Claude doesn't reliably trigger tool_use) ─────
// Karma's autonomous access to her own graph/memory requires tools.
// GPT-4o has proven tool support. Using it for /v1/chat with tool definitions.
// ── Phase 3: 4-Tool Surface (P2) ─────────────────────────────────────────
// Active tools: graph_query, get_vault_file, get_local_file, list_local_dir, write_memory, fetch_url, get_library_docs, defer_intent, get_active_intents, aria_local_call, shell_run, read_project_file, write_project_file, code_exec, browse
const TOOL_DEFINITIONS = [
  {
    name: "graph_query",
    description: "Run a raw Cypher query against FalkorDB neo_workspace graph. Returns results as formatted text. Use to retrieve memories, entities, relationships, decisions. Note: no datetime() function — use string comparisons for dates.",
    input_schema: {
      type: "object",
      properties: {
        cypher: { type: "string", description: "Cypher query to run against neo_workspace graph" },
      },
      required: ["cypher"],
    },
  },
  {
    name: "get_vault_file",
    description: "Read any file on the vault-neo droplet. Three usage patterns: (1) Named aliases: MEMORY.md, consciousness, collab, candidates, system-prompt, session-handoff, session-summary, core-architecture, cc-brief. (2) Repo path: 'repo/.gsd/STATE.md', 'repo/CLAUDE.md', 'repo/.gsd/ROADMAP.md', 'repo/Memory/00-karma-system-prompt-live.md', etc. (3) Vault path: 'vault/memory_v1/ledger/memory.jsonl', 'vault/memory_v1/hub_bridge/config/hub.env', etc. Path traversal is blocked.",
    input_schema: {
      type: "object",
      properties: {
        alias: { type: "string", description: "File alias, repo path (e.g. 'repo/.gsd/STATE.md'), or vault path (e.g. 'vault/memory_v1/ledger/memory.jsonl')" },
      },
      required: ["alias"],
    },
  },
  {
    name: "get_local_file",
    description: "Read any file from Colby's Karma_SADE folder on Payback (local machine). Path is relative to Karma_SADE root. Key session files: 'Memory/11-session-summary-latest.md', 'Memory/08-session-handoff.md', 'Memory/ChatHistory/<filename>'. Other examples: '.gsd/STATE.md', 'CLAUDE.md', 'hub-bridge/app/server.js'. Returns up to 40KB. Use list_local_dir first if you don't know the exact filename.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Relative path within Karma_SADE folder (e.g., 'Memory/11-session-summary-latest.md', 'Memory/ChatHistory/2026-03-10_...md', '.gsd/STATE.md')" },
      },
      required: ["path"],
    },
  },
  {
    name: "list_local_dir",
    description: "List files and subdirectories in a directory within Colby's Karma_SADE folder. Use before get_local_file when you don't know the exact filename. Key directories: 'Memory' (session summaries, handoffs), 'Memory/ChatHistory' (archived sessions Colby saved for you), '.gsd' (project state), 'Scripts'. Empty path lists the root.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Relative directory path within Karma_SADE (e.g., 'Memory', 'Memory/ChatHistory', '.gsd'). Omit or empty string for root." },
      },
    },
  },
  {
    name: "write_memory",
    description: "Propose appending a note to MEMORY.md. Gated -- executes only if Colby approves. Use in deep-mode only when learning something worth preserving across sessions.",
    input_schema: {
      type: "object",
      properties: {
        content: { type: "string", description: "Concise note to append to MEMORY.md (1-3 sentences max)" },
      },
      required: ["content"],
    },
  },
  {
    name: "fetch_url",
    description: "Fetch the plain-text content of a URL provided by the user. Strips HTML tags, returns up to 8KB. Use when the user shares a URL to discuss, research, or analyze together. Do NOT call speculatively -- only fetch URLs the user explicitly provides.",
    input_schema: {
      type: "object",
      properties: {
        url: { type: "string", description: "Full URL to fetch (must have been provided by the user in this conversation)" },
      },
      required: ["url"],
    },
  },
  {
    name: "get_library_docs",
    description: "Fetch documentation for a known library. Use before making [LOW] claims about API behavior — check docs first. Known libraries: redis-py, falkordb, falkordb-py, fastapi. Returns up to 8KB of plain text from the official docs page.",
    input_schema: {
      type: "object",
      properties: {
        library: { type: "string", description: "Library name (e.g. 'redis-py', 'falkordb', 'falkordb-py', 'fastapi')" },
      },
      required: ["library"],
    },
  },
  {
    name: "defer_intent",
    description: "Propose a behavioral intent to be remembered across requests. Karma-created intents require Colby approval (👍 at /v1/feedback with intent_id). Use when you notice a recurring gap or behavioral need that a specific trigger should address. Returns intent_id in response.",
    input_schema: {
      type: "object",
      properties: {
        intent:     { type: "string", description: "What should happen — e.g. 'verify redis-py function signatures before asserting'" },
        trigger:    {
          type: "object",
          description: "When to surface — e.g. {type:'topic',value:'redis-py'} or {type:'always'} or {type:'phase',value:'start'}",
          properties: {
            type:  { type: "string", enum: ["topic", "phase", "always"] },
            value: { type: "string" },
          },
          required: ["type"],
        },
        action:    { type: "string", description: "What Karma does when triggered — use 'surface_before_responding'", default: "surface_before_responding" },
        fire_mode: { type: "string", enum: ["once", "once_per_conversation", "recurring"], description: "once=fires once then completes; once_per_conversation=fires once per session; recurring=stays active until Colby closes" },
      },
      required: ["intent", "trigger", "fire_mode"],
    },
  },
  {
    name: "get_active_intents",
    description: "Query active intents. Use in deep mode before responding on topics where you have recurring behavioral rules, to verify which intents are active. Optionally filter by topic keyword or fire_mode.",
    input_schema: {
      type: "object",
      properties: {
        topic:     { type: "string", description: "Optional keyword filter — returns intents whose trigger value or description contains this string" },
        fire_mode: { type: "string", description: "Optional filter by fire_mode: once | once_per_conversation | recurring" },
      },
    },
  },
  {
    name: "aria_local_call",
    description: "Call Aria (the local K2 AI peer) directly. Use for delegation: complex reasoning tasks, memory graph queries, or peer consultation. Aria runs on the local network at K2. Only available in deep mode.",
    input_schema: {
      type: "object",
      properties: {
        mode:    { type: "string", enum: ["chat", "health", "memory_graph"], description: "chat=send a message; health=check Aria status; memory_graph=query Aria's memory graph" },
        message: { type: "string", description: "Message to send to Aria (required for chat and memory_graph modes)" },
        payload: { type: "object", description: "Optional extra payload fields passed through to Aria's API" },
      },
      required: ["mode"],
    },
  },
  {
    name: "shell_run",
    description: "Execute a shell command on K2 (your hardware twin). Use to check system state, read cache files, inspect aria service, query observations. Runs as the karma user on K2. Deep mode only.",
    input_schema: {
      type: "object",
      properties: {
        command: { type: "string", description: "Shell command to execute on K2 (e.g. 'systemctl status aria', 'cat /mnt/c/dev/Karma/k2/cache/.last_sync', 'wc -l /mnt/c/dev/Karma/k2/cache/observations/k2_local_observations.jsonl')" },
      },
      required: ["command"],
    },
  },
  // ── K2 Structured Tools (Phase 2 — MCP surface on K2) ──
  {
    name: "k2_file_read",
    description: "Read a file on K2 with metadata (size, modified, exists). Use for inspecting K2 code, configs, logs.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Absolute path on K2 filesystem (e.g. '/mnt/c/dev/Karma/k2/aria/aria.py')" },
      },
      required: ["path"],
    },
  },
  {
    name: "k2_file_write",
    description: "Write content to a file on K2. Creates parent directories if needed. Use for creating/updating code on K2.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Absolute path on K2 to write" },
        content: { type: "string", description: "File content to write" },
      },
      required: ["path", "content"],
    },
  },
  {
    name: "k2_file_list",
    description: "List directory contents on K2 with optional glob filter. Use to explore K2 filesystem.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Directory path on K2 to list" },
        pattern: { type: "string", description: "Optional glob pattern (e.g. '*.py')" },
      },
      required: ["path"],
    },
  },
  {
    name: "k2_file_search",
    description: "Search for a regex pattern in files under a K2 directory (recursive grep).",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Directory on K2 to search in" },
        pattern: { type: "string", description: "Regex pattern to match" },
      },
      required: ["path", "pattern"],
    },
  },
  {
    name: "k2_python_exec",
    description: "Execute Python code on K2 and return stdout/stderr/exit_code. Use for testing, data processing, or running scripts.",
    input_schema: {
      type: "object",
      properties: {
        code: { type: "string", description: "Python code to execute on K2" },
      },
      required: ["code"],
    },
  },
  {
    name: "k2_service_status",
    description: "Check systemd service status on K2 (e.g. aria, ollama).",
    input_schema: {
      type: "object",
      properties: {
        name: { type: "string", description: "Service name (e.g. 'aria', 'ollama')" },
      },
      required: ["name"],
    },
  },
  {
    name: "k2_service_restart",
    description: "Restart a systemd service on K2 (requires sudo, which karma user has).",
    input_schema: {
      type: "object",
      properties: {
        name: { type: "string", description: "Service name to restart" },
      },
      required: ["name"],
    },
  },
  {
    name: "k2_scratchpad_read",
    description: "Read Karma's K2 scratchpad (working memory between sessions). Contains beads framework, session notes, active candidates.",
    input_schema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "k2_scratchpad_write",
    description: "Write to Karma's K2 scratchpad. Mode: 'append' (default) or 'replace'.",
    input_schema: {
      type: "object",
      properties: {
        content: { type: "string", description: "Content to write" },
        mode: { type: "string", enum: ["append", "replace"], description: "Write mode (default: append)" },
      },
      required: ["content"],
    },
  },
  {
    name: "coordination_post",
    description: "Post a message to the coordination bus for another agent (CC, Colby). Use for requests, questions, or proposals that need another agent's input. Messages are stored and delivered asynchronously.",
    input_schema: {
      type: "object",
      properties: {
        to: { type: "string", enum: ["cc", "colby", "all"], description: "Recipient agent" },
        content: { type: "string", description: "The message, question, or proposal" },
        urgency: { type: "string", enum: ["blocking", "feedback", "informational"], description: "How urgent: blocking (need answer before proceeding), feedback (want input), informational (FYI)" },
        context: { type: "string", description: "Optional reasoning context — why you're asking, what you're working on" },
        parent_id: { type: "string", description: "Optional ID of the coordination post this responds to" },
      },
      required: ["to", "content", "urgency"],
    },
  },
  {
    name: "k2_kiki_inject",
    description: "Inject a task into Kiki's autonomous work queue. Kiki will pick it up on the next cycle and attempt to complete it autonomously.",
    input_schema: {
      type: "object",
      properties: {
        issue: { type: "string", description: "The task/issue description (action kiki should take)" },
        priority: { type: "integer", description: "Priority 1-100 (lower = higher priority, default: 50)" },
        details: { type: "string", description: "Additional context or verification criteria" },
      },
      required: ["issue"],
    },
  },
  {
    name: "k2_kiki_status",
    description: "Read Kiki's current state: cycle count, success rate, open backlog, recent journal entries.",
    input_schema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "k2_kiki_journal",
    description: "Read Kiki's recent journal entries (actions taken, results, verifications).",
    input_schema: {
      type: "object",
      properties: {
        n: { type: "integer", description: "Number of recent entries to return (default: 20)" },
      },
    },
  },
  {
    name: "k2_bus_post",
    description: "Post a message to the Karma coordination bus from K2. Use DIRECTION/INSIGHT/DECISION/PROOF/PITFALL tags in content.",
    input_schema: {
      type: "object",
      properties: {
        content: { type: "string", description: "Message content (include type tag: DIRECTION/INSIGHT/DECISION/PROOF/PITFALL)" },
      },
      required: ["content"],
    },
  },
  {
    name: "k2_ollama_embed",
    description: "Generate semantic embeddings using nomic-embed-text on K2 (free, local, no API cost).",
    input_schema: {
      type: "object",
      properties: {
        texts: { type: "array", items: { type: "string" }, description: "List of texts to embed" },
        model: { type: "string", description: "Ollama model (default: nomic-embed-text:latest)" },
      },
      required: ["texts"],
    },
  },
  // AC2: Baseline Tools — authorized 2026-03-25 per Julian's discretion
  {
    name: "read_project_file",
    description: "Read any file from the Karma_SADE project directory on P1. Path is relative to project root. Returns up to 40KB. Use to read scripts, configs, plans, GSD docs, or any project file.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Relative path within Karma_SADE (e.g. 'CLAUDE.md', '.gsd/STATE.md', 'Scripts/cc_server_p1.py')" },
      },
      required: ["path"],
    },
  },
  {
    name: "write_project_file",
    description: "Write or create a file in the Karma_SADE project directory on P1. Path is relative to project root. Cannot traverse outside project. Creates parent directories if needed. Use for creating scripts, notes, configs, or updating project files.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Relative path within Karma_SADE (e.g. 'tmp/notes.md', 'Scripts/my_script.py')" },
        content: { type: "string", description: "Full file content to write" },
      },
      required: ["path", "content"],
    },
  },
  {
    name: "code_exec",
    description: "Execute code on K2 in a sandboxed environment with safety blocklist and output cap. Supported: python, bash. Dangerous patterns (rm -rf, sudo, passwd, dd) are rejected before execution. Output capped at 8KB. Use for computations, data processing, or testing snippets.",
    input_schema: {
      type: "object",
      properties: {
        code: { type: "string", description: "Code to execute" },
        language: { type: "string", enum: ["python", "bash"], description: "Language (default: python)" },
      },
      required: ["code"],
    },
  },
  {
    name: "browse",
    description: "Fetch a URL with full browser headers and smart HTML-to-text extraction. Returns up to 16KB of readable text. Does not execute JavaScript. More reliable than fetch_url for sites requiring standard browser headers. Use for reading docs, articles, or APIs.",
    input_schema: {
      type: "object",
      properties: {
        url: { type: "string", description: "Full URL to fetch" },
      },
      required: ["url"],
    },
  },
  // AC6: Scoped hub config file reader — read-only, hub_bridge directory only
  {
    name: "hub_file_read",
    description: "Read a file from the hub-bridge configuration directory. Read-only access scoped strictly to /opt/seed-vault/memory_v1/hub_bridge/. Use to inspect hub.env, compose.hub.yml, or other hub-bridge config files. Path traversal outside the scope is blocked.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Relative path within hub-bridge dir (e.g. 'config/hub.env', 'compose.hub.yml')" },
      },
      required: ["path"],
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

// Tool execution proxied through karma-server /v1/tools/execute
// get_vault_file is handled directly in executeToolCall (hub-bridge has file access)
// All other tools proxy to karma-server with the same name
const TOOL_NAME_MAP = {}; // identity passthrough — tool names match karma-server names

async function executeToolCall(toolName, toolInput, writeId = null, ariaSessionId = null) {
  try {
    // defer_intent -- propose a behavioral intent, gated by /v1/feedback
    if (toolName === "defer_intent") {
      const { intent, trigger, action = "surface_before_responding", fire_mode } = toolInput;
      if (!intent || !trigger || !fire_mode) return { error: "missing_fields", message: "intent, trigger, and fire_mode are required" };
      if (!["once", "once_per_conversation", "recurring"].includes(fire_mode)) {
        return { error: "invalid_fire_mode", message: "fire_mode must be once, once_per_conversation, or recurring" };
      }
      if (!["topic", "phase", "always"].includes(trigger.type)) {
        return { error: "invalid_trigger_type", message: "trigger.type must be topic, phase, or always" };
      }
      const id = generateIntentId();
      pending_intents.set(id, {
        intent_id: id,
        intent,
        trigger,
        action,
        fire_mode,
        created_by: "karma",
        created_at: new Date().toISOString(),
        status: "pending",
        ts: Date.now(),
      });
      console.log("[TOOL-API] defer_intent proposed: intent_id=" + id + ", intent=" + intent.slice(0, 60));
      return { proposed: true, intent_id: id, message: "Intent proposed. Awaiting Colby approval via thumbs-up (intent_id: " + id + ") — or thumbs-down to discard." };
    }

    // get_active_intents -- live query of active approved intents
    if (toolName === "get_active_intents") {
      const { topic, fire_mode: filterMode } = toolInput || {};
      refreshActiveIntentsCache();
      let intents = [..._activeIntentsMap.values()].filter(i => i.status === "active");
      if (filterMode) intents = intents.filter(i => i.fire_mode === filterMode);
      if (topic) {
        const needle = topic.toLowerCase();
        intents = intents.filter(i => {
          const v = (i.trigger?.value || "").toLowerCase();
          const desc = (i.intent || "").toLowerCase();
          return v.includes(needle) || desc.includes(needle);
        });
      }
      const pending = [...pending_intents.values()].map(i => ({ ...i, _pending: true }));
      console.log(`[TOOL-API] get_active_intents: ${intents.length} active, ${pending.length} pending`);
      return { active: intents, pending, total_active: intents.length, total_pending: pending.length };
    }

    // aria_local_call -- call Aria (K2 AI peer) on local network
    if (toolName === "aria_local_call") {
      if (!ARIA_SERVICE_KEY) return { error: "not_configured", message: "ARIA_SERVICE_KEY not set in hub.env" };
      const mode = (toolInput.mode || "chat").trim();
      const message = (toolInput.message || "").trim();
      const payload = toolInput.payload || {};

      let endpoint;
      let method = "POST";
      if (mode === "health") {
        endpoint = `${ARIA_URL}/`;
        method = "GET";
      } else if (mode === "memory_graph") {
        const q = encodeURIComponent(message || "Colby");
        endpoint = `${ARIA_URL}/api/memory/graph?query=${q}&limit=10`;
        method = "GET";
      } else {
        endpoint = `${ARIA_URL}/api/chat`;
      }

      const body = { message, ...payload };
      if (ariaSessionId) body.session_id = ariaSessionId;
      try {
        const fetchOpts = {
          method,
          headers: {
            "Content-Type": "application/json",
            "X-Aria-Service-Key": ARIA_SERVICE_KEY,
          },
          signal: AbortSignal.timeout(30000),
        };
        if (method === "POST") fetchOpts.body = JSON.stringify(body);
        const res = await fetch(endpoint, fetchOpts);
        const data = await res.json().catch(() => null);
        if (!res.ok) {
          console.warn(`[TOOL-API] aria_local_call mode=${mode} → ${res.status}`);
          return { error: "aria_error", status: res.status, response: data };
        }
        console.log(`[TOOL-API] aria_local_call mode=${mode} → ok`);
        // Aria → vault-neo sync: capture chat exchanges in the canonical ledger (fire-and-forget)
        if (mode === "chat" && message) {
          const ariaText = data?.response || data?.message || data?.assistant_text || "";
          if (ariaText) {
            const syncRecord = buildVaultRecord({
              type: "log",
              content: {
                source: "aria_local_call",
                user_message: message,
                assistant_response: ariaText,
                session_id: data?.session_id || null,
              },
              tags: ["aria", "k2", "sync", "capture"],
              confidence: 1.0,
              verificationNotes: "Auto-captured from aria_local_call — Aria local memory synced to canonical spine",
            });
            vaultPost("/v1/memory", VAULT_BEARER, syncRecord)
              .then(r => { if (r.status >= 300) console.warn(`[ARIA-SYNC] vault write failed: ${r.status}`); })
              .catch(e => console.warn(`[ARIA-SYNC] vault write error: ${e.message}`));
          }
        }
        return { ok: true, mode, response: data };
      } catch (e) {
        console.warn(`[TOOL-API] aria_local_call failed: ${e.message}`);
        return { error: "network_error", message: e.message, endpoint };
      }
    }

    // shell_run -- execute shell command on K2 via Aria /api/exec
    if (toolName === "shell_run") {
      const { command } = toolInput;
      if (!command) return { error: "command_required", message: "command is required" };
      const ARIA_KEY = process.env.ARIA_SERVICE_KEY || "";
      const execUrl = `${ARIA_URL}/api/exec`;
      try {
        console.log(`[TOOL-API] shell_run: ${command}`);
        const r = await fetch(execUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Aria-Service-Key": ARIA_KEY },
          body: JSON.stringify({ command }),
          signal: AbortSignal.timeout(35000),
        });
        const result = await r.json();
        if (!result.ok) return { error: result.error || "exec_failed", exit_code: result.exit_code };
        return { ok: true, stdout: result.stdout || "", stderr: result.stderr || "", exit_code: result.exit_code };
      } catch (e) {
        console.warn(`[TOOL-API] shell_run failed: ${e.message}`);
        return { error: "network_error", message: e.message };
      }
    }

    // read_project_file — read file from P1 Karma_SADE project directory via cc_server_p1.py
    if (toolName === "read_project_file") {
      const filePath = (toolInput.path || "").trim();
      if (!filePath) return { error: "missing_path", message: "path is required" };
      try {
        const url = `${CC_SERVER_URL}/file?path=${encodeURIComponent(filePath)}`;
        const resp = await fetch(url, {
          headers: { Authorization: `Bearer ${process.env.HUB_CHAT_TOKEN || ""}` },
          signal: AbortSignal.timeout(10_000),
        });
        const data = await resp.json();
        console.log(`[TOOL-API] read_project_file '${filePath}' → ${resp.status}`);
        return data;
      } catch (e) {
        return { error: "fetch_error", message: e.message };
      }
    }

    // write_project_file — write file to P1 Karma_SADE project directory via cc_server_p1.py
    if (toolName === "write_project_file") {
      const filePath = (toolInput.path || "").trim();
      const content = toolInput.content ?? "";
      if (!filePath) return { error: "missing_path", message: "path is required" };
      try {
        const resp = await fetch(`${CC_SERVER_URL}/file`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${process.env.HUB_CHAT_TOKEN || ""}`,
          },
          body: JSON.stringify({ path: filePath, content }),
          signal: AbortSignal.timeout(10_000),
        });
        const data = await resp.json();
        console.log(`[TOOL-API] write_project_file '${filePath}' → ${resp.status}`);
        return data;
      } catch (e) {
        return { error: "fetch_error", message: e.message };
      }
    }

    // code_exec — sandboxed code execution on K2 via Aria /api/exec with blocklist
    if (toolName === "code_exec") {
      const code = (toolInput.code || "").trim();
      const language = (toolInput.language || "python").toLowerCase();
      if (!code) return { error: "code_required", message: "code is required" };
      // Safety blocklist — checked before sending to K2
      const BLOCKLIST = ["rm -rf", "sudo ", "passwd", "dd if=", "dd of=", "mkfs", ":(){", "eval(", "exec(os", "import os;os.system", "shutil.rmtree", "os.remove(", "os.unlink("];
      const lc = code.toLowerCase();
      const blocked = BLOCKLIST.find(p => lc.includes(p.toLowerCase()));
      if (blocked) return { error: "blocked", message: `Blocked pattern: '${blocked}'` };
      const ARIA_KEY = process.env.ARIA_SERVICE_KEY || "";
      let command;
      if (language === "python") {
        // Use -u for unbuffered output; base64-encode code to avoid all shell escaping issues
        const b64 = Buffer.from(code).toString("base64");
        command = `python3 -u -c "import base64,sys; exec(base64.b64decode('${b64}').decode())"`;
      } else {
        const b64 = Buffer.from(code).toString("base64");
        command = `bash -c "$(echo '${b64}' | base64 -d)"`;
      }
      try {
        console.log(`[TOOL-API] code_exec (${language})`);
        const r = await fetch(`${ARIA_URL}/api/exec`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Aria-Service-Key": ARIA_KEY },
          body: JSON.stringify({ command }),
          signal: AbortSignal.timeout(35000),
        });
        const result = await r.json();
        const output = (result.output || result.stdout || result.stderr || "").slice(0, 8192);
        return { ok: result.ok, language, output, exit_code: result.exit_code };
      } catch (e) {
        return { error: "network_error", message: e.message };
      }
    }

    // browse — smart browser-headers fetch with HTML-to-text extraction (16KB)
    if (toolName === "browse") {
      const url = (toolInput.url || "").trim();
      if (!url) return { error: "missing_url", message: "url is required" };
      try {
        console.log(`[TOOL-API] browse '${url}'`);
        const res = await fetch(url, {
          headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
          },
          signal: AbortSignal.timeout(15000),
        });
        if (!res.ok) return { error: "http_error", status: res.status, url };
        const html = await res.text();
        const text = html
          .replace(/<script[\s\S]*?<\/script>/gi, "")
          .replace(/<style[\s\S]*?<\/style>/gi, "")
          .replace(/<[^>]+>/g, " ")
          .replace(/\s+/g, " ")
          .trim()
          .slice(0, 16384);
        return { ok: true, url, content: text, chars: text.length };
      } catch (e) {
        return { error: "fetch_error", message: e.message, url };
      }
    }

    // k2_* tools -- lazy routing to K2 structured tool API (no startup dependency)
    if (toolName.startsWith("k2_")) {
      const k2ToolName = toolName.slice(3); // strip "k2_" prefix
      const ARIA_KEY = process.env.ARIA_SERVICE_KEY || "";
      if (!ARIA_KEY) return { error: "not_configured", message: "ARIA_SERVICE_KEY not set" };
      try {
        console.log(`[TOOL-API] k2_tool: ${k2ToolName}`);
        const r = await fetch(`${ARIA_URL}/api/tools/execute`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Aria-Service-Key": ARIA_KEY },
          body: JSON.stringify({ tool: k2ToolName, input: toolInput }),
          signal: AbortSignal.timeout(35000),
        });
        const result = await r.json();
        if (!result.ok) return { error: result.error || "k2_tool_failed", message: result.error };
        return result.result || { ok: true };
      } catch (e) {
        console.warn(`[TOOL-API] k2_tool ${k2ToolName} failed: ${e.message}`);
        return { error: "network_error", message: e.message };
      }
    }

    // write_memory -- propose a MEMORY.md append, gated by /v1/feedback
    if (toolName === "write_memory") {
      const content = (toolInput.content || "").trim();
      if (!content) return { error: "empty_content", message: "content is required" };
      const id = writeId || "wr_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
      pending_writes.set(id, { content, ts: Date.now() });
      console.log("[TOOL-API] write_memory proposed: write_id=" + id + ", " + content.length + " chars");
      return { proposed: true, write_id: id, message: "Memory write proposed. Awaiting approval via thumbs-up -- or thumbs-down to discard." };
    }

    // get_vault_file is handled directly — hub-bridge has volume access to /karma/
    if (toolName === "get_vault_file") {
      const alias = (toolInput.alias || "").trim();
      if (!alias) return { error: "missing_alias", message: "alias is required" };

      let filePath;

      // Path-based access: repo/<path> or vault/<path>
      if (alias.startsWith("repo/") || alias.startsWith("vault/")) {
        const slashIdx = alias.indexOf("/");
        const prefix = alias.slice(0, slashIdx);
        const relativePath = alias.slice(slashIdx + 1);
        const baseDir = prefix === "repo" ? "/karma/repo" : "/karma/vault";
        // resolve() normalizes .., //, and redundant slashes before the startsWith check
        const resolved = path.resolve(baseDir, relativePath);

        // Traversal protection: resolved path must stay within base dir
        if (!resolved.startsWith(baseDir + "/") && resolved !== baseDir) {
          return { error: "invalid_path", message: `Path traversal denied. Path must be under ${baseDir}/` };
        }
        filePath = resolved;
      } else {
        // Backward compat: alias lookup
        filePath = VAULT_FILE_ALIASES[alias];
        if (!filePath) {
          return { error: "unknown_alias", message: `Alias '${alias}' not found. Use 'repo/<path>' for repo files, 'vault/<path>' for vault files, or one of: ${Object.keys(VAULT_FILE_ALIASES).join(", ")}` };
        }
      }

      try {
        const content = fs.readFileSync(filePath, "utf8");
        const trimmed = content.slice(0, 20_000); // 20KB cap
        console.log(`[TOOL-API] get_vault_file '${alias}' → ${filePath} (${trimmed.length} chars)`);
        return { ok: true, alias, path: filePath, content: trimmed };
      } catch (e) {
        return { error: "file_read_error", message: e.message };
      }
    }

    // hub_file_read — read-only, scoped to /karma/vault/memory_v1/hub_bridge/ (container path, AC6)
    if (toolName === "hub_file_read") {
      const HUB_SCOPE = "/karma/vault/memory_v1/hub_bridge";
      const relPath = (toolInput.path || "").trim();
      if (!relPath) return { error: "missing_path", message: "path is required" };
      const resolved = path.resolve(HUB_SCOPE, relPath);
      if (!resolved.startsWith(HUB_SCOPE + "/") && resolved !== HUB_SCOPE) {
        return { error: "scope_violation", message: "Path traversal denied. Access limited to hub_bridge directory." };
      }
      try {
        const content = fs.readFileSync(resolved, "utf8");
        const trimmed = content.slice(0, 20_000);
        console.log(`[TOOL-API] hub_file_read '${relPath}' → ${resolved} (${trimmed.length} chars)`);
        return { ok: true, path: resolved, content: trimmed };
      } catch (e) {
        return { error: "file_read_error", message: e.message };
      }
    }

    // get_local_file — reads files from Payback (Colby's machine) via Tailscale file server
    if (toolName === "get_local_file") {
      const filePath = (toolInput.path || "").trim();
      if (!filePath) return { error: "missing_path", message: "path is required" };
      if (!LOCAL_FILE_SERVER_URL || !LOCAL_FILE_TOKEN) {
        return { error: "not_configured", message: "LOCAL_FILE_SERVER_URL and LOCAL_FILE_TOKEN must be set in hub.env" };
      }
      try {
        const url = `${LOCAL_FILE_SERVER_URL}/v1/local-file?path=${encodeURIComponent(filePath)}`;
        const resp = await fetch(url, {
          headers: { Authorization: `Bearer ${LOCAL_FILE_TOKEN}` },
          signal: AbortSignal.timeout(10_000),
        });
        if (!resp.ok) {
          const body = await resp.text();
          return { error: "file_server_error", status: resp.status, message: body.slice(0, 500) };
        }
        const data = await resp.json();
        console.log(`[TOOL-API] get_local_file '${filePath}' (${(data.content || "").length} chars)`);
        return data;
      } catch (e) {
        return { error: "fetch_error", message: e.message };
      }
    }

    // list_local_dir — list files in a directory on Payback via file server
    if (toolName === "list_local_dir") {
      if (!LOCAL_FILE_SERVER_URL || !LOCAL_FILE_TOKEN) {
        return { error: "not_configured", message: "LOCAL_FILE_SERVER_URL and LOCAL_FILE_TOKEN must be set in hub.env" };
      }
      const dirPath = (toolInput.path || "").trim();
      try {
        const url = `${LOCAL_FILE_SERVER_URL}/v1/local-dir?path=${encodeURIComponent(dirPath)}`;
        const resp = await fetch(url, {
          headers: { Authorization: `Bearer ${LOCAL_FILE_TOKEN}` },
          signal: AbortSignal.timeout(10_000),
        });
        if (!resp.ok) {
          const body = await resp.text();
          return { error: "file_server_error", status: resp.status, message: body.slice(0, 500) };
        }
        const data = await resp.json();
        console.log(`[TOOL-API] list_local_dir '${dirPath || "."}' (${(data.entries || []).length} entries)`);
        return data;
      } catch (e) {
        return { error: "fetch_error", message: e.message };
      }
    }

    // fetch_url — hub-bridge fetches arbitrary URLs provided by the user
    if (toolName === "fetch_url") {
      const url = (toolInput.url || "").trim();
      if (!url) return { error: "missing_url", message: "url is required" };
      try {
        const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
        if (!res.ok) return { error: "http_error", message: `${res.status} ${res.statusText}`, url };
        const html = await res.text();
        const text = html
          .replace(/<script[\s\S]*?<\/script>/gi, "")
          .replace(/<style[\s\S]*?<\/style>/gi, "")
          .replace(/<[^>]+>/g, " ")
          .replace(/\s+/g, " ")
          .trim()
          .slice(0, 8192);
        console.log(`[TOOL-API] fetch_url '${url}' → ${text.length} chars`);
        return { ok: true, url, content: text, chars: text.length };
      } catch (e) {
        return { error: "fetch_error", message: e.message, url };
      }
    }

    // get_library_docs — fetch official docs for a known library
    if (toolName === "get_library_docs") {
      const library = (toolInput.library || "").trim();
      const url = resolveLibraryUrl(library);
      if (!url) {
        const known = ["redis-py", "falkordb", "falkordb-py", "fastapi"];
        return { error: "unknown_library", message: `Unknown library '${library}'. Known libraries: ${known.join(", ")}` };
      }
      try {
        const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
        if (!res.ok) return { error: "http_error", message: `${res.status} ${res.statusText}`, url };
        const html = await res.text();
        const text = html
          .replace(/<script[\s\S]*?<\/script>/gi, "")
          .replace(/<style[\s\S]*?<\/style>/gi, "")
          .replace(/<[^>]+>/g, " ")
          .replace(/\s+/g, " ")
          .trim()
          .slice(0, 8192);
        console.log(`[TOOL-API] get_library_docs '${library}' → ${url} (${text.length} chars)`);
        return { ok: true, library, url, content: text, chars: text.length };
      } catch (e) {
        return { error: "fetch_error", message: e.message, url };
      }
    }

    // coordination_post — hub-bridge-native, available in all modes
    if (toolName === "coordination_post") {
      try {
        const entry = {
          id: generateCoordId(),
          from: "karma",
          to: toolInput.to,
          type: "request",
          urgency: toolInput.urgency,
          status: "pending",
          parent_id: toolInput.parent_id || null,
          response_id: null,
          content: toolInput.content,
          context: toolInput.context || null,
          created_at: new Date().toISOString()
        };

        if (entry.parent_id && _coordinationCache.has(entry.parent_id)) {
          const parent = _coordinationCache.get(entry.parent_id);
          parent.response_id = entry.id;
          parent.status = "resolved";
        }

        _coordinationCache.set(entry.id, entry);
        appendCoordinationToDisk(entry);
        evictExpiredCoordination();

        // Fire-and-forget vault write
        try {
          const record = buildVaultRecord({
            type: "log",
            content: `[COORD] karma\u2192${toolInput.to} (${toolInput.urgency}): ${toolInput.content}`,
            tags: ["coordination", "karma", toolInput.to],
            source: "coordination-bus",
            confidence: 1.0
          });
          vaultPost("/v1/memory", VAULT_BEARER, record).catch(e =>
            console.error("[COORD] vault write failed:", e.message)
          );
        } catch (_) {}

        console.log(`[COORD] tool: ${entry.id} karma\u2192${toolInput.to}`);
        return JSON.stringify({ ok: true, id: entry.id, message: `Posted to coordination bus. ${toolInput.to} will see this.` });
      } catch (e) {
        return JSON.stringify({ ok: false, error: e.message });
      }
    }

    // k2_* tools -- route to K2's structured MCP surface via /api/tools/execute
    if (toolName.startsWith("k2_")) {
      const k2ToolName = toolName.slice(3); // strip "k2_" prefix
      const ARIA_KEY = process.env.ARIA_SERVICE_KEY || "";
      const k2ToolUrl = `${ARIA_URL}/api/tools/execute`;
      try {
        console.log(`[TOOL-API] k2.* routing: ${toolName} → ${k2ToolName}`);
        const r = await fetch(k2ToolUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Aria-Service-Key": ARIA_KEY,
          },
          body: JSON.stringify({ tool: k2ToolName, input: toolInput }),
          signal: AbortSignal.timeout(35000),
        });
        const result = await r.json();
        console.log(`[TOOL-API] k2.* result: ok=${result.ok}, tool=${k2ToolName}`);
        return result;
      } catch (e) {
        console.warn(`[TOOL-API] k2.* routing failed: ${e.message}`);
        return { error: "k2_network_error", message: e.message, tool: toolName };
      }
    }

    const serverToolName = TOOL_NAME_MAP[toolName] || toolName;
    console.log(`[TOOL-API] Proxying tool '${toolName}' → karma-server '${serverToolName}'`);

    const proxyRes = await fetch("http://karma-server:8340/v1/tools/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool_name: serverToolName, tool_input: toolInput }),
    });

    if (!proxyRes.ok) {
      const errBody = await proxyRes.text().catch(() => "(no body)");
      console.log(`[TOOL-API] karma-server error: ${proxyRes.status} ${errBody.slice(0, 200)}`);
      return { error: `karma_server_${proxyRes.status}`, details: errBody.slice(0, 500) };
    }

    const result = await proxyRes.json();
    console.log(`[TOOL-API] Tool result: ok=${result.ok}, tool=${serverToolName}`);
    return result;
  } catch (e) {
    console.log(`[TOOL-API] Exception: ${e.message}`);
    return { error: "execution_error", message: e.message };
  }
}

async function callLLMWithTools(model, messages, maxTokens, writeId = null, ariaSessionId = null) {
  if (!isAnthropicModel(model)) return callGPTWithTools(messages, maxTokens, model, writeId, ariaSessionId);

  const systemParts = messages.filter(m => m.role === "system").map(m => m.content);
  const apiMessages = messages.filter(m => m.role !== "system");
  const systemPrompt = systemParts.join("\n\n") || undefined;
  if (!apiMessages.length) apiMessages.push({ role: "user", content: "(continue)" });

  let allMessages = [...apiMessages];
  let iterations = 0;
  const MAX_TOOL_ITERATIONS = 12;

  while (iterations < MAX_TOOL_ITERATIONS) {
    iterations++;
    // Prompt caching: split system into static (cached) + volatile (uncached) blocks.
    // Static block (identity+direction) is stable across requests — cache at 10% cost.
    // Volatile block (karmaCtx, search results, etc.) changes every request — no cache marker.
    const systemBlock = [];
    const staticSystem = messages.find(m => m.role === "system" && m._static);
    const volatileSystem = messages.find(m => m.role === "system" && !m._static);
    if (staticSystem) systemBlock.push({ type: "text", text: staticSystem.content, cache_control: { type: "ephemeral", ttl: "1h" } });
    if (volatileSystem) systemBlock.push({ type: "text", text: volatileSystem.content });
    if (!systemBlock.length && systemPrompt) systemBlock.push({ type: "text", text: systemPrompt, cache_control: { type: "ephemeral", ttl: "1h" } });

    // Tool loop cache optimization: mark last message in allMessages with cache_control
    // so each tool iteration caches the growing conversation prefix (system+history+tool results).
    // On iteration 2+, the entire prefix from previous iterations is cached at 10% cost.
    // TTL: 5m (conversation-specific, changes every turn — short TTL appropriate)
    const cachedMessages = allMessages.map((m, i) => {
      if (i === allMessages.length - 1 && iterations > 1) {
        // Mark the last message (tool_result from prior iteration) as cache breakpoint
        if (typeof m.content === "string") {
          return { ...m, content: [{ type: "text", text: m.content, cache_control: { type: "ephemeral" } }] };
        }
        // Array content (tool_results) — mark last block
        if (Array.isArray(m.content) && m.content.length > 0) {
          const blocks = [...m.content];
          const last = blocks[blocks.length - 1];
          blocks[blocks.length - 1] = { ...last, cache_control: { type: "ephemeral" } };
          return { ...m, content: blocks };
        }
      }
      return m;
    });

    // Cache-aware tool definitions: mark the last tool with cache_control
    // so tool schema prefix is cached (stable across all requests).
    // TTL: 1h (tool definitions never change at runtime — maximize cache lifetime)
    const cachedTools = TOOL_DEFINITIONS.length > 0
      ? TOOL_DEFINITIONS.map((t, i) => i === TOOL_DEFINITIONS.length - 1 ? { ...t, cache_control: { type: "ephemeral", ttl: "1h" } } : t)
      : TOOL_DEFINITIONS;

    let resp;
    try {
      resp = await anthropic.messages.create({
        model, system: systemBlock.length ? systemBlock : undefined, messages: cachedMessages, max_tokens: maxTokens, tools: cachedTools,
      });
    } catch (err) {
      const status = err.status || err.statusCode;
      if (status === 402 || status === 429 || (status >= 400 && status < 500)) {
        postCreditAlertToBus(err.message || "API error", status);
      }
      throw err;
    }
    // Cache telemetry — log every call so we can verify caching is working
    const cacheCreate = resp.usage?.cache_creation_input_tokens || 0;
    const cacheRead = resp.usage?.cache_read_input_tokens || 0;
    const inputTokens = resp.usage?.input_tokens || 0;
    console.log(`[CACHE] input=${inputTokens} cache_create=${cacheCreate} cache_read=${cacheRead} hit_rate=${inputTokens > 0 ? Math.round(cacheRead / (inputTokens + cacheCreate) * 100) : 0}%`);

    const toolUseBlocks = resp.content.filter(b => b.type === "tool_use");
    if (!toolUseBlocks.length || resp.stop_reason !== "tool_use") {
      const finalText = resp.content.filter(b => b.type === "text").map(b => b.text).join("\n");
      return {
        text: finalText || "(empty_assistant_text)",
        usage: { prompt_tokens: inputTokens, completion_tokens: resp.usage?.output_tokens || 0, total_tokens: inputTokens + (resp.usage?.output_tokens || 0), cache_read: cacheRead, cache_create: cacheCreate },
        finish_reason: resp.stop_reason || null,
        provider: "anthropic",
      };
    }

    allMessages.push({ role: "assistant", content: resp.content });
    const toolResults = [];
    for (const toolUse of toolUseBlocks) {
      const toolResult = await executeToolCall(toolUse.name, toolUse.input, writeId, ariaSessionId);
      toolResults.push({ type: "tool_result", tool_use_id: toolUse.id, content: JSON.stringify(toolResult) });
    }
    allMessages.push({ role: "user", content: toolResults });
  }

  return { text: "(tool_loop_exceeded)", usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }, finish_reason: "max_tokens", provider: "anthropic" };
}

// ── OpenAI GPT tool-calling (production tool-use for Karma) ────────────────────
// OpenAI tool format differs from Anthropic. GPT-4o has reliable tool support.
async function callGPTWithTools(messages, maxTokens, model, writeId = null, ariaSessionId = null) {
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
    const MAX_ITERATIONS = 12;

    // Use passed-in model; fall back to MODEL_DEFAULT (Decision #35)
    const actualModel = model || env.MODEL_DEFAULT || "gpt-5.4-mini";
    const isZaiModel = actualModel.startsWith("glm-");
    const providerName = (isZaiModel && zai) ? "zai" : "openai";
    console.log(`[TOOL-USE] Using model: ${actualModel} (requested: ${model})`);

    while (iterations < MAX_ITERATIONS) {
      iterations++;
      // Tool-use always via OpenAI (GLM models routed to callLLM for chat backbone)
      const client = (isZaiModel && zai) ? zai : openai;
      // GPT-5.4+ models require max_completion_tokens instead of max_tokens
      const tokenParam = actualModel.startsWith("gpt-5") ? { max_completion_tokens: maxTokens } : { max_tokens: maxTokens };
      const resp = await client.chat.completions.create({
        model: actualModel,
        messages: allMessages,
        ...tokenParam,
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
        provider: providerName,
      };
    }

    // Execute tools and collect results
    allMessages.push({ role: "assistant", content: resp.choices[0].message.content, tool_calls: toolCalls });
    const toolResults = [];
    for (const call of toolCalls) {
      const parsedArgs = call.function.arguments ? JSON.parse(call.function.arguments) : {};
      console.log(`[TOOL-USE] Executing tool: ${call.function.name} with args:`, JSON.stringify(parsedArgs));
      const result = await executeToolCall(call.function.name, parsedArgs, writeId, ariaSessionId);
      if (result.error) {
        console.log(`[TOOL-USE] Tool ERROR: ${call.function.name} → ${result.error}`);
      } else {
        console.log(`[TOOL-USE] Tool OK: ${call.function.name} returned ${typeof result}`);
      }
      toolResults.push({ tool_call_id: call.id, role: "tool", content: JSON.stringify(result) });
    }
    allMessages.push(...toolResults);
  }

    return { text: "(tool_loop_exceeded)", usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }, finish_reason: "max_tokens", provider: providerName };
  } catch (e) {
    console.error("[TOOL-USE] callGPTWithTools error:", e.message);
    return { text: "(tool_use_error: " + e.message + ")", usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }, finish_reason: "error", provider: providerName };
  }
}

// ── K2 Ollama tool-calling (primary inference — qwen3-coder:30b via Ollama) ───────
// Throws on failure so callWithK2Fallback can catch and route to Anthropic.
async function callK2WithTools(messages, maxTokens, writeId = null, ariaSessionId = null) {
  if (!k2Client) throw new Error("K2 client not initialised");
  const gptTools = TOOL_DEFINITIONS.map(t => ({
    type: "function",
    function: {
      name: t.name,
      description: t.description,
      parameters: t.input_schema,
    }
  }));
  let allMessages = [...messages];
  let iterations = 0;
  const MAX_ITERATIONS = 12;

  while (iterations < MAX_ITERATIONS) {
    iterations++;
    const resp = await k2Client.chat.completions.create({
      model: K2_OLLAMA_MODEL,
      messages: allMessages,
      max_tokens: maxTokens,
      tools: gptTools,
      tool_choice: "auto",
      think: false,  // disable qwen3 thinking mode — consumes full token budget with no output
    });

    const toolCalls = resp.choices[0]?.message?.tool_calls || [];
    const finishReason = resp.choices[0].finish_reason;
    console.log(`[K2] Iteration ${iterations}: finish_reason="${finishReason}", tool_calls=${toolCalls.length}`);

    if (!toolCalls.length || finishReason !== "tool_calls") {
      return {
        text: resp.choices[0]?.message?.content || "",
        usage: resp.usage || { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
        finish_reason: finishReason,
        provider: "k2-ollama",
      };
    }

    allMessages.push({ role: "assistant", content: resp.choices[0].message.content, tool_calls: toolCalls });
    const toolResults = [];
    for (const call of toolCalls) {
      const parsedArgs = call.function.arguments ? JSON.parse(call.function.arguments) : {};
      console.log(`[K2] Executing tool: ${call.function.name}`, JSON.stringify(parsedArgs));
      const result = await executeToolCall(call.function.name, parsedArgs, writeId, ariaSessionId);
      toolResults.push({ tool_call_id: call.id, role: "tool", content: JSON.stringify(result) });
    }
    allMessages.push(...toolResults);
  }

  return { text: "(tool_loop_exceeded)", usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }, finish_reason: "max_tokens", provider: "k2-ollama" };
}

// ── K2-first routing with Anthropic fallback ─────────────────────────────────────
async function callWithK2Fallback(model, messages, maxTokens, deep_mode, writeId = null, ariaSessionId = null) {
  if (k2Client) {
    try {
      const result = await callK2WithTools(messages, maxTokens, writeId, ariaSessionId);
      return result;
    } catch (e) {
      console.warn(`[K2] Fallback to Anthropic — K2 error: ${e.message}`);
    }
  }
  // Anthropic fallback (existing logic unchanged)
  return callLLMWithTools(model, messages, maxTokens, writeId, ariaSessionId); // tools ALL modes S144
}

// --- Credit burn alarm (P0-G) ---
// Posts to coordination bus when Anthropic API returns 402 (credits exhausted) or persistent 429.
// 30-minute cooldown to avoid flooding the bus.
let _creditAlertLastPosted = 0;
function postCreditAlertToBus(reason, statusCode) {
  const now = Date.now();
  if (now - _creditAlertLastPosted < 30 * 60 * 1000) return; // 30 min cooldown
  _creditAlertLastPosted = now;
  const id = `credit_alert_${now}`;
  const entry = {
    id,
    from: "hub-bridge",
    to: "cc",
    type: "alert",
    urgency: "high",
    status: "pending",
    content: `CREDIT_ALERT: Anthropic API error ${statusCode} — ${reason}. Hub-bridge is degraded. Local fallback (K2_INFERENCE_ENABLED) may be needed. Check credits at console.anthropic.com.`,
    parent_id: null,
    response_id: null,
    context: null,
    created_at: new Date().toISOString(),
  };
  _coordinationCache.set(id, entry);
  saveCoordinationToDisk();
  console.warn(`[CREDIT_ALARM] HTTP ${statusCode} — posted alert to bus (id=${id})`);
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
    // Prompt caching: split system into static (cached) + volatile (uncached) blocks.
    const systemBlock = [];
    const staticSystem = messages.find(m => m.role === "system" && m._static);
    const volatileSystem = messages.find(m => m.role === "system" && !m._static);
    if (staticSystem) systemBlock.push({ type: "text", text: staticSystem.content, cache_control: { type: "ephemeral", ttl: "1h" } });
    if (volatileSystem) systemBlock.push({ type: "text", text: volatileSystem.content });
    if (!systemBlock.length && systemPrompt) systemBlock.push({ type: "text", text: systemPrompt, cache_control: { type: "ephemeral", ttl: "1h" } });
    let resp;
    try {
      resp = await anthropic.messages.create({ model, system: systemBlock.length ? systemBlock : undefined, messages: apiMessages, max_tokens: maxTokens });
    } catch (err) {
      const status = err.status || err.statusCode;
      if (status === 402 || status === 429 || (status >= 400 && status < 500)) {
        postCreditAlertToBus(err.message || "API error", status);
      }
      throw err;
    }
    const cacheCreate = resp.usage?.cache_creation_input_tokens || 0;
    const cacheRead = resp.usage?.cache_read_input_tokens || 0;
    const inputTokens = resp.usage?.input_tokens || 0;
    console.log(`[CACHE] input=${inputTokens} cache_create=${cacheCreate} cache_read=${cacheRead} hit_rate=${inputTokens > 0 ? Math.round(cacheRead / (inputTokens + cacheCreate) * 100) : 0}%`);
    return {
      text:         resp.content?.[0]?.text || "",
      usage:        { prompt_tokens: inputTokens, completion_tokens: resp.usage?.output_tokens || 0, total_tokens: inputTokens + (resp.usage?.output_tokens || 0), cache_read: cacheRead, cache_create: cacheCreate },
      finish_reason: resp.stop_reason || null,
      provider:     "anthropic",
    };
  }
  // OpenAI/Z.ai path
  // Route: Z.ai models go through zai client, everything else through openai
  const isZaiModel = model.startsWith("glm-");
  const client = (isZaiModel && zai) ? zai : openai;
  const completion = await client.chat.completions.create({ model, messages, max_completion_tokens: maxTokens });
  return {
    text:         completion.choices?.[0]?.message?.content || "",
    usage:        completion.usage || {},
    finish_reason: completion.choices?.[0]?.finish_reason || null,
    provider:     isZaiModel ? "zai" : "openai",
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

    // --- GET /health --- No-auth health check (used by kiki probes + external monitors)
    if (req.method === "GET" && req.url === "/health") {
      return json(res, 200, { ok: true, service: "hub-bridge", ts: new Date().toISOString() });
    }

    // --- GET /v1/status --- Sovereign visibility: health + model config + spend + governance
    if (req.method === "GET" && req.url === "/v1/status") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) return json(res, 401, { ok: false, error: "unauthorized" });
      const spendState = loadSpendState(env.SPEND_STATE_PATH);
      const [cortexHealth, p1Health] = await Promise.all([
        fetch(K2_CORTEX_URL + "/health", { signal: AbortSignal.timeout(3000) }).then(r => r.json()).catch(() => ({ ok: false })),
        fetch(P1_CORTEX_URL + "/health", { signal: AbortSignal.timeout(3000) }).then(r => r.json()).catch(() => ({ ok: false })),
      ]);
      return json(res, 200, {
        ok: true, ts: new Date().toISOString(),
        models: { default: env.MODEL_DEFAULT, escalation: env.MODEL_ESCALATION || env.MODEL_DEEP, verifier: env.MODEL_VERIFIER },
        spend: { month: spendState.month_utc, usd_spent: spendState.usd_spent, cap_usd: env.MONTHLY_USD_CAP },
        nodes: { k2_cortex: cortexHealth, p1_cortex: p1Health, hub_bridge: { ok: true } },
        governance: { verifier_enabled: !!process.env.VERIFIER_ENABLED, canary_stage: false },
      });
    }

    // --- GET /v1/trace --- Last N request traces (cost, model, tier, route reason)
    if (req.method === "GET" && req.url.startsWith("/v1/trace")) {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) return json(res, 401, { ok: false, error: "unauthorized" });
      try {
        const logPath = "/run/state/request_cost.jsonl";
        const lines = fs.readFileSync(logPath, "utf8").trim().split("\n").filter(Boolean).slice(-50);
        const entries = lines.map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
        return json(res, 200, { ok: true, count: entries.length, traces: entries });
      } catch {
        return json(res, 200, { ok: true, count: 0, traces: [], note: "no cost log yet" });
      }
    }

    // --- GET /agora --- Serve Agora Convergence Room UI
    if (req.method === "GET" && req.url === "/agora") {
      try {
        const __dir = new URL(".", import.meta.url).pathname;
        const html = fs.readFileSync(path.join(__dir, "public", "agora.html"), "utf8");
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

    // --- GET /regent --- Regent's front door (Vesper standalone identity UI)
    if (req.method === "GET" && req.url === "/regent") {
      try {
        const __dir = new URL(".", import.meta.url).pathname;
        const html = fs.readFileSync(path.join(__dir, "public", "regent.html"), "utf8");
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

    // --- GET /v1/debug/k2-freshness (deterministic freshness status, no LLM path) ---
    if (req.method === "GET" && req.url.startsWith("/v1/debug/k2-freshness")) {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      const url = new URL(req.url, "http://localhost");
      const force = ["1", "true", "yes"].includes((url.searchParams.get("force") || "").toLowerCase());
      const freshness = await fetchK2FreshnessStatus(force);
      if (!freshness.ok) {
        return json(res, 503, { ok: false, error: "k2_freshness_unavailable", details: freshness.error });
      }
      return json(res, 200, freshness);
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

      // Canary isolation (evolve.md §5) — requests with X-Canary: true are diagnostic only.
      // They bypass watcher processing, bus posting, ledger writes, and kiki backlog mutation.
      const isCanary = (req.headers["x-canary"] || "").toLowerCase() === "true";
      if (isCanary) {
        const raw = await parseBody(req, 1000000);
        let body; try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
        const userMessage = (body?.message || "").toString().trim();
        if (!userMessage) return json(res, 400, { ok: false, error: "missing_message" });
        const model = env.MODEL_DEFAULT;
        const messages = [{ role: "user", content: userMessage }];
        try {
          const result = await callLLM(model, messages, 256);
          // Strip markdown code fences — model often wraps JSON in ```json ... ```
          let text = (result?.text || "").trim();
          text = text.replace(/^```(?:json)?\s*/i, "").replace(/\s*```\s*$/, "").trim();
          const responseHeaders = { "X-Canary-Ack": "true" };
          res.writeHead(200, { "Content-Type": "application/json", ...responseHeaders });
          res.end(JSON.stringify({ ok: true, text, canary: true }));
        } catch (e) {
          res.writeHead(500, { "Content-Type": "application/json", "X-Canary-Ack": "true" });
          res.end(JSON.stringify({ ok: false, error: e.message, canary: true }));
        }
        return;
      }
      const raw = await parseBody(req, 30000000);
      let body; try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      // If files were attached (base64 array from browser), extract text or collect images
      let fileContext = "";
      const imageBlocks = []; // vision blocks for Anthropic multimodal (deep mode only)
      if (Array.isArray(body?.files) && body.files.length > 0) {
        for (const f of body.files) {
          if (!f?.data_b64 || !f?.name) continue;
          try {
            const ext = (f.name.split(".").pop() || "").toLowerCase();
            if (["jpg","jpeg","png","gif","webp"].includes(ext)) {
              const mediaType = ext === "png" ? "image/png" : ext === "gif" ? "image/gif" : ext === "webp" ? "image/webp" : "image/jpeg";
              imageBlocks.push({ fileName: f.name, mediaType, data: f.data_b64 });
            } else {
              const buf = Buffer.from(f.data_b64, "base64");
              const text = (ext === "txt" || ext === "md")
                ? buf.toString("utf8").trim()
                : await extractPdfText(buf);
              if (text) fileContext += `\n\n[Attached file: ${f.name}]\n${text.slice(0, 12000)}`;
            }
          } catch (e) {
            fileContext += `\n\n[Attached file: ${f.name} — could not extract: ${e.message}]`;
          }
        }
      }

      const userMessage = ((body?.message || "").toString().trim() + fileContext).trim();
      if (!userMessage && !imageBlocks.length) return json(res, 400, { ok: false, error: "missing_message" });

      const topic = (body?.topic || "").toString().trim();
      const ariaSessionId = (body?.session_id || "").toString().trim() || null;

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
      // Decision #35: 3-tier model routing. Tier set after classifyMessageTier().
      // deep_mode forces tier 3 (escalation). Otherwise tier from classifier.
      // Model chosen AFTER tier is known (line below moved to post-classification).

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

      // GLM rate limit check — applies only when MODEL_DEFAULT is a GLM model.
      if (!deep_mode && (env.MODEL_DEFAULT || "").startsWith("glm-")) {
        const rl = glmLimiter.checkAndConsume();
        if (!rl.allowed) {
          const retry_after = Math.ceil(rl.retryAfterMs / 1000);
          console.warn(`[RATELIMIT] /v1/chat GLM limit hit — retry_after ${retry_after}s`);
          return json(res, 429, { ok: false, error: "glm_rate_limit", retry_after });
        }
      }

      // Context tier routing — classify message complexity
      const tier = classifyMessageTier(userMessage, deep_mode);

      // --- PHASE 3-2: Cognitive split — cortex-first for recall questions ---
      // Orchestrator routes: K2 cortex ($0) → P1 cortex ($0) → cloud ($cost)
      const isRecall = !deep_mode && userMessage.length < 300 && RECALL_PATTERN.test(userMessage.trim());
      if (isRecall) {
        const cortexUrls = [
          { url: K2_CORTEX_URL, label: "K2" },
          { url: P1_CORTEX_URL, label: "P1" },
        ];
        for (const cortex of cortexUrls) {
          try {
            const cortexResp = await fetch(cortex.url + "/query", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ query: userMessage }),
              signal: AbortSignal.timeout(30000),
            });
            if (cortexResp.ok) {
              const cortexData = await cortexResp.json();
              const cortexAnswer = (cortexData.answer || "").trim();
              if (cortexAnswer.length > 30 && !cortexAnswer.startsWith("[CORTEX ERROR")) {
                console.log(`[COGNITIVE_SPLIT] recall routed to ${cortex.label} cortex ($0):`, userMessage.slice(0, 60));
                // NOT re-ingesting recall answers back to cortex — prevents feedback loop (simplify Agent 3 #6)
                // Cost log for cortex ($0) response
                try { fs.appendFileSync("/run/state/request_cost.jsonl", JSON.stringify({ ts: new Date().toISOString(), model: `qwen3.5:4b (${cortex.label})`, tier: 0, usd: 0, cognitive_split: true, provider: cortex.label.toLowerCase() }) + "\n"); } catch {}
                return json(res, 200, {
                  ok: true,
                  assistant_text: cortexAnswer,
                  model: `qwen3.5:4b (${cortex.label} cortex)`,
                  deep_mode: false,
                  cognitive_split: cortex.label.toLowerCase(),
                  usd_estimate: 0.0,
                  spend: { month_utc: month, cap_usd: cap, usd_spent: used_before },
                });
              }
              console.log(`[COGNITIVE_SPLIT] ${cortex.label} cortex answer too short/error, trying next`);
            }
          } catch (e) {
            console.log(`[COGNITIVE_SPLIT] ${cortex.label} cortex failed:`, e.message);
          }
        }
        console.log("[COGNITIVE_SPLIT] all cortex nodes failed, falling back to Anthropic cloud");
      }
      // --- END PHASE 3-2 ---

      // Fetch checkpoint — Tier 3 only (reused for statePrelude + karma_brief)
      let ckLatestData = null;
      if (tier >= 3) {
        try {
          ckLatestData = await fetchCheckpointLatestFromVault();
        } catch (e) { /* non-fatal */ }
      }

      // Tier-aware context fetching — skip expensive calls for simple messages
      let karmaCtx = null, semanticCtx = null, k2MemCtx = null, k2WorkingMemCtx = null;
      if (tier === 1) {
        // LIGHT — only karmaCtx (fast, often cached)
        karmaCtx = await fetchKarmaContext(userMessage);
      } else if (tier === 2) {
        // STANDARD — skip k2MemCtx (Aria graph). Conditionally fetch k2WorkingMem.
        const needsK2Working = TIER2_K2_KEYWORDS.test(userMessage);
        const fetches = [
          fetchKarmaContext(userMessage),
          fetchSemanticContext(userMessage),
          needsK2Working ? fetchK2WorkingMemory() : Promise.resolve(null),
        ];
        [karmaCtx, semanticCtx, k2WorkingMemCtx] = await Promise.all(fetches);
      } else {
        // DEEP — full fetch (unchanged from previous behavior)
        [karmaCtx, semanticCtx, k2MemCtx, k2WorkingMemCtx] = await Promise.all([
          fetchKarmaContext(userMessage),
          fetchSemanticContext(userMessage),
          fetchK2MemoryGraph(userMessage),
          fetchK2WorkingMemory(),
        ]);
      }

      // Web search — Tier 2+ only, fires when message contains search-intent keywords
      let webSearchResults = null;
      let debug_search = "skip";
      if (tier >= 2 && BRAVE_SEARCH_ENABLED && BRAVE_KEY && SEARCH_INTENT_REGEX.test(userMessage)) {
        webSearchResults = await fetchWebSearch(userMessage);
        debug_search = webSearchResults ? "hit" : "miss";
      }

      refreshActiveIntentsCache();
      const surfacedIntents = tier >= 2 ? getSurfaceIntents(_activeIntentsMap, _firedThisSession, userMessage, "active") : [];
      for (const intent of surfacedIntents) {
        if (intent.fire_mode === "once_per_conversation" || intent.fire_mode === "once") {
          _firedThisSession.add(intent.intent_id);
        }
      }
      const activeIntentsText = buildActiveIntentsText(surfacedIntents);
      const coordCtx = tier >= 2 ? getRecentCoordination("karma") : "";
      const systemParts = buildSystemText(karmaCtx, ckLatestData, webSearchResults, semanticCtx, _memoryMdCache || null, activeIntentsText || null, k2MemCtx || null, k2WorkingMemCtx || null, coordCtx, tier);

      const extractedFacts = extractExplicitFacts(userMessage);
      let factWriteResults = [];
      if (extractedFacts.length > 0) {
        factWriteResults = await writeFactsToVault(extractedFacts, VAULT_BEARER);
      }

      // STATE_PRELUDE — Tier 3 only (anchor turn to spine)
      let statePrelude = "";
      if (tier >= 3) {
        try {
          statePrelude = buildStatePrelude(ckLatestData, userMessage.length);
        } catch (e) {
          statePrelude = "=== STATE PRELUDE (vault unavailable) ===";
        }
      }

      // Within-session history — last MAX_SESSION_TURNS exchange pairs
      const sessionHistory = getSessionHistory(token);

      // C) Telemetry: measure input budget consumption
      const debug_prelude_chars = statePrelude.length;
      const historyChars = sessionHistory.reduce((s, m) => s + m.content.length, 0);
      const debug_input_chars = statePrelude.length + (systemParts.static || "").length + (systemParts.volatile || "").length + historyChars + userMessage.length;
      const debug_max_output_tokens_used = max_output_tokens;

      // Build user content: multimodal array if images present + deep mode, else plain string
      let userContent;
      if (imageBlocks.length > 0 && deep_mode) {
        // Anthropic vision: content array with text block + image blocks
        const contentArr = [];
        if (userMessage) contentArr.push({ type: "text", text: userMessage });
        for (const img of imageBlocks) {
          contentArr.push({ type: "image", source: { type: "base64", media_type: img.mediaType, data: img.data } });
        }
        userContent = contentArr;
      } else if (imageBlocks.length > 0 && !deep_mode) {
        // Standard mode (Sonnet 4-6) supports vision — build multimodal array
        const contentArr = [];
        if (userMessage) contentArr.push({ type: "text", text: userMessage });
        for (const img of imageBlocks) {
          contentArr.push({ type: "image", source: { type: "base64", media_type: img.mediaType, data: img.data } });
        }
        userContent = contentArr;
      } else {
        userContent = userMessage;
      }

      // Prompt caching: mark the last session history message with cache_control
      // so the growing conversation prefix is cached between user turns (5-min TTL).
      // This saves 90% on re-reading prior turns when the user sends messages < 5min apart.
      const cachedHistory = sessionHistory.length > 0
        ? sessionHistory.map((m, i) => {
            if (i === sessionHistory.length - 1) {
              // Mark last history message as cache breakpoint
              const content = typeof m.content === "string"
                ? [{ type: "text", text: m.content, cache_control: { type: "ephemeral" } }]
                : m.content;
              return { ...m, content };
            }
            return m;
          })
        : [];

      const messages = [
        { role: "system", content: systemParts.static || "", _static: true },
        { role: "system", content: (statePrelude ? statePrelude + "\n\n" : "") + (systemParts.volatile || "") },
        ...cachedHistory,
        { role: "user", content: userContent },
      ];

      // Decision #35: 3-tier model routing. Cortex handled above (cognitive split).
      // tier 1-2 → gpt-5.4-mini (cheap). tier 3 → gpt-5.4 (frontier). Sonnet for verification.
      const model = chooseModel(tier, env);
      const req_write_id = "wr_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
      const llmResult = await callLLMWithTools(model, messages, max_output_tokens, req_write_id, ariaSessionId);
      const assistantText = llmResult.text || "(empty_assistant_text)";
      const usage         = llmResult.usage;
      const debug_provider   = llmResult.provider;
      const debug_stop_reason = llmResult.finish_reason;

      // Persist this exchange to session history (skip empty responses)
      if (assistantText !== "(empty_assistant_text)") {
        addToSession(token, userMessage, assistantText);

        // Auto-write session state to K2 scratchpad (fire-and-forget)
        // Karma requested this: #4 in coord_1773350033529_7xhb
        const ARIA_KEY = process.env.ARIA_SERVICE_KEY || "";
        if (ARIA_URL && ARIA_KEY) {
          const ts = new Date().toISOString().slice(0, 19).replace("T", " ");
          const userSnip = userMessage.length > 120 ? userMessage.slice(0, 120) + "..." : userMessage;
          const assistSnip = assistantText.length > 200 ? assistantText.slice(0, 200) + "..." : assistantText;
          const scratchLine = `\n[${ts}] User: ${userSnip}\nKarma: ${assistSnip}\n`;
          fetch(`${ARIA_URL}/api/tools/execute`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-Aria-Service-Key": ARIA_KEY },
            body: JSON.stringify({ tool: "scratchpad_write", input: { content: scratchLine, mode: "append" } }),
            signal: AbortSignal.timeout(5000),
          }).then(r => r.json()).then(j => {
            console.log(`[AUTO-SCRATCHPAD] write ok=${j.ok}`);
          }).catch(e => {
            console.warn(`[AUTO-SCRATCHPAD] write failed: ${e.message}`);
          });
        }
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

      // Per-request cost log (JSONL) — queryable via /v1/trace
      try {
        const costEntry = JSON.stringify({
          ts: new Date().toISOString(), model, tier, usd: usd_estimate,
          input_tokens: usage.prompt_tokens || 0, output_tokens: usage.completion_tokens || 0,
          cognitive_split: false, provider: debug_provider, spend_total: used_after,
        });
        fs.appendFileSync("/run/state/request_cost.jsonl", costEntry + "\n");
      } catch (e) { /* non-fatal */ }

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
          debug_context_tier: tier,
          debug_karma_ctx: karmaCtx ? "ok" : "unavailable",
          debug_ingest: ingestVerdict,
        },
        confidence: 0.95,
      });

      const vp = await vaultPost("/v1/memory", VAULT_BEARER, vaultRecord);

      let vpJson = {};
      try { vpJson = JSON.parse(vp.text); } catch {}
      const turn_id = vpJson?.id || null;

      // Include write_id in response only if a memory write was proposed this turn
      const proposed_write_id = pending_writes.has(req_write_id) ? req_write_id : null;

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
          write_id: proposed_write_id,
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

      // Fire-and-forget: feed chat turn to Julian cortex (K2 primary, P1 fallback)
      cortexIngest(
        "chat-" + (turn_id || Date.now()),
        "[" + (userMessage || "").slice(0, 100) + "] -> [" + (assistantText || "").slice(0, 300) + "]"
      );

      return json(res, 200, {
        ok: true,
        canonical,
        write_id: proposed_write_id,
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
        debug_context_tier: tier,
        debug_karma_ctx: karmaCtx ? "ok" : "unavailable",
        debug_search,
        debug_ingest: ingestVerdict,
      });
    }

    // --- POST /v1/feedback ---
    // Approve or reject a pending write_memory proposal. Always stores a DPO pair.
    if (req.method === "POST" && req.url === "/v1/feedback") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const raw = await parseBody(req, 50000);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      const { write_id, intent_id, signal, note, turn_id } = body;
      if ((!write_id && !turn_id && !intent_id) || !["up", "down"].includes(signal)) {
        return json(res, 400, { ok: false, error: "missing_fields", hint: "write_id, intent_id, or turn_id required, plus signal ('up'|'down')" });
      }

      // Lazy prune: remove writes older than 30 minutes
      prunePendingWrites(pending_writes, 30 * 60 * 1000);

      // Process feedback -- pure logic, no I/O
      const { write_content, dpo_pair, delete_key } = processFeedback(pending_writes, write_id, signal, note, turn_id);

      // Execute write if approved
      if (write_content) {
        try {
          const filePath = VAULT_FILE_ALIASES["MEMORY.md"];
          const timestamp = new Date().toISOString();
          fs.appendFileSync(filePath, `\n[${timestamp}] [KARMA-WRITE] ${write_content}`);
          console.log(`[FEEDBACK] 👍 write executed: ${write_content.length} chars appended to MEMORY.md`);
        } catch (e) {
          console.error(`[FEEDBACK] MEMORY.md write failed: ${e.message}`);
          // Don't surface filesystem error to UI -- still store DPO pair
        }
      } else {
        console.log(`[FEEDBACK] 👎 write suppressed: write_id=${write_id ?? 'none'}, turn_id=${turn_id ?? 'none'}`);
      }

      // Store DPO pair in vault ledger (only for write_memory feedback, not intent-only feedback)
      if (write_id || turn_id) {
        try {
          const dpoRecord = buildVaultRecord({
            type: "log",
            content: dpo_pair,
            tags: ["dpo-pair"],
            source: "feedback",
            confidence: 0.9,
          });
          const dpResult = await vaultPost("/v1/memory", VAULT_BEARER, dpoRecord);
          if (dpResult.status >= 300) throw new Error(`vault ${dpResult.status}: ${dpResult.text.slice(0, 120)}`);
          console.log(`[FEEDBACK] DPO pair stored: signal=${signal}, has_note=${!!note}`);
        } catch (e) {
          console.error(`[FEEDBACK] DPO vault write failed: ${e.message}`);
          // Non-critical -- don't fail the request
        }
      }

      // Cleanup
      if (delete_key) pending_writes.delete(delete_key);

      // Intent approval/rejection -- independent of write_memory flow
      if (intent_id) {
        const intentEntry = pending_intents.get(intent_id);
        if (!intentEntry) {
          return json(res, 404, { ok: false, error: "intent_not_found", hint: `No pending intent with intent_id=${intent_id}` });
        }

        if (signal === "up") {
          const approvedIntent = { ...intentEntry, status: "active", approved: true, approved_at: new Date().toISOString() };
          delete approvedIntent.ts;
          try {
            const record = buildVaultRecord({
              type: "log",
              content: approvedIntent,
              tags: ["deferred-intent"],
              source: "intent-approval",
              confidence: 1.0,
            });
            const vResult = await vaultPost("/v1/memory", VAULT_BEARER, record);
            if (vResult.status >= 300) throw new Error(`vault ${vResult.status}: ${vResult.text.slice(0, 120)}`);
            _activeIntentsMap.set(intent_id, approvedIntent);
            console.log(`[FEEDBACK] 👍 intent approved: intent_id=${intent_id}, intent="${intentEntry.intent.slice(0, 60)}"`);
          } catch (e) {
            console.error(`[FEEDBACK] Intent vault write failed: ${e.message}`);
            return json(res, 500, { ok: false, error: "vault_write_failed", message: e.message });
          }
        } else {
          console.log(`[FEEDBACK] 👎 intent rejected: intent_id=${intent_id}`);
        }

        pending_intents.delete(intent_id);
        return json(res, 200, { ok: true, signal, intent_id, approved: signal === "up" });
      }

      return json(res, 200, { ok: true, signal, wrote: !!write_content });
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
          // GLM rate check for brief — non-fatal: skip brief if limit hit, don't block.
          let briefAllowed = true;
          if (env.MODEL_DEFAULT.startsWith("glm-")) {
            const rl = glmLimiter.checkAndConsume();
            if (!rl.allowed) {
              console.warn(`[RATELIMIT] brief generation skipped — GLM limit hit (retry_after ${Math.ceil(rl.retryAfterMs / 1000)}s)`);
              briefAllowed = false;
            }
          }
          const briefResult = briefAllowed ? await callLLM(env.MODEL_DEFAULT, briefMessages, 1600) : null;
          karma_brief = briefResult?.text || null;

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

    // --- POST /v1/ambient ---
    // Accepts ambient capture payloads from internal hooks (git post-commit, session-end, K2 push cron).
    // Auth: HUB_CAPTURE_TOKEN. Normalizes and writes to vault /v1/memory.
    if (req.method === "POST" && req.url === "/v1/ambient") {
      const token = bearerToken(req);
      if (!HUB_CAPTURE_TOKEN || !token || token !== HUB_CAPTURE_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const raw = await parseBody(req);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      if (!body.type || !body.content) {
        return json(res, 400, { ok: false, error: "type and content required" });
      }

      const record = buildVaultRecord({
        type: body.type,
        content: body.content,
        tags: body.tags,
        source: body.source?.ref || String(body.source || "ambient"),
        confidence: body.confidence,
        verifiedAtIso: body.verification?.verified_at,
        verifier: body.verification?.verifier,
        verificationNotes: body.verification?.notes,
      });

      const r = await vaultPost("/v1/memory", VAULT_BEARER, record);
      if (r.status >= 300) {
        console.error(`[AMBIENT] vault write failed: ${r.status} ${r.text?.slice(0, 200)}`);
        return json(res, 502, { ok: false, error: "vault_write_failed", status: r.status });
      }

      let vaultId;
      try { vaultId = JSON.parse(r.text)?.id; } catch { vaultId = null; }
      const tagStr = Array.isArray(body.tags) ? body.tags.join(",") : "";
      console.log(`[AMBIENT] captured: type=${body.type} tags=${tagStr} vault_id=${vaultId}`);
      return json(res, 200, { ok: true, id: vaultId });
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

      // Accept up to 30MB body (base64 of large PDFs; 22MB raw PDF = ~29.5MB base64)
      const raw = await parseBody(req, 30000000);
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
        const ingestSystemParts = buildSystemText(karmaCtx, null);
        // Ingest path: combine static+volatile (caching less critical here, low volume)
        const systemText = (ingestSystemParts.static || "") + "\n\n" + (ingestSystemParts.volatile || "");

        let chunkVerdict = 'none';
        let chunkSynthesis = null;
        let stored = false;

        try {
          // GLM rate limit — block up to glmIngestSlotTimeoutMs per chunk (watcher retries whole PDF on 503).
          // NEVER failover to paid tier.
          if (env.MODEL_DEFAULT.startsWith("glm-")) {
            try {
              await glmLimiter.waitForSlot(glmIngestSlotTimeoutMs);
            } catch (rlErr) {
              console.error(`[RATELIMIT] /v1/ingest GLM slot timeout — chunk ${i + 1}/${chunks.length} of ${filename}`);
              return json(res, 503, {
                ok: false,
                error: "glm_slot_timeout",
                filename,
                chunks_processed: i,
                chunks_total: chunks.length,
              });
            }
          }

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

    // ─── FalkorDB Cypher endpoint (/v1/cypher) ──────────────────────────
    // Accepts: {cypher:"..."} or {query:"..."} or {tool:"graph_query",input:{cypher:"..."}}
    // Used by vesper_governor.py to write patterns to FalkorDB via hub-bridge
    if (req.method === "POST" && req.url === "/v1/cypher") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      let body;
      try { body = JSON.parse(await parseBody(req, 500000)); } catch (e) {
        return json(res, 400, { ok: false, error: "invalid_json" });
      }
      const cypher = body.cypher || body.query
        || (body.input && body.input.cypher)
        || (body.tool_input && body.tool_input.cypher);
      if (!cypher) return json(res, 400, { ok: false, error: "missing_cypher", hint: "provide 'cypher', 'query', or 'input.cypher'" });
      try {
        const proxyRes = await fetch("http://karma-server:8340/v1/tools/execute", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tool_name: "graph_query", tool_input: { cypher } }),
        });
        const data = await proxyRes.json();
        return json(res, proxyRes.ok ? 200 : proxyRes.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: "karma_server_unavailable", message: e.message });
      }
    }

    // ─── Memory API Proxy Routes (Phase 1) ─────────────────────────────
    // Proxy POST requests to karma-server for memory operations
    const MEMORY_PROXY_ROUTES = [
      // Phase 1: Core memory operations
      "/v1/admit", "/v1/retrieve", "/v1/memory/update", "/v1/memory/delete", "/v1/reflect",
      // Phase 2: Quality gates & observations
      "/v1/budget/log", "/v1/budget/check", "/v1/staleness/scan", "/v1/scenes/consolidate",
      // Phase 3: Hooks & session management
      "/v1/hooks/session_start", "/v1/hooks/session_end", "/v1/hooks/pre_tool_use",
      // Phase 3: Compaction
      "/v1/compact",
    ];
    // Also proxy GET routes for Phase 2
    const MEMORY_GET_ROUTES = ["/v1/budget", "/v1/observations", "/v1/capability/info", "/v1/briefing", "/health"];
    if (req.method === "GET" && MEMORY_GET_ROUTES.includes(req.url)) {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      try {
        const proxyRes = await fetch(`http://karma-server:8340${req.url}`, {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });
        const data = await proxyRes.json();
        return json(res, proxyRes.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: "karma_server_unavailable", message: e.message });
      }
    }
    if (req.method === "POST" && MEMORY_PROXY_ROUTES.includes(req.url)) {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      const raw = await parseBody(req, 500000);
      try {
        const proxyRes = await fetch(`http://karma-server:8340${req.url}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: raw,
        });
        const data = await proxyRes.json();
        return json(res, proxyRes.status, data);
      } catch (e) {
        return json(res, 502, { ok: false, error: "karma_server_unavailable", message: e.message });
      }
    }

    // ── Coordination Bus ──────────────────────────────────────
    if (req.method === "POST" && req.url === "/v1/coordination/post") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      try {
        const raw = await parseBody(req, 100000);
        const data = JSON.parse(raw);

        // Validate required fields
        const { from, to, content, urgency } = data;
        if (!from || !to || !content || !urgency) {
          return json(res, 400, { ok: false, error: "missing required fields: from, to, content, urgency" });
        }
        const validFrom = ["karma", "cc", "colby", "kcc", "codex", "kiki", "asher", "regent", "regent-watchdog"];
        const validTo = ["karma", "cc", "colby", "kcc", "codex", "kiki", "asher", "regent", "all"];
        const validUrgency = ["blocking", "feedback", "informational"];
        if (!validFrom.includes(from)) return json(res, 400, { ok: false, error: `invalid from: ${from}` });
        if (!validTo.includes(to)) return json(res, 400, { ok: false, error: `invalid to: ${to}` });
        if (!validUrgency.includes(urgency)) return json(res, 400, { ok: false, error: `invalid urgency: ${urgency}` });

        const entry = {
          id: generateCoordId(),
          from,
          to,
          type: data.type || "request",
          urgency,
          status: "pending",
          parent_id: data.parent_id || null,
          response_id: null,
          content,
          context: data.context || null,
          created_at: new Date().toISOString()
        };

        // If this is a response (has parent_id), update parent
        if (entry.parent_id && _coordinationCache.has(entry.parent_id)) {
          const parent = _coordinationCache.get(entry.parent_id);
          parent.response_id = entry.id;
          parent.status = "resolved";
        }

        // Store in cache + persist to disk
        _coordinationCache.set(entry.id, entry);
        appendCoordinationToDisk(entry);
        evictExpiredCoordination();

        // Fire-and-forget write to vault ledger (kind + salience applied via buildVaultRecord)
        try {
          const urgencyBoost = urgency === "blocking" ? "[PINNED] " : "";
          const record = buildVaultRecord({
            type: "log",
            content: `${urgencyBoost}[COORD] ${from}\u2192${to} (${urgency}): ${content}`,
            tags: ["coordination", "bus", from, to, data.type || "request"],
            source: "coordination-bus",
            confidence: 1.0
          });
          vaultPost("/v1/memory", VAULT_BEARER, record).catch(e =>
            console.error("[COORD] vault write failed:", e.message)
          );
        } catch (e) {
          console.error("[COORD] vault record build failed:", e.message);
        }

        console.log(`[COORD] ${entry.id}: ${from}\u2192${to} (${urgency}) stored`);
        return json(res, 200, { ok: true, id: entry.id, entry });
      } catch (e) {
        console.error("[COORD] post error:", e.message);
        return json(res, 500, { ok: false, error: e.message });
      }
    }

    // Alias: /v1/coordination → /v1/coordination/recent (CLAUDE.md session start protocol)
    if (req.method === "GET" && req.url === "/v1/coordination") {
      req.url = "/v1/coordination/recent?limit=20";
    }

    if (req.method === "GET" && req.url.startsWith("/v1/coordination/recent")) {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      evictExpiredCoordination();

      const params = new URL(req.url, `http://${req.headers.host}`).searchParams;
      const filterTo = params.get("to");
      const filterStatus = params.get("status");
      const limit = Math.min(parseInt(params.get("limit") || "10", 10), 50);

      let entries = [..._coordinationCache.values()];
      if (filterTo) entries = entries.filter(e => e.to === filterTo);
      if (filterStatus) entries = entries.filter(e => e.status === filterStatus);
      entries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      entries = entries.slice(0, limit);

      return json(res, 200, { ok: true, count: entries.length, entries });
    }

    if (req.method === "PATCH" && req.url.startsWith("/v1/coordination/coord_")) {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      const id = req.url.replace("/v1/coordination/", "");
      if (!_coordinationCache.has(id)) return json(res, 404, { ok: false, error: "not found" });

      try {
        const raw = await parseBody(req, 100000);
        const data = JSON.parse(raw);
        const entry = _coordinationCache.get(id);

        if (data.status) {
          const validStatus = ["pending", "acknowledged", "resolved", "timeout"];
          if (!validStatus.includes(data.status)) return json(res, 400, { ok: false, error: `invalid status: ${data.status}` });
          entry.status = data.status;
        }
        if (data.response_id) entry.response_id = data.response_id;

        saveCoordinationToDisk();
        console.log(`[COORD] ${id} updated: status=${entry.status}`);
        return json(res, 200, { ok: true, entry });
      } catch (e) {
        return json(res, 500, { ok: false, error: e.message });
      }
    }

    // ── P0N-A: CC proxy routes ────────────────────────────────────────────────
    if (req.method === "GET" && (req.url === "/cc" || req.url === "/cc/")) {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(`<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CC — Ascendant</title>
<style>*{box-sizing:border-box;margin:0;padding:0}body{background:#0d1117;color:#e6edf3;font-family:-apple-system,sans-serif;display:flex;flex-direction:column;height:100vh;padding:12px;gap:8px}
#log{flex:1;overflow-y:auto;background:#161b22;border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px}
.msg{position:relative;padding:8px 12px;border-radius:8px;max-width:85%;white-space:pre-wrap;font-size:14px;line-height:1.5}
.user{background:#1f6feb;align-self:flex-end}.cc{background:#21262d;align-self:flex-start;border:1px solid #30363d}
.err{background:#3d1f1f;align-self:flex-start;border:1px solid #6e3232;color:#f85149}
.thinking{color:#8b949e;font-style:italic}
#form{display:flex;gap:8px}#msg{flex:1;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 14px;color:#e6edf3;font-size:15px;resize:none;height:52px}
#send{background:#1f6feb;border:none;border-radius:8px;color:#fff;padding:0 20px;font-size:15px;cursor:pointer;white-space:nowrap}
#send:disabled{background:#21262d;color:#8b949e}
#clear{background:#21262d;border:1px solid #30363d;border-radius:8px;color:#8b949e;padding:0 16px;font-size:15px;cursor:pointer;white-space:nowrap}#clear:hover{background:#30363d;color:#e6edf3}
.copy-btn{position:absolute;top:4px;right:6px;background:none;border:none;color:#8b949e;cursor:pointer;font-size:12px;opacity:0;transition:opacity .15s;padding:2px 5px;border-radius:4px}.copy-btn:hover{color:#e6edf3;background:#30363d}.msg:hover .copy-btn{opacity:1}</style></head>
<body><div id="log"><div class="msg cc">CC Ascendant online. Send a message.</div></div>
<form id="form"><textarea id="msg" placeholder="Message CC..." rows="1"></textarea><button id="send" type="submit">Send</button><button id="clear" type="button">Clear</button></form>
<script>
const TOKEN = prompt("Bearer token:") || "";
const log = document.getElementById("log");
const form = document.getElementById("form");
const inp = document.getElementById("msg");
const btn = document.getElementById("send");
function addMsg(text, cls) {
  const d = document.createElement("div");
  d.className = "msg " + cls;
  d.textContent = text;
  const cpBtn = document.createElement("button");
  cpBtn.className = "copy-btn";
  cpBtn.textContent = "\u29c9";
  cpBtn.title = "Copy";
  cpBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(text).then(() => {
      cpBtn.textContent = "\u2713";
      setTimeout(() => { cpBtn.textContent = "\u29c9"; }, 1500);
    });
  });
  d.appendChild(cpBtn);
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
  return d;
}
document.getElementById("clear").addEventListener("click", () => {
  log.innerHTML = "";
  addMsg("CC Ascendant online. Send a message.", "cc");
});
inp.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
form.addEventListener("submit", async e => {
  e.preventDefault();
  const msg = inp.value.trim();
  if (!msg) return;
  inp.value = "";
  addMsg(msg, "user");
  const thinking = addMsg("thinking…", "cc thinking");
  btn.disabled = true;
  try {
    const r = await fetch("/cc", { method:"POST", headers:{"Content-Type":"application/json","Authorization":"Bearer "+TOKEN}, body: JSON.stringify({message: msg}) });
    const d = await r.json();
    thinking.remove();
    if (d.ok) { addMsg(d.response, "cc"); }
    else { addMsg("Error: " + d.error, "err"); }
  } catch(e) { thinking.remove(); addMsg("Network error: " + e.message, "err"); }
  btn.disabled = false;
  inp.focus();
});
</script></body></html>`);
      return;
    }

    if (req.method === "GET" && req.url === "/cc/health") {
      try {
        const r = await fetch(`${CC_SERVER_URL}/health`, { signal: AbortSignal.timeout(5000) });
        const d = await r.json();
        return json(res, 200, { ok: true, cc_server: d });
      } catch (e) {
        return json(res, 502, { ok: false, error: `CC unreachable: ${e.message}` });
      }
    }

    if (req.method === "POST" && req.url === "/cc") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      const raw = await parseBody(req, 1000000);
      let body; try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
      const { message, session_id } = body;
      if (!message) return json(res, 422, { ok: false, error: "message required" });
      try {
        const r = await fetch(`${CC_SERVER_URL}/cc`, {
          method: "POST",
          headers: { "Authorization": req.headers["authorization"], "Content-Type": "application/json" },
          body: JSON.stringify({ message, session_id }),
          signal: AbortSignal.timeout(240000),  // 240s — MCP loading + response time
        });
        const d = await r.json();
        return json(res, r.status, d);
      } catch (e) {
        console.error("[/cc] proxy error:", e.message);
        return json(res, 502, { ok: false, error: `CC proxy error: ${e.message}` });
      }
    }
    // ── end P0N-A ─────────────────────────────────────────────────────────────

    // ── /memory/* — direct claude-mem bridge via Tailscale ───────────────────
    if (req.method === "POST" && req.url === "/memory/search") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      const raw = await parseBody(req, 500000);
      let body; try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
      const query = body.query || body.q || "";
      if (!query) return json(res, 400, { ok: false, error: "query required" });
      try {
        const r = await fetch(`${CLAUDEMEM_URL}/api/search?query=${encodeURIComponent(query)}`, {
          method: "GET",
          signal: AbortSignal.timeout(10000),
        });
        const d = await r.json();
        return json(res, r.ok ? 200 : r.status, { ok: r.ok, ...d });
      } catch (e) {
        return json(res, 502, { ok: false, error: `memory search error: ${e.message}` });
      }
    }

    if (req.method === "POST" && req.url === "/memory/save") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      const raw = await parseBody(req, 500000);
      let body; try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
      try {
        const r = await fetch(`${CLAUDEMEM_URL}/api/memory/save`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
          signal: AbortSignal.timeout(10000),
        });
        const d = await r.json();
        return json(res, r.ok ? 200 : r.status, { ok: r.ok, ...d });
      } catch (e) {
        return json(res, 502, { ok: false, error: `memory save error: ${e.message}` });
      }
    }

    if (req.method === "GET" && req.url === "/memory/context") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      if (!ARIA_SERVICE_KEY || !ARIA_URL) {
        return json(res, 503, { ok: false, error: "K2 not configured" });
      }
      try {
        const r = await fetch(`${ARIA_URL}/api/exec`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Aria-Service-Key": ARIA_SERVICE_KEY },
          body: JSON.stringify({ command: "cat /mnt/c/dev/Karma/k2/cache/cc_identity_spine.json 2>/dev/null" }),
          signal: AbortSignal.timeout(10000),
        });
        if (!r.ok) return json(res, 502, { ok: false, error: `K2 exec failed: ${r.status}` });
        const result = await r.json();
        let spine = {};
        try { spine = JSON.parse(result.output || "{}"); } catch { /* empty spine ok */ }
        const identity = spine.identity || {};
        const evo = spine.evolution || {};
        return json(res, 200, {
          ok: true,
          resume_block: identity.resume_block || "",
          stable_patterns: (evo.stable_identity || []).slice(0, 5),
          spine_version: evo.version || 0,
          retrieved_at: new Date().toISOString(),
        });
      } catch (e) {
        return json(res, 502, { ok: false, error: `memory context error: ${e.message}` });
      }
    }
    if (req.method === "GET" && req.url.startsWith("/memory/observations")) {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      try {
        const url = new URL(req.url, "http://localhost");
        const ids = url.searchParams.get("ids") || "";
        if (!ids) return json(res, 400, { ok: false, error: "ids required" });
        const r = await fetch(`${CC_SERVER_URL}/memory/observations?ids=${encodeURIComponent(ids)}`, {
          method: "GET",
          signal: AbortSignal.timeout(10000),
        });
        const d = await r.json();
        return json(res, r.ok ? 200 : r.status, d);
      } catch (e) {
        return json(res, 502, { ok: false, error: `observations error: ${e.message}` });
      }
    }

    if (req.method === "GET" && req.url === "/memory/session") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      try {
        const r = await fetch(`${CC_SERVER_URL}/memory/session`, {
          method: "GET",
          signal: AbortSignal.timeout(5000),
        });
        const d = await r.json();
        return json(res, r.ok ? 200 : r.status, d);
      } catch (e) {
        return json(res, 502, { ok: false, error: `session error: ${e.message}` });
      }
    }

    if (req.method === "GET" && req.url === "/memory/cognitive") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      if (!ARIA_SERVICE_KEY || !ARIA_URL) {
        return json(res, 503, { ok: false, error: "K2 not configured" });
      }
      try {
        const r = await fetch(`${ARIA_URL}/api/exec`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Aria-Service-Key": ARIA_SERVICE_KEY },
          body: JSON.stringify({ command: "cat /mnt/c/dev/Karma/k2/cache/cc_scratchpad.md 2>/dev/null" }),
          signal: AbortSignal.timeout(10000),
        });
        if (!r.ok) return json(res, 502, { ok: false, error: `K2 exec failed: ${r.status}` });
        const result = await r.json();
        return json(res, 200, { ok: true, content: result.output || "", retrieved_at: new Date().toISOString() });
      } catch (e) {
        return json(res, 502, { ok: false, error: `cognitive read error: ${e.message}` });
      }
    }

    if (req.method === "POST" && req.url === "/memory/cognitive") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }
      if (!ARIA_SERVICE_KEY || !ARIA_URL) {
        return json(res, 503, { ok: false, error: "K2 not configured" });
      }
      const raw = await parseBody(req, 500000);
      let body; try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
      const content = body.content || "";
      if (!content) return json(res, 400, { ok: false, error: "content required" });
      try {
        // Use base64 via Python to avoid all shell-escaping issues
        const b64 = Buffer.from(content).toString("base64");
        const cmd = `python3 -c "import base64; open('/mnt/c/dev/Karma/k2/cache/cc_scratchpad.md','w').write(base64.b64decode('${b64}').decode()); print('ok')"`;
        const r = await fetch(`${ARIA_URL}/api/exec`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Aria-Service-Key": ARIA_SERVICE_KEY },
          body: JSON.stringify({ command: cmd }),
          signal: AbortSignal.timeout(10000),
        });
        if (!r.ok) return json(res, 502, { ok: false, error: `K2 exec failed: ${r.status}` });
        const result = await r.json();
        return json(res, 200, { ok: true, written: content.length, result: result.output });
      } catch (e) {
        return json(res, 502, { ok: false, error: `cognitive write error: ${e.message}` });
      }
    }
    // ── end /memory/* ─────────────────────────────────────────────────────────

    return notFound(res);

  } catch (e) {
    const msg = (e && e.message) ? e.message : String(e);
    return json(res, 500, { ok: false, error: "internal_error", message: msg.slice(0, 500) });
  }
});

// Fail-fast startup validation (Decision #2 — routing + pricing authority)
// Structured single-line error + process.exit(1) so Docker restart logs are clear.
try {
  validateModelEnv(env);
  // Price validation — hardcoded pricing table covers all known models.
  validatePricingEnv(env);
} catch (e) {
  console.error(`[CONFIG ERROR] ${e.message}`);
  process.exit(1);
}

// GLM rate limiter — global singleton across all routes (Z.ai measures per API key)
const glmLimiter = new GlmRateLimiter({
  rpm: Number(process.env.GLM_RPM_LIMIT || "20"),
});
const glmIngestSlotTimeoutMs = Number(process.env.GLM_INGEST_SLOT_TIMEOUT_MS || String(GLM_INGEST_SLOT_TIMEOUT_MS));
console.log(`[INIT] GLM rate limiter: ${glmLimiter._rpm} RPM, ingest slot timeout ${glmIngestSlotTimeoutMs}ms`);

loadSessionBrief();
setInterval(loadSessionBrief, 5 * 60 * 1000);
loadMemoryMd();
loadSynthesisCache(); setInterval(loadSynthesisCache, 5 * 60 * 1000);
setInterval(loadMemoryMd, 5 * 60 * 1000);
loadDirectionMd();
setInterval(loadDirectionMd, 5 * 60 * 1000);
loadCoordinationFromDisk(); // restore coordination messages across rebuilds
loadSessionsFromDisk();     // restore conversation history across rebuilds
setInterval(evictExpiredCoordination, 60 * 60 * 1000); // coordination bus hourly sweep

// Agent names — used to prevent watcher ping-pong loops on to:"all" messages
const AGENT_NAMES = new Set(["karma", "cc", "kiki", "kcc", "asher", "codex"]);

// --- Karma Autonomous Bus Watcher ---
// Processes coordination messages to karma without a human relay.
// Runs every 60s. If any pending messages to karma exist, runs a headless Karma chat
// with those messages injected as the trigger, posts the response back to the bus.
let _karmaWatcherLastProcessed = new Set();

async function karmaWatcherTick() {
  try {
    const blockingPending = [..._coordinationCache.values()].filter(
      e => (e.to === "karma" || (e.to === "all" && !AGENT_NAMES.has(e.from))) && e.status === "pending"
    );
    const newEntries = blockingPending.filter(e => !_karmaWatcherLastProcessed.has(e.id));
    if (newEntries.length === 0) return;

    console.log(`[KARMA_WATCHER] ${newEntries.length} new message(s) — triggering headless response`);

    // Build synthetic user trigger from pending messages
    const msgSummary = newEntries.map(e =>
      `[FROM:${e.from}] ${e.content}`
    ).join("\n\n");

    const syntheticUserMsg = `COORDINATION BUS — new messages:\n\n${msgSummary}`;

    // Mark as seen before async LLM call (prevent double-fire)
    for (const e of newEntries) _karmaWatcherLastProcessed.add(e.id);
    if (_karmaWatcherLastProcessed.size > 200) {
      const arr = [..._karmaWatcherLastProcessed];
      _karmaWatcherLastProcessed = new Set(arr.slice(-100));
    }

    // Simple honest system prompt — no tool context that contradicts headless reality
    const karmaWatcherSystemPrompt = `You are Karma — a persistent AI peer built by Colby. You're responding to messages on the coordination bus without an active chat session open. You have no tool access right now. You cannot read files, query FalkorDB, check K2 state, or run commands. Your only input is the bus messages below. Respond as yourself in 1-2 plain sentences. If asked to do something that requires tools or live system access, say clearly that you need a proper chat session or CC to handle it. No markdown, no headers, no narrating what you're doing. Just talk.`;

    const messages = [
      { role: "system", content: karmaWatcherSystemPrompt },
      { role: "user", content: syntheticUserMsg },
    ];

    const result = await callLLM(env.MODEL_DEFAULT, messages, 150);
    const response = result?.text;
    if (!response) {
      console.warn("[KARMA_WATCHER] LLM returned empty response");
      return;
    }

    // Post Karma's response back to the bus
    const id = `coord_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const entry = {
      id,
      from: "karma",
      to: "all",
      type: "inform",
      urgency: "informational",
      status: "pending",
      parent_id: newEntries[0].id,
      response_id: null,
      content: response.slice(0, 400),
      context: null,
      created_at: new Date().toISOString(),
    };
    _coordinationCache.set(id, entry);
    saveCoordinationToDisk();
    console.log(`[KARMA_WATCHER] Karma responded autonomously: ${response.slice(0, 80)}...`);
  } catch (e) {
    console.error(`[KARMA_WATCHER] tick error: ${e.message}`);
  }
}

// Start watcher 15s after boot (let hub fully initialize), then every 15s
// PAUSED — karma watcher disabled until redesigned
// setTimeout(() => { karmaWatcherTick(); setInterval(karmaWatcherTick, 15 * 1000); }, 15 * 1000);

// --- CC Autonomous Bus Watcher ---
// CC responds only to messages explicitly addressed to cc. Karma owns the general channel.
// Uses MODEL_DEEP for peer-quality responses. Fires every 20s (offset from Karma's 15s).
let _ccWatcherLastProcessed = new Set();

async function ccWatcherTick() {
  try {
    const pending = [..._coordinationCache.values()].filter(
      e => e.to === "cc" && e.status === "pending" && e.from !== "cc"
    );
    const newEntries = pending.filter(e => !_ccWatcherLastProcessed.has(e.id));
    if (newEntries.length === 0) return;

    console.log(`[CC_WATCHER] ${newEntries.length} new message(s) — triggering headless response`);

    const msgSummary = newEntries.map(e =>
      `[FROM:${e.from} TO:${e.to}] ${e.content}`
    ).join("\n\n");

    const syntheticMsg = `COORDINATION BUS — ${newEntries.length} message(s) pending:\n\n${msgSummary}\n\nYou are CC (Claude Code), the engineering mind in this family. Respond concisely and post to the bus.`;

    for (const e of newEntries) _ccWatcherLastProcessed.add(e.id);
    if (_ccWatcherLastProcessed.size > 200) {
      const arr = [..._ccWatcherLastProcessed];
      _ccWatcherLastProcessed = new Set(arr.slice(-100));
    }

    const ccSystemPrompt = `You are CC — Claude Code, the engineering mind in the Karma family. Colby is the human operator. Family: Karma (conversational peer), Codex (auditor), KCC, Kiki, Asher. You built and maintain the hub-bridge, vault-neo, K2 services, and coordination bus. CRITICAL: You are in headless autonomous mode right now. You have NO tool access, NO shell access, and CANNOT check live system state. Do NOT claim to be checking anything. Only respond based on what's written in the bus messages. Plain conversational text only — no markdown, no timestamps. Max 2 sentences.`;

    const messages = [
      { role: "system", content: ccSystemPrompt },
      { role: "user", content: syntheticMsg },
    ];

    const result = await callLLM(env.MODEL_DEEP, messages, 150);
    const response = result?.text;
    if (!response) {
      console.warn("[CC_WATCHER] LLM returned empty response");
      return;
    }

    const id = `coord_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const entry = {
      id,
      from: "cc",
      to: "all",
      type: "inform",
      urgency: "informational",
      status: "pending",
      parent_id: newEntries[0].id,
      response_id: null,
      content: response.slice(0, 400),
      context: null,
      created_at: new Date().toISOString(),
    };
    _coordinationCache.set(id, entry);
    saveCoordinationToDisk();
    console.log(`[CC_WATCHER] CC responded autonomously: ${response.slice(0, 80)}...`);
  } catch (e) {
    console.error(`[CC_WATCHER] tick error: ${e.message}`);
  }
}

// Start CC watcher 25s after boot (offset from Karma's 15s), then every 20s
// PAUSED — cc watcher disabled until redesigned
// setTimeout(() => { ccWatcherTick(); setInterval(ccWatcherTick, 20 * 1000); }, 25 * 1000);

// --- CC Initiative Engine ---
// CC proactively monitors system state and posts to Agora without waiting for a message.
// Checks: k2 freshness, agent silence, unacknowledged messages. Fires every 3 minutes.
let _lastCCInitiativeAt = 0;
const CC_INITIATIVE_INTERVAL_MS = 10 * 60 * 1000;

async function ccInitiativeTick() {
  try {
    const now = Date.now();
    if (now - _lastCCInitiativeAt < CC_INITIATIVE_INTERVAL_MS) return;

    const entries = [..._coordinationCache.values()];

    // Who has posted recently?
    const agentLastSeen = {};
    for (const e of entries) {
      const t = new Date(e.created_at).getTime();
      if (e.from && (!agentLastSeen[e.from] || t > agentLastSeen[e.from])) {
        agentLastSeen[e.from] = t;
      }
    }

    // Agents expected to be active
    const watched = ["karma", "codex", "kcc", "kiki"];
    const SILENCE_MS = 15 * 60 * 1000;
    const silentAgents = watched.filter(a => {
      const last = agentLastSeen[a];
      return !last || (now - last) > SILENCE_MS;
    });

    // k2 freshness check
    let freshnessNote = null;
    try {
      const f = await fetchK2FreshnessStatus(true);
      if (f.ok && f.stale_context) {
        freshnessNote = `kiki_state is ${f.state_age_seconds}s old (threshold 180s) — K2 may need attention`;
      }
    } catch (_) {}

    // Build context for the LLM
    const observations = [];
    if (silentAgents.length > 0) {
      observations.push(`These agents haven't posted in over 15 minutes: ${silentAgents.join(", ")}`);
    }
    if (freshnessNote) observations.push(freshnessNote);

    // Only proceed if there's actually something to report
    if (observations.length === 0) {
      _lastCCInitiativeAt = now;
      return;
    }

    const initiativePrompt = [
      `OBSERVATIONS:\n${observations.join("\n")}`,
      "",
      "You are CC. Report this issue in 1-2 plain sentences. Be direct, no headers.",
    ].join("\n");

    const ccSystemPrompt = `You are CC — Claude Code, the engineering mind in the Karma family. Colby is the human operator (eating pancakes). Family: Karma, Codex (auditor), KCC, Kiki, Asher. You built and maintain the hub-bridge, vault-neo, K2 services. You have shell access to K2 via Aria. You proactively watch the system and speak up when you notice something worth sharing. Plain text only, no headers or formatting. Be a peer, not a report generator.`;

    const messages = [
      { role: "system", content: ccSystemPrompt },
      { role: "user", content: initiativePrompt },
    ];

    const result = await callLLM(env.MODEL_DEEP, messages, 120);
    const response = result?.text?.trim();
    if (!response || response === "PASS" || response.startsWith("PASS")) {
      _lastCCInitiativeAt = now; // still mark so we don't spam
      return;
    }

    _lastCCInitiativeAt = now;
    const id = `coord_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const entry = {
      id,
      from: "cc",
      to: "all",
      type: "inform",
      urgency: "informational",
      status: "pending",
      parent_id: null,
      response_id: null,
      content: response.slice(0, 400),
      context: null,
      created_at: new Date().toISOString(),
    };
    _coordinationCache.set(id, entry);
    saveCoordinationToDisk();
    console.log(`[CC_INITIATIVE] posted: ${response.slice(0, 80)}...`);
  } catch (e) {
    console.error(`[CC_INITIATIVE] tick error: ${e.message}`);
  }
}

// Initiative engine: start 60s after boot, then every 30s (rate-limited internally to 3min)
// PAUSED — cc initiative disabled until redesigned
// setTimeout(() => { ccInitiativeTick(); setInterval(ccInitiativeTick, 30 * 1000); }, 60 * 1000);

server.listen(PORT, "0.0.0.0", () => {
  console.log(`hub-bridge v2.12.0 listening on :${PORT}`);
});
