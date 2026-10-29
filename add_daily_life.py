from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root=Path(__file__).parent
path=root/'Persona_5_RPG_Zasady_0_2.docx'
doc=Document(path)
assert not any(p.text=='Daily life i relacje' for p in doc.paragraphs)
backup=root/'Persona_5_RPG_Zasady_0_2_przed_daily_life.docx'
if not backup.exists(): backup.write_bytes(path.read_bytes())
body=doc.element.body
old_nodes=set(body)
def p(t): doc.add_paragraph(t)
def h(t): doc.add_heading(t,2)
doc.add_page_break()
doc.add_heading('Daily life i relacje',1)
p('Moduł dla GM łączący kalendarz, swobodne aktywności, śledztwo oraz relacje. Zasady poniżej są naszym homebrew. Wartości treningu i bonusów Arkan są roboczą bazą do pierwszych sesji; nie były jeszcze sprawdzane w kampanii. Nie wymagamy rozpisania wszystkich Arkan ani wszystkich dni przygody z góry.')
h('Dwa bloki czasu')
p('Każdy dzień daje dwa bloki: dzień i wieczór. Szkoła albo praca, zależnie od wieku postaci, zwykle poprzedza blok dzienny. GM może rozegrać tam okazjonalną krótką scenę i przyznać punkt rozwoju odpowiedni do sytuacji, bez zużywania bloku. Nie jest to gwarantowana codzienna nagroda.')
p('Wyprawa do pałacu jest możliwa wyłącznie w bloku dziennym i zużywa ten blok. Wieczór po powrocie pozostaje dostępny. Śledztwo odbywa się zgodnie z fikcją i decyzją GM, zwykle za jeden blok. Rekomendujemy więcej tropów i spotkań śledczych wieczorem, aby ustalenia można było wykorzystać w pałacu następnego dnia.')
h('Aktywności i własne pomysły')
p('Spotkanie w ramach relacji, trening na siłowni, medytacja i inna znacząca aktywność zajmują zwykle jeden blok. Trzy bloki treningu fizycznego dają +1 maksymalnego HP; trzy bloki medytacji lub podobnej praktyki dają +1 maksymalnego SP. Prowadź osobny licznik 0–3 dla każdego zasobu i wyzeruj go po zwiększeniu maksimum. Wzrost maksimum nie odnawia bieżącego HP ani SP. Są to dodatki do bazowych wzorów 34 + poziom HP i 30 + poziom SP, a nie ich zamiennik.')
p('Lista aktywności pozostaje otwarta. Gdy gracz opisuje inny sposób spędzenia czasu, GM dopasowuje nagrodę: postęp HP/SP, odpowiednią cechę społeczną, relację albo inne uzasadnione zwiększenie statystyki. Przed zużyciem bloku gracz powinien wiedzieć, co rozwija. Nie podnosimy automatycznie ataku lub Obrony za każde hobby; przy nietypowym bonusie ustalamy wcześniej jego zakres. Szczegółowe progi cech społecznych pozostają do ustalenia w podręczniku gracza.')
p('Przykłady: taniec może rozwijać kondycję lub urok, gotowanie troskliwość lub zręczność, czytanie wiedzę, a prowadzenie bloga kontakty. GM dobiera kategorię do celu gracza i opisu sceny. Nie wymagamy rzutów za rutynową aktywność, żeby uzyskać zwykły postęp.')
h('Relacje od rangi 1 do 6')
p('Ranga 1 oznacza nawiązanie znaczącej relacji. Każda kolejna ranga wymaga dwóch znaczących spotkań i sceny pokazującej zmianę w relacji; ta scena może być częścią drugiego spotkania i nie wymaga dodatkowego bloku. Rangi 2, 4 i 6 odblokowują bonusy, a rangi 3 i 5 rozwijają historię. Na osiągnięcie rangi 6 od rangi 1 potrzeba zatem zwykle dziesięciu znaczących spotkań. Tempo można dopasować do długości kampanii, uzgadniając zmianę z graczami.')
p('Nie oceniamy poprawności odpowiedzi dialogowych. Szczera kłótnia, wzajemna pomoc lub rozwiązanie wspólnego problemu również mogą rozwijać więź. Zwykłe powitanie nie daje automatycznie postępu. Rozwój nie wymaga romansu; rangę 6 mogą osiągnąć przyjaźń, relacja rodzinna lub mentorska. Nie trzeba tworzyć NPC każdej Arkany.')
h('Wspólne aktywności bohaterów')
p('Relację między dwoma bohaterami zapisujemy raz, wspólnie, z jedną rangą i licznikiem spotkań. Wspólna aktywność zużywa blok obu osób. Każda otrzymuje zwykły postęp aktywności; jeśli rozegrała się znacząca scena między nimi, obie rozwijają również wspólną relację. Przykład: wspólna siłownia może dać każdemu jeden z trzech punktów treningu HP oraz jedno znaczące spotkanie. Nie mnożymy automatycznie postępu wszystkich par tylko dlatego, że grupa znalazła się w jednym miejscu.')
p('Na rangach 2, 4 i 6 każdy bohater otrzymuje bonus Arkany drugiej osoby. Relacje z NPC również dają bonusy Arkany tego NPC. Ten sam nazwany bonus nie kumuluje się z kilku relacji: zachowujemy najwyższą odblokowaną wersję, bez dodatkowych użyć. Dzięki temu kilka znajomości tej samej Arkany nie zwielokrotnia identycznej zdolności.')
h('Osobista Arkana bohatera')
p('Każdy gracz wybiera jedną Arkanę, unikatową w obrębie drużyny, według tematu postaci, jej pragnień lub drogi rozwoju. Nie narzuca ona osobowości, moralności, żywiołów ani Arkany osobistej Persony. Bohater od początku otrzymuje jej bonus rangi 2 jako zdolność inherentną. Nie zajmuje ona jednego z ośmiu slotów skilli. Nie wymaga posiadania talii tarota.')
p('Osobistej zdolności nie kopiują pozostali przez relację z jej właścicielem. Dla wybranych przez graczy Arkan przygotujemy przed grą zamienniki bonusu rangi 2 dla odbiorców takiej relacji oraz dopasujemy zależne od niego ulepszenia rang 4 i 6. Poniższy katalog jest pełną bazą dla relacji z NPC; warianty relacji między bohaterami wymagają tego krótkiego dopasowania. Osobista zdolność nie rośnie automatycznie od rozwijania relacji ze sobą. Świat pozostaje opcją finałową i nie jest dostępny przy tworzeniu postaci.')
h('Wspólne zasady bonusów')
p('Wyższa wartość zastępuje niższą, chyba że opis dodaje nowy efekt. Przykładowo Rydwan na randze 6 daje łącznie +6 maksymalnego HP. Aktywna zdolność działa raz na wyprawę do pałacu, chyba że podano inaczej; jedno użycie obejmuje jej odblokowane ulepszenia. Bierne zwiększenia maksimum działają stale, a wytwarzanie przedmiotów wymaga wskazanego bloku. Wyprawa kończy się powrotem do świata rzeczywistego; safe room i respawn nie odnawiają użyć. Zdolności na sesję odnawiają się na kolejnym spotkaniu przy stole. Drugi wynik przerzutu jest obowiązkowy.')
p('Zdolność bez kosztu akcji deklarujemy przy opisanym wyzwalaczu. Bonusy obrażeń Głupca i Osądu dodajemy po zwykłych mnożnikach. Aktywne zdolności wymagające decyzji bohatera są niedostępne, gdy nie może działać, chyba że opis wprost dotyczy nokautu. Zdolności informacyjne nie zastępują podstawowych wskazówek niezbędnych do prowadzenia historii.')

