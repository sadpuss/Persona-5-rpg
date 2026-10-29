from pathlib import Path
from docx import Document

root=Path(__file__).parent
path=root/'Persona_5_RPG_Zasady_0_2.docx'
doc=Document(path)
old=next(p for p in doc.paragraphs if p.text.startswith('1. Ustal kolejność bohaterów przed walką.'))
old.text=('1. Ustal, czy jedna ze stron zaskoczyła drugą, a następnie wykonaj rzuty inicjatywy według zasad poniżej. '
          'Każdy uczestnik rzuca raz d20 bez bonusów; wyższy wynik oznacza wcześniejszą turę. '
          'Kolejność ustalamy na początku walki i zachowujemy w następnych rundach.')

anchor=next(p for p in doc.paragraphs if p.text=='Leczenie i wsparcie')
def insert(text,style=None):return anchor.insert_paragraph_before(text,style)
insert('Inicjatywa bez zaskoczenia','Heading 2')
insert('Wszyscy bohaterowie i wszyscy przeciwnicy rzucają po jednym d20, bez żadnych premii. '
       'Wyniki tworzą jedną wspólną kolejkę od najwyższego do najniższego, niezależnie od strony. '
       'Tury bohaterów i Shadows mogą się przeplatać. Każdy uczestnik ma jedną zwykłą turę w rundzie.')
insert('Surprise gdy bohaterowie zaskoczą wrogów','Heading 2')
insert('Najpierw działają wszyscy bohaterowie, a dopiero po nich wszyscy przeciwnicy. '
       'Każdy rzuca d20 bez bonusów, ale porównujemy wyniki wyłącznie wewnątrz jego strony. '
       'Wysoki wynik Shadow nie pozwala mu wyprzedzić bohatera. Do strony bohaterów należą również ich walczący kompanowie prowadzeni przez GM.')
insert('Surprise gdy wrogowie zaskoczą bohaterów','Heading 2')
insert('Najpierw działają wszyscy przeciwnicy, a dopiero po nich wszyscy bohaterowie. '
       'Każdy rzuca d20 bez bonusów; wyniki ustalają kolejność wewnątrz każdej strony. '
       'Wysoki wynik bohatera nie pozwala mu wyprzedzić przeciwnika z pierwszego bloku.')
insert('Remisy i czas obowiązywania','Heading 2')
insert('Doprecyzowanie: remis rozstrzygają dodatkowym d20 tylko remisujące osoby. '
       'Dogrywka ustala wyłącznie ich kolejność w zajmowanym miejscu, nie zastępuje pierwotnej inicjatywy. '
       'Przy zaskoczeniu nie ma remisu między stronami, bo ich bloki są już ustalone. '
       'Nie przerzucamy inicjatywy co rundę. W tej wersji kolejność bloków z zaskoczenia pozostaje przez całą walkę.')
insert('Surprise jest sposobem rozpoczęcia walki i ustawienia kolejności, a nie dolegliwością. '
       'Nie dodaje osobnej rundy, nie odbiera tur zaskoczonej stronie i samo nie daje dodatkowych obrażeń. '
       'Atak rozpoczynający zasadzkę rozgrywamy jako akcję w pierwszej turze, nie jako darmowy atak przed inicjatywą. '
       'One More i Baton Pass nadal mogą dawać natychmiastowe dodatkowe akcje poza zwykłą kolejką, '
       'ale nie przesuwają kolejnej zwykłej tury żadnej postaci.')
insert('Kiedy występuje zaskoczenie','Heading 2')
insert('GM ustala zaskoczenie przed rzutami na podstawie sytuacji: ukrycia, przygotowanej zasadzki i tego, '
       'czy druga strona dostrzegła zagrożenie na czas. Nie dodajemy jeszcze osobnego testu skradania lub percepcji. '
       'Jeśli obie strony są świadome zagrożenia albo żadna nie zdobyła wyraźnej przewagi zaskoczenia, '
       'stosujemy wspólną kolejkę bez surprise. W jednej walce najwyżej jedna strona zaczyna z surprise.')
insert('Przykład tej samej inicjatywy w trzech sytuacjach','Heading 2')
insert('Rzuty: Zorro 8, Captain Kidd 17, Shadow A 19, Shadow B 4. '
       'Bez surprise: Shadow A → Kidd → Zorro → Shadow B. '
       'Bohaterowie zaskakują: Kidd → Zorro → Shadow A → Shadow B. '
       'Wrogowie zaskakują: Shadow A → Shadow B → Kidd → Zorro. '
       'Ustalona kolejność powtarza się w kolejnych rundach, z pominięciem pokonanych uczestników.')
for p in doc.paragraphs:
    if p.text.startswith('Wersja 0.2'):p.text='Wersja 0.2 • aktualizacja 28 października 2026 • inicjatywa i surprise'
backup=root/'Persona_5_RPG_Zasady_0_2_przed_inicjatywa.docx'
if not backup.exists():backup.write_bytes(path.read_bytes())
doc.save(path)
check=Document(path)
text='\n'.join(p.text for p in check.paragraphs)
assert 'Inicjatywa i zasadzki nie mają jeszcze osobnych zasad' not in text
assert all(s in text for s in ['Inicjatywa bez zaskoczenia','Surprise gdy bohaterowie zaskoczą wrogów','Surprise gdy wrogowie zaskoczą bohaterów'])
assert len(check.tables)==36
assert sum(len(t.rows)-1 for t in check.tables[-4:])==157
assert sum(len(t.rows)-1 for t in check.tables if len(t.columns)==6 and t.rows[0].cells[0].text=='Umiejętność')==541
print('OK: inicjatywa i surprise dodane; 541 skilli i traitów, 157 przedmiotów i moduł statusów zachowane')
