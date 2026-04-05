const { contextBridge, ipcRenderer } = require("electron");

// KARMA NEXUS IPC Bridge (S156)
contextBridge.exposeInMainWorld("karma", {
  isElectron: true,
  isNexus: true,

  // File operations (with checkpointing)
  fileRead: (path) => ipcRenderer.invoke("file-read", path),
  fileWrite: (path, content) => ipcRenderer.invoke("file-write", path, content),
  showOpenDialog: () => ipcRenderer.invoke("show-open-dialog"),

  // Shell execution
  shellExec: (command) => ipcRenderer.invoke("shell-exec", command),

  // CC harness
  chat: (message, options) => ipcRenderer.invoke("cc-chat", message, options),
  cancel: () => ipcRenderer.invoke("cc-cancel"),
  onChatEvent: (handler) => {
    const listener = (_event, payload) => handler(payload);
    ipcRenderer.on("cc-chat-event", listener);
    return () => ipcRenderer.removeListener("cc-chat-event", listener);
  },

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
