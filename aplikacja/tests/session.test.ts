import test from 'node:test';
import assert from 'node:assert/strict';
import {fresh,stats,threshold,setResource,adjustResource,learnInSession,addSkill,warnings,validate,addInventoryItem,changeItemQuantity,inventoryText} from '../src/model';

test('zasoby mają dolną i górną granicę, a zmiana nie wpływa na EXP',()=>{
 const c={...fresh(),active:true,exp:threshold(10),hp:12,sp:4};
 assert.equal(adjustResource(c,'hp',-20).hp,0);
 assert.equal(adjustResource(c,'sp',999).sp,stats(c).sp);
 assert.equal(setResource(c,'hp',50).hp,stats(c).hp);
 assert.equal(adjustResource({...c,hp:null},'hp',-5).hp,stats(c).hp-5);
 assert.equal(adjustResource(c,'hp',2).exp,c.exp);
 assert.throws(()=>adjustResource(c,'sp',NaN));
});
test('nauka przy ośmiu miejscach zastępuje jeden skill i wydaje dokładnie jeden punkt',()=>{
 let c={...fresh(),active:true,exp:threshold(65),hp:5,sp:2,name:'Maja',arcana:'Rydwan',persona:'Latarnik',weak:'Ice',resist:'Fire'};
 for(const name of ['Agi','Garu','Dia','Tarunda'])c=addSkill(c,name,'start');
 for(const name of ['Agilao','Garula','Diarama','Maragi'])c=addSkill(c,name,'point');
 assert.throws(()=>learnInSession(c,'Inferno'));
 const next=learnInSession(c,'Inferno','Agi');
 assert.equal(next.skills.length,8);assert.equal(next.spent,5);assert.equal(next.skills.some(s=>s.name==='Agi'),false);
 assert.equal(next.skills.some(s=>s.name==='Inferno'),true);assert.equal(next.hp,5);assert.equal(next.sp,2);
 assert.equal(warnings(next).some(w=>w.includes('cztery darmowe')),false);
 assert.throws(()=>learnInSession(next,'Inferno','Garu'));
 assert.throws(()=>learnInSession(c,'Inferno','Nieznana'));
});
test('rozwój sprawdza poziom, dostęp i budżet nauki',()=>{
 assert.throws(()=>learnInSession({...fresh(),active:true},'Agi'));
 const c={...fresh(),active:true,exp:threshold(10)};
 assert.throws(()=>learnInSession(c,'Inferno'));
 assert.throws(()=>learnInSession(c,'Life Surge'));
 const next=learnInSession(c,'Agilao');assert.equal(next.spent,1);assert.equal(stats(next).points,8);
});
test('ekwipunek zachowuje dawne notatki, ilości, opisy i zapis wymienny',()=>{
 const legacy={...fresh(),inventory:'Stary plecak i latarka'} as Record<string,unknown>;delete legacy.items;
 let c=validate(legacy);assert.deepEqual(c.items,[]);assert.equal(c.inventory,'Stary plecak i latarka');
 c=addInventoryItem(c,{id:'lek',name:' Lek ',quantity:3,description:'Odnawia 10 HP'});
 c=changeItemQuantity(c,'lek',-1);assert.equal(c.items[0].quantity,2);
 assert.match(inventoryText(c),/Stary plecak i latarka/);assert.match(inventoryText(c),/Lek ×2 — Odnawia 10 HP/);
 assert.deepEqual(validate(JSON.parse(JSON.stringify(c))),c);
 assert.equal(changeItemQuantity(c,'lek',-99).items[0].quantity,0);
 assert.throws(()=>addInventoryItem(c,{id:'lek',name:'Lek',quantity:1,description:''}));
 assert.throws(()=>validate({...c,items:[{id:'x',name:'Lek',quantity:-1,description:''}]}));
});
