from pathlib import Path
import json, hashlib
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image,ImageDraw
from docx import Document
from zipfile import ZipFile
from lxml import etree

root=Path(__file__).parent
qa=root/'qa_gm_0_3'
pdf=pdfium.PdfDocument(str(qa/'guide.pdf'))
reader=PdfReader(qa/'guide.pdf')
texts=[]
for i,page in enumerate(pdf):
    image=page.render(scale=1.5).to_pil().convert('RGB')
    image.save(qa/f'page-{i+1:02}.png')
    texts.append(reader.pages[i].extract_text() or '')
    page.close()
for start in range(0,len(texts),6):
    sheet=Image.new('RGB',(1260,1230),'#c6c6c6')
    draw=ImageDraw.Draw(sheet)
    for j in range(6):
        if start+j>=len(texts):break
        im=Image.open(qa/f'page-{start+j+1:02}.png')
        im.thumbnail((400,565))
        x=10+(j%3)*420;y=25+(j//3)*610
        sheet.paste(im,(x,y));draw.text((x,y-18),f'Strona {start+j+1}',fill='black')
    sheet.save(qa/f'contact-{start//6+1:02}.png')
doc=Document(root/'Persona_5_RPG_Podrecznik_GM_0_3.docx')
source=Document(root/'Persona_5_RPG_Zasady_0_2.docx')
report=json.loads((root/'gm_guide_0_3_audit.json').read_text(encoding='utf-8'))
report['source_unchanged_after_word']=hashlib.sha256((root/'Persona_5_RPG_Zasady_0_2.docx').read_bytes()).hexdigest()==report['source_sha256']
report['word_page_count']=len(texts)
report['pdf_links']=sum(len(p.get('/Annots',[])) for p in reader.pages)
report['pdf_text_errors']=[i+1 for i,t in enumerate(texts) if any(s in t for s in ['Error!','Błąd! Nie','Bookmark not defined','Nie zdefiniowano zakładki'])]
report['empty_pages']=[i+1 for i,t in enumerate(texts) if len(t.strip())<30]
report['table_count_after_word']=len(doc.tables)
report['skills_after_word']=sum(len(t.rows)-1 for t in doc.tables if len(t.columns)==6 and t.cell(0,0).text=='Umiejętność')
report['items_after_word']=sum(len(t.rows)-1 for t in doc.tables if len(t.columns)==6 and t.cell(0,0).text=='Przedmiot')
with ZipFile(root/'Persona_5_RPG_Podrecznik_GM_0_3.docx') as z:
    xml=etree.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    bookmarks=xml.xpath('//w:bookmarkStart/@w:name',namespaces=ns)
    anchors=xml.xpath('//w:hyperlink/@w:anchor',namespaces=ns)
    report['toc_internal_links']=len(anchors)
    report['unresolved_internal_links']=sorted(set(anchors)-set(bookmarks))
    report['return_to_toc_bookmark']='GM_Spis' in bookmarks
assert report['source_unchanged_after_word']
assert not report['pdf_text_errors'] and not report['empty_pages']
assert report['skills_after_word']==541 and report['items_after_word']==157
assert report['table_count_after_word']==60
assert not report['unresolved_internal_links']
(root/'gm_guide_0_3_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(qa/'extracted_pages.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{t}' for i,t in enumerate(texts)),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
print('CHAPTER LOCATIONS')
for i,t in enumerate(texts):
    for line in t.splitlines()[:12]:
        if line and line[0].isdigit() and any(c.isalpha() for c in line):print(i+1,line[:115])
