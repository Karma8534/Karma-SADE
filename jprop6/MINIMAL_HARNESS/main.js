const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

const HUB_URL = process.env.JPROP6_HUB_URL || 'https://hub.arknexus.net';
const SESSION_FILE = path.join(app.getPath('userData'), 'session-contract.json');

function readSessionFile() {
  if (!fs.existsSync(SESSION_FILE)) return null;
  try {
    return JSON.parse(fs.readFileSync(SESSION_FILE, 'utf8'));
  } catch {
    return null;
  }
}

function writeSessionFile(payload) {
  const envelope = {
    schema_version: 'jprop6.v1',
    written_at: new Date().toISOString(),
    session: payload || {},
  };
  fs.writeFileSync(SESSION_FILE, JSON.stringify(envelope, null, 2), 'utf8');
  return envelope;
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 820,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  win.webContents.on('did-fail-load', (_event, code, desc, validatedURL) => {
    const fallback = path.join(__dirname, 'renderer', 'fallback.html');
    const target = validatedURL || HUB_URL;
    const query = `?target=${encodeURIComponent(target)}&code=${encodeURIComponent(String(code))}&desc=${encodeURIComponent(desc || '')}`;
    win.loadFile(fallback + query);
  });

  win.loadURL(HUB_URL);
}

ipcMain.handle('harness:getRuntime', () => ({
  hub_url: HUB_URL,
  user_data: app.getPath('userData'),
  session_file: SESSION_FILE,
  scaffold: true,
  capabilities: {
    hub_embed: true,
    continuity_envelope: true,
    shell_exec: false,
    code_editing: false,
    multi_agent_orchestration: false,
  },
}));

ipcMain.handle('harness:session:read', () => {
  return readSessionFile();
});

ipcMain.handle('harness:session:write', (_event, payload) => {
  return writeSessionFile(payload);
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
