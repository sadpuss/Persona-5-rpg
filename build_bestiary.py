import json,math,csv,collections
from pathlib import Path
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

R=Path(__file__).parent
load=lambda n:json.loads((R/n).read_text(encoding='utf-8-sig'))
personas=load('p5r_personas.json');party=load('p5r_party.json');enemies=load('p5r_enemies.json')
skills={}
for file in ['p5_base_skill_data.json','p5r_skill_data.json']:
    for v in load(file).values():skills[v['a'][0]]=v
unlocks={};dlc=set()
for category in load('p5r_unlocks.json'):
    for names,condition in category['conditions'].items():
        for name in names.split(','):
            unlocks[name]=condition
            if category['category']=='Downloadable Content':dlc.add(name)
prereqs=load('p5r_prereqs.json');recipes=load('p5r_special_recipes.json')
by_persona=collections.defaultdict(list)
for name,e in enemies.items():by_persona[e['persona']].append((name,e))
entries=[(name,data,'party' if name in party else 'persona') for name,data in {**personas,**party}.items()]
entries.sort(key=lambda x:(x[1]['lvl'],x[0].casefold()))
assert len(entries)==242
elements=['Physical','Gun','Fire','Ice','Electricity','Wind','Psy','Nuclear','Bless','Curse']
el_names={'phy':'Physical','gun':'Gun','fir':'Fire','ice':'Ice','ele':'Electricity','win':'Wind','psy':'Psy','nuk':'Nuclear','ble':'Bless','cur':'Curse','alm':'Almighty'}
owners={'Zorro':'Morgana','Captain Kidd':'Ryuji','Carmen':'Ann','Goemon':'Yusuke','Johanna':'Makoto','Necronomicon':'Futaba','Milady':'Haru','Robin Hood':'Akechi','Loki':'Akechi','Cendrillon':'Sumire'}
areas={'Castle':'Pałac Kamoshidy','Museum':'Pałac Madarame','Bank':'Pałac Kaneshiro','Pyramid':'Pałac Futaby','Spaceport':'Pałac Okumury','Casino':'Pałac Sae','Cruiser':'Pałac Shido','Depths':'Głębie Mementos','Qliphoth':'Qliphoth','Laboratory':'Pałac Marukiego'}
fixed_hp={'Sandman':28,'Sui-Ki':36,'Nekomata':28,'Rakshasa':34,'Orobas':30}
special={
'Arsene':'Persona startowa protagonisty; w naszej kampanii może służyć jako wzór osobistej Persony.',
'Shiki-Ouji':'Null Physical/Gun wyłącza darmowe ataki tych typów. Nuclear otwiera One More. Próbę minibossa 140 HP traktuj jako osobny wariant.',
'Take-Minakata':'Electricity wraca przez Repel; Psy jest drogą do słabości. Nie kieruj Zio w ten cel po odkryciu odbicia.',
'Girimehkala':'Repel Physical: atak wręcz lub skill fizyczny może skrzywdzić napastnika. Sprawdź osobno Gun.',
'Rangda':'Repel Physical i Gun utrudnia kończenie walki darmowymi atakami. Sprawdzaj pozostałe typy na karcie.',
'Arahabaki':'Odbicie ataków fizycznych wymusza zmianę podejścia; profil Shadow może różnić się od Persony.',
'Fafnir':'Bardzo odporny przeciwnik. Nie przenoś całego zestawu mocnych skilli do RPG bez przetestowania pojedynczych efektów.',
'Abaddon':'Oryginalny Shadow ma wyjątkowo dużo HP. Nasz profil celowo nie dzieli jego 7000 HP przez stałą liczbę.',
'Sandman':'Dormina służy kontroli, nie zadawaniu obrażeń. Testowy darmowy atak jest dodatkiem RPG; Sleep wymaga własnych zasad.',
'Oni':'Brak słabości żywiołowej w zwykłym profilu. Specjalne wersje fabularne mogą mieć inne mnożniki.',
'Orpheus':'Circle of Sadness w P5R chroni przed nokautem do czterech razy na walkę. W podstawowym profilu testowym nie uruchamiaj go automatycznie.',
'Izanagi-no-Okami':'Myriad Truths i Country Maker są mocami unikatowymi. Wymagają osobnej adaptacji; nie stanowią standardu siły RPG.',
'Izanagi-no-Okami Picaro':'Wariant DLC z unikatowym zestawem mocy; Myriad Truths i Country Maker wymagają osobnej adaptacji.',
'Yoshitsune':'Hassou Tobi jest atakiem wielokrotnym. Nie wykonuj ośmiu pełnych rzutów heavy według naszej skali.',
'Alice':'Die For Me! i Just Die dotyczą instakill; brak gotowego odpowiednika w podstawowych testach RPG.',
'Satanael':'W P5R wymaga New Game+. Jego odporności i silne pasywy nie są domyślną nagrodą za sam poziom.',
'Necronomicon':'Persona nawigatora: wsparcie poza zwykłym udziałem w walce. Nie ma standardowej tury ofensywnej w P5R.',
}

