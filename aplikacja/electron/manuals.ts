import {app,dialog,shell} from 'electron';
import type {BrowserWindow} from 'electron';
import {stat,copyFile} from 'node:fs/promises';
import path from 'node:path';
import type {ManualId,ManualInfo} from '../src/bridge';

const manuals:{id:ManualId;title:string;fileName:string}[]=[
 {id:'player',title:'Podręcznik gracza',fileName:'Persona_5_RPG_Podrecznik_Gracza.docx'},
 {id:'gm',title:'Podręcznik MG',fileName:'Persona_5_RPG_Podrecznik_GM.docx'},
 {id:'bestiary',title:'Bestiariusz',fileName:'Persona_5_RPG_Bestiariusz.docx'}
];
async function present(file:string){try{return(await stat(file)).isFile();}catch{return false;}}
async function projectDirectory(){
 const candidates=new Set<string>([path.resolve(app.getAppPath(),'..')]);
 let directory=path.dirname(app.getPath('exe'));
 for(let i=0;i<6;i++){candidates.add(directory);const parent=path.dirname(directory);if(parent===directory)break;directory=parent;}
 for(const candidate of candidates)if((await Promise.all(manuals.map(m=>present(path.join(candidate,m.fileName))))).every(Boolean))return candidate;
 return null;
}
async function locate(id:unknown){
 const manual=manuals.find(m=>m.id===id);if(!manual)throw new Error('Nieznany podręcznik.');
 const project=await projectDirectory();
 const directory=project??(app.isPackaged?path.join(process.resourcesPath,'podreczniki'):path.join(app.getAppPath(),'assets/manuals'));
 const file=path.join(directory,manual.fileName),info=await stat(file);
 if(!info.isFile())throw new Error('Nie znaleziono podręcznika.');
 return{manual,file,info,source:project?'project' as const:'bundled' as const};
}
export async function listManuals():Promise<ManualInfo[]>{
 return Promise.all(manuals.map(async m=>{const result=await locate(m.id);return{...m,updatedAt:result.info.mtime.toISOString(),size:result.info.size,source:result.source};}));
}
export async function openManual(id:unknown){const {file}=await locate(id);const error=await shell.openPath(file);if(error)throw new Error(error);}
export async function saveManual(win:BrowserWindow,id:unknown){
 const {manual,file}=await locate(id);
 const result=await dialog.showSaveDialog(win,{title:`Zapisz Word — ${manual.title}`,defaultPath:manual.fileName,filters:[{name:'Dokument Word',extensions:['docx']}]});
 if(result.canceled||!result.filePath)return{canceled:true};
 if(path.resolve(result.filePath).toLowerCase()===path.resolve(file).toLowerCase())throw new Error('Wybierz inne miejsce dla kopii, aby zachować plik źródłowy.');
 await copyFile(file,result.filePath);return{canceled:false,path:result.filePath};
}
