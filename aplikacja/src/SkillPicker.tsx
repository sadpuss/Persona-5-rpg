import {useState} from 'react';
import type {Dispatch,SetStateAction} from 'react';
import {RULES,TYPES,skillByName,stats,startProgress,learnSkill} from './model';
import type {Character} from './model';
import {TrashIcon} from './Icons';

export default function SkillPicker({character:c,onChange,onForget,onPreset}:{character:Character;onChange:Dispatch<SetStateAction<Character>>;onForget:(name:string)=>void;onPreset:(index:number)=>void}){
 const [query,setQuery]=useState(''),[type,setType]=useState(''),[showAll,setShowAll]=useState(false);
 const t=stats(c),progress=startProgress(c),choosingStart=!c.active&&progress.count<4;
 const found=RULES.skills.filter(s=>(!query||s.skill.toLowerCase().includes(query.toLowerCase())||(s.effect||'').toLowerCase().includes(query.toLowerCase()))&&(!type||s.type===type)&&(showAll||(s.access==='R'&&s.min_level!==null&&s.min_level<=t.level&&(!choosingStart||s.starter))));
 return <>
 <section className="skill-guide" aria-label="Zasady wyboru umiejętności">
  <div className="guide-heading">TWÓJ ZESTAW NA START</div>
  <div className="guide-stats"><div><strong>{progress.count}<span> / 4</span></strong><p>umiejętności startowe</p></div><div><strong>{progress.elements}<span> / 2</span></strong><p>różne żywioły ataków</p></div></div>
  <p>Wybierz <b>cztery umiejętności z poziomu 1</b>. Ataki mogą obejmować <b>najwyżej dwa różne żywioły</b>. Pozostałe miejsca możesz przeznaczyć na leczenie, statusy lub wsparcie.</p>
  <p className={progress.count===4&&progress.elements<=2?'guide-status complete':'guide-status'}>{choosingStart?`Wybierz jeszcze ${4-progress.count} umiejętności startowe — są darmowe.`:!c.active?'Zestaw startowy wybrany. Możesz teraz dodać umiejętności dostępne na swoim poziomie.':'Rozwijasz gotową postać. Nowe umiejętności kosztują po 1 punkcie nauki.'}</p>
  <p className="guide-note">Poziom {t.level} · {t.points} pkt nauki · {c.skills.length} / 8 miejsc. Trait Arkany jest osobno. Na wyższych poziomach kolejne umiejętności kosztują po 1 punkcie nauki; aplikacja nalicza to automatycznie.</p>
 </section>
 <details><summary>Pomóż mi wybrać — zestawy startowe</summary>Cztery gotowe wybory, które możesz później zmienić. Zastępują dotychczasowy zestaw startowy.<div className="preset-row">{['Ogień i wiatr','Leczenie i wsparcie','Lód i kontrola'].map((name,i)=><button onClick={()=>onPreset(i)} key={name}>{name}</button>)}</div></details>
 <div className="section-title">WYBRANE UMIEJĘTNOŚCI <small>{c.skills.length} / 8 miejsc</small></div>
 <div className="chosen-skills">{c.skills.length?c.skills.map(p=>{const s=skillByName.get(p.name);return <div className="chosen-skill" key={p.name}><div><strong>{p.name}</strong><small>{s?TYPES[s.type]:''}{s?.cost?` · ${s.cost}`:''}</small></div><button className="remove-skill" aria-label={`Usuń umiejętność ${p.name}`} onClick={()=>onForget(p.name)}><TrashIcon/> Usuń</button></div>;}):<p className="muted">Dodaj umiejętność z listy poniżej lub wybierz gotowy zestaw.</p>}</div>
 <div className="section-title">{choosingStart?'WYBIERZ UMIEJĘTNOŚCI STARTOWE':'KATALOG UMIEJĘTNOŚCI'} <small>Poziom {t.level}</small></div>
 <div className="skill-controls"><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Szukaj umiejętności…" aria-label="Szukaj umiejętności"/><select aria-label="Typ umiejętności" value={type} onChange={e=>setType(e.target.value)}><option value="">Wszystkie typy</option>{Object.entries(TYPES).map(([key,name])=><option key={key} value={key}>{name}</option>)}</select></div>
 <label className="check-label"><input type="checkbox" checked={showAll} onChange={e=>setShowAll(e.target.checked)}/> Pokaż także poza aktualnym poziomem i zwykłą nauką</label>
 <div className="skill-list">{found.map(s=>{const selected=c.skills.some(p=>p.name===s.skill),free=!c.active&&progress.count<4&&s.starter;return <button key={s.skill} data-skill={s.skill} className={`skill-card ${selected?'selected':''}`} aria-pressed={selected} onClick={()=>selected?onForget(s.skill):onChange(old=>learnSkill(old,s.skill))}><header><h3>{s.skill}</h3><small>{s.cost||'—'}</small></header><span className="tag">{TYPES[s.type]} · POZIOM {s.min_level??'—'}{s.access!=='R'?' · Poza zwykłą nauką':''}</span><p>{s.effect}</p><span className="skill-action">{selected?'Usuń z zestawu':free?'+ Dodaj bez punktu nauki':'+ Dodaj · 1 pkt nauki'}</span></button>;})}{!found.length&&<p className="muted">Brak wyników. Zmień filtr lub pokaż cały katalog.</p>}</div>
 </>;
}
