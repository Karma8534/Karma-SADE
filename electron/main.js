const { app, BrowserWindow, ipcMain, dialog, Tray, Menu } = require("electron");
const { exec, spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

// KARMA NEXUS — Electron Harness (S156)
const WORK_DIR = process.platform === "win32"
  ? "C:\\Users\\raest\\Documents\\Karma_SADE"
  : "/mnt/c/dev/Karma/k2/cache";
const NODE_EXE = process.platform === "win32"
  ? "C:\\Program Files\\nodejs\\node.exe"
  : "/usr/bin/node";
const CLAUDE_CLI = process.platform === "win32"
  ? path.join(process.env.APPDATA || "", "npm", "node_modules", "@anthropic-ai", "claude-code", "cli.js")
  : "/usr/local/bin/claude";
const CORTEX_URL = "http://192.168.0.226:7892";
const CLAUDEMEM_URL = "http://127.0.0.1:37778";
const OLLAMA_URL = process.platform === "win32" ? "http://localhost:11434" : "http://172.22.240.1:11434";
const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
const GROQ_MODEL = "llama-3.3-70b-versatile";
const BOUNDS_FILE = path.join(app.getPath("userData"), "karma_bounds.json");
const SESSION_FILE = path.join(app.getPath("home"), ".karma_electron_session_id");
const FRONTEND_DIR = path.join(__dirname, "frontend", "out");
const NEXUS_URL = "https://hub.arknexus.net";
const CC_TIMEOUT_MS = 180000;
const TOOL_LOOP_LIMIT = 6;
const STREAM_CHANNEL = "cc-chat-event";
const TOOL_DEFS = [
  {
    name: "read_file",
    description: "Read a file from the local workspace.",
    input_schema: { type: "object", properties: { path: { type: "string" }, limit: { type: "integer" } }, required: ["path"] },
  },
  {
    name: "write_file",
    description: "Write file content with checkpoint backup.",
    input_schema: { type: "object", properties: { path: { type: "string" }, content: { type: "string" } }, required: ["path", "content"] },
  },
  {
    name: "shell",
    description: "Execute a shell command in the workspace.",
    input_schema: { type: "object", properties: { command: { type: "string" } }, required: ["command"] },
  },
  {
    name: "git",
    description: "Run a git command in the workspace.",
    input_schema: { type: "object", properties: { command: { type: "string" } }, required: ["command"] },
  },
  {
    name: "glob",
    description: "Find files matching a glob pattern under a path.",
    input_schema: {
      type: "object",
      properties: { pattern: { type: "string" }, path: { type: "string" } },
      required: ["pattern"],
    },
  },
  {
    name: "grep",
    description: "Search file contents with a regex pattern under a path.",
    input_schema: {
      type: "object",
      properties: { pattern: { type: "string" }, path: { type: "string" } },
      required: ["pattern"],
    },
  },
];
const TOOL_PROMPT = [
  "You are Karma inside the Nexus harness.",
  "You do not have direct filesystem or shell access.",
  "When you need a tool, respond with ONLY a JSON object in this exact form:",
  '{"tool_use":{"name":"read_file","input":{"path":"MEMORY.md"}}}',
  "Allowed tools:",
  JSON.stringify(TOOL_DEFS),
  "Rules:",
  "1. Use tools instead of guessing about files, git state, or shell output.",
  "2. After a tool result is returned, continue from that result.",
  "3. When you are done, return plain text only, not JSON.",
].join("\n");

let mainWindow;
let tray;
let currentCCProc = null;
let currentCCRunId = null;

function createWindow() {
  let saved;
  try {
    saved = JSON.parse(fs.readFileSync(BOUNDS_FILE, "utf-8"));
  } catch {
    saved = null;
  }
  mainWindow = new BrowserWindow({
    width: saved?.width || 1200,
    height: saved?.height || 800,
    x: saved?.x,
    y: saved?.y,
    title: "KARMA — The Nexus",
    backgroundColor: "#0d0d0f",
    icon: path.join(__dirname, "icon.png"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    autoHideMenuBar: true,
  });
  if (fs.existsSync(path.join(FRONTEND_DIR, "index.html"))) {
    mainWindow.loadFile(path.join(FRONTEND_DIR, "index.html"));
  } else {
    mainWindow.loadURL(NEXUS_URL);
  }
  mainWindow.on("page-title-updated", (e) => e.preventDefault());
  mainWindow.setTitle("KARMA — The Nexus");
  mainWindow.on("close", () => {
    try {
      fs.writeFileSync(BOUNDS_FILE, JSON.stringify(mainWindow.getBounds()));
    } catch {}
  });
  mainWindow.webContents.on("before-input-event", (_event, input) => {
    if (input.key === "Escape" && currentCCProc) {
      currentCCProc.kill();
      currentCCProc = null;
      currentCCRunId = null;
    }
  });
}

function checkpointDir() {
  return path.join(app.getPath("userData"), "checkpoints");
}

function normalizeWorkspacePath(targetPath = "") {
  const resolved = path.resolve(WORK_DIR, targetPath);
  const normalizedRoot = path.resolve(WORK_DIR);
  if (resolved !== normalizedRoot && !resolved.startsWith(normalizedRoot + path.sep)) {
    throw new Error(`Path escapes workspace: ${targetPath}`);
  }
  return resolved;
}

function readSessionId() {
  try {
    return fs.readFileSync(SESSION_FILE, "utf-8").trim() || null;
  } catch {
    return null;
  }
}

function saveSessionId(sessionId) {
  if (!sessionId) return;
  try {
    fs.writeFileSync(SESSION_FILE, sessionId);
  } catch {}
}

function clearSessionId() {
  try {
    fs.unlinkSync(SESSION_FILE);
  } catch {}
}

function emitChatEvent(runId, evt) {
  if (!mainWindow || !runId) return;
  try {
    mainWindow.webContents.send(STREAM_CHANNEL, { runId, ...evt });
  } catch {}
}

function safePreview(value, max = 1200) {
  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  return text.length > max ? `${text.slice(0, max)}\n...[truncated]...` : text;
}

function toolResultContent(value) {
  return [{ type: "text", text: safePreview(value) }];
}

function fileRead(targetPath) {
  try {
    const filePath = normalizeWorkspacePath(targetPath);
    return {
      ok: true,
      content: fs.readFileSync(filePath, "utf-8"),
      size: fs.statSync(filePath).size,
      path: filePath,
    };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

function fileWrite(targetPath, content) {
  const cpDir = checkpointDir();
  try {
    const filePath = normalizeWorkspacePath(targetPath);
    fs.mkdirSync(cpDir, { recursive: true });
    if (fs.existsSync(filePath)) {
      fs.copyFileSync(
        filePath,
        path.join(
          cpDir,
          `${crypto.createHash("sha256").update(targetPath).digest("hex").slice(0, 8)}_${Date.now()}.bak`,
        ),
      );
    }
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, content, "utf-8");
    return { ok: true, path: filePath };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

function shellExec(command) {
  return new Promise((resolve) => {
    exec(command, { timeout: 30000, cwd: WORK_DIR }, (err, stdout, stderr) => {
      resolve({
        ok: !err,
        stdout: stdout || "",
        stderr: stderr || "",
        code: err?.code || 0,
      });
    });
  });
}

function gitStatus() {
  return new Promise((resolve) => {
    exec("git status --porcelain -b", { cwd: WORK_DIR, timeout: 5000 }, (_err, out) => {
      const lines = (out || "").trim().split("\n");
      resolve({
        ok: true,
        branch: lines[0]?.replace("## ", "") || "?",
        changed: lines.slice(1).filter((line) => line.trim()).length,
        files: lines.slice(1).slice(0, 20),
      });
    });
  });
}

function globToRegExp(pattern) {
  const escaped = pattern
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*\*/g, ":::DOUBLESTAR:::")
    .replace(/\*/g, "[^\\\\/]*")
    .replace(/\?/g, ".");
  return new RegExp(`^${escaped.replace(/:::DOUBLESTAR:::/g, ".*")}$`, "i");
}

function walkFiles(rootDir, out = []) {
  const entries = fs.readdirSync(rootDir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === ".git" || entry.name === "node_modules" || entry.name === ".next") continue;
    const full = path.join(rootDir, entry.name);
    if (entry.isDirectory()) {
      walkFiles(full, out);
    } else {
      out.push(full);
    }
  }
  return out;
}

function globFiles(pattern, basePath = ".") {
  try {
    const root = normalizeWorkspacePath(basePath);
    const regex = globToRegExp(pattern);
    const matches = walkFiles(root)
      .map((full) => path.relative(WORK_DIR, full).replace(/\\/g, "/"))
      .filter((rel) => regex.test(rel) || regex.test(path.basename(rel)));
    return { ok: true, matches };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

function grepFiles(pattern, basePath = ".") {
  try {
    const root = normalizeWorkspacePath(basePath);
    const regex = new RegExp(pattern, "i");
    const matches = [];
    for (const full of walkFiles(root)) {
      const rel = path.relative(WORK_DIR, full).replace(/\\/g, "/");
      try {
        const content = fs.readFileSync(full, "utf-8");
        const lines = content.split(/\r?\n/);
        lines.forEach((line, index) => {
          if (regex.test(line)) {
            matches.push({ path: rel, line: index + 1, text: line.trim().slice(0, 200) });
          }
        });
      } catch {}
    }
    return { ok: true, matches: matches.slice(0, 200) };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

async function executeTool(toolName, input) {
  switch (toolName) {
    case "read_file":
      return fileRead(input.path);
    case "write_file":
      return fileWrite(input.path, input.content || "");
    case "shell":
      return shellExec(input.command || "");
    case "git":
      return shellExec(`git ${input.command || ""}`);
    case "glob":
      return globFiles(input.pattern || "", input.path || ".");
    case "grep":
      return grepFiles(input.pattern || "", input.path || ".");
    default:
      return { ok: false, error: `Unknown tool: ${toolName}` };
  }
}

function parseJsonObject(text) {
  const trimmed = (text || "").trim();
  if (!trimmed) return null;
  const candidates = [trimmed];
  const fenced = trimmed.match(/```json\s*([\s\S]+?)```/i);
  if (fenced) candidates.push(fenced[1].trim());
  const bare = trimmed.match(/\{[\s\S]+\}/);
  if (bare) candidates.push(bare[0].trim());
  for (const candidate of candidates) {
    try {
      return JSON.parse(candidate);
    } catch {}
  }
  return null;
}

function isStaleResumeError(text = "") {
  const lower = text.toLowerCase();
  return lower.includes("resume")
    || lower.includes("session")
    || lower.includes("not found")
    || lower.includes("invalid conversation");
}

function buildClaudePrompt(message, transcript) {
  const blocks = [TOOL_PROMPT];
  for (const entry of transcript) {
    blocks.push(`[${entry.role.toUpperCase()}]\n${entry.content}`);
  }
  blocks.push(`[USER]\n${message}`);
  return blocks.join("\n\n");
}

function extractAssistantTextFromEvents(lines) {
  let text = "";
  for (const line of lines) {
    try {
      const evt = JSON.parse(line);
      if (evt.type === "assistant") {
        const content = evt.message?.content || [];
        for (const block of content) {
          if (block.type === "text" && block.text) text += block.text;
        }
      }
      if (evt.type === "result" && evt.result && !text) {
        text = evt.result;
      }
    } catch {}
  }
  return text.trim();
}

function runClaudeAttempt(prompt, opts = {}) {
  const sessionId = opts.resume ? readSessionId() : null;
  const args = [CLAUDE_CLI, "-p", prompt, "--output-format", "stream-json", "--verbose", "--dangerously-skip-permissions"];
  if (sessionId) args.push("--resume", sessionId);
  if (opts.effort) args.push("--effort", opts.effort);
  if (opts.model) args.push("--model", opts.model);
  return new Promise((resolve) => {
    const proc = spawn(NODE_EXE, args, { cwd: WORK_DIR });
    currentCCProc = proc;
    let stdout = "";
    let stderr = "";
    const lines = [];
    let settled = false;
    const finish = (payload) => {
      if (settled) return;
      settled = true;
      if (currentCCProc === proc) currentCCProc = null;
      resolve(payload);
    };
    proc.stdout.on("data", (chunk) => {
      const text = chunk.toString();
      stdout += text;
      const nextLines = text.split(/\r?\n/).filter(Boolean);
      lines.push(...nextLines);
      for (const line of nextLines) {
        try {
          const evt = JSON.parse(line);
          if (evt.type === "result" && evt.session_id) saveSessionId(evt.session_id);
        } catch {}
      }
    });
    proc.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    proc.on("error", (error) => finish({ ok: false, error: error.message, stdout, stderr, lines }));
    proc.on("close", (code) => {
      const text = extractAssistantTextFromEvents(lines);
      if (code === 0) {
        finish({ ok: true, text, stdout, stderr, lines });
        return;
      }
      finish({
        ok: false,
        error: `CC exit ${code}: ${(stderr || stdout).trim()}`,
        stdout,
        stderr,
        lines,
      });
    });
    setTimeout(() => {
      if (settled) return;
      try {
        proc.kill();
      } catch {}
      finish({ ok: false, error: "timeout", stdout, stderr, lines });
    }, CC_TIMEOUT_MS);
  });
}

async function runClaudeHarness(message, opts = {}, runId = null) {
  const transcript = [];
  const emitted = [];
  let usedFreshSession = false;
  for (let turn = 0; turn < TOOL_LOOP_LIMIT; turn += 1) {
    const prompt = buildClaudePrompt(message, transcript);
    const attempt = await runClaudeAttempt(prompt, { ...opts, resume: !usedFreshSession });
    if (!attempt.ok) {
      if (!usedFreshSession && isStaleResumeError(attempt.error || "")) {
        clearSessionId();
        usedFreshSession = true;
        continue;
      }
      throw new Error(attempt.error || "claude failed");
    }
    for (const raw of attempt.lines) {
      try {
        const evt = JSON.parse(raw);
        if (evt.type === "stream_event" || evt.type === "assistant") {
          emitChatEvent(runId, evt);
          emitted.push(evt);
        }
      } catch {}
    }
    const maybeJson = parseJsonObject(attempt.text);
    const toolUse = maybeJson?.tool_use;
    if (!toolUse?.name) {
      const resultEvt = { type: "result", result: attempt.text, session_id: readSessionId(), provider: "claude" };
      emitChatEvent(runId, resultEvt);
      emitted.push(resultEvt);
      return { ok: true, provider: "claude", result: attempt.text, events: emitted, session_id: readSessionId() };
    }
    const toolId = `${toolUse.name}-${Date.now()}-${turn}`;
    const assistantEvt = {
      type: "assistant",
      message: {
        role: "assistant",
        content: [{ type: "tool_use", id: toolId, name: toolUse.name, input: toolUse.input || {} }],
      },
    };
    emitChatEvent(runId, assistantEvt);
    emitted.push(assistantEvt);
    const toolOutput = await executeTool(toolUse.name, toolUse.input || {});
    const toolEvt = { type: "tool_result", tool_use_id: toolId, content: toolResultContent(toolOutput) };
    emitChatEvent(runId, toolEvt);
    emitted.push(toolEvt);
    transcript.push({
      role: "assistant",
      content: JSON.stringify({ tool_use: { name: toolUse.name, input: toolUse.input || {} } }),
    });
    transcript.push({ role: "tool", content: JSON.stringify(toolOutput, null, 2) });
  }
  throw new Error("Tool loop limit exceeded");
}

async function callGroq(message) {
  let apiKey = process.env.GROQ_API_KEY || "";
  if (!apiKey) {
    try {
      apiKey = fs.readFileSync(path.join(WORK_DIR, ".groq-api-key"), "utf-8").trim();
    } catch {}
  }
  if (!apiKey) throw new Error("missing Groq API key");
  const response = await fetch(GROQ_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
      "User-Agent": "Karma-Nexus-Electron/1.0",
    },
    body: JSON.stringify({
      model: GROQ_MODEL,
      messages: [{ role: "user", content: message }],
      max_tokens: 1024,
      temperature: 0.2,
    }),
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Groq ${response.status}: ${text.slice(0, 300)}`);
  }
  const data = await response.json();
  return {
    ok: true,
    provider: "groq",
    result: data.choices?.[0]?.message?.content || "",
    model: data.model || GROQ_MODEL,
  };
}

async function callCortex(message) {
  const response = await fetch(`${CORTEX_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: message }),
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) throw new Error(`Cortex ${response.status}`);
  const data = await response.json();
  return {
    ok: true,
    provider: "cortex",
    result: data.answer || data.response || data.result || "",
    raw: data,
  };
}

async function runChatCascade(message, opts = {}, runId = null) {
  try {
    return await runClaudeHarness(message, opts, runId);
  } catch (claudeError) {
    emitChatEvent(runId, { type: "error", error: `Claude unavailable, falling back: ${claudeError.message}` });
    try {
      const groq = await callGroq(message);
      const assistantEvt = {
        type: "assistant",
        message: { role: "assistant", content: [{ type: "text", text: groq.result }], model: groq.model },
      };
      emitChatEvent(runId, assistantEvt);
      emitChatEvent(runId, { type: "result", result: groq.result, provider: "groq", total_cost_usd: 0 });
      return { ...groq, events: [assistantEvt] };
    } catch (groqError) {
      emitChatEvent(runId, { type: "error", error: `Groq unavailable, falling back: ${groqError.message}` });
      const cortex = await callCortex(message);
      const assistantEvt = {
        type: "assistant",
        message: { role: "assistant", content: [{ type: "text", text: cortex.result }], model: "k2-cortex" },
      };
      emitChatEvent(runId, assistantEvt);
      emitChatEvent(runId, { type: "result", result: cortex.result, provider: "cortex", total_cost_usd: 0 });
      return { ...cortex, events: [assistantEvt] };
    }
  }
}

ipcMain.handle("file-read", (_event, p) => fileRead(p));
ipcMain.handle("file-write", (_event, p, c) => fileWrite(p, c));
ipcMain.handle("shell-exec", (_event, cmd) => shellExec(cmd));
ipcMain.handle("cc-chat", async (_event, msg, opts) => {
  const runId = opts?.runId || `cc-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  currentCCRunId = runId;
  try {
    return await runChatCascade(msg, opts || {}, runId);
  } finally {
    currentCCRunId = null;
  }
});
ipcMain.handle("cc-cancel", () => {
  if (currentCCProc) {
    currentCCProc.kill();
    currentCCProc = null;
    emitChatEvent(currentCCRunId, { type: "error", error: "cancelled" });
    currentCCRunId = null;
    return { ok: true };
  }
  return { ok: false };
});
ipcMain.handle("cortex-query", async (_event, q) => {
  try {
    const r = await fetch(`${CORTEX_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q }),
      signal: AbortSignal.timeout(30000),
    });
    return await r.json();
  } catch (error) {
    return { ok: false, error: error.message };
  }
});
ipcMain.handle("cortex-context", async () => {
  try {
    return await (await fetch(`${CORTEX_URL}/context`, { signal: AbortSignal.timeout(30000) })).json();
  } catch (error) {
    return { ok: false, error: error.message };
  }
});
ipcMain.handle("ollama-query", async (_event, prompt, model) => {
  try {
    const r = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: model || "qwen3.5:4b",
        messages: [{ role: "user", content: prompt }],
        stream: false,
        options: { num_predict: 1024 },
      }),
      signal: AbortSignal.timeout(60000),
    });
    const d = await r.json();
    return { ok: true, response: d.message?.content || "" };
  } catch (error) {
    return { ok: false, error: error.message };
  }
});
ipcMain.handle("memory-search", async (_event, q, l) => {
  try {
    return await (await fetch(`${CLAUDEMEM_URL}/api/search?query=${encodeURIComponent(q)}&limit=${l || 10}`, {
      signal: AbortSignal.timeout(5000),
    })).json();
  } catch (error) {
    return { ok: false, error: error.message };
  }
});
ipcMain.handle("memory-save", async (_event, t, title) => {
  try {
    return await (await fetch(`${CLAUDEMEM_URL}/api/memory/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: t, title, project: "Karma_SADE" }),
      signal: AbortSignal.timeout(5000),
    })).json();
  } catch (error) {
    return { ok: false, error: error.message };
  }
});
ipcMain.handle("spine-read", async () => {
  try {
    return await (await fetch(`${CORTEX_URL}/spine`, { signal: AbortSignal.timeout(5000) })).json();
  } catch (error) {
    return { ok: false, error: error.message };
  }
});
ipcMain.handle("git-status", () => gitStatus());
ipcMain.handle("show-open-dialog", async () => {
  const result = await dialog.showOpenDialog(mainWindow, { properties: ["openFile", "multiSelections"] });
  return { ok: !result.canceled, paths: result.filePaths || [] };
});

app.whenReady().then(() => {
  createWindow();
  try {
    const t = new Tray(path.join(__dirname, "icon.png"));
    t.setToolTip("Karma Nexus");
    t.setContextMenu(Menu.buildFromTemplate([
      { label: "Show", click: () => mainWindow?.show() },
      { label: "Hide", click: () => mainWindow?.hide() },
      { type: "separator" },
      { label: "Quit", click: () => app.quit() },
    ]));
    t.on("click", () => mainWindow?.show());
    tray = t;
  } catch {}
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
