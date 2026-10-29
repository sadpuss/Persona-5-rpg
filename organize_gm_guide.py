from pathlib import Path
from copy import deepcopy
from collections import Counter
import hashlib, json, re
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER

ROOT=Path(__file__).parent
SRC=ROOT/'Persona_5_RPG_Zasady_0_2.docx'
OUT=ROOT/'Persona_5_RPG_Podrecznik_GM_0_3.docx'
source_hash=hashlib.sha256(SRC.read_bytes()).hexdigest()
src=Document(SRC)
doc=Document(SRC)
body=doc.element.body
original_tables=[[ [c.text for c in row.cells] for row in t.rows] for t in src.tables]
blocks=[]
current=None
for node in list(body):
    if node.tag==qn('w:sectPr'):continue
    para=Paragraph(node,doc) if node.tag==qn('w:p') else None
    if para is not None and para.style.name.startswith('Heading'):
        current={'title':para.text,'nodes':[],'used':False}
        blocks.append(current)
    if current is not None:current['nodes'].append(deepcopy(node))

for node in list(body):
    if node.tag!=qn('w:sectPr'):body.remove(node)

def p(text='',style=None):return doc.add_paragraph(text,style)
def heading(text,level=1):return doc.add_heading(text,level)
def find(title,occurrence=0):
    candidates=[b for b in blocks if b['title']==title]
    if len(candidates)<=occurrence:raise ValueError(('Missing',title,occurrence))
    b=candidates[occurrence]
    assert not b['used'],('Already used',title,occurrence)
    b['used']=True
    return b
def put(title,level=2,rename=None,occurrence=0):
    b=find(title,occurrence)
    for i,node in enumerate(b['nodes']):
        if node.tag==qn('w:p'):
            par=Paragraph(node,doc)
            if not par.text.strip():continue
            for br in list(node.iter(qn('w:br'))):
                if br.get(qn('w:type'))=='page':br.getparent().remove(br)
            par.paragraph_format.page_break_before=False
            if i==0:
                par.style=doc.styles[f'Heading {level}']
                if rename:par.text=rename
        body.insert(len(body)-1,node)
def skip(title,occurrence=0):find(title,occurrence)
def chapter(title):heading(title,1)

# Preserve established typography while supplying a consistent hierarchy.
for name,size in [('Title',28),('Heading 1',18),('Heading 2',13),('Heading 3',11)]:
    st=doc.styles[name]
    st.font.name='Calibri';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0)
    st.paragraph_format.keep_with_next=True
    st.paragraph_format.space_before=Pt(12 if name!='Title' else 0)
    st.paragraph_format.space_after=Pt(6)
    pr=st.element.get_or_add_pPr()
    for border in list(pr.findall(qn('w:pBdr'))):pr.remove(border)
doc.styles['Heading 1'].paragraph_format.page_break_before=True
doc.styles['Normal'].paragraph_format.widow_control=True

p('Persona 5 RPG', 'Title')
p('Podręcznik dla GM','Subtitle')
p('Wersja 0.3 • uporządkowany układ • 28 października 2026')
p('Zasady walki, eksploracji pałaców i daily life do prowadzenia przy stole. Rozdziały 1–10 zawierają zasady oraz wskazówki dla GM; rozdziały 11–13 służą jako katalogi do szybkiego sprawdzania wartości. Tworzenie postaci, EXP i szczegółowy rozwój Person będą opisane w osobnym podręczniku gracza.')
p('Układ zmieniono na podstawie wersji 0.2. Liczby i zaakceptowane mechaniki zachowano; poprawiono hierarchię, odsyłacze i starsze notatki o zakresie projektu. Balans nadal wymaga gry próbnej.')
p('Nawigacja: spis treści prowadzi do rozdziałów i podrozdziałów. W Wordzie można również otworzyć panel Nawigacja, aby wyszukiwać nagłówki, w tym poszczególne Arkana. Po zmianie układu stron kliknij spis prawym przyciskiem i wybierz Aktualizuj pole → Aktualizuj cały spis. W Wordzie przejście przez odnośnik może wymagać Ctrl + kliknięcie.')
toc_title=p('Spis treści','Title')
toc_title.paragraph_format.page_break_before=True
toc_start=p()
toc_end=p()

