from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT = Path(__file__).parent
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(1.7)
sec.left_margin = sec.right_margin = Cm(1.8)
for name in ['Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2']:
    st = doc.styles[name]
    st.font.name = 'Calibri'
    st.font.color.rgb = RGBColor(0,0,0)
doc.styles['Normal'].font.size = Pt(10.5)
doc.styles['Normal'].paragraph_format.space_after = Pt(6)
doc.styles['Normal'].paragraph_format.line_spacing = 1.08
doc.styles['Title'].font.size = Pt(25)
doc.styles['Heading 1'].font.size = Pt(18)
doc.styles['Heading 2'].font.size = Pt(12)
doc.core_properties.title = 'Persona 5 RPG Zasady podstawowe'
doc.core_properties.author = 'Projekt Persona 5 RPG'

def p(text, style=None):
    return doc.add_paragraph(text, style)
def h(text):
    doc.add_heading(text, 2)
def page(title):
    doc.add_page_break()
    doc.add_heading(title, 1)
def table(headers, rows, widths):
    t=doc.add_table(rows=1, cols=len(headers))
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.autofit=False
    for col,w in zip(t.columns,widths): col.width=Cm(w)
    for i,v in enumerate(headers):t.rows[0].cells[i].text=v
    rep=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(rep)
    for row in rows:
        cells=t.add_row().cells
        for i,v in enumerate(row):cells[i].text=str(v)
    for ri,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
        for ci,c in enumerate(row.cells):
            c.width=Cm(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=c._tc.get_or_add_tcPr()
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
            cp.append(borders)
            margins=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                el=OxmlElement('w:'+side);el.set(qn('w:w'),'85');el.set(qn('w:type'),'dxa');margins.append(el)
            cp.append(margins)
            sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'333333' if ri==0 else ('F2F2F2' if ri%2 else 'FFFFFF'));cp.append(sh)
            for par in c.paragraphs:
                par.paragraph_format.space_after=Pt(2)
                par.paragraph_format.line_spacing=1.0
                if ci==0 and len(headers)>2:par.alignment=WD_ALIGN_PARAGRAPH.LEFT
                for run in par.runs:
                    run.font.size=Pt(9.5)
                    if ri==0:run.bold=True;run.font.color.rgb=RGBColor(255,255,255)
    p('')
    return t

doc.add_heading('Persona 5 RPG',0)
p('Zasady podstawowe', 'Subtitle')
p('Wersja 0.1 • 24 października 2026')
p('Zestaw zasad do wspólnej gry prowadzonej przez GM. Dokument porządkuje dotychczasowe ustalenia i wartości z prób walki. Pozwala rozegrać prostą potyczkę; rozwój postaci, statusy i życie codzienne będziemy dopracowywać osobno.')
h('Jak czytać dokument')
p('Ustalenie oznacza przyjęty kierunek projektu. Wartość testowa obowiązuje podczas prób wersji 0.1, ale może się zmienić. Doprecyzowanie oznacza nowy zapis porządkujący wcześniejsze przykłady. Brak liczby oznacza, że mechanika nie została jeszcze ustalona.')
h('Najważniejsze założenia')
p('Jedna własna Persona, maksymalnie osiem umiejętności, HP i SP oraz niewielka liczba kości. Bez części ciała z osobnym HP, talii tarota i toru zmęczenia. Eksploracja Pałacu przeplata się ze śledztwem i codziennością. Powrót do rzeczywistości wynika przede wszystkim z fabuły.')
h('Podstawowe definicje')
table(['Pojęcie','Znaczenie'],[
('GM','Osoba prowadząca świat, NPC, Shadows i rozstrzygająca sytuacje przy stole.'),
('Persona','Moc bohatera określająca jego umiejętności i właściwości żywiołowe.'),
('Shadow','Przeciwnik. Jego karta może różnić się od karty Persony o tej samej nazwie.'),
('HP','Wytrzymałość. Obrażenia ją obniżają, leczenie przywraca.'),
('SP','Zasób wydawany na magię, leczenie i część wsparcia.'),
('d20 i d6','Jedna kość dwudziestościenna i jedna sześciościenna. 2d6 oznacza sumę dwóch d6.'),
('Runda i tura','Runda obejmuje zwykłe tury uczestników; tura to moment działania jednej postaci.')
],[3.2,14.2])

