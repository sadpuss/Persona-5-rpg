from pathlib import Path
import json,re,unicodedata
R=Path(__file__).parent
cards=json.loads((R/'persona_skill_cards.json').read_text(encoding='utf-8'))
pages=json.loads((R/'bestiary_image_pages.json').read_text(encoding='utf-8'))
norm=lambda text:re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower())
aliases={'Orpheus F':'Orpheus','Orpheus F Picaro':'Orpheus','Orpheus Picaro F':'Orpheus','Kushinada':'Kushinada-Hime','Koropokkuru':'Koropokguru'}
overrides={
'Arsene':'File:Arsene.png',
'Orpheus':'File:Orpheus Render.png',
'Orpheus F':'File:FemOrpheus Render.png',
'Orpheus Picaro':'File:P5 Orpheus2.jpg',
'Orpheus F Picaro':'File:F Orpheus Picaro P5R.jpg',
'Orpheus Picaro F':'File:F Orpheus Picaro P5R.jpg',
'Izanagi Picaro':'File:P5 Izanagi3.jpg',
'Magatsu-Izanagi Picaro':'File:P5 Izanagi2.jpg',
'Athena':'File:Athena P5R.jpg',
'Athena Picaro':'File:Athena Picaro P5R.jpg',
'Asterius Picaro':'File:P5 Asterius2.jpg',
'Thanatos Picaro':'File:P5 Thanatos2.jpg',
'Messiah Picaro':'File:Messiah Picaro Render.png',
'Kaguya Picaro':'File:P5 Kaguya2.jpg',
'Tsukiyomi Picaro':'File:P5 Tsukuyomi2.jpg',
'Ariadne Picaro':'File:P5 Ariadne2.jpg',
'Izanagi-no-Okami':'File:IzanagiNoOkami Render.png',
'Izanagi-no-Okami Picaro':'File:IzanagiNoOkami Picaro Render.png',
'Loki':'File:Loki P5.png',
'Cendrillon':'File:P5RCendrillon.png',
'Necronomicon':'File:Necronomicon (P O.A.).png',
'Hecatoncheires':'File:Hecatoncheir (P O.A.).png',
'Tsukiyomi':'File:P5 Tsukuyomi.jpg',
'Thanatos':'File:P5 Thanatos.jpg',
'Izanagi':'File:P5 Izanagi.jpg',
'Messiah':'File:Messiah Render.png',
}
def article(name):return aliases.get(name,name.replace(' Picaro',''))
selections=[];missing=[]
for card in cards:
    name=card['persona'];page=pages[article(name)]
    acceptable={norm(name),norm(re.sub(r'\s*\([^)]*\)','',page['title']))}
    def score(title):
        text=title.removeprefix('File:');stem=re.sub(r'\.[^.]+$','',text)
        n=norm(stem);s=stem.lower()
        if not text.lower().endswith(('.png','.jpg','.jpeg','.webp')):return -999
        if any(t in s for t in ['concept','icon','wallpaper','steam','funko','manga','anime','comic','artbook','line art','p5x','p5s','p5t','battle','cutin','cut-in','awaken','logo','card','dx2','animation','t-shirt','crossover']):return -999
        if 'picaro' in s and 'Picaro' not in name:return -999
        if '(p o.a.)' in s:
            base=norm(re.sub(r'\(P O\.A\.\)','',stem,flags=re.I))
            if base in acceptable:return 120
        if n.endswith('p5r') and re.sub(r'p5r$','',n) in acceptable:return 115
        if n.startswith('p5') and re.sub(r'^p5','',n) in acceptable:return 113
        if 'render' in s and any(x and x in n for x in acceptable):return 110
        if n in acceptable:return 105
        if any(x and x in n for x in acceptable):return 35-len(stem)/100
        return -999
    candidates=sorted([(score(t),t) for t in page['images']],reverse=True)
    choice=overrides.get(name)
    if choice:
        assert choice in page['images'],(name,choice)
        quality='wybrany wariant'
    elif candidates and candidates[0][0]>0:
        choice=candidates[0][1];quality='render lub artwork' if candidates[0][0]>=105 else 'zrzut P5R' if candidates[0][0]>=95 else 'do kontroli'
    else:
        missing.append((name,page['title'],page['images']));continue
    selections.append({'number':card['card_number'],'persona':name,'file_title':choice,'article_title':page['title'],'quality':quality,'alternatives':[t for s,t in candidates[:5] if s>0]})
(R/'bestiary_image_choices.json').write_text(json.dumps(selections,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'bestiary_images_missing.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2),encoding='utf-8')
print('CHOSEN',len(selections),'MISSING',[x[0] for x in missing])
print('LOW CONFIDENCE',[(x['persona'],x['file_title']) for x in selections if x['quality']=='do kontroli'])