chapter('1 Podstawy systemu')
put('Jak czytać dokument')
put('Najważniejsze założenia')
put('Podstawowe definicje')
put('Jedna osobista Persona')
put('Rozwój przez EXP')

chapter('2 Przebieg walki i dostępne akcje')
put('Walka krok po kroku',2,rename='Przygotowanie i kolejność rozstrzygania')
put('Parametry do rozpoczęcia prób')
put('Kolejność i akcje')
for title in ['Inicjatywa bez zaskoczenia','Surprise gdy bohaterowie zaskoczą wrogów','Surprise gdy wrogowie zaskoczą bohaterów','Remisy i czas obowiązywania','Kiedy występuje zaskoczenie','Przykład tej samej inicjatywy w trzech sytuacjach']:
    put(title,3)
put('Pozycja i zasięg')
put('Guard')
put('Ucieczka drużyny')
skip('Obrona ucieczka i zakończenie walki')

chapter('3 Obrażenia leczenie i koszty umiejętności')
skip('Obrażenia i właściwości')
put('Wspólna skala obrażeń')
put('Właściwość celu wobec danego typu ataku')
put('Przykład',3,rename='Przykład mnożników obrażeń')
put('Bestiariusz gracza',2,rename='Odkrywanie właściwości przeciwników')
put('Leczenie i wsparcie')
put('Nokaut')
put('Koszty i katalog umiejętności',2,rename='Podstawowe umiejętności i ich koszty')
put('Czas działania',3,rename='Czas działania premii i osłabień')
put('Czego jeszcze nie wyceniamy',3,rename='Granice adaptacji umiejętności')

chapter('4 Down One More i Baton Pass')
skip('One More i Baton Pass')
for title in ['Down','One More','Łańcuch dodatkowych akcji','Baton Pass','Przykład dwóch bohaterów','Zakres wersji']:put(title)

chapter('5 Hold Up negocjacje i All Out Attack')
for title in ['Hold Up','Kto prowadzi negocjacje','Automatyczna nagroda za negocjacje','All Out Attack']:put(title)

chapter('6 Statusy i ich usuwanie')
put('Nakładanie statusów',2,rename='Zasady nakładania statusów')
for title in ['Jeden rzut obronny','Dwa rodzaje działania']:put(title,3)
put('Czas działania i ochrona przed blokowaniem')
for title in ['Zwykłe tury zamiast dodatkowych akcji','Powrót do działania','Nakładanie i usuwanie']:put(title,3)
put('Statusy żywiołowe')
put('Odporność na żywioł a odporność na status',3)
put('Sen dezorientacja i ograniczenia działania')
put('Szał głód i rozpacz')
put('Resist Null i premie do szans',3)
put('Leczenie statusów i stany specjalne')
put('Przykłady działania statusów')
for title in ['Agilao i Burn','Dormina i Sleep','Headbutt i Forget','Despair i własny przedmiot','Zakres dalszych testów']:put(title,3)

chapter('7 Eksploracja pałacu i punkty zapisu')
put('Eksploracja poza walką',2,rename='Skradanie pułapki i testy uznaniowe')
put('Safe room i zasoby')
heading('Wyjście do świata rzeczywistego',2)
p('Wyjście z pałacu odnawia całe HP i SP bohaterów oraz kompanów i kończy obecną wyprawę. Następna wyprawa zaczyna się z pełnymi zasobami w kolejnym dostępnym bloku dziennym. Nie dotyczy to safe roomu, ucieczki z jednej walki ani respawnu po porażce. Respawn przywraca połowę maksymalnego HP i SP według zasad poniżej.')
skip('Punkty zapisu i porażka drużyny')
put('Zapis przy wejściu do safe roomu')
put('Powrót po porażce')

chapter('8 Daily life aktywności i cechy społeczne')
put('Daily life i relacje',2,rename='Kalendarz codzienności')
put('Dwa bloki czasu')
put('Aktywności i własne pomysły')
put('Prowadzenie bez dodatkowych podsystemów')
put('Rozwój cech społecznych',2,rename='Pięć cech społecznych')
for title in ['Progi i zdobywanie punktów','Testy poza walką','Wspólna progresja zdolności']:put(title,3)
for title in ['Wiedza','Odwaga','Empatia','Urok','Zręczność']:put(title,3)
put('Łączenie bonusów i pierwsze testy',3)
skip('Zakres cech społecznych')

