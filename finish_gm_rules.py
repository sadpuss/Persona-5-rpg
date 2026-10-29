from pathlib import Path
from docx import Document

root = Path(__file__).parent
path = root / 'Persona_5_RPG_Zasady_0_2.docx'
backup = root / 'Persona_5_RPG_Zasady_0_2_przed_domknieciem_GM.docx'
if not backup.exists():
    backup.write_bytes(path.read_bytes())
doc = Document(path)

for p in doc.paragraphs:
    t = p.text
    if t.startswith('Wersja 0.2'):
        p.text = 'Wersja 0.2 • aktualizacja 28 października 2026 • zasady walki i eksploracji dla GM'
    elif t.startswith('2. Na początku tury usuń Down'):
        p.text = ('2. Na początku zwykłej tury kończy się poprzedni Guard i znika Down tej postaci; następnie sprawdź statusy. Postać ma jedną zwykłą akcję: atak, skill, przedmiot, Guard, próbę ucieczki albo świadome zrezygnowanie z działania. Dodatkowa akcja nie zastępuje zwykłej tury kompana.')
    elif t.startswith('Doprecyzowanie do prób: przy 0 HP'):
        p.text = ('Przy 0 HP postać jest nieprzytomna i nie działa; zwykłe leczenie nie wskrzesza. Nokaut jednej osoby nie kończy walki, dopóki ktoś z drużyny pozostaje przytomny. Dopiero 0 HP wszystkich bohaterów i ich walczących kompanów oznacza porażkę oraz powrót do punktu zapisu. Dawne symulacje kończone na pierwszym nokaucie były ostrzejszym testem bezpieczeństwa balansu, a nie regułą kampanii.')
    elif t.startswith('Nie rozpatrujemy jeszcze Technical, All Out Attack'):
        p.text = 'Hold Up, negocjacje i All-Out Attack działają według kolejnego rozdziału. Technical pomijamy w tym systemie. One More z krytyków nadal nie ma ustalonej reguły.'
    elif t.startswith('Na początku tury usuń Down, następnie sprawdź statusy.'):
        p.text = t.replace('Na początku tury usuń Down, następnie sprawdź statusy.', 'Na początku zwykłej tury zakończ Guard, usuń Down, a następnie sprawdź statusy.')
    elif t.startswith('Nakładanie statusu samo nie daje One More.'):
        p.text = ('Nakładanie statusu samo nie daje One More. Technical pomijamy: połączenia żywiołu ze statusem nie dają dodatkowych obrażeń ani Down. Garu przeciw Burn i Nuclear przeciw Freeze rozliczamy jak zwykłe ataki według właściwości celu. Skille i traity z katalogu źródłowego działające wyłącznie na Technical są niedostępne. Czasy statusów i stałe liczby są propozycją do testów przy stole, nie odtworzeniem wzorów komputerowych P5R.')
    elif t.startswith('Safe room jest bezpiecznym miejscem powrotu.'):
        p.text = t + ' Wejście zapisuje także stan wyprawy na wypadek porażki; szczegóły opisuje rozdział Punkty zapisu i porażka drużyny.'
    elif t.startswith('Oczyszczone miejsca nie odradzają przeciwników'):
        p.text = t.replace('Alarm może w przyszłości stanowić wyjątek.', 'Wyjątkiem jest odtworzenie zapisu po porażce; alarm może w przyszłości stanowić kolejny wyjątek.')

anchor = next(p for p in doc.paragraphs if p.text == 'Nakładanie statusów')
def add(text, style=None):
    return anchor.insert_paragraph_before(text, style)
def h(text): add(text, 'Heading 2')

