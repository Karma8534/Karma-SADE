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
const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";
const OPENROUTER_MODEL = process.env.KARMA_OPENROUTER_MODEL || "anthropic/claude-sonnet-4.6";
const OPENROUTER_FALLBACK_MODEL = process.env.KARMA_OPENROUTER_FALLBACK_MODEL || "google/gemini-2.0-flash";
const OPENROUTER_THIRD_MODEL = process.env.KARMA_OPENROUTER_THIRD_MODEL || "meta-llama/llama-3.3-70b-instruct";
const BOUNDS_FILE = path.join(app.getPath("userData"), "karma_bounds.json");
const SESSION_FILE = path.join(app.getPath("home"), ".karma_electron_session_id");
const SESSION_REGISTRY_FILE = path.join(app.getPath("home"), ".karma_electron_session_registry.json");
const TRANSCRIPT_DIR = path.join(WORK_DIR, "tmp", "transcripts");
const FRONTEND_DIR = path.join(WORK_DIR, "frontend", "out");
const NEXUS_URL = "https://hub.arknexus.net";
const CC_TIMEOUT_MS = 180000;
const TOOL_LOOP_LIMIT = 6;
const STREAM_CHANNEL = "cc-chat-event";
const SMOKE_MODE = process.env.KARMA_ELECTRON_SMOKE === "1";
const SMOKE_PROMPT = process.env.KARMA_ELECTRON_SMOKE_PROMPT || "";
const SMOKE_OUT = process.env.KARMA_ELECTRON_SMOKE_OUT || path.join(WORK_DIR, "tmp", "electron-smoke.json");
const LOCAL_OLLAMA_MODEL = process.env.KARMA_LOCAL_OLLAMA_MODEL || "sam860/LFM2:350m";
const EMERGENCY_INDEPENDENT = String(process.env.KARMA_EMERGENCY_INDEPENDENT || "").toLowerCase() === "1"
  || String(process.env.KARMA_EMERGENCY_INDEPENDENT || "").toLowerCase() === "true";
const RUNTIME_LOG_FILE = path.join(app.getPath("userData"), "karma_runtime.log");
const HUB_CHAT_TOKEN = (() => {
  try {
    return fs.readFileSync(path.join(WORK_DIR, ".hub-chat-token"), "utf-8").trim();
  } catch {
    return "";
  }
})();
const OPENROUTER_API_KEY = (() => {
  const fromEnv = (process.env.OPENROUTER_API_KEY || "").trim();
  if (fromEnv) return fromEnv;
  const candidates = [
    path.join(WORK_DIR, ".openrouter-api-key"),
    path.join(WORK_DIR, ".openrouter-api-key.txt"),
    path.join(app.getPath("home"), ".openrouter-api-key"),
  ];
  for (const candidate of candidates) {
    try {
      const value = fs.readFileSync(candidate, "utf-8").trim();
      if (value) return value;
    } catch {}
  }
  return "";
})();
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
const GROQ_TOOL_DEFS = TOOL_DEFS.map((tool) => ({
  type: "function",
  function: {
    name: tool.name,
    description: tool.description,
    parameters: tool.input_schema,
  },
}));
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

if (process.platform === "win32") {
  // Windows Electron crashes here have been correlating with GPU watchdog events.
  app.disableHardwareAcceleration();
}

function runtimeLog(event, details = null) {
  try {
    const line = JSON.stringify({
      ts: new Date().toISOString(),
      event,
      ...(details ? { details } : {}),
    });
    fs.appendFileSync(RUNTIME_LOG_FILE, `${line}\n`, "utf-8");
  } catch {}
}

function normalizeCrashDetails(details) {
  if (!details || typeof details !== "object") return details || null;
  return Object.fromEntries(
    Object.entries(details).map(([key, value]) => {
      if (value instanceof Error) {
        return [key, { message: value.message, stack: value.stack }];
      }
      return [key, value];
    }),
  );
}

