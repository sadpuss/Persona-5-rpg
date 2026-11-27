from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,quote
from concurrent.futures import ThreadPoolExecutor,as_completed
from io import BytesIO
import json,time,re,hashlib
from PIL import Image

R=Path(__file__).parent;out=R/'bestiary_images';out.mkdir(exist_ok=True)
choices=json.loads((R/'bestiary_image_choices.json').read_text(encoding='utf-8'))
assert len(choices)==242
API='https://megamitensei.fandom.com/api.php'
headers={'User-Agent':'PersonaRPGResearch/1.0 (personal tabletop reference)'}
meta_path=out/'metadata.json';metadata=json.loads(meta_path.read_text(encoding='utf-8')) if meta_path.exists() else {}
titles=sorted(set(x['file_title'] for x in choices))
pending=[title for title in titles if title not in metadata]
for start in range(0,len(pending),40):
    batch=pending[start:start+40]
    params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size','iiurlwidth':480,'iiurlheight':480,'titles':'|'.join(batch),'redirects':1}
    with urlopen(Request(API+'?'+urlencode(params),headers=headers),timeout=40) as r:data=json.load(r)
    infos={p['title']:p for p in data.get('query',{}).get('pages',{}).values()}
    redirects={x['from']:x['to'] for x in data.get('query',{}).get('normalized',[])+data.get('query',{}).get('redirects',[])}
    for title in batch:
        resolved=redirects.get(title,title)
        p=infos.get(resolved)
        if not p or 'imageinfo' not in p:raise RuntimeError(('Missing file metadata',title,resolved))
        metadata[title]=p['imageinfo'][0]
    meta_path.write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print('METADATA',min(start+40,len(pending)),'/',len(pending),flush=True)

def download(choice):
    record={**choice};meta=metadata[choice['file_title']]
    stem=f'{choice["number"]:03d}_'+re.sub(r'[^A-Za-z0-9_-]+','_',choice['persona'])+'_'+hashlib.sha1(choice['file_title'].encode()).hexdigest()[:6]
    existing=list(out.glob(stem+'.*'))
    if existing:
        file=existing[0]
        with Image.open(file) as im:record.update(width=im.width,height=im.height,format=im.format)
    else:
        url=meta.get('thumburl',meta['url'])
        for attempt in range(3):
            try:
                with urlopen(Request(url,headers=headers),timeout=35) as r:blob=r.read()
                with Image.open(BytesIO(blob)) as im:
                    kind=im.format;w,h=im.size;im.verify()
                if kind=='WEBP':
                    with Image.open(BytesIO(blob)) as decoded:
                        encoded=BytesIO();decoded.save(encoded,format='PNG');blob=encoded.getvalue()
                    kind='PNG'
                if kind not in ('PNG','JPEG'):raise RuntimeError(('Unsupported original image format',kind,choice['file_title']))
                file=out/(stem+('.png' if kind=='PNG' else '.jpg'));file.write_bytes(blob)
                record.update(width=w,height=h,format=kind)
                break
            except Exception:
                if attempt==2:raise
                time.sleep(1+attempt)
    record.update(path=str(file),original_url=meta['url'],download_url=meta.get('thumburl',meta['url']),file_page=meta.get('descriptionurl','https://megamitensei.fandom.com/wiki/'+quote(choice['file_title'].replace(' ','_'))),article_url='https://megamitensei.fandom.com/wiki/'+quote(choice['article_title'].replace(' ','_')))
    return record

records=[];errors=[]
with ThreadPoolExecutor(max_workers=5) as pool:
    futures={pool.submit(download,choice):choice for choice in choices}
    for future in as_completed(futures):
        choice=futures[future]
        try:records.append(future.result())
        except Exception as exc:
            errors.append({'persona':choice['persona'],'error':str(exc)})
            if len(errors)<=5:print('ERROR',choice['persona'],str(exc),flush=True)
        if (len(records)+len(errors))%20==0:print('IMAGES',len(records),'errors',len(errors),'/',len(choices),flush=True)
records.sort(key=lambda x:x['number'])
(R/'bestiary_images_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'bestiary_images_errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE',len(records),'ERRORS',errors)
