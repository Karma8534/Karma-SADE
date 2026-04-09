const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('jprop6Harness', {
  runtime: () => ipcRenderer.invoke('harness:getRuntime'),
  readSessionEnvelope: () => ipcRenderer.invoke('harness:session:read'),
  writeSessionEnvelope: (session) => ipcRenderer.invoke('harness:session:write', session),
});
