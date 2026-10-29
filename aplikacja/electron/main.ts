import { app, BrowserWindow, dialog, ipcMain, Menu, session } from 'electron';
import type { IpcMainInvokeEvent } from 'electron';
import { readFile, writeFile, rename, copyFile, mkdir, stat, mkdtemp, rm, rmdir } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

// Oddzielny katalog dla testów; nigdy nie nadpisują rzeczywistej karty.
if (process.env.PERSONA_TEST_DATA) app.setPath('userData', path.resolve(process.env.PERSONA_TEST_DATA));
app.setName('Take Your Heart');
if (!app.requestSingleInstanceLock()) app.exit(0);
let mainWindow: BrowserWindow | null = null;
app.on('second-instance', () => {
  if (mainWindow?.isMinimized()) mainWindow.restore();
  mainWindow?.show();
  mainWindow?.focus();
});
const rendererFile = path.join(__dirname, '../../dist/index.html');
const rendererURL = pathToFileURL(rendererFile).href;
const draftPath = () => path.join(app.getPath('userData'), 'postac.json');
const maxBytes = 4 * 1024 * 1024;

function authorize(event: IpcMainInvokeEvent) {
  if (!mainWindow || event.sender !== mainWindow.webContents || event.senderFrame !== event.sender.mainFrame || event.senderFrame?.url !== rendererURL) {
    throw new Error('Niedozwolone źródło żądania.');
  }
  return mainWindow;
}
function checkData(data: unknown): asserts data is string {
  if (typeof data !== 'string' || Buffer.byteLength(data, 'utf8') > maxBytes) throw new Error('Plik postaci przekracza dopuszczalny rozmiar.');
  const parsed: unknown = JSON.parse(data);
  if (!parsed || typeof parsed !== 'object' || !('format' in parsed) || parsed.format !== 1) throw new Error('Nieprawidłowy format postaci.');
}
async function readLimited(file: string) {
  if ((await stat(file)).size > maxBytes) throw new Error('Plik jest za duży.');
  const data = await readFile(file, 'utf8');
  checkData(data);
  return data;
}
function safeName(name: unknown) {
  return (typeof name === 'string' ? name : 'Persona RPG').replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').slice(0, 90).replace(/[. ]+$/, '') || 'Persona RPG';
}
async function exists(file: string) { try { await stat(file); return true; } catch { return false; } }
let saving: Promise<void> = Promise.resolve();
let pendingSaves = 0;
function registerIPC() {
  ipcMain.handle('draft:load', async event => {
    authorize(event);
    try {
      if (!(await exists(draftPath()))) return { data: null };
      return { data: await readLimited(draftPath()) };
    } catch {
      try { return { data: await readLimited(draftPath() + '.bak'), recovered: true }; }
      catch { return { data: null, error: 'Nie udało się odczytać automatycznego zapisu. Zachowano go na dysku. Możesz otworzyć własny plik postaci.' }; }
    }
  });
  ipcMain.handle('draft:save', (event, data: unknown) => {
    authorize(event); checkData(data);
    pendingSaves++;
    // Kolejka zapobiega wyścigom między kolejnymi zapisami z interfejsu.
    const operation = saving.catch(() => {}).then(async () => {
      await mkdir(app.getPath('userData'), { recursive: true });
      await writeFile(draftPath() + '.tmp', data, 'utf8');
      if (await exists(draftPath())) {
        // Uszkodzony zapis nie może zastąpić prawidłowej kopii zapasowej.
        try { await readLimited(draftPath()); await copyFile(draftPath(), draftPath() + '.bak'); } catch { /* Zachowaj wcześniejszą kopię. */ }
      }
      await rename(draftPath() + '.tmp', draftPath());
    });
    saving = operation.finally(() => { pendingSaves--; });
    return saving;
  });
  ipcMain.handle('character:open', async event => {
    const win = authorize(event);
    const result = await dialog.showOpenDialog(win, { title: 'Otwórz zapis postaci', properties: ['openFile'], filters: [{ name: 'Postać Persona RPG', extensions: ['json'] }] });
    if (result.canceled) return { canceled: true };
    return { canceled: false, data: await readLimited(result.filePaths[0]) };
  });
  ipcMain.handle('character:save', async (event, data: unknown, name: unknown) => {
    const win = authorize(event); checkData(data);
    const result = await dialog.showSaveDialog(win, { title: 'Zapisz postać do pliku', defaultPath: safeName(name) + '.json', filters: [{ name: 'Postać Persona RPG', extensions: ['json'] }] });
    if (result.canceled || !result.filePath) return { canceled: true };
    await writeFile(result.filePath, data, 'utf8');
    return { canceled: false, path: result.filePath };
  });
  ipcMain.handle('cards:pdf', async (event, name: unknown) => {
    const win = authorize(event);
    const result = await dialog.showSaveDialog(win, { title: 'Zapisz karty jako PDF', defaultPath: safeName(name) + ' — karty.pdf', filters: [{ name: 'Dokument PDF', extensions: ['pdf'] }] });
    if (result.canceled || !result.filePath) return { canceled: true };
    const pdf = await win.webContents.printToPDF({ printBackground: true, preferCSSPageSize: true, pageSize: 'A4', displayHeaderFooter: false });
    await writeFile(result.filePath, pdf);
    return { canceled: false, path: result.filePath };
  });
  ipcMain.handle('cards:print', async event => {
    const win = authorize(event);
    const pdf = await win.webContents.printToPDF({ printBackground: true, preferCSSPageSize: true, pageSize: 'A4', displayHeaderFooter: false });
    const directory = await mkdtemp(path.join(app.getPath('temp'), 'persona-podglad-'));
    const file = path.join(directory, 'Karty postaci.pdf');
    await writeFile(file, pdf);
    // Wbudowany czytnik PDF pokazuje rzeczywiste strony, skalę i przycisk drukarki.
    const preview = new BrowserWindow({ parent: win, width: 1050, height: 900, minWidth: 650, minHeight: 500,
      title: 'Podgląd wydruku — karty postaci', show: false, backgroundColor: '#ffffff',
      webPreferences: { nodeIntegration: false, contextIsolation: true, sandbox: true, plugins: true }
    });
    preview.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
    preview.webContents.on('will-navigate', navigation => navigation.preventDefault());
    preview.webContents.on('page-title-updated', titleEvent => titleEvent.preventDefault());
    preview.on('closed', () => { void rm(file, { force: true }).then(() => rmdir(directory)).catch(() => {}); });
    try {
      await preview.loadFile(file);
      if (!process.env.PERSONA_TEST_DATA) preview.show();
    } catch (error) {
      preview.close();
      throw error;
    }
  });
}
async function createWindow() {
  mainWindow = new BrowserWindow({ width: 1500, height: 1000, minWidth: 850, minHeight: 650, backgroundColor: '#ffffff', title: 'Take Your Heart — Persona RPG', show: false,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), nodeIntegration: false, contextIsolation: true, sandbox: true, webSecurity: true, spellcheck: false }
  });
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  mainWindow.webContents.on('will-navigate', event => event.preventDefault());
  mainWindow.webContents.on('will-attach-webview', event => event.preventDefault());
  mainWindow.once('ready-to-show', () => { if (!process.env.PERSONA_TEST_DATA) mainWindow?.show(); });
  mainWindow.on('closed', () => { mainWindow = null; });
  await mainWindow.loadFile(rendererFile);
}
app.whenReady().then(async () => {
  Menu.setApplicationMenu(null);
  session.defaultSession.setPermissionRequestHandler((_wc, _permission, callback) => callback(false));
  session.defaultSession.setPermissionCheckHandler(() => false);
  registerIPC();
  await createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) void createWindow(); });
}).catch(error => { dialog.showErrorBox('Nie udało się uruchomić kreatora', String(error)); app.quit(); });
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
// Dokończ rozpoczęty zapis przed zamknięciem aplikacji.
let canQuit = false;
app.on('before-quit', event => {
  if (canQuit || pendingSaves === 0) return;
  event.preventDefault();
  void saving.catch(() => {}).finally(() => { canQuit = true; app.quit(); });
});
