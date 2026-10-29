import {readFile,writeFile,rename,copyFile,mkdir,stat,rm} from 'node:fs/promises';
import {randomUUID} from 'node:crypto';
import path from 'node:path';
import type {CharacterSummary,LibraryResult} from '../src/bridge';

interface Manifest { version:1; activeId:string; characters:CharacterSummary[] }
const MAX_BYTES=4*1024*1024;
const validId=(id:unknown):id is string=>typeof id==='string'&&/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/.test(id);
export function checkData(data:unknown):asserts data is string{
 if(typeof data!=='string'||Buffer.byteLength(data,'utf8')>MAX_BYTES)throw new Error('Plik postaci przekracza dopuszczalny rozmiar.');
 const c:unknown=JSON.parse(data);
 if(!c||typeof c!=='object'||!('format' in c)||c.format!==1)throw new Error('Nieprawidłowy format postaci.');
}
export async function readCharacter(file:string){
 if((await stat(file)).size>MAX_BYTES)throw new Error('Plik jest za duży.');
 const data=await readFile(file,'utf8');checkData(data);return data;
}
async function exists(file:string){try{await stat(file);return true;}catch(e){if((e as NodeJS.ErrnoException).code==='ENOENT')return false;throw e;}}
async function recover<T>(file:string,read:(file:string)=>Promise<T>):Promise<{value:T;recovered:boolean}>{
 try{return{value:await read(file),recovered:false};}
 catch(original){try{return{value:await read(file+'.bak'),recovered:true};}catch{throw original;}}
}
async function atomic(file:string,data:string,verify:(file:string)=>Promise<unknown>){
 await mkdir(path.dirname(file),{recursive:true});
 await writeFile(file+'.tmp',data,'utf8');
 if(await exists(file)){
  // Zastępuj kopię zapasową wyłącznie prawidłowym plikiem.
  try{await verify(file);await copyFile(file,file+'.bak');}catch{/* Zachowaj ostatnią dobrą kopię. */}
 }
 await rename(file+'.tmp',file);
}
function summary(id:string,data:string):CharacterSummary{
 const c=JSON.parse(data) as Record<string,unknown>;
 const exp=typeof c.exp==='number'&&Number.isFinite(c.exp)?Math.max(0,c.exp):0;
 return{id,name:typeof c.name==='string'?c.name.slice(0,120):'',persona:typeof c.persona==='string'?c.persona.slice(0,120):'',level:Math.min(99,Math.floor((1+Math.sqrt(1+exp*.08))/2)),updatedAt:new Date().toISOString()};
}
async function readManifest(file:string):Promise<Manifest>{
 if((await stat(file)).size>8*1024*1024)throw new Error('Biblioteka jest za duża.');
 const m=JSON.parse(await readFile(file,'utf8')) as Manifest;
 if(m.version!==1||!validId(m.activeId)||!Array.isArray(m.characters)||!m.characters.length||m.characters.length>10000)throw new Error('Nieprawidłowy spis postaci.');
 const ids=new Set<string>();
 for(const c of m.characters){
  if(!c||!validId(c.id)||ids.has(c.id)||typeof c.name!=='string'||typeof c.persona!=='string'||!Number.isInteger(c.level)||c.level<1||c.level>99||typeof c.updatedAt!=='string')throw new Error('Nieprawidłowy wpis biblioteki.');
  ids.add(c.id);
 }
 if(!ids.has(m.activeId))throw new Error('Brak aktywnej postaci w bibliotece.');
 return m;
}

/** Operacje są kolejkowane przez proces główny. Każda karta ma własny plik i kopię. */
export class CharacterLibrary{
 private manifest:Manifest|null=null;
 private readonly manifestPath:string;
 constructor(private readonly directory:string){this.manifestPath=path.join(directory,'biblioteka.json');}
 private file(id:string){if(!validId(id))throw new Error('Nieprawidłowy identyfikator postaci.');return path.join(this.directory,'postacie',id+'.json');}
 private current(){if(!this.manifest)throw new Error('Biblioteka nie została odczytana.');return this.manifest;}
 private async persist(m:Manifest){await atomic(this.manifestPath,JSON.stringify(m,null,2),readManifest);this.manifest=m;}
 private async result(recovered=false):Promise<LibraryResult>{
  const m=this.current(),read=await recover(this.file(m.activeId),readCharacter);
  return{data:read.value,activeId:m.activeId,characters:m.characters,recovered:recovered||read.recovered};
 }
 async load(initialData:string):Promise<LibraryResult>{
  checkData(initialData);
  if(this.manifest)return this.result();
  if(await exists(this.manifestPath)||await exists(this.manifestPath+'.bak')){
   const loaded=await recover(this.manifestPath,readManifest);this.manifest=loaded.value;return this.result(loaded.recovered);
  }
  // Pierwsze uruchomienie nowej wersji: przenieś dawną kartę, zachowując oryginał.
  const old=path.join(this.directory,'postac.json');
  const legacy=await exists(old)||await exists(old+'.bak')?await recover(old,readCharacter):null;
  const created=await this.createFirst(legacy?.value??initialData);
  return{...created,recovered:legacy?.recovered??false};
 }
 private async createFirst(data:string){
  const id=randomUUID();
  await atomic(this.file(id),data,readCharacter);
  await this.persist({version:1,activeId:id,characters:[summary(id,data)]});
  return this.result();
 }
 async save(id:string,data:string):Promise<CharacterSummary[]>{
  checkData(data);const m=this.current();
  if(!m.characters.some(c=>c.id===id))throw new Error('Nie znaleziono tej postaci w bibliotece.');
  await atomic(this.file(id),data,readCharacter);
  const next={...m,characters:m.characters.map(c=>c.id===id?summary(id,data):c)};
  await this.persist(next);return next.characters;
 }
 async create(data:string):Promise<LibraryResult>{
  checkData(data);const m=this.current(),id=randomUUID();
  await atomic(this.file(id),data,readCharacter);
  await this.persist({...m,activeId:id,characters:[...m.characters,summary(id,data)]});
  return this.result();
 }
 async select(id:string):Promise<LibraryResult>{
  const m=this.current();
  if(!m.characters.some(c=>c.id===id))throw new Error('Nie znaleziono tej postaci w bibliotece.');
  // Odczytaj przed zmianą aktywnej karty; błąd nie odbiera dostępu do poprzedniej.
  const loaded=await recover(this.file(id),readCharacter);
  await this.persist({...m,activeId:id});
  return{data:loaded.value,activeId:id,characters:this.current().characters,recovered:loaded.recovered};
 }
 async delete(id:string,emptyData:string):Promise<LibraryResult>{
  checkData(emptyData);const m=this.current();
  if(!m.characters.some(c=>c.id===id))throw new Error('Nie znaleziono tej postaci w bibliotece.');
  const remaining=m.characters.filter(c=>c.id!==id);
  if(!remaining.length){
   const replacement=randomUUID();await atomic(this.file(replacement),emptyData,readCharacter);
   remaining.push(summary(replacement,emptyData));
  }
  const next={...m,characters:remaining,activeId:m.activeId===id?remaining[0].id:m.activeId};
  await recover(this.file(next.activeId),readCharacter);
  await this.persist(next);
  // Zaktualizuj również kopię spisu, żeby usunięty wpis nie wrócił przy odzyskiwaniu.
  await this.persist(next);
  for(const suffix of ['', '.bak', '.tmp'])await rm(this.file(id)+suffix,{force:true});
  return this.result();
 }
}
