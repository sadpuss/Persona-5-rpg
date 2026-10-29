from pathlib import Path
from collections import Counter
from zipfile import ZipFile
import json,re,hashlib,csv
from lxml import etree
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

R=Path(__file__).parent
SOURCES={'gm':'Persona_5_RPG_Podrecznik_GM_0_6.docx','player':'Persona_5_RPG_Podrecznik_Gracza_0_3.docx','bestiary':'Persona_5_RPG_Bestiariusz_0_3.docx'}
OUT={'gm':'Persona_5_RPG_Podrecznik_GM_0_7.docx','player':'Persona_5_RPG_Podrecznik_Gracza_0_4.docx','bestiary':'Persona_5_RPG_Bestiariusz_0_4.docx'}
assert not any((R/n).exists() for n in OUT.values())
hashes={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in SOURCES.values()}
gates=json.loads((R/'skill_level_gates.json').read_text(encoding='utf-8'))
skills={}
for file in ['p5_base_skill_data.json','p5r_skill_data.json']:
    for v in json.loads((R/file).read_text(encoding='utf-8-sig')).values():skills[v['a'][0]]=v
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(R/SOURCES['gm']) as z:root=etree.fromstring(z.read('word/document.xml'))
def txt(el):return ''.join(el.xpath('.//w:t/text()',namespaces=ns))
catalog={}
for t in root.xpath('//w:body/w:tbl',namespaces=ns):
    rows=t.findall('w:tr',ns)
    if len(rows[0].findall('w:tc',ns))==7 and txt(rows[0].find('w:tc',ns))=='Umiejętność':
        for row in rows[1:]:
            vals=[txt(c) for c in row.findall('w:tc',ns)];catalog[vals[0]]=vals