function recreateMainWindow(reason) {
  runtimeLog("recreate-main-window", { reason });
  try {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.destroy();
    }
  } catch {}
  mainWindow = null;
  createWindow();
  if (!SMOKE_MODE) {
    try {
      mainWindow.show();
    } catch {}
  }
}

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
    show: !SMOKE_MODE,
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
  mainWindow.on("unresponsive", () => {
    runtimeLog("window-unresponsive");
  });
  mainWindow.webContents.on("unresponsive", () => {
    runtimeLog("renderer-unresponsive");
  });
  mainWindow.webContents.on("did-fail-load", (_event, errorCode, errorDescription, validatedURL, isMainFrame) => {
    runtimeLog("did-fail-load", {
      errorCode,
      errorDescription,
      validatedURL,
      isMainFrame,
    });
  });
  mainWindow.webContents.on("render-process-gone", (_event, details) => {
    const crashDetails = normalizeCrashDetails(details);
    runtimeLog("render-process-gone", crashDetails);
    if (!SMOKE_MODE) {
      setTimeout(() => recreateMainWindow(`render-process-gone:${details?.reason || "unknown"}`), 750);
    }
  });
  mainWindow.webContents.on("before-input-event", (_event, input) => {
    if (input.key === "Escape" && currentCCProc) {
      currentCCProc.kill();
      currentCCProc = null;
      currentCCRunId = null;
    }
  });
  if (SMOKE_MODE) {
    mainWindow.once("ready-to-show", () => mainWindow.hide());
  }
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

function normalizeConversationId(conversationId) {
  const value = String(conversationId || "default").trim();
  return value || "default";
}

function transcriptPath(conversationId) {
  return path.join(TRANSCRIPT_DIR, `${normalizeConversationId(conversationId)}.jsonl`);
}

function isoTimestamp(value = Date.now()) {
  return new Date(value).toISOString();
}

function normalizeTranscriptEntry(conversationId, entry) {
  const role = String(entry?.role || "").trim().toLowerCase();
  const ts = typeof entry?.ts === "number" ? entry.ts : Date.now() / 1000;
  return {
    type: role,
    role,
    content: String(entry?.content || ""),
    timestamp: entry?.timestamp || isoTimestamp(ts * 1000),
    ts,
    session_id: normalizeConversationId(conversationId),
    cwd: WORK_DIR,
    uuid: entry?.uuid || crypto.randomUUID(),
    ...(entry?.parent_uuid ? { parent_uuid: entry.parent_uuid } : {}),
  };
}

function coerceTranscriptEntry(entry) {
  if (!entry || typeof entry !== "object") return null;
  if (!entry.type && entry.role && Object.prototype.hasOwnProperty.call(entry, "content")) {
    return {
      role: String(entry.role).toLowerCase(),
      content: String(entry.content || ""),
      ts: typeof entry.ts === "number" ? entry.ts : Date.now() / 1000,
      timestamp: entry.timestamp || isoTimestamp(),
      session_id: entry.session_id || "",
      uuid: entry.uuid || null,
      parent_uuid: entry.parent_uuid || null,
    };
  }
  if (["user", "assistant", "system", "tool", "attachment"].includes(String(entry.type).toLowerCase())) {
    return {
      role: String(entry.type).toLowerCase(),
      content: String(entry.content || ""),
      ts: typeof entry.ts === "number" ? entry.ts : Date.now() / 1000,
      timestamp: entry.timestamp || isoTimestamp(),
      session_id: entry.session_id || "",
      uuid: entry.uuid || null,
      parent_uuid: entry.parent_uuid || null,
    };
  }
  return null;
}

function appendTranscriptEntry(conversationId, entry) {
  const normalized = normalizeTranscriptEntry(conversationId, entry);
  const rows = [normalized];
  if (normalized.type === "user") {
    rows.push({
      type: "last-prompt",
      session_id: normalizeConversationId(conversationId),
      timestamp: normalized.timestamp,
      last_prompt: normalized.content,
    });
  }
  fs.mkdirSync(TRANSCRIPT_DIR, { recursive: true });
  fs.appendFileSync(
    transcriptPath(conversationId),
    rows.map((row) => `${JSON.stringify(row)}\n`).join(""),
    "utf-8",
  );
}

function loadTranscript(conversationId, limit = 100) {
  try {
    const lines = fs.readFileSync(transcriptPath(conversationId), "utf-8")
      .split(/\r?\n/)
      .filter(Boolean);
    const messages = lines
      .map((line) => {
        try {
          return coerceTranscriptEntry(JSON.parse(line));
        } catch {
          return null;
        }
      })
      .filter(Boolean);
    return limit > 0 ? messages.slice(-limit) : messages;
  } catch {
    return [];
  }
}

