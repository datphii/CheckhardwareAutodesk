const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("autodeskAgent", {
  appInfo: () => ipcRenderer.invoke("app:info"),
  exportPdf: (title) => ipcRenderer.invoke("app:export-pdf", title),
  openUrl: (url) => ipcRenderer.invoke("app:open-url", url),
  getConfig: () => ipcRenderer.invoke("config:get"),
  setConfig: (settings) => ipcRenderer.invoke("config:set", settings),
  updateConfig: () => ipcRenderer.invoke("config:update"),
  health: () => ipcRenderer.invoke("agent:health"),
  options: () => ipcRenderer.invoke("agent:options"),
  hardware: () => ipcRenderer.invoke("agent:hardware"),
  softwareCheck: (body) => ipcRenderer.invoke("agent:software-check", body),
  networkCheck: () => ipcRenderer.invoke("agent:network-check"),
  networkConfig: () => ipcRenderer.invoke("agent:network-config"),
  updateNetwork: (body) => ipcRenderer.invoke("agent:update-network", body),
  updateAll: () => ipcRenderer.invoke("agent:update-all")
});