arcanas=[
('Głupiec — Fool','Zaufanie i nowy początek','Gdy drużyna zaskoczy wrogów, twój pierwszy trafiony atak w pierwszej rundzie zadaje +3 obrażenia.','Premia rośnie do +5.','Premia +5 obejmuje także pierwszy trafiony atak jednego wybranego sojusznika w pierwszej rundzie.'),
('Mag — Magician','Pomysłowość i rzemiosło','W jednym bloku przygotuj przedmiot odnawiający 5 HP.','Możesz zamiast niego przygotować przedmiot odnawiający 2 SP.','W tym samym bloku przygotowujesz dwa takie przedmioty, dowolnie wybrane.'),
('Kapłanka — Priestess','Obserwacja i intuicja','Bez akcji poznaj jedną wybraną właściwość żywiołową widocznego wroga.','Przy tym samym użyciu poznaj też jedną jego umiejętność.','Przy tym samym użyciu poznaj wszystkie właściwości tego wroga.'),
('Cesarzowa — Empress','Opieka i tworzenie','Jedno twoje leczenie HP skillem przywraca dodatkowe 3 HP każdemu celowi.','Premia rośnie do 5 HP.','Premia rośnie do 8 HP.'),
('Cesarz — Emperor','Odpowiedzialność i organizacja','Jeden sojusznik otrzymuje +2 do pojedynczego rzutu ataku. Deklaruj przed rzutem.','Premia rośnie do +3.','Możesz wspomóc dwa różne ataki zamiast jednego.'),
('Hierofant — Hierophant','Tradycja i bezpieczna przystań','W wieczornym bloku przygotuj porcję posiłku odnawiającą 5 HP poza walką.','Przygotowujesz dwie porcje.','Każda porcja odnawia również 2 SP.'),
('Kochankowie — Lovers','Bliskość i szczerość','Gdy przekazujesz Baton Pass, odbiorca odzyskuje 3 HP.','Odzyskuje 5 HP zamiast 3.','Odzyskuje również 1 SP.'),
('Rydwan — Chariot','Wytrwałość i działanie','Stałe +2 maksymalnego HP.','Łącznie +4 maksymalnego HP.','Łącznie +6 maksymalnego HP; raz na wyprawę po udanej wspólnej ucieczce odzyskujesz 5 HP.'),
('Sprawiedliwość — Justice','Prawda i wydawanie wyroku','Po trafieniu zadającym co najmniej 1 obrażenie ogłoś Osąd: +4 obrażenia, których nie zmniejsza Resist ani Guard.','Osąd zadaje +7 obrażeń zamiast +4.','Dwa użycia Osądu na wyprawę, najwyżej jedno na akcję.'),
('Pustelnik — Hermit','Dystans i rozpoznanie','Przed wybraniem drogi GM wskazuje bezpieczniejszy z dwóch dostępnych kierunków.','Przy tym samym użyciu ujawnia także rodzaj zagrożenia na niebezpieczniejszej drodze.','Dodatkowo raz na wyprawę drużyna omija bez rzutu jedną wcześniej zauważoną zwykłą grupę Shadows. Bez zdobyczy, z wyłączeniem bossów i obowiązkowych starć fabularnych.'),
('Koło Fortuny — Fortune','Szansa i zmiana','Przerzuć własny rzut obronny przeciw statusowi.','Możesz zamiast tego przekazać przerzut sojusznikowi.','Dwa użycia zamiast jednego, nie na ten sam rzut.'),
('Siła — Strength','Opanowanie i odwaga','Gdy twój Guard się skończy, odzyskaj 3 HP, jeśli zmniejszył obrażenia przynajmniej jednego ataku i nadal jesteś przytomny.','Odzyskujesz 5 HP.','Możesz zamiast siebie uleczyć o 5 HP jednego sojusznika.'),
('Wisielec — Hanged Man','Poświęcenie i inna perspektywa','Po rozliczeniu trafienia sojusznika przejmij 3 jego obrażenia, najwyżej tyle, ile miał otrzymać.','Możesz przejąć do 5 obrażeń.','Możesz przejąć do 8 obrażeń. Przeniesionych obrażeń nie redukujemy ponownie; mogą cię znokautować.'),
('Śmierć — Death','Przemiana i leczenie','Użyty przez ciebie przedmiot przywracający HP leczy dodatkowe 3 HP na cel.','Premia rośnie do 5 HP.','Możesz zamiast premii usunąć jeden z 12 zwykłych statusów z jednego leczonego celu.'),
('Umiarkowanie — Temperance','Równowaga i odpoczynek','Podczas pobytu w safe roomie odzyskaj 3 HP bez przedmiotu.','Odzyskujesz również 1 SP.','Ten sam odpoczynek obejmuje także jednego wybranego sojusznika.'),
('Diabeł — Devil','Plotki i wpływy','Podczas jednego bloku śledztwa otrzymaj dodatkowy trop o reputacji lub sekretach celu.','GM wskazuje również osobę, która może go potwierdzić.','Uzyskanie dostępu do tej osoby nie wymaga osobnego bloku, jeśli jest osiągalna.'),
('Wieża — Tower','Przełamanie i upadek pozorów','Jeden twój atak ignoruje Resist celu; deklaruj przed rzutem.','Możesz zamiast siebie wspomóc atak sojusznika.','Dwa użycia zamiast jednego. Nigdy nie omija Null, Drain ani Repel.'),
('Gwiazda — Star','Nadzieja i strategia','Przed pierwszą turą walki zamień swoją pozycję w inicjatywie z chętnym sojusznikiem.','Możesz zamiast tego zamienić miejsca dwóch chętnych sojuszników.','Dwa użycia na wyprawę. Zmiana nigdy nie przekracza granicy stron przy surprise.'),
('Księżyc — Moon','Niepewność i ukryta prawda','Raz na sesję przed blokiem śledztwa zapytaj GM, czy proponowany sposób może dać nową istotną informację. Odpowiedź jest szczera, bez ujawnienia informacji.','Jeśli odpowiedź brzmi nie, GM wskazuje jeden osiągalny kontakt, miejsce lub sposób pozwalający posunąć śledztwo naprzód.','Dodatkowo raz na sesję, jeśli blok śledztwa nie dał nowej istotnej informacji ani postępu, jego uczestnicy mogą wykorzystać ten sam blok na inną aktywność.'),
('Słońce — Sun','Otwartość i inspiracja','Przedmiot HP wybrany w twoich negocjacjach odnawia dodatkowe 3 HP.','Możesz zamiast tego zwiększyć odnowę przedmiotu SP o 1 SP.','Możesz zamiast powyższych premii wybrać dwie sztuki podstawowej nagrody przedmiotowej.'),
('Sąd — Judgement','Rozliczenie i druga szansa','Po twoim nokaucie pierwszy użyty na tobie przedmiot wskrzeszający przywraca dodatkowe 3 HP.','Premia rośnie do 5 HP.','Dodatkowo raz na wyprawę zamiast spaść do 0 HP pozostajesz na 1 HP.'),
('Wiara — Faith','Przekonanie i aspiracja','Dodaj +2 do własnego nieudanego rzutu ataku, jeśli zmieni to wynik w trafienie.','Premia rośnie do +3.','Możesz zamiast siebie wspomóc taki rzut sojusznika.'),
('Doradca — Councillor','Zrozumienie i wsparcie','Stałe +1 maksymalnego SP.','Łącznie +2 maksymalnego SP.','Łącznie +3 maksymalnego SP; dodatkowo raz na wyprawę usuń z siebie jeden zwykły status bez akcji, o ile możesz działać.'),
('Świat — World','Spełnienie i wspólnota','Wybierz jeden bonus rangi 2 innej Arkany, z wyjątkiem zastrzeżonych osobistych zdolności pozostałych graczy.','Wybierz drugi bonus rangi 2 innej Arkany, z tym samym ograniczeniem.','Raz na wyprawę każdy przytomny członek drużyny odzyskuje 5 HP i 2 SP. Świat jest opcją finałową, niedostępną przy tworzeniu postaci.'),
]
doc.add_heading('Katalog bonusów Arkan',1)
p('Rangi 1, 3 i 5 mają znaczenie fabularne według wspólnych zasad relacji. Poniżej podano mechaniczne nagrody rang 2, 4 i 6. Nazwy angielskie pomagają porównywać katalog z P5R; efekty są autorskie.')
for name,theme,r2,r4,r6 in arcanas:
    h(name)
    p(theme)
    t=doc.add_table(rows=1,cols=2)
    t.autofit=False
    from docx.shared import Cm
    for col,width in zip(t.columns,[1.6,15.8]): col.width=Cm(width)
    for c,txt in zip(t.rows[0].cells,['Ranga','Korzyść']): c.text=txt
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for rank,txt in [(2,r2),(4,r4),(6,r6)]:
        cells=t.add_row().cells
        cells[0].text=str(rank); cells[1].text=txt
    for ri,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for ci,cell in enumerate(row.cells):
            cell.width=Cm([1.6,15.8][ci])
            pr=cell._tc.get_or_add_tcPr()
            borders=OxmlElement('w:tcBorders')
            for side in ['top','left','bottom','right']:
                e=OxmlElement('w:'+side)
                for k,v in [('val','single'),('sz','4'),('color','D9D9D9')]: e.set(qn('w:'+k),v)
                borders.append(e)
            pr.append(borders)
            margins=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'80');e.set(qn('w:type'),'dxa');margins.append(e)
            pr.append(margins)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EAEAEA');pr.append(sh)
            for par in cell.paragraphs:
                par.paragraph_format.space_after=Pt(3)
                for run in par.runs: run.font.size=Pt(10);run.bold=ri==0;run.font.color.rgb=RGBColor(0,0,0)
    p('')
