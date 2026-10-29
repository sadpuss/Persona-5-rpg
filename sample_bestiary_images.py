from urllib.request import Request,urlopen
from urllib.parse import urlencode
from pathlib import Path
import json
R=Path(__file__).parent;out=R/'bestiary_images';out.mkdir(exist_ok=True)
titles=['File:Arsene.png','File:Pixie (P O.A.).png','File:Bicorn (P O.A.).png','File:Arsene P5R.jpg','File:Akechi Goro Loki.png','File:Loki P5.png','File:Orpheus Render.png','File:FemOrpheus Render.png','File:P5 Orpheus.jpg','File:P5 Orpheus2.jpg']
params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|extmetadata','iiurlwidth':500,'titles':'|'.join(titles)}
with urlopen(Request('https://megamitensei.fandom.com/api.php?'+urlencode(params),headers={'User-Agent':'PersonaRPGResearch/1.0'}),timeout=30) as r:data=json.load(r)
(out/'sample_metadata.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for i,p in enumerate(data['query']['pages'].values(),1):
    if 'imageinfo' not in p:print('MISSING',p['title']);continue
    meta=p['imageinfo'][0];url=meta.get('thumburl',meta['url']);file=out/f'sample_{i:02}.img'
    with urlopen(Request(url,headers={'User-Agent':'PersonaRPGResearch/1.0'}),timeout=30) as r:file.write_bytes(r.read())
    print(i,p['title'],meta['width'],meta['height'],str(meta.get('extmetadata',{}))[:160],flush=True)
