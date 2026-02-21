// file: /opt/seed-vault/memory_v1/compose/api/server.js
// anr-vault-api v0.3.0 (Phase 2+3 + facts endpoint)
// - GET /healthz (db ping)
// - POST /v1/memory (schema validate + append JSONL ledger)
// - GET /v1/memory/:id (scan JSONL ledger for exact id)
// - GET /v1/facts (deduplicated facts + preferences from ledger)

'use strict';

const express = require('express');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const Ajv = require('ajv');
const addFormats = require('ajv-formats');
const { nanoid } = require('nanoid');

const { Pool } = require('pg');

const PORT = process.env.PORT ? Number(process.env.PORT) : 8080;

const VERIFIER_NAME = process.env.VERIFIER_NAME || 'arknexus-vault-api';

const SCHEMA_PATH =
  process.env.SCHEMA_PATH ||
  '/opt/seed-vault/memory_v1/schema/memory.schema.v0.1.json';

const LEDGER_PATH =
  process.env.LEDGER_PATH ||
  '/opt/seed-vault/memory_v1/ledger/memory.jsonl';

const RAW_LEDGER_PATH =
  process.env.RAW_LEDGER_PATH ||
  '/opt/seed-vault/memory_v1/raw/raw.jsonl';

const PROMOTE_DIR =
  process.env.PROMOTE_DIR ||
  '/opt/seed-vault/memory_v1/checkpoints';



const ANCHOR_PATH =
  process.env.ANCHOR_PATH ||
  '/opt/seed-vault/memory_v1/session/phase1.anchor.json';


// Resurrection Lane v0.1 (host tool runner, internal-only)
const RES_PACKS_DIR = process.env.RESURRECTION_PACKS_DIR || '/opt/seed-vault/memory_v1/resurrection/packs';
const RES_QUAR_DIR  = process.env.RESURRECTION_QUARANTINE_DIR || '/opt/seed-vault/memory_v1/resurrection/quarantine';
const RES_TOOL      = process.env.RESURRECTION_TOOL || '/opt/seed-vault/memory_v1/tools/resurrection_pack_v0_1.py';
function sha256FileSync(filePath) {
  const crypto = require('crypto');
  const h = crypto.createHash('sha256');
  const fd = fs.openSync(filePath, 'r');
  try {
    const buf = Buffer.alloc(1024 * 1024);
    while (true) {
      const n = fs.readSync(fd, buf, 0, buf.length, null);
      if (!n) break;
      h.update(buf.subarray(0, n));
    }
  } finally {
    fs.closeSync(fd);
  }
  return h.digest('hex');
}

// Bounded cache for pack sha256 to avoid O(n*size) per request.
// Keyed by name|bytes|mtime. Max 200 entries; LRU-ish via insertion order.
const packShaCache = new Map();
const PACK_CACHE_MAX = 200;
function cacheGet(key) {
  if (!packShaCache.has(key)) return null;
  const v = packShaCache.get(key);
  packShaCache.delete(key);
  packShaCache.set(key, v);
  return v;
}
function cacheSet(key, value) {
  if (packShaCache.has(key)) packShaCache.delete(key);
  packShaCache.set(key, value);
  while (packShaCache.size > PACK_CACHE_MAX) {
    const first = packShaCache.keys().next().value;
    packShaCache.delete(first);
  }
}

function readRawTail(n) {
  if (!fs.existsSync(RAW_LEDGER_PATH)) return [];
  const st = fs.statSync(RAW_LEDGER_PATH);
  const MAX_BYTES = 1024 * 1024;
  const start = Math.max(0, st.size - MAX_BYTES);
  const fd = fs.openSync(RAW_LEDGER_PATH, 'r');
  let text = '';
  try {
    const buf = Buffer.alloc(st.size - start);
    fs.readSync(fd, buf, 0, buf.length, start);
    text = buf.toString('utf8');
  } finally {
    fs.closeSync(fd);
  }
  const lines = text.split('\n').map(x => x.trim()).filter(Boolean);
  const tail = lines.slice(Math.max(0, lines.length - n));
  return tail.map(ln => { try { return JSON.parse(ln); } catch (_) { return null; } }).filter(Boolean);
}

function writeJsonFileAtomic(filePath, obj) {
  ensureDirForFile(filePath);
  const tmp = filePath + '.tmp.' + Date.now();
  fs.writeFileSync(tmp, JSON.stringify(obj, null, 2) + '\n', { encoding: 'utf8' });
  fs.renameSync(tmp, filePath);
}

async function findLatestCheckpointPointer() {
  if (!fs.existsSync(LEDGER_PATH)) return null;
  return await new Promise((resolve, reject) => {
    let best = null;
    const rs = fs.createReadStream(LEDGER_PATH, { encoding: 'utf8' });
    const rl = readline.createInterface({ input: rs, crlfDelay: Infinity });
    rl.on('line', (ln) => {
      const t = (ln || '').trim();
      if (!t) return;
      let obj;
      try { obj = JSON.parse(t); } catch (_) { return; }
      if (!obj || obj.type !== 'fact') return;
      if (!obj.content || obj.content.key !== 'checkpoint_latest') return;
      const ts = obj.updated_at || obj.created_at || '';
      if (!best) { best = obj; return; }
      const bts = best.updated_at || best.created_at || '';
      if (ts > bts) best = obj;
    });
    rl.on('close', () => resolve(best));
    rl.on('error', reject);
    rs.on('error', reject);
  });
}