page('Walka krok po kroku')
h('Parametry do rozpoczęcia prób')
table(['Parametr','Bohater','Zwykły Shadow','Miniboss'],[
('Maksymalne HP','60','28 do 36','140'),('Maksymalne SP','56','Według karty','Według karty'),('Premia ataku','+5','+4','+4'),('Obrona','12','12','13')],[5,4.1,4.1,4.2])
p('Wszystkie liczby w tabeli są wartościami testowymi. 60 HP i 56 SP służą porównywaniu bohaterów w próbach około poziomu 26. Nie są statystykami postaci początkującej ani wynikiem przeliczenia cech z P5R. Zakresy Shadows nie są automatycznym generatorem przeciwników.')
h('Kolejność i akcje')
p('1. Ustal kolejność bohaterów przed walką. W obecnym teście najpierw działają bohaterowie, potem żyjący przeciwnicy. Inicjatywa i zasadzki nie mają jeszcze osobnych zasad.')
p('2. Na początku tury usuń Down tej postaci. Postać ma jedną zwykłą akcję: atak, skill, użycie przedmiotu albo przekazanie działania bez efektu. Dodatkowa akcja nie zastępuje zwykłej tury kompana.')
p('3. Wybierz umiejętność i cel. Zapłać koszt przed rzutem. Koszt przepada także przy pudle, Null, odbiciu lub absorpcji. Nie można wydać SP poniżej zera. Doprecyzowanie: koszt HP musi pozostawić co najmniej 1 HP.')
p('4. Rzuć d20 i dodaj premię ataku. Wynik równy Obronie lub wyższy trafia. Pudło nie ujawnia właściwości celu. W testach naturalne 1 i 20 nie mają specjalnych efektów; nie rozpatrujemy krytyków.')
p('5. Przy trafieniu rzuć obrażenia, zastosuj właściwość celu i odejmij HP. Sprawdź możliwość One More. Następnie przejdź do kolejnej akcji lub tury.')
h('Leczenie i wsparcie')
p('Leczenie i dobrowolne wsparcie sojusznika nie wymagają rzutu trafienia. Tarunda w obecnym prototypie również działa bez rzutu. Przywracane HP/SP nie mogą przekroczyć maksimum. Wsparcie nie kumuluje się samo ze sobą; ponowienie odnawia czas działania. To doprecyzowanie wersji 0.1.')
h('Nokaut')
p('Doprecyzowanie do prób: przy 0 HP postać jest nieprzytomna i nie działa; zwykłe leczenie nie wskrzesza. W testach balansu pierwszy nokaut kończy próbę jako niepowodzenie. Nie oznacza to automatycznej śmierci postaci ani końca kampanii. Wskrzeszanie, wycofanie i konsekwencje porażki wymagają osobnych zasad.')

page('Obrażenia i właściwości')
h('Wspólna skala obrażeń')
table(['Siła','Rzut','Średnia bez modyfikacji'],[
('Light','1d6 + 4','7,5'),('Medium','2d6 + 6','13'),('Heavy','3d6 + 8','18,5')],[4.2,5,8.2])
p('Skala obowiązuje w testach zarówno bohaterów, jak i przeciwników. Heavy jest propozycją z próby Zorro i Captain Kidda. Severe, Colossal, Almighty o specjalnej sile oraz wielokrotne trafienia nie mają jeszcze ogólnej skali. Nie dodajemy osobno Strength ani Magic do tych rzutów.')
h('Właściwość celu wobec danego typu ataku')
table(['Właściwość','Efekt'],[
('Normal','Pełne obrażenia.'),('Weak','Obrażenia ×1,5, zaokrąglone w dół. Trafienie stojącego celu powoduje Down i One More.'),('Resist','Połowa obrażeń, zaokrąglona w dół.'),('Null','Zero obrażeń. Nie powoduje Down ani One More.'),('Drain','Propozycja: zamiast obrażeń cel odzyskuje tyle HP, ile atak zadałby przy Normal.'),('Repel','Propozycja: obrażenia wracają do atakującego. W próbach 0.1 nie używamy odbijających wrogów; dalsze interakcje wymagają testu.')
],[3.2,14.2])
p('Dla pojedynczego typu stosujemy jedną właściwość z karty. Domyślnie brak wpisu oznacza Normal. Obsługiwane typy: Physical, Gun, Fire, Ice, Electricity, Wind, Psy, Nuclear, Bless, Curse i Almighty. Specjalne wyjątki muszą znaleźć się na karcie.')
h('Przykład')
p('Agilao wyrzuca 3 i 4 na 2d6. Wynik to 3 + 4 + 6 = 13. Przy Weak cel otrzymuje 19 obrażeń; przy Resist 6; przy Null 0. Po udanym trafieniu zapisujemy zaobserwowaną właściwość.')
h('Bestiariusz gracza')
p('Zapisujemy odkryte właściwości i zaobserwowane skille. Wiedza pozostaje na kolejne spotkania z tym samym typem Shadow. Neutralność Fire nie ujawnia innych odporności ani nie dowodzi braku słabości. Nietypowy wariant powinien mieć dostrzegalne wyróżnienie. Gracz nie poznaje całej karty GM po jednym trafieniu.')

