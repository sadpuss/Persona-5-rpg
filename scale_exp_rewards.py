from pathlib import Path
from bisect import bisect_right
from collections import Counter
import json,hashlib,re
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

R=Path(__file__).parent
sources={'gm':R/'Persona_5_RPG_Podrecznik_GM_0_5.docx','player':R/'Persona_5_RPG_Podrecznik_Gracza_0_2.docx'}
outputs={'gm':R/'Persona_5_RPG_Podrecznik_GM_0_6.docx','player':R/'Persona_5_RPG_Podrecznik_Gracza_0_3.docx'}
assert not any(x.exists() for x in outputs.values())
hashes={tag:hashlib.sha256(p.read_bytes()).hexdigest() for tag,p in sources.items()}
coefficients={'easy':10,'normal':20,'hard':35,'miniboss':60,'boss':120,'investigation':20,'goal':50}
thresholds=[50*(l-1)*l for l in range(1,100)]
study=[]
for level in range(1,100):
    rewards={name:k*level for name,k in coefficients.items()}
    row={'challenge_level':level,'next_step_if_not_capped':100*level,**rewards}
    if level<99:
        assert rewards['normal']*5==100*level
        assert all(abs(rewards[name]/(100*level)-coefficients[name]/100)<1e-12 for name in coefficients)
        total=thresholds[level-1]+180*level
        result=bisect_right(thresholds,total)
        row['route_5_normals_miniboss_clue_exp']=180*level
        row['route_level_from_exact_threshold']=result
        row['route_next_step_fraction']=None if result==99 else (total-thresholds[result-1])/(100*result)
        assert result==level+1
        if result<99:assert .4<=row['route_next_step_fraction']<.8
    study.append(row)
(R/'exp_rewards_by_level.json').write_text(json.dumps(study,ensure_ascii=False,indent=2),encoding='utf-8')

def new_table(doc):
    cols=['Poziom wyzwania N','Łatwa','Zwykła','Trudna','Miniboss','Boss','Postęp śledztwa','Cel historii']
    widths=[1.8,1.9,1.9,1.9,2.0,2.2,2.9,2.8]
    assert abs(sum(widths)-17.4)<1e-8
    table=doc.add_table(rows=1,cols=8);table.autofit=False
    for col,width in zip(table.columns,widths):col.width=Cm(width)
    for cell,text in zip(table.rows[0].cells,cols):cell.text=text
    for row in study:
        values=[row['challenge_level']]+[row[k] for k in coefficients]
        for cell,value in zip(table.add_row().cells,values):cell.text=f'{value:,}'.replace(',',' ')
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for ri,row in enumerate(table.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for cell,width in zip(row.cells,widths):
            cell.width=Cm(width);pr=cell._tc.get_or_add_tcPr()
            borders=OxmlElement('w:tcBorders')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
            pr.append(borders)
            margin=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'65');e.set(qn('w:type'),'dxa');margin.append(e)
            pr.append(margin)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EAEAEA');pr.append(sh)
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1
                p.paragraph_format.keep_with_next=ri==0
                for run in p.runs:run.font.size=Pt(8.5);run.bold=ri==0;run.font.color.rgb=RGBColor(0,0,0)
    return table

