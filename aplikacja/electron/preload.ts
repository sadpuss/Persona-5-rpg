import { contextBridge, ipcRenderer } from 'electron';
import type { DesktopAPI } from '../src/bridge';
const api: DesktopAPI = {
  loadDraft: () => ipcRenderer.invoke('draft:load'),
  saveDraft: data => ipcRenderer.invoke('draft:save', data),
  openCharacter: () => ipcRenderer.invoke('character:open'),
  saveCharacter: (data, name) => ipcRenderer.invoke('character:save', data, name),
  savePDF: name => ipcRenderer.invoke('cards:pdf', name),
  print: () => ipcRenderer.invoke('cards:print')
};
contextBridge.exposeInMainWorld('desktop', api);
