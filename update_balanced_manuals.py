from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import json,re,copy
import balance_lab as B
R=Path(__file__).parent
OUT=R/'qa_balance_update'
unit=B.make_hero(99,0,'mage',B.BASE)
newcost={n:f'{B.cost_of(s,unit,B.FINAL)} {s.resource}' for n,s in B.SKILLS.items() if s.kind=='attack' and s.elem!='Almighty' and not n.startswith('Basic ')}
light={n for n,s in B.SKILLS.items() if s.elem in ('Physical','Gun') and s.dice==1 and s.flat==4 and not n.startswith('Basic ')}
WAKE='Po zwycięstwie lub zakończeniu walki przez Hold Up, po rozliczeniu premii końca walki, nieprzytomni członkowie drużyny odzyskują przytomność z 1 HP i niezmienionym SP. Nie daje to dodatkowej akcji. Dalsze leczenie zużywa normalne zasoby. Zasada nie działa po ucieczce ani porażce całej drużyny; podczas walki do podniesienia postaci nadal potrzebny jest skill lub przedmiot wskrzeszający.'
RETREAT='Ponowne zaatakowanie tej samej grupy po ucieczce jest kontynuacją spotkania dla limitów zdolności na walkę. Zachowaj pozostałe SP ocalałych wrogów oraz wykorzystane liczniki zdolności wszystkich uczestników, w tym Regenerate, Invigorate, Heat Up i Soul Chain. Nie zaczynaj ponownie pierwszych trzech tur regeneracji. Liczniki dotyczą konkretnej grupy, nie wszystkich Shadows danego gatunku. Nowa wyprawa po wyjściu do świata rzeczywistego odnawia te liczniki; odtworzenie zapisu przywraca ich zapisany stan.'
DESPAIR='Na bossach i minibossach Despair nie powoduje KO: przy trzecim rozliczeniu, po utracie 2 SP, zadaje zamiast tego 20 obrażeń Almighty i kończy się. Guard zmniejsza te obrażenia do 8; nie dodawaj premii ataku ani obrażeń. Brak Down i One More. Zwykłe Shadows oraz bohaterowie i kompanie zachowują KO przy trzecim rozliczeniu. Ewentualną odporność na sam status GM zapisuje oddzielnie na karcie.'
COST='Aktywne skille Physical/Gun kosztują bazowo: light 2 HP, medium 4 HP, heavy 6 HP, severe 8 HP, colossal 10 HP. Obszar: +3 HP. Dodatkowy status albo premia +2 do trafienia: +1 HP łącznie, również gdy występują oba. Cornered Fang ma −2 HP za warunek zaskoczenia przez wroga; Deadly Fury, Giant Slice i Rising Slash +1 HP za efekt po Baton Pass. Szczegółowy wiersz katalogu jest rozstrzygający. Koszt HP musi pozostawić co najmniej 1 HP. Płatny light Physical/Gun zadaje 1d6 + 6; darmowy atak i strzał nadal 1d6 + 4. Ataki testowe Shadows z bestiariusza mają własny, odrębny cennik.'
MAGIC='Standardowa magia żywiołowa kosztuje pojedynczo / obszarowo: light 1/3 SP, medium 2/4 SP, heavy 3/5 SP, severe 4/6 SP. Progi poziomów pozostają bez zmian. Nie stosuj tej tabeli automatycznie do Almighty, leczenia, egzekucji ani mocy specjalnych; korzystaj z ich wierszy katalogu. Kolumna P5R pozostaje odniesieniem, nie kosztem użycia w RPG.'

def put(p,text):
 if p.text==text:return
 if p.runs:
  p.runs[0].text=text
  for run in p.runs[1:]:run.text=''
 else:p.add_run(text)
def after(p,text,style=None):
 el=OxmlElement('w:p');p._p.addnext(el);q=Paragraph(el,p._parent);q.style=style or 'Normal';q.add_run(text);return q

def allp(d):return [Paragraph(e,d) for e in d.element.body.iter(qn('w:p'))]

