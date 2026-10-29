from pathlib import Path
from copy import deepcopy
import json,math,csv
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

R=Path(__file__).parent;path=R/'Persona_5_RPG_Zasady_0_2.docx'
doc=Document(path)
assert not any(p.text=='Nakładanie statusów' for p in doc.paragraphs)
skills={}
for file in ['p5_base_skill_data.json','p5r_skill_data.json']:
    for v in json.loads((R/file).read_text(encoding='utf-8-sig')).values():skills[v['a'][0]]=v
status_pl={'Burn':'Podpalenie','Freeze':'Zamrożenie','Shock':'Porażenie','Dizzy':'Zawroty głowy','Forget':'Zapomnienie','Sleep':'Sen','Confuse':'Dezorientacja','Fear':'Strach','Despair':'Rozpacz','Rage':'Szał','Brainwash':'Pranie mózgu','Hunger':'Głód'}

def p(t):return doc.add_paragraph(t)
def h(t):doc.add_heading(t,2)
def page(t):doc.add_page_break();doc.add_heading(t,1)
def format_table(t,widths):
    t.autofit=False
    for col,w in zip(t.columns,widths):col.width=Cm(w)
    for ri,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr()
        if pr.find(qn('w:cantSplit')) is None:pr.append(OxmlElement('w:cantSplit'))
        for ci,c in enumerate(row.cells):
            c.width=Cm(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=c._tc.get_or_add_tcPr()
            for old in list(cp.findall(qn('w:tcBorders'))):cp.remove(old)
            b=OxmlElement('w:tcBorders')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
            cp.append(b)
            for old in list(cp.findall(qn('w:shd'))):cp.remove(old)
            sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'333333' if ri==0 else ('F2F2F2' if ri%2 else 'FFFFFF'));cp.append(sh)
            for par in c.paragraphs:
                par.paragraph_format.space_after=Pt(3);par.paragraph_format.line_spacing=1
                for run in par.runs:
                    run.font.size=Pt(9)
                    if ri==0:run.bold=True;run.font.color.rgb=RGBColor(255,255,255)
def table(head,rows,widths):
    t=doc.add_table(rows=1,cols=len(head))
    for i,x in enumerate(head):t.rows[0].cells[i].text=x
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for row in rows:
        cs=t.add_row().cells
        for i,x in enumerate(row):cs[i].text=str(x)
    format_table(t,widths);p('');return t

# Build the new chapter at the end, then move it before the basic skill list.
body=doc.element.body;old_nodes=set(body)
page('Nakładanie statusów')
p('Propozycja zasad do testów przy stole. Wprowadzamy wszystkie 12 zwykłych dolegliwości z P5R oraz osobno stany specjalne. Efekty i czas działania poniżej są naszym homebrew. Zastępują pomijanie statusów w dawnych próbach walki; nie przeliczają wstecz wyników tych prób.')
h('Jeden rzut obronny')
p('Cel rzuca d20 bez premii za poziom. Wynik równy DC lub wyższy oznacza obronę; niższy oznacza otrzymanie statusu. Naturalne 1 i 20 nie mają osobnych efektów. Dotyczy to bohaterów i Shadows. Nie dodajemy na tym etapie Luck ani Endurance.')
table(['Szansa otrzymania','DC obrony','Status przy wyniku'],[
('Niska 25%','6','1–5'),('Średnia 50%','11','1–10'),('Wysoka 70%','15','1–14'),('Bardzo wysoka 90%','19','1–18')
],[6.2,3,8.2])
p('Gdy znany jest procent P5R, możemy go zachować dokładniej: DC = 1 + procent / 5, z liczbą przypadków zaokrągloną do najbliższej całości. Np. 20% → DC 5; 35% → DC 8; 40% → DC 9. W katalogu skilli dopisano dokładne DC zamiast zastępować wszystkie szanse trzema kategoriami. Dla autorskiego skilla wystarczą kategorie powyżej.')
h('Dwa rodzaje działania')
p('Atak z obrażeniami: zapłać koszt, wykonaj rzut trafienia i rozlicz obrażenia. Jeżeli cel nadal ma HP i stracił co najmniej 1 HP, wykonuje rzut obronny przeciw dodatkowej dolegliwości. Pudło, Null, Drain i Repel nie nakładają dolegliwości na pierwotny cel. W prototypie odbity atak nie przenosi statusu na atakującego; jest to jawne uproszczenie.')
p('Czysty skill statusowy, np. Dormina: zapłać koszt, a cel wykonuje tylko rzut obronny. Nie robimy dodatkowego rzutu trafienia przeciw Obronie. Skille obszarowe wymagają jednego rzutu obronnego od każdego celu. Przy multi hit wykonujemy najwyżej jeden rzut na dany status od danego celu w całej akcji, nie po każdym trafieniu.')
p('Sam typ Fire, Ice lub Electricity nie oznacza automatycznie szansy na status. Efekt musi być zapisany na skillu lub przedmiocie. Agi, Bufu i Zio mają odpowiednio Burn, Freeze i Shock przy DC 6. Rzadkość skilla ani siła light/medium/heavy same nie podnoszą DC.')

