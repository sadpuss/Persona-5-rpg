export interface LoadResult { data: string | null; recovered?: boolean; error?: string }
export interface FileResult { canceled: boolean; path?: string; data?: string }
export interface DesktopAPI {
  loadDraft(): Promise<LoadResult>;
  saveDraft(data: string): Promise<void>;
  openCharacter(): Promise<FileResult>;
  saveCharacter(data: string, name: string): Promise<FileResult>;
  savePDF(name: string): Promise<FileResult>;
  print(): Promise<void>;
}
declare global { interface Window { desktop: DesktopAPI } }
