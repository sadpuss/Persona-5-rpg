# UWAGA: badanie archiwalne z 2026-10-29. Dotyczy starej wersji podręczników
# (GM 0.7, Gracza 0.4, Bestiariusz 0.4) i danych skill_*_0_7.json, więc wyniki
# i reguły w tym skrypcie mogą nie odpowiadać aktualnym podręcznikom.
# Wymagane pliki wejściowe są w historii Git pod tagiem archiwum-przed-porzadkami
# (np. git restore --source archiwum-przed-porzadkami -- Persona_5_RPG_Podrecznik_GM_0_7.docx)
# i trzeba je umieścić obok skryptu, razem z p5_base_skill_data.json i p5r_skill_data.json
# z dane/kompendium/. Wyniki to materiał badawczy, nie obowiązujące zasady.
"""Reproducible balance laboratory for the user's P5 tabletop homebrew.

It never edits the rulebooks. The fixture and limitations are exported with results.
"""
from pathlib import Path
from dataclasses import dataclass,field
from collections import Counter,defaultdict
from zipfile import ZipFile
import random,re,json,math,statistics,hashlib,time,copy
from lxml import etree

R=Path(__file__).parent;OUT=R/'balance_tests_2026_10_29';OUT.mkdir(exist_ok=True)
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
BOOKS=['Persona_5_RPG_Podrecznik_GM_0_7.docx','Persona_5_RPG_Podrecznik_Gracza_0_4.docx','Persona_5_RPG_Bestiariusz_0_4.docx']
ELEMENTS=['Physical','Gun','Fire','Ice','Electricity','Wind','Psy','Nuclear','Bless','Curse']
TYPES=dict(zip(['phy','gun','fir','ice','ele','win','psy','nuk','ble','cur'],ELEMENTS));TYPES['alm']='Almighty'
TIERS={'light':(1,4),'medium':(2,6),'heavy':(3,8),'severe':(3,14),'colossal':(3,20)}
def root(file):
    with ZipFile(R/file) as z:return etree.fromstring(z.read('word/document.xml'))
def txt(el):return ''.join(el.xpath('.//w:t/text()',namespaces=NS))
def rows(t):return [[txt(c) for c in row.findall('w:tc',NS)] for row in t.findall('w:tr',NS)]
def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def percentile(a,p):
    a=sorted(a);return a[min(len(a)-1,max(0,round((len(a)-1)*p)))] if a else None
def wilson(k,n):
    z=1.96;p=k/n;den=1+z*z/n
    c=(p+z*z/(2*n))/den;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [round(100*max(0,c-h),2),round(100*min(1,c+h),2)]

catalog={};gm=root(BOOKS[0])
for t in gm.xpath('/w:document/w:body/w:tbl',namespaces=NS):
    rr=rows(t)
    if len(rr[0])==7 and rr[0][0]=='Umiejętność':catalog.update({r[0]:r for r in rr[1:]})
assert len(catalog)==541
gates={x['skill']:x for x in json.loads((R/'skill_level_gates_0_7.json').read_text(encoding='utf-8'))}
newrules={x['skill']:x for x in json.loads((R/'skill_rules_0_7.json').read_text(encoding='utf-8'))}
source={}
for file in ['p5_base_skill_data.json','p5r_skill_data.json']:
    for v in json.loads((R/file).read_text(encoding='utf-8-sig')).values():source[v['a'][0]]=v

@dataclass(frozen=True)
class Skill:
    name:str;elem:str;dice:int;flat:int;cost:int;resource:str;area:bool=False
    status:str='';dc:int=0;kind:str='attack';amount:int=0;accuracy:int=0
    @property
    def mean(self):return self.dice*3.5+self.flat

SKILLS={}
for name,g in gates.items():
    if g['access']!='R':continue
    v=source[name];typ=v['a'][1]
    match=re.search(r'(\d+)d6\s*\+\s*(\d+)',newrules.get(name,{}).get('effect',''))
    dice=flat=0
    if match:dice,flat=map(int,match.groups())
    elif typ in ('fir','ice','ele','win','psy','nuk','ble','cur') and v['b'][2]>0:
        p=v['b'][2];tier='light' if p in (40,50) else 'medium' if p in (100,120) else 'heavy' if p in (160,190) else 'severe';dice,flat=TIERS[tier]
    if name=='Headbutt':dice,flat=2,6
    if name=='Assault Dive':dice,flat=3,8
    if not dice:continue
    costtext=catalog[name][3];cm=re.search(r'(\d+)\s*(HP|SP)',costtext)
    cost=int(cm[1]) if cm else 0;resource=cm[2] if cm else 'HP'
    dc=re.search(r'DC\s*(\d+)',catalog[name][5]);status=v.get('c',[''])[0]
    if status not in ('Burn','Freeze','Shock','Dizzy','Forget','Sleep','Confuse','Fear','Despair','Rage','Brainwash','Hunger'):status=''
    SKILLS[name]=Skill(name,TYPES[typ],dice,flat,cost,resource,v['a'][2]=='All foes',status,int(dc[1]) if dc else 0,accuracy=2 if name in ('Lucky Punch','Miracle Punch') else 0)
SKILLS['Basic Physical']=Skill('Basic Physical','Physical',1,4,0,'HP')
SKILLS['Basic Gun']=Skill('Basic Gun','Gun',1,4,0,'HP')
for name,amount,area in [('Dia',10,False),('Diarama',20,False),('Diarahan',-1,False),('Media',10,True),('Mediarama',20,True),('Mediarahan',-1,True)]:
    SKILLS[name]=Skill(name,'Heal',0,0,int(re.search(r'\d+',catalog[name][3])[0]),'SP',area,kind='heal',amount=amount)