page('Czas działania i ochrona przed blokowaniem')
h('Zwykłe tury zamiast dodatkowych akcji')
p('Czas statusu liczymy w kolejnych zwykłych turach jego celu, nie w rundach całej walki. Status na jedną turę obejmuje następną zwykłą turę celu i kończy się na jej końcu. Dodatkowe akcje One More/Baton Pass nie skracają licznika, nie uruchamiają kolejnych obrażeń Burn ani regeneracji Sleep. Jeżeli status pojawi się podczas własnej tury celu, nie liczymy tej rozpoczętej tury.')
p('Na początku tury usuń Down, następnie sprawdź statusy. Ograniczenie działa również na dodatkowe akcje: postaci bez możliwości działania nie można przekazać Baton Pass. Przy efekcie aktywnym tylko podczas tej jednej akcji, np. Strachu, najpierw ustal możliwość działania. Jeżeli akcja jest dostępna, można ją wykorzystać zgodnie z pozostałymi ograniczeniami.')
h('Powrót do działania')
p('Po zakończeniu Freeze, Shock, Sleep, Confuse, Fear lub Brainwash cel otrzymuje ochronę przed tymi sześcioma statusami do końca swojej następnej zwykłej tury. Dotyczy to również wcześniejszego wyleczenia lub wybudzenia. Ochrona nie usuwa innych statusów, nie blokuje obrażeń, Down ani nokautu. Nie jest odpornością na żywioł. Zapisz krótko: ochrona do końca następnej tury.')
p('Przykład: Sleep odbiera turę 2 i kończy się na jej końcu. Do końca tury 3 cel nie może dostać żadnego z sześciu statusów blokujących. Ponowna Dormina może zadziałać po zakończeniu tury 3. Reguła działa tak samo na wrogach, zapobiegając nieskończonemu blokowaniu minibossa.')
h('Nakładanie i usuwanie')
p('Ta sama dolegliwość nie kumuluje się ani nie odnawia czasu, gdy już trwa. Nie wykonuj kolejnego rzutu na tę samą dolegliwość. Różne statusy mogą współistnieć i mają osobne liczniki. W pierwszych sesjach zalecamy wrogów nakładających jeden rodzaj dolegliwości, żeby ograniczyć liczbę znaczników.')
p('Bezpośrednie trafienie usuwa status tylko wtedy, gdy tabela tak mówi i cel traci co najmniej 1 HP. Obrażenia okresowe, koszt HP skilla, obniżenie SP i utrata HP z innego statusu nie są takim trafieniem. Usunięcie dolegliwości następuje po rozliczeniu całej akcji; multi hit nie daje dodatkowych okien statusu. Zwykłe leczenie HP ani safe room same nie zdejmują dolegliwości.')
p('Po zakończeniu walki usuń wszystkie 12 zwykłych dolegliwości i ich liczniki, ale nie odzyskuj straconych HP/SP. Znikają też czasowe premie, kary i ochrona przed blokowaniem. Nokaut pozostaje według zasad wskrzeszania. Stany fabularne kończą się według opisu sceny.')

