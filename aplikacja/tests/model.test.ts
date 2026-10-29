import test from 'node:test';
import assert from 'node:assert/strict';
import {fresh,stats,threshold,levelOf,gainEXP,changeCharacter,validate,addSkill,removeSkill,warnings} from '../src/model';

test('progi poziomów 1–99 i nadwyżka EXP',()=>{
 for(let l=1;l<=99;l++){assert.equal(levelOf(threshold(l)),l);if(l<99)assert.equal(levelOf(threshold(l+1)-1),l);}
 assert.equal(levelOf(1e8),99);
});
test('wielokrotny awans nie leczy i daje punkty nauki',()=>{
 const c={...fresh(),exp:threshold(10),hp:12,sp:4,active:true};
 const next=gainEXP(c,threshold(15)-threshold(10)+23);
 assert.equal(stats(next).level,15);assert.equal(next.exp,threshold(15)+23);
 assert.equal(next.hp,12);assert.equal(next.sp,4);assert.equal(stats(next).points,14);
});
test('limit 99 i odrzucanie błędnego EXP',()=>{
 assert.equal(gainEXP(fresh(),1e7).exp,threshold(99));
 for(const n of [-1,NaN,Infinity,1.5])assert.throws(()=>gainEXP(fresh(),n));
});
test('zmiana traitu w trakcie gry nie leczy i przycina maksimum',()=>{
 const c={...fresh(),active:true,hp:35,sp:31};
 const chariot=changeCharacter(c,'arcana','Rydwan');assert.equal(stats(chariot).hp,37);assert.equal(chariot.hp,35);
 const removed=changeCharacter({...chariot,hp:37},'arcana','Mag');assert.equal(removed.hp,35);
 const counselor=changeCharacter(c,'arcana','Doradca');assert.equal(stats(counselor).sp,32);assert.equal(counselor.sp,31);
});
test('zapominanie w grze nie zwraca punktów; w przygotowaniu zwraca',()=>{
 const c=addSkill({...fresh(),exp:threshold(5)},'Maragi','point');
 assert.equal(c.spent,1);assert.equal(removeSkill(c,'Maragi').spent,0);
 assert.equal(removeSkill({...c,active:true},'Maragi').spent,1);
 assert.equal(addSkill(c,'Maragi','point').spent,1);
});
test('import zachowuje dane ze starego prototypu i nie wykonuje migracji',()=>{
 const c={...fresh(),name:'Łucja',hp:12,skills:[{name:'Agi',source:'start' as const}],notes:'Uzgodniono z GM'};
 assert.deepEqual(validate(JSON.parse(JSON.stringify(c))),c);
 assert.throws(()=>validate({...c,rulesVersion:'GM 0.7'}));
});
test('import odrzuca wadliwe skille i powtórzenia oraz ogranicza rangi',()=>{
 assert.throws(()=>validate({...fresh(),skills:[null]}));
 assert.throws(()=>validate({...fresh(),skills:[{name:'Agi',source:'start'},{name:'Agi',source:'point'}]}));
 assert.equal(validate({...fresh(),social:{Wiedza:99}}).social.Wiedza,4);
 assert.equal(validate({...fresh(),image:'data:image/svg+xml;base64,AAAA'}).image,'');
});
test('niepełna karta jest dozwolona, a nielegalne wybory mają ostrzeżenia',()=>{
 assert.ok(warnings(fresh()).length>=4);
 const c={...fresh(),name:'Maja',arcana:'Rydwan',persona:'Latarnik',weak:'Ice',resist:'Fire'};
 const complete=['Agi','Garu','Dia','Tarunda'].reduce((c,n)=>addSkill(c,n,'start'),c);
 assert.deepEqual(warnings(complete),[]);
 assert.ok(warnings({...complete,resist:'Ice'}).some(w=>w.includes('tego samego')));
 assert.ok(warnings(addSkill(complete,'Agneyastra','point')).some(w=>w.includes('poziom 65')));
 const physical={...complete,weak:'Physical',resist:'Gun'};
 assert.deepEqual(warnings(physical),[]);
 assert.deepEqual(validate(JSON.parse(JSON.stringify(physical))),physical);
 assert.ok(warnings({...physical,resist:'Physical'}).some(w=>w==='Słabość i odporność dotyczą tego samego typu.'));
});
