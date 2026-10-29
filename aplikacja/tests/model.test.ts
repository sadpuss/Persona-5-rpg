import test from 'node:test';
import assert from 'node:assert/strict';
import {fresh,stats,threshold,levelOf,gainEXP,changeCharacter,validate,addSkill,removeSkill,warnings,learnSkill,startProgress,RULES,skillByName} from '../src/model';

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
test('kreator sam przydziela darmowe wybory i punkty nauki, a usunięcie pozwala poprawić zestaw',()=>{
 let c={...fresh(),exp:threshold(10)};
 for(const name of ['Agi','Garu','Dia','Tarunda'])c=learnSkill(c,name);
 assert.deepEqual(startProgress(c),{count:4,elements:2});assert.equal(c.spent,0);
 c=learnSkill(c,'Agilao');assert.equal(c.spent,1);
 c=removeSkill(c,'Garu');c=learnSkill(c,'Bufu');
 assert.equal(startProgress(c).count,4);assert.equal(c.spent,1);
 c=learnSkill({...c,active:true},'Patra');assert.equal(c.spent,2);
});
test('wszystkie dostępne umiejętności mają opisy bez skrótów żywiołów i roboczych dopisków',()=>{
 const ready=RULES.skills.filter(s=>s.access==='R');assert.equal(ready.length,346);
 for(const s of RULES.skills){
  assert.ok(s.effect?.trim(),s.skill);
  assert.equal(/\b(fir|ele|win|nuk|ble|cur|phy|alm)\b/i.test(s.effect!),false,s.skill);
  assert.equal(/do ustalenia|do uzgodnienia|opis nie został|robocz/i.test(s.effect!),false,s.skill);
 }
 assert.match(skillByName.get('Garu')!.effect!,/Wind/);
 assert.match(skillByName.get('Agilao')!.effect!,/2d6 \+ 6.*Fire/);
 assert.match(skillByName.get('Dormina')!.effect!,/DC 15/);
 assert.match(skillByName.get('Resist Sleep')!.effect!,/\+4/);
});
