const { app, BrowserWindow, ipcMain, shell, dialog, Tray, Menu } = require("electron");
const { exec, spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

// KARMA NEXUS — Electron Harness (S155)
const WORK_DIR = process.platform === "win32" ? "C:\Users\raest\Documents\Karma_SADE" : "/mnt/c/dev/Karma/k2/cache";
const CORTEX_URL = "http://192.168.0.226:7892";
const CLAUDEMEM_URL = "http://127.0.0.1:37778";
const OLLAMA_URL = process.platform === "win32" ? "http://localhost:11434" : "http://172.22.240.1:11434";
const BOUNDS_FILE = path.join(app.getPath("userData"), "karma_bounds.json");
const SESSION_FILE = path.join(app.getPath("home"), ".karma_electron_session_id");
const FRONTEND_DIR = path.join(__dirname, "frontend", "out");
const NEXUS_URL = "https://hub.arknexus.net";
let mainWindow, tray, currentCCProc = null;

function createWindow() {
  let saved; try { saved = JSON.parse(fs.readFileSync(BOUNDS_FILE, "utf-8")); } catch { saved = null; }
  mainWindow = new BrowserWindow({
    width: saved?.width || 1200, height: saved?.height || 800, x: saved?.x, y: saved?.y,
    title: "KARMA — The Nexus", backgroundColor: "#0d0d0f",
    icon: path.join(__dirname, "icon.png"),
    webPreferences: { preload: path.join(__dirname, "preload.js"), contextIsolation: true, nodeIntegration: false },
    autoHideMenuBar: true,
  });
  if (fs.existsSync(path.join(FRONTEND_DIR, "index.html"))) {
    mainWindow.loadFile(path.join(FRONTEND_DIR, "index.html"));
  } else { mainWindow.loadURL(NEXUS_URL); }
  mainWindow.on("page-title-updated", e => e.preventDefault());
  mainWindow.setTitle("KARMA — The Nexus");
  mainWindow.on("close", () => { try { fs.writeFileSync(BOUNDS_FILE, JSON.stringify(mainWindow.getBounds())); } catch {} });
  mainWindow.webContents.on("before-input-event", (event, input) => {
    if (input.key === "Escape" && currentCCProc) { currentCCProc.kill(); currentCCProc = null; }
  });
}

// IPC: File ops with checkpointing
ipcMain.handle("file-read", (e, p) => { try { const f=path.resolve(WORK_DIR,p); return {ok:true,content:fs.readFileSync(f,"utf-8"),size:fs.statSync(f).size}; } catch(e) { return {ok:false,error:e.message}; }});
ipcMain.handle("file-write", (e, p, c) => {
  const f=path.resolve(WORK_DIR,p), cpDir=path.join(app.getPath("userData"),"checkpoints");
  try { fs.mkdirSync(cpDir,{recursive:true}); if(fs.existsSync(f)){fs.copyFileSync(f,path.join(cpDir,crypto.createHash("sha256").update(p).digest("hex").slice(0,8)+"_"+Date.now()+".bak"));} fs.mkdirSync(path.dirname(f),{recursive:true}); fs.writeFileSync(f,c,"utf-8"); return {ok:true}; } catch(e) { return {ok:false,error:e.message}; }
});
ipcMain.handle("shell-exec", (e, cmd) => new Promise(r => exec(cmd, {timeout:30000,cwd:WORK_DIR}, (err,out,serr) => r({ok:!err,stdout:out||"",stderr:serr||"",code:err?.code||0}))));
ipcMain.handle("cc-chat", (e, msg, opts) => new Promise(r => {
  const sid = (() => { try { return fs.readFileSync(SESSION_FILE,"utf-8").trim(); } catch { return null; }})();
  const cmd = [process.platform==="win32"?"C:\Program Files\nodejs\node.exe":"/usr/bin/node",
    process.platform==="win32"?path.join(process.env.APPDATA||"","npm","node_modules","@anthropic-ai","claude-code","cli.js"):"/usr/local/bin/claude",
    "-p",msg,"--output-format","json","--dangerously-skip-permissions"];
  if(sid) cmd.push("--resume",sid); if(opts?.effort) cmd.push("--effort",opts.effort);
  currentCCProc = spawn(cmd[0],cmd.slice(1),{cwd:WORK_DIR}); let out="";
  currentCCProc.stdout.on("data",d=>out+=d); currentCCProc.on("close",code=>{currentCCProc=null;
    for(const l of out.split("\n")){try{const d=JSON.parse(l.trim());if(d.type==="result"){if(d.session_id)try{fs.writeFileSync(SESSION_FILE,d.session_id)}catch{};r({ok:true,result:d.result||"",session_id:d.session_id});return;}}catch{}}
    r({ok:false,error:"CC exit "+code}); }); currentCCProc.on("error",e=>{currentCCProc=null;r({ok:false,error:e.message});}); setTimeout(()=>{if(currentCCProc){currentCCProc.kill();r({ok:false,error:"timeout"});}},180000);
}));
ipcMain.handle("cc-cancel", () => { if(currentCCProc){currentCCProc.kill();currentCCProc=null;return{ok:true};} return{ok:false}; });
ipcMain.handle("cortex-query", async(e,q) => { try { const r=await fetch(CORTEX_URL+"/query",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:q}),signal:AbortSignal.timeout(30000)}); return await r.json(); } catch(e) { return {ok:false,error:e.message}; }});
ipcMain.handle("cortex-context", async() => { try { return await (await fetch(CORTEX_URL+"/context",{signal:AbortSignal.timeout(30000)})).json(); } catch(e) { return {ok:false,error:e.message}; }});
ipcMain.handle("ollama-query", async(e,p,m) => { try { const r=await fetch(OLLAMA_URL+"/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:m||"qwen3.5:4b",messages:[{role:"user",content:p}],stream:false,options:{num_predict:1024}}),signal:AbortSignal.timeout(60000)}); const d=await r.json(); return {ok:true,response:d.message?.content||""}; } catch(e) { return {ok:false,error:e.message}; }});
ipcMain.handle("memory-search", async(e,q,l) => { try { return await (await fetch(CLAUDEMEM_URL+"/api/search?query="+encodeURIComponent(q)+"&limit="+(l||10),{signal:AbortSignal.timeout(5000)})).json(); } catch(e) { return {ok:false,error:e.message}; }});
ipcMain.handle("memory-save", async(e,t,title) => { try { return await (await fetch(CLAUDEMEM_URL+"/api/memory/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:t,title,project:"Karma_SADE"}),signal:AbortSignal.timeout(5000)})).json(); } catch(e) { return {ok:false,error:e.message}; }});
ipcMain.handle("spine-read", async() => { try { return await (await fetch(CORTEX_URL+"/spine",{signal:AbortSignal.timeout(5000)})).json(); } catch(e) { return {ok:false,error:e.message}; }});
ipcMain.handle("git-status", () => new Promise(r => exec("git status --porcelain -b",{cwd:WORK_DIR,timeout:5000},(err,out)=>{const l=(out||"").trim().split("\n");r({ok:true,branch:l[0]?.replace("## ","")||"?",changed:l.slice(1).filter(x=>x.trim()).length,files:l.slice(1).slice(0,20)});})));
ipcMain.handle("show-open-dialog", async() => { const r=await dialog.showOpenDialog(mainWindow,{properties:["openFile","multiSelections"]}); return {ok:!r.canceled,paths:r.filePaths||[]}; });

app.whenReady().then(() => { createWindow(); try { const t=new Tray(path.join(__dirname,"icon.png")); t.setToolTip("Karma Nexus"); t.setContextMenu(Menu.buildFromTemplate([{label:"Show",click:()=>mainWindow?.show()},{label:"Hide",click:()=>mainWindow?.hide()},{type:"separator"},{label:"Quit",click:()=>app.quit()}])); t.on("click",()=>mainWindow?.show()); tray=t; } catch {} });
app.on("window-all-closed", () => { if(process.platform!=="darwin") app.quit(); });