page('Statusy żywiołowe')
table(['Status','Efekt RPG','Naturalny koniec','Wcześniejsze usunięcie'],[
('Burn\nPodpalenie','Na końcu zwykłej tury tracisz 3 HP. Może spowodować nokaut. Brak dodatkowych ticków z One More.','Po 3 kolejnych zwykłych turach; maksymalnie 9 HP z jednego nałożenia.','Baisudi/Amrita lub odpowiedni przedmiot. Własna akcja Ugaś płomienie usuwa Burn bez SP i bez rzutu.'),
('Freeze\nZamrożenie','Nie możesz działać ani przyjąć Baton Pass. W RPG samo Freeze nie zmienia odporności Physical/Gun.','Na końcu następnej zwykłej tury, nawet gdy nie możesz w niej działać.','Baisudi/Amrita, odpowiedni przedmiot albo bezpośrednie Physical/Gun z utratą HP. Potem ochrona przed blokowaniem.'),
('Shock\nPorażenie','Nie możesz działać ani przyjąć Baton Pass. Trafiający cię wręcz atakujący może dostać Shock: jeden rzut obronny DC 6 po akcji.','Na końcu następnej zwykłej tury.','Baisudi/Amrita lub odpowiedni przedmiot. Samo trafienie nie usuwa Shock. Potem ochrona przed blokowaniem.')
],[2.9,6.3,3.4,4.8])
p('Rozprzestrzenianie Shock dotyczy wyłącznie kontaktu wręcz, w tym kontaktowego skilla Physical. Nie dotyczy Gun, zaklęć ani leczenia. Wymaga co najmniej jednego trafienia z utratą HP i żyjącego, nadal porażonego celu na końcu akcji. Nie uruchamia kolejnego łańcucha transmisji ani One More. Ochrona przed blokowaniem i Null Shock normalnie je zatrzymują.')
h('Odporność na żywioł a odporność na status')
p('Resist Fire zmniejsza obrażenia Fire, ale nie daje automatycznie premii przeciw Burn. To samo dotyczy Ice/Freeze i Electricity/Shock. Null, Drain i Repel żywiołu zapobiegają dodatkowej dolegliwości z danego ataku, bo pierwotny cel nie traci HP. Osobna cecha Null Burn/Freeze/Shock chroni również przed czystą dolegliwością lub transmisją.')
p('Warianty Person mogą mieć ukryte odporności na status w P5R. Do naszego RPG wpisujemy je jawnie na kartę; sama nazwa Persony nie przyznaje takiej odporności.')