h('Doprecyzowania czterech poprawionych Arkan')
p('Głupiec: premia działa wyłącznie przy surprise bohaterów, najwyżej raz na wyprawę, i przepada dla osoby, która nie trafi w pierwszej rundzie wybranej walki. Deklaruj użycie przed pierwszą turą tej walki. Atak musi zadać obrażenia. Premia nie tworzy nowej tury ani osobnego One More.')
p('Sprawiedliwość: Osąd nie omija Null, Drain ani Repel, ponieważ wymaga wcześniejszego zadania obrażeń atakiem. Jego dodatek nie powoduje osobnego Down ani One More. Podana premia dotyczy jednego trafionego celu na użycie, także przy skillu obszarowym lub multi hit.')
p('Pustelnik: ranga 6 dodaje osobne jednorazowe ominięcie grupy; wcześniejsze rozpoznanie drogi zachowuje własne jedno użycie. Ominięci przeciwnicy nadal istnieją. GM wskazuje bezpieczniejszą drogę na podstawie dostępnej sytuacji; gdy są równie groźne, mówi o tym wprost.')
p('Księżyc: odzyskanie bloku obejmuje wszystkich uczestników tego śledztwa, nie tylko właściciela bonusu. Nie wymaga ustalenia winy graczy lub GM. Nie cofa zużytych przedmiotów ani wydarzeń, a jedynie daje możliwość innej aktywności w tym samym bloku. Nie pozwala wielokrotnie rozgrywać tego samego bloku.')
h('Prowadzenie bez dodatkowych podsystemów')
p('Przed sceną GM jasno określa, czy zużyje ona blok i czy może dać postęp. Krótkie rozmowy organizacyjne i drobne zakupy można rozstrzygać bez bloku; istotne poszukiwania lub dłuższe spotkania zwykle go zajmują. Dostępność NPC, terminy i konsekwencje wynikają z historii. Jeśli graczom grozi fabularny termin, powinien być dla nich czytelny.')
p('Podstawowa wskazówka konieczna do dalszej gry nie wymaga posiadania konkretnej Arkany. Jej zdobycie może kosztować czas, przysługę lub wymagać innego podejścia. Relacje nie spadają automatycznie przez brak codziennych spotkań. Odpoczynek nocny i jego odnowę HP/SP należy ustalić osobno przed pierwszą wyprawą; ten moduł nie przyznaje automatycznie pełnej regeneracji.')
p('Do testów obserwujemy tempo rang, przyrost maksymalnego HP/SP i liczbę używanych zdolności. Szczególnej uwagi wymagają Wieża, Księżyc oraz Świat. Szczegółowe zasady tworzenia postaci, cech społecznych i rozwoju przez EXP pozostają w zakresie przyszłego podręcznika gracza.')
p('Odniesienie dla listy i angielskich nazw Arkan: Persona 5 Royal Confidant List, SAMURAI GAMERS, https://samurai-gamers.com/persona-5/confidants-list-schedule-guide/. Bonusy, sześć rang oraz osobista Arkana są naszym homebrew.')

