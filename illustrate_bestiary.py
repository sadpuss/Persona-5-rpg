from pathlib import Path
from io import BytesIO
import json,re,hashlib
from PIL import Image,ImageDraw
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

R=Path(__file__).parent
src=R/'Persona_5_RPG_Bestiariusz_0_2.docx';dst=R/'Persona_5_RPG_Bestiariusz_0_3.docx'
# This builder only replaces its own new version; the source remains untouched.
records=json.loads((R/'bestiary_images_manifest.json').read_text(encoding='utf-8'))
assert len(records)==242
qa=R/'qa_exp_scaling_images';qa.mkdir(exist_ok=True)
for start in range(0,242,24):
    sheet=Image.new('RGB',(1500,1200),'#dddddd');draw=ImageDraw.Draw(sheet)
    for j,item in enumerate(records[start:start+24]):
        im=Image.open(item['path']).convert('RGBA');im.thumbnail((225,250))
        x=(j%6)*250;y=(j//6)*300
        sheet.paste(im,(x+(250-im.width)//2,y),im)
        draw.text((x+3,y+253),f"{item['number']:03} {item['persona']}",fill='black')
    sheet.save(qa/f'assets-{start//24+1:02}.png')

doc=Document(src)
orig_tables=[t._tbl for t in doc.tables]
heads=[p for p in doc.paragraphs if p.style.name=='Heading 2' and re.match(r'^\d{3}\s+Lv\s+\d+\s+',p.text)]
assert len(heads)==242
intro=heads[0].insert_paragraph_before('Ilustracje i ich źródła','Heading 2')
heads[0].insert_paragraph_before('Wersja ilustrowana zawiera obraz przy każdym z 242 wpisów. Grafiki przedstawiają odpowiednie formy Person; większość to rendery lub ilustracje, a część wariantów DLC pokazano na zrzutach ekranu. Nie wszystkie grafiki pochodzą z tego samego wydania gry. Autorstwo postaci i grafik: ATLUS / SEGA. Archiwum internetowe: Megami Tensei Wiki. Kliknij „Źródło ilustracji” pod obrazkiem, aby otworzyć stronę wykorzystanego pliku.')
# Keep explanation before first card rather than between its heading and content.
for idx,(head,item) in enumerate(zip(heads,records)):
    assert int(head.text[:3])==item['number'],(head.text,item['persona'])
    paras=[];node=head._p.getnext()
    boundary=heads[idx+1]._p if idx+1<len(heads) else None
    while node is not None and node is not boundary:
        if node.tag==qn('w:p'):
            text=''.join(node.itertext())
            # Use XML style to recognize following headings.
            style=node.find('w:pPr/w:pStyle',namespaces=node.nsmap)
            if style is not None and style.get(qn('w:val')) in ('Heading1','Heading2'):break
            paras.append(node)
        node=node.getnext()
    prefixes=('Arcana:','Profil:','Persona:','Shadow i RPG:','RPG korzysta','RPG:','Skill card RPG:')
    selected=[]
    for el in paras:
        text=''.join(el.xpath('.//w:t/text()'))
        if text.startswith(prefixes):selected.append(el)
    assert sum(''.join(el.xpath('.//w:t/text()')).startswith('Arcana:') for el in selected)==1,(idx,'metadata boundary')
    assert sum(''.join(el.xpath('.//w:t/text()')).startswith('Skill card RPG:') for el in selected)==1,(idx,'skill card boundary')
    table=doc.add_table(rows=1,cols=2);table.autofit=False
    table.columns[0].width=Cm(4.3);table.columns[1].width=Cm(13.3)
    table.rows[0].cells[0].width=Cm(4.3);table.rows[0].cells[1].width=Cm(13.3)
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    borders=OxmlElement('w:tblBorders')
    for side in ['top','bottom','left','right','insideH','insideV']:
        e=OxmlElement('w:'+side);e.set(qn('w:val'),'nil');borders.append(e)
    table._tbl.tblPr.append(borders)
    left,right=table.rows[0].cells
    p=left.paragraphs[0];p.alignment=1;p.paragraph_format.keep_with_next=True
    p.paragraph_format.space_after=Pt(2)
    w,h=item['width'],item['height'];factor=min(3.9/w,3.9/h)
    shape=p.add_run().add_picture(item['path'],width=Cm(w*factor),height=Cm(h*factor))
    shape._inline.docPr.set('descr',item['persona']+' — '+item['file_title'])
    caption=left.add_paragraph();caption.alignment=1;caption.paragraph_format.keep_with_next=True
    caption.paragraph_format.space_after=Pt(3)
    link=OxmlElement('w:hyperlink');link.set(qn('r:id'),doc.part.relate_to(item['file_page'],RT.HYPERLINK,is_external=True))
    run=OxmlElement('w:r');pr=OxmlElement('w:rPr')
    size=OxmlElement('w:sz');size.set(qn('w:val'),'14');pr.append(size)
    col=OxmlElement('w:color');col.set(qn('w:val'),'555555');pr.append(col);run.append(pr)
    text=OxmlElement('w:t');text.text='Źródło ilustracji';run.append(text);link.append(run);caption._p.append(link)
    for empty in list(right._tc):
        if empty.tag==qn('w:p'):right._tc.remove(empty)
    for el in selected:right._tc.append(el)
    if not selected:right.add_paragraph('')
    head._p.addnext(table._tbl)
    # Word otherwise merges two adjacent tables, changing the statistics grid.
    separator=doc.add_paragraph();separator.paragraph_format.space_after=Pt(0)
    separator.paragraph_format.space_before=Pt(0);separator.paragraph_format.line_spacing=Pt(1)
    separator.paragraph_format.keep_with_next=True
    separator.add_run('').font.size=Pt(1)
    table._tbl.addnext(separator._p)
    head.paragraph_format.keep_with_next=True

for p in doc.paragraphs:
    old=p.text
    new=old.replace('bestiariusz 0.2','bestiariusz 0.3').replace('Bestiariusz 0.2','Bestiariusz 0.3').replace('GM 0.5','GM 0.6').replace('gracza 0.2','gracza 0.3')
    if old.startswith('Wersja 0.2'):new='Wersja 0.3 • 28 października 2026 • ilustracje wszystkich 242 wpisów'
    if new!=old:p.text=new
for section in doc.sections:
    for p in section.footer.paragraphs:
        for run in p.runs:
            if '0.2' in run.text:run.text=run.text.replace('0.2','0.3')
doc.core_properties.version='0.3';doc.save(dst)
check=Document(dst)
assert len(check.inline_shapes)==242
actual=[t._tbl.xpath('.//w:t/text()') for t in check.tables if len(t.columns)!=2]
expected=[t.xpath('.//w:t/text()') for t in orig_tables if len(t.tblGrid.gridCol_lst)!=2]
assert actual==expected
assert sum(1 for t in check.tables if len(t.columns)==2 and len(t.rows)==1)==242
(qa/'illustration_audit.json').write_text(json.dumps({'images':242,'source_hash':hashlib.sha256(src.read_bytes()).hexdigest(),'source':src.name,'output':dst.name},indent=2),encoding='utf-8')
print('CREATED',dst,'images',len(check.inline_shapes),'tables',len(check.tables))
