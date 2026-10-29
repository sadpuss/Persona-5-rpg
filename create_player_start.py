from pathlib import Path
from copy import deepcopy
from collections import Counter
import json, math, hashlib, csv
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_ALIGN_PARAGRAPH

R=Path(__file__).parent
GM_SRC=R/'Persona_5_RPG_Podrecznik_GM_0_3.docx'
GM_OUT=R/'Persona_5_RPG_Podrecznik_GM_0_4.docx'
PLAYER=R/'Persona_5_RPG_Podrecznik_Gracza_0_1.docx'
assert not GM_OUT.exists() and not PLAYER.exists()
source_hash=hashlib.sha256(GM_SRC.read_bytes()).hexdigest()
gm=Document(GM_SRC)
skills={}
for f in ['p5_base_skill_data.json','p5r_skill_data.json']:
    for v in json.loads((R/f).read_text(encoding='utf-8-sig')).values():skills[v['a'][0]]=v
assert len(skills)==541
elements={'fir','ice','ele','win','psy','nuk','ble','cur'}
basic_elements={'Agi','Bufu','Zio','Garu','Psi','Frei','Kouha','Eiha'}
support={'Tarukaja','Rakukaja','Sukukaja','Tarunda','Rakunda','Sukunda'}
heal_levels={'Dia':1,'Diarama':10,'Diarahan':40,'Media':5,'Mediarama':15,'Mediarahan':50,'Recarm':15,'Samarecarm':40,'Salvation':65,'Patra':1,'Baisudi':1,'Energy Drop':5,'Me Patra':5,'Mabaisudi':5,'Energy Shower':10,'Amrita Drop':10,'Amrita Shower':20}
heal_ready={'Dia','Diarama','Patra','Baisudi','Energy Drop','Me Patra','Mabaisudi','Energy Shower','Amrita Drop','Amrita Shower'}
ailments={'Burn','Freeze','Shock','Dizzy','Forget','Sleep','Confuse','Fear','Despair','Rage','Brainwash','Hunger'}
def gate(name,v):
    elem,target=v['a'][1:3];b=v['b'];meta=' '.join(str(x) for x in v.get('c',[]));area=target not in ('1 foe','1 ally','Self','-')
    if elem=='tra':return None,'Ź','Trait P5R; osobista Persona używa wyłącznie traitu Arkany.'
    if 'Technical' in meta or 'crit' in meta.lower():return None,'X','Mechanika Technical lub krytyków nieaktywna.'
    if b[0]==99:
        return (25 if name=='Cadenza' else None),'Z','Moc unikatowa, towarzysza, nawigatora lub fabularna; poza zwykłym zakupem.'
    if elem in elements:
        if 'instakill' in meta:return (65 if b[7]>=50 else 50),'A','Instakill wymaga osobnej adaptacji; próg nie włącza tej mechaniki.'
        if b[2]==0:return 50,'A','Efekt procentowy lub szczególny wymaga adaptacji.'
        if b[4]>1:return 50,'A','Multi hit wymaga osobnego opisu i balansu.'
        if b[2] in (40,50):return (5 if area else 1),'R','Light; standardowa skala obrażeń RPG.'
        if b[2] in (100,120):return (15 if area else 10),'R','Medium; standardowa skala obrażeń RPG.'
        if b[2] in (160,190):return (35 if area else 25),'R','Heavy; standardowa skala obrażeń RPG.'
        return (65 if area else 50),'A','Severe lub efekt szczególny; brak ogólnej skali obrażeń.'
    if elem in ('phy','gun'):
        tier={1:1,2:10,3:10,4:15,5:25,6:35,7:50,8:65}.get(b[0],50)
        if name in ('Headbutt','Assault Dive'):return 10,'R','Dotychczasowy atak medium RPG z ustalonym kosztem.'
        if b[4]>1:return max(25,tier),'A','Multi hit wymaga adaptacji; nie mnożymy automatycznie liczby rzutów.'
        if area:tier=max(tier,5)
        return tier,'A','Wymaga przypisania siły RPG i ewentualnych efektów szczególnych.'
    if elem=='ail':
        status=v.get('c',[''])[0]
        lvl=1 if status in ('Dizzy','Forget','Rage') else 10 if status=='Despair' else 5
        if area:lvl=10 if lvl==1 else lvl+10
        return lvl,'R','Zwykły status według rozdziału 6; szansa z kolumny DC.'
    if elem=='rec':return heal_levels.get(name,50),('R' if name in heal_ready else 'A'),'Leczenie według opisu RPG; R oznacza istniejącą lub opisaną w dodatku regułę.'
    if elem=='sup':
        if name in support:return 1,'R','Pojedynczy parametr, jeden cel, trzy zwykłe tury.'
        lvl=15 if name.startswith(('Matar','Marak','Masuk')) else 10 if name in ('Dekaja','Dekunda') else 35 if name in ('Charge','Concentrate') else 50 if name in ('Heat Riser','Debilitate','Thermopylae') else 35 if 'karn' in name.lower() else 20
        return lvl,'A','Przed zakupem potrzebny dokładny opis homebrew.'
    if elem=='alm':
        lvl={'Megido':25,'Megidola':45,'Megidolaon':65,'Life Drain':15,'Spirit Drain':25,'Foul Breath':15,'Stagnant Air':25,'Ghastly Wail':65}.get(name,50)
        return lvl,'A','Almighty lub szczególny efekt wymaga adaptacji; nie jest All-Out Attack.'
    if elem=='pas':
        status_names=' '.join(ailments)
        if name.startswith('Resist ') and name[7:] in ailments:return 10,'R','+4 do obrony przeciw wskazanemu statusowi.'
        if name.startswith('Null ') and name[5:] in ailments:return 25,'R','Odporność na wskazany zwykły status.'
        if name=='Ailment Boost' or (name.endswith(' Boost') and name[:-6] in ailments):return 10,'R','+2 DC statusu; najwyżej jedna taka premia.'
        if name.startswith('Resist '):lvl=25
        elif name.startswith('Null '):lvl=50
        elif name.startswith(('Repel ','Drain ')):lvl=65
        elif name.startswith('Invigorate '):lvl={'1':25,'2':40,'3':55}.get(name[-1],40)
        elif name.startswith('Regenerate '):lvl={'1':15,'2':30,'3':45}.get(name[-1],30)
        elif name.endswith(' Amp'):lvl=40
        elif name.endswith(' Boost'):lvl=10
        elif name in ('Spell Master','Arms Master','Enduring Soul','Firm Stance','Ali Dance','Victory Cry'):lvl=65
        else:lvl={1:10,2:15,3:25,4:35,5:40,6:50,7:65,8:75}.get(b[0],40)
        return lvl,'A','Pasyw zajmuje slot; przed zakupem potrzebny opis i zasady kumulacji.'
    raise ValueError(name)

