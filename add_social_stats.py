from pathlib import Path
from docx import Document

root=Path(__file__).parent
path=root/'Persona_5_RPG_Zasady_0_2.docx'
doc=Document(path)
backup=root/'Persona_5_RPG_Zasady_0_2_przed_cechami_spolecznymi.docx'
if not backup.exists():backup.write_bytes(path.read_bytes())
assert not any(p.text=='Rozwój cech społecznych' for p in doc.paragraphs)
for p in doc.paragraphs:
    if p.text.startswith('Nazwy Wiedza, Odwaga, Empatia, Urok i Zręczność oraz'):
        p.text='Cechy społeczne mają zatwierdzoną strukturę czterech rang, opisaną w rozdziale Rozwój cech społecznych. Zdolności są roboczym balansem do pierwszych sesji; nie wymagamy dalszych podsystemów daily life.'
    elif 'Szczegółowe progi cech społecznych pozostają do ustalenia w podręczniku gracza.' in p.text:
        p.text=p.text.replace('Szczegółowe progi cech społecznych pozostają do ustalenia w podręczniku gracza.','Progi oraz zdolności cech opisuje rozdział Rozwój cech społecznych.')
    elif 'Zdolność oczekuje na zatwierdzenie systemu cech społecznych;' in p.text:
        p.text=p.text.split(' Zdolność oczekuje')[0]
    elif 'Szczegółowe zasady tworzenia postaci, cech społecznych i rozwoju przez EXP pozostają' in p.text:
        p.text=p.text.replace('tworzenia postaci, cech społecznych i rozwoju przez EXP','tworzenia postaci i rozwoju przez EXP')
anchor=next(p for p in doc.paragraphs if p.text=='Katalog bonusów Arkan')
def add(t,style=None):anchor.insert_paragraph_before(t,style)
add('Rozwój cech społecznych','Heading 1')
add('Bohater ma pięć cech: Wiedzę, Odwagę, Empatię, Urok i Zręczność. Każda zaczyna na randze 1 i może osiągnąć rangę 4. Są to osobne statystyki poza bojowym atakiem i Obroną; rozwijają codzienne kompetencje oraz odblokowują zdolności przydatne podczas wypraw.')
add('Progi i zdobywanie punktów','Heading 2')
add('Ranga 1: 0 punktów. Ranga 2: 3 punkty. Ranga 3: 7 punktów. Ranga 4: 12 punktów. To łączne progi dla każdej cechy osobno; punktów nie wydajemy po awansie. Jeden blok odpowiedniej aktywności daje 1 punkt wybranej cechy. Okazjonalna scena w szkole lub pracy może dać dodatkowy punkt według uznania GM.')
add('Przed blokiem wybierz nagrodę statystyczną: punkt jednej cechy albo postęp treningu HP/SP, zgodnie z aktywnością. Nie przyznajemy automatycznie obu. Znacząca scena relacji może dać postęp relacji równocześnie. Każdy uczestnik wspólnej aktywności wybiera własny pasujący rozwój.')
add('Testy poza walką','Heading 2')
add('Jeśli czynność ma niepewny wynik i istotne konsekwencje, GM może zastosować d20 + ranga pasującej cechy − 1 przeciw ustalonemu DC. Wynik równy DC wystarcza. Premia wynosi od +0 do +3. Pomocniczo: DC 6 łatwe, 11 umiarkowane, 16 trudne. Dla działań bez pasującej cechy pozostaje uznaniowy d20 bez bonusów; nie dokładamy drugiego rzutu do tego samego działania. Rutynowe aktywności rozwojowe nie wymagają testu.')
add('Wysoka cecha może dać łatwiejszy dostęp, dodatkowy szczegół albo oszczędność czasu. Podstawowe tropy i możliwość rozwijania relacji nie wymagają posiadania konkretnej rangi. Rozmówca zachowuje własną wolę: udany Urok lub Empatia nie zmuszają go do posłuszeństwa.')
add('Wspólna progresja zdolności','Heading 2')
add('Ranga 1 nie daje zdolności specjalnej. Ranga 2 daje jedno użycie zdolności w podanym okresie. Ranga 3 daje dwa użycia w tym samym okresie. Ranga 4 zachowuje dwa użycia i ulepsza ich działanie według opisu. Najwyżej jedno użycie danej zdolności na tę samą akcję lub Hold Up. Zdolności nie zajmują slotu skilla Persony i nie kosztują HP/SP.')
add('Użycia na walkę odnawiają się na początku nowej walki, nie przy wejściu do safe roomu. Użycia na wyprawę odnawiają się przy rozpoczęciu nowej wyprawy po powrocie do świata rzeczywistego; respawn po porażce ich nie odnawia. Poza reakcją obronną Odwagi zdolności wymagają możliwości działania. Informacyjne i wspierające efekty bez wskazanego kosztu akcji można deklarować w swojej zwykłej turze bez jej zużywania.')
stats=[
('Wiedza','Nauka, analiza i orientacja w świecie. Przykłady: czytanie, nauka, badanie dokumentów.',
 'Raz na walkę, bez akcji, poznajesz aktualne HP jednego widocznego wroga oraz nazwy jego umiejętności. Nie ujawnia to jego słabości ani pozostałych właściwości.',
 'Przy tym samym użyciu GM dodatkowo wskazuje, której umiejętności wróg zamierza użyć w następnej turze. Zmiana sytuacji, np. utrata celu lub brak zasobów, może wymusić inny ruch.'),
('Odwaga','Asertywność, opanowanie i podejmowanie ryzyka. Przykłady: trudna rozmowa, wystąpienie, zmierzenie się z lękiem.',
 'Raz na walkę automatycznie zdajesz własny rzut obronny przeciw statusowi po zobaczeniu wyniku. Nie wymaga to akcji i można zastosować jako reakcję na nakładany status.',
 'Możesz zamiast siebie ochronić jednego sojusznika po jego nieudanym rzucie. Nie usuwa to statusu, który został nałożony wcześniej, i nie chroni przed Down ani nokautem.'),
('Empatia','Rozumienie ludzi, cierpliwość i troska. Przykłady: pomoc komuś, wolontariat, opieka.',
 'Raz na walkę bez zużywania akcji usuwasz z jednego sojusznika Fear, Confuse albo Brainwash. Musisz móc działać; nie używasz tej zdolności na sobie.',
 'Możesz zamiast tego usunąć jeden dowolny z 12 zwykłych statusów. Nie usuwa Down, nokautu ani stanów specjalnych takich jak Rat lub Paint.'),
('Urok','Wyrażanie siebie, prezencja i obycie. Przykłady: teatr, taniec, spotkania towarzyskie.',
 'Raz na wyprawę, gdy prowadzisz negocjacje i pozyskujesz Personę, otrzymujesz również jeden podstawowy przedmiot oferowany w tym Hold Up. Walka kończy się normalnie.',
 'Zamiast dodatkowego przedmiotu możesz pozyskać drugą, inną Personę spośród leżących Shadows, jeśli masz miejsce w banku. Nie jest to druga kopia tego samego Shadows. Nagroda nie daje dodatkowej kolejki negocjacji; pierwszeństwo prowadzącego działa bez zmian.'),
('Zręczność','Precyzja, sprawność manualna i umiejętności praktyczne. Przykłady: majsterkowanie, gotowanie, szycie, instrument.',
 'Raz na walkę używasz jednego przedmiotu jako dodatkowej czynności obok zwykłej akcji w swojej turze. Przedmiot normalnie znika z ekwipunku. Nie jest to One More ani Baton Pass i nie uruchamia ich łańcucha.',
 'Gdy w ten sposób używasz przedmiotu na nieprzytomnym sojuszniku, możesz jednocześnie usunąć z siebie jeden zwykły status, jeśli możesz działać. Przedmiot musi legalnie działać na nieprzytomny cel, np. być wskrzeszający; zwykłe leczenie HP nadal nie wskrzesza. Na niższych rangach również można używać przedmiotu wskrzeszającego, ale bez dodatkowego usunięcia statusu.'),
]
for name,theme,base,upgrade in stats:
    add(name,'Heading 2');add(theme);add('Ranga 2: '+base);add('Ranga 3: dwa użycia zamiast jednego.');add('Ranga 4: '+upgrade)
