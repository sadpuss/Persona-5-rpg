import json,re,math,csv
from pathlib import Path
from copy import deepcopy
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

R=Path(__file__).parent
path=R/'Persona_5_RPG_Zasady_0_2.docx'
items=json.loads((R/'p5r_recovery_items.json').read_text(encoding='utf-8'))
assert len(items)==157 and len({x['name'] for x in items})==157
doc=Document(path)
if any(p.text=='Przedmioty odnawiające HP i SP' for p in doc.paragraphs):raise RuntimeError('Katalog już istnieje')
def p(s):return doc.add_paragraph(s)
def h(s):doc.add_heading(s,2)
def page(s):doc.add_page_break();doc.add_heading(s,1)
def table(headers,rows,widths):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
    for col,w in zip(t.columns,widths):col.width=Cm(w)
    for i,v in enumerate(headers):t.rows[0].cells[i].text=v
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for vals in rows:
        cs=t.add_row().cells
        for i,v in enumerate(vals):cs[i].text=str(v)
    for ri,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for ci,c in enumerate(row.cells):
            c.width=Cm(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=c._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
            for side in ['top','bottom','left','right']:
                el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');b.append(el)
            pr.append(b)
            sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'333333' if ri==0 else ('F2F2F2' if ri%2 else 'FFFFFF'));pr.append(sh)
            m=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                el=OxmlElement('w:'+side);el.set(qn('w:w'),'80');el.set(qn('w:type'),'dxa');m.append(el)
            pr.append(m)
            for par in c.paragraphs:
                par.paragraph_format.space_after=Pt(2);par.paragraph_format.line_spacing=1.0
                for run in par.runs:
                    run.font.size=Pt(9)
                    if ri==0:run.bold=True;run.font.color.rgb=RGBColor(255,255,255)
    p('')
    return t

page('Przedmioty odnawiające HP i SP')
p('Aktualizacja z 28 października 2026. Katalog obejmuje 157 nazw zużywalnych przedmiotów z tabeli Items in Persona 5 Royal, których efekt przywraca HP, SP lub wskrzesza. Są w nim leki, żywność, napoje, racje, uprawy i prezenty fabularne. Same nazwy zachowujemy po angielsku, aby łatwo porównywać je z grą. Efekty RPG są propozycją adaptacji do testów.')
p('Kompletność odnosi się do wskazanej listy P5R, nie do wszystkich przedmiotów całej serii ani nieużywanych wpisów debugowych. Katalog nie obejmuje ekwipunku odnawiającego zasoby pasywnie, skilli ani przedmiotów usuwających wyłącznie status bez leczenia HP/SP. Nie ustala cen, dostępności i receptur.')
h('Przelicznik')
p('Stała liczba HP lub SP w RPG = liczba z P5R podzielona przez 5, zaokrąglona w górę, minimum 1. Efekty procentowe liczymy od maksymalnego HP/SP odbiorcy w naszym systemie, zaokrąglając w dół, minimum 1. Pełne odnowienie oznacza uzupełnienie do naszego maksimum, nie do wartości z gry. Stałe wartości przedmiotów nie rosną automatycznie z poziomem.')
table(['Efekt P5R','Efekt RPG','Przykład'],[
('50 / 100 / 200 HP','10 / 20 / 40 HP','Medicine / Recov-R 100 mg / Takemedic'),
('5 / 10 / 30 SP','1 / 2 / 6 SP','Arginade / Soul Drop / Leblanc Coffee'),
('50 / 100 SP','10 / 20 SP','Snuff Soul / Chewing Soul'),
('30% HP','30% maksymalnego HP','Life Stone: 18 HP przy maksimum 60'),
('20% / 40% SP','20% / 40% maksymalnego SP','Stamina Kit: 11 / 22 SP przy maksimum 56'),
('Pełne HP albo SP','Uzupełnij dany zasób do maksimum','Bead / Soul Food')
],[4.3,5.2,7.9])
p('Testowy przedmiot +20 SP z wcześniejszych symulacji może teraz odpowiadać Chewing Soul. Soma i pełna regeneracja są silnymi nagrodami; sama obecność w katalogu nie oznacza swobodnego zakupu ani stałych dostaw. Poziom dostępności ustalimy przy ekonomii gry.')
h('Zasady używania')
p('Jeden egzemplarz zużywa się po jednym użyciu. W walce użycie zajmuje jedną akcję i nie wymaga rzutu; można wykorzystać dodatkową akcję. Przedmiot dla drużyny działa na każdego uprawnionego odbiorcę osobno i zużywa tylko jeden egzemplarz. Nie przekraczamy maksimów. Zwykłe leczenie oraz Soma nie wskrzeszają i nie przywracają HP/SP postaci przy 0 HP; służą do tego wpisy z części Wskrzeszanie.')
p('W/P oznacza użycie w walce i poza nią; P oznacza wyłącznie poza walką; S oznacza tylko safe room lub inną ustaloną bezpieczną strefę, bez aktywnej walki. Przedmioty z kolumny Battle źródła dopuszczamy również poza walką, chyba że ograniczenie miejsca mówi inaczej. To jawne uproszczenie zasad dostępu; szczególne jedzenie oznaczone w źródle wyłącznie Field pozostaje poza walką. Samo wejście do safe roomu nadal nie odnawia zasobów.')