gates={name:gate(name,v) for name,v in skills.items()}
assert gates['Agi'][:2]==(1,'R') and gates['Agilao'][0]==10 and gates['Agidyne'][0]==25
assert gates['Kouha'][0]==1 and gates['Kougaon'][0]==25
assert gates['Myriad Truths'][1]=='Z' and gates['Country Maker'][1]=='Ź'
rows=[]
for table in gm.tables:
    if len(table.columns)!=6 or table.cell(0,0).text!='Umiejętność':continue
    table.add_column(Cm(2.0))
    table.cell(0,6).text='Min. lvl / dostęp'
    for row in table.rows[1:]:
        name=row.cells[0].text
        lvl,access,reason=gates[name]
        row.cells[6].text=f'{lvl if lvl is not None else "—"} / {access}'
        rows.append({'skill':name,'type':skills[name]['a'][1],'min_level':lvl,'access':access,'reason':reason})
    widths=[3.6,1.8,1.7,1.7,1.5,5.1,2.0]
    table.autofit=False
    for col,width in zip(table.columns,widths):col.width=Cm(width)
    for row in table.rows:
        for cell,width in zip(row.cells,widths):
            cell.width=Cm(width)
            for par in cell.paragraphs:
                par.paragraph_format.space_after=Pt(2)
                for run in par.runs:run.font.size=Pt(8)
            pr=cell._tc.get_or_add_tcPr()
            if pr.find(qn('w:tcBorders')) is None:
                border=OxmlElement('w:tcBorders')
                for side in ['top','bottom','left','right']:
                    e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');border.append(e)
                pr.append(border)
    for cell in table.rows[0].cells:
        sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'333333');cell._tc.get_or_add_tcPr().append(sh)
        for par in cell.paragraphs:
            for run in par.runs:run.bold=True;run.font.color.rgb=RGBColor(255,255,255)
assert len(rows)==541

