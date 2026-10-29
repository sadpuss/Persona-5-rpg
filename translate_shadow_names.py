from pathlib import Path
import json
from docx import Document

R=Path(__file__).parent
translations={
'Abyssal King of Avarice':'Otchłanny Król Chciwości',
'Ambassador of Filth':'Ambasador Plugastwa',
'Apprentice in a Jug':'Uczeń w Dzbanie',
'Arrogant Vulture':'Arogancki Sęp',
'Ascended Feline':'Wyniesiony Kot',
'Auspicious Pachyderm':'Szczęśliwy Gruboskórzec',
'Awakened God':'Przebudzony Bóg',
'Battle Fiend':'Demon Bitewny',
'Bearer of the Scales':'Dzierżyciel Wagi',
'Bedside Brute':'Bestia Przy Łóżku',
'Beguiling Girl':'Zwodnicza Dziewczyna',
'Bloodthirsty Demoness':'Krwiopijcza Demonica',
'Bringer of Misfortune':'Zwiastun Nieszczęścia',
'Brutal Cavalryman':'Okrutny Kawalerzysta',
'Captivating Dancer':'Urzekająca Tancerka',
'Cavern Snakeman':'Jaskiniowy Wężoczłek',
'Chanting Baboon':'Intonujący Pawian',
'Chivalrous Fiend':'Rycerski Demon',
'Coffin-Borne God':'Bóg Niesiony w Trumnie',
'Corpse Bird':'Ptak Trupów',
'Corpse-Eating Corpse':'Trup Pożerający Zwłoki',
'Cruel Leopard':'Okrutny Lampart',
'Crypt-Dwelling Pyromaniac':'Piroman z Krypty',
'Dancer of Death':'Tancerz Śmierci',
'Dancing Lion':'Tańczący Lew',
'Dancing Witch':'Tańcząca Wiedźma',
'Dark Sun':'Mroczne Słońce',
'Decadent False God':'Zdeprawowany Fałszywy Bóg',
'Defeated Avenger':'Pokonany Mściciel',
'Deformed Lion God':'Zniekształcony Lwi Bóg',
'Destructive Beauty':'Niszczycielskie Piękno',
'Dirty Two-Horned Beast':'Plugawa Dwurożna Bestia',
'Divine Warrior':'Boski Wojownik',
'Dream-Dwelling Skull':'Czaszka ze Snów',
'Drunken Serpents':'Pijane Węże',
'Embittered Blacksmith':'Zgorzkniały Kowal',
'Envoy of Slumber':'Posłaniec Snu',
'Equine Sage':'Koński Mędrzec',
'Evil Synthetic Organism':'Złowrogi Syntetyczny Organizm',
'Evil Voracious Dragon':'Złowrogi Żarłoczny Smok',
'Expressionless Beast':'Bestia Bez Wyrazu',
'Final Assessor':'Sędzia Ostateczny',
'Fire Assassin':'Ognisty Zabójca',
'Foolish Monk':'Głupi Mnich',
'Funerary Warrior':'Wojowniczka Pogrzebowa',
'Fused Ghost':'Zespolony Duch',
'Gallows Flower':'Kwiat Szubienicy',
'Gathering Devil':'Gromadzący się Diabeł',
'Girl of the Hanging Tree':'Dziewczyna z Wisielczego Drzewa',
'Guard Dog of Hades':'Pies Strażniczy Hadesu',
'Harlot of Desire':'Nierządnica Pożądania',
'Heavenly Punisher':'Niebiański Egzekutor',
'Hedonistic Braggart':'Hedonistyczny Przechwałek',
'Heretic Goat':'Heretycki Kozioł',
'Human-Eating Lady':'Ludożercza Dama',
'Hunting Puss in Boots':'Polujący Kot w Butach',
'Hunting Wolf Spirit':'Duch Wilczego Łowcy',
'Infuriated Wisdom King':'Rozwścieczony Król Mądrości',
'Jealous Lover':'Zazdrosna Kochanka',
'Killer Teddy Bear':'Zabójczy Pluszowy Miś',
'Lamenting Sacrifice':'Lamentująca Ofiara',
'Leafy Old Man':'Liściasty Starzec',
'Life-Draining Spirit':'Duch Wysysający Życie',
'Mad Marsh Horse':'Szalony Koń Bagienny',
'Menacing Owlman':'Złowrogi Sowi Człowiek',
'Merciless Inquisitor':'Bezlitosny Inkwizytor',
'Midnight Queen':'Królowa Północy',
'Missionary of Depravity':'Misjonarz Zepsucia',
'Mocking Snowman':'Szyderczy Bałwan',
'Monarch of Snow':'Władca Śniegu',
'Monk of the Valley':'Mnich z Doliny',
'Mountain Girl':'Górska Dziewczyna',
'Night Chimera':'Nocna Chimera',
'Night-Walking Warrior':'Nocny Wędrowny Wojownik',
'Nimble Monkey King':'Zwinny Małpi Król',
'Noisy Mountain Spirit':'Hałaśliwy Duch Gór',
'Pagan Savior':'Pogański Zbawiciel',
'Piggyback Demon':'Demon Jeżdżący na Plecach',
'Possessing Dog Ghost':'Opętujący Psi Duch',
'Prankster Leader':'Przywódczyni Psotników',
'Pulsing Mud':'Pulsujące Błoto',
'Quaking Lady of Shadow':'Drżąca Pani Cienia',
'Raging Bird God':'Rozszalały Ptasi Bóg',
'Raging Water Demon':'Rozszalały Demon Wody',
'Rebellious Elephant':'Buntowniczy Słoń',
'Reviled Dictator':'Znienawidzony Dyktator',
'Rhetorician of the Sea':'Morski Retor',
'Rooftop Lion':'Lew na Dachu',
'Sacrificial Pyrekeeper':'Strażnik Stosu Ofiarnego',
'Samurai Killer':'Zabójca Samurajów',
'Scandalous Queen':'Skandaliczna Królowa',
'Self-Infatuated Star':'Zakochana w Sobie Gwiazda',
'She of Life and Death':'Pani Życia i Śmierci',
'Slithering Snakewoman':'Pełzająca Wężowa Kobieta',
'Spear-Wielding General':'Generał z Włócznią',
'Storm-Invoking Ptarmigan':'Pardwa Przywołująca Burzę',
'Strumming Veena Player':'Artystka Grająca na Winie',
'The Black Avenger':'Czarny Mściciel',
'The Blackened Fury':'Poczerniała Furia',
'The Shadowed One':'Spowita Cieniem',
'Thief of Tablets':'Złodziej Tablic',
'Throbbing King of Desire':'Pulsujący Król Pożądania',
'Thunder Emperor':'Cesarz Piorunów',
'Torn King of Desire':'Rozdarty Król Pożądania',
'Tornado Devil':'Diabeł Tornada',
'Troublesome Housemaid':'Kłopotliwa Służąca',
'Twilight Prostitute':'Nierządnica Zmierzchu',
'Twin-Headed Guardian':'Dwugłowy Strażnik',
'Unfaithful Dream-King':'Niewierny Król Snów',
'Vampire Moth':'Wampiryczna Ćma',
'Vicious Pentagram':'Złowrogi Pentagram',
'Viscid Rotting Meat':'Lepkie Gnijące Mięso',
'Wandering Reviver':'Wędrowny Wskrzesiciel',
'War-Hungry Horseman':'Jeździec Żądny Wojny',
'Warped Abyss':'Wypaczona Otchłań',
'Waterside Nymph':'Nimfa znad Wody',
'Wavering Tree Spirit':'Kołyszący się Duch Drzewa',
'Wishless Star':'Gwiazda Bez Życzeń',
'Woman Who Brings Ruin':'Kobieta Niosąca Zgubę',
'Zealous Messenger':'Gorliwy Posłaniec',
}
treasures={'Crystal Skull':'Kryształowa Czaszka',"Emperor's Amulet":'Amulet Cesarza','Hope Diamond':'Diament Hope','Koh-i-Noor':'Koh-i-Noor','Orichalcum':'Orichalcum','Orlov':'Orlov',"Queen's Necklace":'Naszyjnik Królowej','Regent':'Regent','Stone of Scone':'Kamień ze Scone'}
enemies=json.loads((R/'p5r_enemies.json').read_text(encoding='utf-8-sig'))
assert set(enemies)==set(translations)|{n+' D' for n in treasures}
path=R/'Persona_5_RPG_Bestiariusz_0_1.docx'
doc=Document(path)
count=0
for par in doc.paragraphs:
    if 'Shadow name:' not in par.text:continue
    text=par.text
    for en,pl in sorted(translations.items(),key=lambda pair:-len(pair[0])):
        if en in text:
            text=text.replace(en,f'{en} — {pl}')
            count+=1
    for en,pl in treasures.items():
        token=en+' (Treasure Demon)'
        if token in text:
            text=text.replace(token,f'{en} — {pl} (Demon Skarbów)')
            count+=1
    par.text=text