function safeRead(pathStr) {
  try {
    if (!fs.existsSync(pathStr)) return null;
    return fs.readFileSync(pathStr, 'utf8');
  } catch (_) { return null; }
}

function buildResumePrompt(latest, artifacts, resStatus) {
  const ck = latest && latest.content && latest.content.value ? latest.content.value : null;
  const ckid = ck && ck.checkpoint_id ? ck.checkpoint_id : null;
  let identity = null, invariants = null;
  try { identity = artifacts.identity_json ? JSON.parse(artifacts.identity_json) : null; } catch (_) {}
  try { invariants = artifacts.invariants_json ? JSON.parse(artifacts.invariants_json) : null; } catch (_) {}
  const lines = [
    '# KARMA -- RESUME (MIS+VCS)',
    'trust_level: baseline_exec_verified',
    (ck && ck.checkpoint_id ? 'checkpoint_id: ' + ck.checkpoint_id : 'checkpoint_id: (none)'),
    (ck && ck.pack_id ? 'pack_id: ' + ck.pack_id : 'pack_id: (none)'),
    (ck && ck.ledger_sha256 ? 'ledger_sha256: ' + ck.ledger_sha256 : 'ledger_sha256: (none)'),
    (ck && ck.anchor_sha256 ? 'anchor_sha256: ' + ck.anchor_sha256 : 'anchor_sha256: (none)'),
    'generated_at_utc: ' + isoNow(),
    '',
    '## MIS (Minimal Identity Snapshot)',
    identity ? JSON.stringify(identity, null, 2) : '(missing identity.json)',
    '',
    '## Invariants',
    invariants ? JSON.stringify(invariants, null, 2) : '(missing invariants.json)',
    '',
    '## Direction',
    artifacts.direction_md || '(missing direction.md)',
    '',
    '## VCS (Validated Checkpoint System)',
    ckid ? 'checkpoint_id: ' + ckid : 'checkpoint_id: (none)',
    ck && ck.path ? 'checkpoint_path: ' + ck.path : 'checkpoint_path: (none)',
    (ck && typeof ck.raw_count === 'number') ? 'raw_count: ' + ck.raw_count : '',
    '',
    '## Resurrection Status',
    resStatus ? JSON.stringify(resStatus, null, 2) : '(missing resurrection status)',
    '',
    '## Next',
    '- Paste this block into the next chat/tool to resume.',
    '- If drift occurs: PROMOTE again, then capture a pack.'
  ];
  return lines.join('\n');
}


function mustBeInternal(req, res) {
  const xff = req.headers['x-forwarded-for'];
  const rawIp = (typeof xff === 'string' && xff.trim())
    ? xff.split(',')[0].trim()
    : (req.ip || '');
  if (!isPrivateIp(rawIp)) {
    res.status(403).json({ ok: false, error: 'internal_only' });
    return false;
  }
  return true;
}

const DATABASE_URL = process.env.DATABASE_URL || process.env.POSTGRES_URL || '';

const app = express();
app.disable('x-powered-by');

// In-memory rate limiter (single-node, dual-tier).
// Public callers (external IPs): 30 req/min + 10 burst.
// Internal callers (hub-bridge on private network): 240 req/min + 120 burst.
const RL_WINDOW_MS = 60 * 1000;
const RL_RATE_PUBLIC   = Number(process.env.RL_RATE   || 30);
const RL_BURST_PUBLIC  = Number(process.env.RL_BURST  || 10);
const RL_RATE_INTERNAL = Number(process.env.RL_RATE_INTERNAL  || 240);
const RL_BURST_INTERNAL= Number(process.env.RL_BURST_INTERNAL || 120);
const rlState = new Map();

function isPrivateIp(ip) {
  if (!ip || typeof ip !== 'string') return false;
  // Strip IPv4-mapped IPv6 prefix (::ffff:) — Express/Node may use this for Docker bridge IPs
  let s = ip.trim();
  if (s.startsWith('::ffff:')) s = s.slice(7);
  // IPv4 private ranges + loopback
  if (/^127\./.test(s)) return true;
  if (/^10\./.test(s)) return true;
  if (/^172\.(1[6-9]|2\d|3[01])\./.test(s)) return true;
  if (/^192\.168\./.test(s)) return true;
  // IPv6 loopback
  if (s === '::1') return true;
  return false;
}

function pickRlLimits(req) {
  const xff = req.headers['x-forwarded-for'];
  const rawIp = (typeof xff === 'string' && xff.trim())
    ? xff.split(',')[0].trim()
    : (req.ip || '');
  if (isPrivateIp(rawIp)) {
    return { rate: RL_RATE_INTERNAL, burst: RL_BURST_INTERNAL, key: rawIp };
  }
  return { rate: RL_RATE_PUBLIC, burst: RL_BURST_PUBLIC, key: rawIp || 'unknown' };
}

