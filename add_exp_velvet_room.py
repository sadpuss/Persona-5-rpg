from pathlib import Path
from collections import Counter
import json,csv,re,hashlib
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

R=Path(__file__).parent
GM_SOURCE=R/'Persona_5_RPG_Podrecznik_GM_0_4.docx'
P_SOURCE=R/'Persona_5_RPG_Podrecznik_Gracza_0_1.docx'
B_SOURCE=R/'Persona_5_RPG_Bestiariusz_0_1.docx'
GM_OUT=R/'Persona_5_RPG_Podrecznik_GM_0_5.docx'
P_OUT=R/'Persona_5_RPG_Podrecznik_Gracza_0_2.docx'
B_OUT=R/'Persona_5_RPG_Bestiariusz_0_2.docx'
assert not any(x.exists() for x in (GM_OUT,P_OUT,B_OUT))
hashes={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (GM_SOURCE,P_SOURCE,B_SOURCE)}
load=lambda f:json.loads((R/f).read_text(encoding='utf-8-sig'))
personas=load('p5r_personas.json');party=load('p5r_party.json')
skills={}
for f in ['p5_base_skill_data.json','p5r_skill_data.json']:
    for v in load(f).values():skills[v['a'][0]]=v
gates={x['skill']:x for x in load('skill_level_gates.json')}
inherit={'fire':'fir','ice':'ice','elec':'ele','wind':'win','psy':'psy','nuke':'nuk','bless':'ble','curse':'cur','phys':'phy','healing':'rec','ailment':'ail','almighty':'alm'}
entries=sorted({**personas,**party}.items(),key=lambda x:(x[1]['lvl'],x[0].casefold()))
mapping=[]
for index,(name,data) in enumerate(entries,1):
    item=data.get('item')
    if item in skills and skills[item]['a'][1]!='tra':
        card=item;origin='P5R';reason='Zwykła itemizacja P5R daje tę kartę.'
    else:
        candidates=[]
        for sk,learn_level in data['skills'].items():
            g=gates.get(sk)
            if not g or g['access'] not in ('R','A') or g['min_level'] is None:continue
            if learn_level>=1 and learn_level>data['lvl']:continue
            if g['min_level']>data['lvl']:continue
            candidates.append(sk)
        candidates.sort(key=lambda sk:(-(skills[sk]['a'][1]==inherit.get(data.get('inherits'))),-gates[sk]['min_level'],-skills[sk]['b'][2],sk.casefold()))
        defaults={'curse':'Eiha','bless':'Kouha','fire':'Agi','ice':'Bufu','elec':'Zio','wind':'Garu','psy':'Psi','nuke':'Frei','healing':'Dia','phys':'Lunge'}
        card=candidates[0] if candidates else defaults.get(data.get('inherits'),'Sukukaja')
        origin='HB'
        reason=('Stała adaptacja z dostępnego na bazowym poziomie zestawu Persony; preferuje jej motyw dziedziczenia.' if candidates else 'Autorski zamiennik wsparcia dla wpisu bez kwalifikującego się zwykłego skilla.')
    g=gates[card]
    mapping.append({'card_number':index,'persona':name,'persona_level':data['lvl'],'arcana':data['race'].replace(' P',''),'kind':'party' if name in party else 'persona','p5r_item':item,'p5r_alarm_item':data.get('itemr'),'skill_card':card,'origin':origin,'min_skill_level':g['min_level'],'access':g['access'],'reason':reason})
