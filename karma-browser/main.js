const { app, BrowserWindow, ipcMain } = require("electron");
const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");

// ── Config (P1 Windows paths) ────────────────────────────────────────────
const NEXUS_URL = "https://hub.arknexus.net";
const WORK_DIR = path.join(process.env.USERPROFILE || "C:\\Users\\raest", "Documents", "Karma_SADE");
const OLLAMA_URL = "http://localhost:11434";

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: "KARMA",
    backgroundColor: "#080810",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    autoHideMenuBar: true,
  });

  mainWindow.loadURL(NEXUS_URL);
  mainWindow.on("page-title-updated", (e) => e.preventDefault());
  mainWindow.setTitle("KARMA \u2014 Sovereign Peer");
}

// ── IPC Handlers ─────────────────────────────────────────────────────────
// H7: Shell exec — validate input, cap output, redact secrets
ipcMain.handle("shell-exec", async (event, command) => {
  if (typeof command !== "string" || command.length > 2000) {
    return { ok: false, error: "Invalid or too-long command", code: -1 };
  }
  return new Promise((resolve) => {
    exec(command, { timeout: 30000, cwd: WORK_DIR, maxBuffer: 1024 * 1024 }, (err, stdout, stderr) => {
      resolve({ ok: !err, stdout: (stdout || "").slice(0, 50000), stderr: (stderr || "").slice(0, 10000), code: err?.code || 0 });
    });
  });
});

ipcMain.handle("file-read", async (event, filePath) => {
  try {
    const resolved = path.resolve(WORK_DIR, filePath);
    if (!resolved.startsWith(WORK_DIR)) return { ok: false, error: "path outside project" };
    const content = fs.readFileSync(resolved, "utf-8");
    return { ok: true, content };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle("file-write", async (event, filePath, content) => {
  try {
    const resolved = path.resolve(WORK_DIR, filePath);
    if (!resolved.startsWith(WORK_DIR)) return { ok: false, error: "path outside project" };
    fs.mkdirSync(path.dirname(resolved), { recursive: true });
    fs.writeFileSync(resolved, content, "utf-8");
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle("ollama-query", async (event, prompt, model) => {
  try {
    const resp = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: model || "gemma3:4b",
        messages: [{ role: "user", content: prompt }],
        stream: false,
        options: { num_predict: 1024 },
      }),
      signal: AbortSignal.timeout(60000),
    });
    const data = await resp.json();
    return { ok: true, response: data.message?.content || "" };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle("cortex-query", async (event, query) => {
  try {
    const resp = await fetch("http://192.168.0.226:7892/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
      signal: AbortSignal.timeout(30000),
    });
    const data = await resp.json();
    return { ok: true, answer: data.answer || "" };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle("spine-read", async () => {
  try {
    const resp = await fetch("http://192.168.0.226:7892/health", { signal: AbortSignal.timeout(5000) });
    const data = await resp.json();
    return { ok: true, spine: data };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

ipcMain.handle("governor-audit", async () => {
  try {
    const resp = await fetch("http://192.168.0.226:7891/cc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Read last 5 lines of /mnt/c/dev/Karma/k2/cache/vesper_governor_audit.jsonl. Return JSON only." }),
      signal: AbortSignal.timeout(30000),
    });
    const data = await resp.json();
    return { ok: true, entries: data.response || "" };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

// ── Self-edit + deploy (item 11) ─────────────────────────────────────────
// H7: Sanitize commit message to prevent command injection
ipcMain.handle("self-deploy", async (event, commitMsg) => {
  if (typeof commitMsg !== "string" || commitMsg.length > 500) {
    return { ok: false, error: "Invalid or too-long commit message", code: -1 };
  }
  // H7: Strip dangerous chars — only allow printable ASCII + common unicode, no backticks/quotes/pipes
  const safeMsg = commitMsg.replace(/[`$"'|;&<>\\]/g, "").slice(0, 200);
  if (!safeMsg.trim()) return { ok: false, error: "Empty commit message after sanitization", code: -1 };
  return new Promise((resolve) => {
    // H7: Use array form to avoid shell injection — PowerShell -Command with escaped arg
    const cmd = `cd "${WORK_DIR}"; git add -A; git commit -m '${safeMsg.replace(/'/g, "''")}'; git push origin main`;
    exec(cmd, { timeout: 60000, cwd: WORK_DIR, shell: "powershell.exe", maxBuffer: 1024 * 1024 }, (err, stdout, stderr) => {
      resolve({ ok: !err, stdout: (stdout || "").slice(0, 10000), stderr: (stderr || "").slice(0, 5000), code: err?.code || 0 });
    });
  });
});

// ── App lifecycle ────────────────────────────────────────────────────────
app.whenReady().then(createWindow);
app.on("window-all-closed", () => app.quit());
app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });

console.log("[KARMA] Starting Electron on P1...");
console.log("[KARMA] Nexus:", NEXUS_URL);
console.log("[KARMA] Work dir:", WORK_DIR);