assert len(catalog)==541
statuses={'Burn','Freeze','Shock','Dizzy','Forget','Sleep','Confuse','Fear','Despair','Rage','Brainwash','Hunger'}
element={'phy':'Physical','gun':'Gun','fir':'Fire','ice':'Ice','ele':'Electricity','win':'Wind','psy':'Psy','nuk':'Nuclear','ble':'Bless','cur':'Curse','alm':'Almighty'}
alias={'Phys':'Physical','Elec':'Electricity','Nuke':'Nuclear'}
dice={'light':'1d6 + 4','medium':'2d6 + 6','heavy':'3d6 + 8','severe':'3d6 + 14','colossal':'3d6 + 20'}
multi={'Double Fangs':'medium','Double Shot':'heavy','Rampage':'medium','Kill Rush':'heavy','Swift Strike':'heavy','Gattling Blows':'severe','Tempest Slash':'severe','Myriad Slashes':'colossal','Deathbound':'severe','Agneyastra':'colossal','Triple Down':'heavy'}
fixed={
'Divine Judgement':'Atak Bless. Po trafieniu bazowe obrażenia to połowa aktualnego HP celu, w dół; na minibossa lub bossa najwyżej 20. Następnie właściwość i Guard. Nie korzysta z premii do obrażeń ani Charge/Concentrate; nie może obniżyć HP poniżej 1. Może wywołać Down przez Weak.',
'Demonic Decree':'Atak Curse. Po trafieniu bazowe obrażenia to połowa aktualnego HP celu, w dół; na minibossa lub bossa najwyżej 20. Następnie właściwość i Guard. Nie korzysta z premii do obrażeń ani Charge/Concentrate; nie może obniżyć HP poniżej 1. Może wywołać Down przez Weak.',
'Megido':'Atak Almighty na wszystkich wrogów; medium, 2d6 + 6. Osobne trafienie na cel, wspólne obrażenia.',
'Megidola':'Atak Almighty na wszystkich wrogów; heavy, 3d6 + 8. Osobne trafienie na cel, wspólne obrażenia.',
'Megidolaon':'Atak Almighty na wszystkich wrogów; severe, 3d6 + 14. Osobne trafienie na cel, wspólne obrażenia.',
'Life Drain':'Atak Almighty, 1 wróg; stałe 6 obrażeń, następnie Guard. Odzyskujesz HP równe faktycznej utracie HP celu, najwyżej 6. Bez premii do obrażeń i Concentrate. Nie działa na martwy cel.',
'Spirit Drain':'1 żywy wróg z SP; zwykły rzut trafienia. Cel traci najwyżej 3 aktualne SP, a ty odzyskujesz tyle samo. Guard nie zmienia utraty SP. Nie zadaje obrażeń, nie przewraca; nie działa na cel bez SP.',
'Foul Breath':'1 wróg, bez rzutu trafienia; przez 3 zwykłe tury celu DC obrony przed 12 zwykłymi statusami jest wyższe o 2. Nie kumuluje się ze Stagnant Air; Dekunda usuwa efekt. Nie nakłada statusu samo z siebie.',
'Stagnant Air':'Wszyscy uczestnicy walki, także użytkownik i sojusznicy; przez 3 zwykłe tury każdego odbiorcy DC obrony przed 12 zwykłymi statusami jest wyższe o 2. Bez rzutu trafienia. Nie kumuluje się z Foul Breath; Dekunda usuwa efekt.',
'Ghastly Wail':'Tylko wrogowie, którzy przed tą akcją mieli Fear. Zwykły Shadow po nieudanej obronie d20 przeciw DC 15 spada do 0 HP; miniboss lub boss po porażce otrzymuje 20 Almighty obrażeń, następnie Guard. Sukces: brak efektu. Bez rzutu trafienia, premii obrażeń i Concentrate; nie daje Down ani One More.',
'Media':'Wszyscy przytomni aktywni sojusznicy, także użytkownik: odzyskują po 10 HP. Bez rzutu. Nie wskrzesza.',
'Mediarama':'Wszyscy przytomni aktywni sojusznicy, także użytkownik: odzyskują po 20 HP. Bez rzutu. Nie wskrzesza.',
'Diarahan':'1 przytomny sojusznik, także użytkownik: odzyskuje pełne HP do maksimum. Bez rzutu. Nie usuwa statusów ani nie wskrzesza.',
'Mediarahan':'Wszyscy przytomni aktywni sojusznicy, także użytkownik: odzyskują pełne HP do maksimum. Bez rzutu. Nie usuwa statusów ani nie wskrzesza.',
'Recarm':'1 nieprzytomny sojusznik: wraca do połowy maksymalnego HP, w dół, minimum 1; bez SP. Odzyskuje swoje miejsce w inicjatywie, bez dodatkowej akcji. Stosuj zasady wskrzeszenia z rozdziału 14.',
'Samarecarm':'1 nieprzytomny sojusznik: wraca z pełnym HP, bez SP. Odzyskuje swoje miejsce w inicjatywie, bez dodatkowej akcji. Stosuj zasady wskrzeszenia z rozdziału 14.',
'Salvation':'Wszyscy przytomni aktywni sojusznicy, także użytkownik: pełne HP i usunięcie wszystkich 12 zwykłych statusów. Nie przywraca SP, nie wskrzesza, nie usuwa Down ani debuffów.',
'Charge':'Użytkownik: następny wykonany atak Physical lub Gun dostaje +8 obrażeń przed właściwościami i Guard. Premia dotyczy całej serii oraz każdego celu ataku obszarowego. Zużywa się także przy pudle; wygasa z końcem następnej zwykłej tury użytkownika. Nie kumuluje się ze sobą.',
'Concentrate':'Jak Charge, ale +8 do następnego ataku Fire, Ice, Electricity, Wind, Psy, Nuclear, Bless, Curse lub standardowego Almighty z kośćmi. Nie wzmacnia egzekucji, procentów HP, wysysania ani All-Out Attack.',
'Heat Riser':'1 sojusznik, także użytkownik: Tarukaja, Rakukaja i Sukukaja jednocześnie przez 3 jego zwykłe tury, bez rzutu. To te same parametry: nie sumują się z osobnymi wersjami.',
'Debilitate':'1 wróg: Tarunda, Rakunda i Sukunda jednocześnie przez 3 jego zwykłe tury, bez rzutu. Nie sumują się z osobnymi wersjami; przeciwne buffy znoszą efekty parami.',
'Thermopylae':'Jak Heat Riser dla całej aktywnej drużyny, także użytkownika. Dostępne tylko w walce, w której wrogowie zaskoczyli drużynę; warunek pozostaje spełniony do jej końca.',
'Dekaja':'Bez rzutu usuwa ze wszystkich wrogów korzystne efekty Tarukaja, Rakukaja i Sukukaja, także składniki Heat Riser/Thermopylae. Nie usuwa pasywów, Wall, odbić, Charge ani Concentrate.',
'Dekunda':'Bez rzutu usuwa z aktywnej drużyny, także użytkownika, Tarunda, Rakunda i Sukunda oraz Foul Breath/Stagnant Air. Nie usuwa statusów ani właściwości żywiołowych.',
'Tetrakarn':'1 sojusznik, także użytkownik: odbija pierwszy trafiony atak Physical lub Gun przed końcem jego 3. zwykłej tury. Jedna seria to jeden atak; w obszarze odbija tylko część skierowaną na tego sojusznika. Reguła pojedynczego odbicia.',
'Makarakarn':'Jak Tetrakarn, ale obejmuje 8 typów magicznych od Fire do Curse. Nie obejmuje Physical, Gun, Almighty, czystych statusów, egzekucji, wysysania SP ani obrażeń procentowych.',
'Tetra Break':'Bez rzutu usuwa Tetrakarn ze wszystkich wrogów. Nie usuwa wrodzonego Repel ani pasywów.',
'Makara Break':'Bez rzutu usuwa Makarakarn ze wszystkich wrogów. Nie usuwa wrodzonego Repel ani pasywów.',
'Tetraja':'Każdy aktywny sojusznik, także użytkownik, zyskuje osobny jednorazowy blok egzekucji Hama/Mudo lub Ghastly Wail. Blok zużywa się przed rzutem obronnym; wygasa z końcem 3. zwykłej tury odbiorcy. Nie chroni przed normalnymi obrażeniami Bless/Curse ani Divine Judgement/Demonic Decree.',
'Concealment':'Użytkownik, 3 jego zwykłe tury: zwykły wróg nie może wybrać go jako celu, jeśli ma innego legalnego aktywnego przeciwnika bez Concealment. Nie chroni przed obszarem, egzekucją obszarową ani bossem/minibossem. Taunting Aura znosi ten efekt i odwrotnie.',
'Taunting Aura':'Użytkownik, 3 jego zwykłe tury: zwykły wróg wybierający pojedynczy cel musi zaatakować przytomnego użytkownika, jeśli jest to legalne. Przy kilku takich osobach wróg wybiera spośród nich. Nie zmienia obszarów ani wyborów bossa/minibossa. Nie pozwala wymusić innej akcji niż zaplanowana.',
'Ali Dance':'+3 Obrony przeciw wszystkim atakom wymagającym trafienia. Nie daje premii do obrony przed statusem ani egzekucją. Z pasywnych premii do Obrony stosuj tylko najwyższą; Sukukaja działa osobno.',
'Angelic Grace':'+3 Obrony przeciw 8 typom magii od Fire do Curse; bez Almighty, Physical, Gun i czystych statusów. Tylko najwyższa pasywna premia do Obrony.',
'Firm Stance':'Ataki wymagające rzutu trafiają użytkownika automatycznie, lecz ich obrażenia po premiach są dzielone przez 2 przed właściwością i Guard. Dotyczy też trafiających bez rzutu obrażeń All-Out Attack. Nie redukuje kosztów HP, Burn, utraty SP ani egzekucji. Nadal można dostać Down przez Weak; pasywne premie do Obrony są nieaktywne.',
'Divine Grace':'Twoje skille przywracające stałą liczbę HP leczą dodatkowo 5 HP na cel. Nie wzmacnia pełnego/procentowego leczenia, regeneracji, wskrzeszania ani przedmiotów. Łączy się z bonusem Arkany do leczenia.',
'Fast Heal':'Gdy otrzymujesz jeden z 12 zwykłych statusów, skróć jego naturalny czas o 1 zwykłą turę, minimum do 1. Nie zmienia czasu trwania Fear/Despair rozliczanego specjalnie ani osłabień statystyk. Nie sumuje się z Insta-Heal.',
'Insta-Heal':'Na początku swojej następnej zwykłej tury usuń wszystkie 12 zwykłych statusów, zanim sprawdzisz możliwość działania i obrażenia/utratę SP na koniec tury. To nie dodatkowa akcja. Nie usuwa Down, nokautu, buffów ani debuffów.',
'Fortify Spirit':'Stałe +4 do rzutów obronnych przeciw wszystkim 12 zwykłym statusom. Nie sumuje się z Resist danego statusu: stosuj najwyższą premię. Nie chroni przed egzekucją.',
'Endure':'Raz na walkę, gdy obrażenia z ataku obniżyłyby twoje HP do 0, pozostajesz na 1 HP. Nie działa na koszt HP, Burn, egzekucję ani fabularną śmierć. Wspólne jedno użycie z Enduring Soul.',
'Enduring Soul':'Jak Endure, ale po przetrwaniu odzyskujesz połowę maksymalnego HP, w dół, minimum 1. Wspólne jedno użycie z Endure; wybierz mocniejszy efekt. Nie usuwa statusów.',
'Survival Trick':'Raz na walkę, gdy nieudana obrona przed Hama/Mudo lub Ghastly Wail miałaby cię znokautować, pozostajesz na 1 HP. Nie działa na normalne obrażenia. Po zużyciu nie chroni ponownie; działa niezależnie od Endure.',
'Life Aid':'Po zwycięstwie lub udanym Hold Up odzyskaj 5 HP i 2 SP. Bez ucieczki i porażki; raz za całe spotkanie. Z Victory Cry działa tylko mocniejszy efekt.',
'Victory Cry':'Po zwycięstwie lub udanym Hold Up odzyskaj 10 HP i 5 SP. Bez ucieczki i porażki; raz za całe spotkanie. Zastępuje Life Aid. Celowo ograniczona wersja pełnego odnowienia z P5R.',
'Heat Up':'Jeśli twoja drużyna rozpoczęła walkę z surprise, na końcu każdej z pierwszych 3 własnych zwykłych tur odzyskaj 2 HP i 1 SP. Tylko przytomny aktywny użytkownik. Z Regenerate/Invigorate wybierz wyższą odnowę osobno dla HP i SP.',
'Soul Chain':'Pierwszy raz w walce, gdy otrzymujesz Baton Pass, odzyskaj 2 SP, nawet jeśli wykorzystasz akcję bez skilla. Nie działa przy samym przekazaniu ani przy One More.',
"Touch n' Go":'Pierwszy otrzymany Baton Pass w walce nakłada na ciebie Sukukaja na 3 twoje zwykłe tury, bez akcji i SP. Nie kumuluje się z Sukukaja; tylko odnawia czas.',
'Last Stand':'Jeśli wrogowie rozpoczęli walkę z surprise, masz +3 Obrony do końca tej walki. Tylko najwyższa pasywna premia do Obrony.',
'Pressing Stance':'Jeśli wrogowie rozpoczęli walkę z surprise, masz +3 Obrony do końca tej walki. Ten sam efekt co Last Stand; nie sumują się.',
'Ambient Aid':'Przy szczególnej pogodzie ogłoszonej przez GM przed walką: +2 DC nakładanych przez ciebie zwykłych statusów. To ta sama rodzina co Ailment Boost i boost konkretnego statusu: tylko najwyższa premia. Bez wpływu na egzekucje.',
'Climate Decorum':'Przy szczególnej pogodzie ogłoszonej przez GM przed walką: +2 Obrony. Tylko najwyższa pasywna premia do Obrony. Bez wpływu na obronę przed statusem.',
'Magic Ability':'+2 obrażenia do twoich standardowych magicznych ataków z kośćmi, także Almighty. To rodzina Boost/Amp: z inną premią tej rodziny wybierz najwyższą. Bez leczenia, egzekucji, wysysania, procentów HP i All-Out Attack.',
'Hama Boost':'+2 DC twoich egzekucji Bless z rodziny Hama. Nie wzmacnia obrażeń Kouha ani szans zwykłego statusu. Łączy się tylko z modyfikatorem Weak/Resist do DC egzekucji.',
'Mudo Boost':'+2 DC twoich egzekucji Curse z rodziny Mudo. Nie wzmacnia obrażeń Eiha ani szans zwykłego statusu. Łączy się tylko z modyfikatorem Weak/Resist do DC egzekucji.',
}