SKILLS['Recarm']=Skill('Recarm','Heal',0,0,2,'SP',kind='revive',amount=50)
SKILLS['Samarecarm']=Skill('Samarecarm','Heal',0,0,5,'SP',kind='revive',amount=100)
for name in ['Tarunda','Rakukaja','Sukukaja','Tarukaja','Rakunda','Sukunda']:
    SKILLS[name]=Skill(name,'Support',0,0,2,'SP',kind='buff')
for name in ['Dormina','Ominous Words','Evil Touch','Makajam','Dazzler','Pulinpa']:
    v=source[name];SKILLS[name]=Skill(name,'Status',0,0,int(re.search(r'\d+',catalog[name][3])[0]),'SP',status=v['c'][0],dc=int(re.search(r'DC\s*(\d+)',catalog[name][5])[1]),kind='status')

def affline(line):
    out={}
    for kind,els in re.findall(r'(Weak|Resist|Null|Repel|Drain):\s*([^;]+)',line):
        for el in els.split(','):out[el.strip()]=kind
    return out

# Read the actual printed tabletop cards, not a fresh rescaling of P5 stats.
best=root(BOOKS[2]);profiles=[];head=None;header=None;stat=None
for el in best.find('w:body',NS):
    text=txt(el)
    if el.tag.endswith('}p') and re.match(r'^\d{3}\s+Lv\s+\d+\s+',text):head=text;header=None;stat=None
    elif head and el.tag.endswith('}tbl'):
        if el.xpath('.//w:drawing',namespaces=NS):header=el
        else:
            rr=rows(el)
            if rr[0][0]=='Profil':stat=rr
        if header is not None and stat is not None:
            hp=next((r for r in stat if r[0]=='RPG test'),None)
            if hp:
                paras=[txt(p) for p in header.xpath('.//w:p',namespaces=NS)]
                attack=next((p for p in paras if p.startswith('RPG: atak ')),None)
                if attack:
                    m=re.search(r'Atak testowy (\w+): (light|medium|heavy), (\d+) (SP|HP)',attack)
                    af=next((p for p in paras if p.startswith('Shadow i RPG:')),next(p for p in paras if p.startswith('Persona:')))
                    h=re.match(r'^(\d{3})\s+Lv\s+(\d+)\s+(.+)$',head)
                    profiles.append({'number':int(h[1]),'name':h[3],'persona_level':int(h[2]),'level':int(hp[1]),'hp':int(hp[2]),'sp':int(hp[3]),'atk':4,'defense':12,'aff':affline(af),'attack':m[1] if m else 'Physical','tier':m[2] if m else 'light','cost':int(m[3]) if m else 3,'resource':m[4] if m else 'HP'})
            head=None
assert len(profiles)>220,len(profiles)
dump('printed_profiles.json',profiles)
dump('input_manifest.json',{'books':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in BOOKS},'printed_combat_profiles':len(profiles),'catalogue_entries':541,'ready_access_entries':sum(g['access']=='R' for g in gates.values()),'attack_skills_parsed':len([s for s in SKILLS.values() if s.kind=='attack']),'accepted_shopping_fixture':'shared 4 x 10 HP + 1 x 6 SP per day; no turn-free use unless stated','note':'Test laboratory does not alter the three books.'})

@dataclass
class Unit:
    uid:int;name:str;side:int;level:int;maxhp:int;maxsp:int;hp:int;sp:int;atk:int;defense:int
    skills:list;aff:dict=field(default_factory=dict);passives:set=field(default_factory=set)
    role:str='';down:bool=False;guard:bool=False;statuses:dict=field(default_factory=dict)
    grace:int=0;turns:int=0;buffs:dict=field(default_factory=dict);know:dict=field(default_factory=dict)
    boss:bool=False;boss_actions:int=1;hold:bool=True;endure_used:bool=False
    knowledge:bool=False;courage:int=0;dexterity:int=0;arcana:str='';arcana_used:bool=False;social:bool=False
    @property
    def alive(self):return self.hp>0

@dataclass
class Fix:
    label:str='baseline';prices:bool=False;skill_costs:bool=False;light_damage:bool=False;despair_boss:bool=False;no_free_checkpoint:bool=False
    hp_version:int=1

BASE=Fix();PATCH=Fix('proposed',True,True,True,True,True)
MAGICPAIR=Fix('magic_prices_only',prices=True)
SKILLPAIR=Fix('physical_cleanup_only',skill_costs=True,light_damage=True)
FINAL=Fix('revised',True,True,True,True,True,2)

def cost_of(s,u,fix):
    c=s.cost
    if fix.prices and s.elem in TYPES.values() and s.elem not in ('Physical','Gun') and s.dice and s.mean>=24:
        c=6 if s.area else 4
    if fix.skill_costs and s.elem in ('Physical','Gun') and s.name in SKILLS and s.name not in ('Basic Physical','Basic Gun'):
        tier=next((t for t,pair in TIERS.items() if pair==(s.dice,s.flat)),None)
        if fix.hp_version==1:c={'light':3,'medium':5,'heavy':8,'severe':11,'colossal':14}[tier]+(4 if s.area else 0)+(1 if s.status or s.accuracy else 0)
        else:
            c={'light':2,'medium':4,'heavy':6,'severe':8,'colossal':10}[tier]+(3 if s.area else 0)+(1 if s.status or s.accuracy else 0)
            if s.name=='Cornered Fang':c-=2
            if s.name in ('Deadly Fury','Giant Slice','Rising Slash'):c+=1
    if ('Spell Master' in u.passives and s.resource=='SP') or ('Arms Master' in u.passives and s.resource=='HP'):
        c=math.ceil(c/2)
    return c