page('Skutki dodatkowe przedmiotów')
p('Odnawianie HP/SP jest gotowe do prób. Dodatkowe efekty zapisujemy osobno, aby nie usuwać kosztów lub korzyści danego przedmiotu. Poza walką premie i kary bojowe nie obowiązują w kolejnej potyczce. Podczas walki proponujemy następujące wartości na trzy kolejne zwykłe tury odbiorcy; efekty tego samego typu nie kumulują się, a ponowienie odnawia czas.')
table(['Skrót w tabeli','Efekt RPG'],[
('ATK + / ATK −','Dodaj 4 do zadawanych obrażeń / odejmij 4 od zadawanych obrażeń. Minimum 0.'),
('DEF + / DEF −','Odejmij 4 od otrzymywanych obrażeń / dodaj 4 do otrzymywanych obrażeń. Minimum 0.'),
('CEL + / CEL −','Premia +2 / kara −2 do ataku i Obrony.'),
('Wszystkie −','ATK −, DEF − i CEL − równocześnie; nie obniża maksymalnego HP/SP.'),
('Hunger','Przedmiot usuwa Hunger; szczegółowe działanie statusu pozostaje do projektu.'),
('Statusy','Usuwa zwykłe negatywne statusy po opracowaniu ich zasad; nie usuwa Down, nokautu ani efektu fabularnego.'),
('Trening','Oryginalny przedmiot wspiera trening. Liczbę premii do daily life ustalimy osobno; obecnie stosujemy tylko leczenie.')
],[4.1,13.3])
p('Modyfikatory obrażeń stosujemy przed Weak/Resist, zgodnie z obecną kolejnością dla Tarundy. Nowe premie ATK oraz kary DEF są propozycją do testów, nie wynikiem wcześniejszych symulacji. Dodatnie i ujemne modyfikatory tego samego parametru znoszą się; nie sumujemy kilku ATK + lub kilku DEF −.')
h('Wskrzeszanie jako nowa propozycja')
p('Przedmiot wskrzeszający działa tylko na postać przy 0 HP, nie na fabularnie zmarłą. Przywraca wskazany procent jej maksymalnego HP, ale nie odnawia SP. Nie przyznaje dodatkowej akcji ani nie cofa już zużytej tury. Jeśli zwykła tura odbiorcy w tej rundzie jeszcze nie nastąpiła, może w niej działać normalnie. Przy całej drużynie nieprzytomnej nikt samodzielnie nie użyje przedmiotu. To nowa propozycja, niezastosowana w poprzednich testach kończonych po pierwszym nokaucie.')
h('Czytanie tabel')
p('Kolumna P5R podaje sam efekt liczbowy; obie kolumny odnoszą się do tego samego celu z tabeli. 1 oznacza jednego sojusznika, D całą drużynę, a przy wskrzeszaniu wyłącznie uprawnione nieprzytomne postacie. Uwagi zawierają dodatkowy skutek, a nie dodatkowy koszt. Znak — oznacza brak dodatkowego efektu w zakresie katalogu.')

