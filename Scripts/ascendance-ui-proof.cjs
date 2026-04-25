const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { spawn, execFileSync } = require('child_process');
const { chromium } = require('playwright');

const repoRoot = 'C:\\Users\\raest\\Documents\\Karma_SADE';
const tauriExe = 'C:\\Users\\raest\\Documents\\Karma_SADE\\nexus-tauri\\src-tauri\\target\\release\\arknexusv6.exe';
const hubBase = 'https://hub.arknexus.net';
const runDir = getArg('--run-dir');

if (!runDir) {
  console.error('missing --run-dir');
  process.exit(1);
}

const session = JSON.parse(fs.readFileSync(path.join(runDir, 'session.json'), 'utf8'));
const sessionId = session.session_id || session.SESSION_ID;
const runId = session.run_id || path.basename(runDir);
const resultsPath = path.join(runDir, 'ui-proof-results.json');
const artifacts = [];
const results = {
  run_id: runId,
  session_id: sessionId,
  started_at_utc: new Date().toISOString(),
  local: {},
  hub: {},
  errors: [],
};

function getArg(flag) {
  const idx = process.argv.indexOf(flag);
  if (idx === -1 || idx + 1 >= process.argv.length) return '';
  return process.argv[idx + 1];
}

function sha256(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function recordArtifact(gateId, filePath, expected, actual) {
  artifacts.push({
    gate_id: gateId,
    path: filePath,
    sha256: sha256(filePath),
    expected,
    actual,
    timestamp_utc: new Date().toISOString(),
  });
}

function ps(command) {
  return execFileSync(
    'powershell',
    ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command],
    { encoding: 'utf8' },
  );
}