function buildRecoveredTranscriptContext(transcript) {
  if (!Array.isArray(transcript) || !transcript.length) return "";
  const recent = transcript.slice(-10);
  const lines = recent.map((entry) => `[${String(entry.role || "").toUpperCase()}] ${String(entry.content || "")}`);
  return `[RECOVERED TRANSCRIPT]\n${lines.join("\n")}\n[END RECOVERED TRANSCRIPT]`;
}

function composeMessageWithTranscript(message, transcript) {
  const transcriptContext = buildRecoveredTranscriptContext(transcript);
  if (!transcriptContext) return message;
  return `${transcriptContext}\n\n[USER]\n${message}`;
}

function loadSessionRegistry() {
  try {
    const raw = fs.readFileSync(SESSION_REGISTRY_FILE, "utf-8");
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") return parsed;
  } catch {}
  return {};
}

function saveSessionRegistry(registry) {
  try {
    fs.writeFileSync(SESSION_REGISTRY_FILE, JSON.stringify(registry, null, 2), "utf-8");
  } catch {}
}

function readSessionId(conversationId = "default") {
  const convId = normalizeConversationId(conversationId);
  try {
    if (convId === "default") {
      return fs.readFileSync(SESSION_FILE, "utf-8").trim() || null;
    }
    const registry = loadSessionRegistry();
    return registry[convId] || null;
  } catch {
    return null;
  }
}

function saveSessionId(sessionId, conversationId = "default") {
  if (!sessionId) return;
  const convId = normalizeConversationId(conversationId);
  try {
    if (convId === "default") {
      fs.writeFileSync(SESSION_FILE, sessionId);
      return;
    }
    const registry = loadSessionRegistry();
    registry[convId] = sessionId;
    saveSessionRegistry(registry);
  } catch {}
}