for tag,path in sources.items():
    doc=Document(path)
    for p in doc.paragraphs:
        text=p.text
        if tag=='gm' and p.style.name=='Heading 2' and re.match(r'^11\.(\d+) ',text):
            m=re.match(r'^11\.(\d+) (.*)',text)
            if int(m[1])>=3:p.text=f'11.{int(m[1])+1} {m[2]}'
        elif 'Jako prostą propozycję nauki dodajemy 1 punkt nauki za poziom uzyskany od 2 wzwyż.' in text:
            p.text=text.replace('Jako prostą propozycję nauki dodajemy 1 punkt nauki za poziom uzyskany od 2 wzwyż.','Za każdy poziom uzyskany od 2 wzwyż otrzymujesz 1 punkt nauki. Każdy skill kosztuje dokładnie 1 punkt nauki, ale wymaga minimalnego poziomu i gotowego opisu działania.')
        elif text.startswith('Wersja 0.5') and tag=='gm':p.text='Wersja 0.6 • 28 października 2026 • przeliczone nagrody EXP na poziomach 1–99'
        elif text.startswith('Wersja 0.2') and tag=='player':p.text='Wersja 0.3 • 28 października 2026 • punkty nauki i pełne skalowanie EXP'
    anchor=next(p for p in doc.paragraphs if p.style.name=='Heading 2' and p.text.endswith('Tabela poziomów od 1 do 99'))
    title='11.3 Skalowanie nagród dla poziomów 1 do 99' if tag=='gm' else 'Skalowanie nagród dla poziomów 1 do 99'
    anchor.insert_paragraph_before(title,'Heading 2')
    anchor.insert_paragraph_before('Przeliczono wszystkie 98 przejść między poziomami. Nagrody muszą skalować się poziomem wyzwania N: stałe 200 EXP za walkę to 200% kosztu najbliższego awansu na poziomie 1, 20% na poziomie 10, 4% na 50 i około 2,04% na 98. Dlatego nie używamy wartości z przykładu N = 10 przez całą kampanię. Zachowujemy dotychczasowe mnożniki, a konkretne kwoty podaje tabela poniżej.')
    anchor.insert_paragraph_before('Gdy N = poziom bohatera L, łatwa walka daje 10% kosztu następnego awansu, zwykła 20%, trudna 35%, miniboss 60%, boss 120%, postęp śledztwa 20%, a cel historii 50%. Te proporcje są identyczne od poziomu 1 do 98. Pięć zwykłych starć z N równym początkowemu L daje dokładnie jeden awans od progu. EXP za jedną scenę liczymy dla ustalonego N; po drodze nie podnosimy nagrody za ten sam zaplanowany przeciwnik.')
    anchor.insert_paragraph_before('Trasa pięciu zwykłych walk, minibossa i tropu daje 180 × N EXP. Od początku poziomu 1 oznacza to poziom 2 i 40% drogi do 3; od początku poziomu 10 — poziom 11 i około 72,7% drogi do 12; od początku poziomu 50 — poziom 51 i około 78,4% drogi do 52. Przy poziomie 98 taka trasa osiąga limit 99. Różnica tempa na pierwszych poziomach wynika z większego względnego wzrostu progu; nie wymaga osobnej tabeli nagród ani ręcznych wyjątków. To weryfikacja matematyki EXP, nie potwierdzenie balansu walk na wszystkich poziomach.')
    anchor.insert_paragraph_before('Tabela podaje EXP dla każdego bohatera za całe spotkanie. N to zapisany przez GM poziom wyzwania, nie automatycznie aktualny poziom gracza ani suma poziomów Shadows. Za słabszego przeciwnika pozostaje niższe N, więc rozwój nie przyspiesza przez powtarzanie łatwych scen. Wiersz N = 99 opisuje nagrodę za wyzwanie końcowe dla postaci poniżej limitu; bohater na poziomie 99 nie otrzymuje dalszych awansów ani punktów nauki i może zakończyć księgowanie EXP. Próg poziomu 99 pozostaje 485 100.')
    table=new_table(doc);anchor._p.addprevious(table._tbl)
    for p in doc.paragraphs:
        updated=p.text.replace('podręcznika gracza 0.2','podręcznika gracza 0.3').replace('podręcznik gracza 0.2','podręcznik gracza 0.3').replace('GM 0.5','GM 0.6').replace('bestiariusz 0.2','bestiariusz 0.3').replace('bestiariusza 0.2','bestiariusza 0.3')
        if updated!=p.text:p.text=updated
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if 'GM 0.5' in p.text:p.text=p.text.replace('GM 0.5','GM 0.6')
    doc.core_properties.version='0.6' if tag=='gm' else '0.3'
    doc.save(outputs[tag])
    check=Document(outputs[tag]);reward=next(t for t in check.tables if t.cell(0,0).text=='Poziom wyzwania N')
    assert len(reward.rows)==100
    for level,row in enumerate(reward.rows[1:],1):
        vals=[int(c.text.replace(' ','')) for c in row.cells]
        assert vals==[level]+[level*k for k in coefficients.values()]
    exp=next(t for t in check.tables if len(t.columns)==4 and t.cell(0,0).text=='Poziom')
    assert len(exp.rows)==100 and exp.rows[-1].cells[1].text=='485 100'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==hashes[tag]
report={'source_hashes':hashes,'outputs':{tag:str(p) for tag,p in outputs.items()},'rows_per_reward_table':99,'transitions_checked':98,'coefficients':coefficients,'normal_fights_per_level_at_equal_challenge':5,'normal_reward_fraction':.2,'learning_cost_per_skill':1,'skill_minimum_levels_still_required':True,'old_files_unchanged':True}
(R/'exp_scaling_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