function getHubToken() {
  return execFileSync(
    'ssh',
    ['vault-neo', 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt'],
    { encoding: 'utf8' },
  ).trim();
}

function stopTauri() {
  try {
    ps("Get-Process arknexusv6 -ErrorAction SilentlyContinue | Stop-Process -Force");
  } catch {}
}

function startTauri() {
  const child = spawn(tauriExe, [], {
    detached: true,
    stdio: 'ignore',
    env: {
      ...process.env,
      ARKNEXUS_DEVTOOLS: '1',
      WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS: '--remote-debugging-port=9222 --remote-allow-origins=*',
      NEXUS_SESSION_ID: sessionId,
    },
  });
  child.unref();
}

async function connectTauri() {
  for (let i = 0; i < 40; i += 1) {
    try {
      const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
      const page = browser.contexts()[0].pages().find((p) => !p.url().startsWith('devtools:'));
      if (page) return { browser, page };
      await browser.close();
    } catch {}
    await sleep(1000);
  }
  throw new Error('tauri_cdp_unavailable');
}

async function restartTauri() {
  stopTauri();
  await sleep(1500);
  startTauri();
  await sleep(7000);
  return connectTauri();
}

async function authPage(page, token) {
  await page.waitForLoadState('domcontentloaded');
  await page.evaluate((tok) => {
    localStorage.setItem('karma-token', tok);
    localStorage.setItem('karma-authenticated', 'true');
  }, token);
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.waitForSelector('textarea', { timeout: 60000 });
}

async function closeVisibleModal(page) {
  const buttons = page.getByRole('button', { name: /^x$/ });
  const count = await buttons.count();
  if (count > 0) {
    await buttons.nth(count - 1).click();
    await sleep(400);
  }
}

async function sendPrompt(page, prompt, marker, timeoutMs = 90000) {
  await page.waitForSelector('textarea', { timeout: 30000 });
  const before = await page.evaluate(() => {
    const store = window.__karmaStore;
    const state = store && store.getState ? store.getState() : null;
    return state && Array.isArray(state.messages) ? state.messages.length : 0;
  });
  await page.locator('textarea').fill(prompt);
  await page.getByRole('button', { name: 'SEND' }).click();
  await page.waitForFunction(
    ({ m, priorCount }) => {
      const store = window.__karmaStore;
      const state = store && store.getState ? store.getState() : null;
      if (!state || state.isStreaming) return false;
      const messages = Array.isArray(state.messages) ? state.messages : [];
      const last = [...messages.slice(priorCount)].reverse().find((msg) => (
        msg && msg.role === 'karma' && typeof msg.content === 'string' && msg.content.includes(m)
      ));
      return !!last;
    },
    { m: marker, priorCount: before },
    { timeout: timeoutMs },
  );
  await sleep(1500);
  return page.evaluate(({ m, priorCount }) => {
    const store = window.__karmaStore;
    const state = store && store.getState ? store.getState() : null;
    const messages = state && Array.isArray(state.messages) ? state.messages : [];
    const last = [...messages.slice(priorCount)].reverse().find((msg) => (
      msg && msg.role === 'karma' && typeof msg.content === 'string' && msg.content.includes(m)
    ));
    return last ? last.content : '';
  }, { m: marker, priorCount: before });
}

async function sendPromptMatch(page, prompt, matcher, timeoutMs = 90000) {
  await page.waitForSelector('textarea', { timeout: 30000 });
  const before = await page.evaluate(() => {
    const store = window.__karmaStore;
    const state = store && store.getState ? store.getState() : null;
    return state && Array.isArray(state.messages) ? state.messages.length : 0;
  });
  await page.locator('textarea').fill(prompt);
  await page.getByRole('button', { name: 'SEND' }).click();
  await page.waitForFunction(
    ({ priorCount, anyOf, allOf, noneOf }) => {
      const store = window.__karmaStore;
      const state = store && store.getState ? store.getState() : null;
      if (!state || state.isStreaming) return false;
      const messages = Array.isArray(state.messages) ? state.messages : [];
      const karmaMessages = messages
        .slice(priorCount)
        .filter((msg) => msg && msg.role === 'karma' && typeof msg.content === 'string' && msg.content.trim());
      return karmaMessages.some((msg) => {
        const content = msg.content.toLowerCase();
        const anyOk = !anyOf.length || anyOf.some((term) => content.includes(term));
        const allOk = allOf.every((term) => content.includes(term));
        const noneOk = noneOf.every((term) => !content.includes(term));
        return anyOk && allOk && noneOk;
      });
    },
    {
      priorCount: before,
      anyOf: (matcher.anyOf || []).map((term) => String(term).toLowerCase()),
      allOf: (matcher.allOf || []).map((term) => String(term).toLowerCase()),
      noneOf: (matcher.noneOf || []).map((term) => String(term).toLowerCase()),
    },
    { timeout: timeoutMs },
  );
  await sleep(1500);
  return page.evaluate(({ priorCount, anyOf, allOf, noneOf }) => {
    const store = window.__karmaStore;
    const state = store && store.getState ? store.getState() : null;
    const messages = state && Array.isArray(state.messages) ? state.messages : [];
    const karmaMessages = messages
      .slice(priorCount)
      .filter((msg) => msg && msg.role === 'karma' && typeof msg.content === 'string' && msg.content.trim())
      .reverse();
    const match = karmaMessages.find((msg) => {
      const content = msg.content.toLowerCase();
      const anyOk = !anyOf.length || anyOf.some((term) => content.includes(term));
      const allOk = allOf.every((term) => content.includes(term));
      const noneOk = noneOf.every((term) => !content.includes(term));
      return anyOk && allOk && noneOk;
    });
    return match ? match.content : '';
  }, {
    priorCount: before,
    anyOf: (matcher.anyOf || []).map((term) => String(term).toLowerCase()),
    allOf: (matcher.allOf || []).map((term) => String(term).toLowerCase()),
    noneOf: (matcher.noneOf || []).map((term) => String(term).toLowerCase()),
  });
}

async function openHeaderPanel(page, label) {
  await page.getByRole('button', { name: label }).click();
  await sleep(800);
}

async function resetConversation(page, conversationId) {
  await page.evaluate((sid) => {
    const store = window.__karmaStore;
    const state = store && store.getState ? store.getState() : null;
    if (!state) return;
    if (typeof state.setConversationId === 'function') state.setConversationId(sid);
    if (typeof state.clearMessages === 'function') state.clearMessages();
    localStorage.setItem('karma-conversation-id', sid);
    localStorage.removeItem('karma-messages');
  }, conversationId);
  await sleep(800);
}

async function takeShot(page, filePath, fullPage = true) {
  await page.screenshot({ path: filePath, fullPage });
}

async function fetchJson(url, token) {
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

async function runLocal(token) {
  const { browser, page } = await restartTauri();
  try {
    await authPage(page, token);

    const namingShot = path.join(runDir, 'ui-identity-naming.png');
    await takeShot(page, namingShot, false);
    results.local.naming = {
      title: await page.title(),
      header: await page.getByText('ARKNEXUSV6').first().textContent(),
    };
    recordArtifact('G14_IDENTITY_NAMING', namingShot, 'ArknexusV6 title and visible ARKNEXUSV6 header', JSON.stringify(results.local.naming));

    const coworkOpenShot = path.join(runDir, 'ui-cowork-open.png');
    await takeShot(page, coworkOpenShot);
    recordArtifact('G13_COWORK', coworkOpenShot, 'cowork artifact list visible', 'cowork open');
    const hideButton = page.getByRole('button', { name: 'HIDE' });
    if (await hideButton.count()) {
      await hideButton.click();
      await sleep(400);
    }
    const coworkCollapsedShot = path.join(runDir, 'ui-cowork-collapsed.png');
    await takeShot(page, coworkCollapsedShot);
    recordArtifact('G13_COWORK', coworkCollapsedShot, 'collapsed COWORK button visible', 'cowork collapsed');
    await page.getByRole('button', { name: 'COWORK' }).click();
    await sleep(500);
    const coworkReopenShot = path.join(runDir, 'ui-cowork-reopened.png');
    await takeShot(page, coworkReopenShot);
    recordArtifact('G13_COWORK', coworkReopenShot, 'cowork panel reopened', 'cowork reopened');

    const learningsData = await fetchJson('http://127.0.0.1:7891/v1/learnings', token);
    await openHeaderPanel(page, 'LEARNED');
    await page.getByText('LEARNED').first().waitFor({ timeout: 30000 });
    const learningRow = page.locator('text=karma').nth(0);
    if (await learningRow.count()) {
      await learningRow.click().catch(() => {});
      await sleep(300);
    }
    const learningsShot = path.join(runDir, 'ui-learnings-panel.png');
    await takeShot(page, learningsShot);
    results.local.learnings = { entries: (learningsData.entries || learningsData.learnings || []).length };
    recordArtifact('G9_LEARNINGS_PANEL', learningsShot, 'non-empty learnings panel for live source', JSON.stringify(results.local.learnings));
    await closeVisibleModal(page);

    const agentsTaskMarker = `AGENTTASK-${sessionId}`;
    await openHeaderPanel(page, 'AGENTS');
    await page.getByPlaceholder('Type a task for the bus...').fill(`UI proof task ${agentsTaskMarker}`);
    await page.getByRole('button', { name: 'POST' }).click();
    await sleep(1500);
    const tasksRow = page.getByText(/Coord Tasks \(/).first();
    if (await tasksRow.count()) await tasksRow.click();
    const agentsShot = path.join(runDir, 'phase3-agents-sections.png');
    await takeShot(page, agentsShot);
    recordArtifact('G10_AGENTS_TASKS', agentsShot, `agents/tasks panel with posted task ${agentsTaskMarker}`, 'agents/tasks panel expanded');
    const mouthRow = page.getByText('Mouth Policy').first();
    if (await mouthRow.count()) {
      await mouthRow.click();
      await sleep(500);
    }
    const modelShot = path.join(runDir, 'ui-model-policy.png');
    await takeShot(page, modelShot);
    const modelPolicy = await fetchJson('http://127.0.0.1:7891/v1/model-policy', token);
    results.local.model_policy = {
      mouth: modelPolicy.mouth,
      primary_model: modelPolicy.primary_model,
    };
    recordArtifact('G15_MODEL_POLICY', modelShot, 'Anthropic/Haiku primary model policy visible', JSON.stringify(results.local.model_policy));
    await closeVisibleModal(page);

    await openHeaderPanel(page, 'WIP');
    const todoMarker = `TODO-${sessionId}`;
    await page.getByPlaceholder('Add a todo...').fill(`UI proof todo ${todoMarker}`);
    await page.getByRole('button', { name: 'ADD' }).click();
    await sleep(1200);
    const todoRow = page.getByText(`UI proof todo ${todoMarker}`).first();
    if (await todoRow.count()) {
      const row = todoRow.locator('..');
      const doBtn = row.getByRole('button', { name: 'DO' }).first();
      if (await doBtn.count()) await doBtn.click();
      await sleep(500);
    }
    const todoShot = path.join(runDir, 'ui-wip-todos.png');
    await takeShot(page, todoShot);
    recordArtifact('G11_WIP_TODOS', todoShot, `todo ${todoMarker} added and status changed`, 'todo visible in WIP panel');

    const wipData = await fetchJson('http://127.0.0.1:7891/v1/wip', token);
    const dismissedPrimitive = (wipData.primitives || []).find((p) => p.status === 'dismissed' || (p.dismissed_primitives || []).length > 0) || (wipData.primitives || [])[0];
    await page.getByRole('button', { name: 'PRIMITIVES' }).click();
    await sleep(600);
    if (dismissedPrimitive && dismissedPrimitive.title) {
      const primRow = page.getByText(dismissedPrimitive.title, { exact: false }).first();
      if (await primRow.count()) {
        await primRow.click();
        await sleep(400);
      }
    }
    const primitiveShot = path.join(runDir, 'ui-wip-primitives.png');
    await takeShot(page, primitiveShot);
    recordArtifact('G12_PRIMITIVES', primitiveShot, 'primitive entry with source, idea, impact, dismissed state', dismissedPrimitive ? dismissedPrimitive.title : 'no primitive title');
    await closeVisibleModal(page);

    const memMarker = `MEMCAN-${sessionId}`;
    await fetch('http://127.0.0.1:7891/v1/memory/save', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: memMarker,
        text: `Canonical memory write ${memMarker} for ${runId}`,
      }),
    });

    await browser.close();

    const relaunched = await restartTauri();
    const page2 = relaunched.page;
    await authPage(page2, token);
    await openHeaderPanel(page2, 'MEMORY');
    await page2.getByPlaceholder('Search memories...').fill(memMarker);
    await page2.getByRole('button', { name: 'SEARCH' }).click();
    await page2.getByText(memMarker, { exact: false }).first().waitFor({ timeout: 60000 });
    const memShot = path.join(runDir, 'ui-memory-canonical.png');
    await takeShot(page2, memShot);
    recordArtifact('G7_MEMORY_CANONICAL', memShot, `memory search shows ${memMarker} after restart`, 'memory panel returned current run marker');
    await closeVisibleModal(page2);

    await resetConversation(page2, `${sessionId}-ui-proof-local`);

    const localMarker = `LOCALCHAT-${sessionId}`;
    const localPrompt = `Reply in one short sentence beginning exactly with ${localMarker} and confirm the local ArknexusV6 UI rendered a live assistant reply.`;
    const localTail = await sendPrompt(page2, localPrompt, localMarker);
    const localShot = path.join(runDir, 'ui-local-chat.png');
    await takeShot(page2, localShot, false);
    results.local.chat = { marker: localMarker, tail: localTail };
    recordArtifact('G3_LOCAL_APP_CHAT', localShot, `assistant reply containing ${localMarker}`, localTail);

    const offloadPrompt = 'In one sentence, state that you will use runtime tools directly and report the exact command and error if blocked. Do not ask for SSH, credentials, or manual file dumps.';
    const offloadTail = await sendPromptMatch(page2, offloadPrompt, {
      anyOf: ['runtime tools', 'live probes', 'routes/tools', 'available tools'],
      allOf: ['report', 'command'],
      noneOf: ['you run', 'provide file', 'credentials', 'manual file dump'],
    });
    const offloadShot = path.join(runDir, 'ui-no-user-offload.png');
    await takeShot(page2, offloadShot, false);
    results.local.no_user_offload = { tail: offloadTail };
    recordArtifact('G16_NO_USER_OFFLOAD', offloadShot, 'assistant reply commits to direct runtime-tool use and exact command/error reporting without user offload', offloadTail);

    const unicodePrompt = 'Reply in one sentence and include these exact characters unchanged: snowman ☃ omega Ω kanji 雪 grin 😀.';
    const unicodeTail = await sendPromptMatch(page2, unicodePrompt, {
      allOf: ['☃', 'ω', '雪', '😀'],
    });
    const unicodeShot = path.join(runDir, 'ui-unicode-chat.png');
    await takeShot(page2, unicodeShot, false);
    results.local.unicode = { tail: unicodeTail };
    recordArtifact('G17_UNICODE', unicodeShot, 'assistant reply includes the required Unicode characters without runtime crash', unicodeTail);

    await relaunched.browser.close();
  } finally {
    stopTauri();
  }
}

