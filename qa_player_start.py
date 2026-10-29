from pathlib import Path
from collections import Counter
import hashlib,json
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image,ImageDraw
from docx import Document
from zipfile import ZipFile
from lxml import etree

R=Path(__file__).parent
qa=R/'qa_player_start'
report=json.loads((R/'player_start_audit.json').read_text(encoding='utf-8'))
for tag in ['player','gm']:
    reader=PdfReader(qa/f'{tag}.pdf')
    pdf=pdfium.PdfDocument(str(qa/f'{tag}.pdf'))
    errors=[];blank=[]
    texts=[]
    for i,page in enumerate(pdf):
        page.render(scale=1.5).to_pil().convert('RGB').save(qa/f'{tag}-page-{i+1:02}.png')
        page.close()
        text=reader.pages[i].extract_text() or '';texts.append(text)
        body_lines=[line for line in text.splitlines() if line.strip() and not line.strip().startswith(('Persona 5 RPG','Strona '))]
        if not body_lines:blank.append(i+1)
        if any(x in text for x in ['Error!','Nie zdefiniowano zakładki','Bookmark not defined']):errors.append(i+1)
    for start in range(0,len(texts),6):
        sheet=Image.new('RGB',(1260,1230),'#C6C6C6');draw=ImageDraw.Draw(sheet)
        for j in range(6):
            if start+j>=len(texts):break
            im=Image.open(qa/f'{tag}-page-{start+j+1:02}.png');im.thumbnail((400,565))
            x=10+j%3*420;y=25+j//3*610
            sheet.paste(im,(x,y));draw.text((x,y-18),f'{tag} {start+j+1}',fill='black')
        sheet.save(qa/f'{tag}-contact-{start//6+1:02}.png')
    report[tag+'_pages']=len(texts)
    report[tag+'_pdf_errors']=errors
    report[tag+'_blank_pages']=blank
    assert not errors and not blank
    (qa/f'{tag}-text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{t}' for i,t in enumerate(texts)),encoding='utf-8')
gm=Document(R/'Persona_5_RPG_Podrecznik_GM_0_4.docx')
src=Document(R/'Persona_5_RPG_Podrecznik_GM_0_3.docx')
old=[t for t in src.tables if len(t.columns)==6 and t.cell(0,0).text=='Umiejętność']
new=[t for t in gm.tables if len(t.columns)==7 and t.cell(0,0).text=='Umiejętność']
for a,b in zip(old,new):assert [[c.text for c in r.cells] for r in a.rows]==[[c.text for c in r.cells[:6]] for r in b.rows]
assert sum(len(t.rows)-1 for t in new)==541
assert hashlib.sha256((R/'Persona_5_RPG_Podrecznik_GM_0_3.docx').read_bytes()).hexdigest()==report['gm_source_sha256']
for name in ['Persona_5_RPG_Podrecznik_GM_0_4.docx','Persona_5_RPG_Podrecznik_Gracza_0_1.docx']:
    with ZipFile(R/name) as z:
        xml=etree.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        bookmarks=set(xml.xpath('//w:bookmarkStart/@w:name',namespaces=ns))
        anchors=set(xml.xpath('//w:hyperlink/@w:anchor',namespaces=ns))
        assert not anchors-bookmarks,(name,anchors-bookmarks)
(R/'player_start_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
