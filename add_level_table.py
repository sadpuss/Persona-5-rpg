from copy import deepcopy
from pathlib import Path
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

root=Path(__file__).parent
path=root/'Persona_5_RPG_Zasady_0_2.docx'
doc=Document(path)
table=next(t for t in doc.tables if [c.text for c in t.rows[0].cells]==['Poziom','Maksymalne HP','Maksymalne SP'])
template=deepcopy(table.rows[1]._tr)
for row in list(table.rows)[1:]:table._tbl.remove(row._tr)
for level in range(1,100):
    table._tbl.append(deepcopy(template))
    row=table.rows[-1]
    for cell,value in zip(row.cells,[level,34+level,30+level]):
        par=cell.paragraphs[0]
        for run in par.runs:run.text=''
        if par.runs:par.runs[0].text=str(value)
        else:par.add_run(str(value))
        par.alignment=WD_ALIGN_PARAGRAPH.CENTER
for par in doc.paragraphs:
    if par.text.startswith('Wersja 0.2'):
        par.text='Wersja 0.2 • aktualizacja 28 października 2026'
    elif par.text.startswith('Maksymalne HP = 34 + L.'):
        par.text=('Maksymalne HP = 35 + (L − 1) = 34 + L. Maksymalne SP = 31 + (L − 1) = 30 + L. '
                  'L oznacza poziom bohatera od 1 do 99. Nowa postać na poziomie 1 zaczyna z pełnymi zasobami: '
                  '35/35 HP i 31/31 SP. Za każdy kolejny poziom otrzymuje +1 maksymalnego HP oraz +1 maksymalnego SP. '
                  'Na poziomie 26 daje to 60 HP i 56 SP, a na poziomie 99: 133 HP i 129 SP. '
                  'Awans nie odnawia bieżących zasobów; zwiększa tylko ich maksima. Poziom 99 jest limitem tej tabeli.')
    elif par.text.startswith('Ten wzór jest punktem startowym'):
        par.text=('Tabela obejmuje wszystkie poziomy 1–99 i podaje wartości bazowe bez profili, ekwipunku, '
                  'pasywów ani innych stałych premii. Obowiązuje ten sam przyrost +1 HP i +1 SP na każdym awansie. '
                  'Pełna tabela jest przedłużeniem wzoru, nie potwierdzeniem balansu wszystkich poziomów. '
                  'Wzór pozostaje propozycją; szczególnie poziomy 31–99 i umiejętności endgame wymagają dalszych testów.')
    elif par.text.startswith('Nowa propozycja wersji 0.2.'):
        par.text=('Propozycja wersji 0.2 z tabelą poziomów 1–99. Wartości odnoszą się do bohatera, '
                  'a nie osobnej puli przywoływanej Persony. Dotychczasowe próby około poziomu 26 nadal '
                  'korzystają z tych samych 60 HP i 56 SP.')
backup=root/'Persona_5_RPG_Zasady_0_2_przed_tabela_poziomow.docx'
if not backup.exists():backup.write_bytes(path.read_bytes())
doc.save(path)
check=Document(path)
t=next(t for t in check.tables if t.rows[0].cells[0].text=='Poziom')
assert len(t.rows)==100
for lv,row in enumerate(t.rows[1:],1):
    assert [int(c.text) for c in row.cells]==[lv,34+lv,30+lv]
assert sum(len(t.rows)-1 for t in check.tables[-16:])==541
print('OK: 99 poziomów; poziom 1 = 35/31; poziom 26 = 60/56; poziom 99 = 133/129; katalog 541 wpisów zachowany')