notes={
'Protein':'Trening','Moist Protein':'Trening','Imported Protein':'Trening',
'Phantom Wafers':'Statusy','Strawberry Daifuku':'Statusy','Yakisoba Pan':'Hunger',
'Torimeshi Ration':'Hunger','Veg. Stew Ration':'Hunger','Mont Blanc Ration':'Hunger',
'Muscle Drink':'ATK +; DEF −','MRE Ration':'ATK −; CEL +','Oatmeal Ration':'CEL −; ATK +',
'Fruit Ration':'DEF −; ATK +','Kommissbrot':'CEL −','Beef Patty Ration':'DEF −','D Ration':'ATK −',
'Osechi Ration':'Wszystkie −','Kebab Ration':'ATK −; CEL +','Odd Morsel':'ATK +; CEL −',
'Rancid Gravy':'CEL +; ATK −','Sikkenine':'CEL −','Sikkenine A':'ATK −','Sikkenine EX':'DEF −',
'Strawberry Curry':'DEF −; CEL −','Mayo Locust':'ATK −; CEL −','Miso Starfish':'ATK −; DEF −',
'Mystery Stew':'Wszystkie −'}

records=[]
for x in items:
    desc=x['description'];name=x['name'];low=desc.lower()
    mode='S' if 'safe places' in low else ('W/P' if x['battle'] else 'P')
    target='D' if 'all allies' in low or 'all fallen allies' in low else '1'
    if 'revives' in low:
        group='Wskrzeszanie';orig='50% HP' if '50%' in desc else '100% HP';new=orig
    elif 'hp and sp' in low:
        group='HP i SP';orig='Pełne HP/SP';new=orig
    else:
        resource='SP' if re.search(r'\bSP\b',desc) else 'HP';group=resource
        if 'fully restores' in low:
            orig='Pełne '+resource;new=orig
        else:
            match=re.search(r'(\d+)(%)?\s+'+resource,desc)
            if not match:raise ValueError(x)
            n=int(match[1]);pct=bool(match[2]);orig=f'{n}{"%" if pct else ""} {resource}'
            new=orig if pct else f'{max(1,math.ceil(n/5))} {resource}'
    records.append({'name':name,'group':group,'target':target,'original':orig,'rpg':new,'mode':mode,'note':notes.get(name,'—')})

for group,title in [('HP','Przedmioty przywracające HP'),('SP','Przedmioty przywracające SP'),('HP i SP','Przedmioty przywracające oba zasoby'),('Wskrzeszanie','Przedmioty wskrzeszające')]:
    page(title)
    selected=sorted([r for r in records if r['group']==group],key=lambda r:r['name'].casefold())
    p(f'Liczba wpisów: {len(selected)}. Wartości RPG są propozycjami; cel i warunki użycia znajdują się przy każdym przedmiocie.')
    table(['Przedmiot','Cel','P5R','RPG','Użycie','Uwagi'],[[r[k] for k in ['name','target','original','rpg','mode','note']] for r in selected],[4.4,.7,2.6,2.6,1.2,5.9])

h('Źródło katalogu')
p('Megami Tensei Wiki, Items in Persona 5 Royal. Odczyt 28 października 2026. Wybrano wszystkie 157 wierszy odnawiających HP/SP lub wskrzeszających z sekcji Consumables. Opisy fabularne i ceny nie zostały przeniesione. Podział użycia S jest nadrzędny wobec ogólnego oznaczenia Battle w tabeli źródła.')
p('https://megatenwiki.com/wiki/Items_in_Persona_5_Royal')
p('Nazwy prezentów od postaci kanonicznych są zachowane dla identyfikacji. W autorskiej przygodzie analogiczny przedmiot może pochodzić od własnego NPC; nie zmienia to tabeli leczenia. Dostępność pełnego odnowienia i ilość zapasów należy dopasować do odcinka Pałacu.')

for par in doc.paragraphs:
    if par.text.startswith('Wersja 0.2'):par.text='Wersja 0.2 • aktualizacja 28 października 2026 • katalog regeneracji'
backup=R/'Persona_5_RPG_Zasady_0_2_przed_przedmiotami.docx'
if not backup.exists():backup.write_bytes(path.read_bytes())
doc.save(path)
with (R/'recovery_items_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
check=Document(path)
assert len(check.tables)==30
assert sum(len(t.rows)-1 for t in check.tables[-4:])==157
level=next(t for t in check.tables if t.rows[0].cells[0].text=='Poziom')
assert len(level.rows)==100
assert [c.text for c in level.rows[-1].cells]==['99','133','129']
for name,expected in [('Medicine','10 HP'),('Chewing Soul','20 SP'),('Leblanc Coffee','6 SP'),('Life Stone','30% HP'),('Soma','Pełne HP/SP')]:
    assert next(r for r in records if r['name']==name)['rpg']==expected
print('OK',len(records),'items;',len(check.tables),'tables; levels 1–99 preserved')