assert count==129,(count,'shadow names translated')
anchor=next(p for p in doc.paragraphs if p.text.startswith('Dwie różne postacie'))
note=anchor.insert_paragraph_before('Polskie nazwy Shadows są autorskimi tłumaczeniami roboczymi do tej kampanii, nie oficjalną lokalizacją P5R. Przy każdym oryginalnym Shadow name dopisano polski odpowiednik. Nazwy własne Person pozostają bez zmian. Dla Demonów Skarbów zachowano nazwy kamieni i klejnotów; niektóre brzmią identycznie w obu językach.')
for par in doc.paragraphs:
    if par.text.startswith('Wersja 0.1'):par.text='Wersja 0.1 • 28 października 2026 • polskie nazwy Shadows'
backup=R/'Persona_5_RPG_Bestiariusz_0_1_przed_tlumaczeniami.docx'
if not backup.exists():backup.write_bytes(path.read_bytes())
doc.save(path)
(R/'shadow_names_pl.json').write_text(json.dumps({**translations,**{k+' D':v for k,v in treasures.items()}},ensure_ascii=False,indent=2),encoding='utf-8')
check=Document(path)
cards=[p for p in check.paragraphs if 'Shadow name:' in p.text]
assert len(cards)==242
assert sum(p.text.count(' — ') for p in cards if 'brak zwykłego Shadow' not in p.text)==129
print('OK: 129 nazw Shadows ma polskie odpowiedniki; 242 karty zachowane')