function rateLimit(req, res) {
  const { rate, burst, key } = pickRlLimits(req);
  const now = Date.now();
  let st = rlState.get(key);
  if (!st) {
    st = { tokens: rate + burst, last: now };
    rlState.set(key, st);
  }

  // Refill tokens proportionally over the window
  const elapsed = now - st.last;
  if (elapsed > 0) {
    const refill = (elapsed / RL_WINDOW_MS) * rate;
    st.tokens = Math.min(rate + burst, st.tokens + refill);
    st.last = now;
  }

  if (st.tokens < 1) {
    res.status(429).json({ ok: false, error: "rate_limited" });
    return false;
  }
  st.tokens -= 1;
  return true;
}

// Garbage collect stale entries occasionally
setInterval(() => {
  const cutoff = Date.now() - (10 * RL_WINDOW_MS);
  for (const [k, st] of rlState.entries()) {
    if (st.last < cutoff) rlState.delete(k);
  }
}, 5 * RL_WINDOW_MS).unref();
app.use(express.json({ limit: '2mb' }));

function isoNow() {
  return new Date().toISOString();
}

function ensureDirForFile(filePath) {
  const dir = path.dirname(filePath);
  fs.mkdirSync(dir, { recursive: true });
}

function acquireLock(lockPath, timeoutMs) {
  const start = Date.now();
  while (true) {
    try {
      const fd = fs.openSync(lockPath, 'wx');
      return fd;
    } catch (e) {
      if (e && e.code !== 'EEXIST') throw e;
      if (Date.now() - start > timeoutMs) {
        const err = new Error('lock_timeout');
        err.code = 'LOCK_TIMEOUT';
        throw err;
      }
      // sleep ~25ms
      const end = Date.now() + 25;
      while (Date.now() < end) {}
    }
  }
}

function releaseLock(fd, lockPath) {
  try { if (typeof fd === 'number') fs.closeSync(fd); } catch (_) {}
  try { fs.unlinkSync(lockPath); } catch (_) {}
}

function readSchemaOrThrow() {
  const raw = fs.readFileSync(SCHEMA_PATH, 'utf8');
  return JSON.parse(raw);
}

const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);

let validateMemory;
try {
  const schema = readSchemaOrThrow();
  validateMemory = ajv.compile(schema);
} catch (e) {
  console.error('FATAL: schema load/compile failed:', e && e.message ? e.message : e);
  process.exit(1);
}

let pool = null;
if (DATABASE_URL) {
  pool = new Pool({ connectionString: DATABASE_URL });
}


app.get('/livez', (req, res) => {
  // No auth, no secrets: pure liveness for external monitors
  return res.status(200).send('ok');
});

app.get('/healthz', async (req, res) => {
  try {
    if (!pool) {
      return res.status(200).json({ ok: true, db: 'skipped' });
    }
    const r = await pool.query('select 1 as ok');
    const ok = r && r.rows && r.rows[0] && r.rows[0].ok === 1;
    return res.status(200).json({ ok: true, db: ok ? 'ok' : 'unknown' });
  } catch (e) {
    return res.status(500).json({ ok: false, db: 'error', error: String(e && e.message ? e.message : e) });
  }
});

app.get('/v1/memory/:id', async (req, res) => {
  try {
    const id = req.params.id;
    if (!id || typeof id !== 'string' || id.length < 8 || id.length > 128) {
      return res.status(400).json({ ok: false, error: 'invalid_id' });
    }

    if (!fs.existsSync(LEDGER_PATH)) {
      return res.status(404).json({ ok: false, error: 'ledger_not_found' });
    }

    const rl = readline.createInterface({
      input: fs.createReadStream(LEDGER_PATH, { encoding: 'utf8' }),
      crlfDelay: Infinity
    });

    for await (const line of rl) {
      const t = (line || '').trim();
      if (!t) continue;
      try {
        const obj = JSON.parse(t);
        if (obj && obj.id === id) {
          rl.close();
          return res.status(200).json({ ok: true, memory: obj });
        }
      } catch (_) {
        // skip malformed line, keep scanning
      }
    }

    return res.status(404).json({ ok: false, error: 'not_found' });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'server_error', details: String(e && e.message ? e.message : e) });
  }
});