chapter('9 Relacje osobiste Arkana i ich bonusy')
put('Relacje od rangi 1 do 6')
put('Wspólne aktywności bohaterów')
put('Osobista Arkana bohatera')
put('Wspólne zasady bonusów')
put('Katalog bonusów Arkan',2,rename='Katalog bonusów relacji z NPC')
arcana_blocks=[b for b in blocks if ' — ' in b['title'] and any(n in b['title'] for n in ['Fool','Magician','Priestess','Empress','Emperor','Hierophant','Lovers','Chariot','Justice','Hermit','Fortune','Strength','Hanged Man','Death','Temperance','Devil','Tower','Star','Moon','Sun','Judgement','Faith','Councillor','World'])]
assert len(arcana_blocks)==24
for b in arcana_blocks:put(b['title'],3)
put('Doprecyzowania czterech poprawionych Arkan',3,rename='Szczegółowe zasady Głupca Sprawiedliwości Pustelnika i Księżyca')
put('Warianty relacji z bohaterami graczy')
for title in ['Głupiec','Mag','Kapłanka','Cesarzowa','Cesarz','Hierofant','Kochankowie','Rydwan','Sprawiedliwość','Pustelnik','Koło Fortuny','Siła','Wisielec','Śmierć','Umiarkowanie','Diabeł','Wieża','Gwiazda','Księżyc','Słońce','Sąd','Wiara','Doradca','Świat']:put(title,3)

chapter('10 Przygotowanie przeciwników i prowadzenie prób')
skip('Persony eksploracja i przeciwnicy')
put('Wyliczanie zasobów przeciwników',2,rename='Projektowanie zasobów przeciwnika')
for title in ['HP z długości starcia','SP według liczby użyć','Kolejność strojenia']:put(title,3)
put('Przykładowe karty przeciwników')
skip('Prowadzenie prób i dalsze ustalenia')
put('Co sprawdzać przy stole')
put('Granice dotychczasowych symulacji')
put('Kolejne decyzje',2,rename='Zakres przyszłego podręcznika gracza i dodatków')

chapter('11 HP i SP bohaterów oraz tabela poziomów')
put('Proponowane wzory na HP i SP',2,rename='Wartości bazowe i zakres testów')
put('Bohaterowie',2,rename='Wzór oraz poziomy od 1 do 99')
put('Opcjonalne profile')
put('Dlaczego nie jeden dzielnik z P5R')

chapter('12 Katalog umiejętności i traitów P5R')
put('Katalog umiejętności P5R',2,rename='Zakres katalogu')
put('Jak czytać koszty')
put('Reguły nowych propozycji kosztów')
for title in ['Katalog Physical','Katalog Gun','Katalog Fire','Katalog Ice','Katalog Electricity','Katalog Wind','Katalog Psy','Katalog Nuclear','Katalog Bless','Katalog Curse','Katalog Almighty','Katalog Statusy','Katalog Leczenie','Katalog Wsparcie','Katalog Pasywne','Katalog Traity']:put(title)

chapter('13 Przedmioty odnawiające HP i SP')
put('Przedmioty odnawiające HP i SP',2,rename='Zakres katalogu przedmiotów')
put('Przelicznik')
put('Zasady używania')
put('Skutki dodatkowe przedmiotów')
put('Wskrzeszanie jako nowa propozycja',2,rename='Wskrzeszanie przedmiotami')
put('Czytanie tabel')
for title in ['Przedmioty przywracające HP','Przedmioty przywracające SP','Przedmioty przywracające oba zasoby','Przedmioty wskrzeszające']:put(title)