page('One More i Baton Pass')
h('Down')
p('Trafienie w słabość przewraca stojący cel. Down trwa do początku jego następnej zwykłej tury; wtedy cel wstaje i może normalnie działać. W tej wersji Down nie zabiera tury, nie zmniejsza Obrony i nie daje premii do obrażeń. Trafienie już przewróconego celu nadal korzysta z mnożnika Weak, ale nie daje kolejnego One More.')
h('One More')
p('Przewrócenie stojącego przeciwnika daje natychmiast jedną dodatkową akcję. Można ją wykorzystać na atak, leczenie, wsparcie lub przedmiot, przekazać przez Baton Pass albo z niej zrezygnować. Koszt wybranego skilla pozostaje normalny. Dobicie przeciwnika bez trafienia w słabość nie daje One More.')
h('Łańcuch dodatkowych akcji')
p('Doprecyzowanie porządkujące przykłady: postać może wykonać najwyżej jedną dodatkową akcję w łańcuchu rozpoczętym przez daną zwykłą akcję. Zwykła akcja rozpoczynająca łańcuch nie zużywa tego limitu. Jeżeli dodatkowa akcja przewróci kolejny cel, następna akcja może trafić wyłącznie do sojusznika, który nie wykonał jeszcze dodatkowej akcji w tym łańcuchu. To zabezpiecza przed nieskończonym odbijaniem działań.')
p('Przy ataku obszarowym przyznajemy najwyżej jedną dodatkową akcję za całą akcję, nawet jeśli przewrócono kilka celów. Jest to nowa propozycja do testów obszarowych, a nie mechanika sprawdzona w dotychczasowych symulacjach.')
h('Baton Pass')
p('Zamiast wykonać dodatkową akcję samodzielnie, oddaj ją przytomnemu kompanowi. Kompan działa natychmiast i zachowuje swoją zwykłą turę. Samo przekazanie nie kosztuje zasobów. Na razie nie zwiększa obrażeń i nie regeneruje HP/SP. Nie ma obowiązku przekazywania ani wykorzystywania akcji.')
h('Przykład dwóch bohaterów')
p('Orpheus trafia Agilao w słabość Sandmana. Przekazuje One More Johannie. Johanna trafia Freilą w słabość stojącego Sui-Ki, więc może przekazać kolejną dodatkową akcję Orpheusowi. Orpheus może działać raz dodatkowo; Johanna nie może ponownie otrzymać dodatkowej akcji w tym samym łańcuchu. Późniejsza zwykła tura Johanny zaczyna nowy łańcuch.')
h('Zakres wersji')
p('Nie rozpatrujemy jeszcze Technical, All Out Attack, Hold Up ani One More z krytyków. Brak tych zasad nie oznacza usunięcia ich z docelowego systemu.')

