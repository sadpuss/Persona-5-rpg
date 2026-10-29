from pathlib import Path
from zipfile import ZipFile
import json,hashlib,re,sys
from collections import Counter
from lxml import etree
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image,ImageDraw
R=Path(__file__).parent;Q=R/'qa_complete_skills';Q.mkdir(exist_ok=True)
audit=json.loads((R/'skill_completion_audit.json').read_text(encoding='utf-8'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
def root(name):
    with ZipFile(R/name) as z:return etree.fromstring(z.read('word/document.xml'))
def txt(el):return ''.join(el.xpath('.//w:t/text()',namespaces=ns))
def tables(x):return x.xpath('/w:document/w:body/w:tbl',namespaces=ns)
def rows(t):return [[txt(c) for c in row.findall('w:tc',ns)] for row in t.findall('w:tr',ns)]
def catalogue(x):
    result={}
    for t in tables(x):
        rr=rows(t)
        if len(rr[0])==7 and rr[0][0]=='Umiejętność':result.update({r[0]:r for r in rr[1:]})
    return result
rules=json.loads((R/'skill_rules_0_7.json').read_text(encoding='utf-8'));byname={r['skill']:r for r in rules}
oldg=json.loads((R/'skill_level_gates.json').read_text(encoding='utf-8'));newg=json.loads((R/'skill_level_gates_0_7.json').read_text(encoding='utf-8'))
assert set(byname)=={g['skill'] for g in oldg if g['access']=='A'} and len(byname)==236
assert Counter(g['access'] for g in newg)['R']==346 and not any(g['access']=='A' for g in newg)
for a,b in zip(oldg,newg):
    assert a['skill']==b['skill'] and a['min_level']==b['min_level']
    assert b['access']==('R' if a['access']=='A' else a['access'])
gm=root(audit['outputs']['gm']);oldgm=root('Persona_5_RPG_Podrecznik_GM_0_6.docx')
nc,oc=catalogue(gm),catalogue(oldgm);assert nc.keys()==oc.keys() and len(nc)==541
for skill,old in oc.items():
    new=nc[skill];assert old[:4]==new[:4] and old[5]==new[5],skill
    assert new[6]==(old[6].replace('/ A','/ R') if skill in byname else old[6]),skill
effects={}
for t in tables(gm):
    rr=rows(t)
    if rr[0]==['Skill','Min. lvl','Koszt','Gotowe działanie RPG']:effects.update({r[0]:r for r in rr[1:]})
assert effects.keys()==byname.keys()
for skill,r in byname.items():assert effects[skill]==[skill,str(r['min_level']),r['cost'],r['effect']],skill
assert sum(len(rows(t))-1 for t in tables(gm) if rows(t)[0][0]=='Przedmiot')==157
for name,sha in audit['source_hashes'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha
oldbest=root('Persona_5_RPG_Bestiariusz_0_3.docx');best=root(audit['outputs']['bestiary'])
assert len(best.xpath('//wp:inline',namespaces=ns))==242
assert [rows(t) for t in tables(best) if rows(t)[0][0]=='Profil']==[rows(t) for t in tables(oldbest) if rows(t)[0][0]=='Profil']
for name in ['Persona_5_RPG_Bestiariusz_0_3.docx',audit['outputs']['bestiary']]:
    with ZipFile(R/name) as z:
        media={p:hashlib.sha256(z.read(p)).hexdigest() for p in z.namelist() if p.startswith('word/media/')}
    if name.endswith('0_3.docx'):oldmedia=media
    else:assert oldmedia==media
bestparas=[txt(p) for p in best.xpath('//w:p',namespaces=ns)]
assert not any('/ A •' in p for p in bestparas if p.startswith('Skill card RPG:'))
assert all(re.match(r'RPG: atak \+4; Obrona 12;',p) for p in bestparas if p.startswith('RPG: atak '))
report={'structural_checks_passed':True,'completed':236,'ready':346,'remaining_A':0,'source_files_unchanged':True}
for tag in sys.argv[1:] or audit['outputs'].keys():
    x=root(audit['outputs'][tag]);anchors=set(x.xpath('//w:hyperlink/@w:anchor',namespaces=ns));bookmarks=set(x.xpath('//w:bookmarkStart/@w:name',namespaces=ns));assert not anchors-bookmarks,(tag,anchors-bookmarks)
    if tag!='bestiary':assert len(x.xpath('//w:instrText[contains(text(),"TOC ")]',namespaces=ns))==1
    reader=PdfReader(Q/f'{tag}.pdf');pdf=pdfium.PdfDocument(str(Q/f'{tag}.pdf'));texts=[];bad=[]
    for i,page in enumerate(pdf):
        page.render(scale=1.5).to_pil().convert('RGB').save(Q/f'{tag}-page-{i+1:03}.png');page.close()
        tx=reader.pages[i].extract_text() or '';texts.append(tx)
        assert not any(s in tx for s in ['Error!','Nie zdefiniowano zakładki','Bookmark not defined']),(tag,i+1)
        assert len(tx.strip())>40,(tag,'empty',i+1)
        if tag=='bestiary':
            h=len(re.findall(r'(?m)^\d{3}\s+Lv\s+\d+\s+',tx));captions=sum(line.strip()=='Źródło ilustracji' for line in tx.splitlines())
            if h!=tx.count('Skill card RPG:') or h!=captions:bad.append((i+1,h,tx.count('Skill card RPG:'),captions))
    if tag=='bestiary':assert not bad,bad
    for start in range(0,len(texts),8):
        im=Image.new('RGB',(1660,1230),'#C6C6C6');draw=ImageDraw.Draw(im)
        for j in range(min(8,len(texts)-start)):
            page=Image.open(Q/f'{tag}-page-{start+j+1:03}.png');page.thumbnail((395,565));a=10+j%4*415;b=25+j//4*610;im.paste(page,(a,b));draw.text((a,b-18),f'{tag} {start+j+1}',fill='black')
        im.save(Q/f'{tag}-contact-{start//8+1:02}.png')
    (Q/f'{tag}-text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{t}' for i,t in enumerate(texts)),encoding='utf-8')
    report[tag]={'pages':len(texts),'split_cards':bad};print(tag,report[tag],flush=True)
    if tag=='gm':
        entire='\n'.join(texts)
        assert '13.20 Gotowe efekty skilli i wspólne reguły' in entire
        assert not any(t in entire for t in ['Karta A może istnieć','Severe, Colossal, Almighty o specjalnej sile oraz wielokrotne trafienia nie mają jeszcze'])
    if tag=='player':assert 'Dalszy rozwój premii ataku i Obrony pozostaje osobnym ustaleniem' not in '\n'.join(texts)
    (Q/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('ALL CHECKS PASSED')
