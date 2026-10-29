from pathlib import Path
from docx import Document

root=Path(__file__).parent
path=root/'Persona_5_RPG_Zasady_0_2.docx'
doc=Document(path)
backup=root/'Persona_5_RPG_Zasady_0_2_przed_wariantami_Arkan.docx'
if not backup.exists():backup.write_bytes(path.read_bytes())
assert not any(p.text=='Warianty relacji z bohaterami graczy' for p in doc.paragraphs)
for p in doc.paragraphs:
    if p.text.startswith('Osobistej zdolności nie kopiują pozostali'):
        p.text=('Osobistej zdolności nie kopiują pozostali przez relację z jej właścicielem. Relacje między bohaterami korzystają z osobnej ścieżki opisanej w rozdziale Warianty relacji z bohaterami graczy; zastępuje ona całą zwykłą ścieżkę bonusów danej Arkany. Relacje z NPC zachowują podstawowy katalog. Osobista zdolność nie rośnie automatycznie przez relację ze sobą. Świat pozostaje opcją finałową i nie jest dostępny przy tworzeniu postaci.')
    elif 'Odpoczynek nocny i jego odnowę HP/SP należy ustalić osobno' in p.text:
        p.text=p.text.split('Odpoczynek nocny i jego odnowę')[0]+'Wyjście z pałacu do świata rzeczywistego odnawia całe HP i SP wszystkich bohaterów oraz kompanów. Następna wyprawa zaczyna się z pełnymi zasobami. Wyjście kończy obecną wyprawę; powrót jest możliwy w kolejnym dostępnym bloku dziennym. Safe room, ucieczka z walki i respawn po porażce nie uruchamiają pełnej odnowy; respawn nadal daje połowę maksimum.'
