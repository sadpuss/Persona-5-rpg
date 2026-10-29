from pathlib import Path
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import json,csv

R=Path(__file__).parent
mapping=json.loads((R/'persona_skill_cards.json').read_text(encoding='utf-8'))
for item in mapping:
    if item['persona']=='Magatsu-Izanagi':
        item['skill_card']='Eiha';item['min_skill_level']=1;item['access']='R'
        item['reason']='Autorski podstawowy Curse: naturalne skille dostępne na bazowym poziomie są mocami unikatowymi.'
(R/'persona_skill_cards.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
with (R/'persona_skill_cards.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=mapping[0].keys());w.writeheader();w.writerows(mapping)

for filename in ['Persona_5_RPG_Podrecznik_GM_0_5.docx','Persona_5_RPG_Podrecznik_Gracza_0_2.docx','Persona_5_RPG_Bestiariusz_0_2.docx']:
    path=R/filename;doc=Document(path)
    for par in doc.paragraphs:
        text=par.text
        if 'Dla Necronomiconu, który nie ma zwykłego kwalifikującego się skilla' in text:
            par.text=text.replace('Dla Necronomiconu, który nie ma zwykłego kwalifikującego się skilla, przyjęto Sukukaja jako jawny zamiennik wsparcia.','Wyjątki bez zwykłego kwalifikującego się skilla na bazowym poziomie: Necronomicon daje Sukukaja jako zamiennik wsparcia, a Magatsu-Izanagi podstawowe Eiha zgodne z jego typem Curse.')
        elif 'Wyjątek: Necronomicon → Sukukaja' in text:
            par.text=text.replace('Wyjątek: Necronomicon → Sukukaja jako autorskie wsparcie.','Wyjątki bez zwykłego kwalifikującego się skilla na bazowym poziomie: Necronomicon → Sukukaja jako wsparcie; Magatsu-Izanagi → Eiha zgodne z jego typem Curse.')
    if 'Bestiariusz' in filename:
        active_name=None
        for par in doc.paragraphs:
            if par.style.name=='Heading 2' and '  Lv ' in par.text:active_name=par.text.split('  ',2)[-1] if False else par.text.split('  ')[-1]
            if active_name=='Magatsu-Izanagi' and par.text.startswith('Skill card RPG:'):
                par.text='Skill card RPG: Eiha • min. Lv 1 / R • HB'
    if 'GM_0_5' in filename:
        title=next(p for p in doc.paragraphs if p.text=='Spis treści')
        first=next(p for p in doc.paragraphs if p.style.name=='Heading 1')
        node=title._p.getnext()
        while node is not first._p:
            nxt=node.getnext();node.getparent().remove(node);node=nxt
        start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),'19000');start.set(qn('w:name'),'GM_Spis')
        end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),'19000');title._p.append(start);title._p.append(end)
        toc=first.insert_paragraph_before()
        for typ in ['begin','separate','end']:
            run=OxmlElement('w:r');field=OxmlElement('w:fldChar');field.set(qn('w:fldCharType'),typ);run.append(field);toc._p.append(run)
            if typ=='begin':
                run=OxmlElement('w:r');inst=OxmlElement('w:instrText');inst.set(qn('xml:space'),'preserve');inst.text=' TOC \\o "1-2" \\h \\z \\u ';run.append(inst);toc._p.append(run)
            elif typ=='separate':
                run=OxmlElement('w:r');txt=OxmlElement('w:t');txt.text='Spis do przeliczenia w Wordzie.';run.append(txt);toc._p.append(run)
    doc.save(path)
print('Restored GM table of contents and assigned Magatsu-Izanagi a themed HB card Eiha.')
