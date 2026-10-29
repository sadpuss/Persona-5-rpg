from pathlib import Path
import json
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
R=Path(__file__).parent
rules=json.loads((R/'skill_rules_0_7.json').read_text(encoding='utf-8'))
for r in rules:
    if r['skill'] in ('Inferno','Diamond Dust','Thunder Reign','Ice Age'):r['effect']=r['effect'].replace('DC 6','DC 7')
(R/'skill_rules_0_7.json').write_text(json.dumps(rules,ensure_ascii=False,indent=2),encoding='utf-8')
byname={r['skill']:r for r in rules}
f=R/'Persona_5_RPG_Podrecznik_GM_0_7.docx';d=Document(f)
for t in d.tables:
    if len(t.columns)==2 and t.cell(0,0).text=='Obszar':
        for row in t.rows:
            if row.cells[0].text=='Opcjonalne rozszerzenia walki':row.cells[1].text='Serie multi-hit i egzekucje mają gotowe zasady w 13.20. Krytyki i Technical są pominięte; moce Z, alarm i wypadki fuzji pozostają poza zwykłymi zasadami.'
    if len(t.columns)==4 and t.cell(0,3).text=='Gotowe działanie RPG':
        for row in t._tbl.findall(qn('w:tr'))[1:]:
            cells=row.findall(qn('w:tc'));name=''.join(cells[0].xpath('.//w:t/text()'))
            if name in ('Inferno','Diamond Dust','Thunder Reign','Ice Age'):
                for el in cells[3].iter(qn('w:p')):
                    p=Paragraph(el,d)
                    for run in p.runs:run.text=run.text.replace('DC 6','DC 7')
d.save(f)
print('Final consistency corrections complete')
