export interface CharacterSummary { id: string; name: string; persona: string; level: number; updatedAt: string }
export interface LibraryResult { data: string; activeId: string; characters: CharacterSummary[]; recovered?: boolean }
export interface FileResult { canceled: boolean; path?: string; data?: string }
export type ManualId='player'|'gm'|'bestiary';
export interface ManualInfo{id:ManualId;title:string;fileName:string;updatedAt:string;size:number;source:'project'|'bundled'}
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
  listManuals(): Promise<ManualInfo[]>;
  openManual(id:ManualId): Promise<void>;
  saveManual(id:ManualId): Promise<FileResult>;
}
declare global { interface Window { desktop: DesktopAPI } }