// BOOTSTRAP_TAIL_V0_1 -- bounded tail scan, no full readFileSync
app.get('/v1/bootstrap', async (req, res) => {
  try {
    const n = Math.min(parseInt(req.query.n || '20', 10), 200);
    const ledgerPath = LEDGER_PATH;

    // --- 1. Tail: read last 1 MB for recent entries ---
    const TAIL_BYTES = 1 * 1024 * 1024;
    let tailLines = [];
    let fileSize = 0;
    try {
      const stat = fs.statSync(ledgerPath);
      fileSize = stat.size;
      const readBytes = Math.min(TAIL_BYTES, fileSize);
      const buf = Buffer.alloc(readBytes);
      const fd = fs.openSync(ledgerPath, 'r');
      fs.readSync(fd, buf, 0, readBytes, fileSize - readBytes);
      fs.closeSync(fd);
      const raw = buf.toString('utf8');
      const allLines = raw.split('\n').filter(l => l.trim());
      tailLines = (fileSize > TAIL_BYTES) ? allLines.slice(1) : allLines;
    } catch (e) {
      return res.json({ ok: true, entries: [], lineCount: 0, tailBytes: 0, fileSize: 0, note: 'ledger_unreadable' });
    }

    // --- 2. Stream full file for accurate lineCount ---
    const lineCount = await new Promise((resolve, reject) => {
      let count = 0;
      const rl = require('readline').createInterface({
        input: require('fs').createReadStream(ledgerPath),
        crlfDelay: Infinity
      });
      rl.on('line', line => { if (line.trim()) count++; });
      rl.on('close', () => resolve(count));
      rl.on('error', reject);
    });

    // --- 3. Parse + return last n entries ---
    const parsed = [];
    for (const line of tailLines) {
      try { parsed.push(JSON.parse(line)); } catch (_) {}
    }
    const entries = parsed.slice(-n);

    res.json({ ok: true, entries, lineCount, tailBytes: Math.min(TAIL_BYTES, fileSize), fileSize });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});




// STREAMING_FACTS_V0_1
app.get('/v1/facts', async (req, res) => {
  try {
    if (!fs.existsSync(LEDGER_PATH)) {
      return res.status(200).json({ ok: true, facts: [], preferences: [], meta: { count: 0, generated_at: isoNow() } });
    }
    // Streaming scan (bounded memory): read JSONL line-by-line
    const factMap = new Map();
    const prefMap = new Map();
    let ledger_lines = 0;
    const rs = fs.createReadStream(LEDGER_PATH, { encoding: 'utf8' });
    const rl = readline.createInterface({ input: rs, crlfDelay: Infinity });
    rl.on('line', (ln) => {
      const t = (ln || '').trim();
      if (!t) return;
      ledger_lines += 1;
      let obj;
      try { obj = JSON.parse(t); } catch (_) { return; }
      if (obj.verification && obj.verification.status === 'deprecated') return;
      const typ = obj.type;
      const key = obj.content && obj.content.key;
      if (!key) return;
      if (typ === 'fact') {
        const existing = factMap.get(key);
        if (!existing || (obj.updated_at || '') > (existing.updated_at || '')) {
          factMap.set(key, obj);
        }
      } else if (typ === 'preference') {
        const existing = prefMap.get(key);
        if (!existing || (obj.updated_at || '') > (existing.updated_at || '')) {
          prefMap.set(key, obj);
        }
      }
    });
    rl.on('close', () => {
      const facts = Array.from(factMap.values()).map(e => ({
        key: e.content.key,
        value: e.content.value,
        id: e.id,
        updated_at: e.updated_at,
        source: e.source
      }));
      const preferences = Array.from(prefMap.values()).map(e => ({
        key: e.content.key,
        value: e.content.value,
        id: e.id,
        updated_at: e.updated_at,
        source: e.source
      }));
      return res.status(200).json({
        ok: true,
        facts,
        preferences,
        meta: {
          count: facts.length + preferences.length,
          facts_count: facts.length,
          preferences_count: preferences.length,
          ledger_lines,
          generated_at: isoNow()
        }
      });
    });
    rl.on('error', (e) => {
      return res.status(500).json({ ok: false, error: 'server_error', details: String(e && e.message ? e.message : e) });
    });
    rs.on('error', (e) => {
      return res.status(500).json({ ok: false, error: 'server_error', details: String(e && e.message ? e.message : e) });
    });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'server_error', details: String(e && e.message ? e.message : e) });
  }
});



app.post('/v1/memory', async (req, res) => {
  if (!rateLimit(req, res)) return;
  try {
    const body = req.body;

    if (!body || typeof body !== 'object' || Array.isArray(body)) {
      return res.status(400).json({ ok: false, error: 'invalid_json_body' });
    }

    if (!body.id) body.id = `mem_${nanoid(16)}`;
    const now = isoNow();
    if (!body.created_at) body.created_at = now;
    if (!body.updated_at) body.updated_at = now;

    if (body.verification && typeof body.verification === 'object') {
      if (!body.verification.verified_at) body.verification.verified_at = now;
      if (!body.verification.verifier) body.verification.verifier = VERIFIER_NAME;
    }

    const ok = validateMemory(body);
    if (!ok) {
      return res.status(422).json({
        ok: false,
        error: 'schema_validation_failed',
        details: validateMemory.errors || []
      });
    }

    ensureDirForFile(LEDGER_PATH);

    const line = JSON.stringify(body);
    // Locked append to prevent interleaved writes under concurrency
const lockPath = LEDGER_PATH + '.lock';
const lockFd = acquireLock(lockPath, 2000);
try {
  fs.appendFileSync(LEDGER_PATH, line + '\n', { encoding: 'utf8' });
} finally {
  releaseLock(lockFd, lockPath);
}

    return res.status(201).json({ ok: true, id: body.id });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'ledger_write_failed', details: String(e && e.message ? e.message : e) });
  }
});


// Resurrection Lane v0.1 --- list packs (internal-only)

// Resurrection Lane v0.1 --- status snapshot (internal-only)