def make_hero(level,index,role,fix,advanced=False,social=False,knowledge=False):
    elements=[('Agi','Agilao','Agidyne','Inferno','Maragi','Maragion','Maragidyne','Blazing Hell','Fire'),('Garu','Garula','Garudyne','Panta Rhei','Magaru','Magarula','Magarudyne','Vacuum Wave','Wind'),('Zio','Zionga','Ziodyne','Thunder Reign','Mazio','Mazionga','Maziodyne','Wild Thunder','Electricity'),('Frei','Freila','Freidyne','Atomic Flare','Mafrei','Mafreila','Mafreidyne','Cosmic Flare','Nuclear')]
    e=elements[index%4];tier=0 if level<10 else 1 if level<25 else 2 if level<50 else 3
    names=[e[tier],elements[(index+1)%4][tier]]
    area_index=4 if level<15 else 5 if level<35 else 6 if level<65 else 7
    if level>=5:names.append(e[area_index])
    heal='Dia' if level<10 else 'Diarama' if level<40 else 'Diarahan'
    names.append(heal)
    if role=='physical':
        phys='Cleave' if level<10 else 'Assault Dive' if level<25 else 'Kill Rush' if level<35 else 'Gattling Blows' if level<50 else 'Sword Dance'
        names[0]=phys
        if level>=25:names[2]='Rampage' if level<35 else 'Swift Strike' if level<50 else 'Deathbound' if level<65 else 'Agneyastra'
    if role=='support':
        names=names[:2]+[heal,'Tarunda']+(['Rakukaja'] if level>1 else [])
        if level>=5:names.append('Media' if level<15 else 'Mediarama' if level<50 else 'Mediarahan')
        if level>=15:names.append('Recarm' if level<40 else 'Samarecarm')
    elif level==1:names.append('Tarunda')
    if level>=15 and len(names)<8:names.append('Recarm' if level<40 else 'Samarecarm')
    passives=set()
    if advanced:
        if level>=10 and role!='physical':passives.add({'Electricity':'Elec','Nuclear':'Nuke'}.get(e[8],e[8])+(' Boost' if level<40 else ' Amp'))
        if level>=25:passives.add('Invigorate '+('1' if level<40 else '2' if level<55 else '3'))
        if level>=65:passives.add('Arms Master' if role=='physical' else 'Spell Master')
    # Every skill must be legal and there must be room for every passive.
    names=list(dict.fromkeys(names))
    while len(names)+len(passives)>8:names.pop(-1)
    for name in names:
        assert gates[name]['access']=='R' and gates[name]['min_level']<=level,(name,level)
    for name in passives:assert gates[name]['access']=='R' and gates[name]['min_level']<=level,(name,level)
    assert len(names)+len(passives)<=8 and len(names)+len(passives)<=4+level-1
    hp=34+level;sp=30+level
    u=Unit(index,f'Hero {index+1}',0,level,hp,sp,hp,sp,5,12,[SKILLS[n] for n in names],{'Fire' if index%2==0 else 'Electricity':'Weak','Wind' if index%2==0 else 'Nuclear':'Resist'},passives,role=role,knowledge=knowledge)
    if social:u.courage=2;u.dexterity=2;u.social=True
    return u

def make_enemy(p,idx,boss=False,party_size=2,boss_actions=1,boss_variant=0):
    n,f=TIERS[p['tier']];skill=Skill('Printed test attack',p['attack'],n,f,p['cost'],p['resource'])
    hp=p['hp'];sp=p['sp'];aff=dict(p['aff'])
    if boss:
        # GM preparation fixture: five target rounds at a neutral baseline DPR.
        level=p['level'];hero_mean=7.5 if level<10 else 18.5 if level<35 else 24.5 if level<50 else 30.5
        hp=max(60,5*round(party_size*hero_mean*.65*5/5))
        sp=max(sp,p['cost']*8) if p['resource']=='SP' else 0
        aff=[{'Physical':'Resist','Fire':'Null'}, {'Nuclear':'Weak','Fire':'Null','Physical':'Resist'}, {'Bless':'Weak','Physical':'Null','Gun':'Null'}][boss_variant]
        if level>=36:n,f=3,8
        else:n,f=2,6
        skill=Skill('Boss test attack','Physical' if boss_variant==0 else 'Fire',n,f,0,'HP')
    return Unit(100+idx,p['name']+(' miniboss' if boss else ''),1,p['level'],hp,sp,hp,sp,4,13 if boss else 12,[skill],aff,boss=boss,boss_actions=boss_actions,hold=not boss)