def edit(src,dst,kind):
 d=Document(src);count=0
 for p in allp(d):
  if p.style.name.lower().startswith('toc'):continue
  s=p.text
  t=s.replace('podręcznik gracza 0.4','podręcznik gracza 0.5').replace('bestiariusz 0.4','bestiariusz 0.5').replace('GM 0.7','GM 0.8').replace('GM 0.7','GM 0.8').replace('podręcznika GM 0.7','podręcznika GM 0.8').replace('podręcznika gracza 0.4','podręcznika gracza 0.5').replace('podręczniki gracza 0.4','podręczniki gracza 0.5').replace('bestiariusza 0.4','bestiariusza 0.5').replace('persona_skill_cards_0_4.json','persona_skill_cards_0_5.json')
  if re.match(r'^Wersja \d',t):t=f'Wersja {"0.8" if kind=="gm" else "0.5"} • 29 października 2026 • zasady po testach balansu'
  if s.startswith('Light: 1d6 + 4; medium:'):t=s+' Wyjątek: płatne skille light Physical/Gun mają 1d6 + 6 (średnio 9,5). Darmowy atak, darmowy strzał, light magiczny i atak testowy Shadow zachowują 1d6 + 4.'
  if s.startswith('Każdy dawny wpis A ma teraz R i pełny opis'):t=t.replace('Koszty i minimalne poziomy zachowano;','Minimalne poziomy pozostają bez zmian; koszty obowiązują według aktualnego katalogu;')
  if s.startswith('Użycia na walkę odnawiają się na początku nowej walki,'):t=t.replace('na początku nowej walki,','na początku nowego spotkania z inną grupą wrogów; ucieczka i powrót do tej samej grupy ich nie odnawiają,')
  if s.startswith('Po zakończeniu walki usuń wszystkie 12'):t=t.replace('Nokaut pozostaje według zasad wskrzeszania.','Po zwycięstwie lub Hold Up działa budzenie z 1 HP z rozdziału 3.5; po ucieczce nokaut pozostaje.')
  if s.startswith('Sukces natychmiast kończy walkę i przenosi'):t=t.replace('odzyskują własne HP i SP','odzyskują własne HP, lecz zachowują pozostałe SP')
  if s.startswith('Wyjście z pałacu odnawia całe HP i SP'):t=t.replace('Respawn przywraca połowę maksymalnego HP i SP według zasad poniżej.','Respawn przywraca zasoby ograniczone zarówno zapisem, jak i połową maksimum według zasad poniżej.')
  if s.startswith('Gdy cała drużyna ma 0 HP, walka się kończy.'):
   t='Gdy cała drużyna ma 0 HP, wraca do ostatniego zapisanego safe roomu. HP po porażce = max(1, min(HP z zapisu, połowa maksymalnego HP zaokrąglona w dół)). SP po porażce = min(SP z zapisu, połowa maksymalnego SP zaokrąglona w dół). Znikają Down i statusy bojowe. Przykład: maksimum 60 HP/56 SP i zapis 40 HP/35 SP daje 30 HP/28 SP; zapis 1 HP/0 SP daje 1 HP/0 SP. Porażka nie zwiększa zasobów względem zapisu.'
  if s.startswith('Przywróć zapisany stan pałacu:'):t=t.replace('HP i SP, zawsze ustawiane na połowę maksimum, zamiast wartości z zapisu','HP i SP, wyliczane według ograniczenia z poprzedniego akapitu')
  if s.startswith('Respawn sam nie tworzy nowego zapisu'):t='Respawn sam nie tworzy nowego zapisu ani nie leczy przy ponownym wejściu. Zapis nadpisuje następne normalne wejście podczas dalszej eksploracji. Zapis z niskimi zasobami może wymagać leczenia lub zakończenia wyprawy i powrotu kolejnego dnia. Celowa porażka nie służy odnawianiu HP/SP.'
  if s.startswith('Wszystkie 236 dawnych A') :pass
  if s=='13.3 Reguły nowych propozycji kosztów':t='13.3 Koszty umiejętności RPG'
  if s.startswith('Dla pozostałych skilli za SP stosujemy orientacyjnie'):t=MAGIC
  if s.startswith('Dla nieustalonych skilli za procent HP proponujemy'):t=COST
  if s.startswith('Nie mnożymy automatycznie nowych efektów przez wartości z P5R.'):t='Wartości P5R pozostają odniesieniem. Multi hit, egzekucje, regeneracja, redukcja kosztów i premie procentowe mają własne reguły RPG w 13.20. Nie przeliczaj ich ponownie według źródłowych procentów.'
  if s.startswith('Despair jest świadomie łagodniejsze'):t='Despair pozwala na samoratunek przed trzecią turą. Nokaut nie oznacza automatycznej śmierci fabularnej; nie odbieramy SP poniżej 0. '+DESPAIR
  if s.startswith('Przy 0 HP postać jest nieprzytomna i nie działa;'):t='Przy 0 HP postać jest nieprzytomna i nie działa. W walce zwykłe leczenie nie wskrzesza; potrzebny jest odpowiedni skill lub przedmiot. Pojedynczy nokaut nie kończy walki. Gdy wszyscy bohaterowie i walczący kompanie mają 0 HP, następuje porażka i powrót do zapisu.'
  if s.startswith('Symulacje służyły wstępnemu porównaniu zasobów.'):t='Testy z 29 października 2026 obejmują różne poziomy, liczebności drużyn, znajomość słabości oraz serie walk. Wnioski wprowadzono w kosztach skilli, Despair, ciągłości spotkania po ucieczce i zasadach nokautu. Model korzysta z uproszczonych strategii i ataków kart; nie sprawdza wszystkich kombinacji skilli, relacji i przygód. Dobór przeciwników nadal wymaga krótkiej próby dla konkretnej drużyny.'
  if s.startswith('Koszty HP są stałe, nie procentowe.'):t='Koszty HP są stałe, nie procentowe. Tarunda odejmuje 4 od bazowych obrażeń przed właściwością celu i Guard; minimum 0. Obszar rozlicz dla każdego trafionego celu. Serie multi hit mają jeden łączny rzut według 13.20.'
  if s.startswith('Koszty i działanie podstawowych statusów'):t='Statusy i ich usuwanie opisuje rozdział 6, a gotowe działanie pozostałych skilli rozdział 13.20. Moce Z i źródłowe traity nie należą do zwykłej nauki. Koszty RPG bierz z aktualnego katalogu, nie z kolumny P5R.'
  if s.startswith('Te profile nie są zbalansowane jednakowo'):t='Profile wymagają doboru do konkretnej drużyny. Dla dwóch początkujących bohaterów zacznij od jednego Shadowa, następnie sprawdź grupę dwóch; trzech może tworzyć trudne starcie. Solo wymaga osobnej rozpiski. Dla minibossa dobierz HP i liczbę akcji do drużyny oraz zapisz: boss/miniboss, dozwolony Hold Up, dostępne nagrody i odporności na statusy. Sama etykieta nie odbiera Hold Up. Despair na bossie/minibossie przy trzecim rozliczeniu zadaje 20 Almighty zamiast KO, następnie Guard; bez premii obrażeń, Down i One More. Pozostałe reguły: podręcznik GM 0.8.'
  if t!=s:put(p,t);count+=1
 for ti,table in enumerate(d.tables):
  header=[c.text for c in table.rows[0].cells]
  for row in table.rows[1:]:
   cells=row.cells;n=cells[0].text
   if n in newcost:
    idx=3 if len(header)==7 and header[0]=='Umiejętność' else 2 if header[:3]==['Skill','Min. lvl','Koszt'] else 2 if header==['Skill','Działanie RPG','Koszt'] else 2 if header==['Umiejętność','Cel i efekt','Koszt'] else None
    if idx is not None:
     for p in cells[idx].paragraphs:put(p,newcost[n] if p==cells[idx].paragraphs[0] else '')
     # Set via the first existing paragraph without relying on wrapper identity.
     put(cells[idx].paragraphs[0],newcost[n]);count+=1
    if n in light:
     for c in cells[1:]:
      for p in c.paragraphs:
       if '1d6' in p.text:put(p,re.sub(r'1d6\s*\+\s*4','1d6 + 6',p.text))
   if n.startswith('Despair\n'):
    put(cells[1].paragraphs[0],cells[1].text+' Boss/miniboss: zamiast KO otrzymuje 20 Almighty i status się kończy; Guard działa, bez premii obrażeń, Down i One More.')
   if n.startswith('KO\n') and len(cells)>2:put(cells[2].paragraphs[0],'W walce skill lub przedmiot wskrzeszający. Po zwycięstwie/Hold Up: przytomność z 1 HP i niezmienionym SP. Po ucieczce KO pozostaje.')
   if n=='Assault Dive' and header==['Umiejętność','Cel i efekt','Koszt']:put(cells[2].paragraphs[0],'6 HP')
 # Ujednolicenie DC w katalogu i pełnym opisie.
 for table in d.tables:
  if len(table.columns)==7 and table.cell(0,0).text=='Umiejętność':
   for row in table.rows[1:]:
    if row.cells[0].text in ('Inferno','Diamond Dust','Thunder Reign','Ice Age'):
     for p in row.cells[5].paragraphs:put(p,p.text.replace('DC 6','DC 7'))
 # Insert locally without new chapters, preserving TOC structure.
 if kind=='gm':
  for p in list(d.paragraphs):
   if p.text.startswith('Przy 0 HP postać jest nieprzytomna'):after(p,WAKE)
   if p.text.startswith('Sukces natychmiast kończy walkę i przenosi'):after(p,RETREAT)
   if p.text.startswith('Skala obowiązuje bohaterów i przeciwników.'):after(p,'Płatne light Physical/Gun: 1d6 + 6 zamiast 1d6 + 4. Nie dotyczy darmowego ataku, darmowego strzału, magii ani ataku testowego Shadow. Aktualne koszty: rozdział 13.3.')
   if p.text.startswith('GM oznacza na karcie') or p.text.startswith('Zwykłe Shadows reprezentujące Persony'):after(p,'Na karcie bossa zapisz oddzielnie: czy można wywołać Hold Up, czy wolno negocjować i jakie nagrody są dostępne. Jeżeli negocjacje są wyłączone, ale Hold Up dozwolony, można wykonać All-Out Attack. Wyjątki ujawnij przed wyborem gracza.')
   if p.text.startswith('Te profile') :pass
   if p.text.startswith('Dla grupy rozdziel wynik między Shadows'):after(p,'Na początku przygody dla dwóch bohaterów zacznij od jednego Shadowa, potem sprawdź grupę dwóch. Nie przyjmuj automatycznie liczby wrogów równej liczbie bohaterów +1. Planuj możliwość wycofania do safe roomu, leczenia oraz zakończenia dnia; liczba i właściwości przeciwników zależą od skilli drużyny.')
 if kind=='player':
  for p in list(d.paragraphs):
   if p.text.startswith('Atak Physical i strzał różnią'):q=after(p,'Po zwycięstwie lub Hold Up, po premiach końca walki, nieprzytomni budzą się z 1 HP i niezmienionym SP. Nie działa to po ucieczce ani porażce całej drużyny. W walce do wskrzeszenia nadal potrzeba odpowiedniego skilla lub przedmiotu.');q=after(q,'Ucieczka nie odnawia zasobów. Powrót do tej samej grupy zachowuje SP wrogów i wykorzystane limity zdolności. Po porażce wracasz do zapisu z HP/SP nie większymi od zapisanych ani od połowy maksimum (minimum 1 HP). Wyjście do rzeczywistości i powrót kolejnego dnia daje pełne zasoby.')
   if p.text.startswith('Light: 1d6 + 4; medium:'):q=after(p,COST);after(q,MAGIC)
   if p.text.startswith('Hama/Mudo: DC 6;'):after(p,DESPAIR)
 for p in list(d.paragraphs):
  if p.text.startswith('O ile opis nie mówi inaczej: buff/debuff'):after(p,RETREAT)
 # Mark actual TOC for refresh; Word will materialize page references.
 upd=OxmlElement('w:updateFields');upd.set(qn('w:val'),'true');d.settings.element.append(upd)
 for section in d.sections:
  for part in [section.header,section.footer,section.first_page_header,section.first_page_footer,section.even_page_header,section.even_page_footer]:
   for node in part._element.iter(qn('w:t')):
    if node.text:node.text=node.text.replace('Bestiariusz 0.4','Bestiariusz 0.5').replace('Bestiariusz 0.4','Bestiariusz 0.5')
 d.save(dst);return {'file':dst,'changes':count}

