import { RULES, SOCIAL, skillByName, stats, TYPES } from './model';
import type { Character } from './model';
export default function Sheets({character:c,style,index}:{character:Character;style:string;index:boolean}){
 const t=stats(c),trait=RULES.arcana.find(a=>a.name===c.arcana),name=c.name||'________________________';
 return <>
 <section className={`sheet-preview ${style}`}>
  <div className="sheet-meta">PERSONA RPG / BOHATER · {c.rulesVersion}</div><h2>{name}</h2>
  <div className="sheet-grid"><div><h4>TOŻSAMOŚĆ</h4><p>Pseudonim: {c.alias||'________________'}<br/>Wiek: {c.age||'________'}<br/>Zajęcie: {c.occupation||'________________'}</p></div>
  <div><h4>WSPÓLNE ZASOBY</h4><p>Poziom {t.level} · EXP {c.exp}<br/>HP {c.hp??t.hp} / {t.hp} · SP {c.sp??t.sp} / {t.sp}<br/>Trafienie +5 · Obrona 12 (baza)<br/>Punkty nauki: {t.points}</p></div></div>
  <h4>CECHY SPOŁECZNE</h4><p>{SOCIAL.map(s=>`${s}: ${c.social[s]}`).join(' · ')}</p>
  <h4>HISTORIA / MOTYWACJA</h4><div className="write-space"><p>{c.story}</p></div>
  <h4>EKWIPUNEK</h4><div className="write-space"><p>{c.inventory}</p></div>
  <h4>NOTATKI</h4><div className="blank-lines"/>
  <h4>PODSTAWOWE AKCJE</h4><p>Atak Physical / strzał Gun: d20 + 5 ≥ Obrona, 1d6 + 4 obrażeń, bez kosztu.<br/>Guard: otrzymujesz 40% obrażeń i ochronę przed Down do początku następnej zwykłej tury.<br/>Skille i pasywy mogą modyfikować wartości bazowe zgodnie ze swoim opisem.</p>
 </section>
 <section className={`sheet-preview ${style}`}>
  <div className="sheet-meta">PERSONA RPG / OSOBISTA PERSONA · {c.rulesVersion}</div><h2>{c.persona||'________________________'}</h2>
  <div className="sheet-grid"><div><h4>UŻYTKOWNIK</h4><p>{name}<br/>Poziom {t.level} · wspólne HP / SP<br/>Arkana: {c.arcana||'________________'}</p>
  <h4>WŁAŚCIWOŚCI BAZOWE</h4><p>Słabość: {c.weak||'________'} · Odporność: {c.resist||'________'}<br/>Pozostałe typy: neutralne.<br/>Pasywy mogą zakrywać bazowe właściwości.</p></div>
  <div>{c.image?<img src={c.image} alt="Ilustracja Persony"/>:<div className="blank-lines illustration-space"/>}</div></div>
  <h4>OSOBISTY TRAIT ARKANY / POZA SLOTAMI</h4><p>{trait?.effect||'________________________________________________________________'}</p>
  <p className="sheet-meta">Aktywne efekty raz na wyprawę, o ile opis nie mówi inaczej. Stałe premie bierne; wytwarzanie wymaga bloku aktywności.</p>
  <h4>SKILLE / MAKSYMALNIE OSIEM</h4>
  {Array.from({length:Math.max(8,c.skills.length)},(_,i)=>{const s=c.skills[i];return <div className="sheet-skill" key={i}><span>{i+1}. {s?.name||'________________________________'}</span><span>{s?(skillByName.get(s.name)?.cost||'Sprawdź katalog'):''}</span></div>;})}
  <h4>WYGLĄD I SYMBOLIKA</h4><div className="write-space"><p>{c.concept}</p></div>
 </section>
 {index&&c.skills.length>0&&<section className={`sheet-preview index-page ${style}`}><div className="sheet-meta">PERSONA RPG / INDEKS UMIEJĘTNOŚCI</div><h2>Twój zestaw skilli</h2>
 {c.skills.map(p=>{const s=skillByName.get(p.name);return <div className="index-entry" key={p.name}><strong>{p.name}</strong> · {s?.cost||'Koszt: katalog GM'}<p>{s?.effect||'Pełny opis w katalogu GM 0.8; opis nie został jeszcze przeniesiony do aplikacji.'}</p><small>Min. poziom: {s?.min_level??'—'} · {TYPES[s?.type??'']||s?.type||'—'}</small></div>;})}
 </section>}
 </>;
}
