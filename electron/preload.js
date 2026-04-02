const { contextBridge, ipcRenderer } = require("electron");

// KARMA NEXUS IPC Bridge (S155)
// Every capability CC has, Karma has through this bridge.
contextBridge.exposeInMainWorld("karma", {
  isElectron: true,
  isNexus: true,

  // File operations (with checkpointing)
  fileRead: (path) => ipcRenderer.invoke("file-read", path),
  fileWrite: (path, content) => ipcRenderer.invoke("file-write", path, content),
  showOpenDialog: () => ipcRenderer.invoke("show-open-dialog"),

  // Shell execution
  shellExec: (command) => ipcRenderer.invoke("shell-exec", command),

  // CC --resume (the brain)
  chat: (message, options) => ipcRenderer.invoke("cc-chat", message, options),
  cancel: () => ipcRenderer.invoke("cc-cancel"),

  // Cortex (K2 working memory)
  cortexQuery: (query) => ipcRenderer.invoke("cortex-query", query),
  cortexContext: () => ipcRenderer.invoke("cortex-context"),

  // Ollama (local inference)
  ollamaQuery: (prompt, model) => ipcRenderer.invoke("ollama-query", prompt, model),

  // Claude-mem (persistent memory)
  memorySearch: (query, limit) => ipcRenderer.invoke("memory-search", query, limit),
  memorySave: (text, title) => ipcRenderer.invoke("memory-save", text, title),

  // Evolution (Vesper pipeline)
  spineRead: () => ipcRenderer.invoke("spine-read"),

  // Git
  gitStatus: () => ipcRenderer.invoke("git-status"),
});
