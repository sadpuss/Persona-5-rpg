import json, math, collections, csv
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH

R=Path(__file__).parent
load=lambda n:json.loads((R/n).read_text(encoding='utf-8-sig'))
skills={}
for filename in ['p5_base_skill_data.json','p5r_skill_data.json']:
    for v in load(filename).values():skills[v['a'][0]]=v
doc=Document(R/'Persona_5_RPG_Zasady_0_1.docx')
doc.core_properties.title='Persona 5 RPG Zasady i katalog umiejętności'
for par in doc.paragraphs:
    if par.text.startswith('Wersja 0.1'):par.text='Wersja 0.2 • 25 października 2026'
for par in doc.sections[0].footer.paragraphs:
    for run in par.runs:run.text=run.text.replace('0.1','0.2')
def p(t):return doc.add_paragraph(t)
def h(t):doc.add_heading(t,2)
def page(t):doc.add_page_break();doc.add_heading(t,1)
def table(head,rows,widths):
    t=doc.add_table(rows=1,cols=len(head));t.autofit=False
    for col,w in zip(t.columns,widths):col.width=Cm(w)
    for i,x in enumerate(head):t.rows[0].cells[i].text=x
    el=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(el)
    for vals in rows:
        cs=t.add_row().cells
        for i,x in enumerate(vals):cs[i].text=str(x)
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
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'75');e.set(qn('w:type'),'dxa');m.append(e)
            pr.append(m)
            for par in c.paragraphs:
                par.paragraph_format.space_after=Pt(2);par.paragraph_format.line_spacing=1.0
                for run in par.runs:
                    run.font.size=Pt(9)
                    if ri==0:run.bold=True;run.font.color.rgb=RGBColor(255,255,255)
    p('')
    return t

page('Proponowane wzory na HP i SP')
p('Nowa propozycja wersji 0.2. Nie zastępuje jeszcze automatycznie testowych kart z poprzednich rozdziałów. HP i SP należą do bohatera, a nie do osobnej przywoływanej Persony. L oznacza poziom bohatera; zaczyna się od 1.')
h('Bohaterowie')
p('Maksymalne HP = 34 + L. Maksymalne SP = 30 + L. Każdy awans daje zatem +1 do obu maksimów. Na poziomie 26 otrzymujemy dokładnie dotychczasowe 60 HP i 56 SP. Awans nie odnawia automatycznie bieżących zasobów; dodatkowe maksima można uzupełnić normalnie.')
table(['Poziom','Maksymalne HP','Maksymalne SP'],[(n,34+n,30+n) for n in [1,5,10,20,26,30]],[4,6.7,6.7])
p('Ten wzór jest punktem startowym do testów poziomów 1–30. Nie został sprawdzony w pełnej kampanii. Wysokie poziomy, Severe i silniejsze leczenie wymagają wspólnego testu; liniowe przedłużenie wzoru do poziomu 99 nie stanowi jeszcze gotowego balansu endgame.')
h('Opcjonalne profile')
p('Najpierw testujemy wariant bez modyfikatorów. Później można dopuścić stałe przesunięcie: profil fizyczny +8 HP i −8 SP; profil magiczny −4 HP i +4 SP. Nie nadajemy go automatycznie na podstawie nazwy Persony i nie kumulujemy profili. Są to propozycje, nie wartości użyte w poprzednich symulacjach.')
h('Dlaczego nie jeden dzielnik z P5R')
p('Koszty skilli, liczba walczących, dodatkowe akcje i czas starcia zmieniły się względem gry. Dlatego nie stosujemy jednego dzielnika do HP i SP wszystkich bohaterów i Shadows. Nazwy, żywioły i role przenosimy z P5R; wytrzymałość projektujemy do naszej skali obrażeń i długości wyprawy.')

