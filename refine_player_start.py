from pathlib import Path
import json,csv
from docx import Document
from docx.oxml.ns import qn

R=Path(__file__).parent
player_path=R/'Persona_5_RPG_Podrecznik_Gracza_0_1.docx'
p=Document(player_path)
removed=0
for par in list(p.paragraphs):
    if not par.text.strip() and not list(par._p.iter(qn('w:fldChar'))) and not list(par._p.iter(qn('w:drawing'))):
        par._p.getparent().remove(par._p);removed+=1
for table in p.tables:
    for cell in table.rows[0].cells:
        for par in cell.paragraphs:par.paragraph_format.keep_with_next=True
p.save(player_path)
gm_path=R/'Persona_5_RPG_Podrecznik_GM_0_4.docx'
g=Document(gm_path)
gates=json.loads((R/'skill_level_gates.json').read_text(encoding='utf-8'))
fixed={r['skill'] for r in gates if r['type']=='ail' and r['min_level']==11}
for r in gates:
    if r['skill'] in fixed:r['min_level']=10
for table in g.tables:
    for cell in table.rows[0].cells:
        for par in cell.paragraphs:par.paragraph_format.keep_with_next=True
    if len(table.columns)==7 and table.cell(0,0).text=='Umiejętność':
        for row in table.rows[1:]:
            if row.cells[0].text in fixed:row.cells[6].text='10 / R'
g.save(gm_path)
(R/'skill_level_gates.json').write_text(json.dumps(gates,ensure_ascii=False,indent=2),encoding='utf-8')
with (R/'skill_level_gates.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=gates[0].keys());writer.writeheader();writer.writerows(gates)
print('Removed empty spacer paragraphs:',removed,'; normalized status thresholds:',sorted(fixed))
