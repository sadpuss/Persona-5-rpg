export interface CharacterSummary { id: string; name: string; persona: string; level: number; updatedAt: string }
export interface LibraryResult { data: string; activeId: string; characters: CharacterSummary[]; recovered?: boolean }
export interface FileResult { canceled: boolean; path?: string; data?: string }
export interface DesktopAPI {
  loadLibrary(initialData: string): Promise<LibraryResult>;
  saveDraft(id: string, data: string): Promise<CharacterSummary[]>;
  selectCharacter(id: string): Promise<LibraryResult>;
  createCharacter(data: string): Promise<LibraryResult>;
  deleteCharacter(id: string, emptyData: string): Promise<LibraryResult>;
  openCharacter(): Promise<FileResult>;
  saveCharacter(data: string, name: string): Promise<FileResult>;
  savePDF(name: string): Promise<FileResult>;
  print(): Promise<void>;
}
declare global { interface Window { desktop: DesktopAPI } }
