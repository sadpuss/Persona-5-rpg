import catalog from './rules.json';
export const VERSION = 'GM 0.8 / Gracz 0.5';
export const STEPS = ['Bohater','Poziom i rozwój','Arkana','Twoja Persona','Umiejętności','Gotowe karty'];
export const TYPES: Record<string,string> = {fir:'Fire',ice:'Ice',ele:'Electricity',win:'Wind',psy:'Psy',nuk:'Nuclear',ble:'Bless',cur:'Curse',phy:'Physical',gun:'Gun',alm:'Almighty',rec:'Leczenie',ail:'Status',sup:'Wsparcie',pas:'Pasyw',tra:'Trait'};
export const ELEMENTS = Object.values(TYPES).slice(0,8);
export const AFFINITIES = [...ELEMENTS, 'Physical', 'Gun'];
export const SOCIAL = ['Wiedza','Odwaga','Empatia','Urok','Zręczność'] as const;
export type Social = typeof SOCIAL[number];
export type Source = 'start' | 'point' | 'card';
export interface PickedSkill {name:string;source:Source}
export interface Skill {skill:string;type:string;min_level:number|null;access:string;reason:string;effect?:string;cost?:string;starter:boolean}
export const RULES = catalog as {version:string;skills:Skill[];arcana:{name:string;effect:string}[]};
export const skillByName = new Map(RULES.skills.map(s=>[s.skill,s]));
export interface Character {
 format:1;rulesVersion:string;name:string;alias:string;age:string;occupation:string;story:string;
 arcana:string;persona:string;concept:string;image:string;weak:string;resist:string;
 exp:number;startLevel:number;skills:PickedSkill[];spent:number;hp:number|null;sp:number|null;
 bonusHP:number;bonusSP:number;inventory:string;notes:string;social:Record<Social,number>;active:boolean;
}
export const fresh=():Character=>({format:1,rulesVersion:VERSION,name:'',alias:'',age:'',occupation:'',story:'',arcana:'',persona:'',concept:'',image:'',weak:'',resist:'',exp:0,startLevel:1,skills:[],spent:0,hp:null,sp:null,bonusHP:0,bonusSP:0,inventory:'',notes:'',social:{Wiedza:1,Odwaga:1,Empatia:1,Urok:1,'Zręczność':1},active:false});
export const threshold=(level:number)=>50*(level-1)*level;
export const levelOf=(exp:number)=>Math.min(99,Math.floor((1+Math.sqrt(1+Math.max(0,exp)*.08))/2));
export function stats(c:Character){const level=levelOf(c.exp);return{level,hp:34+level+(c.arcana==='Rydwan'?2:0)+c.bonusHP,sp:30+level+(c.arcana==='Doradca'?1:0)+c.bonusSP,points:level-1-c.spent};}
export function validate(value:unknown):Character{
 if(!value||typeof value!=='object')throw new Error('Nieprawidłowy plik postaci.');
 const x=value as Record<string,unknown>;
 if(x.format!==1||typeof x.rulesVersion!=='string'||!Array.isArray(x.skills))throw new Error('Nieprawidłowy format karty.');
 if(x.rulesVersion!==VERSION)throw new Error(`Zapis używa zasad ${x.rulesVersion}. Aplikacja obsługuje ${VERSION}. Zachowaj oryginalny plik do czasu dostępności migracji.`);
 const result=fresh();
 for(const k of ['name','alias','age','occupation','story','arcana','persona','concept','weak','resist','inventory','notes'] as const)if(typeof x[k]==='string')result[k]=x[k].slice(0,30000);
 const num=(v:unknown,fallback=0,max=1e7)=>typeof v==='number'&&Number.isFinite(v)?Math.max(0,Math.min(max,Math.floor(v))):fallback;
 for(const k of ['exp','spent','bonusHP','bonusSP'] as const)result[k]=num(x[k],0,k==='exp'?threshold(99):1e7);
 for(const k of ['hp','sp'] as const)result[k]=x[k]===null||x[k]===undefined?null:num(x[k]);
 result.startLevel=Math.max(1,num(x.startLevel,1,99));result.active=x.active===true;
 const names=new Set<string>();
 result.skills=x.skills.slice(0,100).map((v:unknown)=>{
  if(!v||typeof v!=='object')throw new Error('Nieprawidłowy zapis umiejętności.');
  const s=v as Record<string,unknown>;
  if(typeof s.name!=='string'||!['start','point','card'].includes(String(s.source))||names.has(s.name))throw new Error('Nieprawidłowa lub powtórzona umiejętność w zapisie.');
  names.add(s.name);return{name:s.name.slice(0,150),source:s.source as Source};
 });
 if(typeof x.image==='string'&&/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(x.image)&&x.image.length<3000000)result.image=x.image;
 const social=x.social&&typeof x.social==='object'?x.social as Record<string,unknown>:{};
 for(const s of SOCIAL)result.social[s]=Math.max(1,num(social[s],1,4));
 const t=stats(result);if(result.hp!==null)result.hp=Math.min(result.hp,t.hp);if(result.sp!==null)result.sp=Math.min(result.sp,t.sp);
 return result;
}
export function changeCharacter<K extends keyof Character>(c:Character,key:K,value:Character[K]):Character{
 const old=stats(c),next={...c,[key]:value};
 if(key==='arcana'||key==='bonusHP'||key==='bonusSP'){
  const t=stats(next);next.hp=c.hp===null&&!c.active?null:Math.min(c.hp??old.hp,t.hp);next.sp=c.sp===null&&!c.active?null:Math.min(c.sp??old.sp,t.sp);
 }return next;
}
export function gainEXP(c:Character,amount:number):Character{
 if(!Number.isSafeInteger(amount)||amount<0)throw new Error('Podaj nieujemną liczbę EXP.');
 const t=stats(c);return{...c,exp:Math.min(threshold(99),c.exp+amount),hp:c.hp??t.hp,sp:c.sp??t.sp};
}
export function addSkill(c:Character,name:string,source:Source):Character{
 if(c.skills.some(s=>s.name===name))return c;
 return{...c,skills:[...c.skills,{name,source}],spent:c.spent+(source==='point'?1:0)};
}
export function startProgress(c:Character){
 const start=c.skills.filter(s=>s.source==='start');
 const elements=new Set(start.map(s=>skillByName.get(s.name)?.type).filter(t=>t&&ELEMENTS.includes(TYPES[t])));
 return{count:start.length,elements:elements.size};
}
export function learnSkill(c:Character,name:string):Character{
 const free=!c.active&&startProgress(c).count<4&&skillByName.get(name)?.starter;
 return addSkill(c,name,free?'start':'point');
}
export function removeSkill(c:Character,name:string):Character{
 const p=c.skills.find(s=>s.name===name);return{...c,skills:c.skills.filter(s=>s.name!==name),spent:Math.max(0,c.spent-(!c.active&&p?.source==='point'?1:0))};
}
export function warnings(c:Character):string[]{
 const a:string[]=[],t=stats(c);
 if(!c.name)a.push('Bohater nie ma jeszcze imienia.');
 if(!c.arcana)a.push('Wybierz Arkanę, aby przypisać osobisty trait.');
 else if(!RULES.arcana.some(a=>a.name===c.arcana))a.push('Arkana jest spoza dostępnej puli startowej.');
 if(!c.persona)a.push('Persona nie ma jeszcze nazwy.');
 if(!c.weak||!c.resist)a.push('Wybierz jedną słabość i jedną odporność.');
 if(c.weak&&c.weak===c.resist)a.push('Słabość i odporność dotyczą tego samego typu.');
 if([c.weak,c.resist].some(v=>v&&!AFFINITIES.includes(v)))a.push('Właściwość jest poza dostępną pulą.');
 const start=c.skills.filter(s=>s.source==='start');
 if(start.length!==4)a.push(`Start obejmuje cztery darmowe skille (teraz: ${start.length}).`);
 if(start.some(s=>!skillByName.get(s.name)?.starter))a.push('Darmowy skill jest spoza puli startowej.');
 const elements=new Set(start.map(s=>skillByName.get(s.name)?.type).filter(s=>s&&ELEMENTS.includes(TYPES[s])));
 if(elements.size>2)a.push('Na start wybierz ataki najwyżej dwóch różnych żywiołów.');
 if(c.skills.length>8)a.push('Przekroczono limit ośmiu skilli. Usuń skill zastępowany przy nauce.');
 if(t.points<0)a.push('Wydano więcej punktów nauki, niż wynika z poziomu.');
 for(const p of c.skills){const s=skillByName.get(p.name);if(!s)a.push(`${p.name}: brak w bieżącym katalogu.`);else{
  if(s.access!=='R')a.push(`${s.skill}: dostęp ${s.access}; poza zwykłą nauką.`);
  if(s.min_level!==null&&s.min_level>t.level)a.push(`${s.skill}: wymagany poziom ${s.min_level}.`);
  if(!s.effect)a.push(`${s.skill}: pełny opis sprawdź w katalogu GM 0.8.`);
 }}
 if(c.skills.some(p=>skillByName.get(p.name)?.type==='pas'))a.push('Premie pasywów rozliczaj według opisów. Dodatkowe maksymalne HP/SP wpisz w zasobach.');
 return a;
}
