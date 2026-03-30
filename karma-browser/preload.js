const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("karma", {
  shellExec: (command) => ipcRenderer.invoke("shell-exec", command),
  fileRead: (path) => ipcRenderer.invoke("file-read", path),
  fileWrite: (path, content) => ipcRenderer.invoke("file-write", path, content),
  ollamaQuery: (prompt, model) => ipcRenderer.invoke("ollama-query", prompt, model),
  cortexQuery: (query) => ipcRenderer.invoke("cortex-query", query),
  spineRead: () => ipcRenderer.invoke("spine-read"),
  governorAudit: () => ipcRenderer.invoke("governor-audit"),
  selfDeploy: (commitMsg) => ipcRenderer.invoke("self-deploy", commitMsg),
  autoUpdate: () => ipcRenderer.invoke("auto-update"),
  relaunch: () => ipcRenderer.invoke("relaunch"),
  isElectron: true,
});