add('Łączenie bonusów i pierwsze testy','Heading 2')
add('Zdolności cech mogą współdziałać z Arkanami, ale identyczne nagrody nie mnożą się: Urok i Słońce nie dają dwóch kopii tej samej dodatkowej nagrody przedmiotowej. Wybieramy korzystniejszą opcję dodatkowej nagrody. Osobna premia do ilości odnawianego HP/SP może działać na otrzymany przedmiot zgodnie ze swoim opisem. Urok nie pozwala skopiować unikatowego bossa ani ominąć wymogu wolnego miejsca w banku.')
add('Nazwy, progi oraz działanie zostały przyjęte jako baza systemu. Balans nie był jeszcze testowany przy stole. Szczególnie obserwujemy dodatkowe używanie przedmiotów, automatyczną obronę przeciw statusom i tempo zdobywania Person. Nie dokładamy na tym etapie dalszych podsystemów daily life; tworzenie bohatera, EXP, bank i rozwój osobistej Persony pozostają kolejnym etapem podręcznika gracza.')
doc.save(path)
c=Document(path)
text='\n'.join(p.text for p in c.paragraphs)
assert len(stats)==5 and len(c.tables)==60
assert sum(len(t.rows)-1 for t in c.tables[-4:])==157
assert sum(len(t.rows)-1 for t in c.tables if len(t.columns)==6 and t.cell(0,0).text=='Umiejętność')==541
assert any(len(t.rows)==100 and t.cell(0,0).text=='Poziom' for t in c.tables)
assert 'Dotychczasowy projekt progów i premii do rzutów nie został zatwierdzony' not in text
assert 'Zdolność oczekuje na zatwierdzenie' not in text
print('OK: 5 cech, rangi 1–4, progi 0/3/7/12; katalogi, Arkana i poziomy zachowane.')
