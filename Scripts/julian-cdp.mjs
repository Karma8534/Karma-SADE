#!/usr/bin/env node
/**
 * julian-cdp.mjs — Julian's browser control via Chrome DevTools Protocol
 * Windows-native. Zero dependencies. Node 22+.
 *
 * Usage:
 *   node julian-cdp.mjs list                    — show all tabs
 *   node julian-cdp.mjs snap <id>               — accessibility tree
 *   node julian-cdp.mjs eval <id> "js code"     — execute JS in tab
 *   node julian-cdp.mjs nav <id> <url>          — navigate tab
 *   node julian-cdp.mjs shot <id> [file]        — screenshot
 *   node julian-cdp.mjs html <id> [selector]    — get HTML
 *   node julian-cdp.mjs click <id> "selector"   — click element
 *   node julian-cdp.mjs type <id> "text"        — type text
 *   node julian-cdp.mjs open [url]              — new tab
 *   node julian-cdp.mjs idb <id> <dbname>       — dump IndexedDB
 *
 * Port: reads CDP_PORT env or defaults to 9222
 */
import { WebSocket } from 'node:net';
import { writeFileSync } from 'node:fs';

const PORT = process.env.CDP_PORT || 9222;
const BASE = `http://127.0.0.1:${PORT}`;

// --- HTTP helpers ---
async function cdpGet(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`CDP HTTP ${res.status} on ${path}`);
  return res.json();
}