// Raw Lane v0.1 (internal-only): append-only capture stream
app.post('/v1/raw', async (req, res) => {
  if (!rateLimit(req, res)) return;
  if (!mustBeInternal(req, res)) return;
  try {
    const body = req.body;
    if (!body || typeof body !== 'object' || Array.isArray(body)) {
      return res.status(400).json({ ok: false, error: 'invalid_json_body' });
    }
    const now = isoNow();
    const rec = {
      id: body.id || 'raw_' + nanoid(16),
      ts: body.ts || now,
      kind: body.kind || 'artifact',
      source: body.source || { kind: 'unknown', ref: 'unknown' },
      tags: Array.isArray(body.tags) ? body.tags.slice(0, 25) : [],
      payload: body.payload || body,
      note: typeof body.note === 'string' ? body.note.slice(0, 2000) : undefined
    };
    ensureDirForFile(RAW_LEDGER_PATH);
    const line = JSON.stringify(rec);
    const lockPath = RAW_LEDGER_PATH + '.lock';
    const lockFd = acquireLock(lockPath, 2000);
    try {
      fs.appendFileSync(RAW_LEDGER_PATH, line + '\n', { encoding: 'utf8' });
    } finally {
      releaseLock(lockFd, lockPath);
    }
    return res.status(201).json({ ok: true, id: rec.id });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'raw_write_failed',
      details: String(e && e.message ? e.message : e) });
  }
});

// Raw Lane v0.1 (internal-only): tail last N raw records (bounded 1 MB)
app.get('/v1/raw/tail', async (req, res) => {
  if (!rateLimit(req, res)) return;
  if (!mustBeInternal(req, res)) return;
  try {
    const nRaw = req.query && req.query.n;
    let n = 50;
    if (typeof nRaw === 'string') {
      const v = Number(nRaw);
      if (Number.isFinite(v)) n = Math.max(1, Math.min(200, Math.floor(v)));
    }
    if (!fs.existsSync(RAW_LEDGER_PATH)) {
      return res.status(200).json({ ok: true, records: [],
        meta: { n, count: 0, generated_at: isoNow() } });
    }
    const st = fs.statSync(RAW_LEDGER_PATH);
    const MAX_BYTES = 1024 * 1024;
    const start = Math.max(0, st.size - MAX_BYTES);
    const fd = fs.openSync(RAW_LEDGER_PATH, 'r');
    let text = '';
    try {
      const buf = Buffer.alloc(st.size - start);
      fs.readSync(fd, buf, 0, buf.length, start);
      text = buf.toString('utf8');
    } finally {
      fs.closeSync(fd);
    }
    const lines = text.split('\n').map(x => x.trim()).filter(Boolean);
    const tail = lines.slice(Math.max(0, lines.length - n));
    const records = tail.map(ln => {
      try { return JSON.parse(ln); } catch (_) { return null; }
    }).filter(Boolean);
    return res.status(200).json({ ok: true, records,
      meta: { n, count: records.length, generated_at: isoNow() } });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'raw_tail_failed',
      details: String(e && e.message ? e.message : e) });
  }
});


// PROMOTE v0.1 (internal-only): distill Raw->Candidate->Canonical
app.post('/v1/promote', async (req, res) => {
  if (!rateLimit(req, res)) return;
  if (!mustBeInternal(req, res)) return;
  try {
    const body = req.body && typeof req.body === 'object' ? req.body : {};
    const n = Number.isFinite(Number(body.n))
      ? Math.max(1, Math.min(200, Math.floor(Number(body.n)))) : 50;
    const reason = typeof body.reason === 'string' ? body.reason.slice(0, 400) : 'promote';
    const raw = readRawTail(n);
    const tsStr = isoNow().replace(/[:-]/g, '').slice(0, 15);
    const checkpoint_id = 'ckpt_' + tsStr + '_' + nanoid(6);
    const baseDir = path.join(PROMOTE_DIR, checkpoint_id);
    const checkpoint = {
      checkpoint_id,
      created_at: isoNow(),
      reason,
      raw_count: raw.length,
      raw_tail: raw,
      notes: 'v0.2: raw tail captured; core identity+invariants copied; direction stub written.',
      verification: { status: 'pending' }
    };
    writeJsonFileAtomic(path.join(baseDir, 'checkpoint.json'), checkpoint);
    // v0.2: copy bounded core identity + invariants into checkpoint
    fs.copyFileSync('/opt/seed-vault/memory_v1/core/identity.json', path.join(baseDir, 'identity.json'));
    fs.copyFileSync('/opt/seed-vault/memory_v1/core/invariants.json', path.join(baseDir, 'invariants.json'));
    const next_action = typeof body.next_action === 'string' ? body.next_action.slice(0, 400) : '';
    const dirContent = '# direction' + '\n\n' + '- created_at: ' + isoNow() + '\n' + '- reason: ' + reason + '\n' + '- checkpoint_id: ' + checkpoint_id + '\n\n' + '## next_action' + '\n' + (next_action || '(none)') + '\n';
    fs.writeFileSync(path.join(baseDir, 'direction.md'), dirContent, { encoding: 'utf8' });
    // Commit verified ledger fact
    const mem = {
      type: 'fact',
      content: { key: 'checkpoint_latest', value: {
        checkpoint_id, path: baseDir, created_at: isoNow(),
        raw_count: raw.length, reason } },
      tags: ['checkpoint', 'promote', 'vcs', 'milestone'],
      source: { kind: 'system', ref: 'anr-vault-api:/v1/promote' },
      confidence: 0.9,
      verification: {
        protocol_version: 'memory_v0.1',
        verified_at: isoNow(),
        verifier: 'promote_v0.2',
        status: 'verified',
        notes: 'PROMOTE v0.1: checkpoint artifacts written, pointer recorded.'
      }
    };
    mem.id = 'mem_' + nanoid(16);
    const now = isoNow();
    mem.created_at = now;
    mem.updated_at = now;
    const valid = validateMemory(mem);
    if (!valid) {
      return res.status(500).json({ ok: false, error: 'promote_schema_failed',
        details: validateMemory.errors || [] });
    }
    // Run resurrection capture FIRST so proof refs can be sealed into ledger fact
    let capture = null;
    try {
      const { spawnSync } = require('child_process');
      const r = spawnSync('python3', [RES_TOOL, 'capture'],
        { encoding: 'utf8', timeout: 300000 });
      if (r.status === 0) {
        try { capture = JSON.parse(r.stdout); } catch (_) { capture = { raw: r.stdout }; }
      } else {
        capture = { ok: false, details: String((r.stderr || r.stdout || '')).slice(0, 1000) };
      }
    } catch (e) {
      capture = { ok: false, details: String(e && e.message ? e.message : e) };
    }
    // Inject proof refs from capture into checkpoint_latest fact value
    try {
      if (capture && capture.ok) {
        if (capture.pack_id) mem.content.value.pack_id = capture.pack_id;
        if (capture.meta && capture.meta.sha256) {
          mem.content.value.ledger_sha256 = capture.meta.sha256.ledger || null;
          mem.content.value.anchor_sha256 = capture.meta.sha256.anchor || null;
        }
      }
    } catch (_) {}
    // Now write the sealed fact to ledger
    ensureDirForFile(LEDGER_PATH);
    const ledgerLine = JSON.stringify(mem);
    const lLockPath = LEDGER_PATH + '.lock';
    const lLockFd = acquireLock(lLockPath, 2000);
    try { fs.appendFileSync(LEDGER_PATH, ledgerLine + '\n', { encoding: 'utf8' }); }
    finally { releaseLock(lLockFd, lLockPath); }
    return res.status(200).json({
      ok: true, checkpoint_id, checkpoint_path: baseDir,
      raw_count: raw.length, ledger_id: mem.id, capture
    });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'promote_failed',
      details: String(e && e.message ? e.message : e) });
  }
});