function clearSessionId(conversationId = "default") {
  const convId = normalizeConversationId(conversationId);
  try {
    if (convId === "default") {
      fs.unlinkSync(SESSION_FILE);
      return;
    }
    const registry = loadSessionRegistry();
    if (registry[convId]) {
      delete registry[convId];
      saveSessionRegistry(registry);
    }
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

function normalizeMemorySearchPayload(payload) {
  if (payload && Array.isArray(payload.results)) {
    return payload;
  }
  const text = Array.isArray(payload?.content)
    ? payload.content
        .map((block) => {
          if (!block || typeof block !== "object") {
            return "";
          }
          if (typeof block.text === "string") {
            return block.text;
          }
          return typeof block.content === "string" ? block.content : "";
        })
        .filter(Boolean)
        .join("\n")
        .trim()
    : "";
  return {
    ok: payload?.ok !== false,
    results: text ? [{ text }] : [],
    raw: payload || null,
  };
}

function fileRead(targetPath, limit = 0) {
  try {
    const filePath = normalizeWorkspacePath(targetPath);
    let content = fs.readFileSync(filePath, "utf-8");
    if ((limit || 0) > 0) {
      content = content.split(/\r?\n/).slice(0, Number(limit)).join("\n");
    }
    return {
      ok: true,
      content,
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
      return fileRead(input.path, input.limit || 0);
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

function sanitizedClaudeEnv() {
  const env = { ...process.env };
  delete env.ANTHROPIC_API_KEY;
  delete env.CLAUDE_API_KEY;
  return env;
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

function normalizeRequestedPath(raw = "") {
  return raw
    .trim()
    .replace(/^["'`]+|["'`]+$/g, "")
    .replace(/[?.!,;:]+$/g, "")
    .trim();
}

function deterministicReadRequest(message) {
  const firstLine = message.match(/first line of\s+([^\n]+?)(?:\s+and\s+return|\s+answer|$)/i);
  if (firstLine) {
    return { mode: "first_line", path: normalizeRequestedPath(firstLine[1]) };
  }
  const heading = message.match(/(?:heading at the top of|top of)\s+([^\n]+?)(?:\s+and|\s+answer|$)/i);
  if (heading) {
    return { mode: "heading", path: normalizeRequestedPath(heading[1]) };
  }
  return null;
}

function emitDeterministicToolFlow(runId, toolName, input, output, finalText) {
  const toolId = `det-${toolName}-${Date.now()}`;
  const assistantToolEvt = {
    type: "assistant",
    message: { role: "assistant", content: [{ type: "tool_use", id: toolId, name: toolName, input }] },
  };
  const toolResultEvt = { type: "tool_result", tool_use_id: toolId, content: toolResultContent(output) };
  const assistantTextEvt = {
    type: "assistant",
    message: { role: "assistant", content: [{ type: "text", text: finalText }], model: "deterministic-grounding" },
  };
  if (runId) {
    emitChatEvent(runId, assistantToolEvt);
    emitChatEvent(runId, toolResultEvt);
    emitChatEvent(runId, assistantTextEvt);
    emitChatEvent(runId, { type: "result", result: finalText, provider: "deterministic", total_cost_usd: 0 });
  }
  return { ok: true, provider: "deterministic", result: finalText, events: [assistantToolEvt, toolResultEvt, assistantTextEvt] };
}

function tryDeterministicGrounding(message, runId = null) {
  const request = deterministicReadRequest(message || "");
  if (!request?.path) return null;
  const readResult = fileRead(request.path, request.mode === "first_line" ? 1 : 20);
  if (!readResult.ok) return null;
  let finalText = "";
  if (request.mode === "first_line") {
    finalText = (readResult.content || "").split(/\r?\n/)[0] || "";
  } else {
    finalText = (readResult.content || "")
      .split(/\r?\n/)
      .map((line) => line.trim())
      .find((line) => line.startsWith("#")) || "";
  }
  if (!finalText) return null;
  return emitDeterministicToolFlow(
    runId,
    "read_file",
    { path: request.path, limit: request.mode === "first_line" ? 1 : 20 },
    readResult,
    finalText,
  );
}

function runClaudeAttempt(prompt, opts = {}) {
  const conversationId = normalizeConversationId(opts.session_id);
  const sessionId = opts.resume ? readSessionId(conversationId) : null;
  const args = [CLAUDE_CLI, "-p", prompt, "--output-format", "stream-json", "--verbose", "--dangerously-skip-permissions"];
  if (sessionId) args.push("--resume", sessionId);
  if (opts.effort) args.push("--effort", opts.effort);
  if (opts.model) args.push("--model", opts.model);
  return new Promise((resolve) => {
    const proc = spawn(NODE_EXE, args, {
      cwd: WORK_DIR,
      env: sanitizedClaudeEnv(),
      stdio: ["ignore", "pipe", "pipe"],
    });
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
          if (evt.type === "result" && evt.session_id) saveSessionId(evt.session_id, conversationId);
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
  const transcript = Array.isArray(opts.priorTranscript) ? [...opts.priorTranscript] : [];
  const emitted = [];
  let usedFreshSession = false;
  const conversationId = normalizeConversationId(opts.session_id);
  for (let turn = 0; turn < TOOL_LOOP_LIMIT; turn += 1) {
    const prompt = buildClaudePrompt(message, transcript);
    const attempt = await runClaudeAttempt(prompt, { ...opts, resume: !usedFreshSession });
    if (!attempt.ok) {
      if (!usedFreshSession && isStaleResumeError(attempt.error || "")) {
        clearSessionId(conversationId);
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
      const resultEvt = { type: "result", result: attempt.text, session_id: readSessionId(conversationId), provider: "claude" };
      emitChatEvent(runId, resultEvt);
      emitted.push(resultEvt);
      return { ok: true, provider: "claude", result: attempt.text, events: emitted, session_id: readSessionId(conversationId) };
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

function groqApiKey() {
  let apiKey = process.env.GROQ_API_KEY || "";
  if (!apiKey) {
    try {
      apiKey = fs.readFileSync(path.join(WORK_DIR, ".groq-api-key"), "utf-8").trim();
    } catch {}
  }
  if (!apiKey) throw new Error("missing Groq API key");
  return apiKey;
}

async function callGroqChat(messages, options = {}) {
  const response = await fetch(GROQ_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${groqApiKey()}`,
      "User-Agent": "Karma-Nexus-Electron/1.0",
    },
    body: JSON.stringify({
      model: GROQ_MODEL,
      messages,
      max_tokens: options.maxTokens || 1024,
      temperature: options.temperature ?? 0,
      ...(options.tools ? { tools: options.tools, tool_choice: options.toolChoice || "auto" } : {}),
    }),
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Groq ${response.status}: ${text.slice(0, 300)}`);
  }
  return response.json();
}

async function callGroq(message, runId = null) {
  const messages = [
    {
      role: "system",
      content: "You are Karma inside the Nexus harness. Use the provided tools when you need grounded file, git, or shell data. Do not guess about workspace state. After tool results are returned, continue. When done, answer in plain text only.",
    },
    { role: "user", content: message },
  ];
  for (let turn = 0; turn < TOOL_LOOP_LIMIT; turn += 1) {
    const data = await callGroqChat(messages, { tools: GROQ_TOOL_DEFS, toolChoice: "auto", temperature: 0 });
    const choice = data.choices?.[0] || {};
    const msg = choice.message || {};
    const toolCalls = msg.tool_calls || [];
    const content = (msg.content || "").trim();
    if (!toolCalls.length) {
      const assistantEvt = {
        type: "assistant",
        message: { role: "assistant", content: [{ type: "text", text: content }], model: data.model || GROQ_MODEL },
      };
      if (runId) emitChatEvent(runId, assistantEvt);
      return {
        ok: true,
        provider: "groq",
        result: content,
        model: data.model || GROQ_MODEL,
        events: [assistantEvt],
      };
    }
    messages.push({
      role: "assistant",
      content: msg.content || null,
      tool_calls: toolCalls,
    });
    for (const [idx, toolCall] of toolCalls.entries()) {
      const toolId = toolCall.id || `${toolCall.function?.name || "tool"}-${Date.now()}-${turn}-${idx}`;
      let toolInput = {};
      try {
        toolInput = JSON.parse(toolCall.function?.arguments || "{}");
      } catch {}
      const assistantEvt = {
        type: "assistant",
        message: {
          role: "assistant",
          content: [{ type: "tool_use", id: toolId, name: toolCall.function?.name || "", input: toolInput }],
        },
      };
      if (runId) emitChatEvent(runId, assistantEvt);
      const toolOutput = await executeTool(toolCall.function?.name || "", toolInput);
      const toolEvt = { type: "tool_result", tool_use_id: toolId, content: toolResultContent(toolOutput) };
      if (runId) emitChatEvent(runId, toolEvt);
      messages.push({
        role: "tool",
        tool_call_id: toolId,
        content: JSON.stringify(toolOutput),
      });
    }
  }
  throw new Error("Groq tool loop limit exceeded");
}

async function callOpenRouter(message, runId = null) {
  if (!OPENROUTER_API_KEY) {
    throw new Error("missing OpenRouter API key");
  }
  const models = [OPENROUTER_MODEL, OPENROUTER_FALLBACK_MODEL, OPENROUTER_THIRD_MODEL];
  let lastError = null;
  for (const model of models) {
    try {
      const response = await fetch(OPENROUTER_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENROUTER_API_KEY}`,
          "HTTP-Referer": "https://hub.arknexus.net",
          "X-Title": "Karma Nexus Electron",
        },
        body: JSON.stringify({
          model,
          messages: [{ role: "user", content: message }],
          max_tokens: 1024,
          temperature: 0.1,
        }),
        signal: AbortSignal.timeout(30000),
      });
      if (!response.ok) {
        const text = await response.text();
        if (response.status === 429) {
          lastError = new Error(`OpenRouter ${response.status} (${model}): ${text.slice(0, 200)}`);
          continue;
        }
        throw new Error(`OpenRouter ${response.status} (${model}): ${text.slice(0, 300)}`);
      }
      const data = await response.json();
      const content = (data.choices?.[0]?.message?.content || "").trim();
      const usedModel = data.model || model;
      const assistantEvt = {
        type: "assistant",
        message: { role: "assistant", content: [{ type: "text", text: content }], model: usedModel },
      };
      if (runId) emitChatEvent(runId, assistantEvt);
      if (runId) emitChatEvent(runId, { type: "result", result: content, provider: "openrouter", total_cost_usd: 0 });
      return {
        ok: true,
        provider: "openrouter",
        result: content,
        model: usedModel,
        events: [assistantEvt],
      };
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error("OpenRouter failed");
}

async function callCortex(message) {
  const response = await fetch(`${CORTEX_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: message }),
    signal: AbortSignal.timeout(12000),
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

async function callLocalOllama(message) {
  const response = await fetch(`${OLLAMA_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: LOCAL_OLLAMA_MODEL,
      messages: [{ role: "user", content: message }],
      stream: false,
      options: { num_predict: 512, temperature: 0.1 },
    }),
    signal: AbortSignal.timeout(12000),
  });
  if (!response.ok) {
    throw new Error(`Ollama ${response.status}`);
  }
  const data = await response.json();
  return {
    ok: true,
    provider: "ollama",
    result: (data.message?.content || "").trim(),
    raw: data,
  };
}

async function runChatCascade(message, opts = {}, runId = null) {
  const deterministic = tryDeterministicGrounding(message, runId);
  if (deterministic) return deterministic;
  const transcript = Array.isArray(opts.priorTranscript) ? opts.priorTranscript : [];
  const contextualMessage = composeMessageWithTranscript(message, transcript);
  if (EMERGENCY_INDEPENDENT) {
    emitChatEvent(runId, { type: "error", error: "Emergency independent mode active: skipping Claude primary." });
    try {
      return await callOpenRouter(contextualMessage, runId);
    } catch (openRouterError) {
      emitChatEvent(runId, { type: "error", error: `OpenRouter unavailable, falling back: ${openRouterError.message}` });
    }
  }
  try {
    return await runClaudeHarness(message, opts, runId);
  } catch (claudeError) {
    emitChatEvent(runId, { type: "error", error: `Claude unavailable, falling back: ${claudeError.message}` });
    try {
      return await callOpenRouter(contextualMessage, runId);
    } catch (openRouterError) {
      emitChatEvent(runId, { type: "error", error: `OpenRouter unavailable, falling back: ${openRouterError.message}` });
    }
    try {
      const groq = await callGroq(contextualMessage, runId);
      emitChatEvent(runId, { type: "result", result: groq.result, provider: "groq", total_cost_usd: 0 });
      return groq;
    } catch (groqError) {
      emitChatEvent(runId, { type: "error", error: `Groq unavailable, falling back: ${groqError.message}` });
      try {
        const ollama = await callLocalOllama(contextualMessage);
        const assistantEvt = {
          type: "assistant",
          message: { role: "assistant", content: [{ type: "text", text: ollama.result }], model: LOCAL_OLLAMA_MODEL },
        };
        emitChatEvent(runId, assistantEvt);
        emitChatEvent(runId, { type: "result", result: ollama.result, provider: "ollama", total_cost_usd: 0 });
        return { ...ollama, events: [assistantEvt] };
      } catch (ollamaError) {
        emitChatEvent(runId, { type: "error", error: `Local Ollama unavailable, falling back: ${ollamaError.message}` });
        const cortex = await callCortex(contextualMessage);
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
}

async function handleCCChat(message, opts = {}) {
  const runId = opts?.runId || `cc-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  currentCCRunId = runId;
  const conversationId = normalizeConversationId(opts.session_id);
  const priorTranscript = loadTranscript(conversationId, 100);
  appendTranscriptEntry(conversationId, { role: "user", content: message });
  try {
    const result = await runChatCascade(message, { ...opts, priorTranscript }, runId);
    if (result?.result) {
      appendTranscriptEntry(conversationId, { role: "assistant", content: String(result.result || "").slice(0, 2000) });
    }
    return result;
  } finally {
    currentCCRunId = null;
  }
}

async function runElectronSmoke() {
  const prompt = SMOKE_PROMPT.trim();
  const payload = { ok: false, smoke: true, prompt };
  try {
    if (!prompt) {
      throw new Error("KARMA_ELECTRON_SMOKE_PROMPT is required");
    }
    fs.mkdirSync(path.dirname(SMOKE_OUT), { recursive: true });
    const sessionId = `electron-smoke-${Date.now()}`;
    const directResult = await handleCCChat(prompt, {
      runId: "electron-smoke-direct",
      session_id: `${sessionId}-direct`,
    });
    payload.directResult = directResult;
    const script = `
      (async () => {
        const events = [];
        const runId = "electron-smoke-run";
        const stop = window.karma?.onChatEvent ? window.karma.onChatEvent((evt) => events.push(evt)) : null;
        try {
          const result = await window.karma.chat(${JSON.stringify(prompt)}, { runId, session_id: ${JSON.stringify(sessionId)} });
          return { ok: true, isElectron: window.karma?.isElectron === true, result, events };
        } catch (error) {
          return { ok: false, isElectron: window.karma?.isElectron === true, error: String(error), events };
        } finally {
          if (typeof stop === "function") stop();
        }
      })();
    `;
    const result = await mainWindow.webContents.executeJavaScript(script, true);
    const uiToken = `UI_MEM_${Date.now().toString(36)}`;
    const uiScript = `
      (async () => {
        const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
        const token = ${JSON.stringify(uiToken)};
        const authToken = ${JSON.stringify(HUB_CHAT_TOKEN)};
        const prompt = "Reply with exactly " + token + " and nothing else.";
        const hasKarma = !!window.karma;
        const hasHubTokenApi = !!window.karma?.hubToken;
        let hubTokenInfo = { ok: false, tokenLength: 0, error: null };
        if (hasHubTokenApi) {
          try {
            const tokenPayload = await window.karma.hubToken();
            hubTokenInfo = {
              ok: !!tokenPayload?.ok,
              tokenLength: (tokenPayload?.token || '').length,
              error: null,
            };
          } catch (error) {
            hubTokenInfo = {
              ok: false,
              tokenLength: 0,
              error: error?.message || String(error),
            };
          }
        }
        const setNativeValue = (element, value) => {
          const proto = element instanceof HTMLTextAreaElement
            ? window.HTMLTextAreaElement.prototype
            : window.HTMLInputElement.prototype;
          const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
          if (!setter) return false;
          setter.call(element, value);
          element.dispatchEvent(new Event('input', { bubbles: true }));
          element.dispatchEvent(new Event('change', { bubbles: true }));
          return true;
        };
        const gateInput = document.querySelector('input[placeholder="Enter token"]');
        if (gateInput) {
          const entered = setNativeValue(gateInput, authToken);
          const enterButton = Array.from(document.querySelectorAll('button'))
            .find((btn) => (btn.textContent || '').trim() === 'ENTER');
          if (!entered || !enterButton) {
            return { ok: false, error: 'gate controls not ready', hasKarma, hasHubTokenApi, hubTokenInfo };
          }
          enterButton.click();
          const gateStartedAt = Date.now();
          while (Date.now() - gateStartedAt < 30000) {
            await wait(250);
            if (!document.querySelector('input[placeholder="Enter token"]')) break;
          }
          if (document.querySelector('input[placeholder="Enter token"]')) {
            return {
              ok: false,
              error: 'gate authentication timed out',
              hasKarma,
              hasHubTokenApi,
              hubTokenInfo,
              storedTokenLength: (window.localStorage.getItem('karma-token') || '').length,
              composerPresent: Array.from(document.querySelectorAll('textarea'))
                .some((el) => (el.getAttribute('placeholder') || '').includes('Message Karma')),
              bodyText: (document.body?.innerText || '').slice(0, 500),
            };
          }
        }
        const composerStartedAt = Date.now();
        while (Date.now() - composerStartedAt < 30000) {
          const composerReady = Array.from(document.querySelectorAll('textarea'))
            .some((el) => (el.getAttribute('placeholder') || '').includes('Message Karma'));
          if (composerReady) break;
          await wait(250);
        }
        const composerReady = Array.from(document.querySelectorAll('textarea'))
          .some((el) => (el.getAttribute('placeholder') || '').includes('Message Karma'));
        if (!composerReady) {
          return { ok: false, error: 'composer not ready after auth' };
        }
        const listenerReadyStartedAt = Date.now();
        let listenerReady = !!window.__karmaSendMessageReady;
        while (!listenerReady && Date.now() - listenerReadyStartedAt < 10000) {
          await wait(100);
          listenerReady = !!window.__karmaSendMessageReady;
        }
        if (!listenerReady) {
          return { ok: false, error: 'send listener not ready after auth', listenerReady };
        }
        window.dispatchEvent(new CustomEvent('karma-send-message', { detail: prompt }));
        const startedAt = Date.now();
        while (Date.now() - startedAt < 240000) {
          await wait(500);
          const raw = window.localStorage.getItem('karma-messages') || '[]';
          let messages = [];
          try { messages = JSON.parse(raw); } catch {}
          const lastKarma = [...messages].reverse().find((msg) => msg && msg.role === 'karma' && msg.content);
          if (lastKarma && (lastKarma.content || '').includes(token)) {
            const memory = window.karma?.memorySearch
              ? await window.karma.memorySearch(token, 5)
              : { ok: false, error: 'memorySearch unavailable' };
            const hasMemoryHit = Array.isArray(memory?.results)
              && memory.results.some((item) => JSON.stringify(item).includes(token));
            if (hasMemoryHit) {
              return { ok: true, token, lastKarma, memory };
            }
          }
        }
        const finalRaw = window.localStorage.getItem('karma-messages') || '[]';
        let finalMessages = [];
        try { finalMessages = JSON.parse(finalRaw); } catch {}
        return {
          ok: false,
          error: 'ui smoke timed out',
          listenerReady,
          gatePresent: !!document.querySelector('input[placeholder="Enter token"]'),
          composerPresent: Array.from(document.querySelectorAll('textarea'))
            .some((el) => (el.getAttribute('placeholder') || '').includes('Message Karma')),
          messageCount: Array.isArray(finalMessages) ? finalMessages.length : -1,
          recentMessages: Array.isArray(finalMessages)
            ? finalMessages.slice(-4).map((msg) => ({
                role: msg?.role || null,
                content: typeof msg?.content === 'string' ? msg.content.slice(0, 120) : null,
              }))
            : [],
          bodyText: (document.body?.innerText || '').slice(0, 500),
        };
      })();
    `;
    const uiResult = await mainWindow.webContents.executeJavaScript(uiScript, true);
    payload.ok = !!directResult?.ok && !!result?.ok;
    payload.isElectron = !!result?.isElectron;
    payload.result = result?.result || null;
    payload.events = result?.events || [];
    payload.uiResult = uiResult || null;
    payload.ok = payload.ok && !!uiResult?.ok && !!uiResult?.memory?.results?.length;
    if (!payload.ok) payload.error = result?.error || "smoke failed";
    fs.writeFileSync(SMOKE_OUT, JSON.stringify(payload, null, 2));
    setTimeout(() => app.exit(payload.ok ? 0 : 1), 250);
  } catch (error) {
    payload.error = error.message;
    try {
      fs.mkdirSync(path.dirname(SMOKE_OUT), { recursive: true });
      fs.writeFileSync(SMOKE_OUT, JSON.stringify(payload, null, 2));
    } catch {}
    setTimeout(() => app.exit(1), 250);
  }
}

ipcMain.handle("file-read", (_event, p) => fileRead(p));
ipcMain.handle("file-write", (_event, p, c) => fileWrite(p, c));
ipcMain.handle("shell-exec", (_event, cmd) => shellExec(cmd));
ipcMain.handle("cc-chat", (_event, msg, opts) => handleCCChat(msg, opts || {}));
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
    const payload = await (await fetch(`${CLAUDEMEM_URL}/api/search?query=${encodeURIComponent(q)}&limit=${l || 10}`, {
      signal: AbortSignal.timeout(5000),
    })).json();
    return normalizeMemorySearchPayload(payload);
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
ipcMain.handle("hub-token", () => ({ ok: !!HUB_CHAT_TOKEN, token: HUB_CHAT_TOKEN || "" }));
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

process.on("uncaughtException", (error) => {
  runtimeLog("uncaught-exception", { message: error.message, stack: error.stack });
});

process.on("unhandledRejection", (reason) => {
  runtimeLog("unhandled-rejection", normalizeCrashDetails(reason));
});

app.on("child-process-gone", (_event, details) => {
  runtimeLog("child-process-gone", normalizeCrashDetails(details));
});

app.whenReady().then(() => {
  runtimeLog("app-ready", { smoke: SMOKE_MODE, workDir: WORK_DIR });
  createWindow();
  mainWindow.webContents.once("did-finish-load", () => {
    runtimeLog("did-finish-load", { smoke: SMOKE_MODE });
    if (SMOKE_MODE) runElectronSmoke();
  });
  if (SMOKE_MODE) {
    return;
  }
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
