import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,stat} from 'node:fs/promises';
import path from 'node:path';
import {CharacterLibrary} from '../electron/library';
import {fresh} from '../src/model';

const data=(name:string)=>JSON.stringify({...fresh(),name});
async function directory(){const root=path.resolve('qa-desktop');await mkdir(root,{recursive:true});return mkdtemp(path.join(root,'biblioteka-test-'));}
const file=(root:string,id:string)=>path.join(root,'postacie',id+'.json');

test('migracja poprzedniego zapisu zachowuje oryginał i tworzy jedną postać',async()=>{
 const dir=await directory(),old=data('Łucja');await writeFile(path.join(dir,'postac.json'),old);
 const store=new CharacterLibrary(dir),result=await store.load(data(''));
 assert.equal(result.data,old);assert.equal(result.characters.length,1);
 assert.equal(await readFile(path.join(dir,'postac.json'),'utf8'),old);
 assert.equal((await store.load(data(''))).characters.length,1);
});
test('nowe karty, przełączanie i ponowne uruchomienie zachowują oddzielne dane',async()=>{
 const dir=await directory(),store=new CharacterLibrary(dir),first=await store.load(data('Maja'));
 const second=await store.create(data('Jan'));assert.notEqual(second.activeId,first.activeId);
 assert.equal(second.characters.length,2);await store.save(second.activeId,data('Jan po sesji'));
 assert.equal((await store.select(first.activeId)).data,data('Maja'));
 const restarted=await new CharacterLibrary(dir).load(data(''));assert.equal(restarted.activeId,first.activeId);
 assert.equal((await new CharacterLibrary(dir).load(data(''))).characters.length,2);
 assert.equal((await store.select(second.activeId)).data,data('Jan po sesji'));
});
test('spóźniony zapis poprzedniej karty nie nadpisuje nowej ani aktywnego wyboru',async()=>{
 const dir=await directory(),store=new CharacterLibrary(dir),first=await store.load(data('Pierwsza'));
 const second=await store.create(data('Druga'));await store.save(first.activeId,data('Pierwsza po zmianie'));
 const restarted=await new CharacterLibrary(dir).load(data(''));
 assert.equal(restarted.activeId,second.activeId);assert.equal(restarted.data,data('Druga'));
 assert.equal((await store.select(first.activeId)).data,data('Pierwsza po zmianie'));
});
test('uszkodzona karta jest odtwarzana z jej własnej kopii',async()=>{
 const dir=await directory(),store=new CharacterLibrary(dir),first=await store.load(data('Pierwsza'));
 await store.save(first.activeId,data('Pierwsza zmieniona'));await writeFile(file(dir,first.activeId),'USZKODZONY ZAPIS');
 const recovered=await new CharacterLibrary(dir).load(data(''));assert.equal(recovered.recovered,true);assert.equal(recovered.data,data('Pierwsza'));
});
test('spis biblioteki ma kopię, a uszkodzona stara karta nie znika podczas migracji',async()=>{
 const dir=await directory(),store=new CharacterLibrary(dir);const first=await store.load(data('Maja'));
 await store.save(first.activeId,data('Maja zmieniona'));await writeFile(path.join(dir,'biblioteka.json'),'BŁĄD');
 const recovered=await new CharacterLibrary(dir).load(data(''));assert.equal(recovered.recovered,true);assert.equal(recovered.data,data('Maja zmieniona'));
 const bad=await directory();await writeFile(path.join(bad,'postac.json'),'WAŻNY USZKODZONY PLIK');
 await assert.rejects(new CharacterLibrary(bad).load(data('')));
 assert.equal(await readFile(path.join(bad,'postac.json'),'utf8'),'WAŻNY USZKODZONY PLIK');
 await assert.rejects(stat(path.join(bad,'biblioteka.json')));
});
test('postacie o tych samych nazwach mają inne identyfikatory, a obce ścieżki są odrzucane',async()=>{
 const dir=await directory(),store=new CharacterLibrary(dir);const first=await store.load(data(''));
 const next=await store.create(data(''));assert.notEqual(first.activeId,next.activeId);
 await assert.rejects(store.select('../../postac'));await assert.rejects(store.save('../../postac',data('')));
 assert.equal((await store.load(data(''))).data,data(''));
});
test('usunięcie karty usuwa jej pliki i wpisy także z kopii spisu',async()=>{
 const dir=await directory(),store=new CharacterLibrary(dir),first=await store.load(data('Maja'));
 await store.save(first.activeId,data('Maja po sesji'));
 const second=await store.create(data('Jan'));
 const result=await store.delete(first.activeId,data(''));
 assert.equal(result.activeId,second.activeId);assert.equal(result.characters.length,1);
 await assert.rejects(stat(file(dir,first.activeId)));await assert.rejects(stat(file(dir,first.activeId)+'.bak'));
 const backup=JSON.parse(await readFile(path.join(dir,'biblioteka.json.bak'),'utf8'));
 assert.equal(backup.characters.some((c:{id:string})=>c.id===first.activeId),false);
 await assert.rejects(store.save(first.activeId,data('Nie przywracaj')));
 const restored=await new CharacterLibrary(dir).load(data(''));assert.equal(restored.data,data('Jan'));
});
test('usunięcie ostatniej postaci otwiera nową pustą kartę bez odtwarzania usuniętej',async()=>{
 const dir=await directory(),store=new CharacterLibrary(dir),first=await store.load(data('Ostatnia'));
 const result=await store.delete(first.activeId,data(''));
 assert.notEqual(result.activeId,first.activeId);assert.equal(result.characters.length,1);assert.equal(result.data,data(''));
 assert.equal((await new CharacterLibrary(dir).load(data(''))).activeId,result.activeId);
 await assert.rejects(store.delete('../../postac',data('')));
});
