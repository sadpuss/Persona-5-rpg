from pathlib import Path
import json,re
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
R=Path(__file__).parent
rules=json.loads((R/'skill_rules_0_7.json').read_text(encoding='utf-8'))
fast='Po rozliczeniu jednej własnej zwykłej tury pod wpływem danego zwykłego statusu usuń go na początku następnej zwykłej tury, przed sprawdzaniem możliwości działania. Wcześniejsze naturalne zakończenie nadal działa. Obejmuje wszystkie 12 zwykłych statusów, także Despair; nie usuwa Down, nokautu ani debuffów. Z Insta-Heal działa tylko szybszy efekt.'
for r in rules:
    r['reason']='Gotowy efekt RPG w rozdziale 13.20 podręcznika GM 0.7.'
    if r['skill']=='Fast Heal':r['effect']=fast
(R/'skill_rules_0_7.json').write_text(json.dumps(rules,ensure_ascii=False,indent=2),encoding='utf-8')
names=['Persona_5_RPG_Podrecznik_GM_0_7.docx','Persona_5_RPG_Podrecznik_Gracza_0_4.docx','Persona_5_RPG_Bestiariusz_0_4.docx']
for name in names:
    d=Document(R/name)
    for el in d.element.body.iter(qn('w:p')):
        p=Paragraph(el,d);old=p.text;new=old
        if p.style.name.lower().startswith('toc'):continue
        if old.startswith('Dla poziomu L od 1 do 99'):
            new=old[:old.index('Początkowy atak i Obrona')]+'Bazowe trafienie wynosi +5, a Obrona 12 na wszystkich poziomach 1–99; nie rosną przy awansie. Skille, statusy i buffy mogą je zmieniać według swoich opisów.'
        if old.startswith('Minimum poziomu i dostępność R/A/Z/X/Ź'):
            new='Minimum poziomu i dostępność R/Z/X/Ź obowiązują także karty. Wszystkie dawne A mają teraz R i gotowe działanie z rozdziału 13.20 GM 0.7. X pozostaje nieaktywne, a Z i Ź nie są dostępne przez zwykłą naukę. Nie zużywamy karty, której nie da się legalnie nauczyć. Posiadanie skilla nie zmniejsza kosztu HP/SP jego użycia. Ponowne nauczenie się zapomnianego skilla wymaga nowej karty lub punktu nauki; nie ma darmowego przełączania zapamiętanej biblioteki.'
        if old.startswith('Wyjątki zachowujące poprzednie próby:'):
            new='Wyjątki HP zachowujące poprzednie próby: Sandman 28 HP, Sui-Ki 36, Nekomata 28, Rakshasa 34, Orobas 30. We wszystkich zwykłych roboczych profilach RPG trafienie wynosi +4, a Obrona 12, bez wzrostu z poziomem. Bohater ma bazowe +5 i Obronę 12. GM może nadać konkretnemu przeciwnikowi inny profil, ale nie dodaje premii tylko za jego poziom.'
        if name.endswith('Bestiariusz_0_4.docx'):
            if old.startswith('RPG: atak '):new=re.sub(r'^RPG: atak \+\d+; Obrona \d+;','RPG: atak +4; Obrona 12;',old)
            if old.startswith('Interakcje: Brak dodatkowego wyjątku w tym profilu;'):
                new='Interakcje: Skille R i pasywy według GM 0.7, rozdział 13.20; nie dodawaj całej źródłowej listy do profilu. Moce Z pozostają osobnymi wyjątkami.'
            if old.startswith('Karta RPG daje HP, SP, premię ataku'):
                new='Karta RPG daje HP, SP, trafienie, Obronę, właściwości i jeden prosty atak specjalny oraz darmowy atak light Physical. To profil zwykłego przeciwnika, nie automatyczny miniboss. Pełne efekty skilli R i pasywów podaje GM 0.7, rozdział 13.20; ich dodanie do tego profilu zmienia jego trudność. Źródłowe traity i moce Z nie są automatycznym wyposażeniem RPG.'
            if old.startswith('Odbicie / absorpcja. Zachowane jako cechy'):
                new='Odbicie / absorpcja według wspólnej reguły GM 0.7, rozdział 13.20; jeden powrót obrażeń, bez pętli odbić.'
            if old.startswith('Wersja 0.4'):new='Wersja 0.4 • 28 października 2026 • gotowe skill cards i stałe trafienie oraz Obrona'
            new=new.replace('persona_skill_cards.csv','persona_skill_cards_0_4.json')
        if old.startswith('Sześć podstawowych buffów i debuffów działa'):
            new=old.replace('następnie Hunger, Weak/Resist i Guard.','następnie Hunger, ewentualne Firm Stance, Weak/Resist i Guard.')
        if new!=old:p.text=new
    if 'GM_0_7' in name:
        for t in d.tables:
            if len(t.columns)==4 and t.cell(0,0).text=='Skill' and t.cell(0,3).text=='Gotowe działanie RPG':
                for row in t.rows:
                    if row.cells[0].text=='Fast Heal':row.cells[3].text=fast
            if len(t.columns)==3 and t.cell(0,0).text=='Siła':
                if len(t.rows)==4:
                    for vals in [('Severe','3d6 + 14','24,5'),('Colossal','3d6 + 20','30,5')]:
                        for cell,s in zip(t.add_row().cells,vals):cell.text=s
    d.save(R/name)
print('REFINED 3 DOCX')