anchor=next(p for p in doc.paragraphs if p.text=='Doprecyzowania czterech poprawionych Arkan')
def add(t,style=None):anchor.insert_paragraph_before(t,style)
add('Warianty relacji z bohaterami graczy','Heading 1')
add('Poniższa ścieżka zastępuje standardowe bonusy Arkany, gdy partnerem relacji jest inny bohater gracza. Każdy otrzymuje wariant Arkany drugiej osoby. Osobista zdolność partnera pozostaje jego własna. Relacje z NPC nadal korzystają z podstawowego katalogu.')
add('Ranga 2 daje jedno użycie opisanego efektu, ranga 4 dwa, a ranga 6 trzy. Nie zwiększamy równocześnie wartości liczbowych. Użycia odnawiają się raz na wyprawę, chyba że napisano raz na sesję. Dla efektu na sesję liczba użyć również wynosi odpowiednio 1, 2 lub 3. Najwyżej jedno użycie danego wariantu na jedno zdarzenie; nie sumujemy kilku aktywacji na jednym trafieniu. Wymieniony właściciel Arkany oznacza konkretnego partnera relacji. Efekty wymagające jego działania wymagają jego obecności.')
variants=[
('Głupiec','Gdy wrogowie zaskoczą drużynę, pierwszy wymierzony w ciebie atak otrzymuje −2 do trafienia. Deklaruj przed rzutem; jedna aktywacja na walkę.'),
('Mag','Użycie przez ciebie zwykłego przedmiotu odnawiającego HP może uleczyć również właściciela Arkany o 3 HP, do maksimum.'),
('Kapłanka','Gdy twój atak ujawni nieznane wcześniej drużynie Null, Drain lub Repel, odzyskujesz zapłacony za ten skill SP. Skutek ataku nadal występuje. Jedna refundacja na akcję, również obszarową.'),
('Cesarzowa','Po otrzymaniu leczenia od właściciela Arkany zyskujesz redukcję następnych obrażeń z ataku o 2 w tej walce, po mnożnikach, do minimum 0. Ochrona nie kumuluje się sama ze sobą.'),
('Cesarz','Po trafionym ataku właściciela Arkany twój następny atak przeciw temu samemu celowi zadaje +3 obrażenia, jeżeli sam zadał co najmniej 1 obrażenie. Premia dotyczy jednego celu i wygasa z końcem walki.'),
('Hierofant','Podczas wieczornego spotkania z właścicielem Arkany możesz przerzucić jeden nieudany test cechy społecznej w tej scenie. Raz na sesję. Zdolność oczekuje na zatwierdzenie systemu cech społecznych; do tego czasu działa na uznaniowy test d20 związany ze sceną poza walką.'),
('Kochankowie','Gdy otrzymasz Baton Pass od właściciela Arkany, możesz usunąć z siebie Dizzy albo Forget przed wykonaniem dodatkowej akcji.'),
('Rydwan','Gdy masz najwyżej połowę maksymalnego HP, jeden twój podstawowy atak zadaje +4 obrażenia jednemu celowi, jeśli sam zadał co najmniej 1 obrażenie.'),
('Sprawiedliwość','Po tym, jak wróg zrani właściciela Arkany, otrzymujesz +2 do następnego rzutu ataku przeciw temu wrogowi w tej walce. Deklaruj aktywację przed tym rzutem.'),
('Pustelnik','Przed opuszczeniem safe roomu GM przypomina drużynie jedną już zdobytą informację, która może pomóc w dalszej eksploracji. Nie ujawnia nowej poszlaki.'),
('Koło Fortuny','Możesz przerzucić własny rzut na ucieczkę drużyny. Drugi wynik obowiązuje. Nie daje to dodatkowej próby ucieczki w tej rundzie.'),
('Siła','Na początku własnej zwykłej tury możesz zakończyć Rage albo Hunger bez zużywania akcji.'),
('Wisielec','Gdy właściciel Arkany przejmie twoje obrażenia, odzyskujesz 1 SP, do maksimum.'),
('Śmierć','Używając przedmiotu wskrzeszającego na właścicielu Arkany, możesz jednocześnie usunąć z siebie jeden z 12 zwykłych statusów, jeśli możesz działać.'),
('Umiarkowanie','Pierwszy użyty na tobie w danym pobycie w safe roomie przedmiot odnawiający SP przywraca o 1 SP więcej. Jeden taki bonus na pobyt, do maksimum SP; wizyta nie odnawia użyć zdolności.'),
('Diabeł','Przed rozmową śledczą GM wskazuje, jaką przysługą lub informacją można zainteresować rozmówcę. Nie gwarantuje to jego współpracy. Raz na sesję.'),
('Wieża','Po zadaniu obrażeń wrogowi możesz usunąć z niego jeden aktywny bonus ataku albo Obrony. Nie usuwa naturalnych statystyk, Guard ani właściwości żywiołowych.'),
('Gwiazda','Na początku swojej zwykłej tury możesz odłożyć ją bezpośrednio za turę właściciela Arkany, jeśli jeszcze nie działał w tej rundzie. Nie zmienia to kolejnych rund ani bloków surprise. Do wykonania odłożonej tury utrzymują się twoje dotychczasowe liczniki i Guard; rozpatrujesz je dopiero na jej faktycznym początku.'),
('Księżyc','Po zdobyciu poszlaki zapytaj GM: Co tutaj jest obserwacją, a co naszą interpretacją? GM porządkuje znane fakty bez ujawniania rozwiązania. Raz na sesję.'),
('Słońce','Gdy właściciel Arkany wybiera przedmiot w negocjacjach, ty odzyskujesz 1 SP, do maksimum.'),
('Sąd','Gdy właściciel Arkany zostanie znokautowany, twój następny przedmiot wskrzeszający użyty na nim przywraca dodatkowe 5 HP, do maksimum.'),
('Wiara','Po własnym pudle otrzymujesz +2 do następnego rzutu obronnego przeciw statusowi w tej walce. Bonus nie kumuluje się sam ze sobą.'),
('Doradca','Własna akcja uspokojenia usuwa z ciebie Fear, Confuse albo Despair bez SP i rzutu. Możesz wybrać ją mimo ograniczenia działania lub wymuszonej akcji wynikających z tego jednego usuwanego statusu. Inne blokujące statusy nadal obowiązują.'),
]
for name,text in variants:
    add(name,'Heading 2');add(text)
add('Świat','Heading 2')
add('Pozostaje nagrodą finałową przygotowaną dla konkretnej drużyny. Nie ma standardowego wariantu relacji między bohaterami ani początkowego wyboru tej Arkany.')
add('Zakres cech społecznych','Heading 2')
add('Nazwy Wiedza, Odwaga, Empatia, Urok i Zręczność oraz odpowiadające im aktywności pozostają propozycją. Dotychczasowy projekt progów i premii do rzutów nie został zatwierdzony: potrzebny jest mocniejszy wpływ tych cech na rozgrywkę albo rezygnacja z osobnych statystyk. Nie stosujemy jeszcze ich rang jako obowiązkowych wymagań ani nie naliczamy ich według niezatwierdzonej tabeli.')
doc.save(path)
c=Document(path)
assert len(variants)==23
assert len(c.tables)==60
assert sum(len(t.rows)-1 for t in c.tables[-4:])==157
assert sum(len(t.rows)-1 for t in c.tables if len(t.columns)==6 and t.cell(0,0).text=='Umiejętność')==541
assert any(len(t.rows)==100 and t.cell(0,0).text=='Poziom' for t in c.tables)
print('OK: 23 warianty i Świat; pełna odnowa po wyjściu; katalogi i tabela poziomów zachowane.')