page('Sen dezorientacja i ograniczenia działania')
table(['Status','Efekt RPG','Koniec i usunięcie'],[
('Dizzy\nZawroty głowy','Kara −4 do rzutów trafienia. Obrona, leczenie i rzuty obronne przeciw statusom pozostają bez zmian.','Po 2 zwykłych turach; wcześniej bezpośrednie trafienie z utratą HP, Patra/Amrita lub przedmiot.'),
('Forget\nZapomnienie','Nie możesz używać skilli aktywnych, zarówno za SP, jak i HP. Możesz zwyczajnie atakować, używać przedmiotów i korzystać z pasywów.','Po 2 zwykłych turach; wcześniej trafienie z utratą HP, Patra/Amrita lub przedmiot.'),
('Sleep\nSen','Nie możesz działać. Jeśli nadal śpisz na końcu objętej statusem tury, odzyskujesz 5 HP i 2 SP, do maksimum.','Na końcu następnej zwykłej tury, po regeneracji; wcześniej dowolne bezpośrednie trafienie z utratą HP, Patra/Amrita, przedmiot lub akcja sojusznika Obudź. Potem ochrona.'),
('Confuse\nDezorientacja','Tracisz możliwość działania w następnej zwykłej turze. Nie wyrzucasz pieniędzy ani przedmiotów; to uproszczenie względem P5R.','Na końcu następnej zwykłej tury; wcześniej trafienie z utratą HP, Energy Drop/Amrita, przedmiot lub akcja sojusznika Otrzeźwij. Potem ochrona.'),
('Fear\nStrach','Na początku najbliższej zwykłej tury rzuć d20: 11+ pozwala działać, 1–10 oznacza utratę działania. Nie uciekasz automatycznie z walki.','Na końcu tej jednej zwykłej tury niezależnie od wyniku. Wcześniej Energy Drop/Amrita lub przedmiot. Potem ochrona.'),
('Brainwash\nPranie mózgu','W następnej zwykłej turze wykonujesz jeden darmowy zwykły atak przeciw przytomnemu sojusznikowi. Gdy jest ich kilku, cel wybierz losowo. Gdy nie ma żadnego, tracisz działanie. Bez wydawania SP lub przedmiotów.','Na końcu następnej zwykłej tury; wcześniej Energy Drop/Amrita lub przedmiot. Potem ochrona.')
],[3,7.1,7.3])
p('Obudź i Otrzeźwij to jedna akcja przytomnego sojusznika, bez SP i rzutu, wymagająca możliwości dotarcia do celu. Nie przywraca zużytej tury. Brainwash nie daje One More ani krytyka za wymuszony atak; wybór działania i wydatki postaci nie przechodzą swobodnie pod kontrolę GM.')

page('Szał głód i rozpacz')
table(['Status','Efekt RPG','Koniec i usunięcie'],[
('Rage\nSzał','W swojej turze i każdej dodatkowej akcji możesz wyłącznie wykonać darmowy zwykły atak w przytomnego wroga. Zadajesz +4 obrażenia, ale otrzymujesz +4 obrażenia z trafień. Nie używasz skilli, przedmiotów ani wsparcia.','Po 2 zwykłych turach. Wcześniej Energy Drop/Amrita lub odpowiedni przedmiot użyty przez sojusznika.'),
('Hunger\nGłód','Zadawane przez twoje ataki obrażenia spadają o połowę, w dół. Nie zmniejsza leczenia ani wartości odnawianych przez przedmioty. Nie zmienia maksymalnego HP/SP.','Po 3 zwykłych turach. Wcześniej Patra/Amrita albo jedzenie/przedmiot z wyraźnym efektem usuwającym Hunger.'),
('Despair\nRozpacz','Możesz wykonywać zwykłą akcję, ale nie otrzymujesz ani nie wykorzystujesz One More/Baton Pass. Na końcu każdej zwykłej tury tracisz 2 SP, minimum 0. Po trzecim takim rozliczeniu spadasz do 0 HP.','Brak naturalnego wyleczenia przed konsekwencją trzeciej tury. Usuwa Energy Drop/Amrita lub przedmiot. Możesz w swojej akcji użyć odpowiedniego środka na sobie; wtedy końcowy ubytek i nokaut nie następują.')
],[3,7.1,7.3])
p('Despair jest świadomie łagodniejsze od blokującej akcje wersji gry komputerowej: pozostawia możliwość samoratunku, ale nadal wymaga reakcji przed trzecią turą. Nokaut nie oznacza automatycznej śmierci fabularnej. Nie odbieramy SP, których postać już nie ma.')
p('Kolejność obrażeń: rzut i stałe premie/kary → Hunger, jeśli działa → Weak/Resist. Zaokrąglaj w dół po mnożniku, minimum 0. Burn, koszt HP skilla i utrata SP przez Despair nie są atakami, więc Hunger i Rage ich nie modyfikują. Przy jednoczesnych ograniczeniach stosuj wszystkie: np. Rage z Forget nadal pozwala na zwykły atak, ale Sleep z Rage nie pozwala działać.')
h('Resist Null i premie do szans')
p('Resist konkretnej dolegliwości daje +4 do rzutu obronnego; Null daje pełną odporność i usuwa potrzebę rzutu. Nie wymyślamy odporności wszystkim minibossom: zapisuj ją osobno na karcie i informuj gracza, gdy ją odkryje.')
p('Propozycja do pasywów: odpowiedni statusowy Boost lub Ailment Boost zwiększa DC o 2. Wybierz tylko jedną taką premię, bez kumulacji. Fire Boost zwiększający obrażenia nie jest Burn Boost. Pozostałe traity i skille manipulujące szansą wymagają osobnego opisu; nie mnożymy automatycznie procentów z P5R. DC losowego efektu ograniczamy do 20; gwarantowany status fabularny wymaga jawnego wyjątku na karcie.')