// Checkpoint latest v0.1 (internal-only): pointer + artifacts + resume prompt
app.get('/v1/checkpoint/latest', async (req, res) => {
  if (!rateLimit(req, res)) return;
  if (!mustBeInternal(req, res)) return;
  try {
    const latest = await findLatestCheckpointPointer();
    const ck = latest && latest.content && latest.content.value ? latest.content.value : null;
    const baseDir = ck && ck.path ? ck.path : null;
    const artifacts = {
      checkpoint_json: baseDir ? safeRead(path.join(baseDir, 'checkpoint.json')) : null,
      identity_json:   baseDir ? safeRead(path.join(baseDir, 'identity.json'))   : null,
      invariants_json: baseDir ? safeRead(path.join(baseDir, 'invariants.json')) : null,
      direction_md:    baseDir ? safeRead(path.join(baseDir, 'direction.md'))    : null
    };
    fs.mkdirSync(RES_PACKS_DIR, { recursive: true });
    fs.mkdirSync(RES_QUAR_DIR, { recursive: true });
    const packs = fs.readdirSync(RES_PACKS_DIR).filter(n => n.endsWith('.tar.gz')).sort().reverse();
    const quarantine = fs.readdirSync(RES_QUAR_DIR)
      .filter(n => n.includes('.quarantine.') || n.includes('.pruned.'))
      .sort().reverse();
    const resStatus = {
      paths: { packs_dir: RES_PACKS_DIR, quarantine_dir: RES_QUAR_DIR },
      counts: { packs: packs.length, quarantine: quarantine.length },
      latest: packs.length ? { name: packs[0] } : null
    };
    const resume_prompt = buildResumePrompt(latest, artifacts, resStatus);

    // Autonomous continuity: find karma_brief stored during last PROMOTE.
    // hub-bridge injects this into Karma's system prompt on every chat turn.
    const ckId = ck && ck.checkpoint_id ? ck.checkpoint_id : null;
    let karma_brief = null;
    if (ckId && fs.existsSync(LEDGER_PATH)) {
      karma_brief = await new Promise((resolve) => {
        let found = null;
        const rs2 = fs.createReadStream(LEDGER_PATH, { encoding: 'utf8' });
        const rl2 = readline.createInterface({ input: rs2, crlfDelay: Infinity });
        rl2.on('line', (ln) => {
          const t = (ln || '').trim();
          if (!t) return;
          let obj;
          try { obj = JSON.parse(t); } catch (_) { return; }
          if (!obj || !Array.isArray(obj.tags)) return;
          if (!obj.tags.includes('karma_brief')) return;
          if (obj.content && obj.content.checkpoint_id === ckId) {
            found = obj.content.karma_brief || null;
          }
        });
        rl2.on('close', () => resolve(found));
        rl2.on('error', () => resolve(null));
        rs2.on('error', () => resolve(null));
      });
    }

    // Distillation brief: most recent karma_distillation entry in the ledger.
    // No checkpoint_id filter — always the latest synthesis Karma wrote.
    let distillation_brief = null;
    if (fs.existsSync(LEDGER_PATH)) {
      distillation_brief = await new Promise((resolve) => {
        let found = null;
        const rs3 = fs.createReadStream(LEDGER_PATH, { encoding: 'utf8' });
        const rl3 = readline.createInterface({ input: rs3, crlfDelay: Infinity });
        rl3.on('line', (ln) => {
          const t = (ln || '').trim();
          if (!t) return;
          let obj;
          try { obj = JSON.parse(t); } catch (_) { return; }
          if (!obj || !Array.isArray(obj.tags)) return;
          if (!obj.tags.includes('karma_distillation')) return;
          if (obj.content && obj.content.distillation_brief) {
            found = obj.content.distillation_brief;
          }
        });
        rl3.on('close', () => resolve(found));
        rl3.on('error', () => resolve(null));
        rs3.on('error', () => resolve(null));
      });
    }

    return res.status(200).json({
      ok: true,
      latest_checkpoint_fact: latest || null,
      artifacts,
      resume_prompt,
      karma_brief,
      distillation_brief,
      meta: { generated_at: isoNow() }
    });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'checkpoint_latest_failed',
      details: String(e && e.message ? e.message : e) });
  }
});

