from pathlib import Path
from zipfile import ZipFile
import json,hashlib,re,sys
from lxml import etree
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image,ImageDraw
R=Path(__file__).parent;Q=R/'qa_exp_scaling_images'
names={'player':'Persona_5_RPG_Podrecznik_Gracza_0_3.docx','gm':'Persona_5_RPG_Podrecznik_GM_0_6.docx','bestiary':'Persona_5_RPG_Bestiariusz_0_3.docx'}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
report={}
def xml(name):
    with ZipFile(R/name) as z:return etree.fromstring(z.read('word/document.xml'))
def text(el):return ''.join(el.xpath('.//w:t/text()',namespaces=ns))
def tables(x):return x.xpath('/w:document/w:body/w:tbl',namespaces=ns)
def rows(t):return [[text(c) for c in row.findall('w:tc',ns)] for row in t.findall('w:tr',ns)]
for tag in sys.argv[1:] or names.keys():
    x=xml(names[tag]);anchors=set(x.xpath('//w:hyperlink/@w:anchor',namespaces=ns));bookmarks=set(x.xpath('//w:bookmarkStart/@w:name',namespaces=ns))
    assert not anchors-bookmarks,(tag,anchors-bookmarks)
    if tag!='bestiary':
        assert len(x.xpath('//w:instrText[contains(text(),"TOC ")]',namespaces=ns))==1
        rewards=next(rows(t) for t in tables(x) if rows(t)[0][0]=='Poziom wyzwania N')
        assert len(rewards)==100
        for level,row in enumerate(rewards[1:],1):assert [int(c.replace(' ','')) for c in row]==[level]+[level*k for k in [10,20,35,60,120,20,50]]
        exp=next(rows(t) for t in tables(x) if rows(t)[0][0]=='Poziom' and len(rows(t)[0])==4)
        assert len(exp)==100
        for level,row in enumerate(exp[1:],1):assert int(row[1].replace(' ',''))==50*(level-1)*level
    else:
        assert len(x.xpath('//wp:inline',namespaces=ns))==242
        old=xml('Persona_5_RPG_Bestiariusz_0_2.docx')
        oldrows=[rows(t) for t in tables(old)]
        newrows=[rows(t) for t in tables(x) if not t.xpath('.//wp:inline',namespaces=ns)]
        assert oldrows==newrows
        oldmeta=[text(p) for p in old.xpath('//w:p',namespaces=ns) if text(p).startswith(('Arcana:','Skill card RPG:'))]
        newmeta=[text(p) for p in x.xpath('//w:p',namespaces=ns) if text(p).startswith(('Arcana:','Skill card RPG:'))]
        assert sorted(oldmeta)==sorted(newmeta)
        assert len([p for p in x.xpath('//w:p',namespaces=ns) if text(p)=='Źródło ilustracji'])==242
        for t in tables(x):
            if t.xpath('.//wp:inline',namespaces=ns):
                assert sum(text(p).startswith('Arcana:') for p in t.xpath('.//w:p',namespaces=ns))==1
                assert sum(text(p).startswith('Skill card RPG:') for p in t.xpath('.//w:p',namespaces=ns))==1
    reader=PdfReader(Q/f'{tag}.pdf');pdf=pdfium.PdfDocument(str(Q/f'{tag}.pdf'));texts=[];bad=[]
    for i,page in enumerate(pdf):
        page.render(scale=1.5).to_pil().convert('RGB').save(Q/f'{tag}-page-{i+1:03}.png');page.close()
        tx=reader.pages[i].extract_text() or '';texts.append(tx)
        assert not any(e in tx for e in ['Error!','Nie zdefiniowano zakładki','Bookmark not defined']),(tag,i+1)
        assert len(tx.strip())>40,(tag,'empty page',i+1)
        if tag=='bestiary':
            h=len(re.findall(r'(?m)^\d{3}\s+Lv\s+\d+\s+',tx))
            captions=sum(line.strip()=='Źródło ilustracji' for line in tx.splitlines())
            if h!=tx.count('Skill card RPG:') or h!=captions:bad.append((i+1,h,tx.count('Skill card RPG:'),captions))
    for start in range(0,len(texts),8):
        im=Image.new('RGB',(1660,1230),'#C6C6C6');draw=ImageDraw.Draw(im)
        for j in range(min(8,len(texts)-start)):
            page=Image.open(Q/f'{tag}-page-{start+j+1:03}.png');page.thumbnail((395,565))
            a=10+j%4*415;b=25+j//4*610;im.paste(page,(a,b));draw.text((a,b-18),f'{tag} {start+j+1}',fill='black')
        im.save(Q/f'{tag}-contact-{start//8+1:02}.png')
    (Q/f'{tag}-text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{t}' for i,t in enumerate(texts)),encoding='utf-8')
    report[tag]={'pages':len(texts),'split_cards':bad,'images':242 if tag=='bestiary' else 0}
    if tag=='bestiary':assert not bad,bad
    print(tag,report[tag],flush=True)
audit=json.loads((R/'exp_scaling_audit.json').read_text(encoding='utf-8'))
for tag,sha in audit['source_hashes'].items():
    name={'gm':'Persona_5_RPG_Podrecznik_GM_0_5.docx','player':'Persona_5_RPG_Podrecznik_Gracza_0_2.docx'}[tag]
    assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha
imageaudit=json.loads((Q/'illustration_audit.json').read_text(encoding='utf-8'))
assert hashlib.sha256((R/imageaudit['source']).read_bytes()).hexdigest()==imageaudit['source_hash']
(Q/'qa_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ALL CHECKS PASSED')