page('Leczenie statusów i stany specjalne')
table(['Skill','Usuwane zwykłe statusy','Cel','Koszt RPG'],[
('Baisudi','Burn Freeze Shock','1 sojusznik','1 SP'),('Mabaisudi','Burn Freeze Shock','Drużyna','2 SP'),
('Patra','Dizzy Forget Sleep Hunger','1 sojusznik','1 SP'),('Me Patra','Dizzy Forget Sleep Hunger','Drużyna','2 SP'),
('Energy Drop','Confuse Fear Despair Rage Brainwash','1 sojusznik','1 SP'),('Energy Shower','Confuse Fear Despair Rage Brainwash','Drużyna','2 SP'),
('Amrita Drop','Wszystkie 12 zwykłych dolegliwości','1 sojusznik','2 SP'),('Amrita Shower','Wszystkie 12 zwykłych dolegliwości','Drużyna','3 SP')
],[3.2,7,3.2,4])
p('To propozycje kosztów zgodne z dotychczasowym przeliczeniem katalogu. Wyleczenie nie wymaga rzutu, ale kosztuje akcję i SP. Usuwa wszystkie pasujące dolegliwości z danego celu. Nie leczy HP i nie wskrzesza. Samodzielne użycie jest możliwe tylko wtedy, gdy postać może działać i używać skilli.')
table(['Stan','Zasada RPG','Zakończenie'],[
('Down\nPowalenie','Według dotychczasowego One More. To osobny stan, nie jedna z 12 dolegliwości.','Na początku zwykłej tury. Nie usuwa go Amrita.'),
('KO\nNokaut','0 HP; brak działania.','Przedmiot lub skill wskrzeszający. Amrita i zwykłe leczenie nie wystarczą.'),
('Rat\nPrzemiana w szczura','Propozycja do scen specjalnych: brak skilli i ataków bronią; można użyć przedmiotu lub słabego zwykłego ataku za stałe 2 Physical po trafieniu. Otrzymywane obrażenia +4.','Po 2 zwykłych turach lub usunięciu źródła według sceny. Amrita nie działa.'),
('Paint\nZamalowanie','Propozycja do scen specjalnych: wszystkie 10 typów poza Almighty traktuj jako Weak, również zamiast zwykłego Null/Repel/Drain. Nie daje dodatkowego mnożnika na istniejącą słabość.','Po 2 zwykłych turach lub rozwiązaniu mechaniki sceny. Amrita nie działa.')
],[3.2,9.6,4.6])
p('Buffy i debuffy, np. Tarukaja/Tarunda, nie są dolegliwościami: leczą je inne zdolności. Rat i Paint nie wchodzą domyślnie do zwykłych skilli ani losowych spotkań. Jeśli skill ich nie ma, nie nadajemy ich z samego typu obrażeń. Dla nowego źródła wybierz jawne DC z tabeli, domyślnie średnie DC 11; mechanika sceny może zamiast rzutu wymagać uniknięcia pułapki.')

