from pathlib import Path
import json,re,hashlib,sys
from collections import Counter
from zipfile import ZipFile
from lxml import etree
from docx import Document
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image,ImageDraw

R=Path(__file__).parent;QA=R/'qa_exp_velvet'
report=json.loads((R/'exp_velvet_audit.json').read_text(encoding='utf-8'))
names={'player':'Persona_5_RPG_Podrecznik_Gracza_0_2.docx','gm':'Persona_5_RPG_Podrecznik_GM_0_5.docx','bestiary':'Persona_5_RPG_Bestiariusz_0_2.docx'}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for tag,name in names.items():
    if len(sys.argv)>1 and tag not in sys.argv[1:]:continue
    reader=PdfReader(QA/f'{tag}.pdf');pdf=pdfium.PdfDocument(str(QA/f'{tag}.pdf'))
    texts=[];empty=[];errors=[];split_cards=[]
    for i,page in enumerate(pdf):
        page.render(scale=1.5).to_pil().convert('RGB').save(QA/f'{tag}-page-{i+1:03}.png');page.close()
        text=reader.pages[i].extract_text() or '';texts.append(text)
        lines=[line for line in text.splitlines() if line.strip() and not line.strip().startswith(('Persona 5 RPG','Strona ','Bestiariusz 0.2'))]
        if not lines:empty.append(i+1)
        if any(x in text for x in ['Error!','Nie zdefiniowano zakładki','Bookmark not defined']):errors.append(i+1)
        if tag=='bestiary':
            heads=len(re.findall(r'(?m)^\d{3}\s+Lv\s+\d+\s+',text))
            cards=text.count('Skill card RPG:')
            if heads!=cards:split_cards.append({'page':i+1,'heads':heads,'cards':cards})
    for start in range(0,len(texts),8):
        im=Image.new('RGB',(1660,1230),'#C6C6C6');draw=ImageDraw.Draw(im)
        for j in range(8):
            if start+j>=len(texts):break
            page=Image.open(QA/f'{tag}-page-{start+j+1:03}.png');page.thumbnail((395,565))
            x=10+j%4*415;y=25+j//4*610;im.paste(page,(x,y));draw.text((x,y-18),f'{tag} {start+j+1}',fill='black')
        im.save(QA/f'{tag}-contact-{start//8+1:02}.png')
    report[tag+'_pages']=len(texts);report[tag+'_empty_pages']=empty;report[tag+'_pdf_errors']=errors
    assert not empty and not errors,(tag,empty,errors)
    if tag=='bestiary':
        report['bestiary_split_card_checks']=split_cards
        report['bestiary_pdf_card_labels']=sum(t.count('Skill card RPG:') for t in texts)
        assert report['bestiary_pdf_card_labels']==242
        assert not split_cards,split_cards
    with ZipFile(R/name) as z:
        xml=etree.fromstring(z.read('word/document.xml'))
        anchors=set(xml.xpath('//w:hyperlink/@w:anchor',namespaces=ns))
        bookmarks=set(xml.xpath('//w:bookmarkStart/@w:name',namespaces=ns))
        report[tag+'_unresolved_links']=sorted(anchors-bookmarks)
        assert not anchors-bookmarks,(tag,anchors-bookmarks)
        report[tag+'_toc_fields']=len(xml.xpath('//w:instrText[contains(text(),"TOC ")]',namespaces=ns))
        if tag!='bestiary':assert report[tag+'_toc_fields']==1
    (QA/f'{tag}-text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{t}' for i,t in enumerate(texts)),encoding='utf-8')
for filename,sha in report['source_hashes'].items():assert hashlib.sha256((R/filename).read_bytes()).hexdigest()==sha
b=Document(R/names['bestiary']);oldb=Document(R/'Persona_5_RPG_Bestiariusz_0_1.docx')
assert [[[c.text for c in row.cells] for row in t.rows] for t in b.tables]==[[[c.text for c in row.cells] for row in t.rows] for t in oldb.tables]
assert [p.text for p in b.paragraphs if p.text.startswith('Arcana:')]==[p.text for p in oldb.paragraphs if p.text.startswith('Arcana:')]
mapping=json.loads((R/'persona_skill_cards.json').read_text(encoding='utf-8'))
assert len(mapping)==242 and len({x['persona'] for x in mapping})==242
assert Counter(x['origin'] for x in mapping)=={'P5R':114,'HB':128}
gm=Document(R/names['gm']);oldgm=Document(R/'Persona_5_RPG_Podrecznik_GM_0_4.docx')
oldskills=[t for t in oldgm.tables if len(t.columns)==7 and t.cell(0,0).text=='Umiejętność']
newskills=[t for t in gm.tables if len(t.columns)==7 and t.cell(0,0).text=='Umiejętność']
assert [[[c.text for c in row.cells] for row in t.rows] for t in oldskills]==[[[c.text for c in row.cells] for row in t.rows] for t in newskills]
assert sum(len(t.rows)-1 for t in newskills)==541
assert sum(len(t.rows)-1 for t in gm.tables if len(t.columns)==6 and t.cell(0,0).text=='Przedmiot')==157
for tag in ['gm','player']:
    d=Document(R/names[tag]);t=next(t for t in d.tables if len(t.columns)==4 and t.cell(0,0).text=='Poziom')
    assert len(t.rows)==100
    for level,row in enumerate(t.rows[1:],1):
        vals=[c.text.replace(' ','') for c in row.cells]
        assert int(vals[0])==level and int(vals[1])==50*(level-1)*level
        assert vals[2]==(str(100*level) if level<99 else '—')
    if tag=='player':assert not any(t.cell(0,0).text=='Pole' for t in d.tables)
report['final_audit_passed']=True
(R/'exp_velvet_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