def before(anchor,text,style=None):return anchor.insert_paragraph_before(text,style)
anchor=next(p for p in gm.paragraphs if p.style.name=='Heading 2' and 'Katalog Physical' in p.text)
before(anchor,'Minimalne poziomy i dostępność skilli','Heading 3')
before(anchor,'Nowa kolumna podaje próg homebrew, nie oryginalny poziom nauki w P5R. R = gotowy opis RPG; A = wymaga adaptacji efektu; Z = unikat lub moc fabularna, bez zwykłego zakupu; X = mechanika pominięta lub nieaktywna; Ź = źródłowy trait P5R, niedostępny jako dodatkowy trait osobistej Persony. Stara kolumna Adaptacja nadal opisuje status kosztu; nowa kolumna opisuje dostępność efektu. Poziom jest warunkiem zakupu, nie automatycznym nauczeniem się. Cenę nauki i progi EXP ustalimy osobno.')
before(anchor,'Progi magii: light jeden cel 1, light obszar 5, medium jeden cel 10, medium obszar 15, heavy jeden cel 25, heavy obszar 35, severe jeden cel 50 i obszar 65. Almighty, wsparcie, pasywy i efekty szczególne mają osobne progi w wierszach. Wpis A wymaga opisu homebrew nawet po osiągnięciu poziomu. Progi dotyczą nowych osobistych Person; nie zmieniają wstecz dawnych symulacji ani oryginalnych kart fabularnych NPC.')
before(anchor,'Trait osobistej Persony to osobista zdolność Arkany bohatera z rangi 2, przyznana dokładnie raz. Nie dokładamy drugiego traitu z P5R. Źródłowe 92 traity zostają w katalogu wyłącznie jako odniesienie. Nowy podręcznik gracza zawiera pulę startową, opisy sześciu podstawowych buffów/debuffów i Dia oraz zasady przywołania, broni i wymiany NPC.')

anchor=next(p for p in gm.paragraphs if p.style.name=='Heading 2' and p.text.endswith('Guard'))
before(anchor,'Akcje bohatera i wymiana NPC','Heading 3')
before(anchor,'Bohater wybiera jedną zwykłą akcję: skill Persony, podstawowy Physical, strzał Gun, Guard, przedmiot, próbę ucieczki albo wymianę jednego NPC. Wezwanie Persony jest częścią skilla, bez osobnej akcji i kosztu. Podstawowy Physical i strzał to d20 + premia ataku przeciw Obronie, a po trafieniu 1d6 + 4 odpowiedniego typu; oba są darmowe i nie zajmują slotu skilla. W tym prostym wariancie nie liczymy amunicji ani przeładowania.')
before(anchor,'Wymiana NPC zajmuje zwykłą akcję bohatera, bez kosztu zasobów i rzutu; nie może być wykonana jako One More lub Baton Pass. Wybierz jednego przytomnego aktywnego NPC i jednego przytomnego kompana dostępnego w ustalonej przed walką rezerwie. Nowy zajmuje jego miejsce w inicjatywie, przejmuje informację, czy zwykła tura tego miejsca została już zużyta, i nie dostaje dodatkowej akcji za samo wejście. Nie można wymieniać postaci innych graczy ani w ten sposób usuwać nokautu. Zamiana nie zwiększa liczby miejsc w aktywnej drużynie; obrażenia i zużyte SP obu NPC pozostają zapisane. Rezerwa nie odnawia zasobów i nie wykonuje akcji. Co najwyżej jedna taka wymiana drużyny na rundę. Szczegółowe zasady podano w podręczniku gracza.')

for par in gm.paragraphs:
    t=par.text
    if t.startswith('Wersja 0.3'):par.text='Wersja 0.4 • 28 października 2026 • akcje bohatera i progi poziomów skilli'
    elif t.startswith('Układ zmieniono na podstawie wersji 0.2.'):
        par.text='Układ zachowuje uporządkowaną wersję 0.3. Wersja 0.4 dodaje akcje bohatera, wymianę NPC i proponowane minimalne poziomy skilli. Osobista zdolność Arkany pełni rolę jedynego traitu własnej Persony. Szczegóły tworzenia Persony zawiera oddzielny podręcznik gracza.'
    elif 'trait zapisujemy osobno, a jego dostępność i moc wymagają dalszego projektu.' in t:
        par.text=t.replace('trait zapisujemy osobno, a jego dostępność i moc wymagają dalszego projektu.','trait zapisujemy osobno i jest nim osobista zdolność Arkany bohatera, bez drugiej kopii tej zdolności i bez dodatkowego traitu P5R.')
    elif t.startswith('2. Na początku zwykłej tury'):
        par.text=t.replace('atak, skill, przedmiot, Guard, próbę ucieczki','atak Physical, strzał Gun, skill Persony, przedmiot, Guard, wymianę NPC, próbę ucieczki')
