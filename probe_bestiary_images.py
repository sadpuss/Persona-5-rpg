from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
import hashlib,json

filename='P5_Abaddon_Render.png'
h=hashlib.md5(filename.encode()).hexdigest()
urls=[
 'https://megatenwiki.com/api.php?action=query&format=json&meta=siteinfo',
 'https://megatenwiki.com/w/api.php?action=query&format=json&meta=siteinfo',
 'https://megamitensei.fandom.com/api.php?action=query&format=json&meta=siteinfo',
 f'https://megatenwiki.com/images/{h[0]}/{h[:2]}/{filename}',
]
def probe(url):
    try:
        with urlopen(Request(url,headers={'User-Agent':'PersonaRPGResearch/1.0'}),timeout=15) as r:
            data=r.read(180)
            return {'url':url,'status':r.status,'type':r.headers.get('Content-Type'),'sample':data.decode('utf-8','replace') if 'json' in r.headers.get('Content-Type','') else data[:20].hex()}
    except Exception as e:return {'url':url,'error':str(e)}
with ThreadPoolExecutor(max_workers=2) as pool:
    print(json.dumps(list(pool.map(probe,urls)),ensure_ascii=False,indent=2))