page('Przykłady działania statusów')
h('Agilao i Burn')
p('Orpheus płaci 2 SP za Agilao i trafia. Shadow otrzymuje obrażenia Fire. Ma co najmniej 1 HP, więc rzuca d20 przeciw DC 6. Wynik 4 oznacza Burn. Na końcu każdej z trzech następnych zwykłych tur straci 3 HP, jeśli wcześniej się nie ugasi. One More z trafienia w słabość nie daje dodatkowego testu Burn w tej samej akcji; osobne dodatkowe Agilao jest już nową akcją.')
h('Dormina i Sleep')
p('Sandman używa Dorminy za 1 SP. Nie rzuca na trafienie. Bohater rzuca obronę DC 15; wynik 10 oznacza Sleep. Kompan może poświęcić akcję na Obudź lub użyć Patry. Jeśli nikt tego nie zrobi i nie nastąpi trafienie z utratą HP, bohater traci działanie w swojej następnej zwykłej turze, odzyskuje na jej końcu 5 HP i 2 SP, po czym Sleep znika. Do końca kolejnej zwykłej tury jest chroniony przed sześcioma statusami blokującymi.')
h('Headbutt i Forget')
p('Kidd płaci 5 HP i trafia Headbutt. Po rozliczeniu medium Physical cel rzuca obronę DC 8, odpowiadającą źródłowym 35%. Przy wyniku 7 otrzymuje Forget na dwie zwykłe tury. Kolejne bezpośrednie trafienie z utratą HP może usunąć Forget wcześniej.')
h('Despair i własny przedmiot')
p('Bohater otrzymał Despair i dwukrotnie stracił po 2 SP. W swojej trzeciej zwykłej turze używa przedmiotu usuwającego Despair. Status znika przed końcem tury: nie dochodzi do trzeciej utraty ani nokautu. Wsparcie sojusznika działa tak samo, jeśli zdąży przed rozliczeniem trzeciej tury celu.')
h('Zakres dalszych testów')
p('Nakładanie statusu samo nie daje One More. Technical i jego dodatkowe obrażenia pozostają osobnym, jeszcze nieaktywnym modułem. Nie uznajemy więc automatycznie Garu przeciw Burn ani Nuclear przeciw Freeze za słabość. Wszystkie przedstawione czasy i stałe liczby są propozycją do testu walk solo oraz drużynowych, nie odtworzeniem wzorów komputerowych P5R.')
h('Źródła odniesienia P5R')
p('Lista dolegliwości i ich ogólne role: tekst samouczka P5R, https://mysh.dev/tools/persona/5r/view?file=%5CdataR.cpk%5Ctutorial%5CscriptTutorial_battle_022.bf .')
p('Mechaniki i zależności: https://aqiu384.github.io/megaten-database/p5r/metaverse oraz https://wikiwiki.jp/persona5r/状態異常 . Konkretne szanse skilli: lokalna baza aqiu384 megaten-fusion-tool, dane Royal nadpisujące P5. Wartości i ograniczenia homebrew w tym rozdziale są autorską propozycją.')

new_nodes=[n for n in body if n not in old_nodes and n.tag!=qn('w:sectPr')]
anchor=next(par for par in doc.paragraphs if par.text=='Koszty i katalog umiejętności')._p
previous=anchor.getprevious()
if previous is not None and previous.find('.//'+qn('w:br')) is not None:anchor=previous
for node in new_nodes:body.remove(node);anchor.addprevious(node)

