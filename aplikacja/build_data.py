"""Buduje lokalny katalog wyłącznie z aktualnych reguł i tabel Word."""
import json
import re
import hashlib
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def tables(name):
    with zipfile.ZipFile(ROOT / name) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    return [[[' '.join(t.text or '' for t in cell.findall('.//w:t', NS)) for cell in row.findall('w:tc', NS)] for row in table.findall('w:tr', NS)] for table in root.findall('.//w:tbl', NS)]

gates = json.loads((ROOT / 'skill_level_gates_0_8.json').read_text('utf-8'))
rules = {r['skill']: r for r in json.loads((ROOT / 'skill_rules_0_8.json').read_text('utf-8'))}
inputs = ['Persona_5_RPG_Podrecznik_Gracza.docx', 'Persona_5_RPG_Podrecznik_GM.docx']
hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in inputs}
player = tables(inputs[0])
gm = tables(inputs[1])
effects = {}
arcana = []
starters = []
catalog = {}
cleansing = {}
for table in player + gm:
    if not table:
        continue
    header = ' | '.join(table[0])
    if table[0] == ['Skill', 'Min. lvl', 'Koszt', 'Gotowe działanie RPG']:
        for row in table[1:]:
            if len(row) >= 4:
                effects[row[0]] = {'effect': row[3], 'cost': row[2]}
    if table[0] == ['Umiejętność', 'Cel i efekt', 'Koszt']:
        for row in table[1:]:
            if len(row) >= 3:
                effects[row[0]] = {'effect': row[1], 'cost': row[2]}
    if 'Koszt RPG' in table[0] and 'Min. lvl / dostęp' in table[0]:
        for row in table[1:]:
            if len(row) >= 7:
                effects.setdefault(row[0], {})['cost'] = row[3]
                catalog[row[0]] = {'target': row[1], 'status': row[5]}
    if table[0] == ['Skill', 'Usuwane zwykłe statusy', 'Cel', 'Koszt RPG']:
        for row in table[1:]:
            if len(row) >= 4:
                cleansing[row[0]] = {'effect': f'{row[2]}; usuwa: {row[1]}.', 'cost': row[3]}
    if 'Skill' in header and 'Działanie RPG' in header and 'Koszt' in header:
        for row in table[1:]:
            if len(row) >= 3:
                effects[row[0]] = {'effect': row[1], 'cost': row[2]}
for table in player:
    if table and 'Osobisty trait na start' in ' '.join(table[0]):
        arcana = [{'name': r[0], 'effect': r[1]} for r in table[1:] if len(r) >= 2]
    if table and 'Działanie RPG' in ' '.join(table[0]) and 'Koszt' in ' '.join(table[0]):
        starters = [r[0] for r in table[1:] if len(r) >= 3]
skills = []
types = {'fir': 'Fire', 'ice': 'Ice', 'ele': 'Electricity', 'win': 'Wind', 'psy': 'Psy', 'nuk': 'Nuclear', 'ble': 'Bless', 'cur': 'Curse', 'phy': 'Physical', 'gun': 'Gun', 'alm': 'Almighty'}
damage = {1: '1d6 + 4', 5: '1d6 + 4', 10: '2d6 + 6', 15: '2d6 + 6', 25: '3d6 + 8', 35: '3d6 + 8'}
def status_text(text):
    return re.sub(r'\s*\([^)]*P5R\)', '', text).strip()

for g in gates:
    r = dict(g)
    r.update(effects.get(g['skill'], {}))
    r.update(rules.get(g['skill'], {}))
    if not r.get('effect') and r['access'] == 'R':
        entry = catalog.get(r['skill'], {})
        if r['skill'] in cleansing:
            r.update(cleansing[r['skill']])
        elif r['type'] in list(types)[:8] and r['min_level'] in damage:
            r['effect'] = f"{entry['target']}; {damage[r['min_level']]} obrażeń {types[r['type']]}"
            if entry.get('status') not in [None, '', '—']:
                r['effect'] += f"; po trafieniu i utracie HP: {status_text(entry['status'])}."
            else:
                r['effect'] += '.'
        elif r['type'] == 'ail' and entry.get('status') not in [None, '', '—']:
            r['effect'] = f"{entry['target']}; {status_text(entry['status'])}. Cel wykonuje rzut obronny d20; wynik równy DC lub wyższy chroni przed statusem."
        elif r['skill'] == 'Ailment Boost' or r['skill'].endswith(' Boost'):
            status = r['skill'].removesuffix(' Boost')
            target = 'statusów' if status == 'Ailment' else f'statusu {status}'
            r['effect'] = f'Zwiększa DC nakładanych przez ciebie {target} o 2. Z pasujących premii do DC stosuj tylko jedną, najwyższą.'
        elif r['skill'].startswith('Null '):
            r['effect'] = f"Pełna odporność na status {r['skill'][5:]}. Nie wykonujesz przeciw niemu rzutu obronnego."
        elif r['skill'].startswith('Resist '):
            r['effect'] = f"+4 do rzutu obronnego przeciw statusowi {r['skill'][7:]}."
        else:
            raise ValueError(f"Brakuje opisu dostępnego skilla: {r['skill']}")
    if not r.get('effect'):
        r['effect'] = {'Z': 'Umiejętność unikatowa, poza zwykłą nauką.', 'X': 'Mechanika nieużywana w tym systemie.', 'Ź': 'Trait źródłowy P5R; nie jest dodatkowym traitem osobistej Persony.'}.get(r['access'], '')
    r['effect'] = re.sub(r'\b(fir|ice|ele|win|psy|nuk|ble|cur|phy|gun|alm)\b', lambda m: types[m[0].lower()], r['effect'], flags=re.I)
    r['starter'] = r['skill'] in starters
    skills.append(r)
data = {'version': 'GM 0.8 / Gracz 0.5', 'skills': skills, 'arcana': arcana}
for name in inputs:
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != hashes[name]:
        raise RuntimeError(f'Podręcznik zmienił się podczas odczytu: {name}. Uruchom generowanie ponownie.')
(ROOT / 'aplikacja' / 'src' / 'rules.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Katalog: {len(skills)} skilli, {len(arcana)} Arkan, {len(starters)} skilli startowych; opisanych: {sum(bool(s.get("effect")) for s in skills)}')