gm.core_properties.version='0.4'
gm.save(GM_OUT)

# Player guide follows the existing handbook's typography and page setup.
player=Document(GM_SRC)
for node in list(player.element.body):
    if node.tag!=qn('w:sectPr'):player.element.body.remove(node)
for part in [player.sections[0].header,player.sections[0].first_page_header]:
    for par in part.paragraphs:par.clear()
player.sections[0].header.paragraphs[0].text='Persona 5 RPG  •  Podręcznik gracza'
player.core_properties.title='Persona 5 RPG Podręcznik gracza Tworzenie Persony'
player.core_properties.version='0.1'
def p(t):return player.add_paragraph(t)
def h(t,l=2):return player.add_heading(t,l)
def table(headers,data,widths):
    t=player.add_table(rows=1,cols=len(headers));t.autofit=False
    for col,width in zip(t.columns,widths):col.width=Cm(width)
    for cell,text in zip(t.rows[0].cells,headers):cell.text=text
    for values in data:
        for cell,value in zip(t.add_row().cells,values):cell.text=str(value)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for ri,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for cell,width in zip(row.cells,widths):
            cell.width=Cm(width);pr=cell._tc.get_or_add_tcPr()
            borders=OxmlElement('w:tcBorders')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
            pr.append(borders)
            margins=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'75');e.set(qn('w:type'),'dxa');margins.append(e)
            pr.append(margins)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EAEAEA');pr.append(sh)
            for par in cell.paragraphs:
                par.paragraph_format.space_after=Pt(3)
                for run in par.runs:run.font.size=Pt(9);run.bold=ri==0;run.font.color.rgb=RGBColor(0,0,0)
    p('');return t

player.add_paragraph('Persona 5 RPG','Title')
player.add_paragraph('Podręcznik gracza','Subtitle')
p('Wersja 0.1 • 28 października 2026 • bohater i osobista Persona')
p('Ten fragment prowadzi przez zaprojektowanie własnej Persony i wybór początkowych umiejętności. Opisuje też akcje bohatera oraz progi przyszłego dostępu do skilli. Korzysta z zasad GM 0.4. Tworzenie EXP, ceny nauki, bank, fuzje i skill cards pozostawiamy na kolejne kroki. Progi poziomów i wskazane ograniczenia startowe są nową propozycją homebrew do testu.')
p('Na start: jedna osobista Persona, jedna słabość, jeden Resist, cztery skille i jeden trait Arkany. Maksimum po rozwoju to osiem skilli; trait oraz podstawowe akcje nie zajmują tych miejsc.')
h('1 Twój bohater i zasoby',1)
p('Zapisz imię, wiek, zajęcie i powód wejścia w historię. Wybierz jedną osobistą Arkanę, inną niż pozostałych graczy. Świat jest wyłączony z początkowego wyboru. Pięć cech społecznych zaczyna na randze 1 według podręcznika GM.')
p('Dla poziomu L od 1 do 99 bazowe maksymalne HP = 34 + L, a SP = 30 + L. Na poziomie 1 zaczynasz z pełnymi 35 HP i 31 SP. Dodaj ewentualny stały bonus traitu Arkany. Kolejny poziom zwiększa oba maksima o 1 bez leczenia; trening i inne bonusy zapisuj oddzielnie. Pełna tabela jest w rozdziale 11 podręcznika GM. Początkowy atak i Obrona nie wynikają z wyglądu Persony; do prób zachowujemy robocze +5 ataku i Obronę 12 z dotychczasowego zestawu. Ich rozwój ustalimy razem z awansem.')
h('2 Zaprojektuj osobistą Personę',1)
h('Nazwa wygląd i historia')
p('Samodzielnie nazwij Personę, opisz jej wygląd i historię. Zachęcamy do własnych pomysłów: inspiracji mitem, legendą, literaturą lub symbolem ważnym dla bohatera, a także całkowicie autorskiej postaci. Nie musisz wybierać istniejącej Persony z kompendium. Opisz, czego jest wyrazem i jak wiąże się z buntem lub pragnieniami bohatera.')
p('Wygląd nie daje dodatkowych ataków, lotu, odporności ani liczby tur. Skrzydła, pancerz lub wiele ramion mogą być częścią opisu. Mechaniczne możliwości wynikają z karty. Persona dzieli HP/SP z użytkownikiem; nie jest drugim walczącym ani dodatkowym celem.')
h('Jedna słabość i jeden Resist')
p('Na start wybierz dokładnie jedną słabość i jeden Resist na dwa różne typy. Dla bezpiecznej, wspólnej puli startowej proponujemy osiem typów magicznych: Fire, Ice, Electricity, Wind, Psy, Nuclear, Bless i Curse. Physical, Gun i Almighty pozostają Normal. Ograniczenie do tych ośmiu typów jest propozycją balansu startu; nie zmieniamy nim istniejących kart Shadows lub NPC.')
p('Weak: ×1,5 obrażeń i możliwość Down/One More. Resist: ×0,5 obrażeń. Pozostałe typy: Normal. Nie zaczynasz z Null, Drain, Repel, drugą odpornością ani odpornością na status. Słabość i Resist nie dotyczą tego samego typu. Wygląd i backstory nie przyznają dodatkowych właściwości. Dostęp do późniejszych pasywów odporności wymaga poziomu i osobnego opisu; nie zakładamy automatycznego usunięcia początkowej słabości.')
h('Cztery początkowe skille')
p('Wybierz bez kosztu nauki cztery różne skille z poniższej puli poziomu 1. Proponowane ograniczenie: początkowe skille z obrażeniami obejmują najwyżej dwa różne żywioły magiczne. Pozostałe miejsca możesz przeznaczyć na leczenie, status lub wsparcie. Nie ma obowiązkowego uzdrowiciela ani obowiązku wyboru konkretnej roli. Na start wybieramy aktywne skille; pasywy odblokujemy od wyższych poziomów. Wszystkie skille i pasywy w późniejszym zestawie liczą się do limitu ośmiu.')
starter_rows=[]
for name in sorted(basic_elements):
    v=skills[name];effect=f'1 wróg; light {v["a"][1]}; 1d6 + 4'
    extra={'Agi':'Burn DC 6','Bufu':'Freeze DC 6','Zio':'Shock DC 6'}.get(name,'bez statusu')
    starter_rows.append((name,effect+'; '+extra,'1 SP'))