app.get('/v1/resurrection/status', async (req, res) => {
  if (!rateLimit(req, res)) return;
  if (!mustBeInternal(req, res)) return;
  try {
    fs.mkdirSync(RES_PACKS_DIR, { recursive: true });
    fs.mkdirSync(RES_QUAR_DIR, { recursive: true });
    const packs = fs.readdirSync(RES_PACKS_DIR).filter(n => n.endsWith('.tar.gz')).sort().reverse();
    const quarantine = fs.readdirSync(RES_QUAR_DIR).filter(n => n.includes('.quarantine.') || n.includes('.pruned.')).sort().reverse();
    const latest_name = packs.length ? packs[0] : null;
    return res.status(200).json({
      ok: true,
      paths: {
        ledger: LEDGER_PATH,
        anchor: ANCHOR_PATH,
        packs_dir: RES_PACKS_DIR,
        quarantine_dir: RES_QUAR_DIR,
        tool: RES_TOOL
      },
      counts: {
        packs: packs.length,
        quarantine: quarantine.length
      },
      latest: latest_name ? { name: latest_name } : null,
      retention_default: 30,
      meta: { generated_at: isoNow() }
    });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'resurrection_status_failed', details: String(e && e.message ? e.message : e) });
  }
});

app.get('/v1/resurrection/packs', async (req, res) => {
  if (!rateLimit(req, res)) return;
  if (!mustBeInternal(req, res)) return;
  try {
    ensureDirForFile(RES_PACKS_DIR + '/.keep');
    
    let cache_hits = 0;
    let cache_misses = 0;
    const entries = fs.readdirSync(RES_PACKS_DIR)
      .filter(n => n.endsWith('.tar.gz'))
      .map(n => {
        const fp = path.join(RES_PACKS_DIR, n);
        const st = fs.statSync(fp);
        const mtime = st.mtime.toISOString();
        const key = n + '|' + st.size + '|' + mtime;
        let sha = cacheGet(key);
        if (sha) {
          cache_hits += 1;
        } else {
          cache_misses += 1;
          sha = sha256FileSync(fp);
          cacheSet(key, sha);
        }
        return { name: n, bytes: st.size, mtime, sha256: sha };
      })
      .sort((a, b) => (a.mtime < b.mtime ? 1 : -1));

    return res.status(200).json({ ok: true, packs: entries, meta: { count: entries.length, generated_at: isoNow(), cache_hits, cache_misses, cache_size: packShaCache.size } });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'resurrection_list_failed', details: String(e && e.message ? e.message : e) });
  }
});

// Resurrection Lane v0.1 --- capture pack via host tool (internal-only)
app.post('/v1/resurrection/capture', async (req, res) => {
  if (!rateLimit(req, res)) return;
  if (!mustBeInternal(req, res)) return;
  try {
    const { spawnSync } = require('child_process');
    const packId = (req.body && typeof req.body === 'object') ? (req.body.pack_id || null) : null;
    const args = [RES_TOOL, 'capture'];
    if (packId && typeof packId === 'string' && packId.length < 128) {
      args.push('--pack-id', packId);
    }
    const r = spawnSync('python3', args, { encoding: 'utf8', timeout: 300000 });
    if (r.error) {
      return res.status(500).json({ ok: false, error: 'resurrection_capture_failed', details: String(r.error) });
    }
    if (r.status !== 0) {
      return res.status(500).json({ ok: false, error: 'resurrection_capture_failed', details: String(r.stderr || r.stdout || '').slice(0, 4000) });
    }
    let out = null;
    try { out = JSON.parse(r.stdout); } catch (_) { out = { raw: r.stdout }; }
    return res.status(200).json({ ok: true, result: out });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'resurrection_capture_failed', details: String(e && e.message ? e.message : e) });
  }
});