chapter('14 Źródła i zakres adaptacji')
put('Źródła odniesienia',2,rename='Inspiracje i przykładowe Persony')
put('Źródła odniesienia P5R',2,rename='Statusy i dane P5R')
put('Źródło katalogu',2,rename='Katalog przedmiotów')
heading('Katalog umiejętności i lista Arkan',2)
p('Źródłem katalogu umiejętności jest aqiu384 megaten-fusion-tool, publiczna baza na licencji Unlicense: https://github.com/aqiu384/megaten-fusion-tool/tree/master/src/app/p5/data . Połączono wpisy P5 z poprawkami Royal. Lista Arkan: Persona 5 Royal Confidant List, SAMURAI GAMERS, https://samurai-gamers.com/persona-5/confidants-list-schedule-guide/ . Mechaniki, sześć rang relacji, warianty Arkan i cechy społeczne są naszym homebrew.')

unused=[b['title'] for b in blocks if not b['used']]
assert not unused,unused

# Editorial cleanup of obsolete planning notes and cross-references.
for par in doc.paragraphs:
    t=par.text
    if t.startswith('Ustalenie oznacza przyjęty kierunek projektu.'):
        par.text='Ustalenie oznacza przyjętą zasadę systemu. Wartość testowa jest roboczą liczbą do sprawdzenia przy stole; wcześniejsze symulacje nie potwierdzają balansu całego katalogu. Brak liczby lub znacznik adaptacji oznacza, że efekt wymaga osobnego opisu przed użyciem. Najnowsze rozdziały opisują obowiązujące zasady, a historyczne próby służą tylko jako przykłady.'
    elif 'Hold Up, negocjacje i All-Out Attack działają według kolejnego rozdziału.' in t:
        par.text=t.replace('według kolejnego rozdziału','według rozdziału 5')
    elif 'rozdział Nakładanie statusów' in t:
        par.text=t.replace('rozdział Nakładanie statusów','rozdział 6 Statusy i ich usuwanie')
    elif 'szczegóły opisuje rozdział Punkty zapisu i porażka drużyny.' in t:
        par.text=t.replace('szczegóły opisuje rozdział Punkty zapisu i porażka drużyny.','szczegóły podano w dalszej części tego rozdziału.')
    elif 'moduł Daily life i relacje' in t or 'rozdział Daily life i relacje' in t:
        par.text=t.replace('moduł Daily life i relacje','rozdziały 8 i 9').replace('rozdział Daily life i relacje','rozdziały 8 i 9')
    elif t.startswith('Przed sceną GM jasno określa'):
        pass
    elif t.startswith('Podstawowa wskazówka konieczna do dalszej gry'):
        par.text='Podstawowa wskazówka konieczna do dalszej gry nie wymaga posiadania konkretnej Arkany. Jej zdobycie może kosztować czas, przysługę lub wymagać innego podejścia. Relacje nie spadają automatycznie przez brak codziennych spotkań. Wyjście z pałacu i odnowienie HP/SP opisano w rozdziale 7.'
    elif t.startswith('Na rangach 2, 4 i 6 każdy bohater otrzymuje bonus Arkany drugiej osoby.'):
        par.text=t.replace('bonus Arkany drugiej osoby.','wariant bonusu Arkany drugiej osoby według katalogu relacji między bohaterami, zamiast ścieżki NPC.')
    elif t.startswith('Obudź i Otrzeźwij to jedna akcja'):
        par.text=t.replace('wymagająca możliwości dotarcia do celu','bez osobnego pomiaru zasięgu zgodnie z abstrakcją walki')
    elif t.startswith('Kolejność obrażeń:'):
        par.text=t.replace('→ Weak/Resist. Zaokrąglaj w dół po mnożniku, minimum 0.','→ Weak/Resist → Guard, jeśli działa. Zaokrąglaj w dół na końcu, minimum 0.')
    elif t.startswith('Testowy przedmiot +20 SP'):
        par.text=t.replace('może teraz odpowiadać Chewing Soul','odpowiada w katalogu Chewing Soul')
    elif t.startswith('Safe room jest bezpiecznym miejscem powrotu.'):
        par.text=par.text.replace('Nie nadaliśmy mu jeszcze ceny ani zasad dostępności.','W katalogu odpowiada mu Chewing Soul. Ceny i dostępność ustala GM dla przygody.')
    elif t.startswith('Odniesienie dla listy i angielskich nazw Arkan:'):
        par.text='Listę źródeł dla Arkan i danych P5R zebrano w rozdziale 14. Wszystkie bonusy relacji są naszym homebrew.'