starter_rows += [
('Dia','1 sojusznik; odnów 10 HP','1 SP'),
('Patra','1 sojusznik; usuń Dizzy, Forget, Hunger i Sleep','1 SP'),
('Baisudi','1 sojusznik; usuń Burn, Freeze i Shock','1 SP'),
('Dazzler','1 wróg; Dizzy; obrona DC 15','1 SP'),
('Makajam','1 wróg; Forget; obrona DC 15','1 SP'),
('Taunt','1 wróg; Rage; obrona DC 15','1 SP'),
('Tarukaja','1 sojusznik; +4 obrażenia z ataków','2 SP'),
('Rakukaja','1 sojusznik; −4 otrzymywane obrażenia z ataków','2 SP'),
('Sukukaja','1 sojusznik; +2 do trafienia i +2 Obrony','2 SP'),
('Tarunda','1 wróg; −4 obrażenia z jego ataków','2 SP'),
('Rakunda','1 wróg; +4 otrzymywane obrażenia z ataków','2 SP'),
('Sukunda','1 wróg; −2 do trafienia i −2 Obrony','2 SP'),
]
table(['Skill','Działanie RPG','Koszt'],starter_rows,[3.0,12.7,1.7])
p('Skróty typów w tabeli: fir Fire, ice Ice, ele Electricity, win Wind, psy Psy, nuk Nuclear, ble Bless, cur Curse. Skill statusowy wymaga tylko obrony celu; atak z obrażeniami najpierw musi trafić. Cel rzuca d20; wynik równy DC lub wyższy broni przed statusem. Pełne czasy i skutki statusów opisuje rozdział 6 podręcznika GM.')
p('Sześć podstawowych buffów i debuffów działa bez rzutu przez trzy kolejne zwykłe tury odbiorcy. Kolejność: obrażenia z kości i płaskie premie/kary, następnie Hunger, Weak/Resist i Guard. Minimum 0, zaokrąglenie w dół na końcu. Ta sama premia nie kumuluje się ze sobą, przeciwne efekty tego samego parametru znoszą się, a ponowienie odnawia czas. Zmiana obrażeń nie zmienia kosztu HP skilla, Burn ani odnowy HP. Pełne zasoby nie mogą przekroczyć maksimum. Te opisy doprecyzowują dotychczasową skalę +4/−4 oraz +2/−2; są roboczą adaptacją.')
h('3 Trait odpowiadający Arkanie',1)
p('Trait osobistej Persony to ta sama osobista zdolność Arkany bohatera, którą otrzymuje od początku z rangi 2 podstawowego katalogu Arkan. Zapisujemy ją raz. Nie dodajemy drugiego traitu z P5R i nie kupujemy źródłowych traitów za EXP. Trait nie zajmuje jednego z ośmiu slotów. Może działać również poza wezwaniem Persony, jeśli pozwala na to jego opis, np. podczas śledztwa.')
p('Poniżej skróty początkowych traitów. Aktywne efekty działają raz na wyprawę, chyba że podano inaczej. Stałe zwiększenie maksimum jest bierne; wytwarzanie wymaga bloku aktywności. Safe room i respawn nie odnawiają użyć. W razie szczegółów obowiązują opisy rozdziału 9 podręcznika GM. Nie otrzymujesz wyższych rang własnego traitu przez relację ze sobą.')
trait_rows=[]
src=Document(GM_SRC)
for t in src.tables:
    if t.cell(0,0).text!='Ranga':continue
    prev=t._tbl.getprevious()
    while prev is not None:
        if prev.tag==qn('w:p'):
            par=Paragraph(prev,src)
            if par.style.name.startswith('Heading'):
                name=par.text.split(' ',1)[1].split(' — ')[0];break
        prev=prev.getprevious()
    if name=='Świat':continue
    trait_rows.append((name,t.cell(1,1).text))