page('Wyliczanie zasobów przeciwników')
h('HP z długości starcia')
p('Łączne HP przeciwników ≈ R × (D + K − H). Wynik zaokrąglij do najbliższych 5 HP. R to oczekiwana liczba rund, D to średnie obrażenia drużyny na rundę już po celności i właściwościach, K to średni koszt HP płacony przez przeciwników na rundę, H to ich średnie leczenie na rundę. To przybliżenie do pierwszej karty, nie gwarancja długości walki.')
p('Przykład: dwóch bohaterów atakuje medium za średnio 13. Przy +5 przeciw Obronie 13 trafiają w 65% przypadków. Bez słabości i dodatkowych akcji D = 2 × 13 × 0,65 = 16,9. Pięć rund bez leczenia i kosztów HP sugeruje około 85 HP. Jeśli miniboss płaci średnio 6 HP co rundę, wynik rośnie do około 115 HP. Dostępna słabość i One More dodatkowo zwiększają D, więc mogą uzasadniać 140 HP.')
p('Dla grupy rozdziel wynik między Shadows według ich ról, potem sprawdź przebieg: zabity wcześniej przeciwnik przestaje atakować. D nie pozostaje stałe, kiedy brakuje SP, trwa leczenie lub drużyna dopiero szuka słabości. Dotychczasowe 28–36 HP dla drobnego Shadow i 140 HP minibossa są przykładami, nie poziomami obowiązkowymi.')
h('SP według liczby użyć')
p('Maksymalne SP przeciwnika = suma kosztów zaplanowanych użyć skilli. Na początek zwykłemu Shadow zaplanuj 3–4 użycia magii, a minibossowi 6–8. Przykładowo cztery medium po 2 SP oznaczają pulę 8 SP. Gdy brakuje zasobów, przeciwnik przechodzi na darmowy atak lub inną dostępną akcję. Nie potrzebuje setek SP tylko dlatego, że miał je w P5R.')
p('Ataki fizyczne wydają HP według karty i nie mogą sprowadzić użytkownika poniżej 1 HP. Miniboss łączący magię, leczenie i ataki za HP potrzebuje osobnego rozpisania całego zestawu; nie dodajemy pełnych budżetów każdej roli bez testu.')
h('Kolejność strojenia')
p('Najpierw dobierz obrażenia i liczbę akcji przeciwnika, potem HP, na końcu SP i zapasy na trasie. Samo zwiększanie HP wydłuża walkę, a samo zwiększanie obrażeń może powodować nokaut bez szansy na reakcję. Testuj osobno pierwsze spotkanie i walkę ze znanym przeciwnikiem.')

page('Katalog umiejętności P5R')
counts=collections.Counter(v['a'][1] for v in skills.values())
p(f'Katalog zawiera {len(skills)} unikalnych nazw z połączonych plików P5 i poprawek Royal: {len(skills)-counts["tra"]} umiejętności oraz {counts["tra"]} traitów. Obejmuje wpisy DLC i umiejętności towarzyszy obecne w tej bazie. Jest indeksem kosztów, nie pełnym opisem efektów ani listą mocy dostępnych do kupienia.')
p('Kompletność dotyczy wskazanej bazy. Wszystkie nazwy skilli z pobranych plików towarzyszy i zwykłych przeciwników Royal mają odpowiednik w katalogu. Osobne akcje fabularne, nawigacyjne i unikatowe komendy bossów, których baza nie zawiera, nie są objęte tym sprawdzeniem. Wpis nie oznacza dostępności dla własnej Persony.')
h('Jak czytać koszty')
p('Kolumna P5R jest odniesieniem do gry. Koszt procentowy HP z gry pozostaje procentowy tylko w tej kolumnie. Kolumna RPG podaje stałą liczbę HP lub SP. Zapis 0 oznacza brak kosztu aktywacji, a nie brak ograniczeń ani darmowe nauczenie się mocy. Traity są osobną kategorią, a nie kolejnymi aktywnymi skillami.')
p('U oznacza wcześniej ustalony koszt. P oznacza nową propozycję kosztu. A oznacza, że oprócz proponowanego kosztu konieczna jest adaptacja efektu. T oznacza trait o zerowym koszcie aktywacji, wymagający osobnego balansu. Znacznik A i T nie dopuszcza skilla do gry bez opisu działania.')
h('Reguły nowych propozycji kosztów')
p('Dla pozostałych skilli za SP stosujemy orientacyjnie koszt P5R podzielony przez 4, zaokrąglony w górę, minimum 1 SP. Wyjątki: standardowy heavy elemental pojedynczy cel 3 SP; standardowy heavy elemental obszar 6 SP. Pozostałe efekty szczególne zachowują znacznik A. To katalog propozycji, a nie potwierdzenie ich balansu.')
p('Dla nieustalonych skilli za procent HP proponujemy stały koszt równy połowie liczbowej wartości procentu, zaokrąglonej w górę: 10% HP → 5 HP. Zasada jest zakotwiczona w pulach około 60 HP. Headbutt 5 HP i Assault Dive 8 HP pozostają wyjątkami z dotychczasowych prób. Pasywne skille mają 0 kosztu aktywacji, lecz wymagają zasad efektu, limitu i zdobywania.')
p('Nie mnożymy automatycznie nowych efektów przez wartości z P5R. W szczególności multi hit, instakill, regeneracja, redukcja kosztów, procentowe premie i moce unikatowe wymagają opisu homebrew. Nie wszystkie odwołują się do istniejących już zasad.')
p('Źródło danych: aqiu384, megaten-fusion-tool, publiczna baza na licencji Unlicense. Odczyt 24 października 2026. Połączenie według nazwy: Royal nadpisuje wpis podstawowy; duplikaty techniczne tej samej nazwy są scalone. Receptury i dostępność skilli nie są częścią tej tabeli.')
p('https://github.com/aqiu384/megaten-fusion-tool/tree/master/src/app/p5/data')

