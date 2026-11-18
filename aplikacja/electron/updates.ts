import { app } from 'electron';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { autoUpdater } from 'electron-updater';

export function startUpdates() {
  if (!app.isPackaged || process.env.PERSONA_TEST_DATA) return;
  if (process.platform === 'linux' && !process.env.APPIMAGE) return;
  if (!existsSync(path.join(process.resourcesPath, 'app-update.yml'))) return;

  autoUpdater.autoDownload = true;
  autoUpdater.autoInstallOnAppQuit = true;
  autoUpdater.allowPrerelease = false;
  autoUpdater.on('error', error => console.warn('Błąd aktualizacji aplikacji:', error.message));

  const check = () => {
    void autoUpdater.checkForUpdates().catch(() => {
      // Błąd obsługuje zdarzenie „error”. Aplikacja nadal działa offline.
    });
  };
  setTimeout(check, 10_000).unref();
  setInterval(check, 4 * 60 * 60 * 1000).unref();
}