// Resurrection Lane v0.1 --- verify a pack (internal-only). On failure, quarantine.
app.post('/v1/resurrection/verify', async (req, res) => {
  if (!rateLimit(req, res)) return;
  if (!mustBeInternal(req, res)) return;
  try {
    const name = req.body && typeof req.body === 'object' ? req.body.name : null;
    if (!name || typeof name !== 'string' || !name.endsWith('.tar.gz') || name.includes('/') || name.includes('..')) {
      return res.status(400).json({ ok: false, error: 'invalid_pack_name' });
    }
    fs.mkdirSync(RES_PACKS_DIR, { recursive: true });
    fs.mkdirSync(RES_QUAR_DIR, { recursive: true });
    const src = path.join(RES_PACKS_DIR, name);
    if (!fs.existsSync(src)) {
      return res.status(404).json({ ok: false, error: 'pack_not_found' });
    }
    const { spawnSync } = require('child_process');
    const args = [RES_TOOL, 'verify', src];
    const r = spawnSync('python3', args, { encoding: 'utf8', timeout: 300000 });
    if (r.error || r.status !== 0) {
      const qname = name + '.quarantine.' + Date.now();
      const dst = path.join(RES_QUAR_DIR, qname);
      try { fs.renameSync(src, dst); } catch (_) {}
      const msg = String(r.stderr || r.stdout || r.error || '').slice(0, 4000);
      return res.status(200).json({ ok: false, verified: false, quarantined: true, quarantine_name: qname, details: msg });
    }
    let out = null;
    try { out = JSON.parse(r.stdout); } catch (_) { out = { raw: r.stdout }; }
    return res.status(200).json({ ok: true, verified: true, result: out });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'resurrection_verify_failed', details: String(e && e.message ? e.message : e) });
  }
});


// Resurrection Lane v0.1 --- prune packs by retention policy (internal-only).
// Keeps newest N packs in RES_PACKS_DIR; moves older packs to RES_QUAR_DIR (no deletion).
app.post('/v1/resurrection/prune', async (req, res) => {
  if (!rateLimit(req, res)) return;
  if (!mustBeInternal(req, res)) return;
  try {
    const body = req.body && typeof req.body === 'object' ? req.body : {};
    const keep = Number.isFinite(Number(body.keep)) ? Math.max(1, Math.min(200, Number(body.keep))) : 30;
    const dry_run = body.dry_run === true;
    fs.mkdirSync(RES_PACKS_DIR, { recursive: true });
    fs.mkdirSync(RES_QUAR_DIR, { recursive: true });
    const packs = fs.readdirSync(RES_PACKS_DIR)
      .filter(n => n.endsWith('.tar.gz'))
      .map(n => {
        const fp = path.join(RES_PACKS_DIR, n);
        const st = fs.statSync(fp);
        return { name: n, fp, mtime: st.mtime.getTime(), bytes: st.size };
      })
      .sort((a, b) => (a.mtime < b.mtime ? 1 : -1));
    const keepSet = new Set(packs.slice(0, keep).map(pk => pk.name));
    const toMove = packs.filter(pk => !keepSet.has(pk.name));
    let moved = 0;
    const moved_names = [];
    for (const pk of toMove) {
      const qname = pk.name + '.pruned.' + Date.now();
      const dst = path.join(RES_QUAR_DIR, qname);
      if (!dry_run) {
        try { fs.renameSync(pk.fp, dst); moved += 1; moved_names.push(qname); } catch (_) {}
      } else {
        moved_names.push(qname);
      }
    }
    try { packShaCache.clear(); } catch (_) {}
    return res.status(200).json({
      ok: true,
      keep,
      dry_run,
      total_before: packs.length,
      kept: Math.min(keep, packs.length),
      moved: (dry_run ? toMove.length : moved),
      moved_names: moved_names.slice(0, 50),
      meta: { generated_at: isoNow() }
    });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'resurrection_prune_failed', details: String(e && e.message ? e.message : e) });
  }
});

// Phase 2: Search proxy endpoint
// Forwards search requests to Python search service
app.post('/v1/search', async (req, res) => {
  if (!rateLimit(req, res)) return;
  
  try {
    const searchUrl = 'http://search:8081/v1/search';
    
    // Forward request to Python search service
    const response = await fetch(searchUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(req.body)
    });
    
    if (!response.ok) {
      const error = await response.json();
      return res.status(response.status).json(error);
    }
    
    const searchResults = await response.json();
    return res.status(200).json(searchResults);
    
  } catch (e) {
    return res.status(500).json({ 
      ok: false, 
      error: 'search_service_unavailable', 
      details: String(e && e.message ? e.message : e) 
    });
  }
});

// Phase 2: Reindex endpoint
app.post('/v1/reindex', async (req, res) => {
  if (!rateLimit(req, res)) return;
  
  try {
    const reindexUrl = 'http://search:8081/v1/reindex';
    const response = await fetch(reindexUrl, { method: 'POST' });
    
    if (!response.ok) {
      const error = await response.json();
      return res.status(response.status).json(error);
    }
    
    const result = await response.json();
    return res.status(200).json(result);
    
  } catch (e) {
    return res.status(500).json({ 
      ok: false, 
      error: 'search_service_unavailable', 
      details: String(e && e.message ? e.message : e) 
    });
  }
});

app.listen(PORT, () => {
  console.log(`anr-vault-api listening on :${PORT}`);
  console.log(`schema: ${SCHEMA_PATH}`);
  console.log(`ledger: ${LEDGER_PATH}`);
});