labels={'phy':'Physical','gun':'Gun','fir':'Fire','ice':'Ice','ele':'Electricity','win':'Wind','psy':'Psy','nuk':'Nuclear','ble':'Bless','cur':'Curse','alm':'Almighty','ail':'Statusy','rec':'Leczenie','sup':'Wsparcie','pas':'Pasywne','tra':'Traity'}
targets={'1 foe':'1 wróg','All foes':'Wrogowie','1 ally':'1 sojusznik','All allies':'Drużyna','Self':'Własny','-':'Własny','Random foes':'Losowe cele','All':'Wszyscy','All foes and allies':'Wszyscy'}
fixed={'Frei':1,'Garu':1,'Zio':1,'Freila':2,'Agilao':2,'Garula':2,'Mafrei':3,'Headbutt':5,'Assault Dive':8,'Diarama':2,'Tarunda':2,'Rakukaja':2,'Cadenza':6}
elemental=set('fir ice ele win psy nuk ble cur'.split())
rowsout=[]
for elem,label in labels.items():
    page('Katalog '+label)
    rows=[]
    for name,v in sorted(skills.items(),key=lambda x:x[0].casefold()):
        if v['a'][1]!=elem:continue
        cost=v['b'][1];power=v['b'][2];multi=v['b'][4]>1
        target=v['a'][2];status='A'
        if elem in ['pas','tra'] or cost==0:
            orig='0';new='0';status='T' if elem=='tra' else 'A'
        elif cost>2000:
            orig=str(cost-2001)+' SP / tura';new=str(max(1,math.ceil((cost-2001)/4)))+' SP / tura'
        elif cost>1000:
            actual=cost-1000;orig=f'{actual} SP';n=max(1,math.ceil(actual/4))
            if elem in elemental and power==160 and not multi:n=6 if 'All' in target else 3
            if name in fixed:n=fixed[name];status='U'
            elif elem in elemental and power in [40,100,160] and not multi:status='P'
            new=f'{n} SP'
        else:
            orig=f'{cost}% HP';n=max(1,math.ceil(cost/2))
            if name in fixed:n=fixed[name];status='U'
            new=f'{n} HP'
        if name=='Cadenza':status='U'
        row=[name,targets.get(target,target),orig,new,status]
        rows.append(row);rowsout.append([name,label,target,orig,new,status])
    table(['Umiejętność','Cel P5R','Koszt P5R','Koszt RPG','Status'],rows,[5.4,3.3,3,3.8,1.9])

out=R/'Persona_5_RPG_Zasady_0_2.docx';doc.save(out)
with (R/'skill_catalog_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['name','type','target','p5r_cost','rpg_cost','status']);w.writerows(rowsout)
assert len(rowsout)==len(skills)==541
check=Document(out)
assert len(check.tables)==24
for name,c in [('Agilao','2 SP'),('Cadenza','6 SP'),('Headbutt','5 HP'),('Assault Dive','8 HP')]:
    assert next(r for r in rowsout if r[0]==name)[4]==c
print(f'OK {out} | skills={len(rowsout)} | tables={len(check.tables)}')
