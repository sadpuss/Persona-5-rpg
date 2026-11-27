from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
import json,time

R=Path(__file__).resolve().parent
API='https://megamitensei.fandom.com/api.php'
cards=json.loads((R.parent/'dane'/'persona_skill_cards.json').read_text(encoding='utf-8'))
aliases={'Orpheus F':'Orpheus','Orpheus F Picaro':'Orpheus','Orpheus Picaro F':'Orpheus','Kushinada':'Kushinada-Hime','Koropokkuru':'Koropokguru'}
def article(name):
    if name in aliases:return aliases[name]
    return name.replace(' Picaro','')
titles=sorted(set(article(x['persona']) for x in cards))
path=R/'bestiary_image_pages.json'
cache=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
pending=[x for x in titles if x not in cache]
def api(params):
    url=API+'?'+urlencode({'format':'json',**params})
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={'User-Agent':'PersonaRPGResearch/1.0 (personal tabletop reference)'}),timeout=40) as r:return json.load(r)
        except Exception:
            if attempt==2:raise
            time.sleep(1+attempt)
for start in range(0,len(pending),20):
    batch=pending[start:start+20];continuation={};pages={};redirects={}
    while True:
        data=api({'action':'query','prop':'images','titles':'|'.join(batch),'redirects':1,'imlimit':'max',**continuation})
        q=data.get('query',{})
        for item in q.get('normalized',[])+q.get('redirects',[]):redirects[item['from']]=item['to']
        for v in q.get('pages',{}).values():
            entry=pages.setdefault(v['title'],{'title':v['title'],'missing':'missing' in v,'images':[]})
            entry['images'].extend(x['title'] for x in v.get('images',[]))
        if 'continue' not in data:break
        continuation=data['continue']
    for title in batch:
        resolved=title;seen=set()
        while resolved in redirects and resolved not in seen:seen.add(resolved);resolved=redirects[resolved]
        entry=pages.get(resolved,{'title':resolved,'missing':True,'images':[]})
        entry['images']=sorted(set(entry['images']))
        cache[title]=entry
    path.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PAGES',min(start+20,len(pending)),'/',len(pending),'cached',len(cache),flush=True)
print('MISSING',[(k,v['title']) for k,v in cache.items() if v['missing']])
print('TOTAL IMAGE REFERENCES',sum(len(v['images']) for v in cache.values()))