assert len(trait_rows)==23
table(['Arkana','Osobisty trait na start'],trait_rows,[3.3,14.1])
h('4 Co możesz zrobić w walce',1)
p('W swojej zwykłej turze wybierasz jedną akcję z tabeli. Wezwanie Persony jest częścią skilla: nie płacisz osobnej akcji ani SP za samo przywołanie. Nie dostajesz równocześnie darmowego ataku bohatera. One More i Baton Pass mogą dać dodatkowe działania według zasad GM; nie są gwarantowaną drugą akcją w każdej rundzie.')
table(['Akcja','Rozstrzygnięcie'],[
('Skill Persony','Zapłać koszt i zastosuj opis. Atak: d20 + atak ≥ Obrona. Leczenie/wsparcie: bez rzutu; czysty status: obrona celu.'),
('Atak podstawowy','Jeden wróg; d20 + atak ≥ Obrona; 1d6 + 4 Physical; bez HP/SP i bez slotu skilla.'),
('Strzał z broni palnej','Jeden wróg; identyczny test i 1d6 + 4 Gun. Bez HP/SP i bez slotu skilla. Dla prostoty bez liczenia amunicji i przeładowania.'),
('Guard','Otrzymujesz 40% obrażeń po właściwości celu i nie możesz dostać Down. Ochrona trwa do początku następnej zwykłej tury.'),
('Przedmiot','Zużywasz jedną sztukę; zwykle bez rzutu. Cel i ograniczenia według przedmiotu. Zręczność może dać osobną dodatkową czynność.'),
('Ucieczka drużyny','Zwykła akcja, d20 bez bonusów; 11+ oznacza sukces. Jedna próba drużyny na rundę. Porażka zużywa twoją akcję.'),
('Wymiana NPC','Zwykła akcja, bez rzutu i zasobów; zamieniasz jednego aktywnego NPC na dostępnego kompana z rezerwy według zasad poniżej.')
],[4.0,13.4])
p('Atak Physical i strzał różnią się właściwością, nie kośćmi: Resist Gun działa na strzał, ale nie na atak Physical. Oba mogą trafić w odpowiednią słabość i wywołać Down/One More. Rodzaj, wygląd i nazwa broni są swobodne; na tym etapie nie dają innych kości ani dodatkowych trafień. Cała walka używa abstrakcyjnego zasięgu każdy sięga każdego.')
h('Wymiana NPC w praktyce')
p('Przed walką GM wskazuje, którzy towarzysze są dostępni w rezerwie. Nie można przywołać osoby nieobecnej w scenie ani stworzyć nowego NPC samą akcją. Zamiana dotyczy przytomnego, zdolnego do działania aktywnego NPC i przytomnego rezerwowego; nigdy postaci innego gracza. Nie zwiększa liczby aktywnych miejsc ustalonej dla drużyny. Nie służy do wynoszenia nieprzytomnych, kasowania statusów lub darmowego leczenia.')
p('Nowy NPC zajmuje dokładnie miejsce poprzednika w inicjatywie. Jeśli ta zwykła tura została już zużyta w rundzie, nowy kompan czeka do następnej; jeśli jeszcze nie, może działać w tym miejscu. Wejście nie daje dodatkowego ataku. Obaj zachowują aktualne HP/SP i pozostałe skutki, które nie skończyły się według własnych zasad. Rezerwa nie działa ani nie regeneruje zasobów. Zamiana nie przerywa liczników statusów: jeśli wymagają tur, GM rozlicza je w dawnym miejscu inicjatywy, bez przyznawania rezerwowemu akcji. Co najwyżej jedna zamiana drużyny na rundę, wyłącznie ze zwykłej akcji, bez One More lub Baton Pass.')
p('Przykład: kolejność to bohater, NPC A, wróg. Bohater zużywa akcję na zamianę A na B. B może wykonać późniejszą turę tego miejsca. Jeśli bohater wymieni A dopiero po jego turze, B nie dostaje drugiej zwykłej tury w tej samej rundzie. Nowy NPC jest także traktowany jako ta sama pozycja na potrzeby limitów dodatkowych akcji w bieżącym łańcuchu.')
h('5 Poziomy dostępności i późniejsza nauka',1)
p('Poziom bohatera i osobistej Persony traktujemy na potrzeby progów jako ten sam poziom L; nie prowadzimy dwóch liczników EXP. Awans odblokowuje możliwość nauki, a nie automatycznie wszystkie skille. Sposób płacenia za naukę, jej ceny i uzyskiwanie EXP ustalimy w kolejnym kroku. Cztery początkowe skille są darmowe. Nie wydajemy zwykłego HP/SP na stałe nauczenie się skilla.')
table(['Min. poziom','Rodzaj','Przykład'],[
(1,'Light, jeden cel','Agi, Bufu, Zio, Garu, Psi, Frei, Kouha, Eiha'),
(5,'Light, wszyscy wrogowie','Maragi, Mabufu, Mazio'),
(10,'Medium, jeden cel','Agilao, Bufula, Freila; także Diarama'),
(15,'Medium, wszyscy wrogowie','Maragion, Mabufula, Mafreila'),
(25,'Heavy, jeden cel','Agidyne, Bufudyne, Freidyne'),
(35,'Heavy, wszyscy wrogowie','Maragidyne, Mabufudyne, Mafreidyne'),
(50,'Severe, jeden cel','Inferno, Diamond Dust; wymaga adaptacji obrażeń'),
(65,'Severe, wszyscy wrogowie','Blazing Hell, Ice Age; wymaga adaptacji obrażeń'),
('Osobno','Physical, Gun, Almighty, leczenie, statusy, wsparcie i pasywy','Sprawdź konkretny wiersz katalogu GM 0.4.')
],[2.0,6.0,9.4])
p('Gotowe standardowe ataki light/medium/heavy zadają odpowiednio 1d6 + 4, 2d6 + 6 i 3d6 + 8. Wersja obszarowa działa na wszystkich wrogów: osobny rzut trafienia na cel i jeden wspólny rzut obrażeń; każdy cel osobno rozlicza właściwości i ewentualny status. Jedna akcja daje najwyżej jedno One More niezależnie od liczby przewróconych. Nie przenosimy źródłowych współczynników P5R jako dodatkowych mnożników.')
p('Katalog GM 0.4 ma kolumnę Min. lvl / dostęp dla wszystkich 541 wpisów. R: gotowy efekt RPG. A: wymagany dodatkowy opis adaptacji. Z: unikat, poza zwykłym zakupem. X: nieaktywna mechanika. Ź: źródłowy trait P5R, bez zakupu. Liczba przy A jest proponowanym przyszłym progiem, nie zgodą na użycie nieopisanej mocy. Nie wymagamy wcześniejszego kupienia słabszej wersji: wymagany jest poziom i przyszły koszt nauki.')
p('Maksymalnie osiem skilli łącznie z pasywami. Przy nauczeniu się dziewiątego wybierz jeden zastępowany; nie ma darmowego przełączania całej biblioteki między walkami. Czy i jak odzyskać zapomniany skill, określimy razem ze skill cards. Jeśli kampania zaczyna się na wyższym poziomie, nie przyznajemy automatycznie wszystkich odblokowanych mocy; budżet takiej postaci ustalimy razem z EXP.')
h('6 Przykład i karta do wypełnienia',1)
p('Przykład poziomu 1: Arkana Rydwan, Persona Latarnik, postać w płaszczu z latarnią zamiast serca. Symbolizuje wytrwałość w szukaniu drogi dla innych. Weak Ice, Resist Fire, reszta Normal. Skille: Agi, Garu, Dia, Tarunda. Trait Rydwanu daje +2 maksymalnego HP, więc bohater zaczyna z 37/37 HP i 31/31 SP. Trait nie jest piątym skillem. Podstawowy Physical i strzał Gun są dostępne niezależnie od czterech skilli.')
table(['Pole','Twoja postać'],[
('Bohater i poziom',''),('Arkana i trait',''),('Persona i jej imię',''),('Wygląd i symbolika',''),('Historia i więź z bohaterem',''),('Maksymalne i aktualne HP/SP',''),('Atak i Obrona',''),('Słabość',''),('Resist',''),('Skill 1 i koszt',''),('Skill 2 i koszt',''),('Skill 3 i koszt',''),('Skill 4 i koszt',''),('Dalsze sloty 5–8','Na start puste'),('Użycia traitu i innych zdolności',''),('Dostępni towarzysze i rezerwa','')
],[5.4,12.0])
p('Kontrola przed grą: dokładnie cztery początkowe skille, jeden trait Arkany zapisany raz, jedna słabość i jeden Resist, pełne zasoby oraz brak nieopisanych dodatkowych mocy z wyglądu. Na następnym etapie dopracujemy EXP, bank Person, fuzje oraz skill cards.')