page('Koszty i katalog umiejętności')
p('Obowiązują obniżone koszty homebrew. Stare koszty P5R z pierwszych przykładów nie są cennikiem tej wersji. Poniżej są tylko umiejętności potrzebne do prób, nie kompletna lista dostępnych mocy.')
table(['Umiejętność','Cel i efekt','Koszt'],[
('Zwykły atak','Jeden cel; light Physical.','0'),
('Frei Garu Zio','Jeden cel; light Nuclear / Wind / Electricity.','1 SP'),
('Agilao Freila Garula','Jeden cel; medium Fire / Nuclear / Wind.','2 SP'),
('Mafrei','Wszyscy wrogowie; light Nuclear. Propozycja kosztu, nieprzetestowana obszarowo.','3 SP'),
('Headbutt','Jeden cel; medium Physical. Bez Forget w próbach.','5 HP'),
('Assault Dive','Jeden cel; heavy Physical.','8 HP'),
('Diarama','Jeden sojusznik; przywraca 20 HP.','2 SP'),
('Tarunda','Jeden wróg; −4 obrażenia przez trzy jego tury.','2 SP'),
('Rakukaja','Jeden sojusznik; propozycja: −4 otrzymywane obrażenia przez trzy jego tury.','2 SP'),
('Cadenza','Cała drużyna; leczy 50% maks. HP, daje +2 do ataku i Obrony przez trzy tury każdego odbiorcy.','6 SP')
],[3.8,11.6,2])
p('Koszty HP są stałe, nie procentowe. Dla Tarundy licz obrażenia jako: maksimum z 0 oraz wynik ataku minus 4, następnie zastosuj właściwość celu. To kolejność proponowana dla spójności; dotychczas badaliśmy Tarundę przy normalnych trafieniach. Efekt obszarowy zmniejsza obrażenia każdemu trafionemu celowi. Wielokrotne uderzenia wymagają osobnego balansu.')
h('Czas działania')
p('Efekt działa podczas trzech kolejnych zwykłych tur wskazanej postaci. Po zakończeniu trzeciej wygasa. Dodatkowe akcje nie skracają czasu. Przy efekcie nakładanym podczas własnej tury licznik zaczynamy od następnej własnej tury. Ponowienie tego samego efektu odnawia licznik do trzech.')
h('Czego jeszcze nie wyceniamy')
p('Nie ustaliliśmy uniwersalnych kosztów heavy magic, medium obszarowego, wskrzeszania, statusów i zdejmowania debuffów. Nie przenosimy automatycznie kosztów z gry. Każdy nowy skill otrzymuje opis celu, siły, kosztu i czasu działania.')

page('Persony eksploracja i przeciwnicy')
h('Jedna osobista Persona')
p('Bohater ma jedną własną Personę, z którą pozostaje związany i którą rozwija. Limit to osiem skilli; przy dodawaniu dziewiątego wybiera zastępowany. Nie stosujemy części ciała ani osobnych pul HP Persony i użytkownika. Doprecyzowanie robocze: pasywne skille liczymy do ośmiu; trait zapisujemy osobno, a jego dostępność i moc wymagają dalszego projektu.')
p('Zebrane od Shadows Persony trafiają do ograniczonego banku i stanowią materiał do rozwoju lub tworzenia skill cards w Velvet Room. Wielkość banku, koszty i receptury nie są jeszcze ustalone. Itemizacja w P5R i nasze łączenie materiałów na karty nie są tą samą procedurą.')
h('Rozwój przez EXP')
p('Przyjęty kierunek: jeden licznik EXP prowadzi do awansu. Awans daje przyrost parametrów i wybór ulepszenia, bez kupowania podstawowej wytrzymałości i skilli z konkurujących pul. Osobista Persona ma zachować długą ścieżkę rozwoju. Progi EXP, przyrosty i dostępność poziomów mocy pozostają nieustalone.')
h('Safe room i zasoby')
p('Safe room jest bezpiecznym miejscem powrotu. Sam pobyt nie odnawia automatycznie HP ani SP. Leczenie działa według skilli i zużywa SP. Przedmiot testowy odnawia 20 SP jednej postaci, do jej maksimum; podczas walki użycie zajmuje akcję. Nie nadaliśmy mu jeszcze ceny ani zasad dostępności.')
p('Oczyszczone miejsca nie odradzają przeciwników przy zwykłym cofnięciu. Alarm może w przyszłości stanowić wyjątek. Nie ma dodatkowego toru zmęczenia. Kalendarz, Social Links i przeszkody śledcze pozostają przyjętym kierunkiem, bez gotowych wartości liczbowych.')
h('Przykładowe karty przeciwników')
table(['Przeciwnik','HP','Wybrane właściwości','Atak w próbie'],[
('Sandman','28','Weak Fire, Electricity; Resist Wind','Light Physical, jeden cel'),
('Sui Ki','36','Weak Nuclear; Drain Ice; Resist Gun, Electricity','Medium Ice, jeden cel'),
('Shiki Ouji miniboss','140','Weak Nuclear; Null Physical, Gun, Bless, Curse','Double Shot: dwa osobne light Gun; 6 HP za całość'),
('Rakshasa miniboss','140','Weak Wind, Bless; Resist Physical, Fire, Curse; Null Gun','Jeden heavy Physical; koszt 8 HP')
],[4,1.1,6.8,5.5])
p('To karty uproszczone do testów, nie pełny bestiariusz. Zestawy ataków i koszty minibossów są homebrew. Nie traktuj 140 HP jako uniwersalnego wzoru ani nie obniżaj HP przeciwnika poniżej 1 przez sam koszt jego skilla.')

