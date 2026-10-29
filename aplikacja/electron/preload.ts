import { contextBridge, ipcRenderer } from 'electron';
import type { DesktopAPI } from '../src/bridge';
const api: DesktopAPI = {
  loadLibrary: initialData => ipcRenderer.invoke('library:load', initialData),
  saveDraft: (id,data) => ipcRenderer.invoke('draft:save', id,data),
  selectCharacter: id => ipcRenderer.invoke('library:select', id),
  createCharacter: data => ipcRenderer.invoke('library:create', data),
  deleteCharacter: (id,emptyData) => ipcRenderer.invoke('library:delete', id,emptyData),
  openCharacter: () => ipcRenderer.invoke('character:open'),
  saveCharacter: (data, name) => ipcRenderer.invoke('character:save', data, name),
  savePDF: name => ipcRenderer.invoke('cards:pdf', name),
  print: () => ipcRenderer.invoke('cards:print'),
  listManuals:()=>ipcRenderer.invoke('manuals:list'),
  openManual:id=>ipcRenderer.invoke('manuals:open',id),
  saveManual:id=>ipcRenderer.invoke('manuals:save',id)
};
contextBridge.exposeInMainWorld('desktop', api);
