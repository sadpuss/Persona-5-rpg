// Kopie do paczki aplikacji. Główne Wordy są tylko odczytywane.
const fs=require('node:fs/promises'),path=require('node:path'),crypto=require('node:crypto');
const names=['Persona_5_RPG_Podrecznik_Gracza.docx','Persona_5_RPG_Podrecznik_GM.docx','Persona_5_RPG_Bestiariusz.docx'];
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
(async()=>{
 const root=path.resolve(__dirname,'../..'),destination=path.resolve(__dirname,'../assets/manuals');await fs.mkdir(destination,{recursive:true});
 for(const name of names){
  const source=path.join(root,name),bytes=await fs.readFile(source),info=await fs.stat(source),target=path.join(destination,name);
  await fs.writeFile(target,bytes);
  if(hash(await fs.readFile(source))!==hash(bytes))throw new Error(`Podręcznik zmienił się podczas kopiowania: ${name}. Zbuduj aplikację ponownie.`);
  await fs.utimes(target,info.atime,info.mtime);
 }
 console.log('Dołączono aktualne kopie trzech podręczników Word.');
})().catch(error=>{console.error(error);process.exitCode=1;});
