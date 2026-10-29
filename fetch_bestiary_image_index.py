from urllib.request import Request,urlopen
from urllib.parse import urlencode
from pathlib import Path
import json,time

R=Path(__file__).parent
API='https://megamitensei.fandom.com/api.php'
def api(params):
    url=API+'?'+urlencode({'format':'json',**params})
    with urlopen(Request(url,headers={'User-Agent':'PersonaRPGResearch/1.0 (personal tabletop reference)'}),timeout=30) as r:return json.load(r)

categories=['Category:Persona 5 Personas Images','Category:Persona 5 Royal Persona Images']
records=[]
for category in categories:
    cont={};items=[]
    while True:
        result=api({'action':'query','list':'categorymembers','cmtitle':category,'cmtype':'file','cmlimit':500,**cont})
        items.extend(result.get('query',{}).get('categorymembers',[]))
        if 'continue' not in result:break
        cont=result['continue']
    for x in items:x['category']=category
    records.extend(items)
    print(category,len(items),flush=True)
unique={x['title']:x for x in records}
(R/'bestiary_image_index.json').write_text(json.dumps(list(unique.values()),ensure_ascii=False,indent=2),encoding='utf-8')
print('TOTAL',len(unique))
print('SAMPLE',list(unique)[:18])