def affinities(code):
    groups=collections.defaultdict(list)
    for typ,ch in zip(elements,code):
        c=ch.lower()
        if c in 'wxz':groups['Weak'].append(typ)
        elif c=='s':groups['Resist'].append(typ)
        elif c in ['n','_']:groups['Null'].append(typ)
        elif c=='r':groups['Repel'].append(typ)
        elif c=='d':groups['Drain'].append(typ)
    return '; '.join(k+': '+', '.join(groups[k]) for k in ['Weak','Resist','Null','Repel','Drain'] if groups[k]) or 'Wszystkie typy Normal'

def profile(name,data):
    matches=by_persona.get(name,[])
    base=matches[0][1] if matches else data
    lv=base['lvl'];st=base['stats'][2:] if matches else data['stats'];mean=sum(st)/5
    adjustment=5 if st[2]>=mean*1.25 else -5 if st[2]<=mean*.75 else 0
    hp=fixed_hp.get(name,max(20,5*round((.6*(34+lv)+adjustment)/5)))
    bonus=3+lv//20;defense=11+lv//20
    available=base['skills'] if matches else [n for n,l in data['skills'].items() if l<1]
    offensive=[skills[n] for n in available if n in skills and skills[n]['a'][1] in el_names and skills[n]['b'][2]>0]
    magic=next((s for s in offensive if s['a'][1] not in ['phy','gun']),None)
    strength='light' if lv<=10 else 'medium' if lv<=35 else 'heavy'
    if magic:
        kind=el_names[magic['a'][1]];cost={'light':1,'medium':2,'heavy':3}[strength];sp=4*cost
        attack=f'Atak testowy {kind}: {strength}, {cost} SP'
    else:
        kind='Physical';cost={'light':3,'medium':5,'heavy':8}[strength];sp=0
        attack=f'Atak testowy Physical: {strength}, {cost} HP'
    return dict(lv=lv,hp=hp,sp=sp,atk=bonus,defense=defense,attack=attack,kind=kind,strength=strength,code=base['resists'])

doc=Document();sec=doc.sections[0]
sec.page_width,sec.page_height=Cm(21),Cm(29.7)
sec.top_margin,sec.bottom_margin=Cm(1.45),Cm(1.4)
sec.left_margin=sec.right_margin=Cm(1.7)
for n in ['Normal','Title','Subtitle','Heading 1','Heading 2']:
    st=doc.styles[n];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
    for b in list(st.element.iter(qn('w:pBdr'))):b.getparent().remove(b)
doc.styles['Normal'].font.size=Pt(9)
doc.styles['Normal'].paragraph_format.space_after=Pt(3)
doc.styles['Normal'].paragraph_format.line_spacing=1.0
doc.styles['Title'].font.size=Pt(25)
doc.styles['Heading 1'].font.size=Pt(17)
doc.styles['Heading 2'].font.size=Pt(12)
doc.styles['Heading 2'].paragraph_format.space_before=Pt(5)
doc.styles['Heading 2'].paragraph_format.space_after=Pt(4)
doc.core_properties.title='Persona 5 RPG Bestiariusz Person i Shadows'
doc.core_properties.author='Projekt Persona 5 RPG'
def p(text,bold_prefix=None):
    par=doc.add_paragraph()
    if bold_prefix and text.startswith(bold_prefix):par.add_run(bold_prefix).bold=True;par.add_run(text[len(bold_prefix):])
    else:par.add_run(text)
    return par
def heading(text):doc.add_heading(text,2)
def page(text=None):
    doc.add_page_break()
    if text:doc.add_heading(text,1)