# Place the module before the reference appendices, keeping the recovery tables last.
new_nodes=[n for n in body if n not in old_nodes and n.tag!=qn('w:sectPr')]
anchor=next(p for p in doc.paragraphs if p.text=='Proponowane wzory na HP i SP')._p
for node in new_nodes: anchor.addprevious(node)
for par in doc.paragraphs:
    if par.text.startswith('Wersja 0.2'):par.text='Wersja 0.2 • aktualizacja 28 października 2026 • podręcznik GM z modułem daily life'
    elif 'Daily life i śledztwo będą kolejnym modułem.' in par.text:par.text=par.text.replace('Daily life i śledztwo będą kolejnym modułem.','Daily life i śledztwo opisuje rozdział Daily life i relacje.')
    elif par.text.startswith('Oczyszczone miejsca nie odradzają przeciwników'):
        par.text=par.text.replace('Kalendarz, Social Links i przeszkody śledcze pozostają przyjętym kierunkiem, bez gotowych wartości liczbowych.','Kalendarz, relacje i przeszkody śledcze opisuje moduł Daily life i relacje.')
doc.save(path)
c=Document(path)
assert len(arcanas)==24 and len(c.tables)==60
assert sum(len(t.rows)-1 for t in c.tables[-4:])==157
assert sum(len(t.rows)-1 for t in c.tables if len(t.columns)==6 and t.cell(0,0).text=='Umiejętność')==541
assert all(any(par.text==a[0] for par in c.paragraphs) for a in arcanas)
assert any(len(t.rows)==100 and t.cell(0,0).text=='Poziom' for t in c.tables)
print('OK: daily life, 24 Arkana, 72 nagrody rang; zachowano 541 skilli i traitów, 157 przedmiotów oraz poziomy 1–99.')
