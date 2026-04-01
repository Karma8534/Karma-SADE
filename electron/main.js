const { app, BrowserWindow, ipcMain, shell, dialog, Tray, Menu } = require("electron");
const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");

// ── Config ───────────────────────────────────────────────────────────────
const NEXUS_URL = "https://hub.arknexus.net";
const K2_CACHE = "/mnt/c/dev/Karma/k2/cache";
const OLLAMA_URL = "http://172.22.240.1:11434";
const CORTEX_URL = "http://localhost:7892";
const BOUNDS_FILE = path.join(K2_CACHE, "karma_window_bounds.json");

let mainWindow;
let tray;

function loadBounds() {
  try { return JSON.parse(fs.readFileSync(BOUNDS_FILE, "utf-8")); } catch { return null; }
}

function saveBounds() {
  if (!mainWindow) return;
  try { fs.writeFileSync(BOUNDS_FILE, JSON.stringify(mainWindow.getBounds())); } catch {}
}

function createWindow() {
  const saved = loadBounds();
  mainWindow = new BrowserWindow({
    width: saved?.width || 1200,
    height: saved?.height || 800,
    x: saved?.x,
    y: saved?.y,
    title: "KARMA",
    icon: path.join(__dirname, "icon.png"),
    backgroundColor: "#0d0d0f",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    autoHideMenuBar: true,
  });

  mainWindow.loadURL(NEXUS_URL);
  mainWindow.on("page-title-updated", (e) => e.preventDefault());
  mainWindow.setTitle("KARMA — Sovereign Peer");
  mainWindow.on("close", saveBounds);

  // Keyboard shortcuts
  mainWindow.webContents.on("before-input-event", (event, input) => {
    if (input.key === "Escape" && input.type === "keyDown") {
      mainWindow.webContents.executeJavaScript(
        "document.querySelector(\"#send-btn, button[class*=danger]\")?.click()"
      ).catch(() => {});
    }
  });
}

// ── System Tray ──────────────────────────────────────────────────────────
function createTray() {
  try {
    tray = new Tray(path.join(__dirname, "icon.png"));
    tray.setToolTip("Karma — Sovereign Peer");
    const contextMenu = Menu.buildFromTemplate([
      { label: "Show Karma", click: () => mainWindow?.show() },
      { label: "Hide", click: () => mainWindow?.hide() },
      { type: "separator" },
      { label: "Quit", click: () => app.quit() },
    ]);
    tray.setContextMenu(contextMenu);
    tray.on("click", () => mainWindow?.show());
  } catch (e) {
    console.log("[KARMA] Tray icon not available:", e.message);
  }
}

// ── IPC Handlers ─────────────────────────────────────────────────────────
ipcMain.handle("shell-exec", async (event, command) => {
  return new Promise((resolve) => {
    exec(command, { timeout: 30000, cwd: K2_CACHE }, (err, stdout, stderr) => {
      resolve({ ok: !err, stdout: stdout || "", stderr: stderr || "", code: err?.code || 0 });
    });
  });
});

ipcMain.handle("file-read", async (event, filePath) => {
  try { return { ok: true, content: fs.readFileSync(filePath, "utf-8") }; }
  catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle("file-write", async (event, filePath, content) => {
  try {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, content, "utf-8");
    return { ok: true };
  } catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle("show-open-dialog", async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ["openFile", "multiSelections"],
    filters: [
      { name: "All Files", extensions: ["*"] },
      { name: "Images", extensions: ["png", "jpg", "jpeg", "gif", "webp"] },
      { name: "Documents", extensions: ["md", "txt", "pdf", "json", "yaml"] },
    ],
  });
  return { ok: !result.canceled, paths: result.filePaths || [] };
});

ipcMain.handle("ollama-query", async (event, prompt, model) => {
  try {
    const resp = await fetch(OLLAMA_URL + "/api/chat", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: model || "qwen3.5:4b", messages: [{ role: "user", content: prompt }], stream: false, options: { num_predict: 1024 } }),
      signal: AbortSignal.timeout(60000),
    });
    const data = await resp.json();
    return { ok: true, response: data.message?.content || "" };
  } catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle("cortex-query", async (event, query) => {
  try {
    const resp = await fetch(CORTEX_URL + "/query", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }), signal: AbortSignal.timeout(30000),
    });
    const data = await resp.json();
    return { ok: true, answer: data.answer || "" };
  } catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle("spine-read", async () => {
  try { return { ok: true, spine: JSON.parse(fs.readFileSync(path.join(K2_CACHE, "vesper_identity_spine.json"), "utf-8")) }; }
  catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle("governor-audit", async () => {
  try {
    const lines = fs.readFileSync(path.join(K2_CACHE, "vesper_governor_audit.jsonl"), "utf-8")
      .trim().split("\n").filter(Boolean).slice(-10)
      .map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
    return { ok: true, entries: lines };
  } catch (e) { return { ok: false, error: e.message }; }
});

// ── App lifecycle ────────────────────────────────────────────────────────
app.whenReady().then(() => { createWindow(); createTray(); });
app.on("window-all-closed", () => app.quit());
app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });

console.log("[KARMA BROWSER] Starting...");
console.log("[KARMA BROWSER] Nexus:", NEXUS_URL);