def table(headers,rows,widths,small=False):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
    for col,w in zip(t.columns,widths):col.width=Cm(w)
    for i,v in enumerate(headers):t.rows[0].cells[i].text=str(v)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for vals in rows:
        cells=t.add_row().cells
        for i,v in enumerate(vals):cells[i].text=str(v)
    for ri,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for ci,c in enumerate(row.cells):
            c.width=Cm(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=c._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
            pr.append(b);sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'333333' if ri==0 else ('F2F2F2' if ri%2 else 'FFFFFF'));pr.append(sh)
            m=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'55' if small else '85');e.set(qn('w:type'),'dxa');m.append(e)
            pr.append(m)
            for par in c.paragraphs:
                par.paragraph_format.space_after=Pt(1);par.paragraph_format.line_spacing=1
                if ci>0:par.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for run in par.runs:
                    run.font.size=Pt(8 if small else 9)
                    if ri==0:run.bold=True;run.font.color.rgb=RGBColor(255,255,255)
    return t

doc.add_heading('Persona 5 RPG',0)
p('Bestiariusz Person i Shadows','Bestiariusz')
p('Wersja 0.1 • 28 października 2026')
p('Osobny katalog dla GM: 232 Persony kompendium P5R oraz 10 początkowych form Person towarzyszy. Wszystkie 242 wpisy są uporządkowane według bazowego poziomu Persony, a przy remisie alfabetycznie. Karty zestawiają dane oryginalne i robocze profile do naszego RPG. Zawierają informacje o późnych przeciwnikach i DLC.')
heading('Dwie różne postacie tej samej istoty')
p('Persona P5R to wersja kompendium, z własnymi pięcioma cechami. Shadow P5R to przeciwnik o osobnym poziomie, HP, SP, cechach i skillach. Nie przepisujemy statystyk jednej wersji do drugiej. Tam, gdzie baza nie zawiera przeciwnika, Shadow name pozostaje nieprzypisane, a profil RPG jest hipotetycznym przeciwnikiem inspirowanym Personą.')
heading('Co jest gotowe do użycia')
p('Karta RPG daje HP, SP, premię ataku, Obronę, właściwości i jeden prosty atak specjalny. Każda walcząca istota ma też darmowy zwykły atak light Physical. To profil pojedynczego zwykłego przeciwnika, nie automatyczny miniboss. Wersje złożone, statusy, traity i unikatowe moce wymagają osobnej adaptacji; dane P5R pozostają odniesieniem.')
heading('Skróty')
table(['Skrót','Znaczenie'],[
('St Ma En Ag Lu','Strength, Magic, Endurance, Agility, Luck. Liczby źródłowe z P5R, bez automatycznego wpływu na rzuty RPG.'),
('Weak Resist Null','Słabość ×1,5, odporność ×0,5, brak obrażeń. Down i One More według zasad podstawowych.'),
('Repel Drain','Odbicie / absorpcja. Zachowane jako cechy; ich szczegółowe interakcje w RPG pozostają testowe.'),
('P S R','Persona P5R, Shadow P5R, roboczy przeciwnik RPG. Myślnik oznacza brak danej lub brak zastosowania.'),
('DLC Towarzysz','Wariant dodatkowy / Persona członka drużyny. Nie jest automatycznie zwykłym Shadow w Pałacu.')
],[3.8,13.8])
p('Nie używaj całej listy uczonych skilli równocześnie na początkowym poziomie. Karta podaje skille startowe i najbliższy rozwój oddzielnie. Limit ośmiu skilli naszej osobistej Persony pozostaje bez zmian. Traity są osobnym polem, nie dziewiątym skillem.')