# Real TOC, evaluated by Word during pagination.
title=player.paragraphs[5]
toc_title=title.insert_paragraph_before('Spis treści','Title');toc_title.paragraph_format.page_break_before=True
toc=title.insert_paragraph_before()
for typ in ['begin','separate','end']:
    run=OxmlElement('w:r');field=OxmlElement('w:fldChar');field.set(qn('w:fldCharType'),typ);run.append(field);toc._p.append(run)
    if typ=='begin':
        run=OxmlElement('w:r');inst=OxmlElement('w:instrText');inst.set(qn('xml:space'),'preserve');inst.text=' TOC \\o "1-2" \\h \\z \\u ';run.append(inst);toc._p.append(run)
    elif typ=='separate':
        run=OxmlElement('w:r');text=OxmlElement('w:t');text.text='Spis zostanie przeliczony w Wordzie.';run.append(text);toc._p.append(run)
for st in ['Title','Heading 1','Heading 2','Heading 3']:
    player.styles[st].font.color.rgb=RGBColor(0,0,0)
player.save(PLAYER)

# Structural and data-preservation checks.
g=Document(GM_OUT);pcheck=Document(PLAYER)
new_skill_tables=[t for t in g.tables if len(t.columns)==7 and t.cell(0,0).text=='Umiejętność']
assert len(new_skill_tables)==16 and sum(len(t.rows)-1 for t in new_skill_tables)==541
old_tables=[t for t in src.tables if len(t.columns)==6 and t.cell(0,0).text=='Umiejętność']
for old,new in zip(old_tables,new_skill_tables):
    assert [[c.text for c in row.cells] for row in old.rows]==[[c.text for c in row.cells[:6]] for row in new.rows]
assert len(g.tables)==60
assert sum(len(t.rows)-1 for t in g.tables if len(t.columns)==6 and t.cell(0,0).text=='Przedmiot')==157
assert hashlib.sha256(GM_SRC.read_bytes()).hexdigest()==source_hash
for name,effect,cost in starter_rows:
    assert gates[name][:2]==(1,'R'),name
    oldrow=next(row for t in old_tables for row in t.rows[1:] if row.cells[0].text==name)
    assert oldrow.cells[3].text==cost,(name,oldrow.cells[3].text,cost)
report={'gm_source_sha256':source_hash,'gm_output':str(GM_OUT),'player_output':str(PLAYER),'catalog_entries':len(rows),'access_counts':dict(Counter(r['access'] for r in rows)),'initial_skills':len(starter_rows),'arcana_traits':len(trait_rows),'source_unchanged':True,'existing_skill_costs_preserved':True,'level_thresholds_are_homebrew':True}
(R/'player_start_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'skill_level_gates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with (R/'skill_level_gates.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
print(json.dumps(report,ensure_ascii=False,indent=2))