add('Obrona ucieczka i zakończenie walki', 'Heading 1')
add('Ten rozdział uzupełnia podstawową pętlę walki. Liczby dotyczą naszego RPG i pozostają do sprawdzenia w kampanii. Nie zmieniają kosztów ani statystyk w źródłowym katalogu P5R.')
h('Guard')
add('Guard zajmuje jedną akcję i nie kosztuje HP ani SP. Działa od wybrania tej akcji do początku następnej zwykłej tury postaci albo do jej nokautu lub końca walki. Zmniejsza obrażenia z trafiających ją ataków o 60%, czyli postać otrzymuje 40% wyliczonej wartości. Dotyczy to także ataków obszarowych i Almighty. Ponowne użycie nie wzmacnia ochrony.')
add('Najpierw oblicz obrażenia ataku i właściwość celu, następnie pomnóż przez 0,4 za Guard. Na końcu zaokrąglij w dół; wynik może wynieść 0. Resist i Guard łączą się przez mnożenie, nie przez dodanie procentów. Null nadal oznacza 0; Drain i Repel rozpatrujemy według ich własnych zasad, bez zmniejszania leczenia lub odbicia przez Guard.')
add('Przykłady dla ataku o bazowych 20 obrażeniach: zwykły cel z Guard otrzymuje 20 × 0,4 = 8 HP obrażeń. Cel z Resist i Guard otrzymuje 20 × 0,5 × 0,4 = 4 HP obrażeń. Cel z Weakness i Guard otrzymuje 20 × 1,5 × 0,4 = 12 HP obrażeń. Bez Guard te wartości wynosiłyby odpowiednio 20, 10 i 30.')
add('Podczas Guard postaci nie można przewrócić atakiem, również trafiając w jej Weakness. Słabość nadal zwiększa obrażenia, lecz nie wywołuje Down ani One More za to trafienie. Wybranie Guard usuwa już istniejący Down tej postaci. Guard nie leczy statusów ani nie chroni przed ich nałożeniem; Burn, utrata SP, koszt HP skilla i inne skutki niebędące obrażeniami z ataku pozostają bez zmian. Dodatkowa akcja nie kończy ochrony i nie przedłuża jej czasu.')
h('Ucieczka drużyny')
add('Raz na rundę jedna zdolna do działania postać może przeznaczyć swoją zwykłą akcję na próbę wycofania całej drużyny. Rzuć d20 bez bonusów: wynik 11 lub więcej oznacza sukces. Nie można próbować ucieczki w One More ani Baton Pass. Nieudana próba zużywa tylko akcję próbującej postaci; pozostali zachowują swoje tury, ale w tej rundzie nie podejmują kolejnej próby.')
add('Sukces natychmiast kończy walkę i przenosi drużynę do poprzedniej bezpiecznej części pałacu; przytomni zabierają nieprzytomnych. HP, SP i zużyte przedmioty pozostają w aktualnym stanie, a statusy kończą się jak po walce. Ucieczka nie jest porażką i nie odtwarza zapisu. Pokonani wrogowie pozostają pokonani; pozostali zostają w tym miejscu i przed kolejnym starciem odzyskują własne HP i SP. Sama ucieczka nie daje zdobyczy za ocalałych wrogów.')
add('W wyjątkowym starciu fabularnym GM może wyłączyć ucieczkę, ale informuje o tym przed wyborem akcji. Przykład: w rundzie 2 Zorro wyrzuca 7, więc zużywa akcję. Kidd nadal działa normalnie. Kolejna próba jest możliwa dopiero w rundzie 3; wynik 14 wyprowadza obu bohaterów z walki.')
h('Pozycja i zasięg')
add('W trakcie walki każdy uczestnik może dosięgnąć każdego przeciwnika lub sojusznika, jeśli działanie pozwala wybrać taki cel. Nie mierzymy ruchu, odległości, sąsiedztwa ani linii strzału. Atak na jednego wroga nadal dotyczy jednego celu, a atak na wszystkich obejmuje całą wskazaną stronę. Nie ma ataków okazyjnych ani bonusów za otoczenie.')
add('Na czas starcia otoczenie poza areną umownie znika. Nie dodajemy do inicjatywy osób spoza walki ani akcji otwierania odległych drzwi. Po walce wraca zwykła scena eksploracji. Jeśli scena wymaga ratowania kogoś za drzwiami lub innej przeszkody przestrzennej, GM rozstrzyga to jako osobną scenę, zamiast wprowadzać ukryte zasięgi do tej walki.')
h('Hold Up')
add('Hold Up uruchamia się natychmiast po akcji bohatera, która przewróci ostatniego stojącego wroga, gdy wszyscy żywi przeciwnicy mają Down i przynajmniej jeden bohater jest przytomny oraz zdolny do działania. Sam Sleep, Freeze lub inny status nie zastępuje Down. Przy braku żywych przeciwników następuje zwykłe zwycięstwo.')
add('Zatrzymaj kolejkę i przed wykorzystaniem nowego One More wybierz jedną opcję: przedmiot, pozyskanie jednej Persony lub All-Out Attack. Hold Up jest bezpłatnym rozstrzygnięciem uzyskanej przewagi, a nie kolejną zwykłą turą. Każda z tych opcji kończy bieżący łańcuch One More i Baton Pass. Można też zrezygnować z Hold Up i kontynuować uzyskaną dodatkową akcję. Nowy Hold Up wymaga ponownego przewrócenia stojącego wroga; nie uruchamia się po każdym uderzeniu leżącego.')
h('Kto prowadzi negocjacje')
add('GM prowadzi prosty licznik przeprowadzonych negocjacji dla każdego gracza podczas bieżącej wyprawy do pałacu. Spośród chętnych, których bohaterowie mogą działać, pierwszeństwo mają osoby z najmniejszym licznikiem. Jeśli remisują, każda rzuca d20 bez bonusów; wyższy wynik wybiera prowadzącego, a remis rozstrzyga dogrywka. Po wyborze przedmiotu lub Persony zwiększ jego licznik o 1. All-Out Attack nie zużywa kolejki do negocjacji. Kompani prowadzeni przez GM nie odbierają graczom tej kolejki.')
add('Przykład: czterech graczy zaczyna z licznikiem 0. A wygrywa dogrywkę i bierze Personę; ma teraz 1. W następnym Hold Up pierwszeństwo mają B, C i D. Gdy wszyscy skorzystają raz, znów mają równe szanse. Osoba nieobecna lub niezdolna do działania nie blokuje pozostałych; zachowuje swój niższy licznik na później.')
h('Automatyczna nagroda za negocjacje')
add('Nie ma testu rozmowy, losowej odmowy ani obowiązkowego odgrywania pytań. Prowadzący wybiera jedną nagrodę. Przedmiot: drużyna dostaje jeden przedmiot z nagrody podanej na karcie Shadow, a jeśli karta jej nie określa, GM wybiera drobny przedmiot odpowiedni do starcia. Nagroda jest wspólna. Pozyskanie Persony: prowadzący wybiera dokładnie jednego z leżących Shadows i wpisuje jego Personę do własnego banku. Nie zastępuje ona osobistej Persony bohatera.')
add('W obu przypadkach wybrana nagroda jest gwarantowana, pozostali przeciwnicy odchodzą i walka się kończy. Nie dodajemy jeszcze drugiego kompletu łupów za odprawionych Shadows. Przy pełnym banku gracz zwalnia jedno miejsce przed przyjęciem nowej Persony albo wybiera inną nagrodę; pojemność banku ustalimy w podręczniku gracza. Nie wprowadzamy dodatkowego rzutu ani ograniczenia poziomu przy rekrutacji.')
add('Zwykłe Shadows reprezentujące Persony można pozyskiwać. Unikatowa istota fabularna bez odpowiednika Persony nie staje się automatycznie Personą do banku. GM oznacza na karcie przed sesją, czy dany boss dopuszcza Hold Up oraz jakie nagrody oferuje, i ujawnia wyjątek przed podjęciem decyzji o negocjacjach. Sama etykieta minibossa ani posiadanie Resist lub Null nie odbiera Hold Up.')
h('All Out Attack')
add('Każdy przytomny bohater i walczący kompan zdolny w tej chwili do wykonania ataku może uczestniczyć; jedna postać liczy się raz, razem ze swoją Personą. Nieprzytomni oraz osoby z zakazem działania lub atakowania nie uczestniczą. Sam Down nie wyklucza udziału. Jeśli nikt nie może zaatakować, tej opcji nie można wybrać.')
add('Nie rzucamy na trafienie. Rzuć raz 2d6 i dodaj 4 za każdego uczestnika: obrażenia = 2d6 + 4 × liczba uczestników. Każdy żywy wróg otrzymuje tę samą wartość obrażeń Almighty. Przykładowo: solo 2d6 + 4 (6–16), duet 2d6 + 8 (10–20), cztery postacie 2d6 + 16 (18–28). Wspólny wynik 7 na kościach daje odpowiednio 11, 15 lub 23 obrażenia każdemu wrogowi.')
add('All-Out Attack nie kosztuje HP ani SP. Pomija właściwości Physical, Gun i żywiołów; stosujemy wyłącznie wyraźnie zapisaną ochronę przed Almighty lub wszystkimi obrażeniami. Nie dokłada mnożnika za Down, Weakness, krytyka ani statusu. Nie daje One More ani kolejnego Hold Up. Ocalali wrogowie tracą Down i walka wraca do następnego uczestnika w kolejce po aktualnie działającej postaci. Jeżeli wszyscy zginęli, starcie się kończy. To robocza skala obrażeń do testu, zwłaszcza przy czterech bohaterach.')