page('Zasady roboczych profili RPG')
p('L to poziom Shadow, jeżeli istnieje w źródle; w pozostałych wpisach poziom Persony. Bazowe HP = 60% × (34 + L), zaokrąglone do najbliższych 5, minimum 20. Jeżeli źródłowe En jest co najmniej o 25% wyższe od średniej pięciu cech, dodaj przed zaokrągleniem 5 HP; jeśli o co najmniej 25% niższe, odejmij 5. Przy połówkach wybieramy parzystą wielokrotność 5. Wszystkie wyniki są już policzone na kartach.')
p('Wyjątki zachowujące poprzednie próby: Sandman 28 HP, Sui-Ki 36, Nekomata 28, Rakshasa 34, Orobas 30. Premia ataku = 3 + pełne dwudziestki poziomu; Obrona = 11 + pełne dwudziestki poziomu. Na poziomach 20–39 daje to +4 i Obronę 12. To nowe propozycje katalogowe, nie zmiany zasad bohaterów.')
p('Atak testowy ma siłę light na poziomach 1–10, medium na 11–35 i heavy od 36. Magia: odpowiednio 1, 2 lub 3 SP; pula SP pozwala na cztery użycia. Atak Physical: odpowiednio 3, 5 lub 8 HP, bez puli SP. Koszt HP musi pozostawić minimum 1 HP. Rzuty: light 1d6 + 4; medium 2d6 + 6; heavy 3d6 + 8. Niektóre profile mają 0 SP, ponieważ używają wyłącznie ataków za HP.')
p('Typ ataku wybieramy z ofensywnych skilli danej wersji źródłowej, preferując magię; jeśli nie ma odpowiedniego skilla, dodajemy testowy Physical. Atak testowy jest osobną konstrukcją homebrew, nie wiernym zamiennikiem wszystkich skilli P5R i nie ich kosztem z głównego katalogu. Zachowuje motyw istoty, pomijając statusy i multi hit.')
heading('Ważne ograniczenia')
p('Dane przeciwników dostępne są dla 128 z 232 Person, w 129 rekordach Shadow. Odporności profilu RPG pochodzą z wersji Shadow; przy jej braku z Persony. Różnice oraz znane nietypowe mnożniki źródłowe są zaznaczone na kartach. Dodatkowe listy odporności na statusy nie są w pełni adaptowane.')
p('Te profile nie są zbalansowane jednakowo dla każdej drużyny. Szczególnie poziomy powyżej 30, instakill, odbicie i skille unikatowe wymagają testów. Dla minibossa dobierz HP do docelowej długości walki; nie mnożymy automatycznie każdej karty. Wcześniejsze 140 HP Oni i Shiki-Ouji dotyczyło osobnych wersji minibossów.')
p('Treasure Demons nie dostają ataku ani zwykłego budżetu walki: oznaczamy je jako spotkania specjalne. Necronomicon pozostaje Personą nawigatora bez standardowej karty przeciwnika. Dla pozostałych Person towarzyszy parametry RPG przedstawiają hipotetyczny Shadow, nie gotową kartę bohatera z poziomu bazowego.')
heading('Źródła i identyfikacja')
p('aqiu384, Megaten Fusion Tool, pliki roy-demon-data, roy-party-data, roy-enemy-data, skill-data, roy-skill-data, roy-demon-unlocks, roy-fusion-prereqs, roy-special-recipes i comp-config. Baza publiczna na licencji Unlicense. Pobranie 28 października 2026. Dane Royal nadpisują dane bazowego P5.')
p('https://github.com/aqiu384/megaten-fusion-tool/tree/master/src/app/p5/data')
p('Krótkie opisy na kartach są własnymi profilami taktycznymi opracowanymi z cech i skilli; nie są cytatami mitologicznymi ani tekstem kompendium gry. Warunki odblokowania i nazwy itemizacji są referencją P5R. Nasze wytwarzanie skill cards wymaga osobnych zasad.')

page('Indeks według poziomu')
indexrows=[]
for start in range(1,100,10):
    selected=[(i+1,n,d['lvl']) for i,(n,d,k) in enumerate(entries) if start<=d['lvl']<=min(start+9,99)]
    indexrows.append([f'{start}–{min(start+9,99)}',', '.join(f'{n} ({lv}; #{i})' for i,n,lv in selected)])
table(['Poziomy','Nazwy i numery kart'],indexrows,[2.1,15.5])