async function cdpPut(path, body) {
  const res = await fetch(`${BASE}${path}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return res.json();
}

// --- WebSocket CDP session ---
function connectTab(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new globalThis.WebSocket(wsUrl);
    let id = 1;
    const pending = new Map();

    ws.onopen = () => resolve({
      send(method, params = {}) {
        return new Promise((res, rej) => {
          const msgId = id++;
          pending.set(msgId, { res, rej });
          ws.send(JSON.stringify({ id: msgId, method, params }));
        });
      },
      close() { ws.close(); }
    });

    ws.onmessage = (evt) => {
      const msg = JSON.parse(evt.data);
      if (msg.id && pending.has(msg.id)) {
        const { res, rej } = pending.get(msg.id);
        pending.delete(msg.id);
        if (msg.error) rej(new Error(msg.error.message));
        else res(msg.result);
      }
    };

    ws.onerror = (e) => reject(new Error(`WebSocket error: ${e.message || 'connection failed'}`));
    setTimeout(() => reject(new Error('WebSocket connect timeout (5s)')), 5000);
  });
}

// --- Tab resolution ---
async function listTabs() {
  const targets = await cdpGet('/json');
  return targets.filter(t => t.type === 'page');
}

async function resolveTab(prefix) {
  const tabs = await listTabs();
  if (!prefix) {
    if (tabs.length === 0) throw new Error('No tabs open');
    return tabs[0];
  }
  const matches = tabs.filter(t => t.id.startsWith(prefix));
  if (matches.length === 0) throw new Error(`No tab matching "${prefix}". Use 'list' to see tabs.`);
  if (matches.length > 1) throw new Error(`Ambiguous prefix "${prefix}" matches ${matches.length} tabs. Use more chars.`);
  return matches[0];
}

// --- Commands ---
async function cmdList() {
  const tabs = await listTabs();
  if (tabs.length === 0) { console.log('No tabs open.'); return; }
  for (const t of tabs) {
    const prefix = t.id.substring(0, 8);
    const title = (t.title || '').substring(0, 60);
    console.log(`${prefix}  ${title.padEnd(62)} ${t.url}`);
  }
}

async function cmdSnap(prefix) {
  const tab = await resolveTab(prefix);
  const ws = await connectTab(tab.webSocketDebuggerUrl);
  await ws.send('Accessibility.enable');
  const { nodes } = await ws.send('Accessibility.getFullAXTree');
  ws.close();

  // Compact tree: filter noise, show role + name
  for (const n of nodes) {
    const role = n.role?.value || '';
    const name = n.name?.value || '';
    if (!role || role === 'none' || role === 'generic' || role === 'InlineTextBox') continue;
    if (!name && !['document', 'main', 'navigation', 'banner', 'contentinfo'].includes(role)) continue;
    const indent = '  '.repeat(Math.min(n.depth || 0, 10));
    console.log(`${indent}[${role}] ${name}`);
  }
}

async function cmdEval(prefix, expr) {
  const tab = await resolveTab(prefix);
  const ws = await connectTab(tab.webSocketDebuggerUrl);
  const result = await ws.send('Runtime.evaluate', {
    expression: expr,
    returnByValue: true,
    awaitPromise: true,
  });
  ws.close();
  if (result.exceptionDetails) {
    console.error('ERROR:', result.exceptionDetails.text || result.exceptionDetails.exception?.description);
    process.exit(1);
  }
  const val = result.result?.value;
  console.log(typeof val === 'object' ? JSON.stringify(val, null, 2) : String(val));
}

async function cmdNav(prefix, url) {
  const tab = await resolveTab(prefix);
  const ws = await connectTab(tab.webSocketDebuggerUrl);
  await ws.send('Page.enable');
  await ws.send('Page.navigate', { url });
  // Wait for load
  await new Promise(r => setTimeout(r, 3000));
  ws.close();
  console.log(`Navigated ${tab.id.substring(0, 8)} to ${url}`);
}

async function cmdShot(prefix, file) {
  const tab = await resolveTab(prefix);
  const ws = await connectTab(tab.webSocketDebuggerUrl);
  const { data } = await ws.send('Page.captureScreenshot', { format: 'png' });
  ws.close();
  const outFile = file || `screenshot-${Date.now()}.png`;
  writeFileSync(outFile, Buffer.from(data, 'base64'));
  console.log(`Screenshot saved: ${outFile}`);
}

async function cmdHtml(prefix, selector) {
  const tab = await resolveTab(prefix);
  const ws = await connectTab(tab.webSocketDebuggerUrl);
  const expr = selector
    ? `document.querySelector(${JSON.stringify(selector)})?.outerHTML || 'NOT FOUND'`
    : `document.documentElement.outerHTML`;
  const result = await ws.send('Runtime.evaluate', { expression: expr, returnByValue: true });
  ws.close();
  console.log(result.result?.value || 'ERROR');
}

async function cmdClick(prefix, selector) {
  const tab = await resolveTab(prefix);
  const ws = await connectTab(tab.webSocketDebuggerUrl);
  await ws.send('Runtime.evaluate', {
    expression: `document.querySelector(${JSON.stringify(selector)})?.scrollIntoView({block:'center'})`,
    awaitPromise: true,
  });
  await ws.send('Runtime.evaluate', {
    expression: `document.querySelector(${JSON.stringify(selector)})?.click()`,
    awaitPromise: true,
  });
  ws.close();
  console.log(`Clicked: ${selector}`);
}

async function cmdType(prefix, text) {
  const tab = await resolveTab(prefix);
  const ws = await connectTab(tab.webSocketDebuggerUrl);
  await ws.send('Input.insertText', { text });
  ws.close();
  console.log(`Typed: ${text.substring(0, 40)}${text.length > 40 ? '...' : ''}`);
}

async function cmdOpen(url) {
  const result = await cdpGet(`/json/new?${url || 'about:blank'}`);
  console.log(`Opened: ${result.id?.substring(0, 8)} ${result.url}`);
}

async function cmdIdb(prefix, dbName) {
  const tab = await resolveTab(prefix);
  const ws = await connectTab(tab.webSocketDebuggerUrl);
  const expr = `
    (async () => {
      const db = await new Promise((res, rej) => {
        const req = indexedDB.open(${JSON.stringify(dbName)});
        req.onsuccess = () => res(req.result);
        req.onerror = () => rej(req.error);
      });
      const stores = Array.from(db.objectStoreNames);
      const result = {};
      for (const storeName of stores) {
        const tx = db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const all = await new Promise((res, rej) => {
          const req = store.getAll();
          req.onsuccess = () => res(req.result);
          req.onerror = () => rej(req.error);
        });
        result[storeName] = { count: all.length, sample: all.slice(0, 3) };
      }
      db.close();
      return JSON.stringify(result);
    })()
  `;
  const result = await ws.send('Runtime.evaluate', {
    expression: expr,
    returnByValue: true,
    awaitPromise: true,
  });
  ws.close();
  if (result.exceptionDetails) {
    console.error('ERROR:', result.exceptionDetails.text);
    process.exit(1);
  }
  console.log(result.result?.value || 'NO DATA');
}

// --- Main ---
const [,, cmd, ...args] = process.argv;

try {
  switch (cmd) {
    case 'list': case 'ls': await cmdList(); break;
    case 'snap': await cmdSnap(args[0]); break;
    case 'eval': await cmdEval(args[0], args.slice(1).join(' ')); break;
    case 'nav': await cmdNav(args[0], args[1]); break;
    case 'shot': await cmdShot(args[0], args[1]); break;
    case 'html': await cmdHtml(args[0], args[1]); break;
    case 'click': await cmdClick(args[0], args[1]); break;
    case 'type': await cmdType(args[0], args[1]); break;
    case 'open': await cmdOpen(args[0]); break;
    case 'idb': await cmdIdb(args[0], args[1]); break;
    default:
      console.log('Julian CDP — Browser control for the Resurrection');
      console.log('Usage: node julian-cdp.mjs <command> [args]');
      console.log('Commands: list, snap, eval, nav, shot, html, click, type, open, idb');
      console.log(`\nCDP port: ${PORT} (set CDP_PORT env to override)`);
  }
} catch (e) {
  console.error(`ERROR: ${e.message}`);
  process.exit(1);
}