results=[]
for src,dst,kind in [('Persona_5_RPG_Podrecznik_GM_0_7.docx','Persona_5_RPG_Podrecznik_GM_0_8.docx','gm'),('Persona_5_RPG_Podrecznik_Gracza_0_4.docx','Persona_5_RPG_Podrecznik_Gracza_0_5.docx','player'),('Persona_5_RPG_Bestiariusz_0_4.docx','Persona_5_RPG_Bestiariusz_0_5.docx','best')]:results.append(edit(src,dst,kind))
rules=json.loads((R/'skill_rules_0_7.json').read_text(encoding='utf-8'))
for x in rules:
 n=x['skill'];x['reason']=x.get('reason','').replace('GM 0.7','GM 0.8')
 if n in newcost:x['cost']=newcost[n]
 if n in light:x['effect']=re.sub(r'1d6\s*\+\s*4','1d6 + 6',x['effect'])
(R/'skill_rules_0_8.json').write_text(json.dumps(rules,ensure_ascii=False,indent=2),encoding='utf-8')
for src,dst in [('skill_level_gates_0_7.json','skill_level_gates_0_8.json'),('persona_skill_cards_0_4.json','persona_skill_cards_0_5.json')]:
 obj=json.loads((R/src).read_text(encoding='utf-8'));(R/dst).write_text(json.dumps(obj,ensure_ascii=False,indent=2).replace('GM 0.7','GM 0.8'),encoding='utf-8')
(OUT/'edits.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(results)