add('Punkty zapisu i porażka drużyny', 'Heading 1')
h('Zapis przy wejściu do safe roomu')
add('Każde wejście drużyny do safe roomu automatycznie ustawia ten pokój jako ostatni punkt zapisu i nadpisuje poprzedni stan. Dotyczy to również ponownego wejścia do tego samego pokoju. Sam pobyt nie leczy i nie odnawia SP. Przed odkryciem pierwszego safe roomu punktem powrotu jest wejście do pałacu.')
add('GM zapisuje krótko: nazwę pokoju, pokonane grupy Shadows i bossów, otwarte przejścia, rozbrojone pułapki, zabrane skarby oraz rozwiązane przeszkody fabularne. Gracze odnotowują aktualne przedmioty, pieniądze, zawartość banku i postęp postaci. Wystarczą notatka i zdjęcia kart; nie trzeba odtwarzać każdej rozmowy. Wiedzy graczy o słabościach i zagadkach nie kasujemy.')
h('Powrót po porażce')
add('Gdy cała drużyna ma 0 HP, walka się kończy. Drużyna budzi się w ostatnim zapisanym safe roomie. Każda postać odzyskuje dokładnie połowę maksymalnego HP i połowę maksymalnego SP, zaokrąglając w dół; HP wynosi co najmniej 1. Znikają Down i wszystkie statusy bojowe. Przykład: maksimum 60 HP i 56 SP oznacza powrót z 30 HP i 28 SP; maksimum 35 HP i 31 SP daje 17 HP i 15 SP.')
add('Przywróć zapisany stan pałacu: wrogowie pokonani po zapisie wracają, a pokonani przed nim pozostają pokonani. Przejścia, pułapki i skarby również wracają do zapisanego stanu. Odtwórz zapisane przedmioty, pieniądze, bank i postęp postaci: zdobycze uzyskane po zapisie przepadają, a przedmioty zużyte po zapisie wracają. Wyjątkiem od odtworzenia kart są HP i SP, zawsze ustawiane na połowę maksimum, zamiast wartości z zapisu. Dzięki temu nie można zachowywać nagród z wielokrotnie resetowanych przeciwników.')
add('Przykład: przy zapisie w pokoju A grupa 1 jest pokonana, a grupy 2 i 3 żyją. Bohaterowie pokonują grupę 2, zużywają przedmiot i przegrywają z grupą 3. Po powrocie grupa 1 nadal nie istnieje, grupy 2 i 3 wracają w stanie z zapisu, zdobycz z grupy 2 przepada, a zużyty przedmiot wraca do ekwipunku. Gdyby po pokonaniu grupy 2 weszli ponownie do pokoju A, nowy zapis zachowałby jej pokonanie i aktualny ekwipunek.')
add('Respawn sam nie tworzy nowego zapisu ani nie daje kolejnego leczenia przy wychodzeniu i wchodzeniu. Zapis zostaje nadpisany przy następnym normalnym wejściu podczas dalszej eksploracji. Połowa zasobów jest łagodną konsekwencją porażki, nie ścisłą ochroną przed celowym wykorzystaniem respawnu; nie dokładamy teraz dodatkowej kary. Jeżeli taki wzorzec pojawi się przy stole, wrócimy do tej zasady po teście.')