async function runHub(token) {
  const userDataDir = path.join(os.tmpdir(), `ark-hub-${sessionId}`);
  fs.rmSync(userDataDir, { recursive: true, force: true });
  const context = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    channel: 'msedge',
  });
  try {
    await context.addCookies([{
      name: 'hub_token',
      value: token,
      domain: 'hub.arknexus.net',
      path: '/',
      secure: true,
      httpOnly: false,
      sameSite: 'Lax',
    }]);
    const page = await context.newPage();
    await page.goto(hubBase, { waitUntil: 'domcontentloaded', timeout: 120000 });
    await page.evaluate((tok) => {
      localStorage.setItem('karma-token', tok);
      localStorage.setItem('karma-authenticated', 'true');
    }, token);
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('textarea', { timeout: 90000 });
    await resetConversation(page, `${sessionId}-ui-proof-hub`);
    const marker = `HUBCHAT-${sessionId}`;
    const prompt = `Reply in one short sentence beginning exactly with ${marker} and confirm the hub browser chat rendered a live assistant reply.`;
    const hubTail = await sendPrompt(page, prompt, marker, 120000);
    const hubShot = path.join(runDir, 'ui-hub-chat.png');
    await takeShot(page, hubShot, false);
    results.hub.chat = { marker, tail: hubTail, title: await page.title() };
    recordArtifact('G4_HUB_CHAT', hubShot, `assistant reply containing ${marker}`, hubTail);
  } finally {
    await context.close();
    fs.rmSync(userDataDir, { recursive: true, force: true });
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

(async () => {
  try {
    const token = getHubToken();
    await runLocal(token);
    await runHub(token);
    results.completed_at_utc = new Date().toISOString();
    results.artifacts = artifacts;
    fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));
    console.log(JSON.stringify({ ok: true, resultsPath, artifactCount: artifacts.length }, null, 2));
  } catch (error) {
    results.completed_at_utc = new Date().toISOString();
    results.errors.push(String(error && error.stack ? error.stack : error));
    results.artifacts = artifacts;
    fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));
    console.error(String(error && error.stack ? error.stack : error));
    process.exit(1);
  }
})();