audit=[]
for idx,(name,data,kind) in enumerate(entries):
    if idx%3==0:page()
    else:p('')
    lv=data['lvl'];matches=by_persona.get(name,[]);r=profile(name,data)
    treasure=name in prereqs
    heading(f'{idx+1:03d}  Lv {lv}  {name}')
    tags='Towarzysz '+owners.get(name,'') if kind=='party' else 'DLC' if name in dlc else 'Treasure Demon' if treasure else 'Kompendium'
    shadownames='; '.join(n if not treasure else name+' (Treasure Demon)' for n,e in matches) or '— brak zwykłego Shadow w tej bazie'
    p(f'Arcana: {data["race"].replace(" P","")}  •  {tags}  •  Shadow name: {shadownames}')
    roles=['siła fizyczna','magia','wytrzymałość','szybkość','szczęście'];strongest=roles[data['stats'].index(max(data['stats']))]
    p(f'Profil: wyróżnia się cechą {strongest}. '+('Spotkanie specjalne; materiał do rozwoju i fuzji.' if treasure else ('Nawigator i wsparcie drużyny.' if name=='Necronomicon' else 'Wariant testowy wykorzystuje '+r['kind']+'.')))
    rows=[['P5R Persona',lv,'—','—',*data['stats']]]
    for n,e in matches:rows.append(['P5R Shadow',e['lvl'],*e['stats']])
    if not treasure and name!='Necronomicon':rows.append(['RPG test',r['lv'],r['hp'],r['sp'],'—','—','—','—','—'])
    table(['Profil','Lv','HP','SP','St','Ma','En','Ag','Lu'],rows,[4.3,1,1.6,1.6,1.82,1.82,1.82,1.82,1.82],True)
    p('Persona: '+affinities(data['resists']))
    if matches:
        p('Shadow i RPG: '+affinities(matches[0][1]['resists']))
        p('Skille Shadow P5R: '+(', '.join(matches[0][1]['skills']) or 'Brak standardowych skilli w rekordzie')+'.')
    else:p('RPG korzysta z właściwości Persony; przeciwnik jest hipotetyczny.')
    if not treasure and name!='Necronomicon':
        p(f'RPG: atak +{r["atk"]}; Obrona {r["defense"]}; {r["attack"]}. Zwykły atak light Physical: 0 kosztu.')
    innate=[n for n,l in data['skills'].items() if l<1 and skills.get(n,{}).get('a',['',''])[1]!='tra']
    future=sorted([(l,n) for n,l in data['skills'].items() if 1<=l<=99 and skills.get(n,{}).get('a',['',''])[1]!='tra'])
    p('Start Persony: '+(', '.join(innate) or 'według sceny przebudzenia')+'. '+('Najbliższy rozwój: '+', '.join(f'{n} Lv {int(l)}' for l,n in future[:4])+'.' if future else ''))
    p('Trait P5R: '+data.get('trait','—')+'. '+('Przedmiot / alarm: '+data.get('item','—')+' / '+data.get('itemr','—')+'.' if kind!='party' else 'Ewolucje towarzysza i skille z rang więzi nie są automatycznymi awansami tej karty.'))
    notes=[]
    if name in special:notes.append(special[name])
    if treasure:notes.append('Treasure Demon: bez standardowej walki; brak nadanej puli HP/SP RPG.')
    if name in recipes:notes.append('Fuzja specjalna: '+' + '.join(recipes[name])+'.')
    if name in unlocks and name not in dlc:notes.append('Warunek P5R: '+unlocks[name]+'.')
    if matches:
        e=matches[0][1]
        if 'resmods' in e:notes.append('Nietypowe mnożniki P5R: '+','.join(map(str,e['resmods']))+' (kolejność typów z legendy i Almighty; 0 = brak nadpisania). Nie stosujemy ich automatycznie w RPG.')
        if e['trait'] in ['Timid','Upbeat','Irritable','Gloomy']:notes.append('Negocjacje P5R: '+e['trait']+'.')
        loc=e.get('areas','')
        if loc:notes.append('Miejsce: '+areas.get(loc,str(loc))+'.')
        dangerous=[n for n in e['skills'] if n.startswith(('Counter','Drain','Repel','Null')) or n in ['Charge','Concentrate','Mudo','Mudoon','Hama','Hamaon']]
        if dangerous:notes.append('Uwaga na: '+', '.join(dangerous)+'.')
    if not notes:notes.append('Brak dodatkowego wyjątku w tym profilu; skille unikatowe i pasywy adaptuj osobno.')
    p('Interakcje: '+' '.join(notes))
    audit.append({'card':idx+1,'name':name,'persona_level':lv,'kind':kind,'shadow_names':[n for n,e in matches],'rpg':None if treasure or name=='Necronomicon' else r})

foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT
run=foot.add_run('Bestiariusz 0.1  •  ');run.font.size=Pt(8)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)
out=R/'Persona_5_RPG_Bestiariusz_0_1.docx';doc.save(out)
(R/'bestiary_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
check=Document(out)
assert len([x for x in check.paragraphs if x.style.name=='Heading 2' and x.text[:3].isdigit()])==242
assert [x['persona_level'] for x in audit]==sorted(x['persona_level'] for x in audit)
assert len({x['name'] for x in audit})==242
assert sum(len(x['shadow_names']) for x in audit)==129
print('OK',out,'| 242 cards | 232 compendium + 10 party | 129 shadow records')
