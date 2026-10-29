import {RULES,skillByName,stats} from './model';
import type {Character} from './model';
export default function Preview({character:c}:{character:Character}){
 const t=stats(c),trait=RULES.arcana.find(a=>a.name===c.arcana);
 return <aside className="live-panel"><div className="preview-label">PODGLĄD NA ŻYWO ↗</div>
 <div className="card-art">{c.image?<img src={c.image} alt="Ilustracja Persony"/>:<span className="monogram">{c.alias?c.alias.slice(0,2).toUpperCase():'P5'}</span>}</div>
 <div className="preview-label">{c.alias||'NIEZNANA TOŻSAMOŚĆ'}</div><h2>{c.name||'Twój bohater'}</h2><div className="subtitle">{c.arcana||'Arkana czeka na wybór'} / {c.persona||'Osobista Persona'}</div>
 <div className="level-strip"><span>POZIOM</span><strong>{String(t.level).padStart(2,'0')}</strong><span>{c.exp.toLocaleString('pl-PL')} EXP</span></div>
 <div className="resources"><div className="resource hp"><small>HP</small><strong>{c.hp??t.hp}<small> / {t.hp}</small></strong></div><div className="resource sp"><small>SP</small><strong>{c.sp??t.sp}<small> / {t.sp}</small></strong></div></div>
 <div className="mini-heading">SKILLE PERSONY <span className="float-right">{c.skills.length} / 8</span></div>
 {c.skills.slice(0,8).map(s=><div className="mini-skill" key={s.name}><b>{s.name}</b><small>{skillByName.get(s.name)?.cost||'—'}</small></div>)}
 {Array.from({length:Math.max(0,4-c.skills.length)},(_,i)=><div className="empty-slot" key={i}>+ Miejsce na umiejętność</div>)}
 {trait&&<div className="trait"><b>TRAIT / {c.arcana}</b>{trait.effect}</div>}
 <p className="small-copy">Dwie karty. Jeden bohater.<br/>Zapisuj do pliku, by zabrać historię ze sobą.</p></aside>;
}