assert len(mapping)==242 and sum(x['origin']=='P5R' for x in mapping)==114
assert all(x['skill_card'] in skills for x in mapping)
assert all(x['min_skill_level'] is not None or x['access']=='X' for x in mapping)
cards={x['persona']:x for x in mapping}
(R/'persona_skill_cards.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
with (R/'persona_skill_cards.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=mapping[0].keys());w.writeheader();w.writerows(mapping)

def exp_at(level):return 50*(level-1)*level
exp_rows=[(level,exp_at(level),100*level if level<99 else None,exp_at(level+1) if level<99 else None) for level in range(1,100)]
assert exp_at(1)==0 and exp_at(99)==485100
assert all(exp_rows[i+1][1]-exp_rows[i][1]==exp_rows[i][2] for i in range(98))
(R/'exp_levels_1_99.json').write_text(json.dumps([dict(zip(['level','total_exp','to_next_level','next_total'],row)) for row in exp_rows],ensure_ascii=False,indent=2),encoding='utf-8')

def table(doc,headers,rows,widths,size=9):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
    for col,width in zip(t.columns,widths):col.width=Cm(width)
    for cell,value in zip(t.rows[0].cells,headers):cell.text=str(value)
    for values in rows:
        for cell,value in zip(t.add_row().cells,values):cell.text=str(value)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for ri,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for cell,width in zip(row.cells,widths):
            cell.width=Cm(width);pr=cell._tc.get_or_add_tcPr()
            b=OxmlElement('w:tcBorders')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
            pr.append(b)
            mar=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'65');e.set(qn('w:type'),'dxa');mar.append(e)
            pr.append(mar)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EAEAEA');pr.append(sh)
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1
                p.paragraph_format.keep_with_next=ri==0
                for run in p.runs:run.font.size=Pt(size);run.bold=ri==0;run.font.color.rgb=RGBColor(0,0,0)
    return t

def exp_module(doc,chapter,sub_prefix=''):
    h=lambda text:doc.add_heading(sub_prefix+text,2)
    p=doc.add_paragraph
    doc.add_heading(chapter,1)
    p('Propozycja wspólnego tempa rozwoju do testów. GM ustala nagrody dla konkretnej przygody; tabela progów pozostaje stałą bazą, dzięki której karty, poziomy skilli i fuzje używają tego samego poziomu bohatera.')
    h('EXP i awans')
    p('Prowadzimy jeden łączny licznik EXP dla bohatera i osobistej Persony. Nie wydajemy tego EXP przy nauce ani w Velvet Roomie. Poziom L wymaga łącznie 50 × (L − 1) × L EXP. Przejście z poziomu L na L + 1 kosztuje dodatkowe 100 × L EXP. Poziom 1 zaczyna się od 0; poziom 99 wymaga 485 100. Nadwyżka zostaje, a duża nagroda może dać kilka awansów. Poziom 99 jest końcem tabeli, bez dalszych automatycznych awansów.')
    p('Każdy awans daje +1 maksymalnego HP i +1 maksymalnego SP według istniejących wzorów, bez automatycznego leczenia. Jako prostą propozycję nauki dodajemy 1 punkt nauki za poziom uzyskany od 2 wzwyż. Nowy lub ponownie uczony zwykły skill kosztuje 1 punkt, niezależnie od kosztu HP/SP jego użycia. Punkty można zachować. Poziom nie przyznaje wszystkich skilli automatycznie; obowiązują minimum z katalogu, gotowy opis RPG i limit ośmiu slotów. Cztery skille startowe są darmowe, a trait Arkany jest osobno. Przy starcie na wyższym poziomie roboczy budżet to cztery skille startowe plus L − 1 punktów nauki, po uzgodnieniu z GM.')
    h('Przykładowe nagrody')
    p('N oznacza poziom wyzwania ustalony przez GM przy przygotowaniu sceny, zwykle zbliżony do poziomu drużyny. Zapisujemy go przy spotkaniu; nie rośnie tylko dlatego, że bohater awansował. Nagroda jest za całe starcie, nie za każdego Shadow. Każdy uczestniczący bohater gracza otrzymuje pełną wartość; nie dzielimy puli i nie premiujemy ostatniego trafienia. NPC nie wymagają osobnego licznika EXP; ich poziom i karty ustala GM.')
    table(doc,['Rozstrzygnięcie','EXP dla bohatera','Przykład N = 10'],[
        ('Drobna, łatwa potyczka','10 × N','100'),('Zwykła potyczka','20 × N','200'),('Trudna potyczka','35 × N','350'),('Miniboss','60 × N','600'),('Boss ważnego wątku','120 × N','1 200'),('Istotny postęp śledztwa lub pokonana przeszkoda fabularna','20 × N','200'),('Zamknięcie ważnego celu historii','50 × N','500')
    ],[9.0,4.4,4.0])
    p('Za jedno starcie wybieramy jedną kategorię trudności. Nagroda za osobny cel fabularny może dojść do walki, ale nie naliczamy kilku nazw tej samej zasługi. Rozwiązanie starcia przez Hold Up i negocjacje daje tyle samo EXP co pokonanie jego przeciwników. Samo ominięcie grupy, np. Pustelnikiem, nie daje bojowego EXP; osiągnięty cel śledczy może dostać własną nagrodę. Ucieczka nie daje pełnego EXP za żyjących wrogów; ewentualną częściową nagrodę za trwały postęp ustala GM. Nokaut pojedynczej osoby nie odbiera jej udziału. Porażka całej drużyny cofa EXP, poziomy i punkty nauki razem z ostatnim zapisem.')
    p('Przykład wyprawy na poziomie 10: pięć zwykłych walk po 200 EXP, miniboss 600 i ważny trop 200 dają każdemu 1 800 EXP. Bohater z dokładnie 4 500 EXP ma po wyprawie 6 300: osiąga poziom 11 i ma 800 z 1 100 EXP potrzebnych do poziomu 12. To punkt odniesienia dla około jednego do dwóch awansów na taki odcinek, nie obietnica na każdą sesję. GM może zmienić mnożniki nagród, aby dobrać długość kampanii.')
    h('Tabela poziomów od 1 do 99')
    fmt=lambda n:'—' if n is None else f'{n:,}'.replace(',',' ')
    table(doc,['Poziom','Łączny EXP na ten poziom','EXP do następnego','Łączny próg następnego'],[(l,fmt(total),fmt(delta),fmt(nxt)) for l,total,delta,nxt in exp_rows],[2.0,5.4,4.4,5.6])

def velvet_module(doc,chapter,sub_prefix=''):
    h=lambda text:doc.add_heading(sub_prefix+text,2)
    p=doc.add_paragraph
    doc.add_heading(chapter,1)
    p('Velvet Room jest osobnym miejscem zarządzania bankiem, fuzjami i skill cards. W daily life można wejść do niego zawsze poza aktywną walką; w pałacu dostępny jest w każdym safe roomie. Zwykłe zarządzanie, fuzja, tworzenie karty i nauka nie zużywają bloku dnia ani akcji walki. Dłuższą scenę fabularną można rozegrać osobno. Samo wejście nie odnawia HP/SP, nie nadpisuje zapisu pałacu i nie zastępuje wyjścia do rzeczywistości.')
    h('Bank pięciu Person')
    p('Każdy bohater ma własny bank do pięciu Person. Osobista Persona nie zajmuje miejsca i nigdy nie jest składnikiem fuzji lub itemizacji. W banku zapisujemy nazwę, bazowy poziom z kompendium i stałą kartę z bestiariusza; nie prowadzimy dodatkowych pasków EXP, HP/SP ani odziedziczonych zestawów skilli materiałów. Duplikaty są dozwolone, ale każda kopia zajmuje miejsce. Bank nie pozwala zmieniać osobistej Persony podczas walki.')
    p('Przy pełnym banku przed przyjęciem nowej Persony zwolnij jedną kopię albo wybierz inną nagrodę Hold Up. Możesz przechowywać pozyskaną Personę o poziomie wyższym od bohatera; nie omija to progów skilli ani ograniczenia wyniku fuzji. Rejestr poznanych nazw jest notatką, nie darmowym przywołaniem utraconej kopii. Nie wprowadzamy obecnie zakupów kopii z kompendium. Fuzje i itemizacja nie przyznają EXP.')
    h('Fuzje według P5R')
    p('Wybierz kopie z własnego banku i sprawdź recepturę w kalkulatorze P5R aqiu384: https://aqiu384.github.io/megaten-fusion-tool/?csr=/p5r/personas . Wybierz Persona 5 Royal, nie podstawowe Persona 5. Uzgodnij z GM stałą konfigurację DLC; wyłączenie lub włączenie DLC może zmienić zwykłe receptury. Baza bestiariusza zawiera DLC. Nie zgadujemy wyniku na podstawie samych poziomów lub Arkan.')
    p('Wynik musi być wskazany przez kalkulator dla dokładnie tych składników i mieć bazowy poziom nie większy niż poziom bohatera. Przed zatwierdzeniem pokaż GM składniki, wynik, jego poziom i kartę. Udana fuzja jest gwarantowana, usuwa wszystkie składniki i dodaje jedną kopię wyniku. Nie kosztuje dodatkowego EXP, HP/SP ani pieniędzy. Bank po operacji nadal ma najwyżej pięć kopii. Nie stosujemy alarmów, wypadków fuzji ani dziedziczenia skilli materiałów; wynik ma zawsze własną stałą kartę.')
    p('Specjalne receptury i Treasure Demons sprawdzamy osobno w tym samym kalkulatorze. Warunki P5R, np. fabularne odblokowanie lub maksymalna relacja, wymagają odpowiednika w kampanii ustalonego przez GM; nie trzeba spotkać kanonicznego NPC. Nie tworzymy przez zwykłą fuzję Person towarzyszy oznaczonych jako wyłącznie fabularne. Receptury wymagające więcej niż pięciu równoczesnych składników są niedostępne w podstawowym banku; nie skracamy ich ani nie podmieniamy składników, żeby udawać zgodność z P5R.')
    p('Przykład z P5R: Berith + Eligor + Orobas → Flauros, poziom 19. Bohater na poziomie 20 może wykonać tę specjalną fuzję, o ile ma wszystkie trzy kopie i dopuszczoną recepturę. Trzy miejsca banku zastępuje jedno. Bohater na poziomie 18 nie może jeszcze stworzyć Flaurosa. Pozostałe pary i receptury sprawdzamy bezpośrednio w kalkulatorze.')
    h('Jedna Persona zamienia się w jedną kartę')
    p('Itemizacja i fuzja to różne czynności. Fuzja łączy materiały w nową Personę, a itemizacja zużywa jedną kopię z banku i daje dokładnie jedną przypisaną jej skill card. Wynik jest stały, podany na karcie bestiariusza i znany przed potwierdzeniem. Nie losujemy karty i nie wybieramy dowolnego skilla z całej listy Persony. Dla prostoty nie wymagamy Blank Card, pieniędzy ani dodatkowej szansy powodzenia. W tej wersji używamy zwykłej itemizacji, bez wyniku alarmowego.')
    p('W P5R nie każda Persona daje kartę: część daje broń, pancerz lub akcesorium. Bestiariusz zachowuje oryginalny przedmiot i wynik alarmowy jako odniesienie. W polu Skill card RPG oznaczenie P5R wskazuje dokładną zwykłą kartę z gry, a HB stałe przypisanie do naszego RPG. Spośród 242 wpisów 114 zachowuje źródłową kartę, a 128 otrzymało autorski zamiennik, w tym 10 hipotetycznych wpisów Person towarzyszy. Nazwy i efekty samych skilli pochodzą z katalogu; autorskie jest przypisanie materiału do karty.')
    p('Zamienniki HB dobrano z naturalnych skilli dostępnych danej Personie na jej bazowym poziomie, preferując jej motyw dziedziczenia i moc pasującą do poziomu RPG; nie kopiujemy traitów, mocy unikatowych ani Technical. Dla Necronomiconu, który nie ma zwykłego kwalifikującego się skilla, przyjęto Sukukaja jako jawny zamiennik wsparcia. To stałe przypisania redakcyjne, nie algorytm do przeliczania po każdej fuzji. Oryginalnych Person sojuszników nie można odbierać NPC ani zamieniać w karty: ich wpisy są wyłącznie odniesieniem dla ewentualnej wersji Shadow dopuszczonej przez GM.')
    h('Nauka ze skill card')
    p('W Velvet Roomie wybierz kartę i osobistą Personę właściciela. Jeśli bohater osiągnął minimalny poziom skilla i jego efekt jest gotowy do użycia, zużyj kartę i naucz się skilla bez wydawania punktu nauki. Karta zastępuje koszt jednego punktu; nie daje dodatkowego EXP ani punktu. Pozostaje limit ośmiu skilli, więc w razie potrzeby wybierz jeden zastępowany. Niewykorzystaną kartę można zachować na później lub przekazać innemu graczowi poza walką. Karty nie zajmują miejsc banku i nie można ich bezpłatnie kopiować.')
    p('Minimum poziomu i dostępność R/A/Z/X/Ź obowiązują także karty. Karta A może istnieć w ekwipunku, ale przed nauką wymaga opisu adaptacji zaakceptowanego przez GM; X pozostaje nieaktywne w tej wersji. Nie zużywamy karty, gdy nie da się jej legalnie nauczyć. Posiadanie skilla nie zmniejsza kosztu HP/SP jego użycia. Ponowne nauczenie się zapomnianego skilla wymaga nowej karty lub punktu nauki; nie ma darmowego przełączania zapamiętanej biblioteki.')
    p('Przykład: Agathion daje Zio, oznaczone P5R, minimum poziom 1. Zużycie Agathiona zwalnia jedno miejsce banku i tworzy jedną kartę Zio. Nauczenie Zio zużywa kartę, ale nie punkt nauki. Arsene daje w P5R broń Arsene’s Cane; w naszym wariancie ma stałą kartę Eiha, oznaczoną HB. Te dwie informacje są rozdzielone na jego karcie.')
    h('Zapis i poświęcone materiały')
    p('W daily life zmiany banku i kart są trwałą częścią ekwipunku. W pałacu należy je uwzględnić przy następnym nadpisaniu punktu zapisu. Samo przebywanie w Velvet Roomie nie zapisuje stanu: po porażce odtwarzamy ostatni zapis banku, kart, punktów nauki i EXP tak samo jak pozostały ekwipunek. Dlatego materiały zużyte po zapisie wracają, a ich nowe wyniki przepadają; nie zachowujemy jednocześnie składników i produktu.')
    h('Źródła i granice uproszczenia')
    p('Kalkulator i baza danych: aqiu384 megaten-fusion-tool, wariant Royal; https://github.com/aqiu384/megaten-fusion-tool/tree/master/src/app/p5/data . Sprawdzono 28 października 2026. Oryginalne itemizacje z pól item i itemr lokalnej bazy roy-demon-data. Dodatkowe odniesienie: https://www.rpgsite.net/feature/13388-persona-5-royal-electric-chair-item-list-database-for-itemization . Przypisania HB, punkty nauki, brak Blank Cards, brak kosztów i dostęp z safe roomów są naszym homebrew. Nie odtwarzamy komputerowego EXP, ekonomii ani losowych wypadków fuzji.')

# Player guide: remove the draft character-sheet form and retain only the example.
player=Document(P_SOURCE)
for t in list(player.tables):
    if t.cell(0,0).text=='Pole':t._tbl.getparent().remove(t._tbl)
for p in player.paragraphs:
    t=p.text
    if t=='6 Przykład i karta do wypełnienia':p.text='6 Przykład stworzonej Persony'
    elif t.startswith('Wersja 0.1'):p.text='Wersja 0.2 • 28 października 2026 • EXP bank fuzje i skill cards'
    elif t.startswith('Ten fragment prowadzi przez'):
        p.text='Podręcznik opisuje tworzenie własnej Persony, akcje bohatera, progi skilli oraz proponowany rozwój przez EXP. Velvet Room obejmuje bank pięciu Person, fuzje P5R i stałe skill cards. Korzystamy z podręcznika GM 0.5 i bestiariusza 0.2. Ozdobną kartę postaci przygotujemy osobno, z oddzielnymi miejscami na zdolności bohatera i skille Persony.'
    elif t.startswith('Poziom bohatera i osobistej Persony traktujemy'):
        p.text='Poziom bohatera i osobistej Persony to jeden poziom L i jeden licznik EXP. Awans odblokowuje możliwość nauki, nie wszystkie skille automatycznie. Proponowane punkty nauki i ich alternatywę w postaci skill cards opisują rozdziały 7 i 8. Cztery początkowe skille są darmowe; zwykłego HP/SP nie wydajemy na trwałe uczenie.'
    elif 'GM 0.4' in t:p.text=t.replace('GM 0.4','GM 0.5')
    elif 'podręcznika GM 0.4' in t:p.text=t.replace('podręcznika GM 0.4','podręcznika GM 0.5')
    elif t.startswith('Maksymalnie osiem skilli łącznie z pasywami.'):
        p.text='Maksymalnie osiem skilli łącznie z pasywami. Przy nauce dziewiątego wybierz jeden zastępowany; nie ma darmowej zmiany biblioteki między walkami. Zapomniany skill można ponownie pozyskać kartą lub punktem nauki. Budżet startu na wyższym poziomie podaje rozdział 7.'
    elif t.startswith('Kontrola przed grą:'):
        p.text=t.split(' Na następnym etapie')[0]+' Osobny formularz karty postaci będzie zawierał oddzielne miejsca na zdolności bohatera i skille osobistej Persony.'
    elif 'Pełna tabela jest w rozdziale 11 podręcznika GM.' in t:
        p.text=t.replace('rozdziale 11','rozdziale 12')
exp_module(player,'7 EXP i nauka skilli')
velvet_module(player,'8 Velvet Room bank fuzje i skill cards')
player.core_properties.version='0.2'
player.save(P_OUT)

# GM guide: insert the shared module before reference tables, then renumber later chapters.
gm=Document(GM_SOURCE)
for p in gm.paragraphs:
    if p.style.name.startswith('Heading'):
        m=re.match(r'^(\d+)([. ]|$)',p.text)
        if m and int(m[1])>=11:p.text=str(int(m[1])+1)+p.text[len(m[1]):]
    elif not p.style.name.startswith('TOC'):
        p.text=re.sub(r'(rozdzia\w*\s+)(11|12|13|14)(?!\d)',lambda m:m[1]+str(int(m[2])+1),p.text)
    if p.text.startswith('Wersja 0.4'):p.text='Wersja 0.5 • 28 października 2026 • EXP i Velvet Room'
    elif p.text.startswith('Zasady walki, eksploracji pałaców i daily life'):
        p.text='Zasady walki, eksploracji, daily life, rozwoju i Velvet Roomu do prowadzenia przy stole. Rozdziały 1–11 zawierają zasady i wskazówki dla GM; rozdziały 12–14 są katalogami wartości, a 15 zawiera źródła. Tworzenie Persony rozwija osobny podręcznik gracza 0.2; przypisania skill cards podaje bestiariusz 0.2.'
    elif p.text.startswith('Układ zachowuje uporządkowaną wersję'):
        p.text='Wersja 0.5 zachowuje wcześniejsze zasady i katalogi oraz dodaje propozycję EXP i punktów nauki, bank pięciu Person, dostęp do Velvet Roomu, fuzje z P5R i tworzenie skill cards. Wszystkie progi i nagrody EXP są homebrew do testów. Karty postaci będą osobnym dokumentem.'
    elif p.text.startswith('Przyjęty kierunek: jeden licznik EXP'):
        p.text='Bohater i osobista Persona używają jednego licznika EXP. Proponowane progi poziomów 1–99, nagrody i punkty nauki podaje rozdział 11. Wydawanie punktów nauki lub kart nie obniża EXP ani poziomu.'
    elif p.text.startswith('Zebrane od Shadows Persony trafiają'):
        p.text='Zebrane Persony trafiają do banku do pięciu kopii, poza osobistą Personą. Velvet Room jest dostępny w daily life i w każdym safe roomie. Fuzje używają receptur P5R, a jedna kopia może zostać zamieniona w stałą skill card z bestiariusza. Pełne zasady opisuje rozdział 11.'
    elif 'Cenę nauki i progi EXP ustalimy osobno.' in p.text:
        p.text=p.text.replace('Cenę nauki i progi EXP ustalimy osobno.','Proponowany koszt nauki to jeden punkt z awansu lub jedna pasująca skill card; progi EXP i szczegóły podaje rozdział 11.')
    elif p.text.startswith('Rozwój przez EXP, tworzenie osobistej Persony, pojemność banku'):
        p.text='Tworzenie osobistej Persony opisuje podręcznik gracza 0.2. Rozwój przez EXP, bank, fuzje i skill cards podaje rozdział 11, a daily life i relacje rozdziały 8 i 9. Technical pozostaje pominięte.'
    elif 'pojemność banku ustalimy w podręczniku gracza' in p.text:
        p.text=p.text.replace('pojemność banku ustalimy w podręczniku gracza','bank mieści do pięciu Person, poza osobistą Personą')
    elif 'Szczegółowe zasady tworzenia postaci i rozwoju przez EXP pozostają' in p.text:
        p.text=p.text.split(' Szczegółowe zasady')[0]+' Tworzenie Persony opisuje podręcznik gracza; EXP i Velvet Room podaje rozdział 11.'
    elif 'tworzenie bohatera, EXP, bank i rozwój osobistej Persony pozostają kolejnym etapem' in p.text:
        p.text=p.text.replace('tworzenie bohatera, EXP, bank i rozwój osobistej Persony pozostają kolejnym etapem podręcznika gracza','tworzenie Persony opisuje podręcznik gracza, a EXP i Velvet Room rozdział 11')
    elif p.text.startswith('Minimalne poziomy i dostępność skilli'):
        pass
pending=next(t for t in gm.tables if t.cell(0,0).text=='Obszar')
updates=[
('Postać i awans','Tworzenie Persony opisuje podręcznik gracza 0.2. Progi EXP, nauka i awans są w rozdziale 11, HP/SP w 12. Dalszy rozwój ataku i Obrony wymaga osobnego ustalenia.'),
('Rozwój Persony','Bank pięciu kopii, fuzje i karty są w rozdziale 11. Niezaadaptowane efekty A nadal wymagają opisu, a źródłowe traity P5R nie są dodatkowym traitem bohatera.'),
('Opcjonalne rozszerzenia walki','Krytyki, multi hit, instakill i nieopisane moce. Technical celowo pominięto; alarm i wypadki fuzji nie są częścią podstawowej wersji.'),
('Daily life','Podstawowy moduł jest gotowy. Testujemy tempo cech i relacji; Velvet Room nie zużywa bloku.'),
('Przygotowanie GM','Dostosowanie nagród EXP, cen i zapasów do konkretnej przygody, testy składu drużyny i opcjonalny alarm.')]
for row,vals in zip(pending.rows[1:],updates):
    for cell,value in zip(row.cells,vals):cell.text=value
body=gm.element.body;old_nodes=set(body)
exp_module(gm,'11 Rozwój przez EXP i Velvet Room')
# Keep Velvet Room under the same main chapter in the GM guide.
velvet_module(gm,'Velvet Room i rozwój materiałów')
new_nodes=[node for node in body if node not in old_nodes and node.tag!=qn('w:sectPr')]
sub=0
for node in new_nodes:
    if node.tag==qn('w:p'):
        p=Paragraph(node,gm)
        if p.style.name=='Heading 1' and p.text=='Velvet Room i rozwój materiałów':p.style=gm.styles['Heading 2']
        if p.style.name=='Heading 2':sub+=1;p.text=f'11.{sub} '+p.text
anchor=next(p for p in gm.paragraphs if p.style.name=='Heading 1' and p.text.startswith('12 HP'))._p
for node in new_nodes:anchor.addprevious(node)
gm.core_properties.version='0.5';gm.save(GM_OUT)

# Bestiary: add a fixed card to every existing entry without changing source stats or names.
bestiary=Document(B_SOURCE)
intro_anchor=next(p for p in bestiary.paragraphs if p.style.name=='Heading 1')
intro_anchor.insert_paragraph_before('Skill cards i Velvet Room','Heading 2')
intro_anchor.insert_paragraph_before('Każdy z 242 wpisów ma teraz jedną stałą Skill card RPG. P5R oznacza dokładną zwykłą kartę z gry, HB oznacza autorski zamiennik, gdy gra daje przedmiot albo wpis dotyczy Persony towarzysza. 114 przypisań jest źródłowych, 128 homebrew. Pole Przedmiot / alarm pozostaje oryginalnym wynikiem P5R i nie jest drugim łupem. Alarmów nie stosujemy w podstawowej wersji RPG.')
intro_anchor.insert_paragraph_before('Min. Lv i R/A/X dotyczą nauki z karty, nie poziomu materiału. R ma gotowy efekt, A wymaga adaptacji, X pozostaje nieaktywne. Jedna kopia bankowa znika za jedną kartę; nie zmieniamy jej wyniku przez fuzję lub dziedziczenie skilli. Bank mieści pięć Person, osobista Persona pozostaje poza nim. Persony towarzyszy mają przypisanie hipotetyczne: nie można odbierać ich NPC ani poświęcać osobistej Persony. Pełne reguły są w podręczniku gracza 0.2 i GM 0.5.')
intro_anchor.insert_paragraph_before('Przypisania źródłowe: pola item bazy aqiu384 roy-demon-data. HB dobrano z naturalnych skilli Persony na bazowym poziomie, preferując jej typ i próg RPG. Wyjątek: Necronomicon → Sukukaja jako autorskie wsparcie. Lista kontrolna jest zapisana także w pliku persona_skill_cards.csv. Kalkulator: https://aqiu384.github.io/megaten-fusion-tool/?csr=/p5r/personas .')
card_starts=[p for p in bestiary.paragraphs if p.style.name=='Heading 2' and re.match(r'^\d{3}\s+Lv\s+\d+\s+',p.text)]
assert len(card_starts)==242
for p in bestiary.paragraphs:
    if p.text.startswith('Wersja 0.1'):p.text='Wersja 0.2 • 28 października 2026 • polskie nazwy Shadows i stałe skill cards'
    elif p.text.startswith('Krótkie opisy na kartach są własnymi profilami'):
        p.text=p.text.replace('Nasze wytwarzanie skill cards wymaga osobnych zasad.','Nasze wytwarzanie skill cards opisują podręczniki gracza 0.2 i GM 0.5; przypisania HB są jawnie oddzielone od oryginalnej itemizacji.')
    elif p.text.startswith('Traity są osobnym polem, nie dziewiątym skillem.'):
        p.text+=' Osobista Persona gracza używa traitu Arkany; źródłowe traity P5R na kartach nie są dodatkową nagrodą.'
for i,start in enumerate(card_starts):
    m=re.match(r'^(\d{3})\s+Lv\s+(\d+)\s+(.+)$',start.text)
    name=m[3];entry=cards[name]
    end=card_starts[i+1]._p if i+1<len(card_starts) else None
    node=start._p.getnext();trait=None
    while node is not None and node is not end:
        if node.tag==qn('w:p'):
            par=Paragraph(node,bestiary)
            if par.text.startswith('Trait P5R:'):trait=par;break
        node=node.getnext()
    assert trait is not None,name
    new=OxmlElement('w:p');trait._p.addnext(new);par=Paragraph(new,bestiary)
    par.add_run('Skill card RPG: ').bold=True
    par.add_run(f'{entry["skill_card"]} • min. Lv {entry["min_skill_level"] if entry["min_skill_level"] is not None else "—"} / {entry["access"]} • {entry["origin"]}'+(' • tylko hipotetyczny Shadow' if entry['kind']=='party' else ''))

# Remove forced three-card pages, then keep each complete card together.
for par in list(bestiary.paragraphs):
    if not par.text.strip() and not list(par._p.iter(qn('w:fldChar'))) and not list(par._p.iter(qn('w:fldSimple'))):
        par._p.getparent().remove(par._p)
for i,start in enumerate(card_starts):
    node=start._p;end=card_starts[i+1]._p if i+1<len(card_starts) else None
    paras=[]
    while node is not None and node is not end and node.tag!=qn('w:sectPr'):
        if node.tag==qn('w:p'):paras.append(Paragraph(node,bestiary))
        elif node.tag==qn('w:tbl'):
            for xmlpar in node.iter(qn('w:p')):Paragraph(xmlpar,bestiary).paragraph_format.keep_with_next=True
        node=node.getnext()
    for j,par in enumerate(paras):par.paragraph_format.keep_with_next=j<len(paras)-1
    start.paragraph_format.page_break_before=i==0
for table_ in bestiary.tables:
    for cell in table_.rows[0].cells:
        for p in cell.paragraphs:p.paragraph_format.keep_with_next=True
for sec in bestiary.sections:
    for p in sec.footer.paragraphs:
        for run in p.runs:run.text=run.text.replace('Bestiariusz 0.1','Bestiariusz 0.2')
bestiary.core_properties.version='0.2';bestiary.save(B_OUT)

for file,sha in hashes.items():assert hashlib.sha256((R/file).read_bytes()).hexdigest()==sha
bc=Document(B_OUT);original_b=Document(B_SOURCE)
assert len(bc.tables)==len(original_b.tables)==244
assert [[[c.text for c in row.cells] for row in t.rows] for t in bc.tables]==[[[c.text for c in row.cells] for row in t.rows] for t in original_b.tables]
assert len([p for p in bc.paragraphs if p.text.startswith('Skill card RPG:')])==242
assert [p.text for p in bc.paragraphs if p.text.startswith('Arcana:')]==[p.text for p in original_b.paragraphs if p.text.startswith('Arcana:')]
for f in [GM_OUT,P_OUT]:
    d=Document(f);tables=[t for t in d.tables if len(t.columns)==4 and t.cell(0,0).text=='Poziom']
    assert len(tables)==1 and len(tables[0].rows)==100
assert not any(t.cell(0,0).text=='Pole' for t in Document(P_OUT).tables)
report={'source_hashes':hashes,'outputs':[str(x) for x in [GM_OUT,P_OUT,B_OUT]],'exp_level_rows':99,'exp_to_level_99':exp_at(99),'fixed_cards':242,'p5r_cards':114,'homebrew_cards':128,'bestiary_tables_preserved':244,'polish_shadow_names_preserved':True,'sources_unchanged':True,'bank_capacity':5,'character_sheet_removed_from_player_guide':True,'learning_points_are_proposed':True,'card_access_counts':dict(Counter(x['access'] for x in mapping))}
(R/'exp_velvet_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
print('SAMPLE CARDS',[(n,cards[n]['skill_card'],cards[n]['origin']) for n in ['Arsene','Pixie','Agathion','Jack Frost','Flauros','Necronomicon']])
