from urllib.request import Request,urlopen
from urllib.parse import urlencode
from pathlib import Path
import json
R=Path(__file__).parent
cache=json.loads((R/'bestiary_image_pages.json').read_text(encoding='utf-8'))
empty=[k for k,v in cache.items() if not v['images']]
url='https://megamitensei.fandom.com/api.php?'+urlencode({'action':'query','format':'json','prop':'links','plnamespace':0,'pllimit':'max','redirects':1,'titles':'|'.join(empty)})
with urlopen(Request(url,headers={'User-Agent':'PersonaRPGResearch/1.0'}),timeout=30) as r:data=json.load(r)
(R/'bestiary_image_disambiguation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for p in data.get('query',{}).get('pages',{}).values():print(p['title'],[x['title'] for x in p.get('links',[])][:22])
