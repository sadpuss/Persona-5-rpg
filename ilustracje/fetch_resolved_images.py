from urllib.request import Request,urlopen
from urllib.parse import urlencode
from pathlib import Path
import json
R=Path(__file__).parent
path=R/'bestiary_image_pages.json';cache=json.loads(path.read_text(encoding='utf-8'))
targets={
'Bishamonten':'Bishamonten (demon)','Crystal Skull':'Crystal Skull (Treasure Demon)',"Emperor's Amulet":"Emperor's Amulet (Treasure Demon)",'Hope Diamond':'Hope Diamond (Treasure Demon)','Koh-i-Noor':'Koh-i-Noor (Treasure Demon)','Maria':'Maria (demon)','Messiah':'Messiah (Persona)','Milady':'Milady (Persona 5)','Orichalcum':'Orichalcum (Treasure Demon)','Orlov':'Orlov (Treasure Demon)','Orthrus':'Orthrus (demon)',"Queen's Necklace":"Queen's Necklace (Treasure Demon)",'Regent':'Regent (Treasure Demon)','Seth':'Seth (demon)','Stone of Scone':'Stone of Scone (Treasure Demon)'}
continuation={};pages={}
while True:
    params={'action':'query','format':'json','prop':'images','titles':'|'.join(targets.values()),'imlimit':'max',**continuation}
    with urlopen(Request('https://megamitensei.fandom.com/api.php?'+urlencode(params),headers={'User-Agent':'PersonaRPGResearch/1.0'}),timeout=30) as r:data=json.load(r)
    for p in data.get('query',{}).get('pages',{}).values():
        v=pages.setdefault(p['title'],{'title':p['title'],'missing':'missing' in p,'images':[]});v['images'].extend(x['title'] for x in p.get('images',[]))
    if 'continue' not in data:break
    continuation=data['continue']
for old,new in targets.items():
    cache[old]=pages[new];cache[old]['images']=sorted(set(cache[old]['images']))
path.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8')
print('RESOLVED',[(old,len(cache[old]['images'])) for old in targets])