# Update statements made obsolete by the new module, keeping historical test notes.
for par in doc.paragraphs:
    text=par.text
    if text.startswith('Zestaw zasad do wspólnej gry'):
        par.text=text.replace('rozwój postaci, statusy i życie codzienne','rozwój postaci i życie codzienne')
    elif text.startswith('Nie ustaliliśmy uniwersalnych kosztów'):
        par.text='Koszty i działanie podstawowych statusów oraz ich leczenia opisuje rozdział Nakładanie statusów. Pozostałe moce unikatowe, wskrzeszanie i skille obszarowe wymagają osobnych testów. Nie przenosimy automatycznie kosztów z gry.'
    elif text.startswith('Odnawianie HP/SP jest gotowe do prób.'):
        par.text=text.replace('Odnawianie HP/SP jest gotowe do prób.','Odnawianie HP/SP i usuwanie opisanych zwykłych statusów są gotowe do prób.')
    elif text.startswith('Wersja 0.2'):
        par.text='Wersja 0.2 • aktualizacja 28 października 2026 • moduł statusów'

for t in doc.tables:
    if [c.text for c in t.rows[0].cells]==['Umiejętność','Cel i efekt','Koszt']:
        for row in t.rows[1:]:
            if row.cells[0].text=='Headbutt':row.cells[1].text='Jeden cel; medium Physical oraz Forget przy nieudanej obronie DC 8.'

# Annotate status probabilities directly in all skill catalogue tables.
annotations=[]
for t in list(doc.tables):
    if [c.text for c in t.rows[0].cells]!=['Umiejętność','Cel P5R','Koszt P5R','Koszt RPG','Status']:continue
    t.add_column(Cm(4.9));t.rows[0].cells[4].text='Adaptacja';t.rows[0].cells[5].text='Dolegliwość i DC'
    for row in t.rows[1:]:
        name=row.cells[0].text;v=skills.get(name);ann='—'
        if v and v['a'][1] not in ['pas','tra'] and v['c'][0] in status_pl and v['c'][1]=='FMTExact':
            pct=v['b'][7]
            if pct>0:
                dc=1+int(math.floor(float(pct)/5+.5));ann=f'{v["c"][0]}: DC {min(dc,20)} ({pct}% P5R)'
                annotations.append((name,v['c'][0],pct,min(dc,20)))
        row.cells[5].text=ann
    format_table(t,[4.2,2.5,2.2,2.2,1.4,4.9])

# Clarify references in the item glossary that formerly awaited status definitions.
for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            if c.text=='Przedmiot usuwa Hunger; szczegółowe działanie statusu pozostaje do projektu.':c.text='Przedmiot usuwa Hunger zgodnie z rozdziałem statusów.'
            if c.text=='Usuwa zwykłe negatywne statusy po opracowaniu ich zasad; nie usuwa Down, nokautu ani efektu fabularnego.':c.text='Usuwa wszystkie opisane zwykłe dolegliwości; nie usuwa Down, nokautu, Rat, Paint ani efektu fabularnego.'

backup=R/'Persona_5_RPG_Zasady_0_2_przed_statusami.docx'
if not backup.exists():backup.write_bytes(path.read_bytes())
doc.save(path)
with (R/'status_chances_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['skill','ailment','p5r_chance','rpg_DC']);w.writerows(annotations)
check=Document(path)
assert any(p.text=='Nakładanie statusów' for p in check.paragraphs)
assert len(next(t for t in check.tables if t.rows[0].cells[0].text=='Poziom').rows)==100
catalog=[t for t in check.tables if t.rows[0].cells[0].text=='Umiejętność' and len(t.columns)==6]
assert len(catalog)==16 and sum(len(t.rows)-1 for t in catalog)==541
assert sum(len(t.rows)-1 for t in check.tables[-4:])==157
for name,dc in [('Agi',6),('Bufu',6),('Zio',6),('Headbutt',8),('Dormina',15),('Phantom Show',19)]:
    assert next(row for row in annotations if row[0]==name)[3]==dc
print('OK: 12 ailments + 4 special states; annotations',len(annotations),'skills; 541 catalogue entries and 157 items retained')