# Bring the old pending-work table up to date without changing its layout.
pending=next(t for t in doc.tables if t.cell(0,0).text=='Obszar')
pending_rows=[
('Postać i awans','Tworzenie postaci, początkowy atak i Obrona, progi EXP oraz wybory przy awansie. Bazowe HP/SP i ich przyrost są już opisane w rozdziale 11.'),
('Rozwój Persony','Budżet tworzenia, ograniczenia właściwości, dostępność skilli i traitów, pojemność banku oraz receptury i koszty skill cards.'),
('Opcjonalne rozszerzenia walki','Krytyki, szczegółowe multi hit, instakill i pozostałe unikatowe efekty katalogu. Technical celowo pominięto. Guard, ucieczka, statusy, Hold Up i porażka mają już zasady.'),
('Daily life','Moduł podstawowy ukończony: bloki, trening, relacje, Arkana i cechy społeczne. Potrzebne są testy tempa rozwoju, nie kolejny podsystem.'),
('Przygotowanie GM','Dostępność i ceny zapasów w konkretnej przygodzie, testy składu drużyny oraz opcjonalny alarm. Przykładowe wzory spotkań są w rozdziale 10.')]
for row,values in zip(pending.rows[1:],pending_rows):
    for cell,value in zip(row.cells,values):
        cell.text=value
        for par in cell.paragraphs:
            for run in par.runs:run.font.size=Pt(9)

# Ensure readable table pagination and preserve every original data row.
for table in doc.tables:
    first=table.rows[0]._tr.get_or_add_trPr()
    if first.find(qn('w:tblHeader')) is None:first.append(OxmlElement('w:tblHeader'))
    for row in table.rows:
        pr=row._tr.get_or_add_trPr()
        if pr.find(qn('w:cantSplit')) is None:pr.append(OxmlElement('w:cantSplit'))

# Number headings and bookmark all navigation targets.
chapter_no=0;sub_no=0;subsub_no=0
nav=[];bookmark_id=1000
for par in doc.paragraphs:
    style=par.style.name
    if style not in ('Heading 1','Heading 2','Heading 3'):continue
    level=int(style[-1])
    if level==1:
        chapter_no+=1;sub_no=0;subsub_no=0
    elif level==2:
        sub_no+=1;subsub_no=0
        par.text=f'{chapter_no}.{sub_no} '+par.text
    else:
        subsub_no+=1
        par.text=f'{chapter_no}.{sub_no}.{subsub_no} '+par.text
    bookmark_id+=1
    name=f'GM_{bookmark_id}'
    start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),str(bookmark_id));start.set(qn('w:name'),name)
    end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),str(bookmark_id))
    par._p.insert(1 if par._p.pPr is not None else 0,start);par._p.append(end)
    if level<=2:nav.append((level,par.text,name))

def field_run(parent,code,result='—'):
    r=OxmlElement('w:r');b=OxmlElement('w:fldChar');b.set(qn('w:fldCharType'),'begin');b.set(qn('w:dirty'),'true');r.append(b);parent.append(r)
    r=OxmlElement('w:r');i=OxmlElement('w:instrText');i.set(qn('xml:space'),'preserve');i.text=' '+code+' ';r.append(i);parent.append(r)
    r=OxmlElement('w:r');s=OxmlElement('w:fldChar');s.set(qn('w:fldCharType'),'separate');r.append(s);parent.append(r)
    r=OxmlElement('w:r');t=OxmlElement('w:t');t.text=result;r.append(t);parent.append(r)
    r=OxmlElement('w:r');e=OxmlElement('w:fldChar');e.set(qn('w:fldCharType'),'end');r.append(e);parent.append(r)