add('Eksploracja poza walką', 'Heading 1')
add('Skradanie, tropienie, pułapki, zagadki i korzystanie z otoczenia należą do opisu sceny oraz decyzji GM. Nie tworzymy osobnych podsystemów, map z zasięgami ani list akcji eksploracji. Gdy pomysł działa bez istotnej niepewności, nie trzeba rzucać.')
add('Jeśli wynik jest niepewny i ma znaczenie, GM może poprosić o d20 bez bonusów przeciw trudności ustalonej przed rzutem. Pomocnicze wartości: DC 6 łatwe, DC 11 umiarkowane, DC 16 trudne. Wynik równy DC wystarcza. To wskazówki, nie obowiązkowe progi; GM opisuje możliwą konsekwencję porażki, np. hałas, utratę czasu lub uruchomienie pułapki. Nieudany rzut nie musi blokować jedynej drogi do dalszej historii.')
add('Rozwój przez EXP, tworzenie osobistej Persony, pojemność banku i rozpoczęcie gry dopracujemy w oddzielnym podręczniku gracza. Daily life i śledztwo będą kolejnym modułem. Technical pozostaje pominięte.')

doc.save(path)
check = Document(path)
body = '\n'.join(p.text for p in check.paragraphs)
assert len(check.tables) == 36
assert sum(len(t.rows)-1 for t in check.tables[-4:]) == 157
assert sum(len(t.rows)-1 for t in check.tables if len(t.columns)==6 and t.rows[0].cells[0].text=='Umiejętność') == 541
assert any(len(t.rows)==100 and t.cell(0,0).text=='Poziom' for t in check.tables)
assert 'Technical i jego dodatkowe obrażenia pozostają osobnym' not in body
assert 'wymagają osobnych zasad' not in body
print('OK: nowe rozdziały GM; zachowane 36 tabel, 541 skilli i traitów, 157 przedmiotów i poziomy 1–99.')