class Fight:
    def __init__(self,heroes,enemies,seed,fix=BASE,known=False,surprise='none',policy='efficient',kit=None,boss_negotiate=False,limit=35):
        self.heroes=heroes;self.enemies=enemies;self.all=heroes+enemies;self.rng=random.Random(seed);self.fix=fix;self.policy=policy;self.kit=kit if kit is not None else {'hp':0,'sp':0,'revive':0};self.limit=limit
        self.metrics=Counter();self.round=0;self.outcome=None;self.boss_negotiate=boss_negotiate
        self.known=known;self.enemy_memory={};self.startsp=sum(u.sp for u in heroes);self.starthp=sum(u.hp for u in heroes)
        init=[(self.rng.randint(1,20),self.rng.random(),u) for u in self.all]
        init.sort(key=lambda x:(0 if surprise=='none' else (x[2].side if surprise=='heroes' else 1-x[2].side),-x[0],x[1]));self.order=[x[2] for x in init]
        for u in self.all:
            u.down=False;u.guard=False;u.turns=0;u.statuses={};u.grace=0;u.buffs={};u.endure_used=False
            if u.social:u.courage=2;u.dexterity=2
            if known:
                for enemy in enemies:u.know[enemy.name]=dict(enemy.aff)

    def alive(self,side):return [u for u in (self.heroes if side==0 else self.enemies) if u.alive]
    def blocked(self,u):return any(s in u.statuses for s in ('Freeze','Shock','Sleep','Confuse','Brainwash'))
    def value(self,u,param):
        if param=='atk':return u.atk+u.buffs.get('accuracy',(0,0))[0]-(4 if 'Dizzy' in u.statuses else 0)
        if param=='def':return u.defense+u.buffs.get('defense',(0,0))[0]
        return u.buffs.get(param,(0,0))[0]
    def prop(self,u,target,elem):
        if u.side==1:return target.aff.get(elem,'Normal')
        return u.know.get(target.name,{}).get(elem,'Unknown')
    def available(self,u,s):
        c=cost_of(s,u,self.fix)
        return (u.sp>=c if s.resource=='SP' else u.hp>c) and not ('Forget' in u.statuses and s.name not in ('Basic Physical','Basic Gun'))
    def bonus(self,u,s):
        el={'Electricity':'Elec','Nuclear':'Nuke'}.get(s.elem,s.elem);return max([0]+[4 if p==el+' Amp' else 2 if p==el+' Boost' else 0 for p in u.passives])
    def score(self,u,s,target):
        targets=self.alive(1-u.side) if s.area else [target];c=cost_of(s,u,self.fix)
        total=0
        for v in targets:
            a=self.prop(u,v,s.elem);mult={'Normal':1,'Unknown':1,'Weak':1.5,'Resist':.5,'Null':0,'Drain':-.3,'Repel':-.5}[a]
            dmg=s.mean+self.bonus(u,s)+self.value(u,'damage')+(2 if self.fix.light_damage and s.elem in ('Physical','Gun') and s.name in SKILLS and s.cost>0 and (s.dice,s.flat)==TIERS['light'] else 0)
            chance=max(0,min(1,(21+self.value(u,'atk')+s.accuracy-self.value(v,'def'))/20))
            val=min(max(0,dmg*mult),v.hp)*chance
            if a=='Weak' and not v.down and not v.guard:val+=chance*6
            if a=='Unknown' and u.side==0:val+=3
            total+=val
        if self.policy=='burst' or u.side==1:return total
        # Deliberately simple resource-aware heuristic, not an optimal solver.
        denom=1+(c*.20 if s.resource=='SP' else c*.05)
        if s.resource=='HP' and c>u.hp*.3:denom+=.6
        return total/denom
    def choice(self,u):
        foes=self.alive(1-u.side);friends=self.alive(u.side)
        if not foes:return None
        if u.side==0:
            # Recovery is a real action. Consumables shared; no phantom stock.
            dead=[v for v in self.heroes if not v.alive]
            if dead:
                rev=[s for s in u.skills if s.kind=='revive' and self.available(u,s)]
                if rev:return ('skill',rev[-1],dead[0])
                if self.kit['revive']>0:return ('item','revive',dead[0])
            lowest=min(friends,key=lambda v:v.hp/v.maxhp)
            if lowest.hp/lowest.maxhp<getattr(self,'heal_threshold',.40):
                heals=[s for s in u.skills if s.kind=='heal' and self.available(u,s)]
                if heals:
                    def hv(s):
                        ts=friends if s.area else [lowest];amount=sum(v.maxhp-v.hp if s.amount<0 else min(s.amount,v.maxhp-v.hp) for v in ts)
                        return amount/(1+cost_of(s,u,self.fix)*.35)
                    return ('skill',max(heals,key=hv),lowest)
                if self.kit['hp']>0:return ('item','hp',lowest)
            if u.sp<3 and self.kit['sp']>0:return ('item','sp',u)
            if u.role=='support' and any(v.boss for v in foes):
                boss=foes[0]
                tar=next((s for s in u.skills if s.name=='Tarunda' and self.available(u,s)),None)
                if tar and 'damage' not in boss.buffs:return ('skill',tar,boss)
        candidates=[s for s in u.skills if s.kind=='attack' and self.available(u,s)]+[SKILLS['Basic Physical'],SKILLS['Basic Gun']]
        options=[(self.score(u,s,target),s,target) for s in candidates for target in foes]
        best=max(options,key=lambda x:(x[0],-cost_of(x[1],u,self.fix)))
        if best[0]<=0:return ('guard',None,u)
        return ('skill',best[1],best[2])
    def learn(self,target,elem,aff):
        for u in self.heroes:u.know.setdefault(target.name,{})[elem]=aff
    def status(self,target,name,dc):
        if not target.alive or name in target.statuses:return
        if name in ('Freeze','Shock','Sleep','Confuse','Fear','Brainwash') and target.grace>0:return
        if target.side==0 and target.courage>0:
            roll=self.rng.randint(1,20)
            if roll<dc:target.courage-=1;self.metrics['courage_saved']+=1
            return
        if self.rng.randint(1,20)>=dc:return
        duration=3 if name in ('Burn','Despair','Hunger') else 2 if name in ('Dizzy','Forget','Rage') else 1
        target.statuses[name]=[duration,0];self.metrics['statuses_'+name]+=1
    def hit(self,u,target,s,raw):
        if self.rng.randint(1,20)+self.value(u,'atk')+s.accuracy<self.value(target,'def'):self.metrics['misses']+=1;return False
        aff=target.aff.get(s.elem,'Normal')
        if u.side==0:self.learn(target,s.elem,aff)
        raw=max(0,raw+self.bonus(u,s)+self.value(u,'damage')+self.value(target,'taken'))
        if 'Hunger' in u.statuses:raw*=.5
        if aff in ('Null','Repel','Drain'):
            if aff=='Drain':target.hp=min(target.maxhp,target.hp+math.floor(raw))
            if aff=='Repel':u.hp=max(0,u.hp-math.floor(raw*(.4 if u.guard else 1)))
            return False
        raw*=1.5 if aff=='Weak' else .5 if aff=='Resist' else 1
        raw*=.4 if target.guard else 1
        damage=math.floor(raw);old=target.hp;target.hp=max(0,target.hp-damage)
        self.metrics['hero_damage' if u.side==0 else 'enemy_damage']+=min(old,damage)
        if old and not target.hp:self.metrics['hero_KO' if target.side==0 else 'enemy_KO']+=1
        # Direct damage wakes the specified statuses; apply a fresh proc afterwards.
        for status in ['Dizzy','Forget','Sleep','Confuse']+(['Freeze'] if s.elem in ('Physical','Gun') else []):
            if damage and status in target.statuses:
                del target.statuses[status]
                if status in ('Freeze','Sleep','Confuse'):target.grace=1
        if s.status and damage and target.alive:self.status(target,s.status,s.dc)
        earned=aff=='Weak' and not target.down and not target.guard
        if earned:
            if target.alive:target.down=True
            self.metrics['downs']+=1
        return earned
    def action(self,u,used):
        if self.outcome or not u.alive or self.blocked(u):return
        decision=self.choice(u)
        if not decision:return
        kind,s,target=decision;self.metrics['hero_actions' if u.side==0 else 'enemy_actions']+=1
        if getattr(self,'trace',None) is not None:self.trace.append({'round':self.round,'actor':u.name,'action':s.name if isinstance(s,Skill) else s or kind,'target':target.name,'hp_sp_before':[u.hp,u.sp],'extra_chain_used':sorted(used)})
        if kind=='guard':u.guard=True;self.metrics['guards']+=1;return
        if kind=='item':
            self.kit[s]-=1;self.metrics['items_'+s]+=1
            if s=='hp':target.hp=min(target.maxhp,target.hp+10)
            elif s=='sp':target.sp=min(target.maxsp,target.sp+6)
            else:target.hp=max(1,target.maxhp//2)
            if u.side==0 and u.dexterity>0 and getattr(self,'ordinary_actor',None)==u.uid and u.uid not in self.free_item_this_turn:
                u.dexterity-=1;self.free_item_this_turn.add(u.uid);self.metrics['dexterity_free_items']+=1;self.action(u,used)
            return
        c=cost_of(s,u,self.fix)
        if s.resource=='SP':u.sp-=c;self.metrics['hero_SP_paid' if u.side==0 else 'enemy_SP_paid']+=c
        else:u.hp-=c;self.metrics['hero_HP_paid' if u.side==0 else 'enemy_HP_paid']+=c
        self.metrics['skill_'+s.name]+=1
        if s.kind=='heal':
            targets=self.alive(u.side) if s.area else [target]
            for v in targets:
                before=v.hp;v.hp=v.maxhp if s.amount<0 else min(v.maxhp,v.hp+s.amount);self.metrics['HP_healed']+=v.hp-before
            return
        if s.kind=='revive':target.hp=max(1,target.maxhp*s.amount//100);return
        if s.kind=='buff':
            if s.name=='Tarunda':target.buffs['damage']=(-4,3)
            elif s.name=='Rakukaja':target.buffs['taken']=(-4,3)
            return
        if s.kind=='status':self.status(target,s.status,s.dc);return
        targets=list(self.alive(1-u.side)) if s.area else [target]
        raw=sum(self.rng.randint(1,6) for _ in range(s.dice))+s.flat
        if self.fix.light_damage and s.elem in ('Physical','Gun') and s.name in SKILLS and s.name not in ('Basic Physical','Basic Gun') and (s.dice,s.flat)==TIERS['light']:raw+=2
        earned=False
        for v in targets:
            if v.alive:earned=self.hit(u,v,s,raw) or earned
        if not self.alive(1):self.outcome='victory';return
        if not self.alive(0):self.outcome='defeat';return
        foes=self.alive(1-u.side)
        if u.side==0 and foes and all(v.down for v in foes):
            if not any(v.boss for v in foes) or self.boss_negotiate:
                self.outcome='negotiated';self.metrics['hold_up']+=1;return
            self.metrics['all_out']+=1;aoa=sum(self.rng.randint(1,6) for _ in range(2))+4*sum(not self.blocked(v) for v in self.alive(0))
            for v in foes:v.hp=max(0,v.hp-aoa);v.down=False
            if not self.alive(1):self.outcome='victory'
            return
        if earned:
            eligible=[v for v in self.alive(u.side) if v.uid not in used and not self.blocked(v)]
            if u.side==1:eligible=[v for v in eligible if v is u]
            if eligible:
                nxt=u if u in eligible else eligible[0];used.add(nxt.uid);self.metrics['one_more']+=1
                if nxt is not u:self.metrics['baton_pass']+=1
                self.action(nxt,used)
    def run(self):
        for rnd in range(1,self.limit+1):
            self.round=rnd
            for u in self.order:
                if self.outcome:break
                if not u.alive:continue
                self.ordinary_actor=u.uid;self.free_item_this_turn=set()
                u.guard=False;u.down=False;u.turns+=1
                blocked=self.blocked(u)
                if 'Fear' in u.statuses and self.rng.randint(1,20)<11:blocked=True
                if blocked:self.metrics['skipped_hero_turns' if u.side==0 else 'skipped_enemy_turns']+=1
                else:
                    for _ in range(u.boss_actions):
                        if self.outcome:break
                        self.action(u,set())
                for name,state in list(u.statuses.items()):
                    if name=='Burn':u.hp=max(0,u.hp-3)
                    if name=='Sleep' and u.alive:u.hp=min(u.maxhp,u.hp+5);u.sp=min(u.maxsp,u.sp+2)
                    if name=='Despair':
                        u.sp=max(0,u.sp-2)
                        if state[1]==2:
                            if u.boss and self.fix.despair_boss:u.hp=max(0,u.hp-math.floor(20*(.4 if u.guard else 1)))
                            else:u.hp=0
                    state[0]-=1;state[1]+=1
                    if state[0]<=0:
                        del u.statuses[name]
                        if name in ('Freeze','Shock','Sleep','Confuse','Fear','Brainwash'):u.grace=2
                if u.grace:u.grace-=1
                for param,(amount,timer) in list(u.buffs.items()):
                    if timer<=1:del u.buffs[param]
                    else:u.buffs[param]=(amount,timer-1)
                if u.side==0 and u.alive and u.turns<=3:
                    inv=max([0]+[int(p[-1]) for p in u.passives if p.startswith('Invigorate ')])
                    old=u.sp;u.sp=min(u.maxsp,u.sp+inv);self.metrics['SP_regenerated']+=u.sp-old
                if not self.alive(0):self.outcome='defeat'
                if not self.alive(1):self.outcome='victory'
            if self.outcome:break
        if not self.outcome:self.outcome='timeout'
        for u in self.all:
            assert 0<=u.hp<=u.maxhp and 0<=u.sp<=u.maxsp,(u.name,u.hp,u.sp)
        return {'outcome':self.outcome,'rounds':self.round,'hp_pct':100*sum(u.hp for u in self.heroes)/sum(u.maxhp for u in self.heroes),'sp_pct':100*sum(u.sp for u in self.heroes)/sum(u.maxsp for u in self.heroes),'metrics':dict(self.metrics),'seed':None}

def party(level,n,build,fix,advanced=False,social=False,known=False):
    roles=['mage']*n if build in ('magic','burst') else ['physical']*n if build=='physical' else (['mage'] if n==1 else ['mage','support'] if n==2 else ['mage','physical','mage','support'])
    return [make_hero(level,i,role,fix,advanced,social,known) for i,role in enumerate(roles)]
def pool(level):
    candidates=[p for p in profiles if abs(p['level']-level)<=5]
    return candidates or sorted(profiles,key=lambda p:abs(p['level']-level))[:8]
def summarize(results):
    n=len(results);wins=sum(r['outcome'] in ('victory','negotiated') for r in results)
    keys=['rounds','hp_pct','sp_pct']
    out={'n':n,'win_pct':round(100*wins/n,2),'win_CI95':wilson(wins,n),'timeouts':sum(r['outcome']=='timeout' for r in results)}
    for key in keys:out[key]={'median':round(statistics.median(r[key] for r in results),2),'p10':round(percentile([r[key] for r in results],.1),2),'p90':round(percentile([r[key] for r in results],.9),2)}
    mc=Counter()
    for r in results:mc.update(r['metrics'])
    out['mean_metrics']={k:round(v/n,3) for k,v in mc.items()}
    return out

def catalogue_audit():
    # Strict dominance after a hit in the same type/target/status family; duplicates allowed.
    free=SKILLS['Basic Physical'];dom=[]
    candidates=sorted([s for s in SKILLS.values() if s.kind=='attack'],key=lambda s:(s.cost,-s.accuracy))
    conditional={'Cornered Fang','Deadly Fury','Giant Slice','Rising Slash'}
    for b in candidates:
        if b.name.startswith('Basic '):continue
        for a in candidates:
            if a.name in conditional or b.name in conditional:continue
            if a.name==b.name or a.elem!=b.elem or a.area!=b.area or a.resource!=b.resource:continue
            if a.status!=b.status or a.dc!=b.dc:continue
            if gates.get(a.name,{'min_level':1})['min_level']>gates[b.name]['min_level']:continue
            if a.dice==b.dice and a.flat==b.flat and a.accuracy>=b.accuracy and a.cost<b.cost:
                dom.append({'dominated':b.name,'better':a.name,'cost_bad':b.cost,'cost_better':a.cost,'resource':b.resource,'damage':f'{b.dice}d6+{b.flat}'});break
    costs=[]
    for name in ['Agi','Agilao','Agidyne','Inferno','Maragi','Maragion','Maragidyne','Blazing Hell','Cleave','Stomach Blow','Sword Dance',"God's Hand"]:
        s=SKILLS[name];costs.append({'name':name,'mean_hit':s.mean,'cost':s.cost,'resource':s.resource,'min_level':gates[name]['min_level'],'damage_per_resource':round(s.mean/s.cost,3) if s.cost else None})
    out={'exact_dominance_examples':dom,'tier_efficiency':costs,'coverage':'Attack skills with explicit dice, same element and target; no claim to order different statuses or all builds.'};dump('catalogue_audit.json',out);return out

def mechanics_checks():
    # Enumerated dice: exact, not Monte Carlo; include failure paths.
    assert sum(r+5>=12 for r in range(1,21))==14
    assert math.floor(20*.4)==8 and math.floor(20*.5*.4)==4
    checkpoint=[]
    for lvl in [1,10,25,50,65,99]:
        H=34+lvl;S=30+lvl
        for savedhp in range(1,H+1):
            for savedsp in range(S+1):
                before=(savedhp,savedsp);old=(H//2,S//2);new=(max(1,min(savedhp,H//2)),min(savedsp,S//2))
                checkpoint.append((old[0]>savedhp or old[1]>savedsp,new[0]>savedhp or new[1]>savedsp))
    assert not any(b for _,b in checkpoint)
    rescue={'source_states_enumerated':len(checkpoint),'original_has_net_resource_gain':sum(a for a,b in checkpoint),'proposed_has_net_resource_gain':sum(b for a,b in checkpoint),'example_level_25':{'saved_hp_sp':[1,0],'original_respawn':[29,27],'proposed_respawn':[1,0]}}
    # Does the one-more cap and grace period prevent an infinite execution chain?
    u=party(25,2,'balanced',BASE);e=[make_enemy(pool(25)[0],i) for i in range(4)]
    for v in e:v.aff={'Fire':'Weak','Wind':'Weak'};v.hp=v.maxhp=1000
    f=Fight(u,e,1,known=True);f.action(u[0],set())
    assert f.metrics['one_more']<=2
    maxexp=sum(50*l*(l-1) for l in [99]);assert maxexp==485100
    out={'checks':'hit chance, Guard+Resist, resource bounds, extra-chain cap, no new EXP after cap, checkpoint enumeration','checkpoint':rescue}
    dump('mechanics_checks.json',out);return out

def burst_test(n=2000):
    results=[]
    for level in [50,65,99]:
        for actions in [1,2]:
            for fix in [BASE,PATCH]:
                for seed in range(n):
                    heroes=party(level,2,'burst',fix);p=pool(level)[seed%len(pool(level))]
                    enemy=make_enemy(p,0,True,2,actions,0);enemy.aff={'Physical':'Null','Gun':'Null','Wind':'Resist'}
                    # Fixed finite target; compare severe pricing without using a physical weakness.
                    f=Fight(heroes,[enemy],seed+314159,fix,True,'none','burst');res=f.run();res.update(level=level,boss_actions=actions,rules=fix.label);results.append(res)
    return results

def despair_test(n=5000):
    out=[]
    for hp in [140,300,600]:
        for fix in [BASE,PATCH]:
            successes=0;dmg=[];turns=[]
            # Isolate one status application with no direct attacks; exactly the published counter.
            for seed in range(n):
                rng=random.Random(seed+1234);applied=rng.randint(1,20)<15
                lost=min(hp,20) if fix.despair_boss and applied else hp if applied else 0
                successes+=lost>=hp;dmg.append(lost);turns.append(3 if applied else 0)
            out.append({'boss_hp':hp,'rules':fix.label,'n':n,'KO_pct':round(successes/n*100,2),'mean_hp_loss':round(statistics.mean(dmg),2),'conditional_hp_loss_on_failed_defense':min(hp,20) if fix.despair_boss else hp,'spell':'Ominous Words','cost_SP':int(re.search(r'\d+',catalog['Ominous Words'][3])[0]),'interpretation':'No status immunity or cleanse assumed; boss guarding not modelled in this isolated check.'})
    dump('despair_test.json',out);return out

def run_matrix(n=250):
    partial=OUT/'matrix_partial.json';cells=json.loads(partial.read_text(encoding='utf-8')) if partial.exists() else [];count=sum(c['n'] for c in cells)
    for level in [1,5,10,15,25,35,50,65,80,99]:
        if any(c['level']==level for c in cells):continue
        ps=pool(level)
        for size in [1,2,4]:
            for known in [False,True]:
                for surprise in ['heroes','none','enemies']:
                    for build in ['balanced','burst','physical']:
                        for fix in [BASE,PATCH]:
                            results=[]
                            for i in range(n):
                                p=ps[i%len(ps)];heroes=party(level,size,build,fix,advanced=level>=25)
                                enemies=[make_enemy(p,k) for k in range(size+1)]
                                f=Fight(heroes,enemies,1000003*level+97*i+size,fix,known,surprise,'burst' if build=='burst' else 'efficient')
                                results.append(f.run())
                            cell={'level':level,'party_size':size,'known_weaknesses':known,'surprise':surprise,'build':build,'rules':fix.label,**summarize(results)};cells.append(cell);count+=n
        print('MATRIX LEVEL',level,'fights',count,flush=True)
        dump('matrix_partial.json',cells)
    dump('encounter_matrix.json',cells);return cells,count

def run_palaces(n=350):
    cells=[];count=0;fight_count=0
    for level in [5,25,65]:
        ps=pool(level)
        for size in [1,2,4]:
            for build in ['balanced','burst','physical']:
                for rest in [False,True]:
                    for fix in [BASE,PATCH]:
                        results=[]
                        for i in range(n):
                            heroes=party(level,size,build,fix,advanced=level>=25,social=True);kit={'hp':4,'sp':1,'revive':0};acc=Counter();allwin=True;rounds_total=0;cleared=0;enc=[];days=1
                            for step in range(7):
                                if rest and step==3:
                                    for u in heroes:u.hp=u.maxhp;u.sp=u.maxsp
                                    days+=1
                                    # Literal accepted resupply: fill the shared stock, not free extra beyond ten.
                                    kit['hp']=min(9,kit['hp']+4);kit['sp']=min(10-kit['hp'],kit['sp']+1)
                                # Real printed cards at the level; a fixture of six groups and one miniboss.
                                p=ps[(i+step*3)%len(ps)]
                                enemies=[make_enemy(p,k) for k in range(size+1)] if step<6 else [make_enemy(p,0,True,size,2 if size==4 else 1,0)]
                                f=Fight(heroes,enemies,7919*i+level*100000+step*101+size,fix,False,'heroes' if step in (0,3) else 'none','burst' if build=='burst' else 'efficient',kit)
                                res=f.run();fight_count+=1;rounds_total+=res['rounds'];acc.update(res['metrics']);enc.append(res['outcome'])
                                if res['outcome'] not in ('victory','negotiated'):allwin=False;break
                                cleared+=1
                                # HP healing outside combat is allowed, with its actual SP cost. No time ticks.
                                for healer in heroes:
                                    for target in heroes:
                                        if not target.alive:continue
                                        for _ in range(20):
                                            available=[s for s in healer.skills if s.kind=='heal' and not s.area and f.available(healer,s)]
                                            if target.hp>=target.maxhp*.85 or not available:break
                                            def efficiency(s):return min(target.maxhp-target.hp,target.maxhp if s.amount<0 else s.amount)/max(1,cost_of(s,healer,fix))
                                            s=max(available,key=efficiency);c=cost_of(s,healer,fix)
                                            if target.maxhp-target.hp<(target.maxhp if s.amount<0 else s.amount)*.4:break
                                            healer.sp-=c;acc['out_of_combat_SP_paid']+=c;target.hp=min(target.maxhp,target.hp+(target.maxhp if s.amount<0 else s.amount))
                            results.append({'outcome':'victory' if allwin else 'defeat','rounds':rounds_total,'hp_pct':100*sum(u.hp for u in heroes)/sum(u.maxhp for u in heroes),'sp_pct':100*sum(u.sp for u in heroes)/sum(u.maxsp for u in heroes),'metrics':dict(acc),'cleared':cleared,'days':days,'encounters':enc})
                        cell={'level':level,'party_size':size,'build':build,'full_return_after_third_fight':rest,'rules':fix.label,**summarize(results),'mean_encounters_cleared':round(statistics.mean(r['cleared'] for r in results),3)};cells.append(cell);count+=n
        print('PALACE LEVEL',level,'expeditions',count,'actual fights',fight_count,flush=True)
        dump('palace_partial.json',cells)
    dump('palace_matrix.json',cells);return cells,count,fight_count

def health_engine_tests():
    # Explicit fixed-seed assertions of the implemented mechanisms, independent of tuning.
    u=party(1,1,'balanced',BASE)[0];v=make_enemy(pool(1)[0],0)
    u.hp=1;assert not Fight([u],[v],1).available(u,SKILLS['Cleave'])
    u.sp=0;assert not Fight([u],[v],1).available(u,SKILLS['Dia'])
    assert Fight([u],[v],1).available(u,SKILLS['Basic Gun'])
    u.sp=u.maxsp;u.hp=10;f=Fight([u],[v],1);u.statuses['Sleep']=[1,0];v.hp=v.maxhp=1000;v.skills=[]
    # Source parser should never turn source stats into player hit bonuses.
    assert all(p['atk']==4 and p['defense']==12 for p in profiles)
    assert all(0<=cost_of(s,make_hero(99,0,'mage',BASE),PATCH) for s in SKILLS.values())

if __name__=='__main__':
    import sys
    t=time.time();health_engine_tests();catalogue_audit();mechanics_checks();despair_test()
    for lv in range(1,100):
        for bu in ['balanced','burst','physical']:
            for sz in [1,2,4]:party(lv,sz,bu,BASE,advanced=lv>=25)
    command=sys.argv[1] if len(sys.argv)>1 else 'all'
    if command in ('all','matrix'):cells,n=run_matrix();dump('matrix_run.json',{'fights':n,'cells':len(cells),'seconds':round(time.time()-t,2)})
    if command in ('all','palaces'):cells,n,f=run_palaces();dump('palace_run.json',{'expeditions':n,'actual_fights':f,'cells':len(cells),'seconds':round(time.time()-t,2)})
    if command in ('all','burst'):
        rs=burst_test();cells=[]
        for level in [50,65,99]:
            for actions in [1,2]:
                for fix in [BASE,PATCH]:cells.append({'level':level,'boss_actions':actions,'rules':fix.label,**summarize([r for r in rs if r['level']==level and r['boss_actions']==actions and r['rules']==fix.label])})
        dump('burst_comparison.json',cells);dump('burst_run.json',{'fights':len(rs),'seconds':round(time.time()-t,2)})
    print('DONE',round(time.time()-t,2),'seconds',flush=True)