def adapt(g):
    name=g['skill'];v=skills[name];typ=v['a'][1];b=v['b'];c=v.get('c',['-','-','-']);area=v['a'][2]=='All foes'
    if name in fixed:return fixed[name]
    if typ in ('phy','gun'):
        tier=multi.get(name) or ('colossal' if b[2]>=350 else 'severe' if b[2]>=210 else 'heavy' if b[2]>=120 else 'medium' if b[2]>=70 else 'light')
        if name=='Miracle Punch':tier='medium'
        effect=f"Atak {element[typ]}; {'wszyscy wrogowie' if area else '1 wróg'}; {tier}, {dice[tier]}."
        if name in multi:effect+=' Cała seria: jeden rzut trafienia na cel i jeden wspólny rzut obrażeń, bez mnożenia trafień.'
        if c[0] in statuses:
            dc=min(19,max(2,(int(b[7])+4)//5+1));effect+=f' Po trafieniu i utracie HP: {c[0]}, obrona d20 przeciw DC {dc}; jeden test na cel.'
        if 'Baton Pass' in c[0]:effect+=' Jeśli wykonujesz tę akcję z otrzymanego Baton Pass, +4 obrażenia przed właściwością i Guard.'
        if name=='Cornered Fang':effect+=' Można użyć tylko w walce rozpoczętej z surprise wrogów; przez całe takie starcie.'
        if name in ('Lucky Punch','Miracle Punch'):effect+=' +2 do trafienia tym skillem; zastępuje wyróżnik krytyków, których nie używamy.'
        if name=='One-shot Kill':effect+=' To normalne obrażenia Gun, bez egzekucji.'
        return effect
    if typ in element and typ not in ('alm','phy','gun'):
        if 'instakill' in c[0]:
            dc=11 if 'on' in name.lower() else 6
            return f"Egzekucja {element[typ]}; {'wszyscy wrogowie' if area else '1 wróg'}. Bez rzutu trafienia; obrona celu d20 przeciw DC {dc}. Zwykły Shadow i bohater/NPC po porażce: 0 HP; miniboss/boss: zamiast tego 20 obrażeń właściwego typu, potem Guard. Sukces: brak efektu. Właściwości i osłony według wspólnej reguły egzekucji; bez Down i One More."
        effect=f"Atak {element[typ]}; {'wszyscy wrogowie' if area else '1 wróg'}; severe, 3d6 + 14."
        if c[0] in statuses:effect+=f' Po trafieniu i utracie HP: {c[0]}, obrona DC 6; jeden test na cel.'
        return effect
    if typ=='sup':
        if name.endswith(' Break'):
            el=alias.get(c[0],c[0]);return f'Wszyscy wrogowie, bez rzutu: przez 3 zwykłe tury każdego celu jego Resist {el} staje się Normal. Nie tworzy Weak; nie usuwa Null, Drain, Repel ani innych odporności. Przykrywa również Resist z Wall; po końcu wraca aktualna właściwość.'
        if name.endswith(' Wall'):
            el=alias.get(c[0],c[0]);return f'1 sojusznik, także użytkownik: Resist {el} przez 3 jego zwykłe tury. Zastępuje Normal lub Weak; nie osłabia Null, Repel ani Drain. Bez rzutu; ponowienie odnawia czas. Odpowiedni Break czasowo znosi tę ochronę.'
        base=c[0]
        if base in ('Tarukaja','Rakukaja','Sukukaja','Tarunda','Rakunda','Sukunda'):
            meaning={'Tarukaja':'+4 obrażenia z ataków','Rakukaja':'−4 otrzymywane obrażenia z ataków','Sukukaja':'+2 do trafienia i +2 Obrony','Tarunda':'−4 obrażenia z ataków','Rakunda':'+4 otrzymywane obrażenia z ataków','Sukunda':'−2 do trafienia i −2 Obrony'}[base]
            target='wszyscy aktywni sojusznicy, także użytkownik' if name.endswith('kaja') else 'wszyscy wrogowie'
            return f'{target.capitalize()}: {meaning} przez 3 zwykłe tury każdego celu, bez rzutu. Wersja obszarowa {base}; ten sam parametr nie kumuluje się, przeciwne efekty znoszą się parami.'
    if typ=='pas':
        if name.startswith(('Regenerate ','Invigorate ')):
            n=int(name[-1]);resource='HP' if name.startswith('Regenerate') else 'SP';amount=n*2 if resource=='HP' else n
            return f'Na końcu każdej z pierwszych 3 własnych zwykłych tur walki odzyskaj {amount} {resource}, jeśli jesteś przytomny i aktywny. Tylko najwyższy stopień tej rodziny; z Heat Up wybierz wyższą odnowę dla danego zasobu. Bez odnowy poza walką i w rezerwie.'
        if name.startswith('Growth '):
            n=int(name[-1]);return f'Zamiennik RPG: +{2*n} maksymalnego HP i +{n} maksymalnego SP, gdy skill jest nauczony. Tylko najwyższy Growth. Bez dodatkowego EXP; bank nie ma osobnego rozwoju. Nauka nie leczy, usunięcie obniża maksima i przycina nadmiar aktualnych zasobów.'
        if name.startswith(('Resist ','Null ','Repel ','Drain ')):
            kind,el=name.split(' ',1);el=alias.get(el,el)
            return f'Zyskujesz {kind} {el}, także gdy początkowo była to słabość. Dla jednego typu wybierz najsilniejszą ochronę: Drain > Repel > Null > Resist > Normal > Weak; nie mnożymy ochron. Kosztuje slot. Usunięcie skilla przywraca pozostałe źródła ochrony; reguły Drain/Repel w opisie wspólnym.'
        if name.startswith(('Dodge ','Evade ')):
            family,el=name.split(' ',1);n=2 if family=='Dodge' else 3;el=alias.get(el,el)
            return f'+{n} Obrony przeciw atakom {el}. Nie zmienia rzutu obrony przed statusem/egzekucją. Z innymi pasywami Obrony tylko najwyższa premia; buff Sukukaja działa osobno.'
        if name in ('Counter','Counterstrike','High Counter'):
            chance={'Counter':19,'Counterstrike':18,'High Counter':17}[name]
            return f'Gdy trafi cię Physical/Gun, przed obrażeniami rzuć d20: {chance}–20 odbija cały atak według reguły pojedynczego odbicia. Jedna seria to jeden test. Wybierz tylko najwyższy Counter; nie testuj, jeśli atak już odbija Tetrakarn lub twoje Repel. To nie akcja ani One More.'
        if name in ('Arms Master','Spell Master'):
            resource='HP' if name=='Arms Master' else 'SP';return f'Koszt twoich skilli w {resource} dziel przez 2, zaokrąglając w górę, minimum 1 dla płatnego skilla. Koszt 0 pozostaje 0. Nie zmienia przedmiotów ani strat z ataków/statusów; z inną zniżką stosuj tylko najniższy końcowy koszt.'
        auto={'Attack Master':'Tarukaja','Defense Master':'Rakukaja','Speed Master':'Sukukaja','Auto-Mataru':'Matarukaja','Auto-Maraku':'Marakukaja','Auto-Masuku':'Masukukaja'}
        if name in auto:return f'Na początku walki automatycznie zastosuj {auto[name]} bez akcji i kosztu na użytkownika'+(' oraz aktywnych sojuszników.' if name.startswith('Auto-') else '.')+' Efekt trwa 3 zwykłe tury odbiorcy. Nakłada się tylko raz, bez ponawiania przy zamianie NPC; identyczne buffy nie sumują się.'
        if name.endswith((' Boost',' Amp')) or name in ('Snipe','Cripple'):
            n=4 if name.endswith(' Amp') or name=='Cripple' else 2
            el='Gun' if name in ('Snipe','Cripple') else alias.get(name.rsplit(' ',1)[0],name.rsplit(' ',1)[0])
            return f'+{n} obrażenia do twoich ataków {el}, przed właściwością i Guard. Bonus raz na cały atak/serię, na każdy trafiony cel. Z Boost/Amp, Snipe/Cripple i Magic Ability działa tylko najwyższa pasująca premia; bez egzekucji, wysysania, procentów HP i All-Out Attack.'
    raise ValueError(('UNMAPPED',name,typ))

rules=[]
for g in gates:
    if g['access']=='A':
        name=g['skill'];effect=adapt(g)
        rules.append({**g,'previous_access':'A','access':'R','cost':catalog[name][3],'target':catalog[name][1],'effect':effect})
assert len(rules)==236
byname={r['skill']:r for r in rules}
for g in gates:
    if g['skill'] in byname:g['access']='R';g['reason']='Gotowe działanie RPG w rozdziale 13.20 podręcznika GM 0.7.'
(R/'skill_rules_0_7.json').write_text(json.dumps(rules,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'skill_level_gates_0_7.json').write_text(json.dumps(gates,ensure_ascii=False,indent=2),encoding='utf-8')

COMMON=[
('Stałe trafienie i Obrona','Bazowe trafienie bohatera to +5, Obrona 12 na wszystkich poziomach 1–99. Awans nie zwiększa tych wartości. Buff, debuff, status i nauczony pasyw mogą je zmieniać według własnego opisu. Premia ataku nie jest premią do obrażeń. Shadows mają wartości z karty, bez automatycznego dodatku za poziom; GM może nadać im odmienny profil.'),
('Pięć stopni obrażeń','Light: 1d6 + 4; medium: 2d6 + 6; heavy: 3d6 + 8; severe: 3d6 + 14; colossal: 3d6 + 20. Średnie to 7,5; 13; 18,5; 24,5; 30,5. To całość bazowych obrażeń. Strength, Magic, źródłowa moc P5R, liczba trafień i procent krytyka nie dodają kolejnych mnożników. Nie wprowadzamy krytyków ani Technical.'),
('Jedna akcja jedna seria','Multi-hit jest jednym atakiem o podanych łącznych obrażeniach. Rzuć raz na trafienie każdego celu, następnie raz wspólnie na obrażenia; właściwości, Guard i status sprawdza każdy cel oddzielnie. Bonusy obrażeń dodaj raz na serię, nie za pocisk. Jeden atak daje najwyżej jedno One More i jeden test statusu na cel. Broń podstawowa i Gun pozostają 1d6 + 4.'),
('Kolejność obrażeń','Kości i płaskie premie/kary, następnie Hunger, następnie Firm Stance, następnie Weak/Resist, na końcu Guard. Minimum 0; zaokrąglij raz w dół na końcu. Charge/Concentrate dodają +8 zamiast mnożnika i łączą się z Tarukaja oraz najwyższym pasywem obrażeń. Efekty wskazane jako stałe, procentowe lub egzekucyjne nie dostają tych premii. Guard zachowuje redukcję 60% i ochronę przed Down.'),
('Rodziny premii','Boost +2 i Amp +4 zastępują mnożniki procentowe. Dla pojedynczego ataku wybierz najwyższą pasującą premię spośród Boost/Amp, Snipe/Cripple i Magic Ability. Tylko najwyższa pasywna premia Obrony oraz najwyższy stopień Counter, Growth, Regenerate i Invigorate. Buff Sukukaja łączy się z pasywną Obroną; Tarukaja łączy się z pasywem obrażeń. Pasujące bonusy Arkany działają osobno według swoich opisów. Ailment Boost/boost konkretnego statusu/Ambient Aid to jedna premia do DC; Foul Breath jest osobnym osłabieniem celu.'),
('Czas i odnowa','O ile opis nie mówi inaczej: buff/debuff trwa 3 kolejne zwykłe tury odbiorcy; dodatkowa akcja nie skraca ani nie wydłuża czasu. Ponowienie odnawia czas bez sumowania. Regenerate, Invigorate i Heat Up działają tylko na końcu pierwszych 3 własnych zwykłych tur tej walki, wyłącznie na przytomnego aktywnego użytkownika. Pominięty impuls przepada. Poza walką nie tykają; zmiana NPC nie zeruje liczników. Każdy z nich zajmuje własny slot skilla.'),
('Ochrony i pojedyncze odbicie','Dla jednego typu stosuj tylko jedną właściwość: Drain > Repel > Null > Resist > Normal > Weak. Pasyw może zakryć początkową słabość; nie zmienia jej zapisu bazowego. Break znosi tylko Resist, a Wall nie osłabia silniejszej ochrony. Pierwszy trafiony atak odbity przez Repel, Karn lub Counter wraca bez nowego rzutu i bez powtórnego dodawania premii. Użytkownik osłony otrzymuje 0 obrażeń i brak statusu. Atakujący rozlicza odbite obrażenia jak Normal, z własnym Firm Stance i Guard; jego Null/Resist/Drain/Repel nie działają na ten powrót. Brak dalszych odbić, Counter, Down, One More i statusów z odbitego ataku. W obszarze odbija tylko część przypadającą na chroniony cel. Drain zamiast obrażeń przywraca HP równe obliczonym obrażeniom przy Normal, najwyżej do maksimum; bez Guard, bez statusu i bez Down.'),
('Egzekucje','Hama/Mudo: DC 6; Hamaon/Mudoon: DC 11, także dla obszarowych odpowiedników. Cel rzuca d20, wynik równy DC broni. Weak zwiększa DC o 2, Resist zmniejsza o 4. Null, Repel i Drain danego typu blokują efekt bez odbicia lub leczenia. Guard daje +4 do tej obrony i zachowuje pozostałą ochronę; premia Obrony z Sukukaja/Dodge nie działa. Tetraja blokuje próbę przed rzutem. Hama/Mudo Boost dodaje 2 do właściwego DC, ale zwykłe premie statusów nie działają. Nie używamy naturalnej 1/20 jako osobnej reguły. Zwykły Shadow oraz bohater/NPC po porażce dostaje nokaut; boss/miniboss zamiast tego 20 obrażeń Bless/Curse, rozliczając właściwość i Guard. Nigdy Down ani One More. Ghastly Wail ma własny warunek Fear i DC 15; Guard +4 i Tetraja działają również na nie.'),
('Ograniczenia regeneracji i zwycięstwa','SP odzyskujemy najwyżej do maksimum. Spirit Drain zabiera tylko istniejące SP; nie daje zasobów z pustego celu. Soul Chain działa raz na walkę. Life Aid i Victory Cry działają raz za rzeczywiste zakończone spotkanie z należnym EXP, również po Hold Up; nie po ucieczce, porażce, treningowej walce z kompanem ani ponownym biciu tej samej przywołanej zdobyczy. Każde ponownie rozegrane spotkanie po odtworzeniu zapisu korzysta z odtworzonego stanu zasobów i użyć.'),
('Nauka i zmiana skilli','Każdy dawny wpis A ma teraz R i pełny opis w tabelach poniżej. Koszty i minimalne poziomy zachowano; 1 punkt nauki lub odpowiednia skill card, maksymalnie 8 skilli razem z pasywami. Próg nie wymaga zakupu słabszej wersji. Z, X i źródłowe traity pozostają poza tym uzupełnieniem. Skille i pasywy można zastępować wyłącznie poza walką; nie wolno wyłączać ich pomiędzy atakiem a rozliczeniem. Zmiana maksymalnego HP/SP nie leczy; utrata bonusu przycina nadmiar aktualnego zasobu. Growth ma jawny zamiennik, bo EXP bohatera i osobistej Persony jest wspólne.'),
]

def pbefore(anchor,text,style=None):return anchor.insert_paragraph_before(text,style)
def set_cell(cell,text):
    cell.text=text
    for p in cell.paragraphs:
        p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1
        for run in p.runs:run.font.size=Pt(8)

def effect_table(doc,items):
    t=doc.add_table(rows=1,cols=4);t.autofit=False
    widths=[3.5,1.3,1.6,11.0]
    for col,w in zip(t.columns,widths):col.width=Cm(w)
    for c,s in zip(t.rows[0].cells,['Skill','Min. lvl','Koszt','Gotowe działanie RPG']):set_cell(c,s)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for r in items:
        for c,s in zip(t.add_row().cells,[r['skill'],str(r['min_level']),r['cost'],r['effect']]):set_cell(c,s)
    for ri,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for cell,w in zip(row.cells,widths):
            cell.width=Cm(w);pr=cell._tc.get_or_add_tcPr()
            border=OxmlElement('w:tcBorders')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');border.append(e)
            pr.append(border)
            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'333333' if ri==0 else ('F3F3F3' if ri%2==0 else 'FFFFFF'));pr.append(shade)
            margins=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'75');e.set(qn('w:type'),'dxa');margins.append(e)
            pr.append(margins)
            for p in cell.paragraphs:
                p.paragraph_format.keep_with_next=ri==0
                for run in p.runs:run.bold=ri==0;run.font.color.rgb=RGBColor.from_string('FFFFFF' if ri==0 else '000000')
    return t

gm=Document(R/SOURCES['gm'])
# Mutate catalog using XML cells to preserve widths and avoid slow table expansion.
changed=0
for t in gm.tables:
    trs=t._tbl.findall(qn('w:tr'))
    cells=trs[0].findall(qn('w:tc'))
    if len(cells)!=7 or ''.join(cells[0].xpath('.//w:t/text()'))!='Umiejętność':continue
    from docx.table import _Cell
    set_cell(_Cell(cells[4],t),'Koszt HB')
    for tr in trs[1:]:
        cells=tr.findall(qn('w:tc'));name=''.join(cells[0].xpath('.//w:t/text()'))
        set_cell(_Cell(cells[4],t),'—' if skills[name]['a'][1]=='tra' else 'HB')
        if name in byname:
            set_cell(_Cell(cells[6],t),f"{byname[name]['min_level']} / R");changed+=1
assert changed==236
anchor=next(p for p in gm.paragraphs if p.style.name=='Heading 1' and p.text.startswith('14 '))
pbefore(anchor,'13.20 Gotowe efekty skilli i wspólne reguły','Heading 2')
pbefore(anchor,'Uzupełnienie obejmuje wszystkie 236 umiejętności wcześniej oznaczonych A. Są teraz dostępne jako R po osiągnięciu zapisanego poziomu. Poniższe efekty są naszym homebrew; źródłowe koszty i liczby P5R w katalogu pozostają odniesieniem. Wszystkie wartości wymagają prób przy stole, szczególnie na wysokich poziomach, lecz do użycia nie trzeba już dopisywać efektu przez GM.')
for title,body in COMMON:
    pbef=pbefore(anchor,title,'Heading 3');pbefore(anchor,body)
groups=[('Physical i Gun',lambda r:r['type'] in ('phy','gun')),('Magia żywiołowa i egzekucje',lambda r:r['type'] in ('fir','ice','ele','win','psy','nuk','ble','cur')),('Almighty',lambda r:r['type']=='alm'),('Leczenie i wskrzeszanie',lambda r:r['type']=='rec'),('Wsparcie i osłony',lambda r:r['type']=='sup'),('Pasywy',lambda r:r['type']=='pas')]
for title,predicate in groups:
    pbef=pbefore(anchor,'Gotowe skille '+title,'Heading 3')
    t=effect_table(gm,[r for r in rules if predicate(r)]);anchor._p.addprevious(t._tbl)
    spacer=pbefore(anchor,'');spacer.paragraph_format.space_after=Pt(4)

replacement={
'Skala obowiązuje w testach zarówno bohaterów, jak i przeciwników. Heavy jest propozycją z próby Zorro i Captain Kidda. Severe, Colossal, Almighty o specjalnej sile oraz wielokrotne trafienia nie mają jeszcze ogólnej skali. Nie dodajemy osobno Strength ani Magic do tych rzutów.':'Skala obowiązuje bohaterów i przeciwników. Severe to 3d6 + 14, a colossal 3d6 + 20; pełne zasady i zsumowane serie ataków podaje rozdział 13.20. Nie dodajemy osobno Strength ani Magic do tych rzutów.',
}
for p in gm.paragraphs:
    old=p.text
    if p.style.name.lower().startswith('toc'):continue
    new=replacement.get(old,old)
    if old.startswith('Nowa kolumna podaje próg homebrew'):
        new='Min. lvl / dostęp podaje próg homebrew: R oznacza gotowy efekt RPG, Z moc unikatową poza zwykłym zakupem, X mechanikę nieaktywną, Ź źródłowy trait P5R. Wszystkie 236 dawnych A mają teraz gotowe efekty w rozdziale 13.20 i status R. Koszt HB to autorski koszt z kolumny Koszt RPG; nie jest oficjalną wartością z gry. Poziom jest warunkiem zakupu, nie automatycznym nauczeniem się; koszt nauki wynosi 1 punkt lub odpowiednią skill card.'
    if old.startswith('Progi magii: light jeden cel'):
        new='Progi magii: light jeden cel 1, light obszar 5, medium jeden cel 10, medium obszar 15, heavy jeden cel 25, heavy obszar 35, severe jeden cel 50 i obszar 65. Almighty, Physical/Gun, wsparcie i pasywy mają osobne progi w wierszach. R wymaga osiągnięcia progu i opłacenia nauki; Z, X i Ź nie stają się dostępne przez sam poziom.'
    if old.startswith('Nie zmieniamy tu dotychczasowych zasad') and 'adapt' in old:pass
    if old.startswith('Wersja 0.6'):new='Wersja 0.7 • 28 października 2026 • pełne efekty 236 skilli i stałe trafienie oraz Obrona'
    new=new.replace('podręcznika gracza 0.3','podręcznika gracza 0.4').replace('podręcznik gracza 0.3','podręcznik gracza 0.4').replace('bestiariusz 0.3','bestiariusz 0.4').replace('bestiariusza 0.3','bestiariusza 0.4')
    if new!=old:p.text=new
# Resolve outdated summary entries and property definitions, keeping numerical fields intact.
for t in gm.tables:
    if len(t.columns)==2:
        for row in t.rows:
            if row.cells[0].text=='Rozwój Persony':row.cells[1].text='Bank, fuzje i karty: rozdział 11. Wszystkie dawne A mają efekty w 13.20; traity P5R nie są dodatkowym traitem bohatera.'
            if row.cells[0].text=='Postać i awans':row.cells[1].text='Tworzenie Persony: podręcznik gracza 0.4. EXP i nauka: rozdział 11. Trafienie +5 i Obrona 12 nie rosną z poziomem.'
    for row in t.rows:
        if len(row.cells)==2 and row.cells[0].text=='Drain':row.cells[1].text='Zamiast obrażeń odzyskujesz HP jak przy Normal, do maksimum; bez Guard i bez statusu. Pełne reguły 13.20.'
        if len(row.cells)==2 and row.cells[0].text=='Repel':row.cells[1].text='Odbija trafiony atak jeden raz. Bez dalszych odbić, statusów i One More; pełne rozliczenie w 13.20.'
base=next(p for p in gm.paragraphs if p.style.name=='Heading 2' and p.text.startswith('2.3 '))
pbefore(base,COMMON[0][1])
gm.core_properties.version='0.7';gm.save(R/OUT['gm'])

player=Document(R/SOURCES['player'])
for p in player.paragraphs:
    old=p.text
    if p.style.name.lower().startswith('toc'):continue
    new=old
    if old.startswith('Dla poziomu L od 1 do 99'):
        new=old.replace('Początkowy atak i Obrona nie wynikają z wyglądu Persony; do prób zachowujemy robocze +5 ataku i Obronę 12 z dotychczasowego zestawu. Ich rozwój ustalimy razem z awansem.','Bazowe trafienie wynosi +5, a Obrona 12 na wszystkich poziomach 1–99; nie rosną przy awansie i nie wynikają z wyglądu Persony. Skille, statusy i buffy mogą zmieniać je według swoich opisów.')
    if old.startswith('Katalog GM ') and 'kolumnę Min.' in old:
        new='Katalog GM 0.7 podaje Min. lvl / dostęp dla 541 wpisów. R oznacza gotowy efekt RPG; wszystkie dawne 236 wpisów A mają teraz R i dokładne opisy w rozdziale 13.20. Z: unikat poza zwykłym zakupem; X: nieaktywna mechanika; Ź: źródłowy trait P5R bez zakupu. Nadal wymagany jest poziom i 1 punkt nauki lub właściwa skill card.'
    if old.startswith('Gotowe standardowe ataki light/medium/heavy'):
        new='Standardowe ataki: light 1d6 + 4, medium 2d6 + 6, heavy 3d6 + 8, severe 3d6 + 14, colossal 3d6 + 20. Wersja obszarowa: osobny rzut trafienia na cel i wspólny rzut obrażeń. Seria multi-hit ma jedno podane łączne obrażenie, bez mnożenia rzutów. Jeden atak daje najwyżej jedno One More; progi i wyjątki są w katalogu GM 0.7.'
    if old.startswith('Wersja 0.3'):new='Wersja 0.4 • 28 października 2026 • gotowe skille i stałe trafienie oraz Obrona'
    new=new.replace('GM 0.6','GM 0.7').replace('bestiariusza 0.3','bestiariusza 0.4').replace('bestiariusz 0.3','bestiariusz 0.4')
    if new!=old:p.text=new
for t in player.tables:
    for row in t.rows:
        for c in row.cells:
            if 'wymaga adaptacji obrażeń' in c.text:c.text=c.text.replace('; wymaga adaptacji obrażeń','')
            if 'GM 0.6' in c.text:c.text=c.text.replace('GM 0.6','GM 0.7')
player.add_heading('9 Wspólne reguły gotowych skilli',level=1)
player.add_paragraph('W katalogu GM 0.7, rozdział 13.20, znajdziesz pełne działanie wszystkich 236 dawnych skilli A. Każdy jest teraz R. Wybierasz je według progu poziomu, kosztu nauki i limitu ośmiu slotów; nie trzeba już uzgadniać brakującego efektu. Poniżej reguły wspólne potrzebne graczowi.')
for title,body in COMMON:
    player.add_heading(title,level=2);player.add_paragraph(body)
player.core_properties.version='0.4';player.save(R/OUT['player'])

cards=json.loads((R/'persona_skill_cards.json').read_text(encoding='utf-8'))
for card in cards:
    if card['skill_card'] in byname:card['access']='R'
(R/'persona_skill_cards_0_4.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2),encoding='utf-8')
best=Document(R/SOURCES['bestiary']);replaced=0
for el in best.element.body.iter(qn('w:p')):
    from docx.text.paragraph import Paragraph
    p=Paragraph(el,best);old=p.text;new=old
    if old.startswith('Skill card RPG:') and ' / A •' in old:new=old.replace(' / A •',' / R •');replaced+=1
    if old.startswith('Min. Lv i R/A/X dotyczą nauki karty') or old.startswith('Min. Lv i R/A/X'):
        new='Min. Lv i dostęp dotyczą nauki karty. R ma gotowy efekt RPG, X pozostaje nieaktywny, Z jest poza zwykłą nauką. Wszystkie dawne skille A mają teraz R; ich pełne efekty są w rozdziale 13.20 podręcznika GM 0.7. Każda karta zastępuje 1 punkt nauki, lecz nie próg poziomu ani limit 8 slotów.'
    new=new.replace('Wersja 0.3','Wersja 0.4').replace('GM 0.6','GM 0.7').replace('gracza 0.3','gracza 0.4')
    if new!=old:p.text=new
for section in best.sections:
    for p in section.footer.paragraphs:
        for run in p.runs:
            if '0.3' in run.text:run.text=run.text.replace('0.3','0.4')
best.core_properties.version='0.4';best.save(R/OUT['bestiary'])
audit={'outputs':OUT,'source_hashes':hashes,'completed_skills':236,'ready_skills':sum(g['access']=='R' for g in gates),'remaining_A':sum(g['access']=='A' for g in gates),'bestiary_cards_updated':replaced,'groups':{title:sum(pred(r) for r in rules) for title,pred in groups},'costs_and_thresholds_preserved':True}
(R/'skill_completion_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
for name,sha in hashes.items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha
print(json.dumps(audit,ensure_ascii=False,indent=2))
