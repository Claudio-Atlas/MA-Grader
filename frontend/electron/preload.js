// electron/preload.js
// Secure bridge between renderer and main process

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // File dialogs
  openFile: (options) => ipcRenderer.invoke('dialog:openFile', options),
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  
  // Shell operations
  openPath: (path) => ipcRenderer.invoke('shell:openPath', path),
  
  // Clipboard
  copyToClipboard: (text) => ipcRenderer.invoke('clipboard:write', text),
  
  // Platform info
  platform: process.platform
});