page('Prowadzenie prób i dalsze ustalenia')
h('Co sprawdzać przy stole')
p('Notuj liczbę rund, HP/SP po walce, liczbę leczeń i użytych przedmiotów oraz to, czy słabości były znane. Pierwszy nokaut, skrajnie długa walka lub wyczerpanie jednego uzdrowiciela są sygnałem do analizy. Sprawdź osobno zasady systemu i skład konkretnego starcia.')
p('Cel projektowy to możliwość rozegrania około czterech do sześciu drobnych potyczek i minibossa przy rozsądnym przygotowaniu. To nie gwarancja dla każdej drużyny ani sztywny wymóg każdego Pałacu. Niektóre duety potrzebują wcześniej zaplanowanej regeneracji lub alternatywnej drogi.')
h('Granice dotychczasowych symulacji')
p('Symulacje służyły wstępnemu porównaniu zasobów. Korzystały z prostych strategii, ograniczonych zestawów skilli i zmienianych kart przeciwników. Pomijały statusy, krytyki, traity i część ataków obszarowych. Uzyskane odsetki wygranych opisują konkretne modele, nie potwierdzają ostatecznego balansu ani skuteczności każdej taktyki gracza.')
h('Kolejne decyzje')
table(['Obszar','Do ustalenia'],[
('Postać i awans','Cechy bojowe, tworzenie postaci, HP/SP na początku i przyrosty, EXP.'),
('Rozwój Persony','Budżet tworzenia, ograniczenia odporności, osiem skilli, traity i skill cards.'),
('Rozszerzenia walki','Statusy, krytyki, Technical, obszar, Guard, ucieczka, wskrzeszanie i porażka.'),
('Codzienność','Bloki czasu, cechy społeczne, Social Links i nagrody za śledztwo.'),
('Przygotowanie GM','Budżet spotkań, skalowanie poziomów, zapasy i alarm.')
],[4.1,13.3])
h('Źródła odniesienia')
p('Własne zasady opracowane w rozmowie. P5R dostarcza nazw, tożsamości umiejętności i właściwości inspirujących karty. Liczby homebrew z tego dokumentu zastępują liczby gry na potrzeby prób.')
for label,url in [
('Orpheus','https://megatenwiki.com/wiki/Gameplay%3AOrpheus'),
('Johanna','https://megamitensei.fandom.com/wiki/Johanna'),
('Zorro','https://megamitensei.fandom.com/wiki/Zorro'),
('Captain Kidd','https://megatenwiki.com/wiki/Captain_Kidd'),
('Shadows z Pałacu Kaneshiro','https://www.neoseeker.com/persona-5-royal/Kaneshiro%27s_Bank')]:
    par=p(label+' — '+url)
    for r in par.runs:r.font.size=Pt(8.5)

foot=sec.footer.paragraphs[0]
foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT
run=foot.add_run('Persona 5 RPG  •  0.1  •  ');run.font.size=Pt(8)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)
out=ROOT/'Persona_5_RPG_Zasady_0_1.docx'
doc.save(out)
print(out)