# A real Word TOC, with immediately usable cached internal links.
begin=OxmlElement('w:r');fc=OxmlElement('w:fldChar');fc.set(qn('w:fldCharType'),'begin');fc.set(qn('w:dirty'),'true');begin.append(fc);toc_start._p.append(begin)
r=OxmlElement('w:r');instr=OxmlElement('w:instrText');instr.set(qn('xml:space'),'preserve');instr.text=' TOC \\o "1-2" \\h \\z \\u ';r.append(instr);toc_start._p.append(r)
r=OxmlElement('w:r');fc=OxmlElement('w:fldChar');fc.set(qn('w:fldCharType'),'separate');r.append(fc);toc_start._p.append(r)
for level,title,name in nav:
    par=toc_end.insert_paragraph_before()
    par.paragraph_format.space_before=Pt(4 if level==1 else 0)
    par.paragraph_format.space_after=Pt(2)
    par.paragraph_format.left_indent=Cm(0 if level==1 else .45)
    par.paragraph_format.keep_with_next=level==1
    par.paragraph_format.tab_stops.add_tab_stop(Cm(17.2),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
    hyperlink=OxmlElement('w:hyperlink');hyperlink.set(qn('w:anchor'),name);hyperlink.set(qn('w:history'),'1')
    run=OxmlElement('w:r');rp=OxmlElement('w:rPr');size=OxmlElement('w:sz');size.set(qn('w:val'),'20');rp.append(size)
    if level==1:rp.append(OxmlElement('w:b'))
    run.append(rp);txt=OxmlElement('w:t');txt.text=title;run.append(txt);hyperlink.append(run);par._p.append(hyperlink)
    par.add_run('\t')
    field_run(par._p,f'PAGEREF {name} \\h')
r=OxmlElement('w:r');end=OxmlElement('w:fldChar');end.set(qn('w:fldCharType'),'end');r.append(end);toc_end._p.append(r)
settings=doc.settings.element
update=settings.find(qn('w:updateFields'))
if update is None:update=OxmlElement('w:updateFields');settings.append(update)
update.set(qn('w:val'),'true')

# Footer page fields and a header link back to the contents.
start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),'900');start.set(qn('w:name'),'GM_Spis')
end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),'900');toc_title._p.append(start);toc_title._p.append(end)
section=doc.sections[0]
section.different_first_page_header_footer=True
header=section.header.paragraphs[0];header.text='Persona 5 RPG  •  Podręcznik GM'
header.paragraph_format.space_after=Pt(0)
header.add_run('    ')
link=OxmlElement('w:hyperlink');link.set(qn('w:anchor'),'GM_Spis')
r=OxmlElement('w:r');t=OxmlElement('w:t');t.text='Powrót do spisu treści';r.append(t);link.append(r);header._p.append(link)
for run in header.runs:run.font.size=Pt(8);run.font.color.rgb=RGBColor.from_string('666666')
footer=section.footer.paragraphs[0];footer.text='';footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run('Strona ');field_run(footer._p,'PAGE','1');footer.add_run(' z ');field_run(footer._p,'NUMPAGES','—')
for par in doc.paragraphs:
    if par.style.name=='Title':
        pr=par._p.get_or_add_pPr()
        for border in list(pr.findall(qn('w:pBdr'))):pr.remove(border)
doc.core_properties.title='Persona 5 RPG Podręcznik dla GM'
doc.core_properties.subject='Walka eksploracja daily life i katalogi odniesienia'
doc.core_properties.version='0.3'
assert not OUT.exists(),'New output already exists; choose another filename.'
doc.save(OUT)

check=Document(OUT)
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==source_hash
assert len(check.tables)==60
after_tables=[[[c.text for c in row.cells] for row in t.rows] for t in check.tables]
before=Counter(json.dumps(t,ensure_ascii=False) for i,t in enumerate(original_tables) if i!=12)
after=Counter(json.dumps(t,ensure_ascii=False) for t in after_tables if t[0][0]!='Obszar')
assert before==after,'A preserved table changed'
assert sum(len(t.rows)-1 for t in check.tables if len(t.columns)==6 and t.cell(0,0).text=='Umiejętność')==541
assert sum(len(t.rows)-1 for t in check.tables if len(t.columns)==6 and t.cell(0,0).text=='Przedmiot')==157
assert any(len(t.rows)==100 and t.cell(0,0).text=='Poziom' for t in check.tables)
assert len([par for par in check.paragraphs if par.style.name=='Heading 1'])==14
report={'output':str(OUT),'source_sha256':source_hash,'chapters':14,'toc_entries':len(nav),'tables_preserved':59,'planning_table_updated':1,'skill_and_trait_entries':541,'recovery_items':157,'arcana_cards':24,'source_unchanged':True,'unassigned_blocks':unused}
(ROOT/'gm_guide_0_3_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
